from django.urls import path

from . import views

urlpatterns = [
    path("", views.CustomerListView.as_view(), name="customers"),
    path("occupy/<int:id>", views.occupy, name="occupy"),
    path("leave/<int:id>", views.leave, name="leave"),
]