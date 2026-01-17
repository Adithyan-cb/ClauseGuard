"""
Data Validation Schemas for Contract Analysis
Phase 4: Data Validation Layer

This module defines Pydantic models that validate all AI responses
before they reach the database and frontend. Ensures consistent,
predictable JSON structure for all contract analysis results.

Author: ClauseGuard Development Team
Date: January 12, 2026
"""

from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from typing import List, Optional
from enum import Enum


# ========== ENUMS ==========

class RiskLevel(str, Enum):
    """Risk severity levels"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class Priority(str, Enum):
    """Priority levels for suggestions"""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class ContractType(str, Enum):
    """Supported contract types"""
    SERVICE_AGREEMENT = "SERVICE_AGREEMENT"
    EMPLOYMENT = "EMPLOYMENT"
    NDA = "NDA"
    PARTNERSHIP = "PARTNERSHIP"
    VENDOR_AGREEMENT = "VENDOR_AGREEMENT"


class AnalysisStatus(str, Enum):
    """Status of analysis completion"""
    SUCCESS = "success"
    PARTIAL = "partial"
    ERROR = "error"


# ========== INDIVIDUAL ITEM MODELS ==========

class ClauseItem(BaseModel):
    """
    Represents a single clause found in a contract.
    
    Attributes:
        id: Unique identifier for this clause
        type: Type/name of the clause (e.g., "Payment Terms", "Confidentiality")
        text: Full text of the clause as extracted from contract
    """
    id: int
    type: str
    text: str
    
    model_config = ConfigDict(str_strip_whitespace=True)


class RiskItem(BaseModel):
    """
    Represents a single identified risk or issue in the contract.
    
    Attributes:
        id: Unique identifier for this risk
        clause_type: Type of clause where risk was identified
        risk_level: Severity level (LOW, MEDIUM, HIGH)
        issue: Brief title of the issue
        description: Detailed explanation of the problem
        impact: Business/legal impact of this risk
    """
    id: int
    clause_type: str
    risk_level: RiskLevel
    issue: str
    description: str
    impact: str
    
    model_config = ConfigDict(str_strip_whitespace=True)


class SuggestionItem(BaseModel):
    """
    Represents a single improvement suggestion for the contract.
    
    Attributes:
        id: Unique identifier for this suggestion
        priority: Priority level (HIGH, MEDIUM, LOW)
        category: Category of suggestion (Missing Clause, Wording, Protection, etc.)
        current_state: What's currently in the contract
        suggested_text: Proposed text or change
        business_impact: Why this suggestion matters
    """
    id: int
    priority: Priority
    category: str
    current_state: str
    suggested_text: str
    business_impact: str
    
    model_config = ConfigDict(str_strip_whitespace=True)


# ========== OUTPUT RESPONSE MODELS ==========

class SummaryOutput(BaseModel):
    """
    Complete summary of the contract from AI analysis.
    
    Attributes:
        summary: Main overview text of the contract
        contract_type: Type of contract identified
        parties: List of parties involved in the contract
        duration: Contract duration/term
        key_obligations: List of main obligations
        financial_terms: Payment and cost details
        jurisdiction: Applicable jurisdiction(s)
    """
    summary: str
    contract_type: str
    parties: List[str] = Field(default_factory=list)
    duration: str = ""
    key_obligations: List[str] = Field(default_factory=list)
    financial_terms: str = ""
    jurisdiction: str = ""
    
    model_config = ConfigDict(str_strip_whitespace=True)


class ClausesOutput(BaseModel):
    """
    Complete response containing all clauses extracted from contract.
    
    Attributes:
        clauses: List of ClauseItem objects found in contract
        total_clauses: Auto-calculated count of clauses
    """
    clauses: List[ClauseItem] = Field(default_factory=list)
    total_clauses: int = 0
    
    @model_validator(mode='after')
    def calculate_total(self):
        """Auto-calculate total clauses from clauses list"""
        self.total_clauses = len(self.clauses)
        return self


class RisksOutput(BaseModel):
    """
    Complete response containing all identified risks and missing clauses.
    
    Attributes:
        risks: List of RiskItem objects
        missing_clauses: List of clause types that should exist but don't
        total_risks: Auto-calculated count of risks
        total_missing: Auto-calculated count of missing clauses
    """
    risks: List[RiskItem] = Field(default_factory=list)
    missing_clauses: List[str] = Field(default_factory=list)
    total_risks: int = 0
    total_missing: int = 0
    
    @model_validator(mode='after')
    def calculate_totals(self):
        """Auto-calculate total risks and missing clauses"""
        self.total_risks = len(self.risks)
        self.total_missing = len(self.missing_clauses)
        return self


class SuggestionsOutput(BaseModel):
    """
    Complete response containing all improvement suggestions.
    
    Attributes:
        suggestions: List of SuggestionItem objects
        total_suggestions: Auto-calculated count of suggestions
    """
    suggestions: List[SuggestionItem] = Field(default_factory=list)
    total_suggestions: int = 0
    
    @model_validator(mode='after')
    def calculate_total(self):
        """Auto-calculate total suggestions from suggestions list"""
        self.total_suggestions = len(self.suggestions)
        return self


# ========== COMPLETE ANALYSIS MODEL ==========

class CompleteAnalysisOutput(BaseModel):
    """
    Complete analysis result combining all four response types.
    
    This is the main response object returned after contract analysis.
    Contains summary, clauses, risks, and suggestions all in one structure.
    
    Attributes:
        summary: SummaryOutput object with contract overview
        clauses: ClausesOutput object with extracted clauses
        risks: RisksOutput object with identified risks
        suggestions: SuggestionsOutput object with improvement suggestions
        processing_time: Time taken to complete analysis in seconds
        status: Overall status of analysis (success, partial, error)
    """
    summary: Optional[SummaryOutput] = None
    clauses: Optional[ClausesOutput] = None
    risks: Optional[RisksOutput] = None
    suggestions: Optional[SuggestionsOutput] = None
    processing_time: float = 0.0
    status: AnalysisStatus = AnalysisStatus.SUCCESS
    
    model_config = ConfigDict(str_strip_whitespace=True)


# ========== UTILITY FUNCTIONS ==========

def create_empty_analysis() -> CompleteAnalysisOutput:
    """
    Create an empty but valid CompleteAnalysisOutput with default values.
    
    Useful when analysis fails partially or completely, ensuring
    frontend still receives valid (though empty) JSON structure.
    
    Returns:
        CompleteAnalysisOutput with empty/default values
    """
    return CompleteAnalysisOutput(
        summary=SummaryOutput(summary="", contract_type=""),
        clauses=ClausesOutput(),
        risks=RisksOutput(),
        suggestions=SuggestionsOutput(),
        processing_time=0.0,
        status=AnalysisStatus.ERROR
    )


def create_error_analysis(processing_time: float = 0.0) -> CompleteAnalysisOutput:
    """
    Create an error analysis response when something goes wrong.
    
    Args:
        processing_time: Time spent before error occurred
        
    Returns:
        CompleteAnalysisOutput marked as ERROR status
    """
    return CompleteAnalysisOutput(
        summary=None,
        clauses=None,
        risks=None,
        suggestions=None,
        processing_time=processing_time,
        status=AnalysisStatus.ERROR
    )
