import datetime
from django.db import models
from django.contrib.auth.models import AbstractUser


waiting_fee = 5 #per half an hour
parking_fee = 5 #per hour
cancellation_fee = 10 #no of hours before cancelling


class User(AbstractUser):
	is_customer = models.BooleanField(default=True)
	is_employee = models.BooleanField(default=False)


class Price(models.Model):
	waiting_fee = models.IntegerField(default=waiting_fee)
	parking_fee = models.IntegerField(default=parking_fee)
	cancellation_fee = models.IntegerField(default=cancellation_fee)
	date = models.DateField(default=datetime.datetime.today())


class Customer(models.Model):
	user = models.OneToOneField(
		User, on_delete=models.CASCADE, related_name="customer")
	has_booked = models.BooleanField(default=False)
	has_occupied = models.BooleanField(default=False)
 
	def __str__(self) -> str:
		return self.user.username


class Prices(models.Model):
	waiting_fee = models.IntegerField(default=waiting_fee)
	parking_fee = models.IntegerField(default=parking_fee)
	cancellation_fee = models.IntegerField(default=cancellation_fee)
	date = models.DateField(default=datetime.date.today)


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

	def leave(self):
		self.is_reserved = False
		self.save()

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
	is_cancelled = models.BooleanField(default=False)
	parking_spot = models.ForeignKey(ParkingSpot, related_name="bookings", on_delete=models.CASCADE)
	vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, related_name="vehicle", null=True, blank=False)
	amount = models.IntegerField(default=0)

	def __str__(self):
		return f'{self.customer} {self.date} {self.parking_spot}'

	def close(self):
		self.is_active = False
		self.end_time = datetime.datetime.now().time()
		self.save()

	def cancel(self):
		self.end_time = datetime.datetime.now().time()
		self.is_active = False
		self.save()

	
	def calculate_amount(self):
		fee_obj = Prices.objects.last()
		waiting_fee = fee_obj.waiting_fee
		parking_fee = fee_obj.parking_fee
		cancellation_fee = fee_obj.cancellation_fee
		if self.is_cancelled:
			self.amount = cancellation_fee
		else:
			if self.start_time:
				start_time = datetime.datetime.combine(datetime.date.today(), self.start_time)
				end_time = datetime.datetime.combine(datetime.date.today(), self.end_time)
				time_diff = end_time - start_time
				time_diff = time_diff.total_seconds()
				time_diff = time_diff/3600
				time_diff = int(time_diff)
				self.amount += parking_fee*time_diff
			if self.booking_time:
				booking_time = datetime.datetime.combine(datetime.date.today(), self.booking_time)
				start_time = datetime.datetime.combine(datetime.date.today(), self.start_time)
				time_diff = start_time - booking_time
				time_diff = time_diff.total_seconds()
				time_diff = time_diff/3600
				time_diff = int(time_diff)
				self.amount += waiting_fee*time_diff
		self.save()
	

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
