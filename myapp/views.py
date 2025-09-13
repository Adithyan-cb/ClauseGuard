from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request,'home.html')

def login(request):
    return render(request,'login.html')

def register(request):
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