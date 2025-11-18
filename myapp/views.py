from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.models import User
#import PyPDF2
from docx import Document
import os
import logging

# Create your views here.
def home(request):
    return render(request,'home.html')

def login(request):
    return render(request,'login.html')

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
            return JsonResponse({'status': 'success', 'message': 'Account created successfully!'})
        except Exception as e:
            return JsonResponse({"status":"error","message":str(e)})
        
        # Print the data to terminal
        # print("=" * 50)
        # print("NEW REGISTRATION SUBMISSION")
        # print("=" * 50)
        # print(f"Username: {username}")
        # print(f"Email: {email}")
        # print(f"Password: {password}")
        # print(f"Confirm Password: {confirmPassword}")
        # print("=" * 50)
        
        # Send success response
        
    
    # If GET request, show the registration form
    return render(request,'register.html')

def admin_dashboard(request):
    return render(request,'admin.html')

def user_dashboard(request):
    return render(request,'dashboard.html')

def view_contracts(request):
    return render(request,'viewContracts.html')

def upload_contract(request):
    return render(request,'uploadContract.html')

def send_complaint(request):
    return render(request,'complaint.html')

def feedback(request):
    return render(request,'feedback.html')