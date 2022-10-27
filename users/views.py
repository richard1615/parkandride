import datetime
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect, render
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.urls import reverse
from django.contrib import messages


from .models import Booking, Feedback, ParkingSpot, Feedback, Response, Vehicle, Price
from .forms import UserRegisterForm, SearchParkingLotForm, BookingForm, PriceForm


@login_required(login_url='login')
def index(request):
    if request.user.is_employee:
        return redirect('transactions')
    else:
        customer = request.user.customer
        bookings = customer.bookings.filter(
            is_active=False).order_by('-date', '-booking_time')
        current_booking = customer.bookings.filter(is_active=True).first()

        return render(request, "users/index.html", {
            "customer": customer,
            "bookings": bookings,
            "current_booking": current_booking,
            "vehicle_form": BookingForm()
        })


@login_required(login_url='login')
def parking_lots(request):
    spots = ParkingSpot.objects.all()
    return render(request, "users/parking_lots.html", {
        "spots": spots,
    })


@login_required(login_url='login')
def book(request):
    if request.method == 'POST':
        customer = request.user.customer
        form = BookingForm(request.POST)
        if form.is_valid():
            vehicle = form.cleaned_data["vehicle"]
        else:
            return form.errors.as_data()
        spot = ParkingSpot.objects.filter(
            is_reserved=False, vehicle_type=vehicle.vehicle_type).first()
        if spot:
            customer.has_booked = True
            customer.save()
            spot.is_reserved = True
            spot.save()
            Booking.objects.create(
                customer=customer,
                date=datetime.date.today(),
                booking_time=datetime.datetime.now().time(),
                parking_spot=spot,
                vehicle=vehicle
            )
            messages.success(request, "Parking lot allotted succesfully")
        else:
            messages.error(
                request, "No parking spot available for your vehicle type")
    return redirect("index")


@login_required(login_url='login')
def occupy(request, id):
    booking = Booking.objects.get(id=id)
    customer = booking.customer
    customer.has_occupied = True
    customer.save()
    booking.is_active = True
    booking.start_time = datetime.datetime.now().time()
    booking.save()
    return redirect("index")


@login_required(login_url='login')
def leave(request, id):
    customer = request.user.customer
    customer.has_booked = False
    customer.has_occupied = False
    customer.save()
    booking = Booking.objects.get(id=id)
    booking.close()
    booking.setAmount()
    spot = booking.parking_spot
    spot.leave()
    return redirect("index")


@login_required(login_url='login')
def cancel(request, id):
    customer = request.user.customer
    customer.has_booked = False
    customer.has_occupied = False
    customer.save()
    booking = Booking.objects.get(id=id)
    booking.cancel()
    booking.setAmount()
    spot = booking.parking_spot
    spot.leave()
    return redirect("index")


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


class BookingListView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = "users/transactions.html"
    context_object_name = "bookings"
    login_url = 'login/'
    redirect_field_name = 'redirect_to'
    paginate_by = 5

    def get_queryset(self):
        if self.request.user.is_employee:
            return Booking.objects.order_by('-date', '-booking_time')
        else:
            return Booking.objects.filter(customer=self.request.user.customer).order_by('-date', '-booking_time')

class BookingDetailView(LoginRequiredMixin, DetailView):
    model = Booking
    template_employee_name = "users/transaction_detail.html"
    template_user_name = "users/booking_detail.html"
    context_object_name = "booking"
    login_url = 'login/'
    redirect_field_name = 'redirect_to'
    

class ParkingSpotDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = ParkingSpot
    template_name = "users/parking_spot.html"
    context_object_name = "parking_spot"
    login_url = 'login/'
    redirect_field_name = 'redirect_to'

    def get_context_data(self, **kwargs):
        context = super(ParkingSpotDetailView, self).get_context_data(**kwargs)
        bookings = ParkingSpot.objects.get(
            id=self.kwargs['pk']).bookings.order_by('-date', '-booking_time')
        context['bookings'] = bookings
        return context

    def test_func(self):
        return self.request.user.is_employee


@login_required(login_url='login')
@user_passes_test(lambda u: u.is_employee)
def search_parking_spot(request):
    if request.method == "POST":
        form = SearchParkingLotForm(request.POST)
        if form.is_valid():
            row = form.cleaned_data["row"]
            column = form.cleaned_data["column"]
            parking_lot = ParkingSpot.objects.filter(
                row=row, column=column).first()
            return redirect("parking-spot", pk=parking_lot.id)
    return render(request, "users/search_parking_spot.html", {"form": SearchParkingLotForm()})


class FeedbackCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):  # Customer
    model = Feedback
    template_name = "users/feedback.html"
    fields = ["comment"]
    login_url = 'login/'
    redirect_field_name = 'redirect_to'

    def test_func(self):
        return self.request.user.is_customer

    def form_valid(self, form):
        booking = Booking.objects.get(id=self.kwargs['pk'])
        form.instance.booking = booking
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('index')


class FeedbackListView(LoginRequiredMixin, UserPassesTestMixin, ListView):  # Employee
    model = Feedback
    template_name = "users/feedback_list.html"
    context_object_name = "feedbacks"
    login_url = 'login/'
    redirect_field_name = 'redirect_to'

    def get_queryset(self):
        return Feedback.objects.filter(is_responded=False).order_by('-date_time')

    def test_func(self):
        return self.request.user.is_employee


class ResponseCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):  # Employee
    model = Response
    fields = ["response"]
    template_name = "users/create_response.html"
    login_url = 'login/'
    redirect_field_name = 'redirect_to'

    def test_func(self):
        return self.request.user.is_employee

    def form_valid(self, form):
        feedback = Feedback.objects.get(id=self.kwargs['pk'])
        feedback.is_responded = True
        feedback.save()
        form.instance.customer = feedback.booking.customer
        form.instance.feedback = feedback
        form.instance.employee = self.request.user.employee
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return reverse('feedback-list')


class ResponseListView(LoginRequiredMixin, UserPassesTestMixin, ListView):  # Customer
    model = Response
    template_name = "users/response_list.html"
    context_object_name = "responses"
    login_url = 'login/'
    redirect_field_name = 'redirect_to'

    def get_queryset(self):
        return Response.objects.filter(customer=self.request.user.customer).order_by('date_time')

    def test_func(self):
        return self.request.user.is_customer


class VehicleCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Vehicle
    login_url = 'login/'
    redirect_field_name = 'redirect_to'
    fields = ['name', 'license_no', 'vehicle_type']

    def test_func(self):
        return self.request.user.is_customer

    def form_valid(self, form):
        form.instance.customer = self.request.user.customer
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return reverse('vehicles')


class VehicleListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Vehicle
    login_url = 'login/'
    redirect_field_name = 'redirect_to'
    context_object_name = 'vehicles'

    def get_queryset(self):
        return Vehicle.objects.filter(customer=self.request.user.customer)

    def test_func(self):
        return self.request.user.is_customer


class PriceSetView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Price
    login_url = 'login/'
    redirect_field_name = 'redirect_to'

    def test_func(self):
        return self.request.user.is_employee

    def get_success_url(self) -> str:
        return reverse('set-price')

    def get_context_data(self, **kwargs):
        context = super(PriceSetView, self).get_context_data(**kwargs)
        context['form'] = PriceForm()
        return super().get_context_data(**kwargs)