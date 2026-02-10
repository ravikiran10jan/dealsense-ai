"""
Prompt templates for call summarization and action items extraction.
"""

SUMMARY_PROMPT_TEMPLATE = """You are analyzing a sales call transcript for DXC Luxoft trade finance solutions.

CALL DETAILS:
- Customer: {account_name}
- Industry: {industry}
- Deal Stage: {deal_stage}
- Duration: {duration_minutes} minutes

FULL TRANSCRIPT:
{transcript}

INSTRUCTIONS:
Generate a structured call summary with the following sections. Be specific and actionable.

1. EXECUTIVE SUMMARY (2-3 sentences)
   - Overall outcome and sentiment of the call
   - Key decision or next step identified

2. KEY DISCUSSION POINTS (4-6 bullet points)
   - Main topics discussed
   - Customer requirements mentioned
   - Technical details covered
   - Pricing or timeline discussions

3. CUSTOMER PAIN POINTS (if identified)
   - What problems are they trying to solve?
   - Current system limitations mentioned
   - Process inefficiencies noted

4. OBJECTIONS RAISED (if any)
   - Pricing concerns
   - Timeline concerns
   - Feature gaps
   - Competition mentioned

5. NEXT STEPS (specific, actionable)
   - Follow-up actions agreed upon
   - Information to be provided
   - Meetings to schedule

6. DEAL HEALTH ASSESSMENT
   - Score: 1-10 (1=lost, 10=won)
   - Reason for the score
   - Risk factors to watch

FORMAT YOUR RESPONSE AS JSON:
{{
    "executive_summary": "string",
    "key_points": ["string", "string", ...],
    "pain_points": [
        {{"description": "string", "severity": "low|medium|high", "context": "string"}}
    ],
    "objections": [
        {{"description": "string", "category": "pricing|timeline|features|competition|general", "response_suggested": "string"}}
    ],
    "next_steps": "string",
    "deal_health_score": number,
    "deal_health_reason": "string"
}}

Return ONLY valid JSON, no additional text."""


ACTION_ITEMS_PROMPT_TEMPLATE = """Extract action items from this sales call transcript.

CALL DETAILS:
- Customer: {account_name}
- Seller: {seller_name}
- Call Date: {call_date}

TRANSCRIPT:
{transcript}

INSTRUCTIONS:
1. Identify all commitments, promises, and follow-up tasks mentioned
2. Look for phrases like:
   - "We'll send you..."
   - "I'll follow up with..."
   - "Can you provide..."
   - "Let's schedule..."
   - "We need to..."
   - "Action item:"
   - "Next steps:"

3. For each action item, determine:
   - Task description (specific and actionable)
   - Owner (Seller, Customer, or specific person mentioned)
   - Due date (if mentioned, otherwise estimate based on context)
   - Priority (high for deal blockers, medium for important, low for nice-to-have)

FORMAT YOUR RESPONSE AS JSON:
{{
    "action_items": [
        {{
            "task": "Specific task description",
            "owner": "Seller|Customer|Person Name",
            "due_date": "YYYY-MM-DD or null",
            "priority": "high|medium|low"
        }}
    ]
}}

Rules:
- Maximum 10 action items
- Minimum 1 action item (there's always at least a follow-up)
- If no specific due date mentioned, use null
- Default owner to Seller for internal tasks

Return ONLY valid JSON, no additional text."""


LIVE_QUERY_PROMPT_TEMPLATE = """You are a real-time sales assistant helping a seller during an active call.

CURRENT CALL CONTEXT:
- Customer: {account_name}
- Industry: {industry}
- Recent Conversation (last 2 minutes):
{recent_transcript}

RELEVANT KNOWLEDGE BASE CONTEXT:
{rag_context}

SELLER'S QUESTION:
{query}

INSTRUCTIONS:
1. Answer the question concisely (caller is on the line!)
2. Be direct - provide the key information first
3. If relevant numbers/stats are available, lead with those
4. Keep response to 2-3 sentences maximum
5. Use bullet points only if listing multiple items

Provide a clear, immediate answer that the seller can use right now in the conversation."""
