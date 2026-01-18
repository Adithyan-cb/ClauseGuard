# Phase 7 Quick Reference

## Files Modified

### 1. `templates/uploadContract.html`
**What Changed:**
- Added CSS styles for results display (450+ lines of new CSS)
- Added HTML structure for results container with 4 tabs
- Added comprehensive JavaScript for:
  - Form submission to API
  - Polling every 2 seconds
  - Result rendering
  - Tab switching
  - Error handling

**Key Functions:**
```javascript
startPolling(analysisId)         // Initiate polling
displayResults(analysisData)      // Render all 4 tabs
displaySummary(summary)           // Render summary section
displayClauses(clauses)           // Render clauses section
displayRisks(risks)               // Render risks section
displaySuggestions(suggestions)   // Render suggestions section
setupTabSwitching()               // Enable tab clicks
```

## Key JavaScript Variables

```javascript
analysisId       // ID returned from upload endpoint
startTime        // When polling started (for elapsed time)
pollingInterval  // setInterval ID (cleared when done)
pollCount        // Number of polls executed
```

## CSS Classes for Customization

### Main Containers
- `.results-container` - Main results area
- `.results-header` - Header with status
- `.processing-state` - Loading spinner
- `.results-state` - Results display

### Tabs
- `.tabs-container` - Tab bar
- `.tab-button` - Individual tabs
- `.tab-content` - Tab panels

### Risk Styling
- `.risk-item.high` - Red styling for HIGH risk
- `.risk-item.medium` - Orange styling for MEDIUM risk
- `.risk-item.low` - Green styling for LOW risk

### Suggestion Styling
- `.suggestion-item.high` - High priority
- `.suggestion-item.medium` - Medium priority
- `.suggestion-item.low` - Low priority

## API Endpoints

```
POST   /api/upload-contract/      → Start analysis (returns analysis_id)
GET    /api/analysis/<id>/        → Check status & get results
GET    /api/contracts/            → List all contracts
```

## Response Status Values

```
analysis_status: 'pending'       // Not started yet
analysis_status: 'processing'    // Currently analyzing
analysis_status: 'completed'     // Done, results available
analysis_status: 'failed'        // Error occurred
```

## Polling Logic

```
Every 2 seconds:
  → Fetch /api/analysis/<analysis_id>/
  → Update elapsed time counter
  → Check analysis_status field
  → If 'completed' → display results & stop polling
  → If 'failed' → show error & stop polling
  → If 'processing' → continue polling
```

## Notification Types

```javascript
showNotification(message, 'success')  // Green success message
showNotification(message, 'error')    // Red error message
showNotification(message, 'loading')  // Blue loading message
```

## Tab Names (for data-tab attribute)

```html
data-tab="summary"      <!-- Summary tab -->
data-tab="clauses"      <!-- Clauses tab -->
data-tab="risks"        <!-- Risks tab -->
data-tab="suggestions"  <!-- Suggestions tab -->
```

## CSS Animation

```css
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
```

## Form Validation

```javascript
Check: File is selected
Check: Contract type is selected
Check: LLM model is selected
Check: Jurisdiction is selected
Check: File is PDF
Check: File size < 10MB
```

## Security Features

✅ CSRF token included in all requests
✅ HTML escaped to prevent XSS
✅ User permission check on API
✅ PDF-only file upload validation
✅ File size validation (10MB max)

## Mobile Responsive Breakpoints

```css
Max 768px  → Single column layout, full-width tabs
768-1024px → Multi-column, flexible tabs
> 1024px   → Desktop layout, max-width container
```

## Color Scheme

```
Primary Blue:      #3498db
Gold/Accent:       #d4af37
Dark Navy:         #0a2342
Success Green:     #27ae60
Warning Orange:    #f39c12
Danger Red:        #e74c3c
Light Gray:        #f5f7fa
Dark Gray:         #7f8c8d
Text Color:        #333
```

## Common Issues & Solutions

### Results Not Appearing?
1. Check browser console (F12) for JavaScript errors
2. Check Network tab for failed API calls
3. Verify `/api/analysis/` endpoint is returning data
4. Check that analysis_status is 'completed'

### Polling Not Starting?
1. Verify analysis_id is returned from upload endpoint
2. Check that startPolling() is called with correct ID
3. Look at Network tab to see if polling requests are sent

### Tab Switching Not Working?
1. Verify `.tab-button` click handlers are attached
2. Check that `setupTabSwitching()` is called after results display
3. Verify tab IDs match data-tab values

### Results Look Wrong?
1. Check API response format matches expected structure
2. Verify JSON is being parsed correctly
3. Check escapeHtml() is being used for user content

## Testing Console Commands

```javascript
// Check if results container is showing
document.getElementById('results-container').classList.contains('show')

// Check current active tab
document.querySelector('.tab-button.active').getAttribute('data-tab')

// Check elapsed time
document.getElementById('processing-time').textContent

// Manually trigger tab switch
document.querySelectorAll('.tab-button')[1].click()  // Switch to 2nd tab

// Check polling status
pollingInterval  // Should be a number (interval ID) if polling

// Check last API response
// Look in Network tab → api/analysis → Response
```

## Performance Notes

- Polling interval: 2000ms (2 seconds) - can be adjusted if needed
- Processing usually takes: 30-60 seconds
- Max file size: 10MB (configured in backend)
- Timeout: 300 seconds (5 minutes)

## Future Enhancements

- [ ] Download results as PDF
- [ ] Email results
- [ ] Share with team members
- [ ] Compare multiple contracts
- [ ] Custom report generation
- [ ] Bulk upload
- [ ] Advanced filtering on results
- [ ] Save custom suggestions
- [ ] Track analysis history trends

---

**Last Updated:** January 18, 2026  
**Status:** Phase 7 Complete ✅
