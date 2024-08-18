from django.shortcuts import render

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import Booking
from rest_framework.permissions import IsAdminUser
from .models import Train
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.models import User
from django.http import HttpResponse

class RegisterUser(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')

        if User.objects.filter(username=username).exists():
            return Response({'status': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, password=password, email=email)
        return Response({'status': 'Account successfully created', 'status_code': 200, 'user_id': user.id})



class LoginUser(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'status': 'Login successful',
                'status_code': 200,
                'user_id': user.id,
                'access_token': str(refresh.access_token),
                'admin':user.is_staff
            })
        else:
            return Response({'status': 'Incorrect username/password provided. Please retry', 'status_code': 401})



class CreateTrain(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]

    def post(self, request):
        data = request.data
        print(request.data.get('header'))
        train = Train.objects.create(
            train_name=data.get('train_name'),
            source=data.get('source'),
            destination=data.get('destination'),
            seat_capacity=data.get('seat_capacity'),
            available_seats=data.get('seat_capacity'),  # Initially all seats are available
            arrival_time_at_source=data.get('arrival_time_at_source'),
            arrival_time_at_destination=data.get('arrival_time_at_destination'),
        )
        return Response({'message': 'Train added successfully', 'train_id': train.id})

class GetSeatAvailability(APIView):
    def get(self, request):
        source = request.query_params.get('source')
        destination = request.query_params.get('destination')
        
        if source and destination:
            trains = Train.objects.filter(source=source, destination=destination)
            response_data = [
                {
                    'train_id': train.id,
                    'train_name': train.train_name,
                    'available_seats': train.available_seats,
                }
                for train in trains
            ]
            return Response(response_data)
        else:
            return Response({"error": "Source and destination are required."}, status=400)

from django.db import transaction

class BookSeat(APIView):
    authentication_classes = [JWTAuthentication]

    @transaction.atomic
    def post(self, request, train_id):
        train = Train.objects.select_for_update().get(id=train_id)
        no_of_seats = int(request.data.get('no_of_seats'))

        if train.available_seats >= no_of_seats:
            train.available_seats -= no_of_seats
            train.save()

            # Assign seat numbers (example, assign next available seats)
            seat_numbers = list(range(train.seat_capacity - train.available_seats, train.seat_capacity - train.available_seats + no_of_seats))
            booking = Booking.objects.create(
                user=request.user,
                train=train,
                no_of_seats=no_of_seats,
                seat_numbers=seat_numbers
            )

            return Response({
                'message': 'Seat booked successfully',
                'booking_id': booking.id,
                'seat_numbers': seat_numbers,
            })
        else:
            return Response({'message': 'Not enough seats available'}, status=400)

class GetBookingDetails(APIView):
    authentication_classes = [JWTAuthentication]

    def get(self, request, booking_id):
        try:
            booking = Booking.objects.get(id=booking_id, user=request.user)
            return Response({
                'booking_id': booking.id,
                'train_id': booking.train.id,
                'train_name': booking.train.train_name,
                'user_id': booking.user.id,
                'no_of_seats': booking.no_of_seats,
                'seat_numbers': booking.seat_numbers,
                'arrival_time_at_source': booking.train.arrival_time_at_source,
                'arrival_time_at_destination': booking.train.arrival_time_at_destination,
            })
        except Booking.DoesNotExist:
             return Response({
                'message': "Booking not found."
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class MakeAdmin(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]

    def post(self, request, username):
        try:
            user = User.objects.get(username=username)
            user.is_staff = True
            user.save()
            return Response({'message': f'User {username} is now an admin.'}, status=status.HTTP_200_OK)
        
        except User.DoesNotExist:
            return Response({'error': f'User {username} does not exist.'}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({'error': f'An error occurred: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class ListAllTrains(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        trains = Train.objects.all()
        response_data = [
            {
                'train_id': train.id,
                'train_name': train.train_name,
                'source': train.source,
                'destination': train.destination,
                'seat_capacity': train.seat_capacity,
                'available_seats': train.available_seats,
                'arrival_time_at_source': train.arrival_time_at_source,
                'arrival_time_at_destination': train.arrival_time_at_destination,
            }
            for train in trains
        ]
        return Response(response_data)

class DeleteTrain(APIView):
    authentication_classes = [JWTAuthentication] 
    permission_classes = [IsAdminUser]

    def delete(self, request, train_id):
        try:
            train = Train.objects.get(id=train_id)
            train.delete()
            return Response({'message': 'Train deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Train.DoesNotExist:
            return Response({'error': 'Train not found'}, status=status.HTTP_404_NOT_FOUND)

class ModifyTrain(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]

    def put(self, request, train_id):
        try:
            train = Train.objects.get(id=train_id)
        except Train.DoesNotExist:
            return Response({'error': 'Train not found'}, status=status.HTTP_404_NOT_FOUND)

        data = request.data
        train.train_name = data.get('train_name', train.train_name)
        train.source = data.get('source', train.source)
        train.destination = data.get('destination', train.destination)
        train.seat_capacity = data.get('seat_capacity', train.seat_capacity)
        train.available_seats = data.get('available_seats', train.available_seats)
        train.arrival_time_at_source = data.get('arrival_time_at_source', train.arrival_time_at_source)
        train.arrival_time_at_destination = data.get('arrival_time_at_destination', train.arrival_time_at_destination)
        
        train.save()

        return Response({'message': 'Train details updated successfully'}, status=status.HTTP_200_OK)

class GetTrainDetails(APIView):
    permission_classes = [AllowAny]  # Allow anyone to access this endpoint

    def get(self, request, train_id):
        try:
            train = Train.objects.get(id=train_id)
            response_data = {
                'train_id': train.id,
                'train_name': train.train_name,
                'source': train.source,
                'destination': train.destination,
                'seat_capacity': train.seat_capacity,
                'available_seats': train.available_seats,
                'arrival_time_at_source': train.arrival_time_at_source,
                'arrival_time_at_destination': train.arrival_time_at_destination,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except Train.DoesNotExist:
            return Response({'error': 'Train not found'}, status=status.HTTP_404_NOT_FOUND)


