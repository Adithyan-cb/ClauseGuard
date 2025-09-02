from tkinter.font import names

from django.urls import path
from .views import test,login,register
urlpatterns = [
    path('',test,name="home"),
    path('login/',login,name='login'),
    path('register/',register,name='register')
]
