
## **Phase 5 Implementation Plan**

### **Overview**
Phase 5 creates a database of standard clauses for different contract types (Service Agreement, Employment, NDA, etc.) by jurisdiction. This enables the system to identify missing or non-standard clauses in uploaded contracts.

### **Key Components**

#### **1. Standard Clauses Data File**
**File to create:** `myapp/data/standard_clauses.json`
- Structured JSON containing standard clauses for each contract type × jurisdiction combination
- Three categories per type: critical, important, and optional clauses
- Each clause includes: type, recommended text, and recommendations

**Contract Types to support:**
- SERVICE_AGREEMENT
- EMPLOYMENT_CONTRACT
- NDA (Non-Disclosure Agreement)
- PARTNERSHIP_AGREEMENT (implied)
- VENDOR_AGREEMENT (implied)

**Jurisdictions:**
- INDIA
- US
- UK

#### **2. Contract Clause Mapping Service**
**File to create/enhance:** `myapp/services/contract_clause_mapping.py`
- Load standard clauses from JSON file
- Provide utility functions for clause lookups

**Key Functions to implement:**
```
- get_standard_clauses_for_type(contract_type: str, jurisdiction: str) -> list
- get_critical_clauses_for_type(contract_type: str, jurisdiction: str) -> list
- get_important_clauses_for_type(contract_type: str, jurisdiction: str) -> list
- is_clause_standard(clause_type: str, contract_type: str, jurisdiction: str) -> bool
- find_missing_clauses(found_clauses: list, contract_type: str, jurisdiction: str) -> list
```

### **Implementation Tasks**

#### **Task 1: Create Data Directory**
- Create folder: `myapp/data/`
- Create `__init__.py` inside it

#### **Task 2: Create Standard Clauses JSON**
Build comprehensive JSON with:

**For SERVICE_AGREEMENT:**
- Critical clauses: Scope of Services, Payment Terms, Term & Termination, Confidentiality, IP Rights, Liability Limitation
- Important clauses: SLA, Insurance, Dispute Resolution, Amendment Procedures
- Optional clauses: Renewal Terms, Data Protection, Compliance

**For EMPLOYMENT_CONTRACT:**
- Critical clauses: Job Title & Responsibilities, Compensation & Benefits, Working Hours, Termination, Confidentiality, Non-Compete
- Important clauses: Leave Policy, Performance Management, Dispute Resolution, Tax Compliance
- Optional clauses: Relocation, Training, Stock Options

**For NDA:**
- Critical clauses: Definition of Confidential Info, Permitted Disclosures, Term, Return of Info, Consequences of Breach, Exceptions

**For PARTNERSHIP_AGREEMENT:**
- Critical clauses: Capital Contribution, Profit/Loss Distribution, Decision Making, Dispute Resolution, Exit Clause
- Important clauses: Governance Structure, Member Duties, Non-Compete, Confidentiality
- Optional clauses: Expansion, Refinancing, Acquisition

**For VENDOR_AGREEMENT:**
- Critical clauses: Product/Service Description, Pricing, Payment Terms, SLA, Warranties, Liability
- Important clauses: IP Rights, Confidentiality, Insurance, Dispute Resolution
- Optional clauses: Volume Discounts, Renewal, Termination Notice

#### **Task 3: Implement Contract Clause Mapping Module**
Create Python class/functions to:
- Load JSON on module import
- Cache in memory for performance
- Provide lookup methods
- Handle missing jurisdiction/type gracefully

#### **Task 4: Integration with Existing Code**
- Import in the services that need it (for risk analysis and suggestions)
- Use in Phase 6 endpoints to identify missing clauses
- Use in Phase 4 validation to enhance risk detection

### **Deliverables**

1. ✅ `myapp/data/__init__.py` - Empty init file
2. ✅ `myapp/data/standard_clauses.json` - Comprehensive standard clauses database
3. ✅ `myapp/services/contract_clause_mapping.py` - Enhanced/new module with utility functions
4. ✅ Update existing imports in other services if needed

### **Estimated Effort**
- Data creation (JSON): ~30-45 minutes
- Mapping module implementation: ~20-30 minutes
- Integration/testing: ~15-20 minutes
- **Total: ~1-1.5 hours**

### **Dependencies**
- Phase 1 ✅ (environment setup)
- Phase 2 ✅ (database schema)
- Phase 3 (core services - partially, not all needed for this phase)

### **Testing Approach**
- Unit tests for each mapping function
- Test missing clause detection
- Test clause categorization by priority
- Test jurisdiction-specific variations

