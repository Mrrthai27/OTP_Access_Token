from .utils import set_otp
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers, generics,status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from .models import User
from auth_app.serializer import UserRegisterSerializer, UserLoginSerializer


class UserRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    

def send_otp(phone, otp):
    # Logic to send OTP to the user's phone (e.g., via SMS service)
    print(f"Sending OTP {otp} to {phone}")  # For demonstration

class UserLoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer

    def post(self, request):
        phone = request.data.get('phone')
        try:
            user = User.objects.get(phone=phone)
            otp = set_otp(user)  # Only user is passed here
            
            send_otp(user.phone, otp)  # Pass both phone and otp to the function
            
            return Response({"message": "OTP sent","otp":user.otp}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)


class VerifyOtpView(generics.GenericAPIView):
    class OtpSerializer(serializers.Serializer):
        phone = serializers.CharField(max_length=10)
        otp = serializers.CharField(max_length=6)

    def post(self, request):
        serializer = self.OtpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data['phone']
        otp = serializer.validated_data['otp']

        try:
            user = User.objects.get(phone=phone)
            # Check if the OTP is valid and not expired
            if user.otp == otp and user.otp_expiry > timezone.now():
                user.is_active = True  # Activate user
                user.otp = None  # Clear OTP after successful verification
                user.otp_expiry = None  # Clear OTP expiry
                user.save()

                # Generate access token
                refresh = RefreshToken.for_user(user)
                return Response({
                    "message": "OTP verified successfully",
                    "access": str(refresh.access_token),
                    # "refresh": str(refresh),
                }, status=status.HTTP_200_OK)
            else:
                raise ValidationError("Invalid or expired OTP")
        except User.DoesNotExist:
            return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
