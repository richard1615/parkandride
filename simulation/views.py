from django.shortcuts import render, redirect
import datetime
from django.contrib import messages
from django.shortcuts import render
from django.views.generic import ListView, DetailView

from users.models import Booking, Customer


class CustomerListView(ListView):
    model = Customer
    template_name = "simulation/customer_list.html"
    context_object_name = "customers"
    paginate_by = 10


def occupy(request, id):
    customer = Customer.objects.get(id=id)
    bookings = Booking.objects.filter(customer=customer, is_active=True)
    if bookings:
        for booking in bookings:
            if (
                booking
                and booking.start_time <= datetime.datetime.now().time() <= booking.end_time
            ):
                booking.occupy()
                messages.success(request, f"Occupied {booking.parking_spot}")
                break
            else:
                messages.error(request, f"Booking not found")
    else:
        messages.error(request, f"Booking not found")
    return redirect('customers')


def leave(request, id):
    customer = Customer.objects.get(id=id)
    booking = Booking.objects.filter(customer=customer, is_occupied=True).first()
    if (
        booking
        and booking.start_time <= datetime.datetime.now().time() <= booking.end_time
    ):
        booking.close()
        messages.success(request, f"Left {booking.parking_spot}")
    else:
        messages.error(request, f"Booking not found")
    return redirect('customers')
