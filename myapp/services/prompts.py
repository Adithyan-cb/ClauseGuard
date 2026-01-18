"""
AI Prompt Templates Module

Contains all the instruction templates for the Groq LLM.
These prompts guide the AI to analyze contracts in a structured way.
"""

# ============================================================================
# SUMMARY ANALYSIS PROMPT
# ============================================================================
SUMMARY_PROMPT = """
You are a contract analysis expert. Analyze the following {contract_type} contract and provide a structured summary.

CONTRACT TEXT:
{contract_text}

Please provide the analysis in the following JSON format:
{{
    "summary": "A 2-3 paragraph executive summary of the contract",
    "contract_type": "{contract_type}",
    "parties": ["List", "of", "parties"],
    "duration": "Contract duration in plain language (e.g., '2 years')",
    "key_obligations": ["Obligation 1", "Obligation 2", "Obligation 3"],
    "financial_terms": "Summary of payment terms, amounts, and conditions",
    "jurisdiction": "The jurisdiction that governs this contract"
}}

IMPORTANT:
- Be concise but comprehensive
- Extract exact names of parties from the contract
- Include all financial figures and terms
- Identify the primary obligations of each party
- Return ONLY valid JSON, no additional text
- DO NOT wrap the JSON in markdown code fences (no triple backticks)
- Do NOT include any explanations before or after the JSON
"""

# ============================================================================
# CLAUSE EXTRACTION PROMPT
# ============================================================================
CLAUSE_EXTRACTION_PROMPT = """
You are a contract analysis expert. Identify and extract all distinct clauses from the following contract.

CONTRACT TEXT:
{contract_text}

For each clause you find, provide the clause type/name and the complete clause text.

Please provide the analysis in the following JSON format:
{{
    "clauses": [
        {{
            "type": "Clause Name (e.g., 'Payment Terms')",
            "text": "The complete text of this clause..."
        }},
        {{
            "type": "Another Clause Name",
            "text": "The complete text of this clause..."
        }}
    ]
}}

IMPORTANT:
- Extract EVERY distinct clause you can identify
- Use clear, standard names for clause types (e.g., "Scope of Services", "Confidentiality", "Liability Limitation")
- Include the FULL text of each clause, not summaries
- Organize by logical sections if multiple related clauses exist
- Return ONLY valid JSON, no additional text
- DO NOT wrap the JSON in markdown code fences (no triple backticks)
- Do NOT include any explanations before or after the JSON
"""

# ============================================================================
# RISK ANALYSIS PROMPT
# ============================================================================
RISK_ANALYSIS_PROMPT = """
You are a contract risk analysis expert. Analyze the following {contract_type} contract for risks, issues, and missing standard clauses.

CONTRACT TEXT:
{contract_text}

Based on standard industry practices for {contract_type} contracts in {jurisdiction}, identify:
1. Any risky, unusual, or unfavorable terms
2. Clauses that are missing but should be present
3. Gaps in protection or clarity
4. Red flags or non-standard language

Please provide the analysis in the following JSON format:
{{
    "risks": [
        {{
            "clause_type": "The clause or area where the risk exists",
            "risk_level": "HIGH|MEDIUM|LOW",
            "issue": "Brief title of the issue",
            "description": "Detailed explanation of why this is a risk",
            "impact": "Potential business impact of this risk"
        }}
    ],
    "missing_clauses": ["Clause 1", "Clause 2"],
    "total_risks": 5,
    "total_missing": 2
}}

IMPORTANT:
- Only flag ACTUAL risks, not minor issues
- Use proper risk levels: HIGH for critical issues, MEDIUM for important, LOW for minor concerns
- For missing clauses, list standard clauses that should be in a {contract_type}
- Provide clear, actionable descriptions
- Include business impact for each risk
- Return ONLY valid JSON, no additional text
- DO NOT wrap the JSON in markdown code fences (no triple backticks)
- Do NOT include any explanations before or after the JSON
"""

# ============================================================================
# SUGGESTIONS PROMPT
# ============================================================================
SUGGESTIONS_PROMPT = """
You are a contract improvement expert. Based on the following {contract_type} contract and industry standards for {jurisdiction}, provide specific improvement suggestions.

CONTRACT TEXT:
{contract_text}

Provide actionable suggestions for improving this contract based on:
1. Industry best practices for {contract_type} contracts in {jurisdiction}
2. Missing standard clauses
3. Areas that need clarification
4. Terms that could be more favorable
5. Protections that should be added

Please provide the analysis in the following JSON format:
{{
    "suggestions": [
        {{
            "priority": "HIGH|MEDIUM|LOW",
            "category": "Missing Clause|Wording Improvement|Risk Mitigation|Clarification|Protection",
            "current_state": "What the contract currently says (or 'Not mentioned' if missing)",
            "suggested_text": "The specific text you recommend adding or changing",
            "business_impact": "Why this improvement matters for the business"
        }}
    ],
    "total_suggestions": 5
}}

IMPORTANT:
- Prioritize suggestions that protect the business
- For missing clauses, provide complete, professional language
- For changes, explain clearly what should be modified
- Focus on practical, implementable suggestions
- Use HIGH priority only for critical improvements
- Include specific, relevant language in suggested_text
- Return ONLY valid JSON, no additional text
- DO NOT wrap the JSON in markdown code fences (no triple backticks)
- Do NOT include any explanations before or after the JSON
"""

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_summary_prompt(contract_type: str, contract_text: str) -> str:
    """
    Generate a summary analysis prompt with variables filled in.
    
    Args:
        contract_type (str): Type of contract (e.g., "Service Agreement")
        contract_text (str): The full text of the contract
    
    Returns:
        str: The complete prompt ready to send to the LLM
    """
    return SUMMARY_PROMPT.format(
        contract_type=contract_type,
        contract_text=contract_text
    )


def get_clause_extraction_prompt(contract_text: str) -> str:
    """
    Generate a clause extraction prompt with variables filled in.
    
    Args:
        contract_text (str): The full text of the contract
    
    Returns:
        str: The complete prompt ready to send to the LLM
    """
    return CLAUSE_EXTRACTION_PROMPT.format(
        contract_text=contract_text
    )


def get_risk_analysis_prompt(
    contract_type: str,
    jurisdiction: str,
    contract_text: str,
    chromadb_comparisons: str = ""
) -> str:
    """
    Generate a risk analysis prompt with variables filled in.
    
    Args:
        contract_type (str): Type of contract (e.g., "Service Agreement")
        jurisdiction (str): Jurisdiction (e.g., "India", "US", "UK")
        contract_text (str): The full text of the contract
        chromadb_comparisons (str): Standard clauses for comparison (optional)
    
    Returns:
        str: The complete prompt ready to send to the LLM
    """
    return RISK_ANALYSIS_PROMPT.format(
        contract_type=contract_type,
        jurisdiction=jurisdiction,
        contract_text=contract_text
    )


def get_suggestions_prompt(
    contract_type: str,
    jurisdiction: str,
    contract_text: str,
    missing_clauses: list = None
) -> str:
    """
    Generate an improvement suggestions prompt with variables filled in.
    
    Args:
        contract_type (str): Type of contract (e.g., "Service Agreement")
        jurisdiction (str): Jurisdiction (e.g., "India", "US", "UK")
        contract_text (str): The full text of the contract
        missing_clauses (list): List of missing clauses (optional)
    
    Returns:
        str: The complete prompt ready to send to the LLM
    """
    return SUGGESTIONS_PROMPT.format(
        contract_type=contract_type,
        jurisdiction=jurisdiction,
        contract_text=contract_text
    )
