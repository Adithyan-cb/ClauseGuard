"""
Test Suite for Phase 4: Data Validation Layer
Tests all Pydantic schemas for contract analysis

Tests the following:
- Individual item models (ClauseItem, RiskItem, SuggestionItem)
- Output response models (SummaryOutput, ClausesOutput, RisksOutput, SuggestionsOutput)
- Complete analysis model
- Enums and validators
- JSON serialization/deserialization
- Utility functions

Author: ClauseGuard Development Team
Date: January 12, 2026
"""

import json
import unittest
from myapp.services.schemas import (
    RiskLevel, Priority, ContractType, AnalysisStatus,
    ClauseItem, RiskItem, SuggestionItem,
    SummaryOutput, ClausesOutput, RisksOutput, SuggestionsOutput,
    CompleteAnalysisOutput, create_empty_analysis, create_error_analysis
)
from pydantic import ValidationError


class TestEnums(unittest.TestCase):
    """Test all enum definitions"""
    
    def test_risk_level_values(self):
        """Test RiskLevel enum has correct values"""
        self.assertEqual(RiskLevel.LOW.value, "LOW")
        self.assertEqual(RiskLevel.MEDIUM.value, "MEDIUM")
        self.assertEqual(RiskLevel.HIGH.value, "HIGH")
    
    def test_priority_values(self):
        """Test Priority enum has correct values"""
        self.assertEqual(Priority.HIGH.value, "HIGH")
        self.assertEqual(Priority.MEDIUM.value, "MEDIUM")
        self.assertEqual(Priority.LOW.value, "LOW")
    
    def test_contract_type_values(self):
        """Test ContractType enum has correct values"""
        self.assertEqual(ContractType.SERVICE_AGREEMENT.value, "SERVICE_AGREEMENT")
        self.assertEqual(ContractType.EMPLOYMENT.value, "EMPLOYMENT")
        self.assertEqual(ContractType.NDA.value, "NDA")
        self.assertEqual(ContractType.PARTNERSHIP.value, "PARTNERSHIP")
        self.assertEqual(ContractType.VENDOR_AGREEMENT.value, "VENDOR_AGREEMENT")
    
    def test_analysis_status_values(self):
        """Test AnalysisStatus enum has correct values"""
        self.assertEqual(AnalysisStatus.SUCCESS.value, "success")
        self.assertEqual(AnalysisStatus.PARTIAL.value, "partial")
        self.assertEqual(AnalysisStatus.ERROR.value, "error")


class TestClauseItem(unittest.TestCase):
    """Test ClauseItem model"""
    
    def test_valid_clause_item(self):
        """Test creating a valid ClauseItem"""
        clause = ClauseItem(
            id=1,
            type="Payment Terms",
            text="Payment due within 30 days"
        )
        self.assertEqual(clause.id, 1)
        self.assertEqual(clause.type, "Payment Terms")
        self.assertEqual(clause.text, "Payment due within 30 days")
    
    def test_clause_item_missing_id(self):
        """Test ClauseItem validation fails without id"""
        with self.assertRaises(ValidationError):
            ClauseItem(type="Payment Terms", text="Some text")
    
    def test_clause_item_missing_type(self):
        """Test ClauseItem validation fails without type"""
        with self.assertRaises(ValidationError):
            ClauseItem(id=1, text="Some text")
    
    def test_clause_item_missing_text(self):
        """Test ClauseItem validation fails without text"""
        with self.assertRaises(ValidationError):
            ClauseItem(id=1, type="Payment Terms")
    
    def test_clause_item_whitespace_stripping(self):
        """Test that whitespace is stripped from string fields"""
        clause = ClauseItem(
            id=1,
            type="  Payment Terms  ",
            text="  Some text  "
        )
        self.assertEqual(clause.type, "Payment Terms")
        self.assertEqual(clause.text, "Some text")
    
    def test_clause_item_json_serialization(self):
        """Test ClauseItem can be serialized to JSON"""
        clause = ClauseItem(id=1, type="Test", text="Text")
        json_str = clause.model_dump_json()
        # Verify the JSON contains the expected fields
        self.assertIn('"id"', json_str)
        self.assertIn('"type"', json_str)
        self.assertIn('"Test"', json_str)
        self.assertIn('"text"', json_str)


class TestRiskItem(unittest.TestCase):
    """Test RiskItem model"""
    
    def test_valid_risk_item(self):
        """Test creating a valid RiskItem"""
        risk = RiskItem(
            id=1,
            clause_type="Payment Terms",
            risk_level=RiskLevel.HIGH,
            issue="Aggressive payment terms",
            description="15 days is unusually short for India",
            impact="Could damage vendor relationships"
        )
        self.assertEqual(risk.id, 1)
        self.assertEqual(risk.clause_type, "Payment Terms")
        self.assertEqual(risk.risk_level, RiskLevel.HIGH)
        self.assertEqual(risk.issue, "Aggressive payment terms")
    
    def test_risk_item_with_string_risk_level(self):
        """Test RiskItem accepts string risk level and converts to enum"""
        risk = RiskItem(
            id=1,
            clause_type="Liability",
            risk_level="MEDIUM",  # String instead of enum
            issue="Low liability cap",
            description="Cap is only 1 month",
            impact="Insufficient protection"
        )
        self.assertEqual(risk.risk_level, RiskLevel.MEDIUM)
    
    def test_risk_item_invalid_risk_level(self):
        """Test RiskItem validation fails with invalid risk level"""
        with self.assertRaises(ValidationError):
            RiskItem(
                id=1,
                clause_type="Test",
                risk_level="CRITICAL",  # Invalid value
                issue="Test issue",
                description="Test",
                impact="Test"
            )
    
    def test_risk_item_missing_required_field(self):
        """Test RiskItem validation fails without required field"""
        with self.assertRaises(ValidationError):
            RiskItem(
                id=1,
                clause_type="Test",
                risk_level=RiskLevel.HIGH,
                issue="Test",
                # missing description
                impact="Test"
            )


class TestSuggestionItem(unittest.TestCase):
    """Test SuggestionItem model"""
    
    def test_valid_suggestion_item(self):
        """Test creating a valid SuggestionItem"""
        suggestion = SuggestionItem(
            id=1,
            priority=Priority.HIGH,
            category="Missing Clause",
            current_state="SLA is not mentioned",
            suggested_text="Add SLA clause defining uptime guarantees",
            business_impact="Protects service quality"
        )
        self.assertEqual(suggestion.id, 1)
        self.assertEqual(suggestion.priority, Priority.HIGH)
        self.assertEqual(suggestion.category, "Missing Clause")
    
    def test_suggestion_item_with_string_priority(self):
        """Test SuggestionItem accepts string priority"""
        suggestion = SuggestionItem(
            id=1,
            priority="LOW",  # String instead of enum
            category="Clarification",
            current_state="Current",
            suggested_text="Suggested",
            business_impact="Impact"
        )
        self.assertEqual(suggestion.priority, Priority.LOW)
    
    def test_suggestion_item_invalid_priority(self):
        """Test SuggestionItem validation fails with invalid priority"""
        with self.assertRaises(ValidationError):
            SuggestionItem(
                id=1,
                priority="URGENT",  # Invalid value
                category="Test",
                current_state="Test",
                suggested_text="Test",
                business_impact="Test"
            )


class TestSummaryOutput(unittest.TestCase):
    """Test SummaryOutput model"""
    
    def test_valid_summary(self):
        """Test creating a valid SummaryOutput"""
        summary = SummaryOutput(
            summary="This is a service agreement",
            contract_type="SERVICE_AGREEMENT",
            parties=["Company A", "Company B"],
            duration="2 years",
            key_obligations=["Provide service", "Maintain uptime"],
            financial_terms="₹500,000/month",
            jurisdiction="India"
        )
        self.assertEqual(len(summary.parties), 2)
        self.assertEqual(len(summary.key_obligations), 2)
    
    def test_summary_with_defaults(self):
        """Test SummaryOutput with default values"""
        summary = SummaryOutput(
            summary="Overview",
            contract_type="NDA"
        )
        self.assertEqual(summary.parties, [])
        self.assertEqual(summary.duration, "")
        self.assertEqual(summary.key_obligations, [])
        self.assertEqual(summary.financial_terms, "")
    
    def test_summary_missing_required_fields(self):
        """Test SummaryOutput validation fails without required fields"""
        with self.assertRaises(ValidationError):
            SummaryOutput(
                summary="Overview"
                # missing contract_type
            )


class TestClausesOutput(unittest.TestCase):
    """Test ClausesOutput model"""
    
    def test_clauses_output_auto_calculation(self):
        """Test that total_clauses auto-calculates correctly"""
        clauses = ClausesOutput(
            clauses=[
                ClauseItem(id=1, type="Payment", text="Text 1"),
                ClauseItem(id=2, type="Confidentiality", text="Text 2"),
                ClauseItem(id=3, type="Liability", text="Text 3"),
            ]
        )
        self.assertEqual(clauses.total_clauses, 3)
    
    def test_clauses_output_empty(self):
        """Test ClausesOutput with no clauses"""
        clauses = ClausesOutput()
        self.assertEqual(clauses.clauses, [])
        self.assertEqual(clauses.total_clauses, 0)
    
    def test_clauses_output_with_explicit_total(self):
        """Test that provided total_clauses is overridden by calculation"""
        clauses = ClausesOutput(
            clauses=[ClauseItem(id=1, type="Test", text="Text")],
            total_clauses=5  # Wrong value - should be auto-corrected
        )
        self.assertEqual(clauses.total_clauses, 1)  # Should be 1, not 5


class TestRisksOutput(unittest.TestCase):
    """Test RisksOutput model"""
    
    def test_risks_output_auto_calculation(self):
        """Test that total_risks and total_missing auto-calculate"""
        risks = RisksOutput(
            risks=[
                RiskItem(id=1, clause_type="Payment", risk_level=RiskLevel.HIGH,
                        issue="Issue", description="Desc", impact="Impact"),
                RiskItem(id=2, clause_type="Liability", risk_level=RiskLevel.MEDIUM,
                        issue="Issue", description="Desc", impact="Impact"),
            ],
            missing_clauses=["SLA", "Insurance"]
        )
        self.assertEqual(risks.total_risks, 2)
        self.assertEqual(risks.total_missing, 2)
    
    def test_risks_output_empty(self):
        """Test RisksOutput with no risks"""
        risks = RisksOutput()
        self.assertEqual(risks.risks, [])
        self.assertEqual(risks.missing_clauses, [])
        self.assertEqual(risks.total_risks, 0)
        self.assertEqual(risks.total_missing, 0)
    
    def test_risks_output_only_risks(self):
        """Test RisksOutput with risks but no missing clauses"""
        risks = RisksOutput(
            risks=[
                RiskItem(id=1, clause_type="Test", risk_level=RiskLevel.LOW,
                        issue="Issue", description="Desc", impact="Impact"),
            ]
        )
        self.assertEqual(risks.total_risks, 1)
        self.assertEqual(risks.total_missing, 0)


class TestSuggestionsOutput(unittest.TestCase):
    """Test SuggestionsOutput model"""
    
    def test_suggestions_output_auto_calculation(self):
        """Test that total_suggestions auto-calculates"""
        suggestions = SuggestionsOutput(
            suggestions=[
                SuggestionItem(id=1, priority=Priority.HIGH, category="Missing",
                             current_state="Not present", suggested_text="Add this",
                             business_impact="Protects"),
                SuggestionItem(id=2, priority=Priority.MEDIUM, category="Wording",
                             current_state="Current", suggested_text="Change to",
                             business_impact="Better"),
            ]
        )
        self.assertEqual(suggestions.total_suggestions, 2)
    
    def test_suggestions_output_empty(self):
        """Test SuggestionsOutput with no suggestions"""
        suggestions = SuggestionsOutput()
        self.assertEqual(suggestions.suggestions, [])
        self.assertEqual(suggestions.total_suggestions, 0)


class TestCompleteAnalysisOutput(unittest.TestCase):
    """Test CompleteAnalysisOutput model"""
    
    def test_complete_analysis_with_all_data(self):
        """Test CompleteAnalysisOutput with all components"""
        analysis = CompleteAnalysisOutput(
            summary=SummaryOutput(
                summary="Overview",
                contract_type="SERVICE_AGREEMENT",
                parties=["A", "B"]
            ),
            clauses=ClausesOutput(
                clauses=[ClauseItem(id=1, type="Payment", text="Text")]
            ),
            risks=RisksOutput(
                risks=[
                    RiskItem(id=1, clause_type="Payment", risk_level=RiskLevel.HIGH,
                            issue="Issue", description="Desc", impact="Impact")
                ]
            ),
            suggestions=SuggestionsOutput(
                suggestions=[
                    SuggestionItem(id=1, priority=Priority.HIGH, category="Missing",
                                 current_state="Not", suggested_text="Add",
                                 business_impact="Protects")
                ]
            ),
            processing_time=45.3,
            status=AnalysisStatus.SUCCESS
        )
        
        self.assertEqual(analysis.status, AnalysisStatus.SUCCESS)
        self.assertEqual(analysis.processing_time, 45.3)
        self.assertIsNotNone(analysis.summary)
        self.assertIsNotNone(analysis.clauses)
        self.assertIsNotNone(analysis.risks)
        self.assertIsNotNone(analysis.suggestions)
    
    def test_complete_analysis_partial(self):
        """Test CompleteAnalysisOutput with partial data"""
        analysis = CompleteAnalysisOutput(
            summary=SummaryOutput(summary="Test", contract_type="NDA"),
            clauses=None,
            risks=None,
            suggestions=None,
            status=AnalysisStatus.PARTIAL
        )
        self.assertEqual(analysis.status, AnalysisStatus.PARTIAL)
        self.assertIsNotNone(analysis.summary)
        self.assertIsNone(analysis.clauses)
    
    def test_complete_analysis_with_defaults(self):
        """Test CompleteAnalysisOutput with default values"""
        analysis = CompleteAnalysisOutput()
        self.assertIsNone(analysis.summary)
        self.assertIsNone(analysis.clauses)
        self.assertIsNone(analysis.risks)
        self.assertIsNone(analysis.suggestions)
        self.assertEqual(analysis.processing_time, 0.0)
        self.assertEqual(analysis.status, AnalysisStatus.SUCCESS)


class TestJSONSerialization(unittest.TestCase):
    """Test JSON serialization and deserialization"""
    
    def test_complete_analysis_to_json(self):
        """Test converting CompleteAnalysisOutput to JSON string"""
        analysis = CompleteAnalysisOutput(
            summary=SummaryOutput(
                summary="Test overview",
                contract_type="SERVICE_AGREEMENT",
                parties=["Company A", "Company B"]
            ),
            clauses=ClausesOutput(
                clauses=[ClauseItem(id=1, type="Payment", text="Due in 30 days")]
            ),
            processing_time=45.5,
            status=AnalysisStatus.SUCCESS
        )
        
        json_str = analysis.model_dump_json(indent=2)
        self.assertIsInstance(json_str, str)
        self.assertIn('"status": "success"', json_str)
        self.assertIn('"processing_time": 45.5', json_str)
    
    def test_complete_analysis_from_json(self):
        """Test parsing CompleteAnalysisOutput from JSON string"""
        json_data = {
            "summary": {
                "summary": "Test",
                "contract_type": "NDA",
                "parties": [],
                "duration": "",
                "key_obligations": [],
                "financial_terms": "",
                "jurisdiction": ""
            },
            "clauses": {
                "clauses": [],
                "total_clauses": 0
            },
            "risks": {
                "risks": [],
                "missing_clauses": [],
                "total_risks": 0,
                "total_missing": 0
            },
            "suggestions": {
                "suggestions": [],
                "total_suggestions": 0
            },
            "processing_time": 10.0,
            "status": "success"
        }
        
        analysis = CompleteAnalysisOutput(**json_data)
        self.assertEqual(analysis.status, AnalysisStatus.SUCCESS)
        self.assertEqual(analysis.processing_time, 10.0)
    
    def test_roundtrip_serialization(self):
        """Test JSON roundtrip: object -> JSON -> object"""
        original = CompleteAnalysisOutput(
            summary=SummaryOutput(
                summary="Test",
                contract_type="EMPLOYMENT",
                parties=["Employee", "Employer"],
                duration="1 year"
            ),
            processing_time=30.0,
            status=AnalysisStatus.SUCCESS
        )
        
        # Convert to JSON and back
        json_str = original.model_dump_json()
        reconstructed = CompleteAnalysisOutput(**json.loads(json_str))
        
        # Verify data integrity
        self.assertEqual(reconstructed.status, original.status)
        self.assertEqual(reconstructed.processing_time, original.processing_time)
        self.assertEqual(reconstructed.summary.contract_type, original.summary.contract_type)
        self.assertEqual(reconstructed.summary.parties, original.summary.parties)


class TestUtilityFunctions(unittest.TestCase):
    """Test utility functions"""
    
    def test_create_empty_analysis(self):
        """Test create_empty_analysis utility function"""
        empty = create_empty_analysis()
        self.assertEqual(empty.status, AnalysisStatus.ERROR)
        self.assertIsNotNone(empty.summary)
        self.assertIsNotNone(empty.clauses)
        self.assertIsNotNone(empty.risks)
        self.assertIsNotNone(empty.suggestions)
        self.assertEqual(empty.summary.summary, "")
        self.assertEqual(empty.clauses.total_clauses, 0)
    
    def test_create_error_analysis(self):
        """Test create_error_analysis utility function"""
        error = create_error_analysis(processing_time=15.5)
        self.assertEqual(error.status, AnalysisStatus.ERROR)
        self.assertEqual(error.processing_time, 15.5)
        self.assertIsNone(error.summary)
        self.assertIsNone(error.clauses)
        self.assertIsNone(error.risks)
        self.assertIsNone(error.suggestions)
    
    def test_create_error_analysis_default_time(self):
        """Test create_error_analysis with default processing time"""
        error = create_error_analysis()
        self.assertEqual(error.processing_time, 0.0)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions"""
    
    def test_zero_processing_time(self):
        """Test with zero processing time"""
        analysis = CompleteAnalysisOutput(processing_time=0.0)
        self.assertEqual(analysis.processing_time, 0.0)
    
    def test_very_long_text(self):
        """Test with very long text fields"""
        long_text = "A" * 10000
        clause = ClauseItem(id=1, type="Test", text=long_text)
        self.assertEqual(len(clause.text), 10000)
    
    def test_special_characters(self):
        """Test with special characters in text"""
        special_text = "Payment: ₹500,000; Terms: Net 30 (30%). © 2026."
        clause = ClauseItem(id=1, type="Payment", text=special_text)
        self.assertEqual(clause.text, special_text)
    
    def test_unicode_characters(self):
        """Test with unicode characters"""
        unicode_text = "समझौता • Contrato • Договор"
        clause = ClauseItem(id=1, type="Test", text=unicode_text)
        self.assertEqual(clause.text, unicode_text)
    
    def test_empty_lists_in_summary(self):
        """Test SummaryOutput with empty lists"""
        summary = SummaryOutput(
            summary="Test",
            contract_type="NDA",
            parties=[],
            key_obligations=[]
        )
        self.assertEqual(len(summary.parties), 0)
        self.assertEqual(len(summary.key_obligations), 0)
    
    def test_large_number_of_clauses(self):
        """Test ClausesOutput with many clauses"""
        clauses_list = [
            ClauseItem(id=i, type=f"Clause {i}", text=f"Text {i}")
            for i in range(100)
        ]
        clauses = ClausesOutput(clauses=clauses_list)
        self.assertEqual(clauses.total_clauses, 100)


class TestDataTypeValidation(unittest.TestCase):
    """Test type validation and coercion"""
    
    def test_id_must_be_integer(self):
        """Test that id accepts numeric strings and coerces to int"""
        # Pydantic 2.x coerces types rather than raising validation errors
        clause = ClauseItem(id="1", type="Test", text="Text")
        self.assertEqual(clause.id, 1)
        self.assertIsInstance(clause.id, int)
    
    def test_processing_time_must_be_numeric(self):
        """Test that processing_time coerces to float"""
        # Pydantic 2.x coerces numeric strings to float
        analysis = CompleteAnalysisOutput(processing_time="45.5")
        self.assertEqual(analysis.processing_time, 45.5)
        self.assertIsInstance(analysis.processing_time, float)
    
    def test_lists_must_be_lists(self):
        """Test that parties field must be a list"""
        with self.assertRaises(ValidationError):
            SummaryOutput(
                summary="Test",
                contract_type="NDA",
                parties="Company A"  # Should be list, not string
            )


if __name__ == '__main__':
    unittest.main()
