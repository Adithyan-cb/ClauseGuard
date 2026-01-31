"""
Contract Analysis Service Module - Phase 3

This is the MAIN ORCHESTRATOR that coordinates the entire contract analysis workflow.
It brings together:
1. PDF extraction (ContractProcessor)
2. LLM analysis (Groq via LangChain)
3. Vector search (ChromaDB)
4. Data validation (Pydantic schemas)
5. Database storage (Django ORM)

Author: ClauseGuard Development Team
Date: January 17, 2026
"""

import json
import logging
import time
import os
import re
from datetime import datetime
from typing import Dict, List, Any, Optional
from io import BytesIO

# Django imports
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.base import ContentFile

# LangChain imports for Groq LLM
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import LangChainException

# Application imports
from myapp.models import Contract, ContractAnalysis
from myapp.services.contract_processor import ContractProcessor
from myapp.services.chroma_manager import ChromaManager
from myapp.services.contract_clause_mapping import ContractClauseMapper
from myapp.services.pdf_generator import generate_analysis_pdf
from myapp.services.prompts import (
    SUMMARY_PROMPT,
    CLAUSE_EXTRACTION_PROMPT,
    RISK_ANALYSIS_PROMPT,
    SUGGESTIONS_PROMPT
)
from myapp.services.schemas import (
    SummaryOutput,
    ClausesOutput,
    RisksOutput,
    SuggestionsOutput
)

logger = logging.getLogger(__name__)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def clean_json_output(text: str) -> str:
    """
    Clean LLM output by removing markdown code fences and extra whitespace.
    
    LLMs sometimes wrap JSON in markdown code fences (```json...```) even when
    explicitly told not to. This function strips them out.
    
    Args:
        text: Raw output from LLM
    
    Returns:
        Clean JSON string ready for parsing
    """
    # Remove markdown code fences (```json ... ``` or just ``` ... ```)
    text = re.sub(r'^```(?:json)?\s*', '', text.strip())
    text = re.sub(r'\s*```$', '', text.strip())
    
    # Remove any leading/trailing whitespace
    text = text.strip()
    
    return text


class ContractAnalysisService:
    """
    Main orchestrator service for contract analysis.
    
    This service coordinates the entire analysis pipeline:
    1. Extract text from PDF
    2. Analyze with Groq LLM for summary
    3. Extract clauses with ChromaDB comparison
    4. Analyze risks
    5. Generate suggestions
    6. Save results to database
    
    Example usage:
        >>> service = ContractAnalysisService()
        >>> result = service.analyze_contract(
        ...     contract_file=file_obj,
        ...     contract_type="SERVICE_AGREEMENT_INDIA",
        ...     jurisdiction="INDIA",
        ...     llm_model="mixtral-8x7b-32768",
        ...     user=user_obj
        ... )
    """
    
    def __init__(self):
        """Initialize the service with required managers and processors."""
        logger.info("="*80)
        logger.info("ContractAnalysisService.__init__() called")
        
        logger.info("  - Initializing ContractProcessor...")
        self.processor = ContractProcessor()
        logger.info("  ✓ ContractProcessor initialized")
        
        logger.info("  - Initializing ChromaManager...")
        try:
            self.chroma_manager = ChromaManager()
            if self.chroma_manager.available:
                logger.info("  ✓ ChromaManager initialized")
            else:
                logger.warning("  ⚠ ChromaManager initialized but not available (dependencies missing)")
                logger.warning("    Clause similarity search will be disabled")
        except Exception as e:
            logger.error(f"  ✗ Error initializing ChromaManager: {str(e)}")
            logger.warning("  ⚠ Creating fallback ChromaManager instance")
            self.chroma_manager = ChromaManager()
        
        logger.info("  - Initializing ContractClauseMapper...")
        self.clause_mapper = ContractClauseMapper()
        logger.info("  ✓ ContractClauseMapper initialized")
        
        # Initialize Groq LLM via LangChain
        logger.info("  - Reading GROQ_API_KEY from environment...")
        self.groq_api_key = os.getenv('GROQ_API_KEY')
        if not self.groq_api_key:
            logger.error("✗ GROQ_API_KEY not found in environment variables!")
            logger.error("  Solution: Add GROQ_API_KEY to .env or system environment")
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        logger.info(f"  ✓ GROQ_API_KEY found (starts with: {self.groq_api_key[:10]}...)")
        
        logger.info("  - Initializing ChatGroq with Llama 3.1 70B...")
        try:
            self.llm = ChatGroq(
                model="llama-3.3-70b-versatile",
                temperature=0.3,
                max_tokens=2048,
                api_key=self.groq_api_key,
                timeout=60
            )
            logger.info("  ✓ ChatGroq initialized successfully")
        except Exception as e:
            logger.error(f"✗ Failed to initialize ChatGroq: {str(e)}", exc_info=True)
            logger.error("  Check: Is GROQ_API_KEY valid?")
            raise
        
        logger.info("="*80)
        logger.info("✓ ContractAnalysisService initialized successfully")
        logger.info("="*80)
    
    # ============================================================================
    # MAIN ORCHESTRATOR METHOD
    # ============================================================================
    
    def analyze_contract(
        self,
        contract_id: int,
        contract_analysis_id: int,
        contract_type: str,
        jurisdiction: str,
        llm_model: str
    ) -> Dict[str, Any]:
        """
        Main entry point for contract analysis.
        
        Orchestrates the complete analysis workflow:
        1. Fetch contract and analysis records (already created in views.py)
        2. Extract PDF text
        3. Perform AI analysis (summary, clauses, risks, suggestions)
        4. Save results to database
        5. Return analysis results
        
        IMPORTANT: Contract and ContractAnalysis records must already exist
        (created in views.py before starting background thread)
        
        Args:
            contract_id: ID of already-created Contract record
            contract_analysis_id: ID of already-created ContractAnalysis record
            contract_type: Type like "SERVICE_AGREEMENT_INDIA"
            jurisdiction: Location like "INDIA"
            llm_model: LLM model to use (not currently used, fixed to mixtral)
        
        Returns:
            Dict with:
            {
                "status": "success",
                "analysis_id": 1,
                "contract_id": 1,
                "processing_time": 45.3,
                "summary": {...},
                "clauses": {...},
                "risks": {...},
                "suggestions": {...}
            }
        
        Raises:
            Exception: If any critical step fails
        """
        start_time = time.time()
        
        try:
            logger.info("="*80)
            logger.info("ANALYZE_CONTRACT() CALLED")
            logger.info(f"  Contract ID: {contract_id}")
            logger.info(f"  Analysis ID: {contract_analysis_id}")
            logger.info(f"  Contract Type: {contract_type}")
            logger.info(f"  Jurisdiction: {jurisdiction}")
            logger.info(f"  LLM Model: {llm_model}")
            logger.info("="*80)
            
            # ==================== STEP 1: FETCH EXISTING RECORDS ====================
            logger.info("[STEP 1/7] Fetching contract and analysis records...")
            try:
                contract = Contract.objects.get(id=contract_id)
                contract_analysis = ContractAnalysis.objects.get(id=contract_analysis_id)
                logger.info(f"  ✓ Contract loaded (ID: {contract.id})")
                logger.info(f"  ✓ ContractAnalysis loaded (ID: {contract_analysis.id})")
            except Contract.DoesNotExist:
                raise ValueError(f"Contract with ID {contract_id} not found")
            except ContractAnalysis.DoesNotExist:
                raise ValueError(f"ContractAnalysis with ID {contract_analysis_id} not found")
            
            # ==================== STEP 2: EXTRACT TEXT ====================
            logger.info("[STEP 2/7] Extracting text from PDF...")
            try:
                # Use the contract file path from the already-saved file
                contract_text = self._extract_contract_text(
                    contract_file=None,  # Not needed, we have the path
                    contract_path=contract.contract_file.path
                )
                logger.info(f"  ✓ Successfully extracted {len(contract_text)} characters from PDF")
            except Exception as e:
                logger.error(f"  ✗ PDF extraction failed: {str(e)}", exc_info=True)
                raise
            
            # ==================== STEP 3: SUMMARY ANALYSIS ====================
            logger.info("[STEP 3/7] Analyzing contract summary (calling Groq LLM)...")
            try:
                summary_data = self._analyze_summary(
                    contract_text=contract_text,
                    contract_type=contract_type
                )
                logger.info(f"  ✓ Summary analysis completed")
                logger.info(f"    - Contract Type: {summary_data.get('contract_type', 'N/A')}")
                logger.info(f"    - Parties: {len(summary_data.get('parties', []))} parties identified")
            except Exception as e:
                logger.error(f"  ✗ Summary analysis failed (Groq issue?): {str(e)}", exc_info=True)
                raise
            
            # ==================== STEP 4: CLAUSE EXTRACTION ====================
            logger.info("[STEP 4/7] Extracting clauses from contract (calling Groq LLM)...")
            try:
                clauses_data = self._extract_clauses(
                    contract_text=contract_text
                )
                logger.info(f"  ✓ Extracted {len(clauses_data.get('clauses', []))} clauses")
            except Exception as e:
                logger.error(f"  ✗ Clause extraction failed (Groq issue?): {str(e)}", exc_info=True)
                raise
            
            # ==================== STEP 5: CHROMA SEARCH ====================
            logger.info("[STEP 5/7] Searching ChromaDB for similar standard clauses...")
            try:
                chromadb_comparisons = self._search_similar_clauses(
                    found_clauses=clauses_data.get('clauses', []),
                    contract_type=contract_type
                )
                logger.info(f"  ✓ ChromaDB search completed")
            except Exception as e:
                logger.error(f"  ✗ ChromaDB search failed: {str(e)}", exc_info=True)
                raise
            
            # ==================== STEP 6: RISK ANALYSIS ====================
            logger.info("[STEP 6/7] Analyzing risks in contract (calling Groq LLM)...")
            try:
                risks_data = self._analyze_risks(
                    contract_text=contract_text,
                    contract_type=contract_type,
                    clauses=clauses_data.get('clauses', []),
                    chromadb_comparisons=chromadb_comparisons,
                    jurisdiction=jurisdiction
                )
                logger.info(f"  ✓ Identified {len(risks_data.get('risks', []))} risks")
            except Exception as e:
                logger.error(f"  ✗ Risk analysis failed (Groq issue?): {str(e)}", exc_info=True)
                raise
            
            # ==================== STEP 7: GENERATE SUGGESTIONS ====================
            logger.info("[STEP 7/7] Generating improvement suggestions (calling Groq LLM)...")
            try:
                missing_clauses = self._find_missing_clauses(
                    found_clauses=clauses_data.get('clauses', []),
                    contract_type=contract_type
                )
                logger.info(f"  - Found {len(missing_clauses)} missing clauses")
                
                suggestions_data = self._generate_suggestions(
                    contract_text=contract_text,
                    contract_type=contract_type,
                    missing_clauses=missing_clauses,
                    jurisdiction=jurisdiction
                )
                logger.info(f"  ✓ Generated {len(suggestions_data.get('suggestions', []))} suggestions")
            except Exception as e:
                logger.error(f"  ✗ Suggestion generation failed (Groq issue?): {str(e)}", exc_info=True)
                raise
            
            # ==================== STEP 8: SAVE RESULTS ====================
            logger.info("[STEP 8/7] Saving analysis results to database...")
            processing_time = time.time() - start_time
            
            contract_analysis = self._save_analysis_results(
                contract_analysis=contract_analysis,
                summary=summary_data,
                clauses=clauses_data,
                risks=risks_data,
                suggestions=suggestions_data,
                processing_time=processing_time
            )
            logger.info(f"Analysis saved successfully in {processing_time:.2f} seconds")
            
            # ==================== RETURN RESULTS ====================
            logger.info("="*80)
            logger.info(f"✓ ANALYSIS COMPLETED SUCCESSFULLY")
            logger.info(f"  - Analysis ID: {contract_analysis.id}")
            logger.info(f"  - Processing time: {processing_time:.2f}s")
            logger.info(f"  - Summary generated: {bool(summary_data)}")
            logger.info(f"  - Clauses found: {len(clauses_data.get('clauses', []))}")
            logger.info(f"  - Risks identified: {len(risks_data.get('risks', []))}")
            logger.info(f"  - Suggestions generated: {len(suggestions_data.get('suggestions', []))}")
            logger.info("="*80)
            
            return {
                "status": "success",
                "analysis_id": contract_analysis.id,
                "contract_id": contract.id,
                "processing_time": processing_time,
                "summary": summary_data,
                "clauses": clauses_data,
                "risks": risks_data,
                "suggestions": suggestions_data
            }
        
        except Exception as e:
            logger.error("="*80)
            logger.error(f"✗ ERROR DURING CONTRACT ANALYSIS")
            logger.error(f"  Error Type: {type(e).__name__}")
            logger.error(f"  Error Message: {str(e)}")
            logger.error("="*80)
            logger.error("Full traceback:", exc_info=True)
            
            # Mark analysis as failed
            try:
                if 'contract_analysis' in locals():
                    contract_analysis.extraction_status = 'failed'
                    contract_analysis.error_message = str(e)
                    contract_analysis.processing_time = time.time() - start_time
                    contract_analysis.save()
                    logger.error(f"  ✓ Marked analysis {contract_analysis.id} as failed in database")
            except Exception as save_error:
                logger.error(f"  ✗ Error saving failed status: {str(save_error)}")
            
            raise
    
    # ============================================================================
    # STEP 1: SAVE & PREPARE
    # ============================================================================
    
    def _save_and_prepare_contract(
        self,
        contract_file: Any,
        contract_type: str,
        jurisdiction: str,
        llm_model: str,
        user: User
    ) -> tuple:
        """
        Save uploaded contract to database and create analysis record.
        
        Args:
            contract_file: Uploaded file object
            contract_type: Contract type string
            jurisdiction: Jurisdiction string
            llm_model: LLM model string
            user: Django User object
        
        Returns:
            Tuple of (Contract, ContractAnalysis) database objects
        """
        try:
            # Create Contract record
            contract = Contract.objects.create(
                user=user,
                contract_file=contract_file,
                contract_type=contract_type,
                jurisdiction=jurisdiction,
                llm_model=llm_model
            )
            
            # Create ContractAnalysis record
            contract_analysis = ContractAnalysis.objects.create(
                contract=contract,
                extraction_status='processing'
            )
            
            return contract, contract_analysis
        
        except Exception as e:
            logger.error(f"Error saving contract: {str(e)}")
            raise
    
    # ============================================================================
    # STEP 2: EXTRACT PDF TEXT
    # ============================================================================
    
    def _extract_contract_text(
        self,
        contract_file: Any,
        contract_path: str
    ) -> str:
        """
        Extract text from uploaded PDF file.
        
        Args:
            contract_file: File object
            contract_path: Full path to file on disk
        
        Returns:
            Extracted text from PDF
        
        Raises:
            ValueError: If PDF extraction fails
        """
        try:
            extracted_text = self.processor.extract_text_from_pdf(contract_path)
            
            if not extracted_text or len(extracted_text.strip()) < 100:
                raise ValueError("PDF appears to be empty or unreadable")
            
            return extracted_text
        
        except Exception as e:
            logger.error(f"Error extracting PDF text: {str(e)}")
            raise
    
    # ============================================================================
    # STEP 3: ANALYZE SUMMARY
    # ============================================================================
    
    def _analyze_summary(
        self,
        contract_text: str,
        contract_type: str
    ) -> Dict[str, Any]:
        """
        Use Groq LLM to analyze and summarize the contract.
        
        Args:
            contract_text: Full text extracted from PDF
            contract_type: Type of contract
        
        Returns:
            Validated summary data dictionary
        """
        try:
            logger.debug("Sending summary analysis request to Groq LLM...")
            
            # Prepare prompt
            prompt = PromptTemplate.from_template(SUMMARY_PROMPT)
            
            # Create chain WITHOUT JsonOutputParser - we'll parse manually
            chain = prompt | self.llm
            
            # Invoke the chain
            llm_output = chain.invoke({
                "contract_text": contract_text[:5000],  # Limit input size
                "contract_type": contract_type
            })
            
            logger.debug(f"Received summary response from LLM")
            
            # Extract text content from LLM output
            if hasattr(llm_output, 'content'):
                raw_text = llm_output.content
            else:
                raw_text = str(llm_output)
            
            # Clean the JSON output (remove markdown code fences)
            clean_text = clean_json_output(raw_text)
            
            # Parse JSON manually
            response = json.loads(clean_text)
            
            # Validate response using Pydantic
            validated_summary = SummaryOutput(**response)
            
            return validated_summary.model_dump()
        
        except Exception as e:
            logger.error(f"Error analyzing summary: {str(e)}")
            # Return safe defaults instead of failing completely
            return {
                "summary": "Unable to generate summary",
                "contract_type": contract_type,
                "parties": [],
                "duration": "Unknown",
                "key_obligations": [],
                "financial_terms": "Not specified",
                "jurisdiction": "Unknown"
            }
    
    # ============================================================================
    # STEP 4: EXTRACT CLAUSES
    # ============================================================================
    
    def _extract_clauses(self, contract_text: str) -> Dict[str, Any]:
        """
        Use Groq LLM to extract all clauses from contract.
        
        Args:
            contract_text: Full text extracted from PDF
        
        Returns:
            Validated clauses data dictionary
        """
        try:
            logger.debug("Sending clause extraction request to Groq LLM...")
            
            # Prepare prompt
            prompt = PromptTemplate.from_template(CLAUSE_EXTRACTION_PROMPT)
            
            # Create chain WITHOUT JsonOutputParser - we'll parse manually
            chain = prompt | self.llm
            
            # Invoke the chain
            llm_output = chain.invoke({
                "contract_text": contract_text[:5000]
            })
            
            logger.debug(f"Received clauses response from LLM")
            
            # Extract text content from LLM output
            if hasattr(llm_output, 'content'):
                raw_text = llm_output.content
            else:
                raw_text = str(llm_output)
            
            # Clean the JSON output (remove markdown code fences)
            clean_text = clean_json_output(raw_text)
            logger.debug(f"Cleaned JSON: {clean_text[:100]}...")
            
            # Parse JSON manually
            response = json.loads(clean_text)
            
            # Validate response using Pydantic
            validated_clauses = ClausesOutput(**response)
            
            return validated_clauses.model_dump()
        
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON from clause extraction: {str(e)}")
            logger.error(f"Raw response was: {raw_text[:500]}")
            # Return safe defaults
            return {
                "clauses": [],
                "total_clauses": 0
            }
        except Exception as e:
            logger.error(f"Error extracting clauses: {str(e)}")
            # Return safe defaults
            return {
                "clauses": [],
                "total_clauses": 0
            }
    
    # ============================================================================
    # STEP 5: SEARCH SIMILAR CLAUSES IN CHROMA DB
    # ============================================================================
    
    def _search_similar_clauses(
        self,
        found_clauses: List[Dict[str, str]],
        contract_type: str
    ) -> Dict[str, Any]:
        """
        Search ChromaDB for standard clauses similar to found clauses.
        
        Args:
            found_clauses: List of clauses extracted from contract
            contract_type: Type of contract
        
        Returns:
            Dictionary with comparisons for each clause
        """
        try:
            comparisons = {}
            
            # Check if ChromaDB is available
            if not self.chroma_manager.available:
                logger.debug("ChromaDB not available - skipping clause comparison")
                return {}
            
            # Normalize contract type for ChromaDB collection name
            collection_name = f"{contract_type.lower()}"
            
            # Get or create collection
            try:
                collection = self.chroma_manager.get_or_create_collection(collection_name)
                if collection is None:
                    logger.debug("ChromaDB collection not available - skipping clause comparison")
                    return {}
            except Exception as e:
                logger.warning(f"Could not access ChromaDB collection: {str(e)}")
                return {}
            
            # Search for similar clauses
            for clause in found_clauses:
                clause_type = clause.get('type', 'Unknown')
                clause_text = clause.get('text', '')
                
                try:
                    # Search ChromaDB
                    similar = self.chroma_manager.search_similar_clauses(
                        collection_name=collection_name,
                        query_text=clause_text,
                        top_k=3
                    )
                    
                    comparisons[clause_type] = {
                        "found_text": clause_text,
                        "similar_standards": similar if similar else []
                    }
                
                except Exception as e:
                    logger.warning(f"Error searching for similar clauses of type {clause_type}: {str(e)}")
                    comparisons[clause_type] = {
                        "found_text": clause_text,
                        "similar_standards": []
                    }
            
            return comparisons
        
        except Exception as e:
            logger.error(f"Error in ChromaDB search: {str(e)}")
            return {}
    
    # ============================================================================
    # STEP 6: ANALYZE RISKS
    # ============================================================================
    
    def _analyze_risks(
        self,
        contract_text: str,
        contract_type: str,
        clauses: List[Dict[str, str]],
        chromadb_comparisons: Dict[str, Any],
        jurisdiction: str = "INDIA"
    ) -> Dict[str, Any]:
        """
        Use Groq LLM to identify risks in the contract.
        
        Args:
            contract_text: Full text extracted from PDF
            contract_type: Type of contract
            clauses: Extracted clauses
            chromadb_comparisons: ChromaDB comparison results
            jurisdiction: Jurisdiction for contract (defaults to INDIA)
        
        Returns:
            Validated risks data dictionary
        """
        try:
            logger.debug("Sending risk analysis request to Groq LLM...")
            
            # Prepare prompt with context from ChromaDB
            prompt = PromptTemplate.from_template(RISK_ANALYSIS_PROMPT)
            
            # Create chain WITHOUT JsonOutputParser - we'll parse manually
            chain = prompt | self.llm
            
            # Invoke the chain with all required variables
            llm_output = chain.invoke({
                "contract_text": contract_text[:5000],
                "contract_type": contract_type,
                "jurisdiction": jurisdiction
            })
            
            logger.debug("Received risks response from LLM")
            
            # Extract text content from LLM output
            if hasattr(llm_output, 'content'):
                raw_text = llm_output.content
            else:
                raw_text = str(llm_output)
            
            # Clean the JSON output (remove markdown code fences)
            clean_text = clean_json_output(raw_text)
            
            # Parse JSON manually
            response = json.loads(clean_text)
            
            # Validate response using Pydantic
            validated_risks = RisksOutput(**response)
            
            return validated_risks.model_dump()
        
        except Exception as e:
            logger.error(f"Error analyzing risks: {str(e)}")
            # Return safe defaults
            return {
                "risks": [],
                "missing_clauses": [],
                "total_risks": 0,
                "total_missing": 0
            }
    
    # ============================================================================
    # STEP 7: FIND MISSING CLAUSES
    # ============================================================================
    
    def _find_missing_clauses(
        self,
        found_clauses: List[Dict[str, str]],
        contract_type: str
    ) -> List[str]:
        """
        Compare found clauses against standard clauses to find gaps.
        
        Args:
            found_clauses: List of clauses extracted from contract
            contract_type: Type of contract
        
        Returns:
            List of missing clause types
        """
        try:
            # Extract found clause types
            found_types = set()
            for clause in found_clauses:
                clause_type = clause.get('type', '').strip()
                if clause_type:
                    found_types.add(clause_type.lower())
            
            # Get standard clauses for this contract type
            try:
                standard_clauses = self.clause_mapper.get_standard_clauses_for_type(
                    contract_type
                )
            except Exception as e:
                logger.warning(f"Could not load standard clauses: {str(e)}")
                return []
            
            # Find missing clauses
            missing = []
            
            for category in ['critical_clauses', 'important_clauses']:
                if category in standard_clauses:
                    for standard_clause in standard_clauses[category]:
                        standard_type = standard_clause.get('type', '').lower()
                        
                        # Check if this clause type was found
                        if not any(standard_type in found.lower() or found.lower() in standard_type 
                                  for found in found_types):
                            missing.append(standard_clause.get('type', 'Unknown'))
            
            return missing[:10]  # Limit to top 10 missing clauses
        
        except Exception as e:
            logger.error(f"Error finding missing clauses: {str(e)}")
            return []
    
    # ============================================================================
    # STEP 8: GENERATE SUGGESTIONS
    # ============================================================================
    
    def _generate_suggestions(
        self,
        contract_text: str,
        contract_type: str,
        missing_clauses: List[str],
        jurisdiction: str = "INDIA"
    ) -> Dict[str, Any]:
        """
        Use Groq LLM to generate improvement suggestions.
        
        Args:
            contract_text: Full text extracted from PDF
            contract_type: Type of contract
            missing_clauses: List of missing clause types
            jurisdiction: Jurisdiction for contract (defaults to INDIA)
        
        Returns:
            Validated suggestions data dictionary
        """
        try:
            logger.debug("Sending suggestions request to Groq LLM...")
            
            # Prepare prompt
            prompt = PromptTemplate.from_template(SUGGESTIONS_PROMPT)
            
            # Create chain WITHOUT JsonOutputParser - we'll parse manually
            chain = prompt | self.llm
            
            # Invoke the chain with all required variables
            llm_output = chain.invoke({
                "contract_text": contract_text[:5000],
                "contract_type": contract_type,
                "jurisdiction": jurisdiction
            })
            
            logger.debug("Received suggestions response from LLM")
            
            # Extract text content from LLM output
            if hasattr(llm_output, 'content'):
                raw_text = llm_output.content
            else:
                raw_text = str(llm_output)
            
            # Clean the JSON output (remove markdown code fences)
            clean_text = clean_json_output(raw_text)
            
            # Parse JSON manually
            response = json.loads(clean_text)
            
            # Validate response using Pydantic
            validated_suggestions = SuggestionsOutput(**response)
            
            return validated_suggestions.model_dump()
        
        except Exception as e:
            logger.error(f"Error generating suggestions: {str(e)}")
            # Return safe defaults
            return {
                "suggestions": [],
                "total_suggestions": 0
            }
    
    # ============================================================================
    # STEP 9: SAVE RESULTS TO DATABASE
    # ============================================================================
    
    def _save_analysis_results(
        self,
        contract_analysis: ContractAnalysis,
        summary: Dict[str, Any],
        clauses: Dict[str, Any],
        risks: Dict[str, Any],
        suggestions: Dict[str, Any],
        processing_time: float
    ) -> ContractAnalysis:
        """
        Save all analysis results to database and generate PDF report.
        
        Args:
            contract_analysis: ContractAnalysis database object
            summary: Summary analysis results
            clauses: Clauses analysis results
            risks: Risks analysis results
            suggestions: Suggestions results
            processing_time: Total processing time in seconds
        
        Returns:
            Updated ContractAnalysis object
        """
        try:
            # Generate PDF report from analysis data
            logger.info("Generating PDF report from analysis data...")
            analysis_data = {
                'summary': summary,
                'clauses': clauses,
                'risks': risks,
                'suggestions': suggestions
            }
            
            contract_name = contract_analysis.contract.contract_file.name
            pdf_buffer = generate_analysis_pdf(analysis_data, contract_name)
            
            # Save PDF to ContractAnalysis model
            pdf_filename = f"analysis_{contract_analysis.contract.id}_{int(time.time())}.pdf"
            contract_analysis.analysis_pdf.save(
                pdf_filename,
                ContentFile(pdf_buffer.getvalue()),
                save=True
            )
            logger.info(f"  ✓ PDF saved: {pdf_filename}")
            
            # Update metadata
            contract_analysis.processing_time = processing_time
            contract_analysis.analysed_at = datetime.now()
            contract_analysis.error_message = None
            
            # Save to database
            contract_analysis.save()
            
            logger.info(f"Successfully saved analysis {contract_analysis.id} to database with PDF")
            return contract_analysis
        
        except Exception as e:
            logger.error(f"Error saving analysis results: {str(e)}", exc_info=True)
            # Update error status
            try:
                contract_analysis.error_message = str(e)
                contract_analysis.save()
            except:
                pass
            raise
