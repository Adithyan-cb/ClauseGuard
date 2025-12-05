from django.urls import path
from .views import home,login_user,register,admin_dashboard,user_dashboard,view_contracts,upload_contract,send_complaint,feedback,user_logout
urlpatterns = [
   path('',home,name='home'),
   path('login/',login_user,name="login"),
   path('register/',register,name="register"),
   path('admin-dashboard/',admin_dashboard,name="admin-dashboard"),
   path('user-dashboard/',user_dashboard,name='user-dashboard'),
   path('view-contracts/',view_contracts,name='view-contracts'),
   path('upload-contract/',upload_contract,name='upload-contract'),
   path('send-complaint/',send_complaint,name='send-complaint'),
   path('send-feedback/',feedback,name='send-feedback'),
   path('logout/',user_logout,name='logout'),
]