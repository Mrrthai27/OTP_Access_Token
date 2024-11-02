
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import User


class UserRegisterSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(max_length=10)

    class Meta:
        model = User
        fields = ['phone', 'username']  # Add other fields as necessary

    def create(self, validated_data):
        # Create a new user instance
        user = User(
            phone=validated_data['phone'],
            username=self.get_username_from_username(validated_data['username']),
            is_active=False  # Set inactive until OTP verification
        )
        user.save()
        return user

    def validate_phone(self, value):
        # Check if the phone number is already taken
        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError("Phone number is already taken!")
        return value

    def get_username_from_username(self, username):
        # Customize this if you need a different username logic
        return username.strip()  # Example: Trim whitespace from the username

    
class UserLoginSerializer(serializers.ModelSerializer):
    phone = serializers.CharField()

    class Meta:
        model = User
        fields = ['phone']
