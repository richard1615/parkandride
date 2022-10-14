from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.forms import ModelForm

from .models import User, Booking, Vehicle

class UserRegisterForm(UserCreationForm): 

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class SearchParkingLotForm(forms.Form):
    row = forms.CharField(max_length=1, label="Row", widget=forms.Select(choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('E', 'E'), ('F', 'F'), ('G', 'G')]))
    column = forms.IntegerField(label="Column", widget=forms.Select(choices=[(i,i) for i in range(1, 11)]))
        

class BookingForm(forms.ModelForm):
    
    class Meta:
        model = Booking
        fields = ["vehicle"]
            
    def __init__(self, user=None, **kwargs):
        super(BookingForm, self).__init__(**kwargs)
        if user:
            self.fields['vehicle'].queryset = Vehicle.objects.filter(customer=user.customer)