from django.contrib import admin
from .models import (Customer, Booking, ParkingSpot, User, Employee, Feedback, Response, Vehicle, Price)

# Register your models here.
admin.site.register(Customer)
admin.site.register(Booking)
admin.site.register(ParkingSpot)
admin.site.register(User)
admin.site.register(Employee)
admin.site.register(Feedback)
admin.site.register(Response)
admin.site.register(Vehicle)
admin.site.register(Price)