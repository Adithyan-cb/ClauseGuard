"""
Contract Clause Mapping Service Module

This module provides utility functions to work with standard contract clauses.
It loads standard clauses from the JSON database and provides helper functions
for clause lookups, validations, and missing clause detection.

Functions:
    - load_standard_clauses(): Load and cache standard clauses from JSON
    - get_standard_clauses_for_type(): Get all standard clauses for a contract type
    - get_critical_clauses_for_type(): Get only critical clauses
    - get_important_clauses_for_type(): Get only important clauses
    - get_optional_clauses_for_type(): Get only optional clauses
    - is_clause_standard(): Check if a clause type is standard for given contract type
    - find_missing_clauses(): Identify which standard clauses are missing from found clauses
    - get_clause_by_id(): Get specific clause by ID
    - get_all_contract_types(): Get list of all supported contract types
"""

import json
import os
import logging
from typing import List, Dict, Any, Optional
from functools import lru_cache

logger = logging.getLogger(__name__)


class ContractClauseMapper:
    """
    Service class to manage standard contract clauses for different contract types.
    Uses lazy loading and caching for performance.
    """
    
    _instance = None
    _standard_clauses = None
    _json_file_path = None
    
    def __new__(cls):
        """Singleton pattern - ensure only one instance exists"""
        if cls._instance is None:
            cls._instance = super(ContractClauseMapper, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the mapper and load standard clauses if not already loaded"""
        if self._standard_clauses is None:
            self._load_clauses()
    
    @staticmethod
    def _get_json_path():
        """Get the absolute path to standard_clauses.json file"""
        if ContractClauseMapper._json_file_path is None:
            # Get the directory where this file is located
            current_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(current_dir)  # Go to myapp directory
            ContractClauseMapper._json_file_path = os.path.join(
                parent_dir, 'data', 'standard_clauses.json'
            )
        return ContractClauseMapper._json_file_path
    
    def _load_clauses(self):
        """Load standard clauses from JSON file"""
        try:
            json_path = self._get_json_path()
            with open(json_path, 'r', encoding='utf-8') as f:
                ContractClauseMapper._standard_clauses = json.load(f)
            logger.info(f"Successfully loaded standard clauses from {json_path}")
        except FileNotFoundError:
            error_msg = f"standard_clauses.json not found at {self._get_json_path()}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON in standard_clauses.json: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
    
    def get_all_contract_types(self) -> List[str]:
        """
        Get list of all supported contract types.
        
        Returns:
            List of contract type keys (e.g., 'SERVICE_AGREEMENT_INDIA')
        """
        return list(self._standard_clauses.keys())
    
    def get_contract_type_name(self, contract_type_key: str) -> Optional[str]:
        """
        Get the human-readable name of a contract type.
        
        Args:
            contract_type_key: Contract type key (e.g., 'SERVICE_AGREEMENT_INDIA')
        
        Returns:
            Human-readable name or None if not found
        """
        if contract_type_key not in self._standard_clauses:
            return None
        return self._standard_clauses[contract_type_key].get('contract_type')
    
    def get_jurisdiction(self, contract_type_key: str) -> Optional[str]:
        """
        Get the jurisdiction for a contract type.
        
        Args:
            contract_type_key: Contract type key (e.g., 'SERVICE_AGREEMENT_INDIA')
        
        Returns:
            Jurisdiction name or None if not found
        """
        if contract_type_key not in self._standard_clauses:
            return None
        return self._standard_clauses[contract_type_key].get('jurisdiction')
    
    def get_standard_clauses_for_type(
        self,
        contract_type: str,
        jurisdiction: str = 'INDIA'
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get all standard clauses for a specific contract type.
        
        Args:
            contract_type: Contract type (e.g., 'SERVICE_AGREEMENT')
            jurisdiction: Jurisdiction (default: 'INDIA')
        
        Returns:
            Dictionary with 'critical_clauses', 'important_clauses', 'optional_clauses'
            Returns empty dict if contract type not found
        """
        key = f"{contract_type}_{jurisdiction}"
        
        if key not in self._standard_clauses:
            logger.warning(f"Contract type '{key}' not found in mapping")
            return {
                'critical_clauses': [],
                'important_clauses': [],
                'optional_clauses': []
            }
        
        contract_data = self._standard_clauses[key]
        return {
            'critical_clauses': contract_data.get('critical_clauses', []),
            'important_clauses': contract_data.get('important_clauses', []),
            'optional_clauses': contract_data.get('optional_clauses', [])
        }
    
    def get_critical_clauses_for_type(
        self,
        contract_type: str,
        jurisdiction: str = 'INDIA'
    ) -> List[Dict[str, Any]]:
        """
        Get only critical clauses for a contract type.
        
        Args:
            contract_type: Contract type (e.g., 'SERVICE_AGREEMENT')
            jurisdiction: Jurisdiction (default: 'INDIA')
        
        Returns:
            List of critical clauses
        """
        clauses = self.get_standard_clauses_for_type(contract_type, jurisdiction)
        return clauses.get('critical_clauses', [])
    
    def get_important_clauses_for_type(
        self,
        contract_type: str,
        jurisdiction: str = 'INDIA'
    ) -> List[Dict[str, Any]]:
        """
        Get only important clauses for a contract type.
        
        Args:
            contract_type: Contract type (e.g., 'SERVICE_AGREEMENT')
            jurisdiction: Jurisdiction (default: 'INDIA')
        
        Returns:
            List of important clauses
        """
        clauses = self.get_standard_clauses_for_type(contract_type, jurisdiction)
        return clauses.get('important_clauses', [])
    
    def get_optional_clauses_for_type(
        self,
        contract_type: str,
        jurisdiction: str = 'INDIA'
    ) -> List[Dict[str, Any]]:
        """
        Get only optional clauses for a contract type.
        
        Args:
            contract_type: Contract type (e.g., 'SERVICE_AGREEMENT')
            jurisdiction: Jurisdiction (default: 'INDIA')
        
        Returns:
            List of optional clauses
        """
        clauses = self.get_standard_clauses_for_type(contract_type, jurisdiction)
        return clauses.get('optional_clauses', [])
    
    def is_clause_standard(
        self,
        clause_type: str,
        contract_type: str,
        jurisdiction: str = 'INDIA'
    ) -> bool:
        """
        Check if a clause type is standard for a given contract type.
        
        Args:
            clause_type: Clause type name (e.g., 'Payment Terms')
            contract_type: Contract type (e.g., 'SERVICE_AGREEMENT')
            jurisdiction: Jurisdiction (default: 'INDIA')
        
        Returns:
            True if clause is standard (in any priority category), False otherwise
        """
        all_clauses = self.get_standard_clauses_for_type(contract_type, jurisdiction)
        
        # Check all categories
        for category in ['critical_clauses', 'important_clauses', 'optional_clauses']:
            for clause in all_clauses.get(category, []):
                if clause.get('type') == clause_type:
                    return True
        
        return False
    
    def get_clause_priority(
        self,
        clause_type: str,
        contract_type: str,
        jurisdiction: str = 'INDIA'
    ) -> Optional[str]:
        """
        Get the priority level of a clause.
        
        Args:
            clause_type: Clause type name
            contract_type: Contract type
            jurisdiction: Jurisdiction (default: 'INDIA')
        
        Returns:
            Priority level ('critical', 'important', 'optional') or None
        """
        all_clauses = self.get_standard_clauses_for_type(contract_type, jurisdiction)
        
        for priority in ['critical_clauses', 'important_clauses', 'optional_clauses']:
            for clause in all_clauses.get(priority, []):
                if clause.get('type') == clause_type:
                    return priority.replace('_clauses', '')
        
        return None
    
    def find_missing_clauses(
        self,
        found_clause_types: List[str],
        contract_type: str,
        jurisdiction: str = 'INDIA'
    ) -> Dict[str, List[str]]:
        """
        Identify which standard clauses are missing from the found clauses.
        
        Args:
            found_clause_types: List of clause types found in contract
            contract_type: Contract type (e.g., 'SERVICE_AGREEMENT')
            jurisdiction: Jurisdiction (default: 'INDIA')
        
        Returns:
            Dictionary with 'missing_critical', 'missing_important', 'missing_optional'
        """
        all_clauses = self.get_standard_clauses_for_type(contract_type, jurisdiction)
        
        # Normalize found clauses to lowercase for comparison
        found_lower = [c.lower() for c in found_clause_types]
        
        missing = {
            'missing_critical': [],
            'missing_important': [],
            'missing_optional': []
        }
        
        # Check critical clauses
        for clause in all_clauses.get('critical_clauses', []):
            clause_name = clause.get('type')
            if clause_name and clause_name.lower() not in found_lower:
                missing['missing_critical'].append(clause_name)
        
        # Check important clauses
        for clause in all_clauses.get('important_clauses', []):
            clause_name = clause.get('type')
            if clause_name and clause_name.lower() not in found_lower:
                missing['missing_important'].append(clause_name)
        
        # Check optional clauses
        for clause in all_clauses.get('optional_clauses', []):
            clause_name = clause.get('type')
            if clause_name and clause_name.lower() not in found_lower:
                missing['missing_optional'].append(clause_name)
        
        return missing
    
    def get_clause_by_id(
        self,
        clause_id: str,
        contract_type: str,
        jurisdiction: str = 'INDIA'
    ) -> Optional[Dict[str, Any]]:
        """
        Get a specific clause by its ID.
        
        Args:
            clause_id: Clause ID (e.g., 'SA_IND_001')
            contract_type: Contract type
            jurisdiction: Jurisdiction (default: 'INDIA')
        
        Returns:
            Clause dictionary or None if not found
        """
        all_clauses = self.get_standard_clauses_for_type(contract_type, jurisdiction)
        
        for category in ['critical_clauses', 'important_clauses', 'optional_clauses']:
            for clause in all_clauses.get(category, []):
                if clause.get('id') == clause_id:
                    return clause
        
        return None
    
    def get_all_clauses_flat(
        self,
        contract_type: str,
        jurisdiction: str = 'INDIA'
    ) -> List[Dict[str, Any]]:
        """
        Get all clauses (all priorities) in a flat list for a contract type.
        
        Args:
            contract_type: Contract type
            jurisdiction: Jurisdiction (default: 'INDIA')
        
        Returns:
            Flat list of all clauses with their priority information
        """
        all_clauses = self.get_standard_clauses_for_type(contract_type, jurisdiction)
        
        flat_list = []
        
        for clause in all_clauses.get('critical_clauses', []):
            flat_list.append(clause)
        
        for clause in all_clauses.get('important_clauses', []):
            flat_list.append(clause)
        
        for clause in all_clauses.get('optional_clauses', []):
            flat_list.append(clause)
        
        return flat_list
    
    def get_clause_recommendations(
        self,
        clause_type: str,
        contract_type: str,
        jurisdiction: str = 'INDIA'
    ) -> Optional[str]:
        """
        Get recommendations for a specific clause type.
        
        Args:
            clause_type: Clause type name
            contract_type: Contract type
            jurisdiction: Jurisdiction (default: 'INDIA')
        
        Returns:
            Recommendations text or None if clause not found
        """
        all_clauses = self.get_standard_clauses_for_type(contract_type, jurisdiction)
        
        for category in ['critical_clauses', 'important_clauses', 'optional_clauses']:
            for clause in all_clauses.get(category, []):
                if clause.get('type') == clause_type:
                    return clause.get('recommendations')
        
        return None
    
    def get_clause_standard_text(
        self,
        clause_type: str,
        contract_type: str,
        jurisdiction: str = 'INDIA'
    ) -> Optional[str]:
        """
        Get the standard/recommended text for a clause type.
        
        Args:
            clause_type: Clause type name
            contract_type: Contract type
            jurisdiction: Jurisdiction (default: 'INDIA')
        
        Returns:
            Standard text or None if clause not found
        """
        all_clauses = self.get_standard_clauses_for_type(contract_type, jurisdiction)
        
        for category in ['critical_clauses', 'important_clauses', 'optional_clauses']:
            for clause in all_clauses.get(category, []):
                if clause.get('type') == clause_type:
                    return clause.get('standard_text')
        
        return None


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================
# Global instance for convenient access
_mapper = None


def get_mapper() -> ContractClauseMapper:
    """
    Get the singleton instance of ContractClauseMapper.
    
    Returns:
        ContractClauseMapper singleton instance
    """
    global _mapper
    if _mapper is None:
        _mapper = ContractClauseMapper()
    return _mapper


# Convenience functions using the global mapper
def get_standard_clauses_for_type(
    contract_type: str,
    jurisdiction: str = 'INDIA'
) -> Dict[str, List[Dict[str, Any]]]:
    """Convenience function - Get all standard clauses for a contract type"""
    return get_mapper().get_standard_clauses_for_type(contract_type, jurisdiction)


def get_critical_clauses_for_type(
    contract_type: str,
    jurisdiction: str = 'INDIA'
) -> List[Dict[str, Any]]:
    """Convenience function - Get only critical clauses"""
    return get_mapper().get_critical_clauses_for_type(contract_type, jurisdiction)


def get_important_clauses_for_type(
    contract_type: str,
    jurisdiction: str = 'INDIA'
) -> List[Dict[str, Any]]:
    """Convenience function - Get only important clauses"""
    return get_mapper().get_important_clauses_for_type(contract_type, jurisdiction)


def get_optional_clauses_for_type(
    contract_type: str,
    jurisdiction: str = 'INDIA'
) -> List[Dict[str, Any]]:
    """Convenience function - Get only optional clauses"""
    return get_mapper().get_optional_clauses_for_type(contract_type, jurisdiction)


def is_clause_standard(
    clause_type: str,
    contract_type: str,
    jurisdiction: str = 'INDIA'
) -> bool:
    """Convenience function - Check if clause is standard for contract type"""
    return get_mapper().is_clause_standard(clause_type, contract_type, jurisdiction)


def find_missing_clauses(
    found_clause_types: List[str],
    contract_type: str,
    jurisdiction: str = 'INDIA'
) -> Dict[str, List[str]]:
    """Convenience function - Find missing clauses"""
    return get_mapper().find_missing_clauses(found_clause_types, contract_type, jurisdiction)


def get_clause_by_id(
    clause_id: str,
    contract_type: str,
    jurisdiction: str = 'INDIA'
) -> Optional[Dict[str, Any]]:
    """Convenience function - Get clause by ID"""
    return get_mapper().get_clause_by_id(clause_id, contract_type, jurisdiction)


def get_all_contract_types() -> List[str]:
    """Convenience function - Get all supported contract types"""
    return get_mapper().get_all_contract_types()


def get_contract_type_name(contract_type_key: str) -> Optional[str]:
    """Convenience function - Get human-readable contract type name"""
    return get_mapper().get_contract_type_name(contract_type_key)


def get_jurisdiction(contract_type_key: str) -> Optional[str]:
    """Convenience function - Get jurisdiction for contract type"""
    return get_mapper().get_jurisdiction(contract_type_key)


def get_clause_priority(
    clause_type: str,
    contract_type: str,
    jurisdiction: str = 'INDIA'
) -> Optional[str]:
    """Convenience function - Get clause priority level"""
    return get_mapper().get_clause_priority(clause_type, contract_type, jurisdiction)


def get_all_clauses_flat(
    contract_type: str,
    jurisdiction: str = 'INDIA'
) -> List[Dict[str, Any]]:
    """Convenience function - Get all clauses in flat list"""
    return get_mapper().get_all_clauses_flat(contract_type, jurisdiction)


def get_clause_recommendations(
    clause_type: str,
    contract_type: str,
    jurisdiction: str = 'INDIA'
) -> Optional[str]:
    """Convenience function - Get clause recommendations"""
    return get_mapper().get_clause_recommendations(clause_type, contract_type, jurisdiction)


def get_clause_standard_text(
    clause_type: str,
    contract_type: str,
    jurisdiction: str = 'INDIA'
) -> Optional[str]:
    """Convenience function - Get standard text for clause"""
    return get_mapper().get_clause_standard_text(clause_type, contract_type, jurisdiction)
