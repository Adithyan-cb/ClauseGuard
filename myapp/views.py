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
    # Check if user is an admin (staff member)
    if not request.user.is_staff:
        return redirect('user-dashboard')
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

@login_required(login_url='login')
def get_users_ajax(request):
    """Return users as JSON for AJAX request"""
    try:
        users = User.objects.all().order_by('-date_joined')
        users_data = []
        for user in users:
            users_data.append({
                'id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'date_joined': user.date_joined.strftime('%Y-%m-%d')
            })
        return JsonResponse({
            'status': 'success',
            'users': users_data
        })
    except Exception as e:
        logging.error(f"Error fetching users: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': f'An error occurred: {str(e)}'
        }, status=500)

@login_required(login_url='login')
def get_contracts_ajax(request):
    """Return all contracts as JSON for AJAX request"""
    try:
        contracts = Contract.objects.all().order_by('-uploaded_at')
        contracts_data = []
        for contract in contracts:
            contracts_data.append({
                'id': contract.id,
                'user': contract.user.username,
                'contract_type': contract.contract_type,
                'jurisdiction': contract.jurisdiction,
                'llm_model': contract.llm_model,
                'uploaded_at': contract.uploaded_at.strftime('%Y-%m-%d')
            })
        return JsonResponse({
            'status': 'success',
            'contracts': contracts_data
        })
    except Exception as e:
        logging.error(f"Error fetching contracts: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': f'An error occurred: {str(e)}'
        }, status=500)

@login_required(login_url='login')
def get_complaints_ajax(request):
    """Return all complaints as JSON for AJAX request"""
    try:
        complaints = Complaint.objects.all().order_by('-created_at')
        complaints_data = []
        for complaint in complaints:
            complaints_data.append({
                'id': complaint.id,
                'subject': complaint.subject,
                'category': complaint.category,
                'priority': complaint.priority,
                'message': complaint.message,
                'admin_reply': complaint.admin_reply or '',
                'created_at': complaint.created_at.strftime('%Y-%m-%d'),
                'replied_at': complaint.replied_at.strftime('%Y-%m-%d') if complaint.replied_at else '',
                'user_id': complaint.user.id
            })
        return JsonResponse({
            'status': 'success',
            'complaints': complaints_data
        })
    except Exception as e:
        logging.error(f"Error fetching complaints: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': f'An error occurred: {str(e)}'
        }, status=500)

@login_required(login_url='login')
def get_feedback_ajax(request):
    """Return all feedback as JSON for AJAX request"""
    try:
        feedbacks = Feedback.objects.all().order_by('-created_at')
        feedbacks_data = []
        for feedback in feedbacks:
            feedbacks_data.append({
                'date': feedback.date,
                'category': feedback.category,
                'rating': feedback.rating,
                'message': feedback.message,
                'created_at': feedback.created_at.strftime('%Y-%m-%d'),
                'user_id': feedback.user.id
            })
        return JsonResponse({
            'status': 'success',
            'feedbacks': feedbacks_data
        })
    except Exception as e:
        logging.error(f"Error fetching feedbacks: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': f'An error occurred: {str(e)}'
        }, status=500)


# ============================================================================
# PHASE 6: CONTRACT ANALYSIS API ENDPOINTS
# ============================================================================

from .services import ContractAnalysisService
from .models import ContractAnalysis
import json
import asyncio
from threading import Thread

logger = logging.getLogger(__name__)


@login_required(login_url='login')
@require_http_methods(["POST"])
@csrf_protect
def upload_and_analyze_contract(request):
    """
    Endpoint: POST /api/upload-contract/
    
    Upload a PDF contract and start analysis.
    
    Form Data:
        - contract_file: PDF file
        - contract_type: Type like "SERVICE_AGREEMENT_INDIA"
        - jurisdiction: "INDIA"
        - llm_model: "mixtral-8x7b-32768"
    
    Response:
        {
            "status": "success",
            "contract_id": 1,
            "analysis_id": 1,
            "message": "Contract uploaded and analysis started"
        }
    """
    try:
        # Get form data
        contract_file = request.FILES.get('contract_file')
        contract_type = request.POST.get('contract_type', '')
        jurisdiction = request.POST.get('jurisdiction', 'INDIA')
        llm_model = request.POST.get('llm_model', 'llama-3.1-8b-instant')
        
        # Validate inputs
        if not contract_file:
            return JsonResponse({
                'status': 'error',
                'message': 'No contract file provided'
            }, status=400)
        
        if not contract_type:
            return JsonResponse({
                'status': 'error',
                'message': 'Contract type is required'
            }, status=400)
        
        # Validate file is PDF
        if not contract_file.name.lower().endswith('.pdf'):
            return JsonResponse({
                'status': 'error',
                'message': 'Only PDF files are allowed'
            }, status=400)
        
        # Check file size (max 10MB)
        max_size = 10 * 1024 * 1024
        if contract_file.size > max_size:
            return JsonResponse({
                'status': 'error',
                'message': 'File size exceeds 10MB limit'
            }, status=400)
        
        logger.info("="*80)
        logger.info(f"UPLOAD_AND_ANALYZE_CONTRACT: Starting for user {request.user.username}")
        logger.info(f"  - File: {contract_file.name} ({contract_file.size} bytes)")
        logger.info(f"  - Contract Type: {contract_type}")
        logger.info(f"  - Jurisdiction: {jurisdiction}")
        logger.info(f"  - LLM Model: {llm_model}")
        logger.info("="*80)
        
        # Create Contract and ContractAnalysis records FIRST
        logger.info("Creating Contract and ContractAnalysis database records...")
        contract = Contract.objects.create(
            user=request.user,
            contract_file=contract_file,
            contract_type=contract_type,
            jurisdiction=jurisdiction,
            llm_model=llm_model
        )
        logger.info(f"✓ Contract created with ID: {contract.id}")
        
        contract_analysis = ContractAnalysis.objects.create(
            contract=contract,
            extraction_status='processing'
        )
        logger.info(f"✓ ContractAnalysis created with ID: {contract_analysis.id}")
        
        # Initialize analysis service
        logger.info("Initializing ContractAnalysisService...")
        try:
            service = ContractAnalysisService()
            logger.info("✓ ContractAnalysisService initialized successfully")
        except Exception as e:
            logger.error(f"✗ Failed to initialize ContractAnalysisService: {str(e)}", exc_info=True)
            logger.error(f"  Check: GROQ_API_KEY environment variable is set?")
            raise
        
        # Start analysis in background thread to avoid timeout
        def run_analysis():
            logger.info("="*80)
            logger.info(f"BACKGROUND ANALYSIS THREAD STARTED for analysis_id={contract_analysis.id}")
            logger.info("="*80)
            try:
                logger.info("Calling service.analyze_contract()...")
                result = service.analyze_contract(
                    contract_id=contract.id,
                    contract_analysis_id=contract_analysis.id,
                    contract_type=contract_type,
                    jurisdiction=jurisdiction,
                    llm_model=llm_model
                )
                logger.info("="*80)
                logger.info(f"✓ ANALYSIS COMPLETED SUCCESSFULLY for analysis_id={result.get('analysis_id')}")
                logger.info(f"  - Processing time: {result.get('processing_time', 'N/A')}s")
                logger.info(f"  - Status: {result.get('status')}")
                logger.info("="*80)
            except Exception as e:
                logger.error("="*80)
                logger.error(f"✗ ANALYSIS FAILED for analysis_id={contract_analysis.id}")
                logger.error(f"  Error: {str(e)}")
                logger.error(f"  Type: {type(e).__name__}")
                logger.error("="*80, exc_info=True)
        
        # Run in background thread
        logger.info(f"Starting background thread for analysis...")
        analysis_thread = Thread(target=run_analysis, daemon=True)
        analysis_thread.start()
        logger.info(f"✓ Background thread started (Thread ID: {analysis_thread.ident})")
        
        return JsonResponse({
            'status': 'success',
            'contract_id': contract.id,
            'analysis_id': contract_analysis.id,
            'message': 'Contract uploaded and analysis started'
        })
    
    except Exception as e:
        logger.error(f"Error uploading contract: {str(e)}", exc_info=True)
        return JsonResponse({
            'status': 'error',
            'message': f'Error uploading contract: {str(e)}'
        }, status=500)


@login_required(login_url='login')
@require_http_methods(["GET"])
def get_analysis_results(request, analysis_id):
    """
    Endpoint: GET /api/analysis/<analysis_id>/
    
    Get analysis results and status.
    Frontend polls this endpoint to check if analysis is complete.
    
    Response:
        {
            "status": "success",
            "data": {
                "analysis_status": "completed" | "processing" | "pending" | "failed",
                "summary": {...},
                "clauses": {...},
                "risks": {...},
                "suggestions": {...},
                "processing_time": 45.3,
                "error_message": null
            }
        }
    """
    try:
        # Get analysis record
        contract_analysis = get_object_or_404(ContractAnalysis, id=analysis_id)
        
        # Check permissions - user can only see their own analyses
        if contract_analysis.contract.user != request.user:
            return JsonResponse({
                'status': 'error',
                'message': 'Permission denied'
            }, status=403)
        
        # Parse JSON fields
        summary = {}
        clauses = {}
        risks = {}
        suggestions = {}
        
        if contract_analysis.summary:
            try:
                summary = json.loads(contract_analysis.summary)
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON in summary for analysis {analysis_id}")
        
        if contract_analysis.clauses:
            try:
                clauses = json.loads(contract_analysis.clauses)
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON in clauses for analysis {analysis_id}")
        
        if contract_analysis.risks:
            try:
                risks = json.loads(contract_analysis.risks)
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON in risks for analysis {analysis_id}")
        
        if contract_analysis.suggestions:
            try:
                suggestions = json.loads(contract_analysis.suggestions)
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON in suggestions for analysis {analysis_id}")
        
        return JsonResponse({
            'status': 'success',
            'data': {
                'analysis_status': contract_analysis.extraction_status,
                'summary': summary,
                'clauses': clauses,
                'risks': risks,
                'suggestions': suggestions,
                'processing_time': contract_analysis.processing_time,
                'error_message': contract_analysis.error_message,
                'analysed_at': contract_analysis.analysed_at.isoformat() if contract_analysis.analysed_at else None
            }
        })
    
    except ContractAnalysis.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Analysis not found'
        }, status=404)
    
    except Exception as e:
        logger.error(f"Error fetching analysis: {str(e)}", exc_info=True)
        return JsonResponse({
            'status': 'error',
            'message': f'Error fetching analysis: {str(e)}'
        }, status=500)


@login_required(login_url='login')
@require_http_methods(["GET"])
def get_user_contracts(request):
    """
    Endpoint: GET /api/contracts/
    
    Get list of user's uploaded contracts with analysis status.
    
    Response:
        {
            "status": "success",
            "contracts": [
                {
                    "id": 1,
                    "name": "Service Agreement",
                    "type": "SERVICE_AGREEMENT_INDIA",
                    "uploaded_at": "2026-01-17T10:30:45",
                    "analysis_status": "completed",
                    "analysis_id": 1
                }
            ]
        }
    """
    try:
        # Get user's contracts
        contracts = Contract.objects.filter(user=request.user).order_by('-uploaded_at')
        
        contracts_data = []
        
        for contract in contracts:
            # Get latest analysis for this contract
            latest_analysis = contract.analysis.first()
            
            contract_data = {
                'id': contract.id,
                'name': contract.contract_file.name.split('/')[-1],  # Get filename
                'type': contract.contract_type,
                'jurisdiction': contract.jurisdiction,
                'uploaded_at': contract.uploaded_at.isoformat(),
                'llm_model': contract.llm_model,
                'analysis_status': latest_analysis.extraction_status if latest_analysis else 'pending',
                'analysis_id': latest_analysis.id if latest_analysis else None
            }
            contracts_data.append(contract_data)
        
        return JsonResponse({
            'status': 'success',
            'contracts': contracts_data
        })
    
    except Exception as e:
        logger.error(f"Error fetching contracts: {str(e)}", exc_info=True)
        return JsonResponse({
            'status': 'error',
            'message': f'Error fetching contracts: {str(e)}'
        }, status=500)