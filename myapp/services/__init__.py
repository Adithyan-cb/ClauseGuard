"""
Contract Analysis Services Package

This package contains all the core service modules for contract analysis:
- contract_processor: PDF text extraction
- chroma_manager: Vector database management
- contract_analysis_service: Main orchestrator (MAIN SERVICE)
- prompts: AI instruction templates
- contract_clause_mapping: Standard clause definitions
- schemas: Pydantic validation schemas
"""

from .contract_processor import ContractProcessor
from .chroma_manager import ChromaManager
from .contract_analysis_service import ContractAnalysisService
from .contract_clause_mapping import (
    get_standard_clauses_for_type,
    get_critical_clauses_for_type,
    is_clause_standard,
    find_missing_clauses,
)

__all__ = [
    'ContractProcessor',
    'ChromaManager',
    'ContractAnalysisService',
    'get_standard_clauses_for_type',
    'get_critical_clauses_for_type',
    'is_clause_standard',
    'find_missing_clauses',
]
