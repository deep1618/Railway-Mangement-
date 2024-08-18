from django.contrib.auth.models import User
from django.db import models

class Train(models.Model):
    train_name = models.CharField(max_length=100)
    source = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    seat_capacity = models.IntegerField()
    available_seats = models.IntegerField()
    arrival_time_at_source = models.TimeField()
    arrival_time_at_destination = models.TimeField()

    def __str__(self):
        return self.train_name

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    train = models.ForeignKey(Train, on_delete=models.CASCADE)
    no_of_seats = models.IntegerField()
    seat_numbers = models.JSONField()

    def __str__(self):
        return f'Booking {self.id} by {self.user.username}'
