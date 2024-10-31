
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import User


class UserRegisterSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(max_length=10)

    class Meta:
        model = User
        fields = ['phone', 'username']  # Add other fields as necessary

    def create(self, validated_data):
        user = User(
            phone=validated_data['phone'],
            username=self.get_username_from_username(validated_data['username']),  # Define this method
            is_active=True  # Adjust according to your logic
        )
        user.save()
        return user

    def validate_phone(self, value):
        if User.objects.filter(phone=value).exists():
            raise ValidationError("Phone number is already taken!")
        return value
    

    def get_username_from_username(self, username):
        return username  # Customize this if you need a different username logic
    
    
class UserLoginSerializer(serializers.ModelSerializer):
    phone = serializers.CharField()

    class Meta:
        model = User
        fields = ['phone']
