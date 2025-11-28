from django.shortcuts import render,redirect
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
#import PyPDF2
from docx import Document
import os
import logging

# Create your views here.
def home(request):
    return render(request,'home.html')

def login_user(request):
    user = get_user_model()
    if request.method == 'POST':
        email_or_username = request.POST.get('email')
        password = request.POST.get('password')


        try:
            existing_user = user.objects.get(email=email_or_username)
            username = existing_user.username
        except user.DoesNotExist:
            return JsonResponse({"status":"error","message":"user does to exists...!!"})

        usr = authenticate(request,username=username,password=password)
        redirect_url = ""
        
        if usr is not None:
            login(request,usr)

            if usr.is_staff:
                redirect_url = reverse('admin-dashboard')
            else:
                redirect_url = reverse('user-dashboard')

            return JsonResponse({
                    'status': 'success',  # Must match the JS 'success'
                    'message': 'Login successful!',
                    'redirect_url': redirect_url # Must send this key
                 })
        else:
            return JsonResponse({"status":"Error","message":"password or email doesn't match , please try again"})

    return render(request,'login.html')

def user_logout(request):
    logout(request)
    return redirect('login')

def register(request):
    if request.method == 'POST':
        # Get the form data
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirmPassword = request.POST.get('confirmPassword')

        # checking if confirm password matches password
        if password != confirmPassword:
            return JsonResponse({"status":"error","message":"password doesn't match"})
        
        # checking if the user already exists in the database
        if User.objects.filter(username=username).exists():
            return JsonResponse({"status":"error","message":"user already exists.."})
        
        # creating a user and store in database
        try:
            user = User.objects.create_user(username=username,email=email,password=password)
            user.save()
            return JsonResponse({'status': 'success',
                                 'message': 'Account created successfully!',
                                 'redirect_url':reverse('login')})
        except Exception as e:
            return JsonResponse({"status":"error","message":str(e)})
        
        
    
    # If GET request, show the registration form
    return render(request,'register.html')

@login_required(login_url='login')
def admin_dashboard(request):
    return render(request,'admin.html')

@login_required(login_url='login')
def user_dashboard(request):
    return render(request,'dashboard.html')

@login_required(login_url='login')
def view_contracts(request):
    return render(request,'viewContracts.html')

@login_required(login_url='login')
def upload_contract(request):
    return render(request,'uploadContract.html')

@login_required(login_url='login')
def send_complaint(request):
    return render(request,'complaint.html')

@login_required(login_url='login')
def feedback(request):
    return render(request,'feedback.html')