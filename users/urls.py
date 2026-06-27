from django.urls import path
from .views import UserRegistrationView, UserLoginView, UserLogoutView, UserProfileView

app_name = 'users'

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(next_page='/'), name='logout'),
    path('profile/', UserProfileView.as_view(), name='profile'),
]