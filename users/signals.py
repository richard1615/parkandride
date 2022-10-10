from django.db.models.signals import post_save
from django.dispatch import receiver    
from .models import User, Customer, Employee, Booking


@receiver(post_save, sender=User)
def create_customer(sender, instance, created, **kwargs):
    if created and instance.is_customer:
        Customer.objects.create(user=instance)  
    elif created and instance.is_employee:
        Employee.objects.create(user=instance)
