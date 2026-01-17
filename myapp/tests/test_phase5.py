"""
Phase 5 - Industry Knowledge Base Testing

Tests for the Contract Clause Mapping service that loads and manages
standard clauses for different contract types by jurisdiction.

Test Coverage:
    - Loading standard clauses from JSON
    - Getting clauses by contract type and priority
    - Finding missing clauses
    - Clause lookup by ID
    - Clause standard validation
    - Edge cases and error handling
"""

from django.test import TestCase
from myapp.services.contract_clause_mapping import (
    get_mapper,
    ContractClauseMapper,
    get_standard_clauses_for_type,
    get_critical_clauses_for_type,
    get_important_clauses_for_type,
    get_optional_clauses_for_type,
    get_all_contract_types,
    is_clause_standard,
    find_missing_clauses,
    get_clause_by_id,
    get_clause_priority,
    get_clause_recommendations,
    get_clause_standard_text,
    get_all_clauses_flat,
    get_contract_type_name,
    get_jurisdiction,
)


class ContractClauseMapperLoadingTest(TestCase):
    """Test loading and initialization of the clause mapper"""
    
    def test_mapper_singleton_pattern(self):
        """Test that mapper follows singleton pattern"""
        mapper1 = get_mapper()
        mapper2 = get_mapper()
        self.assertIs(mapper1, mapper2, "Mapper should be singleton instance")
    
    def test_mapper_loads_standard_clauses(self):
        """Test that mapper successfully loads standard clauses"""
        mapper = get_mapper()
        self.assertIsNotNone(mapper._standard_clauses, "Standard clauses should be loaded")
        self.assertGreater(len(mapper._standard_clauses), 0, "Should have at least one contract type")
    
    def test_all_contract_types_loaded(self):
        """Test that all 5 contract types are loaded"""
        types = get_all_contract_types()
        
        expected_types = [
            'SERVICE_AGREEMENT_INDIA',
            'EMPLOYMENT_CONTRACT_INDIA',
            'NDA_INDIA',
            'PARTNERSHIP_AGREEMENT_INDIA',
            'VENDOR_AGREEMENT_INDIA'
        ]
        
        for expected_type in expected_types:
            self.assertIn(expected_type, types, f"Contract type '{expected_type}' should be loaded")
    
    def test_contract_types_have_clauses(self):
        """Test that each contract type has clauses"""
        types = get_all_contract_types()
        
        for contract_type_key in types:
            mapper = get_mapper()
            # Extract contract type and jurisdiction from key
            parts = contract_type_key.rsplit('_', 1)
            if len(parts) == 2:
                contract_type, jurisdiction = parts
                clauses = get_standard_clauses_for_type(contract_type, jurisdiction)
                
                self.assertIn('critical_clauses', clauses, f"Should have critical_clauses for {contract_type_key}")
                self.assertIn('important_clauses', clauses, f"Should have important_clauses for {contract_type_key}")
                self.assertIn('optional_clauses', clauses, f"Should have optional_clauses for {contract_type_key}")


class ServiceAgreementClausesTest(TestCase):
    """Test SERVICE_AGREEMENT clauses"""
    
    def test_get_all_service_agreement_clauses(self):
        """Test getting all clauses for service agreement"""
        clauses = get_standard_clauses_for_type('SERVICE_AGREEMENT', 'INDIA')
        
        self.assertIsNotNone(clauses, "Should return clauses dict")
        self.assertIn('critical_clauses', clauses)
        self.assertIn('important_clauses', clauses)
        self.assertIn('optional_clauses', clauses)
        self.assertGreater(len(clauses['critical_clauses']), 0, "Should have critical clauses")
    
    def test_get_critical_clauses_service_agreement(self):
        """Test getting only critical clauses for service agreement"""
        critical = get_critical_clauses_for_type('SERVICE_AGREEMENT', 'INDIA')
        
        self.assertIsInstance(critical, list, "Should return a list")
        self.assertGreater(len(critical), 0, "Should have critical clauses")
        
        # Check that clauses have expected structure
        for clause in critical:
            self.assertIn('type', clause, "Clause should have type")
            self.assertIn('id', clause, "Clause should have id")
            self.assertIn('priority', clause, "Clause should have priority")
            self.assertEqual(clause['priority'], 'critical', "Priority should be critical")
    
    def test_get_important_clauses_service_agreement(self):
        """Test getting only important clauses for service agreement"""
        important = get_important_clauses_for_type('SERVICE_AGREEMENT', 'INDIA')
        
        self.assertIsInstance(important, list)
        self.assertGreater(len(important), 0, "Should have important clauses")
        
        for clause in important:
            self.assertEqual(clause['priority'], 'important', "Priority should be important")
    
    def test_get_optional_clauses_service_agreement(self):
        """Test getting only optional clauses for service agreement"""
        optional = get_optional_clauses_for_type('SERVICE_AGREEMENT', 'INDIA')
        
        self.assertIsInstance(optional, list)
        
        for clause in optional:
            self.assertEqual(clause['priority'], 'optional', "Priority should be optional")
    
    def test_expected_critical_clauses_present(self):
        """Test that expected critical clauses are present"""
        critical = get_critical_clauses_for_type('SERVICE_AGREEMENT', 'INDIA')
        clause_names = [c['type'] for c in critical]
        
        expected_clauses = [
            'Scope of Services',
            'Payment Terms',
            'Term and Termination',
            'Confidentiality',
            'Intellectual Property Rights',
            'Limitation of Liability'
        ]
        
        for expected in expected_clauses:
            self.assertIn(expected, clause_names, f"'{expected}' should be in critical clauses")


class EmploymentContractClausesTest(TestCase):
    """Test EMPLOYMENT_CONTRACT clauses"""
    
    def test_get_all_employment_clauses(self):
        """Test getting all clauses for employment contract"""
        clauses = get_standard_clauses_for_type('EMPLOYMENT_CONTRACT', 'INDIA')
        
        self.assertIsNotNone(clauses)
        self.assertGreater(len(clauses['critical_clauses']), 0)
    
    def test_expected_critical_employment_clauses(self):
        """Test that expected critical employment clauses are present"""
        critical = get_critical_clauses_for_type('EMPLOYMENT_CONTRACT', 'INDIA')
        clause_names = [c['type'] for c in critical]
        
        expected_clauses = [
            'Job Title and Responsibilities',
            'Compensation and Benefits',
            'Working Hours and Leave',
            'Termination of Employment',
            'Confidentiality and Non-Disclosure',
            'Non-Compete and Non-Solicitation'
        ]
        
        for expected in expected_clauses:
            self.assertIn(expected, clause_names, f"'{expected}' should be in critical clauses")


class NDAClausesTest(TestCase):
    """Test NDA clauses"""
    
    def test_get_all_nda_clauses(self):
        """Test getting all clauses for NDA"""
        clauses = get_standard_clauses_for_type('NDA', 'INDIA')
        
        self.assertIsNotNone(clauses)
        self.assertGreater(len(clauses['critical_clauses']), 0)
    
    def test_expected_critical_nda_clauses(self):
        """Test that expected critical NDA clauses are present"""
        critical = get_critical_clauses_for_type('NDA', 'INDIA')
        clause_names = [c['type'] for c in critical]
        
        expected_clauses = [
            'Definition of Confidential Information',
            'Permitted Disclosures',
            'Term of Confidentiality',
            'Return or Destruction of Information',
            'Consequences of Breach',
            'Exceptions to Confidentiality'
        ]
        
        for expected in expected_clauses:
            self.assertIn(expected, clause_names, f"'{expected}' should be in critical clauses")


class PartnershipAgreementClausesTest(TestCase):
    """Test PARTNERSHIP_AGREEMENT clauses"""
    
    def test_get_all_partnership_clauses(self):
        """Test getting all clauses for partnership agreement"""
        clauses = get_standard_clauses_for_type('PARTNERSHIP_AGREEMENT', 'INDIA')
        
        self.assertIsNotNone(clauses)
        self.assertGreater(len(clauses['critical_clauses']), 0)
    
    def test_expected_critical_partnership_clauses(self):
        """Test that expected critical partnership clauses are present"""
        critical = get_critical_clauses_for_type('PARTNERSHIP_AGREEMENT', 'INDIA')
        clause_names = [c['type'] for c in critical]
        
        expected_clauses = [
            'Capital Contribution',
            'Profit and Loss Distribution',
            'Decision Making and Governance',
            'Dispute Resolution and Arbitration',
            'Partner Exit and Buyout Terms',
            'Dissolution and Winding Up'
        ]
        
        for expected in expected_clauses:
            self.assertIn(expected, clause_names, f"'{expected}' should be in critical clauses")


class VendorAgreementClausesTest(TestCase):
    """Test VENDOR_AGREEMENT clauses"""
    
    def test_get_all_vendor_clauses(self):
        """Test getting all clauses for vendor agreement"""
        clauses = get_standard_clauses_for_type('VENDOR_AGREEMENT', 'INDIA')
        
        self.assertIsNotNone(clauses)
        self.assertGreater(len(clauses['critical_clauses']), 0)
    
    def test_expected_critical_vendor_clauses(self):
        """Test that expected critical vendor clauses are present"""
        critical = get_critical_clauses_for_type('VENDOR_AGREEMENT', 'INDIA')
        clause_names = [c['type'] for c in critical]
        
        expected_clauses = [
            'Product/Service Description',
            'Pricing and Payment Terms',
            'Delivery and SLA',
            'Quality Assurance and Warranties',
            'Intellectual Property Rights',
            'Liability and Indemnification'
        ]
        
        for expected in expected_clauses:
            self.assertIn(expected, clause_names, f"'{expected}' should be in critical clauses")


class ClauseStandardValidationTest(TestCase):
    """Test is_clause_standard function"""
    
    def test_clause_is_standard_returns_true(self):
        """Test that is_clause_standard returns True for standard clauses"""
        result = is_clause_standard('Payment Terms', 'SERVICE_AGREEMENT', 'INDIA')
        self.assertTrue(result, "'Payment Terms' should be standard for SERVICE_AGREEMENT")
    
    def test_clause_is_standard_returns_false(self):
        """Test that is_clause_standard returns False for non-standard clauses"""
        result = is_clause_standard('Fictional Clause', 'SERVICE_AGREEMENT', 'INDIA')
        self.assertFalse(result, "Non-existent clause should not be standard")
    
    def test_multiple_clause_validations(self):
        """Test validation of multiple clauses"""
        test_cases = [
            ('Scope of Services', 'SERVICE_AGREEMENT', 'INDIA', True),
            ('Confidentiality', 'EMPLOYMENT_CONTRACT', 'INDIA', True),
            ('Definition of Confidential Information', 'NDA', 'INDIA', True),
            ('Non-existent Clause', 'SERVICE_AGREEMENT', 'INDIA', False),
        ]
        
        for clause_type, contract_type, jurisdiction, expected in test_cases:
            result = is_clause_standard(clause_type, contract_type, jurisdiction)
            self.assertEqual(
                result,
                expected,
                f"is_clause_standard('{clause_type}', '{contract_type}') should be {expected}"
            )


class MissingClausesDetectionTest(TestCase):
    """Test find_missing_clauses function"""
    
    def test_find_missing_critical_clauses(self):
        """Test detection of missing critical clauses"""
        found_clauses = ['Payment Terms', 'Scope of Services']
        
        missing = find_missing_clauses(found_clauses, 'SERVICE_AGREEMENT', 'INDIA')
        
        self.assertIsNotNone(missing)
        self.assertIn('missing_critical', missing)
        self.assertIn('missing_important', missing)
        self.assertIn('missing_optional', missing)
        
        # Should have missing critical clauses
        self.assertGreater(len(missing['missing_critical']), 0, "Should detect missing critical clauses")
        
        # Should have the expected missing clauses
        self.assertIn('Term and Termination', missing['missing_critical'])
        self.assertIn('Confidentiality', missing['missing_critical'])
    
    def test_no_missing_clauses_when_all_found(self):
        """Test no missing clauses when all are found"""
        # Get all clause names first
        critical = get_critical_clauses_for_type('SERVICE_AGREEMENT', 'INDIA')
        important = get_important_clauses_for_type('SERVICE_AGREEMENT', 'INDIA')
        optional = get_optional_clauses_for_type('SERVICE_AGREEMENT', 'INDIA')
        
        all_clause_names = (
            [c['type'] for c in critical] +
            [c['type'] for c in important] +
            [c['type'] for c in optional]
        )
        
        missing = find_missing_clauses(all_clause_names, 'SERVICE_AGREEMENT', 'INDIA')
        
        self.assertEqual(len(missing['missing_critical']), 0, "Should have no missing critical clauses")
        self.assertEqual(len(missing['missing_important']), 0, "Should have no missing important clauses")
        self.assertEqual(len(missing['missing_optional']), 0, "Should have no missing optional clauses")
    
    def test_case_insensitive_clause_matching(self):
        """Test that clause matching is case-insensitive"""
        # Use lowercase clause names
        found_clauses = ['payment terms', 'scope of services']
        
        missing = find_missing_clauses(found_clauses, 'SERVICE_AGREEMENT', 'INDIA')
        
        # Should still detect them as found (case-insensitive)
        self.assertNotIn('Payment Terms', missing['missing_critical'])
        self.assertNotIn('Scope of Services', missing['missing_critical'])
    
    def test_missing_clauses_for_employment_contract(self):
        """Test missing clause detection for employment contract"""
        found_clauses = ['Compensation and Benefits', 'Working Hours and Leave']
        
        missing = find_missing_clauses(found_clauses, 'EMPLOYMENT_CONTRACT', 'INDIA')
        
        self.assertGreater(len(missing['missing_critical']), 0)
        self.assertIn('Job Title and Responsibilities', missing['missing_critical'])


class ClauseByIdLookupTest(TestCase):
    """Test get_clause_by_id function"""
    
    def test_get_clause_by_valid_id(self):
        """Test retrieving a clause by valid ID"""
        # First get a clause to know its ID
        critical = get_critical_clauses_for_type('SERVICE_AGREEMENT', 'INDIA')
        self.assertGreater(len(critical), 0)
        
        first_clause = critical[0]
        clause_id = first_clause['id']
        
        # Now retrieve it by ID
        retrieved_clause = get_clause_by_id(clause_id, 'SERVICE_AGREEMENT', 'INDIA')
        
        self.assertIsNotNone(retrieved_clause, "Should retrieve clause by ID")
        self.assertEqual(retrieved_clause['id'], clause_id)
        self.assertEqual(retrieved_clause['type'], first_clause['type'])
    
    def test_get_clause_by_invalid_id(self):
        """Test that invalid ID returns None"""
        result = get_clause_by_id('INVALID_ID_12345', 'SERVICE_AGREEMENT', 'INDIA')
        self.assertIsNone(result, "Should return None for invalid ID")


class ClausePriorityTest(TestCase):
    """Test get_clause_priority function"""
    
    def test_get_priority_for_critical_clause(self):
        """Test getting priority of critical clause"""
        priority = get_clause_priority('Payment Terms', 'SERVICE_AGREEMENT', 'INDIA')
        self.assertEqual(priority, 'critical', "Payment Terms should be critical priority")
    
    def test_get_priority_for_important_clause(self):
        """Test getting priority of important clause"""
        priority = get_clause_priority('Service Level Agreement (SLA)', 'SERVICE_AGREEMENT', 'INDIA')
        self.assertEqual(priority, 'important', "SLA should be important priority")
    
    def test_get_priority_for_nonexistent_clause(self):
        """Test that non-existent clause returns None"""
        priority = get_clause_priority('Non-Existent Clause', 'SERVICE_AGREEMENT', 'INDIA')
        self.assertIsNone(priority, "Non-existent clause should return None priority")


class ClauseDetailsTest(TestCase):
    """Test get_clause_recommendations and get_clause_standard_text functions"""
    
    def test_get_clause_recommendations(self):
        """Test retrieving clause recommendations"""
        recommendations = get_clause_recommendations('Payment Terms', 'SERVICE_AGREEMENT', 'INDIA')
        
        self.assertIsNotNone(recommendations, "Should return recommendations")
        self.assertIsInstance(recommendations, str, "Recommendations should be a string")
        self.assertGreater(len(recommendations), 0, "Recommendations should not be empty")
    
    def test_get_clause_standard_text(self):
        """Test retrieving standard clause text"""
        standard_text = get_clause_standard_text('Payment Terms', 'SERVICE_AGREEMENT', 'INDIA')
        
        self.assertIsNotNone(standard_text, "Should return standard text")
        self.assertIsInstance(standard_text, str, "Standard text should be a string")
        self.assertGreater(len(standard_text), 0, "Standard text should not be empty")
    
    def test_recommendations_for_nonexistent_clause(self):
        """Test recommendations for non-existent clause"""
        recommendations = get_clause_recommendations('Non-Existent', 'SERVICE_AGREEMENT', 'INDIA')
        self.assertIsNone(recommendations, "Should return None for non-existent clause")


class AllClausesFlatTest(TestCase):
    """Test get_all_clauses_flat function"""
    
    def test_get_all_clauses_flat_returns_list(self):
        """Test that get_all_clauses_flat returns a list"""
        flat_list = get_all_clauses_flat('SERVICE_AGREEMENT', 'INDIA')
        
        self.assertIsInstance(flat_list, list, "Should return a list")
        self.assertGreater(len(flat_list), 0, "Should have at least one clause")
    
    def test_flat_list_contains_all_clauses(self):
        """Test that flat list contains all clauses from all priorities"""
        critical = get_critical_clauses_for_type('SERVICE_AGREEMENT', 'INDIA')
        important = get_important_clauses_for_type('SERVICE_AGREEMENT', 'INDIA')
        optional = get_optional_clauses_for_type('SERVICE_AGREEMENT', 'INDIA')
        
        expected_count = len(critical) + len(important) + len(optional)
        
        flat_list = get_all_clauses_flat('SERVICE_AGREEMENT', 'INDIA')
        
        self.assertEqual(
            len(flat_list),
            expected_count,
            "Flat list should contain all clauses from all priorities"
        )


class ContractTypeMetadataTest(TestCase):
    """Test getting metadata about contract types"""
    
    def test_get_contract_type_name(self):
        """Test getting human-readable contract type name"""
        name = get_contract_type_name('SERVICE_AGREEMENT_INDIA')
        
        self.assertIsNotNone(name)
        self.assertEqual(name, 'Service Agreement')
    
    def test_get_jurisdiction(self):
        """Test getting jurisdiction from contract type key"""
        jurisdiction = get_jurisdiction('SERVICE_AGREEMENT_INDIA')
        
        self.assertIsNotNone(jurisdiction)
        self.assertEqual(jurisdiction, 'India')
    
    def test_get_metadata_for_all_types(self):
        """Test getting metadata for all contract types"""
        types = get_all_contract_types()
        
        for contract_type_key in types:
            name = get_contract_type_name(contract_type_key)
            jurisdiction = get_jurisdiction(contract_type_key)
            
            self.assertIsNotNone(name, f"Name should exist for {contract_type_key}")
            self.assertIsNotNone(jurisdiction, f"Jurisdiction should exist for {contract_type_key}")
            self.assertGreater(len(name), 0, f"Name should not be empty for {contract_type_key}")
            self.assertGreater(len(jurisdiction), 0, f"Jurisdiction should not be empty for {contract_type_key}")


class EdgeCasesTest(TestCase):
    """Test edge cases and error handling"""
    
    def test_empty_found_clauses(self):
        """Test with empty found clauses list"""
        missing = find_missing_clauses([], 'SERVICE_AGREEMENT', 'INDIA')
        
        self.assertIsNotNone(missing)
        # All clauses should be missing
        self.assertGreater(len(missing['missing_critical']), 0)
    
    def test_invalid_contract_type(self):
        """Test with invalid contract type"""
        clauses = get_standard_clauses_for_type('INVALID_TYPE', 'INDIA')
        
        # Should return empty dict or empty lists
        self.assertEqual(len(clauses['critical_clauses']), 0)
        self.assertEqual(len(clauses['important_clauses']), 0)
        self.assertEqual(len(clauses['optional_clauses']), 0)
    
    def test_invalid_jurisdiction(self):
        """Test with invalid jurisdiction (currently only INDIA supported)"""
        clauses = get_standard_clauses_for_type('SERVICE_AGREEMENT', 'INVALID_JURISDICTION')
        
        # Should return empty dict or empty lists
        self.assertEqual(len(clauses['critical_clauses']), 0)


class ClauseStructureTest(TestCase):
    """Test that all clauses have required structure"""
    
    def test_critical_clause_structure(self):
        """Test that critical clauses have required fields"""
        critical = get_critical_clauses_for_type('SERVICE_AGREEMENT', 'INDIA')
        
        required_fields = ['id', 'type', 'priority', 'description', 'recommendations', 'standard_text']
        
        for clause in critical:
            for field in required_fields:
                self.assertIn(field, clause, f"Clause {clause.get('id')} should have field '{field}'")
                self.assertIsNotNone(clause[field], f"Field '{field}' should not be None")
    
    def test_important_clause_structure(self):
        """Test that important clauses have required fields"""
        important = get_important_clauses_for_type('SERVICE_AGREEMENT', 'INDIA')
        
        required_fields = ['id', 'type', 'priority', 'description', 'recommendations', 'standard_text']
        
        for clause in important:
            for field in required_fields:
                self.assertIn(field, clause, f"Clause {clause.get('id')} should have field '{field}'")
    
    def test_optional_clause_structure(self):
        """Test that optional clauses have required fields"""
        optional = get_optional_clauses_for_type('SERVICE_AGREEMENT', 'INDIA')
        
        required_fields = ['id', 'type', 'priority', 'description', 'recommendations', 'standard_text']
        
        for clause in optional:
            for field in required_fields:
                self.assertIn(field, clause, f"Clause {clause.get('id')} should have field '{field}'")


class UniquenessTest(TestCase):
    """Test that clause IDs and types are unique within contract type"""
    
    def test_clause_ids_are_unique_within_contract_type(self):
        """Test that all clause IDs are unique for a contract type"""
        all_clauses = get_all_clauses_flat('SERVICE_AGREEMENT', 'INDIA')
        clause_ids = [c['id'] for c in all_clauses]
        
        unique_ids = set(clause_ids)
        self.assertEqual(
            len(clause_ids),
            len(unique_ids),
            "All clause IDs should be unique within a contract type"
        )
    
    def test_clause_types_are_unique_within_contract_type(self):
        """Test that all clause types are unique for a contract type"""
        all_clauses = get_all_clauses_flat('SERVICE_AGREEMENT', 'INDIA')
        clause_types = [c['type'] for c in all_clauses]
        
        unique_types = set(clause_types)
        self.assertEqual(
            len(clause_types),
            len(unique_types),
            "All clause types should be unique within a contract type"
        )


if __name__ == '__main__':
    import unittest
    unittest.main()
