from sys import path_hooks
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("book", views.book, name="book"),
    path('register/', views.register, name='register'),
    path("occupy/<id>", views.occupy, name="occupy"),
    path("leave/<id>", views.leave, name="leave"),
    path("cancel/<id>", views.cancel, name="cancel"),
    path("business/transactions/", views.BookingListView.as_view(), name="transactions"),
    path("business/parking-spot/<pk>", views.ParkingSpotDetailView.as_view(), name="parking-spot"),
    path("business/search-parking-spot/", views.search_parking_spot, name="search-parking-spot"),
    path("feedback_create/<pk>", views.FeedbackCreateView.as_view(), name="feedback-create"),
    path("business/feedback", views.FeedbackListView.as_view(), name="feedback-list"),
    path('responses', views.ResponseListView.as_view(), name="responses"),
    path('business/response/<pk>', views.ResponseCreateView.as_view(), name="create-response"),
    path('vehicles', views.VehicleListView.as_view(), name='vehicles'),
    path("add-vehicle/", views.VehicleCreateView.as_view(), name="add-vehicle"),
    path("booking/<pk>", views.BookingDetailView.as_view(), name="booking-detail"),
    path("business/setprice", views.PriceSetView.as_view(), name="set-price"),
]