"""
Phase 3 Testing - Service Modules Tests

Simple tests to verify Phase 3 service modules work correctly.
Tests cover:
- PDF Processor (contract_processor.py)
- ChromaDB Manager (chroma_manager.py)
- Prompts (prompts.py)
- Contract Clause Mapping (contract_clause_mapping.py)

Run tests with:
    python manage.py test myapp.tests.test_phase3
"""

import os
import tempfile
from django.test import TestCase
from myapp.services import (
    ContractProcessor,
    ChromaManager,
    get_standard_clauses_for_type,
    get_critical_clauses_for_type,
    is_clause_standard,
    find_missing_clauses,
)
from myapp.services.prompts import (
    get_summary_prompt,
    get_clause_extraction_prompt,
    get_risk_analysis_prompt,
    get_suggestions_prompt,
)


class ContractProcessorTests(TestCase):
    """Test PDF extraction functionality"""

    def setUp(self):
        """Create test PDF file"""
        # Create a simple test PDF using reportlab if available
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter

            self.temp_file = tempfile.NamedTemporaryFile(
                suffix='.pdf',
                delete=False
            )
            c = canvas.Canvas(self.temp_file.name, pagesize=letter)
            c.drawString(100, 750, "Scope of Services")
            c.drawString(100, 730, "The Service Provider shall provide cloud services.")
            c.drawString(100, 700, "Payment Terms")
            c.drawString(100, 680, "Payment shall be made within 30 days.")
            c.save()
            self.pdf_path = self.temp_file.name
            self.has_reportlab = True
        except ImportError:
            self.has_reportlab = False
            self.pdf_path = None

    def tearDown(self):
        """Clean up test file"""
        if self.has_reportlab and self.pdf_path and os.path.exists(self.pdf_path):
            os.unlink(self.pdf_path)

    def test_validate_pdf_with_valid_pdf(self):
        """Test PDF validation with valid PDF"""
        if not self.has_reportlab:
            self.skipTest("reportlab not available")
        
        is_valid = ContractProcessor.validate_pdf(self.pdf_path)
        self.assertTrue(is_valid, "Valid PDF should return True")

    def test_validate_pdf_with_nonexistent_file(self):
        """Test PDF validation with nonexistent file"""
        is_valid = ContractProcessor.validate_pdf("/nonexistent/path/file.pdf")
        self.assertFalse(is_valid, "Nonexistent file should return False")

    def test_validate_pdf_with_text_file(self):
        """Test PDF validation with non-PDF file"""
        # Create a text file
        temp_file = tempfile.NamedTemporaryFile(suffix='.txt', delete=False)
        temp_file.write(b"This is just text")
        temp_file.close()
        
        try:
            is_valid = ContractProcessor.validate_pdf(temp_file.name)
            self.assertFalse(is_valid, "Text file should return False")
        finally:
            os.unlink(temp_file.name)

    def test_extract_text_with_valid_pdf(self):
        """Test text extraction from valid PDF"""
        if not self.has_reportlab:
            self.skipTest("reportlab not available")
        
        text = ContractProcessor.extract_text_from_pdf(self.pdf_path)
        
        # Verify text was extracted
        self.assertIsNotNone(text, "Extracted text should not be None")
        self.assertGreater(len(text), 0, "Extracted text should not be empty")
        self.assertIn("Scope of Services", text, "Extracted text should contain expected content")

    def test_extract_text_with_nonexistent_file(self):
        """Test text extraction with nonexistent file"""
        with self.assertRaises(ValueError) as context:
            ContractProcessor.extract_text_from_pdf("/nonexistent/path/file.pdf")
        
        self.assertIn("File not found", str(context.exception))


class ChromaManagerTests(TestCase):
    """Test ChromaDB Manager functionality"""

    def setUp(self):
        """Initialize ChromaDB Manager"""
        self.manager = ChromaManager()

    def test_chroma_manager_initialization(self):
        """Test ChromaDB Manager initializes correctly"""
        self.assertIsNotNone(self.manager.client, "ChromaDB client should be initialized")

    def test_get_or_create_collection(self):
        """Test creating and retrieving a collection"""
        collection_name = "test_service_agreement_india"
        collection = self.manager.get_or_create_collection(collection_name)
        
        self.assertIsNotNone(collection, "Collection should be created")
        
        # Try retrieving the same collection
        collection2 = self.manager.get_or_create_collection(collection_name)
        self.assertIsNotNone(collection2, "Collection should be retrieved")

    def test_add_standard_clauses(self):
        """Test adding standard clauses to ChromaDB"""
        collection_name = "test_add_clauses"
        clauses = [
            {
                "type": "Payment Terms",
                "text": "Payment shall be made within 30 days of invoice",
                "jurisdiction": "INDIA",
                "contract_type": "SERVICE_AGREEMENT",
                "recommendations": "Standard industry practice"
            },
            {
                "type": "Scope of Services",
                "text": "The Service Provider shall provide cloud infrastructure services",
                "jurisdiction": "INDIA",
                "contract_type": "SERVICE_AGREEMENT",
                "recommendations": "Should be specific and measurable"
            }
        ]
        
        # Add clauses (should not raise exception)
        try:
            self.manager.add_standard_clauses(collection_name, clauses)
            added = True
        except Exception as e:
            added = False
            print(f"Error adding clauses: {e}")
        
        self.assertTrue(added, "Should successfully add clauses")

    def test_search_similar_clauses(self):
        """Test searching for similar clauses"""
        collection_name = "test_search_clauses"
        
        # Add some test clauses
        clauses = [
            {
                "type": "Payment Terms",
                "text": "Payment shall be made within 30 days of invoice date",
                "jurisdiction": "INDIA",
                "contract_type": "SERVICE_AGREEMENT",
                "recommendations": "Standard"
            }
        ]
        self.manager.add_standard_clauses(collection_name, clauses)
        
        # Search for similar text
        results = self.manager.search_similar_clauses(
            collection_name,
            "Payment due within 15 days",
            top_k=1
        )
        
        # Should return results structure (even if empty)
        self.assertIn('ids', results, "Results should have 'ids' key")
        self.assertIn('documents', results, "Results should have 'documents' key")
        self.assertIn('metadatas', results, "Results should have 'metadatas' key")

    def test_delete_collection(self):
        """Test deleting a collection"""
        collection_name = "test_delete_collection"
        
        # Create a collection
        self.manager.get_or_create_collection(collection_name)
        
        # Delete it (should not raise exception)
        try:
            self.manager.delete_collection(collection_name)
            deleted = True
        except Exception as e:
            deleted = False
            print(f"Error deleting collection: {e}")
        
        self.assertTrue(deleted, "Should successfully delete collection")


class PromptsTests(TestCase):
    """Test prompt template functionality"""

    def test_summary_prompt_generation(self):
        """Test summary prompt template"""
        prompt = get_summary_prompt(
            "Service Agreement",
            "Sample contract text here"
        )
        
        self.assertIsNotNone(prompt, "Prompt should not be None")
        self.assertGreater(len(prompt), 0, "Prompt should not be empty")
        self.assertIn("Service Agreement", prompt, "Prompt should contain contract type")
        self.assertIn("Sample contract text here", prompt, "Prompt should contain contract text")
        self.assertIn("JSON", prompt, "Prompt should mention JSON format")

    def test_clause_extraction_prompt_generation(self):
        """Test clause extraction prompt template"""
        prompt = get_clause_extraction_prompt("Sample contract text")
        
        self.assertIsNotNone(prompt, "Prompt should not be None")
        self.assertIn("clause", prompt.lower(), "Prompt should mention clauses")
        self.assertIn("Sample contract text", prompt, "Prompt should contain contract text")

    def test_risk_analysis_prompt_generation(self):
        """Test risk analysis prompt template"""
        prompt = get_risk_analysis_prompt(
            "Service Agreement",
            "India",
            "Sample contract text"
        )
        
        self.assertIsNotNone(prompt, "Prompt should not be None")
        self.assertIn("risk", prompt.lower(), "Prompt should mention risks")
        self.assertIn("India", prompt, "Prompt should contain jurisdiction")

    def test_suggestions_prompt_generation(self):
        """Test suggestions prompt template"""
        prompt = get_suggestions_prompt(
            "Employment Contract",
            "US",
            "Sample contract text"
        )
        
        self.assertIsNotNone(prompt, "Prompt should not be None")
        self.assertIn("suggest", prompt.lower(), "Prompt should mention suggestions")
        self.assertIn("US", prompt, "Prompt should contain jurisdiction")


class ContractClauseMappingTests(TestCase):
    """Test contract clause mapping functionality"""

    def test_get_standard_clauses_for_service_agreement(self):
        """Test getting standard clauses for Service Agreement"""
        clauses = get_standard_clauses_for_type("SERVICE_AGREEMENT", "INDIA")
        
        self.assertIsNotNone(clauses, "Clauses list should not be None")
        self.assertGreater(len(clauses), 0, "Should return clauses")
        self.assertIn("Payment Terms", clauses, "Should include Payment Terms")
        self.assertIn("Scope of Services", clauses, "Should include Scope of Services")

    def test_get_standard_clauses_for_employment(self):
        """Test getting standard clauses for Employment"""
        clauses = get_standard_clauses_for_type("EMPLOYMENT", "INDIA")
        
        self.assertIsNotNone(clauses, "Clauses list should not be None")
        self.assertGreater(len(clauses), 0, "Should return clauses")
        self.assertIn("Compensation and Benefits", clauses, "Should include Compensation")

    def test_get_standard_clauses_for_nda(self):
        """Test getting standard clauses for NDA"""
        clauses = get_standard_clauses_for_type("NDA", "INDIA")
        
        self.assertIsNotNone(clauses, "Clauses list should not be None")
        self.assertGreater(len(clauses), 0, "Should return clauses")
        self.assertIn("Definition of Confidential Information", clauses)

    def test_get_critical_clauses_only(self):
        """Test getting only critical clauses"""
        critical = get_critical_clauses_for_type("SERVICE_AGREEMENT", "INDIA")
        all_clauses = get_standard_clauses_for_type("SERVICE_AGREEMENT", "INDIA")
        
        self.assertIsNotNone(critical, "Critical clauses should not be None")
        self.assertGreater(len(critical), 0, "Should return critical clauses")
        self.assertLess(
            len(critical),
            len(all_clauses),
            "Critical should be subset of all clauses"
        )

    def test_is_clause_standard(self):
        """Test checking if clause is standard"""
        is_standard = is_clause_standard(
            "Payment Terms",
            "SERVICE_AGREEMENT",
            "INDIA"
        )
        self.assertTrue(is_standard, "Payment Terms should be standard for Service Agreement")
        
        is_not_standard = is_clause_standard(
            "Nonexistent Clause",
            "SERVICE_AGREEMENT",
            "INDIA"
        )
        self.assertFalse(is_not_standard, "Nonexistent clause should not be standard")

    def test_find_missing_clauses(self):
        """Test finding missing clauses"""
        found_clauses = [
            "Scope of Services",
            "Payment Terms",
            "Confidentiality"
        ]
        
        missing = find_missing_clauses(
            found_clauses,
            "SERVICE_AGREEMENT",
            "INDIA"
        )
        
        self.assertIsNotNone(missing, "Missing clauses dict should not be None")
        self.assertIn("missing_critical", missing, "Should have missing_critical key")
        self.assertIn("total_missing", missing, "Should have total_missing key")
        
        # These critical clauses should be missing
        self.assertIn(
            "Term and Termination",
            missing["missing_critical"],
            "Term and Termination should be missing"
        )

    def test_find_missing_clauses_empty_list(self):
        """Test finding missing clauses with empty found list"""
        missing = find_missing_clauses(
            [],
            "SERVICE_AGREEMENT",
            "INDIA"
        )
        
        # All standard clauses should be missing
        self.assertGreater(
            missing["total_missing"],
            0,
            "Should report missing clauses"
        )

    def test_unsupported_contract_type(self):
        """Test with unsupported contract type"""
        clauses = get_standard_clauses_for_type("UNSUPPORTED_TYPE", "INDIA")
        
        self.assertEqual(clauses, [], "Should return empty list for unsupported type")

    def test_case_insensitive_missing_clauses(self):
        """Test that missing clause detection is case-insensitive"""
        found_clauses = [
            "scope of services",  # lowercase
            "PAYMENT TERMS",       # uppercase
        ]
        
        missing = find_missing_clauses(
            found_clauses,
            "SERVICE_AGREEMENT",
            "INDIA"
        )
        
        # Should recognize "scope of services" and "PAYMENT TERMS" despite case difference
        self.assertNotIn(
            "Scope of Services",
            missing["missing_critical"],
            "Should recognize clause despite case difference"
        )


# ============================================================================
# QUICK VERIFICATION TESTS (Run without full Django Test framework)
# ============================================================================

def test_phase3_quick_verification():
    """
    Quick verification that all Phase 3 modules work.
    Run this in Django shell: python manage.py shell < test_script.py
    
    Or in shell:
    >>> from myapp.tests.test_phase3 import test_phase3_quick_verification
    >>> test_phase3_quick_verification()
    """
    print("\n" + "="*70)
    print("PHASE 3 QUICK VERIFICATION TEST")
    print("="*70)
    
    # Test 1: Import modules
    print("\n[TEST 1] Importing service modules...")
    try:
        from myapp.services import ContractProcessor, ChromaManager
        from myapp.services.prompts import get_summary_prompt
        from myapp.services.contract_clause_mapping import get_standard_clauses_for_type
        print("✓ All modules imported successfully")
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False
    
    # Test 2: PDF Processor
    print("\n[TEST 2] Testing ContractProcessor...")
    try:
        is_valid = ContractProcessor.validate_pdf("/nonexistent.pdf")
        assert is_valid == False, "Should return False for nonexistent file"
        print("✓ ContractProcessor.validate_pdf() works")
    except Exception as e:
        print(f"✗ ContractProcessor test failed: {e}")
        return False
    
    # Test 3: ChromaDB Manager
    print("\n[TEST 3] Testing ChromaManager...")
    try:
        manager = ChromaManager()
        collection = manager.get_or_create_collection("test_verification")
        assert collection is not None, "Collection should be created"
        print("✓ ChromaManager initialization works")
    except Exception as e:
        print(f"✗ ChromaManager test failed: {e}")
        return False
    
    # Test 4: Prompts
    print("\n[TEST 4] Testing Prompts...")
    try:
        prompt = get_summary_prompt("Service Agreement", "Sample text")
        assert len(prompt) > 0, "Prompt should not be empty"
        assert "Service Agreement" in prompt, "Prompt should contain contract type"
        print("✓ Prompt generation works")
    except Exception as e:
        print(f"✗ Prompt test failed: {e}")
        return False
    
    # Test 5: Contract Clause Mapping
    print("\n[TEST 5] Testing Contract Clause Mapping...")
    try:
        clauses = get_standard_clauses_for_type("SERVICE_AGREEMENT", "INDIA")
        assert len(clauses) > 0, "Should return clauses"
        assert "Payment Terms" in clauses, "Should include Payment Terms"
        print(f"✓ Contract mapping works (found {len(clauses)} clauses)")
    except Exception as e:
        print(f"✗ Contract mapping test failed: {e}")
        return False
    
    print("\n" + "="*70)
    print("ALL TESTS PASSED ✓")
    print("="*70 + "\n")
    return True
