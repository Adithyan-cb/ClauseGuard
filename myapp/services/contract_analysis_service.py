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
from datetime import datetime
from typing import Dict, List, Any, Optional

# Django imports
from django.conf import settings
from django.contrib.auth.models import User

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
        self.processor = ContractProcessor()
        self.chroma_manager = ChromaManager()
        self.clause_mapper = ContractClauseMapper()
        
        # Initialize Groq LLM via LangChain
        self.groq_api_key = os.getenv('GROQ_API_KEY')
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        self.llm = ChatGroq(
            model="mixtral-8x7b-32768",
            temperature=0.3,
            max_tokens=2048,
            api_key=self.groq_api_key,
            timeout=60
        )
        
        logger.info("ContractAnalysisService initialized successfully")
    
    # ============================================================================
    # MAIN ORCHESTRATOR METHOD
    # ============================================================================
    
    def analyze_contract(
        self,
        contract_file: Any,
        contract_type: str,
        jurisdiction: str,
        llm_model: str,
        user: User
    ) -> Dict[str, Any]:
        """
        Main entry point for contract analysis.
        
        Orchestrates the complete analysis workflow:
        1. Save contract and create database records
        2. Extract PDF text
        3. Perform AI analysis (summary, clauses, risks, suggestions)
        4. Save results to database
        5. Return analysis results
        
        Args:
            contract_file: Uploaded PDF file object
            contract_type: Type like "SERVICE_AGREEMENT_INDIA"
            jurisdiction: Location like "INDIA"
            llm_model: LLM model to use (not currently used, fixed to mixtral)
            user: Django User object
        
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
            logger.info(f"Starting contract analysis for user {user.username}")
            logger.info(f"Contract type: {contract_type}, Jurisdiction: {jurisdiction}")
            
            # ==================== STEP 1: SAVE & PREPARE ====================
            logger.info("STEP 1: Saving contract and creating database records...")
            contract, contract_analysis = self._save_and_prepare_contract(
                contract_file=contract_file,
                contract_type=contract_type,
                jurisdiction=jurisdiction,
                llm_model=llm_model,
                user=user
            )
            logger.info(f"Contract saved with ID: {contract.id}")
            logger.info(f"ContractAnalysis created with ID: {contract_analysis.id}")
            
            # ==================== STEP 2: EXTRACT TEXT ====================
            logger.info("STEP 2: Extracting text from PDF...")
            contract_text = self._extract_contract_text(
                contract_file=contract_file,
                contract_path=contract.contract_file.path
            )
            logger.info(f"Successfully extracted {len(contract_text)} characters from PDF")
            
            # ==================== STEP 3: SUMMARY ANALYSIS ====================
            logger.info("STEP 3: Analyzing contract summary...")
            summary_data = self._analyze_summary(
                contract_text=contract_text,
                contract_type=contract_type
            )
            logger.info("Summary analysis completed")
            
            # ==================== STEP 4: CLAUSE EXTRACTION ====================
            logger.info("STEP 4: Extracting clauses from contract...")
            clauses_data = self._extract_clauses(
                contract_text=contract_text
            )
            logger.info(f"Extracted {len(clauses_data.get('clauses', []))} clauses")
            
            # ==================== STEP 5: CHROMA SEARCH ====================
            logger.info("STEP 5: Searching ChromaDB for similar standard clauses...")
            chromadb_comparisons = self._search_similar_clauses(
                found_clauses=clauses_data.get('clauses', []),
                contract_type=contract_type
            )
            logger.info("ChromaDB search completed")
            
            # ==================== STEP 6: RISK ANALYSIS ====================
            logger.info("STEP 6: Analyzing risks in contract...")
            risks_data = self._analyze_risks(
                contract_text=contract_text,
                contract_type=contract_type,
                clauses=clauses_data.get('clauses', []),
                chromadb_comparisons=chromadb_comparisons
            )
            logger.info(f"Identified {len(risks_data.get('risks', []))} risks")
            
            # ==================== STEP 7: FIND MISSING CLAUSES ====================
            logger.info("STEP 7: Finding missing standard clauses...")
            missing_clauses = self._find_missing_clauses(
                found_clauses=clauses_data.get('clauses', []),
                contract_type=contract_type
            )
            logger.info(f"Found {len(missing_clauses)} missing clauses")
            
            # ==================== STEP 8: GENERATE SUGGESTIONS ====================
            logger.info("STEP 8: Generating improvement suggestions...")
            suggestions_data = self._generate_suggestions(
                contract_text=contract_text,
                contract_type=contract_type,
                missing_clauses=missing_clauses
            )
            logger.info(f"Generated {len(suggestions_data.get('suggestions', []))} suggestions")
            
            # ==================== STEP 9: SAVE RESULTS ====================
            logger.info("STEP 9: Saving analysis results to database...")
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
            logger.error(f"Error during contract analysis: {str(e)}", exc_info=True)
            
            # Mark analysis as failed
            try:
                if 'contract_analysis' in locals():
                    contract_analysis.extraction_status = 'failed'
                    contract_analysis.error_message = str(e)
                    contract_analysis.processing_time = time.time() - start_time
                    contract_analysis.save()
            except Exception as save_error:
                logger.error(f"Error saving failed status: {str(save_error)}")
            
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
            
            # Create chain: prompt -> LLM -> JSON parser
            chain = prompt | self.llm | JsonOutputParser()
            
            # Invoke the chain
            response = chain.invoke({
                "contract_text": contract_text[:5000],  # Limit input size
                "contract_type": contract_type
            })
            
            logger.debug(f"Received summary response from LLM")
            
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
            
            # Create chain
            chain = prompt | self.llm | JsonOutputParser()
            
            # Invoke the chain
            response = chain.invoke({
                "contract_text": contract_text[:5000]
            })
            
            logger.debug(f"Received clauses response from LLM")
            
            # Validate response using Pydantic
            validated_clauses = ClausesOutput(**response)
            
            return validated_clauses.model_dump()
        
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
            
            # Normalize contract type for ChromaDB collection name
            collection_name = f"{contract_type.lower()}"
            
            # Get or create collection
            try:
                collection = self.chroma_manager.get_or_create_collection(collection_name)
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
        chromadb_comparisons: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Use Groq LLM to identify risks in the contract.
        
        Args:
            contract_text: Full text extracted from PDF
            contract_type: Type of contract
            clauses: Extracted clauses
            chromadb_comparisons: ChromaDB comparison results
        
        Returns:
            Validated risks data dictionary
        """
        try:
            logger.debug("Sending risk analysis request to Groq LLM...")
            
            # Prepare prompt with context from ChromaDB
            prompt = PromptTemplate.from_template(RISK_ANALYSIS_PROMPT)
            
            # Create chain
            chain = prompt | self.llm | JsonOutputParser()
            
            # Prepare additional context
            comparison_summary = json.dumps(chromadb_comparisons, indent=2)[:2000]
            
            # Invoke the chain
            response = chain.invoke({
                "contract_text": contract_text[:5000],
                "contract_type": contract_type,
                "chromadb_comparisons": comparison_summary
            })
            
            logger.debug("Received risks response from LLM")
            
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
        missing_clauses: List[str]
    ) -> Dict[str, Any]:
        """
        Use Groq LLM to generate improvement suggestions.
        
        Args:
            contract_text: Full text extracted from PDF
            contract_type: Type of contract
            missing_clauses: List of missing clause types
        
        Returns:
            Validated suggestions data dictionary
        """
        try:
            logger.debug("Sending suggestions request to Groq LLM...")
            
            # Prepare prompt
            prompt = PromptTemplate.from_template(SUGGESTIONS_PROMPT)
            
            # Create chain
            chain = prompt | self.llm | JsonOutputParser()
            
            # Invoke the chain
            response = chain.invoke({
                "contract_type": contract_type,
                "jurisdiction": "INDIA",
                "missing_clauses": ", ".join(missing_clauses[:5])
            })
            
            logger.debug("Received suggestions response from LLM")
            
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
        Save all analysis results to database.
        
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
            # Convert all data to JSON strings
            contract_analysis.summary = json.dumps(summary)
            contract_analysis.clauses = json.dumps(clauses)
            contract_analysis.risks = json.dumps(risks)
            contract_analysis.suggestions = json.dumps(suggestions)
            
            # Update metadata
            contract_analysis.extraction_status = 'completed'
            contract_analysis.processing_time = processing_time
            contract_analysis.analysed_at = datetime.now()
            
            # Save to database
            contract_analysis.save()
            
            logger.info(f"Successfully saved analysis {contract_analysis.id} to database")
            return contract_analysis
        
        except Exception as e:
            logger.error(f"Error saving analysis results: {str(e)}")
            raise
