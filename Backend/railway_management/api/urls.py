from django.urls import path
from .views import RegisterUser, LoginUser,BookSeat,GetBookingDetails,CreateTrain,GetSeatAvailability,ListAllTrains,DeleteTrain,ModifyTrain,GetTrainDetails,MakeAdmin

urlpatterns = [
    path('signup/', RegisterUser.as_view(), name='signup'),
    path('login/', LoginUser.as_view(), name='login'),
    path('book-seat/<int:train_id>/', BookSeat.as_view(), name='book_seat'),
    path('booking-details/<int:booking_id>/', GetBookingDetails.as_view(), name='booking_details'),
    path('create-train/',CreateTrain.as_view(),name='create_train'),
    path('make-admin/<str:username>/', MakeAdmin.as_view(), name='make_admin'),
    path('seat-availability/', GetSeatAvailability.as_view(), name='seat-availability'),
    path('trains/', ListAllTrains.as_view(), name='list-all-trains'),
    path('delete/<int:train_id>/', DeleteTrain.as_view(), name='delete-train'),
    path('modify/<int:train_id>/', ModifyTrain.as_view(), name='modify-train'),
    path('trains/<int:train_id>/', GetTrainDetails.as_view(), name='get-train-details'),
]
