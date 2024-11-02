from django.urls import path
from .views import UserLoginView, UserRegisterView, VerifyLoginOtpView, VerifyOtpView

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='user-register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('verify-otp/', VerifyOtpView.as_view(), name='verify-otp'),
    path('verify-otp-log-in/', VerifyLoginOtpView.as_view(), name='verify-login-otp'),
]