from django.urls import path
from .views import home,login,register,admin_dashboard
urlpatterns = [
   path('',home,name='home'),
   path('login/',login,name="login"),
   path('register/',register,name="register"),
   path('admin-dashboard/',admin_dashboard,name="admin-dashboard")
]