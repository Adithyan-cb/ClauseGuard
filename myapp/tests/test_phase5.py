"""
Phase 5 - Standard Clauses Database Testing

Comprehensive tests for the Contract Clause Mapping service that manages
standard clauses for different contract types across jurisdictions.

Test Organization:
    1. Basic Loader Tests - Module initialization and loading
    2. Contract Type Tests - Verify all contract types and their clauses
    3. Clause Retrieval Tests - Get clauses by priority and ID
    4. Clause Validation Tests - Validate clause standards
    5. Missing Clause Detection Tests - Find gaps in contracts
    6. Data Integrity Tests - Ensure data consistency
    7. Edge Case Tests - Handle errors gracefully
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


class BasicLoaderTests(TestCase):
    """Test module loading and initialization"""
    
    def test_singleton_pattern(self):
        """Verify singleton pattern prevents multiple instances"""
        mapper1 = get_mapper()
        mapper2 = get_mapper()
        self.assertIs(mapper1, mapper2)
    
    def test_clauses_loaded_on_init(self):
        """Verify standard clauses are loaded during initialization"""
        mapper = get_mapper()
        self.assertIsNotNone(mapper._standard_clauses)
        self.assertGreater(len(mapper._standard_clauses), 0)
    
    def test_json_file_is_parseable(self):
        """Verify JSON file is valid and properly structured"""
        mapper = get_mapper()
        # Check that we can iterate and access the data
        for key, contract_data in mapper._standard_clauses.items():
            self.assertIsInstance(key, str)
            self.assertIn('contract_type', contract_data)
            self.assertIn('jurisdiction', contract_data)
            self.assertIn('critical_clauses', contract_data)


class ContractTypeLoadingTests(TestCase):
    """Test that all expected contract types are loaded"""
    
    def setUp(self):
        """Get all contract types before each test"""
        self.all_types = get_all_contract_types()
        self.expected_base_types = ['SERVICE_AGREEMENT', 'EMPLOYMENT_CONTRACT', 'NDA', 
                                    'PARTNERSHIP_AGREEMENT', 'VENDOR_AGREEMENT']
        self.expected_jurisdictions = ['INDIA', 'US', 'UK']
    
    def test_all_expected_contract_types_present(self):
        """Verify all 5 contract types are loaded"""
        for base_type in self.expected_base_types:
            found = any(t.startswith(base_type) for t in self.all_types)
            self.assertTrue(found, f"Contract type '{base_type}' should be loaded")
    
    def test_all_jurisdictions_covered(self):
        """Verify contracts exist for all jurisdictions"""
        for base_type in self.expected_base_types:
            for jurisdiction in self.expected_jurisdictions:
                key = f"{base_type}_{jurisdiction}"
                self.assertIn(key, self.all_types, 
                            f"Should have {base_type} for {jurisdiction}")
    
    def test_total_contract_types_count(self):
        """Verify we have exactly 15 contract type combinations"""
        expected_count = len(self.expected_base_types) * len(self.expected_jurisdictions)
        self.assertEqual(len(self.all_types), expected_count)
    
    def test_each_type_has_all_clause_categories(self):
        """Verify each contract type has critical, important, and optional clauses"""
        for contract_type in self.all_types:
            parts = contract_type.rsplit('_', 1)
            if len(parts) == 2:
                base_type, jurisdiction = parts
                clauses = get_standard_clauses_for_type(base_type, jurisdiction)
                
                self.assertIn('critical_clauses', clauses)
                self.assertIn('important_clauses', clauses)
                self.assertIn('optional_clauses', clauses)
                self.assertGreater(len(clauses['critical_clauses']), 0,
                                 f"{contract_type} should have critical clauses")


class ClauseRetrievalTests(TestCase):
    """Test retrieving clauses by various criteria"""
    
    def setUp(self):
        """Set up common test data"""
        self.test_contract = 'SERVICE_AGREEMENT'
        self.test_jurisdiction = 'INDIA'
    
    def test_get_all_clauses_by_type(self):
        """Get all clauses for a contract type"""
        clauses = get_standard_clauses_for_type(self.test_contract, self.test_jurisdiction)
        
        self.assertIsInstance(clauses, dict)
        self.assertIn('critical_clauses', clauses)
        self.assertIn('important_clauses', clauses)
        self.assertIn('optional_clauses', clauses)
    
    def test_get_critical_clauses_only(self):
        """Retrieve only critical priority clauses"""
        critical = get_critical_clauses_for_type(self.test_contract, self.test_jurisdiction)
        
        self.assertIsInstance(critical, list)
        self.assertGreater(len(critical), 0)
        
        for clause in critical:
            self.assertEqual(clause['priority'], 'critical')
    
    def test_get_important_clauses_only(self):
        """Retrieve only important priority clauses"""
        important = get_important_clauses_for_type(self.test_contract, self.test_jurisdiction)
        
        self.assertIsInstance(important, list)
        for clause in important:
            self.assertEqual(clause['priority'], 'important')
    
    def test_get_optional_clauses_only(self):
        """Retrieve only optional priority clauses"""
        optional = get_optional_clauses_for_type(self.test_contract, self.test_jurisdiction)
        
        self.assertIsInstance(optional, list)
        for clause in optional:
            self.assertEqual(clause['priority'], 'optional')
    
    def test_get_clause_by_valid_id(self):
        """Retrieve a specific clause by ID"""
        critical = get_critical_clauses_for_type(self.test_contract, self.test_jurisdiction)
        first_clause = critical[0]
        clause_id = first_clause['id']
        
        retrieved = get_clause_by_id(clause_id, self.test_contract, self.test_jurisdiction)
        
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved['id'], clause_id)
        self.assertEqual(retrieved['type'], first_clause['type'])
    
    def test_get_clause_by_invalid_id_returns_none(self):
        """Non-existent clause ID returns None"""
        result = get_clause_by_id('FAKE_ID_999', self.test_contract, self.test_jurisdiction)
        self.assertIsNone(result)
    
    def test_get_all_clauses_flat(self):
        """Get all clauses in single flat list"""
        flat_list = get_all_clauses_flat(self.test_contract, self.test_jurisdiction)
        
        self.assertIsInstance(flat_list, list)
        self.assertGreater(len(flat_list), 0)
        
        # Count should match sum of all priorities
        critical = get_critical_clauses_for_type(self.test_contract, self.test_jurisdiction)
        important = get_important_clauses_for_type(self.test_contract, self.test_jurisdiction)
        optional = get_optional_clauses_for_type(self.test_contract, self.test_jurisdiction)
        
        expected_count = len(critical) + len(important) + len(optional)
        self.assertEqual(len(flat_list), expected_count)


class ClauseStructureTests(TestCase):
    """Test that clause data has required structure"""
    
    REQUIRED_FIELDS = ['id', 'type', 'priority', 'description', 'recommendations', 'standard_text']
    
    def test_critical_clause_structure(self):
        """Critical clauses have all required fields"""
        critical = get_critical_clauses_for_type('SERVICE_AGREEMENT', 'INDIA')
        self._validate_clause_structure(critical)
    
    def test_important_clause_structure(self):
        """Important clauses have all required fields"""
        important = get_important_clauses_for_type('SERVICE_AGREEMENT', 'INDIA')
        self._validate_clause_structure(important)
    
    def test_optional_clause_structure(self):
        """Optional clauses have all required fields"""
        optional = get_optional_clauses_for_type('SERVICE_AGREEMENT', 'INDIA')
        self._validate_clause_structure(optional)
    
    def _validate_clause_structure(self, clauses):
        """Helper to validate clause structure"""
        for clause in clauses:
            for field in self.REQUIRED_FIELDS:
                self.assertIn(field, clause, 
                            f"Clause {clause.get('id')} missing field '{field}'")
                self.assertIsNotNone(clause[field],
                                   f"Field '{field}' should not be None")
                if field != 'id' and field != 'priority':
                    self.assertGreater(len(str(clause[field])), 0,
                                     f"Field '{field}' should not be empty")


class ClauseValidationTests(TestCase):
    """Test clause standard validation"""
    
    def test_existing_clause_is_standard(self):
        """Valid clause returns True"""
        result = is_clause_standard('Payment Terms', 'SERVICE_AGREEMENT', 'INDIA')
        self.assertTrue(result)
    
    def test_nonexistent_clause_is_not_standard(self):
        """Invalid clause returns False"""
        result = is_clause_standard('Made Up Clause', 'SERVICE_AGREEMENT', 'INDIA')
        self.assertFalse(result)
    
    def test_clause_priority_critical(self):
        """Get priority level for critical clause"""
        priority = get_clause_priority('Payment Terms', 'SERVICE_AGREEMENT', 'INDIA')
        self.assertEqual(priority, 'critical')
    
    def test_clause_priority_important(self):
        """Get priority level for important clause"""
        priority = get_clause_priority('Service Level Agreement (SLA)', 'SERVICE_AGREEMENT', 'INDIA')
        self.assertEqual(priority, 'important')
    
    def test_clause_priority_nonexistent(self):
        """Non-existent clause returns None priority"""
        priority = get_clause_priority('Fake Clause', 'SERVICE_AGREEMENT', 'INDIA')
        self.assertIsNone(priority)


class ClauseDetailsTests(TestCase):
    """Test retrieving clause details"""
    
    def test_get_recommendations(self):
        """Retrieve recommendations for a clause"""
        recommendations = get_clause_recommendations('Payment Terms', 'SERVICE_AGREEMENT', 'INDIA')
        
        self.assertIsNotNone(recommendations)
        self.assertIsInstance(recommendations, str)
        self.assertGreater(len(recommendations), 0)
    
    def test_get_standard_text(self):
        """Retrieve standard text for a clause"""
        text = get_clause_standard_text('Payment Terms', 'SERVICE_AGREEMENT', 'INDIA')
        
        self.assertIsNotNone(text)
        self.assertIsInstance(text, str)
        self.assertGreater(len(text), 0)
    
    def test_nonexistent_clause_details_return_none(self):
        """Non-existent clause returns None for details"""
        recommendations = get_clause_recommendations('Fake', 'SERVICE_AGREEMENT', 'INDIA')
        text = get_clause_standard_text('Fake', 'SERVICE_AGREEMENT', 'INDIA')
        
        self.assertIsNone(recommendations)
        self.assertIsNone(text)


class MissingClausesTests(TestCase):
    """Test missing clause detection"""
    
    def test_find_missing_with_empty_found_list(self):
        """All clauses are missing when found list is empty"""
        missing = find_missing_clauses([], 'SERVICE_AGREEMENT', 'INDIA')
        
        self.assertIsNotNone(missing)
        self.assertGreater(len(missing['missing_critical']), 0)
    
    def test_find_missing_with_some_clauses(self):
        """Detect missing clauses when some are found"""
        found = ['Payment Terms', 'Scope of Services']
        missing = find_missing_clauses(found, 'SERVICE_AGREEMENT', 'INDIA')
        
        self.assertGreater(len(missing['missing_critical']), 0)
        self.assertIn('Term and Termination', missing['missing_critical'])
    
    def test_find_missing_with_all_clauses(self):
        """No missing clauses when all are found"""
        critical = get_critical_clauses_for_type('SERVICE_AGREEMENT', 'INDIA')
        important = get_important_clauses_for_type('SERVICE_AGREEMENT', 'INDIA')
        optional = get_optional_clauses_for_type('SERVICE_AGREEMENT', 'INDIA')
        
        all_names = [c['type'] for c in critical + important + optional]
        missing = find_missing_clauses(all_names, 'SERVICE_AGREEMENT', 'INDIA')
        
        self.assertEqual(len(missing['missing_critical']), 0)
        self.assertEqual(len(missing['missing_important']), 0)
        self.assertEqual(len(missing['missing_optional']), 0)
    
    def test_missing_clauses_case_insensitive(self):
        """Clause matching is case-insensitive"""
        found = ['payment terms', 'scope of services']  # lowercase
        missing = find_missing_clauses(found, 'SERVICE_AGREEMENT', 'INDIA')
        
        # Should match even with different case
        self.assertNotIn('Payment Terms', missing['missing_critical'])
        self.assertNotIn('Scope of Services', missing['missing_critical'])
    
    def test_missing_clauses_structure(self):
        """Missing clauses dict has correct structure"""
        missing = find_missing_clauses([], 'SERVICE_AGREEMENT', 'INDIA')
        
        self.assertIn('missing_critical', missing)
        self.assertIn('missing_important', missing)
        self.assertIn('missing_optional', missing)
        
        self.assertIsInstance(missing['missing_critical'], list)
        self.assertIsInstance(missing['missing_important'], list)
        self.assertIsInstance(missing['missing_optional'], list)


class ContractTypeMetadataTests(TestCase):
    """Test metadata for contract types"""
    
    def test_get_contract_type_name(self):
        """Retrieve human-readable contract type name"""
        name = get_contract_type_name('SERVICE_AGREEMENT_INDIA')
        self.assertEqual(name, 'Service Agreement')
    
    def test_get_jurisdiction(self):
        """Retrieve jurisdiction for contract type"""
        jurisdiction = get_jurisdiction('SERVICE_AGREEMENT_INDIA')
        self.assertEqual(jurisdiction, 'India')
    
    def test_metadata_for_all_types(self):
        """All contract types have valid metadata"""
        types = get_all_contract_types()
        
        for contract_type_key in types:
            name = get_contract_type_name(contract_type_key)
            jurisdiction = get_jurisdiction(contract_type_key)
            
            self.assertIsNotNone(name)
            self.assertIsNotNone(jurisdiction)
            self.assertGreater(len(name), 0)
            self.assertGreater(len(jurisdiction), 0)


class DataIntegrityTests(TestCase):
    """Test data consistency and uniqueness"""
    
    def test_clause_ids_unique_within_type(self):
        """All clause IDs are unique for a contract type"""
        all_clauses = get_all_clauses_flat('SERVICE_AGREEMENT', 'INDIA')
        clause_ids = [c['id'] for c in all_clauses]
        
        unique_ids = set(clause_ids)
        self.assertEqual(len(clause_ids), len(unique_ids),
                       "Clause IDs should be unique within contract type")
    
    def test_clause_types_unique_within_type(self):
        """All clause types are unique for a contract type"""
        all_clauses = get_all_clauses_flat('SERVICE_AGREEMENT', 'INDIA')
        clause_types = [c['type'] for c in all_clauses]
        
        unique_types = set(clause_types)
        self.assertEqual(len(clause_types), len(unique_types),
                       "Clause types should be unique within contract type")
    
    def test_no_empty_clause_descriptions(self):
        """All clauses have meaningful descriptions"""
        all_clauses = get_all_clauses_flat('SERVICE_AGREEMENT', 'INDIA')
        
        for clause in all_clauses:
            self.assertIsNotNone(clause.get('description'))
            self.assertGreater(len(clause['description']), 5,
                             f"Description for {clause['id']} too short")
    
    def test_no_empty_recommendations(self):
        """All clauses have recommendations"""
        all_clauses = get_all_clauses_flat('SERVICE_AGREEMENT', 'INDIA')
        
        for clause in all_clauses:
            self.assertIsNotNone(clause.get('recommendations'))
            self.assertGreater(len(clause['recommendations']), 5)
    
    def test_no_empty_standard_text(self):
        """All clauses have standard text"""
        all_clauses = get_all_clauses_flat('SERVICE_AGREEMENT', 'INDIA')
        
        for clause in all_clauses:
            self.assertIsNotNone(clause.get('standard_text'))
            self.assertGreater(len(clause['standard_text']), 5)


class EdgeCaseTests(TestCase):
    """Test error handling and edge cases"""
    
    def test_invalid_contract_type(self):
        """Invalid contract type returns empty structure"""
        clauses = get_standard_clauses_for_type('INVALID_TYPE', 'INDIA')
        
        self.assertEqual(len(clauses['critical_clauses']), 0)
        self.assertEqual(len(clauses['important_clauses']), 0)
        self.assertEqual(len(clauses['optional_clauses']), 0)
    
    def test_invalid_jurisdiction(self):
        """Invalid jurisdiction returns empty structure"""
        clauses = get_standard_clauses_for_type('SERVICE_AGREEMENT', 'MARS')
        
        self.assertEqual(len(clauses['critical_clauses']), 0)
    
    def test_get_invalid_contract_type_name(self):
        """Invalid contract type returns None"""
        name = get_contract_type_name('INVALID_TYPE_INDIA')
        self.assertIsNone(name)
    
    def test_get_invalid_jurisdiction_name(self):
        """Invalid contract type returns None for jurisdiction"""
        jurisdiction = get_jurisdiction('INVALID_TYPE_INDIA')
        self.assertIsNone(jurisdiction)
    
    def test_missing_clauses_with_invalid_contract(self):
        """Missing clause detection handles invalid contract type"""
        missing = find_missing_clauses(['Payment Terms'], 'INVALID_TYPE', 'INDIA')
        
        # Should return structure with empty lists
        self.assertEqual(len(missing['missing_critical']), 0)
        self.assertEqual(len(missing['missing_important']), 0)
        self.assertEqual(len(missing['missing_optional']), 0)


class ContractSpecificTests(TestCase):
    """Test specific contract types for expected clauses"""
    
    def test_employment_contract_has_compensation_clause(self):
        """Employment contract includes compensation clause"""
        critical = get_critical_clauses_for_type('EMPLOYMENT_CONTRACT', 'INDIA')
        names = [c['type'] for c in critical]
        self.assertIn('Compensation and Benefits', names)
    
    def test_nda_has_definition_of_confidential_info(self):
        """NDA includes definition of confidential information"""
        critical = get_critical_clauses_for_type('NDA', 'INDIA')
        names = [c['type'] for c in critical]
        self.assertIn('Definition of Confidential Information', names)
    
    def test_partnership_has_capital_contribution(self):
        """Partnership agreement includes capital contribution"""
        critical = get_critical_clauses_for_type('PARTNERSHIP_AGREEMENT', 'INDIA')
        names = [c['type'] for c in critical]
        self.assertIn('Capital Contribution', names)
    
    def test_vendor_agreement_has_sla(self):
        """Vendor agreement includes SLA clause"""
        critical = get_critical_clauses_for_type('VENDOR_AGREEMENT', 'INDIA')
        names = [c['type'] for c in critical]
        self.assertIn('Delivery and SLA', names)


if __name__ == '__main__':
    import unittest
    unittest.main()

