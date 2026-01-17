# **Phase 7: User Interface Implementation Plan**

**Version:** 1.0  
**Last Updated:** January 17, 2026  
**Status:** Ready for Implementation  
**Project:** ClauseGuard - Contract Analysis UI/UX

---

## **Table of Contents**

1. [Overview](#overview)
2. [Page Structure](#page-structure)
3. [Upload Contract Page](#upload-contract-page)
4. [Results Display Page](#results-display-page)
5. [Contract History Page](#contract-history-page)
6. [Frontend Components](#frontend-components)
7. [JavaScript/AJAX Implementation](#javascriptajax-implementation)
8. [Styling & UX](#styling--ux)
9. [Implementation Checklist](#implementation-checklist)

---

## **Overview**

### **What Phase 7 Does**

Phase 7 builds the frontend (user-facing) components that interact with the Phase 6 API endpoints.

**User Journey:**
```
1. User navigates to "Analyze Contract" page
   ↓
2. Uploads PDF + selects contract type
   ↓
3. Clicks "Analyze"
   ↓
4. Sees "Processing..." with spinner
   ↓
5. JavaScript polls API every 2 seconds
   ↓
6. When analysis complete, shows 4 tabs with results
   ↓
7. User can view/download/share results
```

### **Technology Stack**

- **HTML/CSS** - Page structure and styling
- **JavaScript** - AJAX calls, real-time polling, UI updates
- **Bootstrap/Tailwind** - CSS framework (already in project)
- **Fetch API** - Call backend endpoints
- **JSON** - Parse API responses

---

## **Page Structure**

### **3 Main Pages to Build**

| Page | Route | Purpose |
|------|-------|---------|
| **Upload Contract** | `/upload-contract/` | User uploads PDF and selects options |
| **Analysis Results** | `/analysis/<id>/` | Display 4-tab results interface |
| **Contract History** | `/view-contracts/` | List of user's contracts |

---

## **Upload Contract Page**

### **File:** `templates/uploadContract.html`

### **Page Layout**

```
┌─────────────────────────────────────────────────────────┐
│ CLAUSE GUARD - Upload Contract for Analysis             │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ Step 1: Select PDF File                                 │
│ ┌──────────────────────────────────────────────────┐   │
│ │ [CHOOSE PDF FILE] 📄                              │   │
│ │ No file chosen                                   │   │
│ └──────────────────────────────────────────────────┘   │
│                                                         │
│ Step 2: Select Contract Type                            │
│ ┌──────────────────────────────────────────────────┐   │
│ │ ▼ Select Contract Type                           │   │
│ │ ─ Service Agreement                              │   │
│ │ ─ Employment Contract                            │   │
│ │ ─ Non-Disclosure Agreement (NDA)                │   │
│ │ ─ Partnership Agreement                         │   │
│ │ ─ Vendor Agreement                              │   │
│ └──────────────────────────────────────────────────┘   │
│                                                         │
│ Step 3: Select LLM Model (Optional)                     │
│ ┌──────────────────────────────────────────────────┐   │
│ │ ▼ Mixtral-8x7b-32768 (Default - Recommended)    │   │
│ │ ─ Llama-70b (Slower but more accurate)          │   │
│ │ ─ Llama-8b (Fastest)                            │   │
│ └──────────────────────────────────────────────────┘   │
│                                                         │
│ [ANALYZE CONTRACT] [CLEAR]                             │
│                                                         │
│ Error message area (red text if error)                 │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### **HTML Elements**

```html
<form id="uploadForm">
  <!-- File upload -->
  <input 
    type="file" 
    id="contractFile" 
    accept=".pdf" 
    required
  />
  
  <!-- Contract type dropdown -->
  <select id="contractType" required>
    <option value="">Select Contract Type</option>
    <option value="SERVICE_AGREEMENT_INDIA">Service Agreement</option>
    <option value="EMPLOYMENT_CONTRACT_INDIA">Employment Contract</option>
    <option value="NDA_INDIA">Non-Disclosure Agreement</option>
    <option value="PARTNERSHIP_AGREEMENT_INDIA">Partnership Agreement</option>
    <option value="VENDOR_AGREEMENT_INDIA">Vendor Agreement</option>
  </select>
  
  <!-- LLM Model dropdown -->
  <select id="llmModel">
    <option value="mixtral-8x7b-32768" selected>
      Mixtral-8x7b (Recommended)
    </option>
    <option value="llama-70b">Llama-70b (Slower)</option>
    <option value="llama-8b">Llama-8b (Faster)</option>
  </select>
  
  <!-- Buttons -->
  <button type="submit" id="analyzeBtn">Analyze Contract</button>
  <button type="reset">Clear</button>
  
  <!-- Error message -->
  <div id="errorMessage" class="error"></div>
</form>
```

### **JavaScript Logic**

```javascript
document.getElementById('uploadForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  
  // 1. Validate form
  const file = document.getElementById('contractFile').files[0];
  const contractType = document.getElementById('contractType').value;
  
  if (!file) {
    showError('Please select a PDF file');
    return;
  }
  
  if (!contractType) {
    showError('Please select a contract type');
    return;
  }
  
  // 2. Validate file is PDF
  if (file.type !== 'application/pdf') {
    showError('Only PDF files are allowed');
    return;
  }
  
  // 3. Validate file size (max 10MB)
  const maxSize = 10 * 1024 * 1024;
  if (file.size > maxSize) {
    showError('File size exceeds 10MB limit');
    return;
  }
  
  // 4. Show loading state
  showLoading('Uploading and analyzing contract...');
  
  // 5. Create FormData
  const formData = new FormData();
  formData.append('contract_file', file);
  formData.append('contract_type', contractType);
  formData.append('jurisdiction', 'INDIA');
  formData.append('llm_model', document.getElementById('llmModel').value);
  
  try {
    // 6. POST to upload endpoint
    const response = await fetch('/api/upload-contract/', {
      method: 'POST',
      body: formData,
      headers: {
        'X-CSRFToken': getCookie('csrftoken')
      }
    });
    
    const data = await response.json();
    
    if (data.status === 'success') {
      // 7. Redirect to results page with polling
      const analysisId = data.analysis_id;
      window.location.href = `/analysis-results/${analysisId}/`;
    } else {
      showError(data.message);
    }
  } catch (error) {
    showError('Error uploading contract: ' + error.message);
  }
});

function showLoading(message) {
  document.getElementById('errorMessage').className = 'loading';
  document.getElementById('errorMessage').textContent = message;
}

function showError(message) {
  document.getElementById('errorMessage').className = 'error';
  document.getElementById('errorMessage').textContent = message;
}
```

---

## **Results Display Page**

### **File:** `templates/analysisResults.html`

### **Page Layout**

```
┌──────────────────────────────────────────────────────────┐
│ CLAUSE GUARD - Analysis Results                          │
├──────────────────────────────────────────────────────────┤
│                                                          │
│ Contract: Service Agreement | Status: ✓ Completed       │
│ Processing Time: 47.3 seconds                           │
│                                                          │
│ [SUMMARY] [CLAUSES] [RISKS] [SUGGESTIONS] [Download] [Share]
│                                                          │
├──────────────────────────────────────────────────────────┤
│ SUMMARY TAB (ACTIVE)                                     │
├──────────────────────────────────────────────────────────┤
│                                                          │
│ Contract Overview                                        │
│ ───────────────────────────────────────────────────     │
│ Type: Service Agreement                                  │
│ Parties: Company A, Company B                            │
│ Duration: 2 years                                        │
│ Jurisdiction: India                                      │
│                                                          │
│ Financial Terms                                          │
│ ───────────────────────────────────────────────────     │
│ Amount: ₹500,000 per month                              │
│ Payment Terms: Due within 15 days                        │
│                                                          │
│ Key Obligations                                          │
│ ───────────────────────────────────────────────────     │
│ • Provide 24/7 infrastructure                            │
│ • Maintain 99.9% uptime                                  │
│ • Daily backups                                          │
│                                                          │
│ [Full Summary Text...]                                   │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### **HTML Structure**

```html
<div id="analysisContainer">
  <!-- Processing state -->
  <div id="processingState" class="processing">
    <h3>⏳ Analyzing your contract...</h3>
    <div class="spinner"></div>
    <p>Processing time: <span id="processingTime">0</span>s</p>
    <p>This usually takes 30-60 seconds</p>
  </div>
  
  <!-- Results state -->
  <div id="resultsState" class="hidden">
    <div class="results-header">
      <h2>Analysis Results</h2>
      <p>Status: <span id="statusBadge">Completed ✓</span></p>
      <p>Processing Time: <span id="totalTime">0</span>s</p>
    </div>
    
    <!-- Tabs -->
    <div class="tabs">
      <button class="tab-button active" data-tab="summary">SUMMARY</button>
      <button class="tab-button" data-tab="clauses">CLAUSES</button>
      <button class="tab-button" data-tab="risks">RISKS</button>
      <button class="tab-button" data-tab="suggestions">SUGGESTIONS</button>
      <button class="action-button" id="downloadBtn">📥 Download</button>
      <button class="action-button" id="shareBtn">📤 Share</button>
    </div>
    
    <!-- Summary Tab -->
    <div id="summary" class="tab-content active">
      <div id="summaryContent"></div>
    </div>
    
    <!-- Clauses Tab -->
    <div id="clauses" class="tab-content">
      <div id="clausesContent"></div>
    </div>
    
    <!-- Risks Tab -->
    <div id="risks" class="tab-content">
      <div id="risksContent"></div>
    </div>
    
    <!-- Suggestions Tab -->
    <div id="suggestions" class="tab-content">
      <div id="suggestionsContent"></div>
    </div>
  </div>
</div>
```

### **JavaScript Logic - Polling**

```javascript
// Extract analysis_id from URL
const analysisId = getAnalysisIdFromURL();
let pollingInterval;
let startTime = Date.now();

// Start polling immediately
pollForResults();

function pollForResults() {
  pollingInterval = setInterval(async () => {
    try {
      const response = await fetch(`/api/analysis/${analysisId}/`, {
        method: 'GET',
        headers: {
          'X-CSRFToken': getCookie('csrftoken')
        }
      });
      
      const data = await response.json();
      
      if (data.status === 'success') {
        const analysisStatus = data.data.analysis_status;
        
        // Update processing time display
        const elapsed = Math.floor((Date.now() - startTime) / 1000);
        document.getElementById('processingTime').textContent = elapsed;
        
        if (analysisStatus === 'completed') {
          // Analysis complete - show results
          clearInterval(pollingInterval);
          displayResults(data.data);
          hideProcessing();
          showResults();
        } else if (analysisStatus === 'failed') {
          // Analysis failed
          clearInterval(pollingInterval);
          showError(data.data.error_message);
          hideProcessing();
        }
      }
    } catch (error) {
      console.error('Error polling:', error);
    }
  }, 2000); // Poll every 2 seconds
}

function displayResults(analysisData) {
  // Display Summary
  displaySummary(analysisData.summary);
  
  // Display Clauses
  displayClauses(analysisData.clauses);
  
  // Display Risks
  displayRisks(analysisData.risks);
  
  // Display Suggestions
  displaySuggestions(analysisData.suggestions);
}

function displaySummary(summary) {
  const html = `
    <div class="summary-section">
      <h3>Contract Overview</h3>
      <p><strong>Type:</strong> ${summary.contract_type}</p>
      <p><strong>Parties:</strong> ${summary.parties.join(', ')}</p>
      <p><strong>Duration:</strong> ${summary.duration}</p>
      <p><strong>Jurisdiction:</strong> ${summary.jurisdiction}</p>
      
      <h3>Financial Terms</h3>
      <p>${summary.financial_terms}</p>
      
      <h3>Key Obligations</h3>
      <ul>
        ${summary.key_obligations.map(o => `<li>${o}</li>`).join('')}
      </ul>
      
      <h3>Full Summary</h3>
      <p>${summary.summary}</p>
    </div>
  `;
  document.getElementById('summaryContent').innerHTML = html;
}

function displayClauses(clauses) {
  const clausesHtml = clauses.clauses.map((clause, idx) => `
    <div class="clause-item">
      <h4>${clause.type}</h4>
      <p>${clause.text}</p>
    </div>
  `).join('');
  
  const html = `
    <div>
      <h3>Found ${clauses.total_clauses} Clauses</h3>
      ${clausesHtml}
    </div>
  `;
  document.getElementById('clausesContent').innerHTML = html;
}

function displayRisks(risks) {
  const risksHtml = risks.risks.map(risk => {
    const icon = risk.risk_level === 'HIGH' ? '🔴' : 
                 risk.risk_level === 'MEDIUM' ? '🟡' : '🟢';
    
    return `
      <div class="risk-item risk-${risk.risk_level.toLowerCase()}">
        <h4>${icon} ${risk.issue}</h4>
        <p><strong>Clause:</strong> ${risk.clause_type}</p>
        <p><strong>Description:</strong> ${risk.description}</p>
        <p><strong>Impact:</strong> ${risk.impact}</p>
      </div>
    `;
  }).join('');
  
  const html = `
    <div>
      <h3>Identified ${risks.total_risks} Risks</h3>
      ${risksHtml}
      ${risks.missing_clauses.length > 0 ? `
        <h3>Missing Clauses (${risks.total_missing})</h3>
        <ul>
          ${risks.missing_clauses.map(c => `<li>${c}</li>`).join('')}
        </ul>
      ` : ''}
    </div>
  `;
  document.getElementById('risksContent').innerHTML = html;
}

function displaySuggestions(suggestions) {
  const suggestionsHtml = suggestions.suggestions.map(sug => {
    const priorityClass = `priority-${sug.priority.toLowerCase()}`;
    
    return `
      <div class="suggestion-item ${priorityClass}">
        <h4>💡 ${sug.category}</h4>
        <p><strong>Priority:</strong> ${sug.priority}</p>
        <p><strong>Current:</strong> ${sug.current_state}</p>
        <p><strong>Suggested:</strong><br/><code>${sug.suggested_text}</code></p>
        <p><strong>Impact:</strong> ${sug.business_impact}</p>
      </div>
    `;
  }).join('');
  
  const html = `
    <div>
      <h3>${suggestions.total_suggestions} Improvement Suggestions</h3>
      ${suggestionsHtml}
    </div>
  `;
  document.getElementById('suggestionsContent').innerHTML = html;
}
```

### **Tab Switching**

```javascript
document.querySelectorAll('.tab-button').forEach(btn => {
  btn.addEventListener('click', () => {
    const tabName = btn.getAttribute('data-tab');
    
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
      tab.classList.remove('active');
    });
    
    // Remove active class from all buttons
    document.querySelectorAll('.tab-button').forEach(b => {
      b.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(tabName).classList.add('active');
    btn.classList.add('active');
  });
});
```

---

## **Contract History Page**

### **File:** `templates/viewContracts.html` (Already exists, needs enhancement)

### **Enhancements**

```html
<div class="contracts-list">
  <h2>Your Contracts</h2>
  
  <table class="contracts-table">
    <thead>
      <tr>
        <th>Contract Name</th>
        <th>Type</th>
        <th>Uploaded</th>
        <th>Status</th>
        <th>Actions</th>
      </tr>
    </thead>
    <tbody id="contractsTableBody">
      <!-- Populated by JavaScript -->
    </tbody>
  </table>
</div>
```

### **JavaScript to Fetch Contracts**

```javascript
async function loadContracts() {
  try {
    const response = await fetch('/api/contracts/', {
      method: 'GET',
      headers: {
        'X-CSRFToken': getCookie('csrftoken')
      }
    });
    
    const data = await response.json();
    
    if (data.status === 'success') {
      displayContracts(data.contracts);
    }
  } catch (error) {
    console.error('Error loading contracts:', error);
  }
}

function displayContracts(contracts) {
  const tbody = document.getElementById('contractsTableBody');
  
  tbody.innerHTML = contracts.map(contract => {
    const statusBadge = getStatusBadge(contract.analysis_status);
    const actions = contract.analysis_id ? 
      `<a href="/analysis-results/${contract.analysis_id}/">View Results</a>` :
      'Pending Analysis';
    
    return `
      <tr>
        <td>${contract.name}</td>
        <td>${contract.type}</td>
        <td>${new Date(contract.uploaded_at).toLocaleDateString()}</td>
        <td>${statusBadge}</td>
        <td>${actions}</td>
      </tr>
    `;
  }).join('');
}

function getStatusBadge(status) {
  const badges = {
    'completed': '<span class="badge badge-success">✓ Completed</span>',
    'processing': '<span class="badge badge-warning">⏳ Processing</span>',
    'failed': '<span class="badge badge-danger">✗ Failed</span>',
    'pending': '<span class="badge badge-secondary">⊘ Pending</span>'
  };
  return badges[status] || badges['pending'];
}

// Load contracts when page loads
document.addEventListener('DOMContentLoaded', loadContracts);
```

---

## **Frontend Components**

### **Shared Components**

#### **1. Loading Spinner**

```html
<div class="spinner">
  <div class="spinner-border"></div>
</div>
```

```css
.spinner {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40px;
}

.spinner-border {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
```

#### **2. Status Badges**

```css
.badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: bold;
}

.badge-success { background: #d4edda; color: #155724; }
.badge-warning { background: #fff3cd; color: #856404; }
.badge-danger { background: #f8d7da; color: #721c24; }
.badge-secondary { background: #e2e3e5; color: #383d41; }
```

#### **3. Risk Level Colors**

```css
.risk-high {
  border-left: 4px solid #dc3545;
  background: #fff5f5;
}

.risk-medium {
  border-left: 4px solid #ffc107;
  background: #fffbf0;
}

.risk-low {
  border-left: 4px solid #28a745;
  background: #f5fff5;
}
```

---

## **JavaScript/AJAX Implementation**

### **Utility Functions**

```javascript
// Get CSRF token from cookie
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
      cookie = cookie.trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

// Format date nicely
function formatDate(dateString) {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-IN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });
}

// Format time elapsed
function formatTime(seconds) {
  if (seconds < 60) return `${seconds}s`;
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}m ${secs}s`;
}

// Extract analysis ID from URL
function getAnalysisIdFromURL() {
  const match = window.location.pathname.match(/\/analysis-results\/(\d+)\//);
  return match ? match[1] : null;
}
```

---

## **Styling & UX**

### **Color Scheme**

| Element | Color | Use |
|---------|-------|-----|
| Primary | #3498db (Blue) | Buttons, Links, Highlights |
| Success | #27ae60 (Green) | Completed status, Low risk |
| Warning | #f39c12 (Orange) | Processing, Medium risk |
| Danger | #e74c3c (Red) | Error, High risk |
| Neutral | #95a5a6 (Gray) | Disabled, Secondary |

### **Typography**

- **Headings:** Bold, larger font
- **Body Text:** Regular weight, readable size
- **Code/Quotes:** Monospace font, light background

### **Responsive Design**

```css
/* Mobile (< 768px) */
@media (max-width: 768px) {
  .tabs {
    flex-direction: column;
  }
  
  .tab-button {
    width: 100%;
  }
  
  .contracts-table {
    font-size: 12px;
  }
}

/* Tablet (768px - 1024px) */
@media (min-width: 768px) and (max-width: 1024px) {
  .tab-button {
    flex: 1;
  }
}

/* Desktop (> 1024px) */
@media (min-width: 1024px) {
  .container {
    max-width: 1200px;
    margin: 0 auto;
  }
}
```

---

## **Implementation Checklist**

### **Phase 7A: Upload Contract Page**
- [ ] Create `uploadContract.html` template
- [ ] Add form with file picker
- [ ] Add contract type dropdown
- [ ] Add LLM model dropdown
- [ ] Add JavaScript form validation
- [ ] Handle file upload via AJAX
- [ ] Show loading state
- [ ] Redirect to results page on success
- [ ] Show error messages

### **Phase 7B: Results Display Page**
- [ ] Create `analysisResults.html` template
- [ ] Add processing state UI
- [ ] Implement polling logic (fetch every 2 seconds)
- [ ] Display loading spinner
- [ ] Create 4 tabs (Summary, Clauses, Risks, Suggestions)
- [ ] Implement Summary tab rendering
- [ ] Implement Clauses tab rendering
- [ ] Implement Risks tab rendering
- [ ] Implement Suggestions tab rendering
- [ ] Add tab switching functionality
- [ ] Show final status and processing time

### **Phase 7C: Contract History Enhancement**
- [ ] Fetch contracts list from API
- [ ] Display contracts in table format
- [ ] Show analysis status with badges
- [ ] Add "View Results" links
- [ ] Implement sorting/filtering (optional)

### **Phase 7D: Styling & Polish**
- [ ] Apply color scheme
- [ ] Add CSS for all components
- [ ] Make responsive for mobile
- [ ] Add hover effects on buttons
- [ ] Add transitions for tab switching
- [ ] Style error/success messages
- [ ] Add loading spinners

### **Phase 7E: Testing**
- [ ] Test file upload validation
- [ ] Test contract type selection
- [ ] Test polling updates
- [ ] Test tab switching
- [ ] Test error handling
- [ ] Test on mobile devices
- [ ] Test API timeout scenarios

---

## **File Modifications Summary**

| File | Changes |
|------|---------|
| `templates/uploadContract.html` | Create new upload form |
| `templates/analysisResults.html` | Create new results display |
| `templates/viewContracts.html` | Enhance contract list |
| `static/js/analysis.js` | New file for AJAX logic |
| `static/css/analysis.css` | New file for analysis styling |

---

## **Next Steps**

After Phase 7 completion:
1. Test full end-to-end workflow
2. Fix any UI bugs
3. Proceed to Phase 8 (Testing)
4. Deploy to production

---

**Status:** Ready for implementation  
**Estimated Time:** 6-8 hours  
**Complexity:** Medium
