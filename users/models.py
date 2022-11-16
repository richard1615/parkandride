import datetime
from django.db import models
from django.contrib.auth.models import AbstractUser


waiting_fee = 5 #per half an hour
parking_fee = 5 #per hour
cancellation_fee = 10 #no of hours before cancelling


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

class Price(models.Model):
	waiting_fee = models.IntegerField(default=5)
	parking_fee = models.IntegerField(default=5)
	cancellation_fee = models.IntegerField(default=10)
	date = models.DateField(auto_now_add=True)

	def __str__(self):
		return f'Waiting Fee: {self.waiting_fee}, Parking Fee: {self.parking_fee}, Cancellation Fee: {self.cancellation_fee}, Date: {self.date}'

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
	is_occupied = models.BooleanField(default=False)
	vehicle_type = models.CharField(max_length=50, choices=[('car', "Car"), ('two wheeler', "Two Wheeler")], default='car')


	def leave(self):
		self.is_reserved = False
		self.save()

	def __str__(self) -> str:
		return f"{self.row}{self.column}"

	def is_available(self, spot, start_time, end_time):
		bookings = spot.bookings.filter(is_active=True)
		for booking in bookings:
			if start_time <= booking.start_time <= end_time or start_time <= booking.end_time <= end_time:
				return False
		return True


class Booking(models.Model):
	customer = models.ForeignKey(
		Customer, on_delete=models.CASCADE, related_name="bookings")
	date = models.DateField()
	booking_time = models.TimeField(null = True, blank = True)
	start_time = models.TimeField(null = True, blank = True)
	end_time = models.TimeField(null = True, blank = True)
	is_active = models.BooleanField(default=True)
	is_cancelled = models.BooleanField(default=False)
	is_occupied = models.BooleanField(default=False)
	parking_spot = models.ForeignKey(ParkingSpot, related_name="bookings", on_delete=models.CASCADE)
	vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, related_name="vehicle", null=True, blank=False)
	amount = models.IntegerField(default=0)

	def __str__(self):
		return f'{self.customer} {self.date} {self.parking_spot}'

	def close(self):
		self.is_active = False
		self.is_occupied = False
		self.customer.has_occupied = False
		self.customer.save()
		self.save()


	def cancel(self):
		self.is_cancelled = True
		self.is_active = False
		cancellation_fee = Price.objects.last().cancellation_fee
		self.amount = cancellation_fee
		self.save()

	
	def occupy(self):
		self.is_occupied = True
		self.customer.has_occupied = True
		self.customer.save()
		self.save()

	
	def setAmount(self):
		fee_obj = Price.objects.last()
		waiting_fee = fee_obj.waiting_fee
		parking_fee = fee_obj.parking_fee
		cancellation_fee = fee_obj.cancellation_fee
		if self.is_cancelled:
			self.amount = cancellation_fee
		else:
			if self.start_time:
				start_time = datetime.datetime.combine(datetime.date.today(), self.start_time)
				end_time = datetime.datetime.combine(datetime.date.today(), self.end_time)
				time_diff = abs((end_time - start_time).total_seconds()//3600)
				self.amount += parking_fee*time_diff
			if self.booking_time:
				booking_time = datetime.datetime.combine(datetime.date.today(), self.booking_time)
				start_time = datetime.datetime.combine(datetime.date.today(), self.start_time)
				time_diff = (start_time - booking_time).total_seconds()//3600
				self.amount += abs(waiting_fee*time_diff)
		self.save()
	

class Feedback(models.Model):
	booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="feedbacks")
	comment = models.TextField()
	is_responded = models.BooleanField(default=False)
	date_time = models.DateTimeField(auto_now_add=True)

	def __str__(self) -> str:
		return f"{self.booking.customer} {self.booking.date}"


class Response(models.Model):
	feedback = models.OneToOneField(Feedback, on_delete=models.CASCADE, related_name="responses")
	employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="responses")
	customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="responses")
	response = models.TextField()
	date_time = models.DateTimeField(auto_now_add=True)

	def __str__(self) -> str:
		return f"{self.feedback.booking.customer} {self.feedback.booking.date}"


