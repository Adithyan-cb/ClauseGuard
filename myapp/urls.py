from django.urls import path
from .views import (
    home, login_user, register, admin_dashboard, user_dashboard, view_contracts,
    upload_contract, send_complaint, feedback, user_logout, view_contract, 
    download_contract, get_users_ajax, get_contracts_ajax, get_complaints_ajax, 
    get_feedback_ajax, upload_and_analyze_contract, get_analysis_results, 
    get_user_contracts, get_analysis_data
)
from .debug_views import (
    chromadb_diagnostics, chromadb_collections, chromadb_test_search, chromadb_initialize
)

urlpatterns = [
   path('', home, name='home'),
   path('login/', login_user, name="login"),
   path('register/', register, name="register"),
   path('admin-dashboard/', admin_dashboard, name="admin-dashboard"),
   path('user-dashboard/', user_dashboard, name='user-dashboard'),
   path('view-contracts/', view_contracts, name='view-contracts'),
   path('upload-contract/', upload_contract, name='upload-contract'),
   path('send-complaint/', send_complaint, name='send-complaint'),
   path('send-feedback/', feedback, name='send-feedback'),
   path('logout/', user_logout, name='logout'),
   path('contract/<int:contract_id>/view/', view_contract, name='view-contract'),
   path('contract/<int:contract_id>/download/', download_contract, name='download-contract'),
   
   # Legacy AJAX endpoints
   path('api/get-users/', get_users_ajax, name='get-users-ajax'),
   path('api/get-contracts/', get_contracts_ajax, name='get-contracts-ajax'),
   path('api/get-complaints/', get_complaints_ajax, name='get-complaints-ajax'),
   path('api/get-feedback/', get_feedback_ajax, name='get-feedback-ajax'),
   
   # Phase 6: Contract Analysis API Endpoints
   path('api/upload-contract/', upload_and_analyze_contract, name='api-upload-contract'),
   path('api/analysis/<int:analysis_id>/', get_analysis_results, name='api-get-analysis'),
   path('api/analysis/<int:analysis_id>/data/', get_analysis_data, name='api-get-analysis-data'),
   path('api/contracts/', get_user_contracts, name='api-get-contracts'),
   
   # Debug: ChromaDB Diagnostics
   path('api/debug/chromadb/', chromadb_diagnostics, name='api-chromadb-diagnostics'),
   path('api/debug/chromadb/collections/', chromadb_collections, name='api-chromadb-collections'),
   path('api/debug/chromadb/search/', chromadb_test_search, name='api-chromadb-search'),
   path('api/debug/chromadb/initialize/', chromadb_initialize, name='api-chromadb-initialize'),
]