"""
Contract Analysis Services Package

This package contains all the core service modules for contract analysis:
- contract_processor: PDF text extraction
- chroma_manager: Vector database management
- prompts: AI instruction templates
- contract_clause_mapping: Standard clause definitions
"""

from .contract_processor import ContractProcessor
from .chroma_manager import ChromaManager
from .contract_clause_mapping import (
    get_standard_clauses_for_type,
    get_critical_clauses_for_type,
    is_clause_standard,
    find_missing_clauses,
)

__all__ = [
    'ContractProcessor',
    'ChromaManager',
    'get_standard_clauses_for_type',
    'get_critical_clauses_for_type',
    'is_clause_standard',
    'find_missing_clauses',
]
