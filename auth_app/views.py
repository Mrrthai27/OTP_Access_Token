import random
from tokenize import Token
from rest_framework.authtoken.models import Token
from .utils import check_attempts, generate_otp
from django.core.cache import cache
from rest_framework import generics,status
from rest_framework.response import Response
from .models import User
from auth_app.serializer import UserRegisterSerializer, UserLoginSerializer


class UserRegisterView(generics.GenericAPIView):
    serializer_class = UserRegisterSerializer

    def post(self, request):
        phone_number = request.data.get('phone')
        username = request.data.get('username')

        if not username:
            return Response({"error": "Username is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Generate OTP
        otp = random.randint(100000, 999999)
        otp_key = f"otp_{phone_number}"
        cache.set(otp_key, otp, timeout=60)  # Store OTP for 60 seconds

        # Send the OTP to the user's phone number (optional)
        send_otp(phone_number, otp)

        # Store username temporarily in cache for later use
        cache.set(f"username_{phone_number}", username, timeout=60)

        # Active status is False since the user has not verified yet
        return Response({
            "message": "Register succesfully OTP sent to your phone.",
            "otp": otp,  # Include the OTP in the response for testing purposes
            "active": False  # Set active status to False initially
        }, status=status.HTTP_200_OK)

    def verify_otp(self, request):
        phone_number = request.data.get('phone')
        otp = request.data.get('otp')

        otp_key = f"otp_{phone_number}"
        cached_otp = cache.get(otp_key)

        if cached_otp and str(cached_otp) == str(otp):
            # Verification successful, mark user as active
            # Here you would normally update the user's status in the database
            # For demonstration, we'll assume the user is now active
            return Response({
                "message": "OTP verified successfully.",
                "active": True  # Now the user is active
            }, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid or expired OTP."}, status=status.HTTP_400_BAD_REQUEST)

def send_otp(phone, otp):
    # Logic to send OTP to the user's phone (e.g., via SMS service)
    print(f"Sending OTP {otp} to {phone}")  # For demonstration

def send_otp(phone, otp):
    # Logic to send OTP to the user's phone (e.g., via SMS service)
    print(f"Sending OTP {otp} to {phone}")  # For demonstration


class UserLoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer

    def post(self, request):
        phone = request.data.get('phone')

        # Check attempts before generating OTP
        if not check_attempts(phone):
            return Response({"error": "You have exceeded the maximum number of attempts or need to wait 60 seconds."},
                            status=status.HTTP_429_TOO_MANY_REQUESTS)

        try:
            user = User.objects.get(phone=phone)
            otp = generate_otp()  # Generate a new OTP

            # Store the OTP in cache with a timeout
            otp_key = f"otp_{phone}"
            cache.set(otp_key, otp, timeout=60)  # Store OTP for 60 seconds
            
            send_otp(user.phone, otp)  # Send the OTP to the user's phone

            # Return a response indicating the OTP was sent
            return Response({
                "message": "OTP sent",
                # Remove this line in production
                "otp": otp  # Include OTP for testing purposes
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)

    def verify_otp(self, request):
        phone = request.data.get('phone')
        otp = request.data.get('otp')
        otp_key = f"otp_{phone}"
        cached_otp = cache.get(otp_key)

        if cached_otp is None:
            return Response({"error": "OTP has expired or is invalid."}, status=status.HTTP_400_BAD_REQUEST)

        if otp == str(cached_otp):
            # OTP is valid, log the user in (e.g., create a token, etc.)
            cache.delete(otp_key)  # Clean up the OTP after successful verification
            
            # Here you would typically generate a token for the user
            # Example: token = create_token(user)
            return Response({"message": "Login successful"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)

class VerifyOtpView(generics.GenericAPIView):
    serializer_class = UserRegisterSerializer  # Use the registration serializer

    def post(self, request):
        phone_number = request.data.get('phone')
        otp = request.data.get('otp')
        cached_otp = cache.get(f"otp_{phone_number}")
        username = cache.get(f"username_{phone_number}")

        if cached_otp is None:
            return Response({"error": "OTP has expired or is invalid."}, status=status.HTTP_400_BAD_REQUEST)

        if otp == str(cached_otp):
            # If the OTP is valid, create the user
            user_data = {
                'phone': phone_number,
                'username': username,
            }
            serializer = self.get_serializer(data=user_data)
            serializer.is_valid(raise_exception=True)

            user = serializer.save()  # Create the user only after successful OTP verification
            
            # Create a token for the user
            token, created = Token.objects.get_or_create(user=user)

            # Clear the cache after registration
            cache.delete(f"otp_{phone_number}")
            cache.delete(f"username_{phone_number}")

            return Response({
                "message": "User activated successfully.",  # Success message
                "token": token.key,  # Include the token in the response
                "user": serializer.data  # Optionally return user data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)


class VerifyLoginOtpView(generics.GenericAPIView):
    def post(self, request):
        phone_number = request.data.get('phone')
        otp = request.data.get('otp')
        cached_otp = cache.get(f"otp_{phone_number}")

        if cached_otp is None:
            return Response({"error": "OTP has expired or is invalid."}, status=status.HTTP_400_BAD_REQUEST)

        if otp == str(cached_otp):
            try:
                user = User.objects.get(phone=phone_number)
                # OTP is valid, log the user in
                cache.delete(f"otp_{phone_number}")  # Clean up the OTP after successful verification
                
                # Create a token for the user
                token, created = Token.objects.get_or_create(user=user)

                return Response({
                    "message": "Login successful",
                    "token": token.key  # Include the token in the response
                }, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({"error": "User does not exist."}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)