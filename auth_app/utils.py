import random
from datetime import datetime, timedelta
from django.core.cache import cache

def generate_otp():
    return str(random.randint(100000, 999999))  # Generate a random 6-digit OTP

def set_otp(user):
    otp = generate_otp()  # Generate the OTP
    user.otp = otp
    user.otp_expiry = datetime.now() + timedelta(minutes=5)  # Set expiry time
    user.save()
    return otp  # Return the generated OTP

def check_attempts(phone):
    attempt_key = f"attempts_{phone}"
    last_attempt_key = f"last_attempt_{phone}"

    attempts = cache.get(attempt_key, 0)
    last_attempt_time = cache.get(last_attempt_key)

    # Check if the last attempt was made within the last 60 seconds
    if last_attempt_time and (datetime.now() - last_attempt_time).total_seconds() < 60:
        return False  # Too soon to make another request

    # Update the cache
    cache.set(last_attempt_key, datetime.now(), timeout=60)  # Update last attempt time

    # Reset attempts if it's been more than 60 seconds since the last attempt
    if attempts >= 10:
        return False  # Exceeded maximum attempts

    cache.set(attempt_key, attempts + 1, timeout=60)  # Increment attempts
    return True  # Allow the attempt

def send_otp(phone, otp):
    # Logic to send OTP to the user's phone (e.g., via SMS service)
    print(f"Sending OTP {otp} to {phone}")  # For demonstration