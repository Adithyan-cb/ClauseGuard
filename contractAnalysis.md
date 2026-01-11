# **Contract Analysis Feature - Detailed Implementation Plan**

**Version:** 2.0  
**Last Updated:** January 11, 2026  
**Status:** Ready for Implementation (Phases 1 & 2 Complete)  
**Project:** ClauseGuard - Intelligent Contract Analysis System using RAG

---

## **Table of Contents**

1. [Introduction & System Overview](#introduction--system-overview)
2. [How The System Works (Step-by-Step)](#how-the-system-works-step-by-step)
3. [Phase 1: Environment Setup](#phase-1-environment-setup) ✓ COMPLETE
4. [Phase 2: Database Schema](#phase-2-database-schema) ✓ COMPLETE
5. [Phase 3: Core Service Modules](#phase-3-core-service-modules)
6. [Phase 4: Data Validation Layer](#phase-4-data-validation-layer)
7. [Phase 5: Industry Knowledge Base](#phase-5-industry-knowledge-base)
8. [Phase 6: API Endpoints](#phase-6-api-endpoints)
9. [Phase 7: User Interface](#phase-7-user-interface)
10. [Phase 8: Testing Strategy](#phase-8-testing-strategy)
11. [Complete Demo Walkthrough](#complete-demo-walkthrough)

---

## **Introduction & System Overview**

### **What Is This Feature?**

Contract Analysis is a smart system that automatically reads contract PDF files and provides:

1. **Summary** - A clear overview of what the contract is about, who is involved, key dates, and money amounts
2. **Clauses** - A list of all the important sections/rules found in the contract
3. **Risk Warnings** - Problems or unusual terms that could cause issues
4. **Smart Suggestions** - How to improve the contract based on industry best practices for that type of contract
5. **Comparison with Standards** - How this contract compares to normal standard contracts

### **Why This Matters**

Instead of having a lawyer manually read a contract (which takes hours), users can upload a PDF and get instant analysis with key insights in seconds. The system is "smart" because it knows what clauses should be in different types of contracts (like service agreements vs. employment contracts).

### **Key Information User Provides**

When uploading a contract, users tell us:

| What | Options | Why We Need It |
|-----|---------|----------------|
| The PDF file | Any contract PDF | This is the document to analyze |
| Contract type | Service Agreement, Employment, Partnership, NDA, Vendor Agreement | Different contracts have different standard clauses |
| Where it applies | India, US, UK | Laws and standards differ by country |
| Which AI model | Mixtral, Llama-70B, Llama-8B | Different models have different speeds and accuracy |

---

## **How The System Works (Step-by-Step)**

Here's what happens when a user uploads a contract:

### **User Perspective (What They See)**

```
1. User clicks "Upload Contract"
2. Selects PDF file + type + jurisdiction + AI model
3. Clicks "Analyze"
4. Sees "Processing..." status
5. Results appear in 4 tabs (Summary, Clauses, Risks, Suggestions)
```

### **Behind The Scenes (What Actually Happens)**

```
Step 1: PDF EXTRACTION
  └─ Read the PDF file
  └─ Extract all text from every page
  └─ Clean up the text (remove junk formatting)
  └─ Store extracted text temporarily

Step 2: AI ANALYSIS (Using Groq LLM)
  └─ Send the text to Groq's AI model
  └─ Ask AI to identify: Summary, Clauses, Risks, Suggestions
  └─ AI reads the contract and creates analysis
  └─ Validate that AI response is properly formatted

Step 3: COMPARISON WITH STANDARDS (Using ChromaDB)
  └─ For each clause the AI found
  └─ Search our database for similar "standard" clauses
  └─ Compare: What's different? What's risky?
  └─ Add these comparisons to the risk section

Step 4: FILTER BY CONTRACT TYPE
  └─ Look up what clauses are standard for this contract type
  └─ Hide irrelevant suggestions
  └─ Highlight critical missing clauses

Step 5: SAVE RESULTS
  └─ Store all analysis in database
  └─ Save 4 separate JSON sections (summary, clauses, risks, suggestions)
  └─ Mark analysis as "complete"

Step 6: RETURN TO USER
  └─ Send analysis to frontend
  └─ Frontend displays 4 tabs with formatted results
```

---

## **Phase 1: Environment Setup** ✓ COMPLETE

### **What This Phase Does**

This phase sets up all the external tools and libraries that the system needs to work. Think of it like getting all the ingredients ready before cooking a meal.

### **Why Each Library?**

| Library | What It Does | Why We Need It |
|---------|--------------|----------------|
| **PyMuPDF (fitz)** | Reads PDF files and extracts text | To read the contract PDFs users upload |
| **Groq** | Connects to the Groq AI service | To use the LLM that analyzes contracts |
| **LangChain** | Framework for building AI applications | To manage how we send data to the AI and get responses back |
| **ChromaDB** | Stores and searches vectors (similar text) | To compare extracted clauses with standard clauses |
| **python-dotenv** | Reads .env files | To keep API keys safe (not hardcoded in code) |
| **Pydantic** | Validates data structure | To ensure JSON response is always in correct format |

### **Detailed Steps**

#### **Step 1: Install Python Packages**

**File to edit:** `/requirements.txt`

**What to do:**
```
Add these new lines to the file:
PyMuPDF==1.26.5
langchain==0.3.0
langchain-groq==0.1.1
langchain-community==0.3.0
groq==0.10.0
chromadb==0.5.3
python-dotenv==1.0.1
pydantic==2.7.0
```

**Then run in terminal:**
```bash
pip install -r requirements.txt
```

**This will:**
- Download all libraries from the internet
- Install them in your Python environment
- Make them available for import in your code

#### **Step 2: Create Environment Configuration File**

**File to create:** `/.env` (in the root folder, same level as manage.py)

**What to put in it:**
```
GROQ_API_KEY=your_actual_groq_api_key_here
DEBUG=True
CONTRACT_ANALYSIS_TIMEOUT=300
CONTRACT_MAX_FILE_SIZE=10485760
```

**Explanation:**
- `GROQ_API_KEY` - Your secret key to use Groq's AI (you'll get this from Groq's website)
- `DEBUG=True` - Tells Django to show detailed error messages during development
- `CONTRACT_ANALYSIS_TIMEOUT=300` - Stop analysis if it takes longer than 5 minutes
- `CONTRACT_MAX_FILE_SIZE=10485760` - Only accept PDF files smaller than 10MB

#### **Step 3: Update Django Configuration**

**File to edit:** `clauseGuardProject/settings.py`

**Add this code after the imports section:**
```python
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ============ GROQ API KEY ============
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

# ============ CONTRACT ANALYSIS SETTINGS ============
CONTRACT_ANALYSIS = {
    'MAX_FILE_SIZE': 10 * 1024 * 1024,      # Maximum file size: 10MB
    'CHUNK_SIZE': 2000,                      # Split text into 2000 character chunks
    'TIMEOUT': 300,                          # 5 minutes timeout for analysis
    'DEFAULT_LLM': 'mixtral-8x7b-32768',    # Default AI model to use
    'GROQ_TEMPERATURE': 0.3,                # How creative/consistent the AI should be (0.3 = very consistent)
    'GROQ_MAX_TOKENS': 2048,                # Maximum length of AI response
}

# ============ CHROMA DATABASE SETTINGS ============
# Create a folder to store vector database files
CHROMA_DATA_DIR = os.path.join(BASE_DIR, 'chroma_data')
os.makedirs(CHROMA_DATA_DIR, exist_ok=True)
```

**What this does:**
- Loads your secret API key from .env file (safe!)
- Sets rules for how large files can be
- Configures the AI model behavior
- Creates a folder for storing the vector database

### **Verification**

After Phase 1, test that everything is installed:

```bash
# Open Python shell
python manage.py shell

# Try importing the libraries
from PyPDF2 import PdfReader  # Should work
from langchain import LLMChain  # Should work
import chromadb  # Should work
from pydantic import BaseModel  # Should work

# If no errors appear, Phase 1 is complete!
```

---

## **Phase 2: Database Schema** ✓ COMPLETE

### **What This Phase Does**

This phase sets up the database tables that will store all contract analysis results. Think of it as creating file cabinets where you'll store important documents.

### **Two Models We Need**

#### **Model 1: ContractAnalysis**

**Purpose:** Store the complete analysis results for a contract

**Fields and What They Store:**

| Field Name | Type | Purpose |
|-----------|------|---------|
| `id` | Auto | Unique ID for this analysis |
| `contract` | ForeignKey | Which contract is this analysis for? (links to Contract model) |
| `summary` | Text | The AI's summary of the contract (stored as JSON text) |
| `clauses` | Text | List of all clauses found (stored as JSON text) |
| `risks` | Text | List of risks and issues (stored as JSON text) |
| `suggestions` | Text | List of improvement suggestions (stored as JSON text) |
| `extraction_status` | Choice | Status: 'pending', 'processing', 'completed', or 'failed' |
| `error_message` | Text | If analysis failed, what went wrong? |
| `processing_time` | Number | How many seconds did analysis take? |
| `analysed_at` | DateTime | When was this analysis created? |

**Why This Design:**
- JSON stored as text is flexible - doesn't require you to know structure in advance
- Status tracking lets you know if analysis is still running
- Processing time helps you optimize performance

#### **Model 2: Clause**

**Purpose:** Store individual clause details if needed

**Fields:**

| Field Name | Type | Purpose |
|-----------|------|---------|
| `id` | Auto | Unique ID for this clause |
| `contract` | ForeignKey | Which contract has this clause? |
| `clause_type` | Text | What type is it? (e.g., "Payment Terms", "Liability") |
| `clause_text` | Text | The actual text of the clause |
| `risk_level` | Choice | 'low', 'medium', or 'high' risk |
| `missing_parts` | Text | What's missing from this clause? |
| `suggestions` | Text | How to improve it? |
| `similarity_score` | Number | How similar to standard clause? (0.0 to 1.0) |
| `created_at` | DateTime | When was this created? |

### **Detailed Steps**

#### **Step 1: Update the Models File**

**File to edit:** `myapp/models.py`

**Add this code (it adds to your existing models):**

```python
from django.db import models
from django.contrib.auth.models import User

class ContractAnalysis(models.Model):
    # Define possible status values
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    # Primary key
    id = models.AutoField(primary_key=True)
    
    # Link to Contract model (each analysis belongs to one contract)
    contract = models.ForeignKey(
        Contract,
        on_delete=models.CASCADE,  # If contract is deleted, delete analysis too
        related_name="analysis",   # Access via: contract.analysis.all()
    )
    
    # The four main analysis results (stored as JSON text)
    summary = models.TextField()
    clauses = models.TextField()
    risks = models.TextField()
    suggestions = models.TextField()
    
    # Status tracking
    extraction_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    error_message = models.TextField(blank=True, null=True)
    processing_time = models.FloatField(null=True, blank=True)
    
    # Timestamps
    analysed_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Analysis for Contract {self.contract.id}"


class Clause(models.Model):
    # Risk level choices
    class RiskLevel(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
    
    # Primary key
    id = models.AutoField(primary_key=True)
    
    # Link to Contract
    contract = models.ForeignKey(
        Contract,
        on_delete=models.CASCADE,
        related_name="clauses",
    )
    
    # Clause information
    clause_type = models.CharField(max_length=100, blank=True)
    clause_text = models.TextField()
    
    # Analysis of the clause
    risk_level = models.CharField(
        max_length=10,
        choices=RiskLevel.choices,
        default=RiskLevel.LOW,
    )
    missing_parts = models.TextField(blank=True, null=True)
    suggestions = models.TextField(blank=True, null=True)
    similarity_score = models.FloatField(default=0.0)
    
    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Clause {self.id} - {self.clause_type} (Contract {self.contract.id})"
```

#### **Step 2: Create Database Migration**

**What's a migration?** A migration is a file that tells Django how to update the database.

**Run this in terminal:**
```bash
python manage.py makemigrations
```

**This will:**
- Create a migration file in `myapp/migrations/` folder
- The file describes the changes you made to models

#### **Step 3: Apply Migration to Database**

**Run this in terminal:**
```bash
python manage.py migrate
```

**This will:**
- Actually update your database with the new tables
- Create `ContractAnalysis` and `Clause` tables in the database

### **Verification**

After Phase 2, verify the tables were created:

```bash
# Open Django shell
python manage.py shell

# Try creating a new analysis
from myapp.models import ContractAnalysis, Clause

# If you can import without errors, Phase 2 is complete!
# You can also check the database file to see the new tables
```

---

## **Phase 3: Core Service Modules**

### **What This Phase Does**

This phase creates the "brain" of the system - the code that:
1. Reads PDFs
2. Talks to the AI
3. Searches for similar clauses
4. Processes the results

Think of it as building the machinery that does the actual analysis work.

### **Module 1: PDF Processor**

**File:** `myapp/services/contract_processor.py`

**What it does:** Opens PDF files and extracts all text

**Simple explanation:**
- Takes a PDF file path
- Opens it using PyMuPDF library
- Reads text from every page
- Returns all the text as one big string
- If anything goes wrong, gives a helpful error message

**Key methods to create:**

```python
# Method 1: Extract text from PDF
extract_text_from_pdf(file_path: str) -> str
  Input: Path to PDF file on the computer
  Process: Open PDF, read all pages, combine text
  Output: All text from the PDF
  Errors: If file doesn't exist or isn't a valid PDF

# Method 2: Validate PDF
validate_pdf(file_path: str) -> bool
  Input: Path to PDF file
  Process: Try to open it, check if it has pages
  Output: True if valid, False if invalid
  Use: Before extracting, make sure it's a real PDF
```

### **Module 2: Vector Database Manager**

**File:** `myapp/services/chroma_manager.py`

**What it does:** Manages the ChromaDB vector database

**Simple explanation:**
- ChromaDB stores "standard" clauses as vectors (mathematical representations)
- When you give it a clause, it can find similar standard clauses
- Think of it like a search engine for contract language

**Key methods to create:**

```python
# Method 1: Get or create a collection
get_or_create_collection(collection_name: str) -> Collection
  Input: Name like "service_agreement_india"
  Process: Check if collection exists, create if not
  Output: The collection object to work with

# Method 2: Add standard clauses to database
add_standard_clauses(collection_name: str, clauses: list) -> None
  Input: Collection name and list of clause dictionaries
  Process: Add each clause to ChromaDB with metadata
  Output: None (just saves to database)
  Example: Add 50 standard "Payment Terms" clauses

# Method 3: Search for similar clauses
search_similar_clauses(collection_name: str, query_text: str, top_k: int) -> dict
  Input: Collection name, clause text to search for, how many results
  Process: Find similar clauses in database
  Output: List of similar standard clauses with similarity scores
  Example: Find 3 standard clauses most similar to extracted clause
```

### **Module 3: Prompt Templates**

**File:** `myapp/services/prompts.py`

**What it does:** Contains the instructions we send to the AI

**Simple explanation:**
- The AI needs clear, detailed instructions to analyze contracts
- We store these instructions as templates
- We fill in the contract text and contract type into the template
- Then send it to Groq AI

**Prompts to create:**

```
1. SUMMARY PROMPT
   "Analyze this {contract_type} contract and provide:
   - Overview
   - Parties involved
   - Duration
   - Key obligations
   - Financial terms"

2. CLAUSE EXTRACTION PROMPT
   "Find all distinct clauses in this contract.
   For each clause, provide:
   - Clause type/name
   - Full clause text
   - Brief description"

3. RISK ANALYSIS PROMPT
   "Identify risks and issues in this {contract_type} contract:
   - Missing standard clauses
   - Unusual or dangerous terms
   - Gaps in protection
   - Non-standard language"

4. SUGGESTIONS PROMPT
   "Based on industry standards for {contract_type} in {jurisdiction},
   suggest improvements:
   - Missing clauses
   - Better wording
   - Added protections
   - Clarifications needed"
```

### **Module 4: Contract Type Mapping**

**File:** `myapp/services/contract_clause_mapping.py`

**What it does:** Defines what clauses are standard for each contract type

**Simple explanation:**
- A Service Agreement needs different clauses than an Employment Contract
- This module lists all standard clauses for each type
- Used to filter suggestions (don't suggest SLA for employment contract)

**Data structure:**

```python
CONTRACT_TYPE_MAPPING = {
    'SERVICE_AGREEMENT': {
        'critical_clauses': [
            'Scope of Services',
            'Payment Terms',
            'Term and Termination',
            'Confidentiality',
            'Liability'
        ],
        'important_clauses': [
            'SLA',
            'Intellectual Property',
            'Insurance',
            'Dispute Resolution'
        ],
        'optional_clauses': [
            'Renewal Terms',
            'Amendment Procedures'
        ]
    },
    'EMPLOYMENT_CONTRACT': {
        'critical_clauses': [
            'Job Title and Responsibilities',
            'Compensation',
            'Benefits',
            'Termination',
            'Confidentiality'
        ],
        # ... etc
    }
}
```

**Key methods to create:**

```python
# Get all standard clauses for a type
get_standard_clauses_for_type(contract_type: str) -> list

# Get only critical clauses for a type
get_critical_clauses_for_type(contract_type: str) -> list

# Check if a clause is standard for a type
is_clause_standard_for_type(clause_type: str, contract_type: str) -> bool
```

---

## **Phase 4: Data Validation Layer**

### **What This Phase Does**

This phase creates a "quality control" system using Pydantic. Instead of letting messy JSON from the AI go straight to the frontend, we validate it first.

**Why it matters:** 
- AI sometimes makes mistakes or returns data in wrong format
- Pydantic automatically checks the format
- If format is wrong, it either fixes it or returns a safe empty response
- Frontend always gets predictable JSON structure

### **What We Validate**

#### **1. Summary Output**

```python
# What the frontend expects:
{
  "summary": "Long text explaining the contract",
  "contract_type": "Service Agreement",
  "parties": ["Company A", "Company B"],
  "duration": "2 years",
  "key_obligations": ["Item 1", "Item 2", "Item 3"],
  "financial_terms": "₹500,000/month",
  "jurisdiction": "India"
}
```

#### **2. Clauses Output**

```python
# What the frontend expects:
{
  "clauses": [
    {
      "id": 1,
      "type": "Payment Terms",
      "text": "The full text of the clause..."
    },
    {
      "id": 2,
      "type": "Confidentiality",
      "text": "The full text of the clause..."
    }
  ],
  "total_clauses": 2
}
```

#### **3. Risks Output**

```python
# What the frontend expects:
{
  "risks": [
    {
      "id": 1,
      "clause_type": "Payment Terms",
      "risk_level": "HIGH",
      "issue": "Payment due in 15 days",
      "description": "This is unusually short...",
      "impact": "Could damage vendor relationships..."
    }
  ],
  "missing_clauses": ["SLA", "Insurance"],
  "total_risks": 1,
  "total_missing": 2
}
```

#### **4. Suggestions Output**

```python
# What the frontend expects:
{
  "suggestions": [
    {
      "id": 1,
      "priority": "HIGH",
      "category": "Missing Clause",
      "current_state": "SLA is not mentioned",
      "suggested_text": "The Service Provider warrants...",
      "business_impact": "Protects your service quality..."
    }
  ],
  "total_suggestions": 1
}
```

### **How to Implement (Simple Explanation)**

**File:** `myapp/services/schemas.py`

Create classes that define the expected structure:

```python
from pydantic import BaseModel, Field
from typing import List, Optional

# For individual items
class ClauseItem(BaseModel):
    id: int
    type: str
    text: str

# For the complete clauses response
class ClausesOutput(BaseModel):
    clauses: List[ClauseItem] = []
    total_clauses: int = 0

# For risk items
class RiskItem(BaseModel):
    id: int
    clause_type: str
    risk_level: str  # "LOW", "MEDIUM", "HIGH"
    issue: str
    description: str
    impact: str

# For complete risks response
class RisksOutput(BaseModel):
    risks: List[RiskItem] = []
    missing_clauses: List[str] = []
    total_risks: int = 0
    total_missing: int = 0
```

**Benefits:**

✅ **Automatic validation** - If AI returns wrong format, Pydantic catches it  
✅ **Consistent format** - Frontend always knows what to expect  
✅ **Type safety** - No surprise null values or missing fields  
✅ **Easy testing** - Easy to write tests for each schema  
✅ **Documentation** - The schema IS the documentation

---

## **Phase 5: Industry Knowledge Base**

### **What This Phase Does**

This phase sets up a database of "standard" clauses for different contract types. Think of it like a library of best practices.

**Why it matters:**
- Different contract types have different standard clauses
- We can compare extracted clauses against these standards
- We can highlight if something important is missing

### **Standard Clauses by Contract Type**

#### **Service Agreement - India**

**Critical Clauses (must have):**
- Scope of Services
- Payment Terms
- Term and Termination
- Confidentiality
- Intellectual Property
- Liability Limitation

**Important Clauses (should have):**
- Service Level Agreement (SLA)
- Insurance Requirements
- Dispute Resolution
- Amendment Procedures

**Optional Clauses (nice to have):**
- Renewal Terms
- Data Protection
- Compliance

#### **Employment Contract - India**

**Critical Clauses:**
- Job Title & Responsibilities
- Compensation & Benefits
- Working Hours
- Termination Clause
- Confidentiality
- Non-Compete

**Important Clauses:**
- Leave Policy
- Performance Management
- Dispute Resolution
- Tax Compliance

#### **NDA (Non-Disclosure Agreement)**

**Critical Clauses:**
- Definition of Confidential Information
- Permitted Disclosures
- Term of Confidentiality
- Return of Information
- Consequences of Breach
- Exceptions (Public Information, etc.)

### **How to Store and Use**

**File:** `myapp/data/standard_clauses.json`

```json
{
  "SERVICE_AGREEMENT_INDIA": {
    "critical_clauses": [
      {
        "type": "Scope of Services",
        "text": "The Service Provider shall provide the following services: ...",
        "recommendations": "Should be specific and measurable"
      }
    ],
    "important_clauses": [...]
  },
  "EMPLOYMENT_INDIA": {...},
  "NDA_INDIA": {...}
}
```

**File:** `myapp/services/contract_clause_mapping.py`

This file:
1. Loads the standard clauses
2. Provides helper functions to look them up
3. Helps identify missing clauses in the contract

**Key functions:**

```python
# Get all standard clauses for a contract type
get_standard_clauses_for_type(contract_type: str, jurisdiction: str) -> list

# Get critical clauses only
get_critical_clauses_for_type(contract_type: str, jurisdiction: str) -> list

# Check if a clause type exists in standards
is_clause_standard(clause_type: str, contract_type: str, jurisdiction: str) -> bool

# Find missing critical clauses
find_missing_clauses(found_clauses: list, contract_type: str, jurisdiction: str) -> list
```

---

## **Phase 6: API Endpoints**

### **What This Phase Does**

This phase creates the server endpoints (URLs) that handle contract analysis requests and return results.

### **Endpoints to Create**

#### **Endpoint 1: Upload & Analyze**

```
URL: /upload-contract/
Method: POST
Purpose: User uploads a PDF, system starts analysis

Input (form data):
  - contract_file: PDF file
  - contract_type: String ("SERVICE_AGREEMENT", "EMPLOYMENT", etc.)
  - jurisdiction: String ("INDIA", "US", "UK")
  - llm_model: String ("mixtral-8x7b-32768", "llama-70b", etc.)

Output (JSON):
{
  "status": "success",
  "contract_id": 1,
  "analysis_id": 1,
  "message": "Contract uploaded and analysis started"
}

Process:
1. Save the PDF file to media folder
2. Create Contract database record
3. Create empty ContractAnalysis record
4. Call the analysis logic (Phase 3-5)
5. Return analysis_id to frontend
```

#### **Endpoint 2: Get Analysis Results**

```
URL: /analysis/<analysis_id>/
Method: GET
Purpose: Frontend polls this to get results and check status

Output (JSON):
{
  "status": "success",
  "data": {
    "status": "completed",  // or "processing", "pending", "failed"
    "summary": {...},
    "clauses": {...},
    "risks": {...},
    "suggestions": {...},
    "processing_time": 45.3
  }
}

Process:
1. Check user has permission to see this analysis
2. Retrieve ContractAnalysis from database
3. Parse the 4 JSON fields
4. Return structured data
```

#### **Endpoint 3: Get Contract List**

```
URL: /contracts/
Method: GET
Purpose: Show user's uploaded contracts

Output (JSON):
{
  "contracts": [
    {
      "id": 1,
      "name": "Service Agreement with TechCorp",
      "type": "SERVICE_AGREEMENT",
      "uploaded_at": "2026-01-10",
      "analysis_status": "completed",
      "analysis_id": 1
    }
  ]
}
```

---

## **Phase 7: User Interface**

### **What This Phase Does**

This phase creates the web interface that users see and interact with.

### **User Experience Flow**

```
1. User opens website
   ↓
2. User clicks "Upload Contract"
   ↓
3. Modal/Page shows upload form:
   - File picker (PDF)
   - Contract type dropdown
   - Jurisdiction dropdown
   - LLM model dropdown
   ↓
4. User clicks "Upload & Analyze"
   ↓
5. Show "Processing..." with animated spinner
   ↓
6. JavaScript polls server every 2 seconds: "Is analysis done yet?"
   ↓
7. When analysis is done:
   - Hide loading spinner
   - Show 4 tabs: Summary | Clauses | Risks | Suggestions
   ↓
8. User clicks tabs to see different sections
   ↓
9. User can download results as PDF or email them
```

### **Frontend Components**

#### **Upload Form**

Should have:
- File upload input (accepts only PDF)
- Contract type select dropdown
- Jurisdiction select dropdown
- LLM model select dropdown
- Submit button
- Error message display area

#### **Results Display**

Structure:
```
[ SUMMARY ] [ CLAUSES ] [ RISKS ] [ SUGGESTIONS ]  [Download]

┌─────────────────────────────────────────────────┐
│ SUMMARY TAB CONTENT                             │
│                                                 │
│ Contract Type: Service Agreement                │
│ Parties: Company A, Company B                   │
│ Duration: 2 years                               │
│ Jurisdiction: India                             │
│ Financial Terms: ₹500,000/month                 │
│ ...                                             │
└─────────────────────────────────────────────────┘
```

#### **Clauses Tab**

Shows list of all found clauses with:
- Clause type/name
- Full clause text
- Risk level badge (LOW/MEDIUM/HIGH)

#### **Risks Tab**

Shows each risk with:
- 🔴 DANGER icon for HIGH risk
- 🟡 WARNING icon for MEDIUM risk
- 🟢 INFO icon for LOW risk
- Issue title
- Detailed description
- Potential impact
- Suggested fix

#### **Suggestions Tab**

Shows improvement suggestions with:
- 💡 Icon
- Priority level (HIGH/MEDIUM/LOW)
- Category (Missing Clause, Wording, Protection, etc.)
- What's current
- What's suggested
- Business impact

---

## **Phase 8: Testing Strategy**

### **Unit Tests** (Test individual functions)

```
Test 1: PDF Extraction
  - Upload a real PDF
  - Extract text
  - Verify text contains expected content

Test 2: Data Validation
  - Create valid ClausesOutput
  - Create invalid data
  - Verify Pydantic rejects invalid
  - Verify valid is accepted

Test 3: Authorization
  - Create analysis for User A
  - Try to access as User B
  - Verify 403 Forbidden error

Test 4: Missing Clause Detection
  - Give employment contract without "Termination" clause
  - Run analysis
  - Verify "Termination" in missing clauses
```

### **Integration Tests** (Test full workflow)

```
Test 1: Complete workflow
  - User A logs in
  - Uploads Service Agreement PDF
  - Waits for analysis
  - Retrieves results
  - Verifies all 4 tabs have data
  - Deletes contract
  - Verifies analysis also deleted

Test 2: Error handling
  - Upload non-PDF file
  - Verify error message
  - Upload PDF with no text
  - Verify graceful handling
```

### **Manual Testing Checklist**

- [ ] Can upload PDF successfully
- [ ] PDF text extraction works
- [ ] Analysis completes without errors
- [ ] Summary tab shows contract overview
- [ ] Clauses tab shows all found clauses
- [ ] Risks tab shows risk with correct severity
- [ ] Suggestions tab shows relevant suggestions only
- [ ] User A can't see User B's analysis
- [ ] Error messages are helpful
- [ ] Processing time is shown
- [ ] Download/email results work

---

## **Complete Demo Walkthrough**

### **Demo Scenario: Analyzing a Service Agreement**

**Setup:**
- A small tech company has a service agreement with a cloud provider
- They want to check if the contract is fair and complete
- They've uploaded the PDF to ClauseGuard

**Step 1: Upload**

User sees this form:
```
┌─────────────────────────────────┐
│ Upload Contract for Analysis    │
├─────────────────────────────────┤
│                                 │
│ PDF File: [Choose File]         │
│ (service_agreement.pdf)         │
│                                 │
│ Contract Type:                  │
│ ▼ Service Agreement             │
│                                 │
│ Jurisdiction:                   │
│ ▼ India                         │
│                                 │
│ AI Model:                       │
│ ▼ Mixtral-8x7b-32768           │
│                                 │
│ [ANALYZE CONTRACT]              │
│                                 │
└─────────────────────────────────┘
```

**Step 2: Behind The Scenes**

1. **PDF Extraction** (PyMuPDF)
   - Opens service_agreement.pdf
   - Reads all 8 pages
   - Extracts ~15,000 words
   - Cleans up formatting

2. **AI Analysis** (Groq LLM)
   - Sends extracted text to Groq
   - Asks: "What's a summary of this service agreement?"
   - AI responds with structured JSON
   - Saves to database

3. **Clause Comparison** (ChromaDB)
   - Found clause: "Payment due within 15 days"
   - Searches ChromaDB for similar standard clauses
   - Finds: Standard is 30-45 days in India
   - Marks as a RISK: "Aggressive payment terms"

4. **Validation** (Pydantic)
   - Checks if AI response has all required fields
   - Verifies data types match schema
   - Converts to safe JSON structure

**Step 3: Frontend Shows Loading**

```
┌──────────────────────────────────┐
│                                  │
│       ⏳ ANALYZING...             │
│                                  │
│   Processing your contract      │
│   This usually takes 30-60 secs │
│                                  │
│   [████████░░] 65%               │
│                                  │
└──────────────────────────────────┘
```

**Step 4: Results Appear**

#### **SUMMARY TAB** (Default view)

```
┌────────────────────────────────────────┐
│ [SUMMARY] [CLAUSES] [RISKS] [SUGGESTI…│
├────────────────────────────────────────┤
│                                        │
│ CONTRACT OVERVIEW                      │
│                                        │
│ Type: Service Agreement                │
│ Parties:                               │
│  • CloudServices Inc.                  │
│  • TechStart Solutions                 │
│                                        │
│ Duration: 2 years                      │
│ Start Date: January 1, 2026            │
│ End Date: December 31, 2027            │
│                                        │
│ Financial Terms:                       │
│ • Base Fee: ₹500,000 per month         │
│ • Setup Cost: ₹50,000 (one-time)       │
│ • Payment Terms: Due within 15 days    │
│                                        │
│ Jurisdiction: Mumbai, India            │
│                                        │
│ KEY OBLIGATIONS:                       │
│ 1. Provide 24/7 cloud infrastructure   │
│ 2. Maintain 99.9% uptime               │
│ 3. Daily backups of customer data      │
│ 4. Response time within 1 hour for     │
│    critical issues                     │
│                                        │
│ FULL SUMMARY:                          │
│ This is a comprehensive service        │
│ agreement between CloudServices Inc.   │
│ and TechStart Solutions for providing  │
│ managed cloud infrastructure services. │
│ The agreement outlines the scope of    │
│ services, payment terms, liability     │
│ limits, and dispute resolution         │
│ procedures...                          │
│                                        │
└────────────────────────────────────────┘
```

#### **CLAUSES TAB**

```
┌────────────────────────────────────────┐
│ [SUMMARY] [CLAUSES] [RISKS] [SUGGESTI…│
├────────────────────────────────────────┤
│                                        │
│ FOUND 12 CLAUSES                       │
│                                        │
│ ▼ SCOPE OF SERVICES                    │
│   Risk Level: LOW ✓                    │
│   Text: "The Service Provider shall    │
│   provide cloud infrastructure         │
│   including servers, storage,          │
│   networking, and backup services..."  │
│                                        │
│ ▼ PAYMENT TERMS                        │
│   Risk Level: HIGH ⚠️                  │
│   Text: "Client shall pay ₹500,000     │
│   per month, due within 15 days of     │
│   invoice date..."                     │
│                                        │
│ ▼ CONFIDENTIALITY                      │
│   Risk Level: LOW ✓                    │
│   Text: "Each party agrees to keep     │
│   confidential all proprietary         │
│   information..."                      │
│                                        │
│ ▼ LIABILITY LIMITATION                 │
│   Risk Level: MEDIUM ⚠️                │
│   Text: "In no event shall either      │
│   party's total liability exceed       │
│   one month's service fee..."          │
│                                        │
│ [... 8 more clauses ...]               │
│                                        │
└────────────────────────────────────────┘
```

#### **RISKS TAB**

```
┌────────────────────────────────────────┐
│ [SUMMARY] [CLAUSES] [RISKS] [SUGGESTI…│
├────────────────────────────────────────┤
│                                        │
│ IDENTIFIED 3 RISKS & 2 MISSING         │
│                                        │
│ 🔴 HIGH RISK                           │
│ ─────────────────────────────────────  │
│ Issue: Aggressive Payment Terms        │
│                                        │
│ Problem: Payment due within 15 days    │
│ is unusually short for India           │
│                                        │
│ Description: Standard practice in      │
│ India for B2B services is 30-45 days   │
│ payment terms. 15 days creates cash    │
│ flow pressure.                         │
│                                        │
│ Business Impact: Could strain your     │
│ cash flow, especially if you have      │
│ slow-paying customers.                 │
│                                        │
│ ────────────────────────────────────── │
│                                        │
│ 🟡 MEDIUM RISK                         │
│ ─────────────────────────────────────  │
│ Issue: Low Liability Cap (1 month)     │
│                                        │
│ Problem: If service provider causes    │
│ damage, you can only recover 1 month   │
│ of fees. This is very low.             │
│                                        │
│ Description: For critical services,    │
│ liability should be 6-12 months or     │
│ more, depending on service impact.     │
│                                        │
│ Business Impact: If service goes down  │
│ for a week and costs you ₹10 lakhs,    │
│ you can only claim ₹5 lakhs.           │
│                                        │
│ ────────────────────────────────────── │
│                                        │
│ 🟡 MEDIUM RISK                         │
│ ─────────────────────────────────────  │
│ Issue: No SLA Definition                │
│                                        │
│ Problem: Contract mentions 99.9%       │
│ uptime but doesn't define what         │
│ counts as "downtime"                   │
│                                        │
│ Business Impact: Disputes likely if    │
│ service has issues                     │
│                                        │
│ ────────────────────────────────────── │
│                                        │
│ ❌ MISSING CLAUSES (2)                 │
│                                        │
│ 1. Data Protection/GDPR Compliance     │
│    Standard for India: Should have     │
│    detailed data security measures     │
│                                        │
│ 2. Insurance Requirements              │
│    Standard for India: Should require  │
│    professional indemnity insurance    │
│                                        │
└────────────────────────────────────────┘
```

#### **SUGGESTIONS TAB**

```
┌────────────────────────────────────────┐
│ [SUMMARY] [CLAUSES] [RISKS] [SUGGESTI…│
├────────────────────────────────────────┤
│                                        │
│ 4 IMPROVEMENT SUGGESTIONS               │
│                                        │
│ 💡 PRIORITY: HIGH                      │
│ ─────────────────────────────────────  │
│ Category: Negotiate Payment Terms      │
│                                        │
│ Current: "Payment due within 15 days"  │
│                                        │
│ Suggestion: Change to:                 │
│ "Payment due within 30 days of         │
│ invoice date"                          │
│                                        │
│ Business Impact: Improves your cash    │
│ flow and aligns with Indian standards  │
│                                        │
│ ────────────────────────────────────── │
│                                        │
│ 💡 PRIORITY: HIGH                      │
│ ─────────────────────────────────────  │
│ Category: Missing Critical Clause      │
│ (Data Protection)                      │
│                                        │
│ Current State: Not mentioned           │
│                                        │
│ Suggested Addition:                    │
│                                        │
│ "DATA PROTECTION AND SECURITY:         │
│  The Service Provider shall:            │
│  1. Encrypt all customer data at rest  │
│     and in transit using AES-256       │
│  2. Perform daily backups              │
│  3. Store backups in a separate        │
│     geographic location                │
│  4. Maintain PCI DSS compliance if     │
│     handling payment data              │
│  5. Notify Client within 24 hours of   │
│     any security breach"               │
│                                        │
│ Business Impact: Protects your         │
│ customer data and reduces legal risk   │
│                                        │
│ ────────────────────────────────────── │
│                                        │
│ 💡 PRIORITY: MEDIUM                    │
│ ─────────────────────────────────────  │
│ Category: Clarify SLA Definition       │
│                                        │
│ Current: Mentions 99.9% uptime but     │
│ doesn't define downtime calculation    │
│                                        │
│ Suggested Addition:                    │
│                                        │
│ "SERVICE LEVEL AGREEMENT (SLA):        │
│  Uptime Guarantee: 99.9% measured on   │
│  a monthly basis                       │
│                                        │
│  Downtime Definition: Counted when:    │
│  - Service is completely unavailable   │
│  - OR response time exceeds 10 secs    │
│  - Scheduled maintenance excluded      │
│                                        │
│  Credits for breaches:                 │
│  - 95-99.8% uptime: 5% monthly fee     │
│  - 90-95% uptime: 10% monthly fee      │
│  - Below 90%: 25% monthly fee"         │
│                                        │
│ Business Impact: Protects you from     │
│ service quality issues                 │
│                                        │
│ ────────────────────────────────────── │
│                                        │
│ 💡 PRIORITY: MEDIUM                    │
│ ─────────────────────────────────────  │
│ Category: Increase Liability Cap       │
│                                        │
│ Current: Limited to 1 month of fees    │
│                                        │
│ Suggestion: Change to:                 │
│ "Liability shall be capped at the      │
│ higher of: (a) 12 months of service    │
│ fees, or (b) actual documented loss,   │
│ whichever is applicable for the        │
│ claimed damages"                       │
│                                        │
│ Business Impact: Better protection if  │
│ service failure causes major loss      │
│                                        │
│ ────────────────────────────────────── │
│                                        │
│ [DOWNLOAD AS PDF] [EMAIL RESULTS]     │
│ [PRINT]           [EXPORT TO EXCEL]   │
│                                        │
└────────────────────────────────────────┘
```

**Step 5: User Actions**

User can now:
- Read each section
- Download as PDF report
- Email results to stakeholders
- Print for review
- Share with legal team
- Use to negotiate better terms

### **Technology Stack Used in Demo**

| Component | Technology | Role |
|-----------|-----------|------|
| **Frontend** | HTML/CSS/JavaScript | User interface - what user sees |
| **File Upload** | Django FileField | Store PDF on server |
| **PDF Reading** | PyMuPDF (fitz) | Extract text from PDF |
| **AI Analysis** | Groq API + Mixtral | Analyze text and identify clauses/risks |
| **Framework** | LangChain | Manage AI interactions |
| **Vector DB** | ChromaDB | Compare with standard clauses |
| **Validation** | Pydantic | Ensure JSON structure is correct |
| **Storage** | SQLite/Django ORM | Save results to database |
| **Backend** | Django + Python | Server logic |
| **Polling** | JavaScript fetch() | Check if analysis is done |

### **Data Flow Diagram**

```
USER
  ↓
[Upload PDF] → Django View
  ↓
  Save to disk + Create DB record
  ↓
[PDF Processor]
  ↓ extracts text
  ↓
[Groq LLM] (via LangChain)
  ↓ analyzes text
  ↓
[ChromaDB Manager]
  ↓ finds similar clauses
  ↓
[Pydantic Schemas]
  ↓ validates structure
  ↓
[ContractAnalysis Model]
  ↓ saves to database
  ↓
[JSON Response]
  ↓
FRONTEND displays in 4 tabs
```

### **Processing Timeline**

```
0:00 User clicks "Analyze"
  ↓
0:05 PDF text extraction complete (15,000 words)
  ↓
0:35 LLM analysis complete (30 seconds via Groq)
  ↓
0:40 ChromaDB vector search complete (5 seconds)
  ↓
0:42 Validation and data processing (2 seconds)
  ↓
0:45 Results saved to database (1 second)
  ↓
0:47 Frontend fetches and displays results

Total: ~47 seconds from upload to results
```

---

## **Status Summary**

✅ **Phase 1** - Environment setup (COMPLETE)  
✅ **Phase 2** - Database schema (COMPLETE)  
⏳ **Phase 3-7** - Ready for implementation  
⏳ **Phase 8** - Testing ready  

**Next Steps:**
1. Verify Phase 1 & 2 are correctly implemented
2. Create Phase 3 service modules
3. Implement Phase 4 validation schemas
4. Build Phase 5-7 in order
5. Test with real contract PDF
6. Deploy to production

---

**Document Version:** 2.0  
**Last Updated:** January 11, 2026  
**Status:** Ready for Implementation
