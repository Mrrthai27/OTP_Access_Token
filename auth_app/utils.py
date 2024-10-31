import random
from datetime import datetime, timedelta

def generate_otp():
    return str(random.randint(100000, 999999))  # Generate a random 6-digit OTP

def set_otp(user):
    otp = generate_otp()  # Generate the OTP
    user.otp = otp
    user.otp_expiry = datetime.now() + timedelta(minutes=5)  # Set expiry time
    user.save()
    return otp  # Return the generated OTP
