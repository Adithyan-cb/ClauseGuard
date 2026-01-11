# ClauseGuard - Intelligent Contract Analysis System

## 📋 Project Description

ClauseGuard is an AI-powered contract analysis system that automatically reads and analyzes PDF contracts. Instead of manually reviewing lengthy documents, users can upload a contract and get instant analysis with key insights, risk warnings, and improvement suggestions in seconds.

The system uses **Groq LLM** for intelligent contract analysis and **ChromaDB** for comparing contracts against industry standards.

---

## 🛠️ Tech Stack

- **Backend:** Django 5.2.5, Django REST Framework 3.16.1
- **Database:** MySQL
- **AI/ML:** 
  - Groq LLM (Mixtral, Llama-70B, Llama-8B models)
  - LangChain 0.3.0
  - ChromaDB 0.5.3 (Vector database for RAG)
- **PDF Processing:** PyMuPDF 1.26.5
- **Validation:** Pydantic 2.7.0
- **Frontend:** HTML, CSS, Bootstrap

---

## 👥 Modules

### **User Module**
Users can:
- Register and login securely
- Upload contract PDF files
- Select contract type (Service Agreement, Employment, Partnership, NDA, Vendor Agreement)
- Choose jurisdiction (India, US, UK)
- Pick preferred AI model for analysis
- View detailed analysis results in 4 tabs:
  - **Summary:** Overview of contract details, parties involved, key dates, amounts
  - **Clauses:** List of all identified clauses and important sections
  - **Risks:** Problems and unusual terms flagged as potential issues
  - **Suggestions:** Improvements based on industry best practices

### **Admin Module**
Administrators can:
- view contracts uploaded by the user
- view users
- view complaints
- view feedback 

---

## 📊 How It Works (Example)

### **Scenario:** Cloud Service Agreement Contract

**Sample Contract Content:**
```
SERVICE AGREEMENT

This Agreement is entered into on January 1, 2026 between:

PROVIDER: TechCloud Solutions Pvt Ltd
CLIENT: Global Enterprises Inc
SERVICE: Cloud Hosting and Support
DURATION: 2 years from effective date
ANNUAL COST: $120,000

KEY TERMS:
- 99.5% uptime guarantee
- 24/7 technical support included
- Data backup daily
- Maximum liability: $500,000
- Intellectual property remains with provider
```

**User Action:**
```
1. Login to ClauseGuard dashboard
2. Click "Upload Contract"
3. Select contract file: cloud_service_agreement.pdf
4. Fill form:
   - Contract Type: "Service Agreement"
   - Jurisdiction: "India"
   - AI Model: "Mixtral"
5. Click "Analyze" button
6. See "Processing..." status with progress
```

**Behind The Scenes (Step-by-Step):**
```
Step 1: PDF Extraction & Cleaning
  → PyMuPDF reads all 15 pages of PDF
  → Extracts 45,000+ characters of text
  → Removes headers, footers, page numbers
  → Normalizes whitespace and formatting

Step 2: AI Analysis with Groq LLM
  → LangChain sends extracted text to Groq's Mixtral model
  → AI analyzes and returns:
     * Summary: parties, dates, amounts, key obligations
     * Clauses: identifies 12 distinct clauses
     * Risks: flags 5 potential issues
     * Suggestions: recommends 4 improvements

Step 3: Industry Standard Comparison
  → ChromaDB searches knowledge base for "Service Agreement" standards
  → Compares found clauses against standard templates
  → Calculates match percentage for each clause
  → Identifies missing critical clauses

Step 4: Data Validation & Storage
  → Pydantic validates all JSON responses
  → Converts results to database format
  → Stores in ContractAnalysis model with status "Completed"
  → Calculates processing time: 12.3 seconds

Step 5: Display Results to User
  → Returns 4 tabs with analysis results
  → Marks status as "Ready for Review"
```

**Analysis Results User Receives:**

**📌 TAB 1: SUMMARY**
```
Contract Overview:
├── Parties:
│   ├── Provider: TechCloud Solutions Pvt Ltd
│   ├── Client: Global Enterprises Inc
│   └── Contact: agreements@techcloud.com
├── Financial Terms:
│   ├── Total Value: $240,000 (2-year contract)
│   ├── Annual Payment: $120,000
│   └── Payment Terms: Monthly invoicing on 1st of month
├── Duration:
│   ├── Start Date: January 1, 2026
│   ├── End Date: December 31, 2027
│   └── Auto-renewal: 1 year unless 90-day notice given
└── Key Obligations:
    ├── Provider: Maintain 99.5% uptime, 24/7 support, daily backups
    └── Client: Pay invoices within 30 days, maintain security protocols
```

**⚖️ TAB 2: CLAUSES FOUND (12 Total)**
```
1. Service Scope & Description ✓
   → Cloud hosting, data storage, technical support included
   
2. Service Levels & Uptime ✓
   → 99.5% uptime SLA with quarterly reviews
   
3. Payment Terms & Conditions ✓
   → Monthly invoicing, Net 30 payment terms
   
4. Confidentiality & NDA ✓
   → Both parties to keep business information confidential
   
5. Liability & Indemnification ✓
   → Liability capped at $500,000 (issue flagged - see Risks)
   
6. Intellectual Property Rights ✓
   → Client data ownership, provider retains code/platform IP
   
7. Termination & Exit Clauses ✓
   → Either party can terminate with 90-day notice
   
8. Dispute Resolution ✓
   → Arbitration in Delhi, Indian arbitration law applies
   
9. Insurance Requirements ✓
   → Provider must maintain cyber liability insurance
   
10. Data Protection & Privacy ✓
    → Compliance with India Data Protection Act, GDPR compliant
    
11. Warranties & Guarantees ✓
    → Services provided "as-is", no warranty on uninterrupted access
    
12. Force Majeure Clause ✓
    → Both parties excused from performance during unforeseen events
```

**⚠️ TAB 3: RISKS IDENTIFIED (5 Issues)**
```
🔴 CRITICAL RISKS:
   1. Liability Cap Unusually High
      ├── Current: $500,000 (4.2x annual contract value)
      ├── Industry Standard: $120,000 - $180,000 (1-1.5x annual)
      ├── Recommendation: Reduce to $150,000
      └── Impact: Client exposed to significant financial risk
   
   2. Termination Clause Lacks Specificity
      ├── Issue: "90-day notice" mentioned but no detail on process
      ├── Missing: Email address for notice, effective date clarity
      ├── Risk: Disputes over when termination actually takes effect
      └── Suggestion: Add "Written notice to agreements@techcloud.com"

🟡 MEDIUM RISKS:
   3. Data Backup Recovery Terms Unclear
      ├── Contract says "daily backups" but no mention of:
      │   ├── Recovery Time Objective (RTO)
      │   ├── Recovery Point Objective (RPO)
      │   └── Cost of data restoration
      └── Recommendation: Add specific timeframes (e.g., RTO: 4 hours)

   4. Service Level Agreement Missing Remedies
      ├── States 99.5% uptime but doesn't specify penalty
      ├── What happens if SLA is breached? Service credit? Refund?
      └── Recommendation: Add "1% monthly credit for each 0.5% breach"

🟢 LOW RISKS:
   5. Auto-renewal Terms Could Be Clearer
      ├── Renewal is automatic unless 90-day notice given
      ├── Issue: Who should receive the cancellation notice?
      └── Suggestion: Specify notification email and procedure
```

**✨ TAB 4: IMPROVEMENT SUGGESTIONS (4 Recommendations)**
```
PRIORITY 1 - CRITICAL CHANGES:
   ✓ Action: Renegotiate Liability Cap
     └─ Propose: Reduce from $500,000 to $150,000
     └─ Reason: Aligns with industry standard for $120K/year contracts
     └─ Estimated Impact: Reduces provider's insurance costs

PRIORITY 2 - HIGH IMPORTANCE:
   ✓ Action: Define SLA Breach Penalties
     └─ Proposal: "1% service credit for each hour below 99.5% uptime"
     └─ Example: 1 hour downtime = $400 credit on next invoice
     └─ Benefit: Clear accountability for both parties

PRIORITY 3 - RECOMMENDED:
   ✓ Action: Add Data Recovery Specifics
     └─ Include:
        - Recovery Time Objective (RTO): 4 business hours
        - Recovery Point Objective (RPO): 24 hours
        - Restoration cost: Included for up to 2 incidents/year
     └─ Reason: Prevents disputes during actual data loss scenarios

PRIORITY 4 - NICE TO HAVE:
   ✓ Action: Add Security Incident Reporting Clause
     └─ Include: "Provider must report security incidents within 48 hours"
     └─ Align with: Industry best practices and GDPR requirements
     └─ Benefit: Enhanced security and transparency
```

**Processing Summary:**
```
✅ Analysis Complete
   ├── Processing Time: 12.3 seconds
   ├── Model Used: Mixtral via Groq
   ├── Pages Analyzed: 15
   ├── Total Content: 45,230 characters
   ├── Clauses Found: 12/12 (expected)
   ├── Risks Flagged: 5
   ├── Suggestions: 4 actionable items
   ├── Confidence Score: 94%
   └── Timestamp: Jan 11, 2026 - 2:45 PM
```
