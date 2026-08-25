# app.py
import streamlit as st
import os
import sys
import time
from datetime import datetime, timedelta
import random
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="🚚 ParcelPilot AI Support Agent",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==================== SESSION STATE INIT ====================
def initialize_session_state():
    """Initialize all session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "agent_initialized" not in st.session_state:
        st.session_state.agent_initialized = False
    if "agent" not in st.session_state:
        st.session_state.agent = None
    if "processing" not in st.session_state:
        st.session_state.processing = False
    if "page" not in st.session_state:
        st.session_state.page = "Overview"  # Start on Overview page
    if "activity" not in st.session_state:
        st.session_state.activity = []
    if "session_start" not in st.session_state:
        st.session_state.session_start = datetime.now()
    if "query_count" not in st.session_state:
        st.session_state.query_count = 0
    if "documents_indexed" not in st.session_state:
        st.session_state.documents_indexed = 20
    if "confidence_score" not in st.session_state:
        st.session_state.confidence_score = 87
    if "last_prompt" not in st.session_state:
        st.session_state.last_prompt = None
    if "agent_mode" not in st.session_state:
        st.session_state.agent_mode = "Mock"
    if "investigation_results" not in st.session_state:
        st.session_state.investigation_results = {}
    if "investigation_timeline" not in st.session_state:
        st.session_state.investigation_timeline = []


initialize_session_state()


# ==================== COMPLETE MOCK AGENT ====================
class MockParcelPilotAgent:
    """Complete mock agent that works without any external dependencies."""

    def __init__(self, user_context=None):
        self.user_context = user_context or {}
        self.conversation_history = []
        self.source_priority = [
            "customer_agreement",
            "current_policy",
            "current_sop",
            "product_guide",
            "deprecated_policy",
        ]
        self.source_priority_labels = {
            "customer_agreement": "Customer Agreement",
            "current_policy": "Current Policy",
            "current_sop": "Current SOP",
            "product_guide": "Product Guide",
            "deprecated_policy": "Deprecated Policy",
        }
        self.source_priority_values = {
            "customer_agreement": 100,
            "current_policy": 90,
            "current_sop": 85,
            "product_guide": 70,
            "deprecated_policy": 20,
        }

    def investigate_issue(self, issue_name: str, details: dict) -> str:
        """Investigate an issue and return findings."""
        customers = ", ".join(details.get("affected_customers", []))
        return f"""🔍 **Investigation Results for {issue_name}**

**Root Cause:** {details.get("root_cause", "Unknown")}

**Recommendation:** {details.get("recommendation", "Escalate to operations team")}

**Key Findings:**
- Severity: {details.get("severity", "Unknown")}
- Tickets affected: {details.get("tickets", 0)}
- Affected customers: {customers}
- Trend: {details.get("trend", "Stable")}
- Avg resolution time: {details.get("avg_resolution_time", "Unknown")}
- SLA Impact: {details.get("sla_impact", "Unknown")}

**Next Steps:**
1. Review the root cause analysis above
2. Implement the recommended action
3. Monitor for recurrence

📄 **Sources:** Issue investigation database, operational metrics"""

    def process_query(self, query: str) -> str:
        """Process a user query and return a response."""
        import re

        query = query.strip()
        if not query:
            return "Please enter a question or request."

        query_lower = query.lower()

        # Check for cancellation policy
        if "cancellation" in query_lower or "cancel" in query_lower:
            if "fee" in query_lower or "cost" in query_lower or "charge" in query_lower:
                return self._get_cancellation_fee_response()
            return self._get_cancellation_policy_response()

        # Check for SLA
        if "sla" in query_lower or "response time" in query_lower:
            return self._get_sla_response()

        # Check for specific orders
        if "ord-" in query_lower:
            return self._get_order_response(query)

        # Check for tickets
        if "ticket" in query_lower:
            return self._get_ticket_response(query)

        # Check for Northstar
        if "northstar" in query_lower:
            if "cancel" in query_lower or "cancellation" in query_lower:
                return self._get_northstar_cancellation_response()
            return self._get_northstar_response()

        # Check for Beacon
        if "beacon" in query_lower:
            return self._get_beacon_response()

        # Check for LumenWorks
        if "lumen" in query_lower or "lumenworks" in query_lower:
            return self._get_lumenworks_response()

        # Check for service credit
        if "credit" in query_lower:
            return self._get_service_credit_response()

        # Check for escalation
        if "escalate" in query_lower or "escalation" in query_lower:
            return self._get_escalation_response()

        # Check for all policies
        if "all policies" in query_lower or "show me all" in query_lower:
            return self._get_all_policies_response()

        # Check for greetings
        greetings = {
            "hello",
            "hi",
            "hey",
            "good morning",
            "good afternoon",
            "good evening",
        }
        if query_lower in greetings:
            return self._get_greeting_response()

        # Default response
        return self._get_general_response(query)

    def _get_cancellation_policy_response(self) -> str:
        return """📋 **Cancellation Policy**

**Standard Cancellation:**
- Orders can be cancelled within 24 hours of placement at **no cost**
- Cancellations after 24 hours may incur a **15% restocking fee**
- Custom orders are non-refundable after production has begun

**Fee Waiver Conditions:**
- Cancellations due to carrier delays or delivery issues may be eligible for fee waiver
- Northstar account holders receive preferential cancellation terms

**Process:**
1. Submit cancellation request through the support portal
2. Cancellation fee will be calculated based on order status
3. Confirmation sent within 2 business hours

📄 **Sources:** cancellation_policy_v3.2.pdf, Northstar_Agreement_2026.pdf"""

    def _get_cancellation_fee_response(self) -> str:
        return """💵 **Cancellation Fee Analysis**

For standard orders:
- **Within 24 hours of placement:** $0 fee
- **24-72 hours:** 15% of order value
- **72+ hours:** 25% of order value

**Northstar Special Terms:**
- Northstar accounts receive waived fees on first 3 cancellations per quarter
- Additional cancellations subject to standard fees

📄 **Sources:** pricing_guide_2026.pdf, Northstar_Agreement_2026.pdf, cancellation_policy_v3.2.pdf"""

    def _get_sla_response(self) -> str:
        return """⏱️ **SLA Response Times**

**Standard SLAs:**
- **P1 (Critical):** 15 minutes response, 4 hours resolution
- **P2 (High):** 1 hour response, 8 hours resolution
- **P3 (Normal):** 4 hours response, 24 hours resolution
- **P4 (Low):** 8 hours response, 48 hours resolution

**Northstar Premium SLA:**
- P1: 5 minutes response, 2 hours resolution
- P2: 30 minutes response, 4 hours resolution
- Dedicated support team

📄 **Sources:** SLA_policy_2026.pdf, Northstar_Agreement_2026.pdf"""

    def _get_order_response(self, query: str) -> str:
        import re

        order_id = re.search(r"ORD-\d+", query.upper())
        if not order_id:
            return "⚠️ Please provide a valid order ID (e.g., ORD-1001)"

        order_id = order_id.group(0)

        if "ORD-1001" in order_id:
            return """📦 **Order ORD-1001**

**Status:** In Transit
**Customer:** Northstar
**Order Date:** 2026-08-20
**Expected Delivery:** 2026-08-28
**Value:** $4,250.00
**Priority:** High

📄 **Sources:** order_ORD-1001"""

        if "ORD-1002" in order_id:
            return """📦 **Order ORD-1002**

**Status:** Processing
**Customer:** Beacon Retail
**Order Date:** 2026-08-22
**Expected Delivery:** 2026-09-01
**Value:** $1,890.00

📄 **Sources:** order_ORD-1002"""

        return f"⚠️ Order {order_id} not found."

    def _get_ticket_response(self, query: str) -> str:
        return """🎫 **Open Tickets Summary**

**Total Open Tickets:** 12
**High Priority:** 3
**Medium Priority:** 5
**Low Priority:** 4

**Recent Tickets:**
- TKT-501: Carrier integration issue (P1) - In Progress
- TKT-502: Billing discrepancy (P2) - Assigned
- TKT-503: API timeout errors (P2) - Under Investigation

📄 **Sources:** ticket_system"""

    def _get_northstar_response(self) -> str:
        return """🏢 **Northstar Account Information**

**Account Type:** Premium Enterprise
**Industry:** Logistics & Distribution
**Contract Start:** January 2026
**Account Manager:** Sarah Mitchell

**Special Terms:**
- Priority support with 15-minute response SLA
- 3 free cancellations per quarter

📄 **Sources:** Northstar_Agreement_2026.pdf"""

    def _get_northstar_cancellation_response(self) -> str:
        return """🏢 **Northstar - Cancellation Analysis**

**Account Status:** Premium
**Cancellation Terms:**
- No fee for first 3 cancellations per quarter
- Standard fees apply after that

**Current Quarter:** Q3 2026
- Cancellations used: 1 of 3
- Remaining free cancellations: 2

📄 **Sources:** Northstar_Agreement_2026.pdf, cancellation_policy_v3.2.pdf"""

    def _get_beacon_response(self) -> str:
        return """🏪 **Beacon Retail Account Information**

**Account Type:** Standard Retail
**Industry:** Retail & E-commerce
**Contract Start:** March 2026

**Special Terms:**
- 24/7 support coverage
- Weekend delivery options

📄 **Sources:** Beacon_Retail_Contract_2026.pdf"""

    def _get_lumenworks_response(self) -> str:
        return """💡 **LumenWorks Account Information**

**Account Type:** Standard
**Industry:** Technology & Software
**Contract Start:** June 2026

**Special Terms:**
- Standard SLAs apply
- 30-day payment terms

📄 **Sources:** LumenWorks_Agreement_2026.pdf"""

    def _get_service_credit_response(self) -> str:
        return """💳 **Service Credit Summary**

**LumenWorks:** $250 (July 2026)
**Northstar:** $0
**Beacon Retail:** $75 (August 2026)

📄 **Sources:** service_credits"""

    def _get_escalation_response(self) -> str:
        return """⚠️ **ESCALATION REQUEST**

**Action:** Create Escalation
**Recommendation:** Escalate to Level 2 Support
**Reason:** Issue requires specialized expertise

**Please confirm:** This action requires your confirmation before proceeding.

📄 **Sources:** escalation_policy_2026.pdf"""

    def _get_all_policies_response(self) -> str:
        return """📚 **All Current Policies & Agreements**

**1. Cancellation Policy (v3.2)**
- 24-hour free cancellation window
- 15% restocking fee after 24 hours

**2. SLA Policy (2026)**
- Tiered response times (P1-P4)

**3. Customer Agreements:**
- Northstar (Premium)
- Beacon Retail (Standard)
- LumenWorks (Standard)

📄 **Sources:** cancellation_policy_v3.2.pdf, SLA_policy_2026.pdf"""

    def _get_greeting_response(self) -> str:
        return """👋 **Hello! I'm ParcelPilot.**

I'm an AI support agent for logistics operations.

**I can help with:**

📄 **Document Search** - Find policies, SOPs, agreements
📊 **Data Lookup** - Check orders, tickets, accounts
🧠 **Evidence-Based Reasoning** - Combine data with documents
⚡ **Actions** - Create escalations with confirmation

**Try:**
- "What is the cancellation policy?"
- "Look up order ORD-1001"
- "Can Northstar cancel without a fee?"
- "Escalate ticket TKT-501"

📄 **Sources:** ParcelPilot knowledge base"""

    def _get_general_response(self, query: str) -> str:
        return f"""❓ **I need more specific information**

I couldn't find a match for: **"{query}"**

**Try asking about:**
- "What is the cancellation policy?"
- "Check the status of ORD-1001"
- "Can Northstar cancel without a fee?"
- "Escalate ticket TKT-501"

📄 **Sources:** ParcelPilot knowledge base"""


# ==================== AGENT INIT ====================
def init_agent():
    """Initialize the agent."""
    if not st.session_state.agent_initialized:
        try:
            user_context = {
                "role": "support_agent",
                "user_id": "demo_user",
                "supported_accounts": ["Northstar", "LumenWorks", "Beacon Retail"],
            }
            st.session_state.agent = MockParcelPilotAgent(user_context)
            st.session_state.agent_mode = "Mock"
            st.session_state.agent_initialized = True
            return True
        except Exception as e:
            st.error(f"⚠️ Agent initialization failed: {str(e)}")
            return False
    return True


# ==================== CUSTOM CSS ====================
st.markdown(
    """
<style>
    .stApp { background: #0a0e17; }
    .header-container {
        background: linear-gradient(135deg, #0f1a2e 0%, #1a1a3e 50%, #0d1f3c 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        border: 1px solid rgba(255,255,255,0.06);
    }
    .header-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
    }
    .header-title {
        color: #ffffff !important;
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        margin: 0 !important;
    }
    .header-title span {
        background: linear-gradient(135deg, #7c6cf7, #4a6cf7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .header-subtitle {
        color: rgba(255,255,255,0.5) !important;
        font-size: 0.9rem !important;
        margin: 0.2rem 0 0 0 !important;
        font-weight: 400;
    }
    .header-status {
        display: inline-block;
        background: rgba(76, 175, 80, 0.12);
        padding: 0.2rem 0.8rem;
        border-radius: 20px;
        color: #4caf50 !important;
        font-size: 0.7rem !important;
        font-weight: 500;
        border: 1px solid rgba(76, 175, 80, 0.15);
    }
    .header-time {
        color: rgba(255,255,255,0.3) !important;
        font-size: 0.8rem !important;
        text-align: right;
    }
    .sidebar-title {
        color: #ffffff !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        text-align: center;
        padding: 0.8rem 0;
        border-bottom: 1px solid rgba(255,255,255,0.06);
        margin-bottom: 1rem;
    }
    .sidebar-section-title {
        color: rgba(255,255,255,0.3) !important;
        font-size: 0.65rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        padding: 0.8rem 0 0.4rem 0;
    }
    .metric-card {
        background: rgba(255,255,255,0.03);
        padding: 0.7rem;
        border-radius: 8px;
        border: 1px solid rgba(255,255,255,0.04);
        text-align: center;
        transition: all 0.2s ease;
        cursor: default;
    }
    .metric-card:hover {
        background: rgba(255,255,255,0.05);
        transform: translateY(-1px);
    }
    .metric-value {
        font-size: 1.4rem !important;
        font-weight: 600 !important;
        color: #ffffff !important;
        line-height: 1.2;
    }
    .metric-value.danger { color: #f5576c !important; }
    .metric-value.warning { color: #f093fb !important; }
    .metric-value.success { color: #43e97b !important; }
    .metric-value.info { color: #4facfe !important; }
    .metric-label {
        color: rgba(255,255,255,0.35) !important;
        font-size: 0.65rem !important;
        margin-top: 0.2rem;
        font-weight: 400;
    }
    .user-message {
        background: rgba(74, 108, 247, 0.12);
        color: #ffffff !important;
        padding: 0.8rem 1.2rem;
        border-radius: 12px 12px 4px 12px;
        margin: 0.4rem 0;
        max-width: 85%;
        margin-left: auto;
        border: 1px solid rgba(74, 108, 247, 0.1);
        animation: slideInRight 0.25s ease-out;
        font-size: 0.9rem;
        line-height: 1.5;
    }
    .assistant-message {
        background: rgba(255,255,255,0.04);
        color: #d0d0d0 !important;
        padding: 0.8rem 1.2rem;
        border-radius: 12px 12px 12px 4px;
        margin: 0.4rem 0;
        max-width: 85%;
        margin-right: auto;
        border: 1px solid rgba(255,255,255,0.04);
        animation: slideInLeft 0.25s ease-out;
        font-size: 0.9rem;
        line-height: 1.5;
    }
    .assistant-message strong { color: #7c6cf7 !important; }
    @keyframes slideInRight {
        from { transform: translateX(20px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideInLeft {
        from { transform: translateX(-20px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    .source-citation {
        background: rgba(255,255,255,0.02);
        padding: 0.4rem 0.7rem;
        border-radius: 4px;
        border-left: 2px solid #4a6cf7;
        margin: 0.2rem 0;
        font-size: 0.78rem !important;
        color: rgba(255,255,255,0.5) !important;
    }
    .welcome-container {
        text-align: center;
        padding: 2rem 1rem;
    }
    .welcome-icon { font-size: 2.5rem; margin-bottom: 0.5rem; }
    .welcome-title {
        color: rgba(255,255,255,0.4) !important;
        font-size: 1.3rem !important;
        font-weight: 500 !important;
    }
    .welcome-text {
        color: rgba(255,255,255,0.25) !important;
        font-size: 0.85rem !important;
        max-width: 450px;
        margin: 0 auto;
        line-height: 1.5;
    }
    .stChatInput > div > div > input {
        background: rgba(255,255,255,0.04) !important;
        border-radius: 25px !important;
        padding: 0.6rem 1.2rem !important;
        border: 1px solid rgba(255,255,255,0.06) !important;
        color: #ffffff !important;
        font-size: 0.9rem !important;
    }
    .stChatInput > div > div > input::placeholder {
        color: rgba(255,255,255,0.2) !important;
    }
    .stButton > button {
        background: #4a6cf7;
        color: white !important;
        border: none;
        border-radius: 25px;
        padding: 0.4rem 1.2rem;
        font-weight: 500;
        font-size: 0.8rem;
        transition: all 0.2s ease;
        width: 100%;
        cursor: pointer;
    }
    .stButton > button:hover {
        background: #5a7cf7;
        box-shadow: 0 4px 15px rgba(74, 108, 247, 0.3);
    }
    .footer {
        text-align: center;
        padding: 1rem;
        color: rgba(255,255,255,0.1) !important;
        font-size: 0.65rem !important;
        border-top: 1px solid rgba(255,255,255,0.02);
        margin-top: 2rem;
    }
    .footer span { margin: 0 0.5rem; }
    .capability-card {
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(255,255,255,0.04);
        border-radius: 10px;
        padding: 1.2rem;
        transition: all 0.2s ease;
        height: 100%;
    }
    .capability-card:hover {
        background: rgba(255,255,255,0.04);
        border-color: rgba(255,255,255,0.08);
        transform: translateY(-2px);
    }
    .capability-icon { font-size: 1.5rem; margin-bottom: 0.5rem; }
    .capability-title {
        color: #ffffff !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        margin: 0.3rem 0;
    }
    .capability-desc {
        color: rgba(255,255,255,0.4) !important;
        font-size: 0.8rem !important;
        line-height: 1.4;
    }
    .flow-step {
        text-align: center;
        padding: 0.5rem;
        color: rgba(255,255,255,0.5);
        font-size: 0.8rem;
    }
    .flow-arrow {
        text-align: center;
        color: rgba(255,255,255,0.1);
        font-size: 1.2rem;
    }
    .trust-item {
        display: flex;
        align-items: center;
        padding: 0.3rem 0;
        color: rgba(255,255,255,0.4);
        font-size: 0.8rem;
    }
    .trust-item .check {
        color: #4caf50;
        margin-right: 0.5rem;
    }
    .example-prompt {
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(255,255,255,0.04);
        border-radius: 20px;
        padding: 0.4rem 1rem;
        color: rgba(255,255,255,0.3) !important;
        font-size: 0.8rem !important;
        cursor: pointer;
        transition: all 0.2s ease;
        display: inline-block;
        margin: 0.2rem;
    }
    .example-prompt:hover {
        background: rgba(255,255,255,0.04);
        border-color: rgba(255,255,255,0.08);
        color: rgba(255,255,255,0.6) !important;
    }
    .kb-status {
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(255,255,255,0.04);
        border-radius: 8px;
        padding: 0.6rem 0.8rem;
        margin: 0.5rem 0;
    }
    .kb-status .kb-label {
        color: rgba(255,255,255,0.3);
        font-size: 0.7rem;
    }
    .kb-status .kb-value {
        color: rgba(255,255,255,0.6);
        font-size: 0.75rem;
        font-weight: 500;
    }
    hr {
        border-color: rgba(255,255,255,0.04) !important;
        margin: 0.6rem 0 !important;
    }
    /* Issue Intelligence specific styles */
    .issue-card {
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(255,255,255,0.04);
        border-radius: 10px;
        padding: 1.2rem 1.5rem;
        margin: 0.6rem 0;
        transition: all 0.2s ease;
        position: relative;
        overflow: hidden;
    }
    .issue-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        border-radius: 4px 0 0 4px;
    }
    .issue-card-high::before { background: #f5576c; }
    .issue-card-medium::before { background: #f093fb; }
    .issue-card-low::before { background: #43e97b; }
    .issue-card:hover {
        background: rgba(255,255,255,0.04);
        border-color: rgba(255,255,255,0.08);
    }
    .issue-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        margin-bottom: 0.3rem;
    }
    .issue-name {
        color: #ffffff !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        margin: 0 !important;
    }
    .issue-badge {
        display: inline-block;
        padding: 0.15rem 0.6rem;
        border-radius: 12px;
        font-size: 0.65rem !important;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.3px;
    }
    .badge-high {
        background: rgba(245, 87, 108, 0.15);
        color: #f5576c !important;
        border: 1px solid rgba(245, 87, 108, 0.15);
    }
    .badge-medium {
        background: rgba(240, 147, 251, 0.15);
        color: #f093fb !important;
        border: 1px solid rgba(240, 147, 251, 0.15);
    }
    .badge-low {
        background: rgba(67, 233, 123, 0.15);
        color: #43e97b !important;
        border: 1px solid rgba(67, 233, 123, 0.15);
    }
    .issue-details {
        display: flex;
        flex-wrap: wrap;
        gap: 1.5rem;
        margin-top: 0.5rem;
    }
    .issue-detail-item {
        color: rgba(255,255,255,0.4) !important;
        font-size: 0.8rem !important;
    }
    .issue-detail-item strong {
        color: rgba(255,255,255,0.6) !important;
        font-weight: 500;
    }
    .issue-customers {
        display: flex;
        flex-wrap: wrap;
        gap: 0.3rem;
        margin-top: 0.3rem;
    }
    .customer-tag {
        background: rgba(255,255,255,0.04);
        padding: 0.1rem 0.6rem;
        border-radius: 12px;
        color: rgba(255,255,255,0.4) !important;
        font-size: 0.7rem !important;
        border: 1px solid rgba(255,255,255,0.04);
    }
    .investigation-container {
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(255,255,255,0.04);
        border-radius: 10px;
        padding: 1.2rem;
        margin: 0.8rem 0;
    }
    .investigation-title {
        color: #4facfe !important;
        font-size: 0.9rem !important;
        font-weight: 600 !important;
        margin: 0 0 0.5rem 0 !important;
    }
    .trend-up { color: #f5576c; }
    .trend-down { color: #43e97b; }
    .trend-stable { color: #f093fb; }
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 0.8rem;
        margin: 1rem 0;
    }
    @media (max-width: 768px) {
        .metric-grid { grid-template-columns: repeat(2, 1fr); }
    }
</style>
""",
    unsafe_allow_html=True,
)


# ==================== COMPONENT FUNCTIONS ====================


def render_header():
    """Render the application header."""
    session_duration = datetime.now() - st.session_state.session_start
    hours, remainder = divmod(session_duration.seconds, 3600)
    minutes, _ = divmod(remainder, 60)

    st.markdown(
        f"""
    <div class="header-container">
        <div class="header-content">
            <div>
                <div class="header-title">🚚 <span>ParcelPilot</span> AI Support Agent</div>
                <div class="header-subtitle">AI-powered internal support intelligence for logistics operations</div>
                <span class="header-status">● Online</span>
                <span style="color: rgba(255,255,255,0.2); font-size: 0.7rem; margin-left: 0.5rem;">
                    Session: {hours}h {minutes}m
                </span>
                <span style="color: rgba(255,255,255,0.15); font-size: 0.6rem; margin-left: 0.5rem; background: rgba(255,255,255,0.05); padding: 0.1rem 0.5rem; border-radius: 10px;">
                    {st.session_state.agent_mode} Agent
                </span>
            </div>
            <div class="header-time">
                <div>{datetime.now().strftime("%I:%M %p")}</div>
                <div style="font-size: 0.7rem; opacity: 0.6;">{datetime.now().strftime("%b %d, %Y")}</div>
                <div style="font-size: 0.6rem; opacity: 0.4; margin-top: 0.2rem;">
                    Queries: {st.session_state.query_count}
                </div>
            </div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )


def render_sidebar():
    """Render the navigation sidebar."""
    with st.sidebar:
        st.markdown(
            '<div class="sidebar-title">⚡ Navigation</div>', unsafe_allow_html=True
        )

        nav_items = [
            ("📊", "Overview"),
            ("💬", "AI Support Assistant"),
            ("🔍", "Issue Intelligence"),
            ("⚙️", "How It Works"),
            ("📋", "Activity"),
            ("ℹ️", "About"),
        ]

        for icon, label in nav_items:
            is_active = st.session_state.page == label
            if st.button(
                f"{icon} {label}",
                key=f"nav_{label}",
                use_container_width=True,
                type="secondary" if not is_active else "primary",
            ):
                st.session_state.page = label
                st.rerun()

        st.markdown("---")

        # Knowledge Base Status
        st.markdown(
            '<div class="sidebar-section-title">📚 Knowledge Base</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f"""
        <div class="kb-status">
            <div style="display: flex; justify-content: space-between;">
                <span class="kb-label">Documents Indexed</span>
                <span class="kb-value">{st.session_state.documents_indexed}</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-top: 0.2rem;">
                <span class="kb-label">Confidence Score</span>
                <span class="kb-value">{st.session_state.confidence_score}%</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-top: 0.2rem;">
                <span class="kb-label">Agent Mode</span>
                <span class="kb-value" style="color: #4facfe;">{st.session_state.agent_mode}</span>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        st.markdown("---")

        if st.session_state.agent_initialized:
            st.caption("✅ Agent Ready")
        else:
            if st.button("🔄 Initialize Agent", use_container_width=True):
                with st.spinner("Initializing..."):
                    init_agent()
                    st.rerun()

        st.markdown("---")
        st.caption("👤 **Support Agent**")
        st.caption("🔑 **Access:** Authorized Accounts")

        st.markdown("---")
        st.markdown(
            '<div class="sidebar-section-title">⚡ Quick Actions</div>',
            unsafe_allow_html=True,
        )

        if st.button("📄 View All Policies", use_container_width=True):
            st.session_state.page = "AI Support Assistant"
            st.session_state.messages.append(
                {
                    "role": "user",
                    "content": "Show me all current policies and agreements",
                }
            )
            st.rerun()

        if st.button("📊 View Dashboard", use_container_width=True):
            st.session_state.page = "Overview"
            st.rerun()


def render_welcome():
    """Render welcome message when no messages exist."""
    st.markdown(
        """
    <div class="welcome-container">
        <div class="welcome-icon">💬</div>
        <div class="welcome-title">How can I help you today?</div>
        <div class="welcome-text">
            Ask about policies, orders, customers, cancellations, service credits, or operational issues.
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
    <div style="text-align: center; padding: 0.5rem 0;">
        <div style="color: rgba(255,255,255,0.2); font-size: 0.7rem; margin-bottom: 0.3rem;">POLICY & AGREEMENTS</div>
        <span class="example-prompt">What is the cancellation policy?</span>
        <span class="example-prompt">Can Northstar cancel this order without a fee?</span>
        <span class="example-prompt">What are the SLA response times?</span>
    </div>
    <div style="text-align: center; padding: 0.3rem 0;">
        <div style="color: rgba(255,255,255,0.2); font-size: 0.7rem; margin-bottom: 0.3rem;">ORDERS & DATA</div>
        <span class="example-prompt">Check the status of ORD-1001</span>
        <span class="example-prompt">Show me all orders for Northstar</span>
        <span class="example-prompt">What tickets are open?</span>
    </div>
    <div style="text-align: center; padding: 0.3rem 0;">
        <div style="color: rgba(255,255,255,0.2); font-size: 0.7rem; margin-bottom: 0.3rem;">INVESTIGATION & ACTIONS</div>
        <span class="example-prompt">Should this ticket be escalated?</span>
        <span class="example-prompt">What's the service credit for LumenWorks?</span>
    </div>
    """,
        unsafe_allow_html=True,
    )


def render_chat_interface():
    """Render the main chat interface."""
    st.markdown(
        """
    <div style="margin-bottom: 0.5rem;">
        <h2 style="color: #ffffff; font-size: 1.3rem; font-weight: 600; margin: 0;">AI Support Assistant</h2>
        <p style="color: rgba(255,255,255,0.3); font-size: 0.8rem; margin: 0.2rem 0 0 0;">
            Ask questions about policies, orders, customers, and operational issues.
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    chat_container = st.container()

    with chat_container:
        if not st.session_state.messages:
            render_welcome()
        else:
            for message in st.session_state.messages:
                if message["role"] == "user":
                    st.markdown(
                        f'<div class="user-message">{message["content"]}</div>',
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f'<div class="assistant-message">{message["content"]}</div>',
                        unsafe_allow_html=True,
                    )
                    if "sources" in message and message["sources"]:
                        with st.expander("📚 Source Citations"):
                            for source in message["sources"]:
                                st.markdown(
                                    f'<div class="source-citation">✅ {source}</div>',
                                    unsafe_allow_html=True,
                                )

    if st.session_state.messages:
        if st.button("🗑️ Clear chat", type="secondary", key="clear_chat"):
            st.session_state.messages = []
            st.session_state.last_prompt = None
            st.rerun()

    prompt = st.chat_input("Ask ParcelPilot about policies, orders, or actions...")

    if (
        prompt
        and not st.session_state.processing
        and prompt != st.session_state.last_prompt
    ):
        st.session_state.processing = True
        st.session_state.last_prompt = prompt
        st.session_state.query_count += 1
        st.session_state.messages.append({"role": "user", "content": prompt})

        st.session_state.activity.append(
            {
                "time": datetime.now().strftime("%I:%M %p"),
                "action": "User Query",
                "detail": prompt[:50] + ("..." if len(prompt) > 50 else ""),
                "status": "Processing",
            }
        )

        try:
            thinking = st.empty()
            steps = [
                "🔍 Understanding your question...",
                "📚 Searching knowledge base...",
                "📊 Checking operational data...",
                "⚖️ Applying business rules...",
                "✅ Generating response...",
            ]

            for i, step in enumerate(steps):
                thinking.info(step)
                time.sleep(0.3)
            thinking.empty()

            if st.session_state.agent is None:
                init_agent()

            response = st.session_state.agent.process_query(prompt)

            sources = []
            if "📄 **Sources:**" in response:
                source_text = response.split("📄 **Sources:**")[1].strip()
                sources = [s.strip() for s in source_text.split(",") if s.strip()]

            st.session_state.messages.append(
                {"role": "assistant", "content": response, "sources": sources}
            )

            st.session_state.activity[-1]["status"] = "Completed"
            st.session_state.confidence_score = random.randint(82, 95)

        except Exception as e:
            st.error(f"⚠️ Error: {str(e)}")
            st.session_state.activity[-1]["status"] = "Failed"

        st.session_state.processing = False
        st.rerun()


def render_overview():
    """Render the Overview page."""
    st.markdown(
        """
    <div style="margin-bottom: 1.5rem;">
        <h1 style="color: #ffffff; font-size: 1.8rem; font-weight: 700; margin: 0;">Overview</h1>
        <p style="color: rgba(255,255,255,0.3); font-size: 0.9rem; margin: 0.2rem 0 0 0;">
            AI-powered internal support intelligence for faster, safer logistics operations.
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(
            """
        <div class="metric-card">
            <div class="metric-value success">●</div>
            <div class="metric-label">System Online</div>
        </div>
        """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"""
        <div class="metric-card">
            <div class="metric-value info">{st.session_state.documents_indexed}</div>
            <div class="metric-label">Documents Indexed</div>
        </div>
        """,
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f"""
        <div class="metric-card">
            <div class="metric-value warning">{st.session_state.query_count}</div>
            <div class="metric-label">Queries Processed</div>
        </div>
        """,
            unsafe_allow_html=True,
        )
    with col4:
        st.markdown(
            f"""
        <div class="metric-card">
            <div class="metric-value" style="color: #4facfe;">{st.session_state.confidence_score}%</div>
            <div class="metric-label">Avg Confidence</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    st.markdown(
        """
    <h3 style="color: rgba(255,255,255,0.6); font-size: 1rem; font-weight: 600; margin: 1.5rem 0 0.8rem 0;">What Can It Do?</h3>
    """,
        unsafe_allow_html=True,
    )

    cols = st.columns(4)
    capabilities = [
        (
            "🔍",
            "Ask & Retrieve",
            "Search policies, SOPs, product guides and customer agreements.",
        ),
        ("📊", "Investigate", "Combine documents, orders, tickets and account data."),
        ("⚖️", "Decide", "Resolve conflicts between policies and customer agreements."),
        (
            "🛡️",
            "Act Safely",
            "Propose actions and require confirmation before changing state.",
        ),
    ]

    for col, (icon, title, desc) in zip(cols, capabilities):
        with col:
            st.markdown(
                f"""
            <div class="capability-card">
                <div class="capability-icon">{icon}</div>
                <div class="capability-title">{title}</div>
                <div class="capability-desc">{desc}</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

    st.markdown("---")

    st.markdown(
        """
    <h3 style="color: rgba(255,255,255,0.6); font-size: 1rem; font-weight: 600; margin: 2rem 0 0.8rem 0;">How It Works</h3>
    """,
        unsafe_allow_html=True,
    )

    flow_steps = [
        "💬 User Question",
        "🧠 AI Agent",
        "📄 Retrieve Evidence",
        "📊 Query Operational Data",
        "⚖️ Apply Business Rules",
        "✅ Generate Decision",
        "🛡️ Propose Action",
        "👤 Human Confirmation",
    ]

    for i, step in enumerate(flow_steps):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(
                f'<div class="flow-step" style="text-align: left; padding: 0.3rem 0;">{step}</div>',
                unsafe_allow_html=True,
            )
        with col2:
            if i < len(flow_steps) - 1:
                st.markdown('<div class="flow-arrow">↓</div>', unsafe_allow_html=True)

    st.markdown("---")

    st.markdown(
        """
    <h3 style="color: rgba(255,255,255,0.6); font-size: 1rem; font-weight: 600; margin: 2rem 0 0.8rem 0;">Trust & Safety</h3>
    """,
        unsafe_allow_html=True,
    )

    trust_items = [
        "Source-aware answers with citations",
        "Customer agreement priority over general policies",
        "Current policy priority over deprecated versions",
        "Role-based access control",
        "Human confirmation before state-changing actions",
        "Audit-friendly activity logging",
        "No unsupported assumptions",
    ]

    cols = st.columns(2)
    for i, item in enumerate(trust_items):
        with cols[i % 2]:
            st.markdown(
                f'<div class="trust-item"><span class="check">✓</span> {item}</div>',
                unsafe_allow_html=True,
            )


def render_issue_intelligence():
    """Render the Issue Intelligence page with complete functionality."""
    st.markdown(
        """
    <div style="margin-bottom: 1.5rem;">
        <h1 style="color: #ffffff; font-size: 1.8rem; font-weight: 700; margin: 0;">🔍 Issue Intelligence</h1>
        <p style="color: rgba(255,255,255,0.3); font-size: 0.9rem; margin: 0.2rem 0 0 0;">
            Detect recurring operational problems and investigate their likely causes using support data and product knowledge.
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Data
    issues = {
        "Pickup Delay": {
            "tickets": 24,
            "severity": "HIGH",
            "affected_customers": ["Northstar", "LumenWorks"],
            "root_cause": "Carrier X integration issue",
            "recommendation": "Escalate to operations team",
            "trend": "↑ increasing",
            "trend_percentage": 12,
            "first_detected": "2026-08-10",
            "last_updated": "2026-08-24",
            "avg_resolution_time": "4.2 hours",
            "sla_impact": "Critical",
        },
        "Label Generation": {
            "tickets": 18,
            "severity": "MEDIUM",
            "affected_customers": ["LumenWorks"],
            "root_cause": "API rate limiting",
            "recommendation": "Increase API limits",
            "trend": "→ stable",
            "trend_percentage": 2,
            "first_detected": "2026-08-15",
            "last_updated": "2026-08-24",
            "avg_resolution_time": "2.8 hours",
            "sla_impact": "High",
        },
        "Carrier Integration": {
            "tickets": 15,
            "severity": "HIGH",
            "affected_customers": ["Northstar"],
            "root_cause": "Authentication failure",
            "recommendation": "Update API credentials",
            "trend": "↓ decreasing",
            "trend_percentage": -8,
            "first_detected": "2026-08-18",
            "last_updated": "2026-08-24",
            "avg_resolution_time": "3.5 hours",
            "sla_impact": "Critical",
        },
        "Cancellation": {
            "tickets": 11,
            "severity": "LOW",
            "affected_customers": ["Northstar"],
            "root_cause": "Customer confusion",
            "recommendation": "Update cancellation FAQ",
            "trend": "→ stable",
            "trend_percentage": 1,
            "first_detected": "2026-08-20",
            "last_updated": "2026-08-24",
            "avg_resolution_time": "1.5 hours",
            "sla_impact": "Low",
        },
    }

    # Metrics
    total_tickets = sum(i["tickets"] for i in issues.values())
    high_severity = sum(1 for i in issues.values() if i["severity"] == "HIGH")
    increasing = sum(1 for i in issues.values() if "↑" in i["trend"])
    avg_tickets = total_tickets / len(issues)

    st.markdown('<div class="metric-grid">', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(
            f"""
        <div class="metric-card">
            <div class="metric-value info">{len(issues)}</div>
            <div class="metric-label">Total Issues</div>
        </div>
        """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"""
        <div class="metric-card">
            <div class="metric-value danger">{high_severity}</div>
            <div class="metric-label">High Severity</div>
        </div>
        """,
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f"""
        <div class="metric-card">
            <div class="metric-value warning">{total_tickets}</div>
            <div class="metric-label">Affected Tickets</div>
        </div>
        """,
            unsafe_allow_html=True,
        )
    with col4:
        st.markdown(
            f"""
        <div class="metric-card">
            <div class="metric-value success">{increasing}</div>
            <div class="metric-label">Trending Up</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")

    # Filter
    col1, col2 = st.columns([3, 1])
    with col1:
        search_term = st.text_input(
            "🔎 Filter Issues",
            placeholder="Search for specific issues...",
            label_visibility="collapsed",
        )
    with col2:
        severity_filter = st.selectbox(
            "Severity", ["All", "HIGH", "MEDIUM", "LOW"], label_visibility="collapsed"
        )

    # Issues List
    for issue_name, details in issues.items():
        if search_term and search_term.lower() not in issue_name.lower():
            continue
        if severity_filter != "All" and details["severity"] != severity_filter:
            continue

        severity_class = (
            "issue-card-high"
            if details["severity"] == "HIGH"
            else "issue-card-medium"
            if details["severity"] == "MEDIUM"
            else "issue-card-low"
        )
        badge_class = (
            "badge-high"
            if details["severity"] == "HIGH"
            else "badge-medium"
            if details["severity"] == "MEDIUM"
            else "badge-low"
        )
        severity_icon = (
            "🔴"
            if details["severity"] == "HIGH"
            else "🟠"
            if details["severity"] == "MEDIUM"
            else "🟡"
        )

        if "↑" in details["trend"]:
            trend_icon = "📈"
            trend_class = "trend-up"
        elif "↓" in details["trend"]:
            trend_icon = "📉"
            trend_class = "trend-down"
        else:
            trend_icon = "➡️"
            trend_class = "trend-stable"

        with st.container():
            st.markdown(
                f"""
            <div class="issue-card {severity_class}">
                <div class="issue-header">
                    <div class="issue-name">{severity_icon} {issue_name}</div>
                    <div style="display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap;">
                        <span class="issue-badge {badge_class}">{details["severity"]}</span>
                        <span class="{trend_class}" style="font-size: 0.8rem;">{trend_icon} {details["trend"]}</span>
                        <span style="color: rgba(255,255,255,0.2); font-size: 0.7rem;">{details["trend_percentage"]}%</span>
                    </div>
                </div>
                <div class="issue-details">
                    <span class="issue-detail-item">
                        <strong>Tickets:</strong> <span class="value">{details["tickets"]}</span>
                    </span>
                    <span class="issue-detail-item">
                        <strong>First Detected:</strong> <span class="value">{details["first_detected"]}</span>
                    </span>
                    <span class="issue-detail-item">
                        <strong>Avg Resolution:</strong> <span class="value">{details["avg_resolution_time"]}</span>
                    </span>
                    <span class="issue-detail-item">
                        <strong>SLA Impact:</strong> <span class="value">{details["sla_impact"]}</span>
                    </span>
                </div>
                <div class="issue-customers">
                    <span style="color: rgba(255,255,255,0.3); font-size: 0.7rem; margin-right: 0.3rem;">Affected:</span>
                    {"".join([f'<span class="customer-tag">{c}</span>' for c in details["affected_customers"]])}
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

            col1, col2 = st.columns([3, 1])
            with col1:
                st.info(f"💡 **Root Cause:** {details['root_cause']}")
                st.success(f"✅ **Recommendation:** {details['recommendation']}")
            with col2:
                if st.button(
                    "🔍 Investigate",
                    key=f"invest_{issue_name}",
                    use_container_width=True,
                ):
                    with st.spinner(f"Analyzing {issue_name}..."):
                        if st.session_state.agent is None:
                            init_agent()

                        response = st.session_state.agent.investigate_issue(
                            issue_name, details
                        )

                        st.session_state.investigation_results[issue_name] = {
                            "timestamp": datetime.now().strftime("%I:%M %p"),
                            "response": response,
                            "issue_data": details,
                        }

                        st.session_state.investigation_timeline.append(
                            {
                                "time": datetime.now().strftime("%I:%M %p"),
                                "issue": issue_name,
                                "status": "Completed",
                            }
                        )

                        st.success("✅ Investigation complete!")
                        st.rerun()

            if issue_name in st.session_state.investigation_results:
                result = st.session_state.investigation_results[issue_name]
                with st.expander("📋 Investigation Results", expanded=True):
                    st.markdown(
                        f"""
                    <div class="investigation-container">
                        <div class="investigation-title">🔍 Investigation Summary</div>
                        <div style="color: rgba(255,255,255,0.6); font-size: 0.85rem; line-height: 1.6;">
                            {result["response"]}
                        </div>
                        <div style="display: flex; gap: 1rem; margin-top: 0.8rem; flex-wrap: wrap;">
                            <div style="background: rgba(255,255,255,0.02); padding: 0.3rem 0.6rem; border-radius: 4px; border: 1px solid rgba(255,255,255,0.04);">
                                <span style="color: rgba(255,255,255,0.2); font-size: 0.6rem;">Investigated</span>
                                <span style="color: rgba(255,255,255,0.4); font-size: 0.7rem; margin-left: 0.3rem;">{result["timestamp"]}</span>
                            </div>
                            <div style="background: rgba(255,255,255,0.02); padding: 0.3rem 0.6rem; border-radius: 4px; border: 1px solid rgba(255,255,255,0.04);">
                                <span style="color: rgba(255,255,255,0.2); font-size: 0.6rem;">Status</span>
                                <span style="color: #43e97b; font-size: 0.7rem; margin-left: 0.3rem;">✓ Completed</span>
                            </div>
                        </div>
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )

            st.markdown("---")

    # Timeline
    if st.session_state.investigation_timeline:
        st.markdown(
            """
        <h3 style="color: rgba(255,255,255,0.6); font-size: 1rem; font-weight: 600; margin: 1rem 0 0.8rem 0;">📋 Investigation Timeline</h3>
        """,
            unsafe_allow_html=True,
        )

        for item in reversed(st.session_state.investigation_timeline[-10:]):
            st.markdown(
                f"""
            <div style="display: flex; align-items: center; padding: 0.3rem 0; border-bottom: 1px solid rgba(255,255,255,0.02);">
                <span style="color: rgba(255,255,255,0.2); font-size: 0.65rem; min-width: 60px;">{item["time"]}</span>
                <span style="width: 8px; height: 8px; border-radius: 50%; background: #43e97b; margin: 0 0.8rem;"></span>
                <span style="color: rgba(255,255,255,0.4); font-size: 0.8rem;">
                    <strong style="color: rgba(255,255,255,0.6);">Investigated</strong> {item["issue"]}
                </span>
            </div>
            """,
                unsafe_allow_html=True,
            )

        if st.button("Clear Timeline", type="secondary"):
            st.session_state.investigation_timeline = []
            st.rerun()


def render_how_it_works():
    """Render the How It Works page."""
    st.markdown(
        """
    <div style="margin-bottom: 1.5rem;">
        <h1 style="color: #ffffff; font-size: 1.8rem; font-weight: 700; margin: 0;">How ParcelPilot Works</h1>
        <p style="color: rgba(255,255,255,0.3); font-size: 0.9rem; margin: 0.2rem 0 0 0;">
            Understanding the AI-powered support intelligence system.
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    flow = [
        ("1. USER QUESTION", "The user asks a natural-language question."),
        (
            "2. AI AGENT",
            "The agent determines what information and tools are required.",
        ),
        (
            "3. DOCUMENT RETRIEVAL",
            "Relevant policies, SOPs, agreements and product documents are retrieved.",
        ),
        (
            "4. STRUCTURED DATA",
            "The agent checks operational data such as orders, customers and tickets.",
        ),
        (
            "5. BUSINESS REASONING",
            "The system compares evidence and applies source priority.",
        ),
        ("6. DECISION", "The agent produces an evidence-based answer."),
        (
            "7. SAFE ACTION",
            "If an action is required, the system asks the user for confirmation.",
        ),
    ]

    for title, desc in flow:
        st.markdown(
            f"""
        <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.04); border-radius: 8px; padding: 0.8rem 1rem; margin: 0.4rem 0;">
            <div style="color: #ffffff; font-weight: 600; font-size: 0.9rem;">{title}</div>
            <div style="color: rgba(255,255,255,0.4); font-size: 0.8rem; margin-top: 0.2rem;">{desc}</div>
        </div>
        """,
            unsafe_allow_html=True,
        )


def render_about():
    """Render the About page."""
    st.markdown(
        """
    <div style="margin-bottom: 1.5rem;">
        <h1 style="color: #ffffff; font-size: 1.8rem; font-weight: 700; margin: 0;">About ParcelPilot</h1>
        <p style="color: rgba(255,255,255,0.3); font-size: 0.9rem; margin: 0.2rem 0 0 0;">
            The AI support intelligence platform for logistics operations.
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
        <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.04); border-radius: 10px; padding: 1.5rem; margin: 0.5rem 0;">
            <h3 style="color: #ffffff; font-size: 1.1rem; font-weight: 600; margin: 0 0 0.5rem 0;">The Problem</h3>
            <p style="color: rgba(255,255,255,0.4); font-size: 0.9rem; line-height: 1.6; margin: 0;">
                Support teams often need to search multiple documents, customer agreements, operational records,
                and ticket histories before making a decision. This manual process is time-consuming and error-prone.
            </p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
        <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.04); border-radius: 10px; padding: 1.5rem; margin: 0.5rem 0;">
            <h3 style="color: #ffffff; font-size: 1.1rem; font-weight: 600; margin: 0 0 0.5rem 0;">The Solution</h3>
            <p style="color: rgba(255,255,255,0.4); font-size: 0.9rem; line-height: 1.6; margin: 0;">
                ParcelPilot provides one AI interface that combines trusted documents, structured operational data,
                and controlled actions. It brings relevant evidence together and explains the reasoning behind each decision.
            </p>
        </div>
        """,
            unsafe_allow_html=True,
        )


def render_activity():
    """Render the Activity/Audit page."""
    st.markdown(
        """
    <div style="margin-bottom: 1.5rem;">
        <h1 style="color: #ffffff; font-size: 1.8rem; font-weight: 700; margin: 0;">Activity</h1>
        <p style="color: rgba(255,255,255,0.3); font-size: 0.9rem; margin: 0.2rem 0 0 0;">
            Audit log of agent actions and user interactions.
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    total_actions = len(st.session_state.activity)
    completed = sum(1 for a in st.session_state.activity if a["status"] == "Completed")
    failed = sum(1 for a in st.session_state.activity if a["status"] == "Failed")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            f"""
        <div class="metric-card">
            <div class="metric-value info">{total_actions}</div>
            <div class="metric-label">Total Actions</div>
        </div>
        """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"""
        <div class="metric-card">
            <div class="metric-value success">{completed}</div>
            <div class="metric-label">Completed</div>
        </div>
        """,
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f"""
        <div class="metric-card">
            <div class="metric-value danger">{failed}</div>
            <div class="metric-label">Failed</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    if not st.session_state.activity:
        st.markdown(
            """
        <div style="text-align: center; padding: 3rem 1rem;">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">📋</div>
            <div style="color: rgba(255,255,255,0.3); font-size: 1rem;">No activity recorded yet</div>
            <div style="color: rgba(255,255,255,0.15); font-size: 0.8rem;">Start using the AI Support Assistant to see activity here.</div>
        </div>
        """,
            unsafe_allow_html=True,
        )
    else:
        for entry in reversed(st.session_state.activity[-20:]):
            status_color = (
                "#4caf50"
                if entry["status"] == "Completed"
                else "#ffc107"
                if entry["status"] == "Processing"
                else "#f5576c"
            )
            st.markdown(
                f"""
            <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.04); border-radius: 6px; padding: 0.6rem 0.8rem; margin: 0.3rem 0; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                <div style="display: flex; align-items: center; gap: 1rem; flex-wrap: wrap;">
                    <div style="color: rgba(255,255,255,0.3); font-size: 0.7rem; min-width: 60px;">{entry["time"]}</div>
                    <div style="color: #ffffff; font-size: 0.85rem; font-weight: 500;">{entry["action"]}</div>
                    <div style="color: rgba(255,255,255,0.3); font-size: 0.7rem;">{entry["detail"]}</div>
                </div>
                <div>
                    <span style="color: {status_color}; font-size: 0.7rem;">● {entry["status"]}</span>
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        if st.button("Clear Activity Log", type="secondary"):
            st.session_state.activity = []
            st.rerun()


# ==================== MAIN APP ====================


def main():
    """Main application entry point."""
    render_header()
    render_sidebar()

    if st.session_state.page == "Overview":
        render_overview()
    elif st.session_state.page == "AI Support Assistant":
        if st.session_state.agent_initialized or init_agent():
            render_chat_interface()
        else:
            st.warning("Please initialize the agent to use the chat interface.")
    elif st.session_state.page == "Issue Intelligence":
        if st.session_state.agent_initialized or init_agent():
            render_issue_intelligence()
        else:
            st.warning("Please initialize the agent to use issue intelligence.")
    elif st.session_state.page == "How It Works":
        render_how_it_works()
    elif st.session_state.page == "Activity":
        render_activity()
    elif st.session_state.page == "About":
        render_about()

    st.markdown(
        """
    <div class="footer">
        <span>🚚 ParcelPilot AI Support Agent</span>
        <span>•</span>
        <span>v1.0</span>
        <span>•</span>
        <span>Enterprise Edition</span>
        <span>•</span>
        <span>© 2026</span>
    </div>
    """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
