from django.shortcuts import render,redirect,get_object_or_404
from django.urls import reverse
from django.http import JsonResponse, FileResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from .models import Contract, Complaint, Feedback
#import PyPDF2
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
    # Fetch all contracts for the logged-in user
    contracts = Contract.objects.filter(user=request.user).order_by('-uploaded_at')
    context = {
        'contracts': contracts
    }
    return render(request,'viewContracts.html', context)

@login_required(login_url='login')
def upload_contract(request):
    if request.method == 'POST':
        try:
            # Get the uploaded file and form data
            contract_file = request.FILES.get('contract_file')
            llm_model = request.POST.get('llm_model')
            contract_type = request.POST.get('contract_type')
            jurisdiction = request.POST.get('jurisdiction')

            # Validate that file is provided
            if not contract_file:
                return JsonResponse({
                    'status': 'error',
                    'message': 'No file provided. Please upload a contract file.'
                }, status=400)

            # Validate file extension
            allowed_extensions = ['pdf', 'doc', 'docx']
            file_ext = contract_file.name.split('.')[-1].lower()
            if file_ext not in allowed_extensions:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Invalid file type. Allowed: {", ".join(allowed_extensions).upper()}'
                }, status=400)

            # Validate file size (10MB)
            max_size = 10 * 1024 * 1024  # 10MB
            if contract_file.size > max_size:
                return JsonResponse({
                    'status': 'error',
                    'message': 'File size exceeds 10MB limit.'
                }, status=400)

            # Validate form fields
            if not all([llm_model, contract_type, jurisdiction]):
                return JsonResponse({
                    'status': 'error',
                    'message': 'Please fill in all required fields.'
                }, status=400)

            # Create and save the Contract object
            contract = Contract(
                user_id=request.user.id,
                contract_file=contract_file,
                llm_model=llm_model,
                contract_type=contract_type,
                jurisdiction=jurisdiction
            )
            contract.save()

            return JsonResponse({
                'status': 'success',
                'message': 'Contract uploaded successfully!',
                'contract_id': contract.id,
                'file_name': contract_file.name
            }, status=201)

        except Exception as e:
            logging.error(f"Error uploading contract: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': f'An error occurred: {str(e)}'
            }, status=500)
    
    # GET request - show the upload form
    return render(request,'uploadContract.html')

@login_required(login_url='login')
def view_contract(request, contract_id):
    """Display the contract file"""
    try:
        # Get the contract and ensure it belongs to the current user
        contract = get_object_or_404(Contract, id=contract_id, user=request.user)
        
        # Check if file exists
        if not contract.contract_file:
            return JsonResponse({
                'status': 'error',
                'message': 'File not found.'
            }, status=404)
        
        # Open and return the file
        file_path = contract.contract_file.path
        if os.path.exists(file_path):
            return FileResponse(open(file_path, 'rb'), as_attachment=False)
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'File not found on server.'
            }, status=404)
    
    except Exception as e:
        logging.error(f"Error viewing contract: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': f'An error occurred: {str(e)}'
        }, status=500)

@login_required(login_url='login')
def download_contract(request, contract_id):
    """Download the contract file"""
    try:
        # Get the contract and ensure it belongs to the current user
        contract = get_object_or_404(Contract, id=contract_id, user=request.user)
        
        # Check if file exists
        if not contract.contract_file:
            return JsonResponse({
                'status': 'error',
                'message': 'File not found.'
            }, status=404)
        
        # Open and return the file as attachment for download
        file_path = contract.contract_file.path
        if os.path.exists(file_path):
            response = FileResponse(open(file_path, 'rb'), as_attachment=True)
            response['Content-Disposition'] = f'attachment; filename="{contract.contract_file.name.split("/")[-1]}"'
            return response
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'File not found on server.'
            }, status=404)
    
    except Exception as e:
        logging.error(f"Error downloading contract: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': f'An error occurred: {str(e)}'
        }, status=500)

@login_required(login_url='login')
def send_complaint(request):
    if request.method == 'POST':
        try:
            # Get the complaint data from AJAX request
            subject = request.POST.get('subject')
            category = request.POST.get('category')
            priority = request.POST.get('priority')
            message = request.POST.get('message')

            # Validate that all required fields are filled
            if not all([subject, category, priority, message]):
                return JsonResponse({
                    'status': 'error',
                    'message': 'Please fill in all required fields.'
                }, status=400)

            # Validate priority value
            valid_priorities = ['low', 'medium', 'high']
            if priority not in valid_priorities:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid priority level.'
                }, status=400)

            # Create and save the Complaint object
            complaint = Complaint(
                user=request.user,
                subject=subject,
                category=category,
                priority=priority,
                message=message
            )
            complaint.save()

            return JsonResponse({
                'status': 'success',
                'message': 'Complaint submitted successfully! Our team will review it soon.',
                'complaint_id': complaint.id
            }, status=201)

        except Exception as e:
            logging.error(f"Error submitting complaint: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': f'An error occurred: {str(e)}'
            }, status=500)
    
    # GET request - show the complaint form
    return render(request,'complaint.html')

@login_required(login_url='login')
def feedback(request):
    if request.method == 'POST':
        try:
            # Get the feedback data from AJAX request
            category = request.POST.get('category')
            rating = request.POST.get('rating')
            message = request.POST.get('message')
            email = request.POST.get('email')

            # Validate that all required fields are filled
            if not all([category, rating, message]):
                return JsonResponse({
                    'status': 'error',
                    'message': 'Please fill in all required fields.'
                }, status=400)

            # Validate rating value
            try:
                rating_int = int(rating)
                if rating_int < 1 or rating_int > 5:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Rating must be between 1 and 5.'
                    }, status=400)
            except ValueError:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid rating value.'
                }, status=400)

            # Create and save the Feedback object
            feedback_obj = Feedback(
                user=request.user,
                category=category,
                rating=rating_int,
                message=message,
                date=str(__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            )
            feedback_obj.save()

            return JsonResponse({
                'status': 'success',
                'message': 'Feedback submitted successfully! Thank you for your input.',
                'feedback_id': feedback_obj.id
            }, status=201)

        except Exception as e:
            logging.error(f"Error submitting feedback: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': f'An error occurred: {str(e)}'
            }, status=500)
    
    # GET request - show the feedback form
    return render(request,'feedback.html')