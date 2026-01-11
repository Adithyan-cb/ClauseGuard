"""
Contract Clause Mapping Module

Defines standard clauses for different contract types and jurisdictions.
Used to identify missing clauses and filter relevant suggestions.
"""

import logging

logger = logging.getLogger(__name__)

# ============================================================================
# CONTRACT TYPE MAPPING
# ============================================================================
# Each contract type has critical, important, and optional clauses
# Critical = Must have, Important = Should have, Optional = Nice to have

CONTRACT_TYPE_MAPPING = {
    # SERVICE AGREEMENT FOR INDIA
    'SERVICE_AGREEMENT_INDIA': {
        'critical_clauses': [
            'Scope of Services',
            'Payment Terms',
            'Term and Termination',
            'Confidentiality',
            'Intellectual Property Rights',
            'Liability Limitation'
        ],
        'important_clauses': [
            'Service Level Agreement (SLA)',
            'Insurance Requirements',
            'Dispute Resolution',
            'Amendment Procedures',
            'Data Protection and Security'
        ],
        'optional_clauses': [
            'Renewal Terms',
            'Compliance Requirements',
            'Performance Metrics'
        ]
    },
    
    # EMPLOYMENT CONTRACT FOR INDIA
    'EMPLOYMENT_INDIA': {
        'critical_clauses': [
            'Job Title and Responsibilities',
            'Compensation and Benefits',
            'Working Hours',
            'Termination Clause',
            'Confidentiality',
            'Non-Compete Agreement'
        ],
        'important_clauses': [
            'Leave Policy',
            'Performance Management',
            'Dispute Resolution',
            'Tax and Compliance',
            'Notice Period'
        ],
        'optional_clauses': [
            'Career Development',
            'Training and Development',
            'Grievance Redressal'
        ]
    },
    
    # NDA (NON-DISCLOSURE AGREEMENT) FOR INDIA
    'NDA_INDIA': {
        'critical_clauses': [
            'Definition of Confidential Information',
            'Permitted Disclosures',
            'Term of Confidentiality',
            'Return of Information',
            'Consequences of Breach',
            'Exceptions to Confidentiality'
        ],
        'important_clauses': [
            'Jurisdiction and Governing Law',
            'Severability',
            'Remedies for Breach',
            'No License Granted'
        ],
        'optional_clauses': [
            'Insurance',
            'Indemnification',
            'Waiver'
        ]
    },
    
    # PARTNERSHIP AGREEMENT FOR INDIA
    'PARTNERSHIP_INDIA': {
        'critical_clauses': [
            'Partnership Structure and Rights',
            'Capital Contribution',
            'Profit and Loss Sharing',
            'Decision Making and Governance',
            'Dispute Resolution',
            'Termination and Exit Clause'
        ],
        'important_clauses': [
            'Liability and Indemnification',
            'Confidentiality',
            'Non-Compete',
            'Amendment Procedures'
        ],
        'optional_clauses': [
            'Succession Planning',
            'Buyout Provisions',
            'Additional Partners'
        ]
    },
    
    # VENDOR AGREEMENT FOR INDIA
    'VENDOR_AGREEMENT_INDIA': {
        'critical_clauses': [
            'Scope of Supplies/Services',
            'Quality and Specifications',
            'Pricing and Payment Terms',
            'Delivery Schedule',
            'Warranty and Liability',
            'Termination Clause'
        ],
        'important_clauses': [
            'Inspection and Acceptance',
            'Returns and Refunds',
            'Intellectual Property Rights',
            'Confidentiality',
            'Insurance'
        ],
        'optional_clauses': [
            'Performance Discounts',
            'Volume Commitments',
            'Extension Options'
        ]
    },
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_standard_clauses_for_type(contract_type: str, jurisdiction: str = 'INDIA') -> list:
    """
    Get all standard clauses for a given contract type and jurisdiction.
    
    Combines critical, important, and optional clauses into one list.
    
    Args:
        contract_type (str): Type of contract
            Examples: 'SERVICE_AGREEMENT', 'EMPLOYMENT', 'NDA', 'PARTNERSHIP', 'VENDOR_AGREEMENT'
        jurisdiction (str): Jurisdiction (default: 'INDIA')
            Examples: 'INDIA', 'US', 'UK'
    
    Returns:
        list: All standard clause names for this contract type
        
    Example:
        >>> clauses = get_standard_clauses_for_type('SERVICE_AGREEMENT', 'INDIA')
        >>> print(clauses)
        ['Scope of Services', 'Payment Terms', 'Term and Termination', ...]
    """
    key = f"{contract_type}_{jurisdiction}"
    
    if key not in CONTRACT_TYPE_MAPPING:
        logger.warning(f"Contract type '{key}' not found in mapping")
        return []
    
    mapping = CONTRACT_TYPE_MAPPING[key]
    all_clauses = (
        mapping.get('critical_clauses', []) +
        mapping.get('important_clauses', []) +
        mapping.get('optional_clauses', [])
    )
    
    return all_clauses


def get_critical_clauses_for_type(contract_type: str, jurisdiction: str = 'INDIA') -> list:
    """
    Get only the critical (must-have) clauses for a contract type.
    
    Critical clauses are essential and their absence is a major risk.
    
    Args:
        contract_type (str): Type of contract
        jurisdiction (str): Jurisdiction (default: 'INDIA')
    
    Returns:
        list: Only critical clause names
        
    Example:
        >>> clauses = get_critical_clauses_for_type('SERVICE_AGREEMENT', 'INDIA')
        >>> print(clauses)
        ['Scope of Services', 'Payment Terms', 'Term and Termination', ...]
    """
    key = f"{contract_type}_{jurisdiction}"
    
    if key not in CONTRACT_TYPE_MAPPING:
        logger.warning(f"Contract type '{key}' not found in mapping")
        return []
    
    return CONTRACT_TYPE_MAPPING[key].get('critical_clauses', [])


def get_important_clauses_for_type(contract_type: str, jurisdiction: str = 'INDIA') -> list:
    """
    Get the important (should-have) clauses for a contract type.
    
    Important clauses provide significant protections and should be present.
    
    Args:
        contract_type (str): Type of contract
        jurisdiction (str): Jurisdiction (default: 'INDIA')
    
    Returns:
        list: Only important clause names
    """
    key = f"{contract_type}_{jurisdiction}"
    
    if key not in CONTRACT_TYPE_MAPPING:
        logger.warning(f"Contract type '{key}' not found in mapping")
        return []
    
    return CONTRACT_TYPE_MAPPING[key].get('important_clauses', [])


def is_clause_standard(
    clause_type: str,
    contract_type: str,
    jurisdiction: str = 'INDIA'
) -> bool:
    """
    Check if a clause type is standard for the given contract type.
    
    Useful for determining if a clause should exist in the contract.
    
    Args:
        clause_type (str): Name of the clause
            Example: "Payment Terms"
        contract_type (str): Type of contract
            Example: "SERVICE_AGREEMENT"
        jurisdiction (str): Jurisdiction (default: 'INDIA')
    
    Returns:
        bool: True if clause is standard, False otherwise
        
    Example:
        >>> is_standard = is_clause_standard('Payment Terms', 'SERVICE_AGREEMENT', 'INDIA')
        >>> print(is_standard)
        True
    """
    standard_clauses = get_standard_clauses_for_type(contract_type, jurisdiction)
    return clause_type in standard_clauses


def find_missing_clauses(
    found_clauses: list,
    contract_type: str,
    jurisdiction: str = 'INDIA'
) -> dict:
    """
    Identify which standard clauses are missing from the contract.
    
    Compares found clauses against the standard mapping to identify gaps.
    
    Args:
        found_clauses (list): List of clause names found in the contract
            Example: ['Scope of Services', 'Payment Terms', 'Confidentiality']
        contract_type (str): Type of contract
        jurisdiction (str): Jurisdiction (default: 'INDIA')
    
    Returns:
        dict: Dictionary with missing clauses organized by priority:
        {
            "missing_critical": ["Clause 1", "Clause 2"],
            "missing_important": ["Clause 3"],
            "missing_optional": [],
            "total_missing": 3
        }
        
    Example:
        >>> found = ['Scope of Services', 'Payment Terms']
        >>> missing = find_missing_clauses(found, 'SERVICE_AGREEMENT', 'INDIA')
        >>> print(missing['missing_critical'])
        ['Term and Termination', 'Confidentiality', ...]
    """
    key = f"{contract_type}_{jurisdiction}"
    
    if key not in CONTRACT_TYPE_MAPPING:
        logger.warning(f"Contract type '{key}' not found in mapping")
        return {
            'missing_critical': [],
            'missing_important': [],
            'missing_optional': [],
            'total_missing': 0
        }
    
    mapping = CONTRACT_TYPE_MAPPING[key]
    
    # Normalize found clauses to lowercase for comparison
    found_lower = [c.lower() for c in found_clauses]
    
    # Find missing critical clauses
    missing_critical = [
        clause for clause in mapping.get('critical_clauses', [])
        if clause.lower() not in found_lower
    ]
    
    # Find missing important clauses
    missing_important = [
        clause for clause in mapping.get('important_clauses', [])
        if clause.lower() not in found_lower
    ]
    
    # Find missing optional clauses
    missing_optional = [
        clause for clause in mapping.get('optional_clauses', [])
        if clause.lower() not in found_lower
    ]
    
    total_missing = len(missing_critical) + len(missing_important) + len(missing_optional)
    
    return {
        'missing_critical': missing_critical,
        'missing_important': missing_important,
        'missing_optional': missing_optional,
        'total_missing': total_missing
    }


def get_all_supported_contract_types() -> list:
    """
    Get list of all supported contract types.
    
    Returns:
        list: List of contract type keys in the mapping
        
    Example:
        >>> types = get_all_supported_contract_types()
        >>> print(types)
        ['SERVICE_AGREEMENT_INDIA', 'EMPLOYMENT_INDIA', 'NDA_INDIA', ...]
    """
    return list(CONTRACT_TYPE_MAPPING.keys())


def get_contract_type_info(contract_type: str, jurisdiction: str = 'INDIA') -> dict:
    """
    Get complete information about a contract type.
    
    Returns all critical, important, and optional clauses in one dictionary.
    
    Args:
        contract_type (str): Type of contract
        jurisdiction (str): Jurisdiction (default: 'INDIA')
    
    Returns:
        dict: Complete clause mapping for the contract type
        
    Example:
        >>> info = get_contract_type_info('SERVICE_AGREEMENT', 'INDIA')
        >>> print(info.keys())
        dict_keys(['critical_clauses', 'important_clauses', 'optional_clauses'])
    """
    key = f"{contract_type}_{jurisdiction}"
    
    if key not in CONTRACT_TYPE_MAPPING:
        logger.warning(f"Contract type '{key}' not found in mapping")
        return {
            'critical_clauses': [],
            'important_clauses': [],
            'optional_clauses': []
        }
    
    return CONTRACT_TYPE_MAPPING[key]
