from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator


class User(AbstractUser):
    phone = models.CharField(max_length=10,unique=True, blank=True, null=True, validators=[RegexValidator(
    regex=r"^\d{10}", message="Phone number must be 10 digits only.")])
    username = models.CharField(max_length=150, unique=True)
    otp = models.CharField(max_length=6, null=True, blank=True)
    max_otp_try = models.IntegerField(default=3)
    otp_expiry = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=False)
