from django.urls import path
from .views import (
    PasswordResetRequestView,
    PasswordResetVerifyOTPView,
    PasswordResetConfirmView,
    UserRegistrationView
)
from auth_kit.views import LoginView, LogoutView , RefreshViewWithCookieSupport

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('password/reset/', PasswordResetRequestView.as_view(), name='password_reset'),
    path('password/reset/verify-otp/', PasswordResetVerifyOTPView.as_view(), name='verify_otp'),
    path('password/reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('token/refresh/', RefreshViewWithCookieSupport.as_view(), name='refresh'),
]