import datetime
from django.db import models
from django.contrib.auth.models import AbstractUser

#cancellation fee: 20
#occupy fee: 30 per hour


class User(AbstractUser):
	is_customer = models.BooleanField(default=True)
	is_employee = models.BooleanField(default=False)


class Customer(models.Model):
	user = models.OneToOneField(
		User, on_delete=models.CASCADE, related_name="customer")
	has_booked = models.BooleanField(default=False)
	has_occupied = models.BooleanField(default=False)
 
	def __str__(self) -> str:
		return self.user.username


class Employee(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="employee")

    def __str__(self) -> str:
        return self.user.username


class Vehicle(models.Model):
	customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='vehicles')
	name = models.CharField(max_length=50)
	license_no = models.CharField(max_length=50)
	vehicle_type = models.CharField(choices=[('car', 'Car'), ('twowheeler', 'Two Wheeler')] ,max_length=50)

	def __str__(self) -> str:
		return f'{self.customer.user.username} {self.name}'


class ParkingSpot(models.Model):
	row = models.CharField(max_length=1, choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('E', 'E'), ('F', 'F'), ('G', 'G')])
	column = models.IntegerField(choices=[(i, i) for i in range(1, 11)])
	is_reserved = models.BooleanField(default=False)
	vehicle_type = models.CharField(max_length=50, choices=[('car', "Car"), ('two wheeler', "Two Wheeler")], default='car')

	def __str__(self) -> str:
		return f"{self.row}{self.column}"


class Booking(models.Model):
	customer = models.ForeignKey(
		Customer, on_delete=models.CASCADE, related_name="bookings")
	date = models.DateField()
	booking_time = models.TimeField(null = True, blank = True)
	start_time = models.TimeField(null = True, blank = True)
	end_time = models.TimeField(null = True, blank = True)
	is_active = models.BooleanField(default=True)
	parking_spot = models.ForeignKey(ParkingSpot, related_name="bookings", on_delete=models.CASCADE)
	vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, related_name="vehicle", null=True, blank=False)

	def __str__(self):
		return f'{self.customer} {self.date} {self.parking_spot}'
	


class Feedback(models.Model):
	booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="feedbacks")
	comment = models.TextField()
	is_responded = models.BooleanField(default=False)
	date_time = models.DateTimeField(default=datetime.datetime.now())

	def __str__(self) -> str:
		return f"{self.booking.customer} {self.booking.date}"



class Response(models.Model):
	feedback = models.OneToOneField(Feedback, on_delete=models.CASCADE, related_name="responses")
	employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="responses")
	customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="responses")
	response = models.TextField()
	date_time = models.DateTimeField(default=datetime.datetime.now())

	def __str__(self) -> str:
		return f"{self.feedback.booking.customer} {self.feedback.booking.date}"
