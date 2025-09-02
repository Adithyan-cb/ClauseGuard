from tkinter.font import names

from django.urls import path
from .views import test,login,register,admin
urlpatterns = [
    path('',test,name="home"),
    path('login/',login,name='login'),
    path('register/',register,name='register'),
    path('admin-login/',admin,name='admin')
]
