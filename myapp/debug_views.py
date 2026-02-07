"""
Debug/Diagnostic view for ChromaDB and clause mapping functionality.

URLs:
    /api/debug/chromadb/           - Show all diagnostics
    /api/debug/chromadb/collections/ - List all collections
    /api/debug/chromadb/search/    - Test search functionality
"""

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
import json

from myapp.services.chroma_manager import ChromaManager, CHROMADB_AVAILABLE
from myapp.services.contract_clause_mapping import ContractClauseMapper
from django.conf import settings
import os


@login_required(login_url='login')
@require_http_methods(["GET"])
def chromadb_diagnostics(request):
    """
    Show complete ChromaDB and clause mapping diagnostics.
    
    Endpoint: GET /api/debug/chromadb/
    
    Returns:
        {
            "status": "success",
            "chromadb_available": true,
            "chroma_initialized": true,
            "chroma_path": "/path/to/chroma_data",
            "database_exists": true,
            "database_size_kb": 123.45,
            "contract_types": ["SERVICE_AGREEMENT_INDIA", ...],
            "standard_clauses": {
                "SERVICE_AGREEMENT_INDIA": {
                    "total_clauses": 25,
                    "clauses_in_chromadb": 25
                }
            }
        }
    """
    try:
        result = {
            "status": "success",
            "chromadb_available": CHROMADB_AVAILABLE,
            "diagnostics": {}
        }

        # Only proceed if ChromaDB is available
        if not CHROMADB_AVAILABLE:
            result["chromadb_available"] = False
            result["message"] = "ChromaDB not installed. Install with: pip install chromadb"
            return JsonResponse(result)

        # Initialize ChromaManager
        chroma = ChromaManager()
        result["diagnostics"]["chroma_initialized"] = chroma.available

        # Get persistence directory
        persist_dir = getattr(
            settings,
            'CHROMA_DATA_DIR',
            os.path.join(settings.BASE_DIR, 'chroma_data')
        )
        result["diagnostics"]["chroma_path"] = persist_dir
        result["diagnostics"]["directory_exists"] = os.path.exists(persist_dir)

        # Check database file
        sqlite_file = os.path.join(persist_dir, 'chroma.sqlite3')
        result["diagnostics"]["database_exists"] = os.path.exists(sqlite_file)
        if result["diagnostics"]["database_exists"]:
            size_kb = os.path.getsize(sqlite_file) / 1024
            result["diagnostics"]["database_size_kb"] = round(size_kb, 2)

        # Load standard clauses
        mapper = ContractClauseMapper()
        contract_types = mapper.get_all_contract_types()
        result["diagnostics"]["contract_types_count"] = len(contract_types)
        result["diagnostics"]["contract_types"] = contract_types

        # Check each collection
        standard_clauses_info = {}
        for contract_type_key in contract_types:
            # Get total clauses from JSON
            parts = contract_type_key.rsplit('_', 1)
            if len(parts) == 2:
                contract_type, jurisdiction = parts
            else:
                contract_type = contract_type_key
                jurisdiction = 'INDIA'

            all_clauses = mapper.get_all_clauses_flat(contract_type, jurisdiction)
            
            # Check how many are in ChromaDB
            collection = chroma.get_or_create_collection(contract_type_key)
            chromadb_count = 0
            
            if collection:
                try:
                    result_data = collection.get()
                    chromadb_count = len(result_data['ids']) if result_data['ids'] else 0
                except:
                    chromadb_count = 0

            standard_clauses_info[contract_type_key] = {
                "total_in_json": len(all_clauses),
                "stored_in_chromadb": chromadb_count,
                "percentage": round((chromadb_count / len(all_clauses) * 100) if all_clauses else 0, 1)
            }

        result["diagnostics"]["standard_clauses"] = standard_clauses_info

        return JsonResponse(result)

    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=500)


@login_required(login_url='login')
@require_http_methods(["GET"])
def chromadb_collections(request):
    """
    List all collections and their contents.
    
    Endpoint: GET /api/debug/chromadb/collections/
    
    Query params:
        - collection: specific collection name to inspect
    
    Returns:
        {
            "status": "success",
            "collections": {
                "SERVICE_AGREEMENT_INDIA": {
                    "document_count": 25,
                    "sample_documents": [...]
                }
            }
        }
    """
    try:
        if not CHROMADB_AVAILABLE:
            return JsonResponse({
                "status": "error",
                "message": "ChromaDB not available"
            }, status=400)

        chroma = ChromaManager()
        mapper = ContractClauseMapper()
        contract_types = mapper.get_all_contract_types()

        # If specific collection requested
        specific_collection = request.GET.get('collection')
        if specific_collection:
            contract_types = [specific_collection] if specific_collection in contract_types else []

        collections_info = {}

        for contract_type_key in contract_types:
            collection = chroma.get_or_create_collection(contract_type_key)
            
            if collection:
                try:
                    result_data = collection.get()
                    
                    sample_docs = []
                    for i, (id_, doc, metadata) in enumerate(
                        zip(
                            result_data['ids'][:5] if result_data['ids'] else [],
                            result_data['documents'][:5] if result_data['documents'] else [],
                            result_data['metadatas'][:5] if result_data['metadatas'] else []
                        ),
                        1
                    ):
                        sample_docs.append({
                            "id": id_,
                            "type": metadata.get('type', 'N/A'),
                            "text_preview": doc[:100] + "...",
                            "jurisdiction": metadata.get('jurisdiction', 'N/A')
                        })

                    doc_count = len(result_data['ids']) if result_data['ids'] else 0
                    collections_info[contract_type_key] = {
                        "document_count": doc_count,
                        "sample_documents": sample_docs
                    }
                except Exception as e:
                    collections_info[contract_type_key] = {
                        "error": str(e)
                    }

        return JsonResponse({
            "status": "success",
            "collections": collections_info
        })

    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=500)


@login_required(login_url='login')
@require_http_methods(["POST"])
def chromadb_test_search(request):
    """
    Test ChromaDB search functionality.
    
    Endpoint: POST /api/debug/chromadb/search/
    
    Request body:
        {
            "query": "payment terms",
            "collection": "SERVICE_AGREEMENT_INDIA",
            "top_k": 3
        }
    
    Returns:
        {
            "status": "success",
            "query": "payment terms",
            "collection": "SERVICE_AGREEMENT_INDIA",
            "results": [
                {
                    "type": "Payment Terms",
                    "text_preview": "...",
                    "similarity": 0.95,
                    "jurisdiction": "INDIA"
                }
            ]
        }
    """
    try:
        if not CHROMADB_AVAILABLE:
            return JsonResponse({
                "status": "error",
                "message": "ChromaDB not available"
            }, status=400)

        data = json.loads(request.body)
        query_text = data.get('query', '')
        collection_name = data.get('collection', 'SERVICE_AGREEMENT_INDIA')
        top_k = int(data.get('top_k', 3))

        if not query_text:
            return JsonResponse({
                "status": "error",
                "message": "Query text is required"
            }, status=400)

        chroma = ChromaManager()
        results = chroma.search_similar_clauses(
            collection_name=collection_name,
            query_text=query_text,
            top_k=top_k
        )

        formatted_results = []
        for doc, metadata, distance in zip(
            results['documents'],
            results['metadatas'],
            results['distances']
        ):
            similarity = 1 - distance if distance else 0  # Convert distance to similarity
            formatted_results.append({
                "type": metadata.get('type', 'N/A'),
                "text_preview": doc[:200] + "...",
                "similarity": round(similarity, 4),
                "jurisdiction": metadata.get('jurisdiction', 'N/A')
            })

        return JsonResponse({
            "status": "success",
            "query": query_text,
            "collection": collection_name,
            "results_found": len(formatted_results),
            "results": formatted_results
        })

    except json.JSONDecodeError:
        return JsonResponse({
            "status": "error",
            "message": "Invalid JSON"
        }, status=400)
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=500)


@login_required(login_url='login')
@require_http_methods(["POST"])
def chromadb_initialize(request):
    """
    Initialize/load all standard clauses into ChromaDB.
    
    Endpoint: POST /api/debug/chromadb/initialize/
    
    Returns:
        {
            "status": "success",
            "clauses_added": 500,
            "collections_initialized": 10
        }
    """
    try:
        if not CHROMADB_AVAILABLE:
            return JsonResponse({
                "status": "error",
                "message": "ChromaDB not available"
            }, status=400)

        chroma = ChromaManager()
        mapper = ContractClauseMapper()
        contract_types = mapper.get_all_contract_types()

        total_added = 0
        collections_initialized = 0

        for contract_type_key in contract_types:
            # Parse contract type and jurisdiction
            parts = contract_type_key.rsplit('_', 1)
            if len(parts) == 2:
                contract_type, jurisdiction = parts
            else:
                contract_type = contract_type_key
                jurisdiction = 'INDIA'

            # Get all clauses for this type
            all_clauses = mapper.get_all_clauses_flat(contract_type, jurisdiction)

            if not all_clauses:
                continue

            # Prepare clauses for ChromaDB
            clauses_for_chroma = []
            for clause in all_clauses:
                clauses_for_chroma.append({
                    'type': clause.get('type', ''),
                    'text': clause.get('standard_text', clause.get('text', '')),
                    'jurisdiction': jurisdiction,
                    'contract_type': contract_type,
                    'recommendations': clause.get('recommendations', '')
                })

            try:
                chroma.add_standard_clauses(
                    collection_name=contract_type_key,
                    clauses=clauses_for_chroma
                )
                total_added += len(clauses_for_chroma)
                collections_initialized += 1
            except Exception as e:
                pass  # Continue with next collection

        return JsonResponse({
            "status": "success",
            "message": f"Successfully initialized {collections_initialized} collections",
            "clauses_added": total_added,
            "collections_initialized": collections_initialized
        })

    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=500)
