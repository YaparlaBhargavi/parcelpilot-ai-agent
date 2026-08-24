# app.py
import streamlit as st
import os
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

# ==================== CUSTOM CSS ====================
st.markdown(
    """
<style>
    /* ===== GLOBAL ===== */
    .stApp {
        background: #0a0e17;
    }

    /* ===== HEADER ===== */
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

    /* ===== SIDEBAR ===== */
    .css-1d391kg {
        background: #0a0e17;
        border-right: 1px solid rgba(255,255,255,0.04);
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

    .sidebar-nav-item {
        display: flex;
        align-items: center;
        padding: 0.6rem 0.8rem;
        border-radius: 8px;
        color: rgba(255,255,255,0.5) !important;
        text-decoration: none;
        transition: all 0.2s ease;
        cursor: pointer;
        margin: 0.2rem 0;
        font-size: 0.9rem;
        border: none;
        background: transparent;
        width: 100%;
        text-align: left;
    }

    .sidebar-nav-item:hover {
        background: rgba(255,255,255,0.05);
        color: #ffffff !important;
    }

    .sidebar-nav-item.active {
        background: rgba(74, 108, 247, 0.12);
        color: #4a6cf7 !important;
        border-left: 3px solid #4a6cf7;
    }

    .sidebar-nav-item .icon {
        margin-right: 0.8rem;
        font-size: 1.1rem;
    }

    .sidebar-section-title {
        color: rgba(255,255,255,0.3) !important;
        font-size: 0.65rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        padding: 0.8rem 0 0.4rem 0;
    }

    /* ===== METRICS ===== */
    .metric-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 0.5rem;
        margin: 0.5rem 0;
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

    /* ===== ISSUES ===== */
    .issue-item {
        background: rgba(255,255,255,0.02);
        padding: 0.35rem 0.5rem;
        border-radius: 6px;
        margin: 0.15rem 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-left: 2px solid;
        transition: all 0.2s ease;
    }

    .issue-item:hover {
        background: rgba(255,255,255,0.04);
    }

    .issue-name {
        color: rgba(255,255,255,0.6) !important;
        font-size: 0.78rem !important;
    }

    .issue-count {
        background: rgba(255,255,255,0.06);
        padding: 0.05rem 0.5rem;
        border-radius: 12px;
        color: rgba(255,255,255,0.5) !important;
        font-weight: 500;
        font-size: 0.7rem !important;
    }

    /* ===== PRIORITY ===== */
    .priority-item {
        display: flex;
        justify-content: space-between;
        padding: 0.2rem 0;
        font-size: 0.75rem !important;
        color: rgba(255,255,255,0.4) !important;
        border-bottom: 1px solid rgba(255,255,255,0.02);
    }

    .priority-value {
        font-weight: 500;
        color: #4a6cf7 !important;
    }

    /* ===== CHAT MESSAGES ===== */
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
    .assistant-message h1, .assistant-message h2, .assistant-message h3 {
        color: #7c6cf7 !important;
    }

    @keyframes slideInRight {
        from { transform: translateX(20px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }

    @keyframes slideInLeft {
        from { transform: translateX(-20px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }

    /* ===== SOURCE CITATIONS ===== */
    .source-citation {
        background: rgba(255,255,255,0.02);
        padding: 0.4rem 0.7rem;
        border-radius: 4px;
        border-left: 2px solid #4a6cf7;
        margin: 0.2rem 0;
        font-size: 0.78rem !important;
        color: rgba(255,255,255,0.5) !important;
    }

    /* ===== WELCOME ===== */
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

    /* ===== CHAT INPUT ===== */
    .stTextInput > div > div > input {
        background: rgba(255,255,255,0.04) !important;
        border-radius: 25px !important;
        padding: 0.6rem 1.2rem !important;
        border: 1px solid rgba(255,255,255,0.06) !important;
        color: #ffffff !important;
        font-size: 0.9rem !important;
    }

    .stTextInput > div > div > input::placeholder {
        color: rgba(255,255,255,0.2) !important;
    }

    .stTextInput > div > div > input:focus {
        border-color: rgba(74, 108, 247, 0.3) !important;
        background: rgba(255,255,255,0.06) !important;
        box-shadow: 0 0 0 3px rgba(74, 108, 247, 0.05);
    }

    /* ===== BUTTONS ===== */
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

    .stButton > button:active { transform: scale(0.97); }

    .button-secondary > button {
        background: rgba(255,255,255,0.06);
        color: rgba(255,255,255,0.6) !important;
    }

    .button-secondary > button:hover {
        background: rgba(255,255,255,0.1);
    }

    /* ===== EXPANDER ===== */
    .streamlit-expanderHeader {
        background: rgba(255,255,255,0.02) !important;
        border-radius: 8px !important;
        color: rgba(255,255,255,0.4) !important;
        border: 1px solid rgba(255,255,255,0.04);
        font-size: 0.8rem !important;
    }

    .streamlit-expanderHeader:hover {
        background: rgba(255,255,255,0.04) !important;
    }

    /* ===== DIVIDER ===== */
    hr {
        border-color: rgba(255,255,255,0.04) !important;
        margin: 0.6rem 0 !important;
    }

    /* ===== FOOTER ===== */
    .footer {
        text-align: center;
        padding: 1rem;
        color: rgba(255,255,255,0.1) !important;
        font-size: 0.65rem !important;
        border-top: 1px solid rgba(255,255,255,0.02);
        margin-top: 2rem;
    }

    .footer span { margin: 0 0.5rem; }

    /* ===== CARDS ===== */
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

    /* ===== FLOW DIAGRAM ===== */
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

    /* ===== TRUST ITEM ===== */
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

    /* ===== CONFLICT ALERT ===== */
    .conflict-alert {
        background: rgba(245, 87, 108, 0.06);
        border-left: 3px solid #f5576c;
        padding: 0.6rem 1rem;
        border-radius: 6px;
        margin: 0.4rem 0;
        color: rgba(255,255,255,0.7);
        font-size: 0.85rem;
    }
    .conflict-alert strong { color: #f5576c; }

    /* ===== ACTION CONFIRMATION ===== */
    .action-confirm {
        background: rgba(255, 193, 7, 0.06);
        border-left: 3px solid #ffc107;
        padding: 0.8rem 1rem;
        border-radius: 6px;
        margin: 0.4rem 0;
    }
    .action-confirm .title {
        color: #ffc107;
        font-weight: 600;
        font-size: 0.9rem;
    }
    .action-confirm .detail {
        color: rgba(255,255,255,0.5);
        font-size: 0.8rem;
        margin: 0.2rem 0;
    }

    /* ===== EXAMPLE PROMPTS ===== */
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

    /* ===== KNOWLEDGE BASE STATUS ===== */
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

    /* ===== SESSION TIMER ===== */
    .session-timer {
        color: rgba(255,255,255,0.2);
        font-size: 0.7rem;
        text-align: center;
        padding: 0.3rem 0;
    }
</style>
""",
    unsafe_allow_html=True,
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
        st.session_state.page = "Overview"
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


initialize_session_state()


# ==================== AGENT INIT ====================
def init_agent():
    """Initialize the agent with error handling."""
    if not st.session_state.agent_initialized:
        try:
            from src.agent import ParcelPilotAgent

            user_context = {
                "role": "support_agent",
                "user_id": "demo_user",
                "supported_accounts": ["Northstar", "LumenWorks", "Beacon Retail"],
            }
            st.session_state.agent = ParcelPilotAgent(user_context)
            st.session_state.agent_initialized = True
            return True
        except Exception as e:
            st.error(f"⚠️ Agent initialization failed: {str(e)}")
            return False
    return True


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

        # ===== KNOWLEDGE BASE STATUS =====
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
                <span class="kb-label">Source Priority</span>
                <span class="kb-value" style="color: #4facfe;">Active</span>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        st.markdown("---")

        # ===== AGENT STATUS =====
        if st.session_state.agent_initialized:
            st.caption("✅ Agent Ready")
        else:
            if st.button("🔄 Initialize Agent", use_container_width=True):
                with st.spinner("Initializing..."):
                    init_agent()
                    st.rerun()

        # Session info
        st.markdown("---")
        st.caption("👤 **Support Agent**")
        st.caption("🔑 **Access:** Authorized Accounts")

        # Quick Actions
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

    # Example prompts with categories
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
        <span class="example-prompt">Investigate carrier integration issues</span>
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

    # Input
    if not st.session_state.processing:
        col1, col2 = st.columns([6, 1])
        with col1:
            prompt = st.chat_input(
                "Ask ParcelPilot about policies, orders, or actions..."
            )
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Clear", use_container_width=True, type="secondary"):
                st.session_state.messages = []
                st.rerun()

        if prompt:
            st.session_state.processing = True
            st.session_state.query_count += 1
            st.session_state.messages.append({"role": "user", "content": prompt})

            # Log activity
            st.session_state.activity.append(
                {
                    "time": datetime.now().strftime("%I:%M %p"),
                    "action": "User Query",
                    "detail": prompt[:50] + ("..." if len(prompt) > 50 else ""),
                    "status": "Processing",
                }
            )

            try:
                with st.spinner("Analyzing..."):
                    # Show thinking steps
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

                    response = st.session_state.agent.process_query(prompt)

                    sources = []
                    if "Sources:" in response:
                        source_lines = response.split("Sources:")[1].strip().split("\n")
                        for line in source_lines:
                            if line.startswith("✓"):
                                sources.append(line.replace("✓", "").strip())

                    st.session_state.messages.append(
                        {"role": "assistant", "content": response, "sources": sources}
                    )

                    # Update activity
                    st.session_state.activity[-1]["status"] = "Completed"

                    # Update confidence score (simulate)
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

    # ===== SYSTEM STATUS =====
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

    # ===== WHAT CAN IT DO =====
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

    # ===== HOW IT WORKS =====
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

    # ===== TRUST & SAFETY =====
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

    # ===== FLOW =====
    st.markdown(
        """
    <h3 style="color: rgba(255,255,255,0.6); font-size: 1rem; font-weight: 600; margin: 1rem 0 0.8rem 0;">The Intelligence Pipeline</h3>
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

    # ===== SOURCE PRIORITY =====
    st.markdown(
        """
    <h3 style="color: rgba(255,255,255,0.6); font-size: 1rem; font-weight: 600; margin: 2rem 0 0.8rem 0;">Evidence Priority System</h3>
    """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
    <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.04); border-radius: 8px; padding: 1rem;">
        <div style="display: flex; flex-direction: column; gap: 0.3rem;">
            <div style="display: flex; justify-content: space-between; padding: 0.3rem 0.5rem; background: rgba(74, 108, 247, 0.1); border-radius: 4px; border-left: 3px solid #4a6cf7;">
                <span style="color: #ffffff;">📄 Customer Agreement</span>
                <span style="color: #4a6cf7; font-weight: 600;">Highest Priority</span>
            </div>
            <div style="display: flex; justify-content: space-between; padding: 0.3rem 0.5rem; background: rgba(79, 172, 254, 0.08); border-radius: 4px; border-left: 3px solid #4facfe;">
                <span style="color: rgba(255,255,255,0.8);">📋 Current Policy</span>
                <span style="color: #4facfe; font-weight: 600;">High Priority</span>
            </div>
            <div style="display: flex; justify-content: space-between; padding: 0.3rem 0.5rem; background: rgba(240, 147, 251, 0.08); border-radius: 4px; border-left: 3px solid #f093fb;">
                <span style="color: rgba(255,255,255,0.8);">📑 Current SOP</span>
                <span style="color: #f093fb; font-weight: 600;">Medium-High</span>
            </div>
            <div style="display: flex; justify-content: space-between; padding: 0.3rem 0.5rem; background: rgba(255,255,255,0.03); border-radius: 4px; border-left: 3px solid rgba(255,255,255,0.1);">
                <span style="color: rgba(255,255,255,0.5);">📖 Product Guide</span>
                <span style="color: rgba(255,255,255,0.3); font-weight: 600;">Medium</span>
            </div>
            <div style="display: flex; justify-content: space-between; padding: 0.3rem 0.5rem; background: rgba(245, 87, 108, 0.05); border-radius: 4px; border-left: 3px solid rgba(245, 87, 108, 0.3);">
                <span style="color: rgba(255,255,255,0.3);">📕 Deprecated Policy</span>
                <span style="color: rgba(245, 87, 108, 0.3); font-weight: 600;">Low Priority</span>
            </div>
        </div>
        <div style="color: rgba(255,255,255,0.2); font-size: 0.7rem; margin-top: 0.5rem; text-align: center;">
            Customer-specific agreements can override general policies.
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # ===== ARCHITECTURE =====
    st.markdown(
        """
    <h3 style="color: rgba(255,255,255,0.6); font-size: 1rem; font-weight: 600; margin: 2rem 0 0.8rem 0;">Technical Architecture</h3>
    """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
    <style>
        .arch-container {
            background: rgba(255,255,255,0.02);
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 10px;
            padding: 1.5rem;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 0;
        }
        .arch-box {
            background: rgba(74, 108, 247, 0.08);
            border: 1px solid rgba(74, 108, 247, 0.3);
            border-radius: 8px;
            padding: 0.7rem 1.4rem;
            text-align: center;
            width: 100%;
            max-width: 420px;
        }
        .arch-box-title {
            color: #ffffff;
            font-size: 0.85rem;
            font-weight: 600;
        }
        .arch-box-sub {
            color: rgba(255,255,255,0.4);
            font-size: 0.7rem;
            margin-top: 0.15rem;
        }
        .arch-arrow {
            color: rgba(255,255,255,0.25);
            font-size: 1.1rem;
            line-height: 1;
            padding: 0.3rem 0;
        }
        .arch-parallel-row {
            display: flex;
            gap: 1rem;
            width: 100%;
            max-width: 420px;
            justify-content: center;
        }
        .arch-parallel-row .arch-box {
            max-width: none;
            flex: 1;
        }
        .arch-sub-box {
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 6px;
            padding: 0.5rem 0.8rem;
            text-align: center;
            flex: 1;
        }
        .arch-sub-box-title {
            color: rgba(255,255,255,0.75);
            font-size: 0.78rem;
            font-weight: 600;
        }
        .arch-sub-box-sub {
            color: rgba(255,255,255,0.35);
            font-size: 0.65rem;
            margin-top: 0.1rem;
        }
    </style>

    <div class="arch-container">
        <div class="arch-box">
            <div class="arch-box-title">🖥️ Streamlit UI</div>
            <div class="arch-box-sub">Overview · Chat · Issue Intelligence</div>
        </div>
        <div class="arch-arrow">▼</div>
        <div class="arch-box">
            <div class="arch-box-title">🧠 AI Agent / Orchestrator</div>
            <div class="arch-box-sub">Intent Detection · Reasoning</div>
        </div>
        <div class="arch-arrow">▼</div>
        <div class="arch-parallel-row">
            <div class="arch-sub-box">
                <div class="arch-sub-box-title">📄 RAG Search</div>
                <div class="arch-sub-box-sub">FAISS Vector DB</div>
            </div>
            <div class="arch-sub-box">
                <div class="arch-sub-box-title">📊 Data Tools</div>
                <div class="arch-sub-box-sub">SQLite / Pandas</div>
            </div>
        </div>
        <div class="arch-arrow">▼</div>
        <div class="arch-box">
            <div class="arch-box-title">🛡️ Security / Authorization</div>
            <div class="arch-box-sub">Role-Based Access Control</div>
        </div>
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

        st.markdown(
            """
        <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.04); border-radius: 10px; padding: 1.5rem; margin: 0.5rem 0;">
            <h3 style="color: #ffffff; font-size: 1.1rem; font-weight: 600; margin: 0 0 0.5rem 0;">Why It Matters</h3>
            <p style="color: rgba(255,255,255,0.4); font-size: 0.9rem; line-height: 1.6; margin: 0;">
                Instead of forcing support agents to manually search multiple systems, ParcelPilot brings relevant
                evidence together and explains the reasoning behind each decision. This enables faster, more accurate
                support with complete transparency.
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

        st.markdown(
            """
        <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.04); border-radius: 10px; padding: 1.5rem; margin: 0.5rem 0;">
            <h3 style="color: #ffffff; font-size: 1.1rem; font-weight: 600; margin: 0 0 0.5rem 0;">Project Metrics</h3>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem;">
                <div>
                    <div style="color: rgba(255,255,255,0.2); font-size: 0.65rem;">Documents</div>
                    <div style="color: #ffffff; font-size: 1.2rem; font-weight: 600;">6</div>
                </div>
                <div>
                    <div style="color: rgba(255,255,255,0.2); font-size: 0.65rem;">Chunks</div>
                    <div style="color: #ffffff; font-size: 1.2rem; font-weight: 600;">20</div>
                </div>
                <div>
                    <div style="color: rgba(255,255,255,0.2); font-size: 0.65rem;">Customers</div>
                    <div style="color: #ffffff; font-size: 1.2rem; font-weight: 600;">3</div>
                </div>
                <div>
                    <div style="color: rgba(255,255,255,0.2); font-size: 0.65rem;">Tools</div>
                    <div style="color: #ffffff; font-size: 1.2rem; font-weight: 600;">3</div>
                </div>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    # Key Features
    st.markdown(
        """
    <h3 style="color: rgba(255,255,255,0.6); font-size: 1rem; font-weight: 600; margin: 1.5rem 0 0.8rem 0;">Key Engineering Work</h3>
    """,
        unsafe_allow_html=True,
    )

    features = [
        "Retrieval-Augmented Generation (RAG)",
        "Multi-step agent reasoning",
        "Structured data tools",
        "Document source prioritization",
        "Customer-specific policy overrides",
        "Issue investigation and detection",
        "Role-based access control",
        "Human confirmation for state-changing actions",
        "Evidence-based responses with citations",
    ]

    cols = st.columns(3)
    for i, feature in enumerate(features):
        with cols[i % 3]:
            st.markdown(
                f'<div class="trust-item"><span class="check">✓</span> {feature}</div>',
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

    # Summary stats
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

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button(
                "Clear Activity Log", use_container_width=True, type="secondary"
            ):
                st.session_state.activity = []
                st.rerun()


def render_issue_intelligence():
    """Render the Issue Intelligence page (fallback view)."""
    st.markdown(
        """
    <div style="text-align: center; padding: 3rem 1rem;">
        <div style="font-size: 3rem; margin-bottom: 1rem;">🔍</div>
        <h2 style="color: #ffffff; font-weight: 600; margin: 0;">Issue Intelligence</h2>
        <p style="color: rgba(255,255,255,0.3); margin: 0.5rem 0 1rem 0;">
            The dedicated Issue Intelligence page provides deeper investigation capabilities.
        </p>
        <div style="display: flex; justify-content: center; gap: 1rem; flex-wrap: wrap;">
            <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.04); border-radius: 8px; padding: 1rem; min-width: 150px;">
                <div style="color: rgba(255,255,255,0.3); font-size: 0.7rem;">Issues Detected</div>
                <div style="color: #ffffff; font-size: 1.5rem; font-weight: 600;">4</div>
            </div>
            <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.04); border-radius: 8px; padding: 1rem; min-width: 150px;">
                <div style="color: rgba(255,255,255,0.3); font-size: 0.7rem;">Affected Tickets</div>
                <div style="color: #ffffff; font-size: 1.5rem; font-weight: 600;">68</div>
            </div>
            <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.04); border-radius: 8px; padding: 1rem; min-width: 150px;">
                <div style="color: rgba(255,255,255,0.3); font-size: 0.7rem;">High Severity</div>
                <div style="color: #f5576c; font-size: 1.5rem; font-weight: 600;">2</div>
            </div>
        </div>
        <div style="margin-top: 1.5rem;">
            <span style="color: rgba(255,255,255,0.2); font-size: 0.8rem;">Click the "Issue Intelligence" button in the sidebar to access the full investigation dashboard.</span>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )


def render_issue_intelligence_page():
    """
    Actually run pages/issue_investigation.py in place, instead of just
    printing its file path. Falls back to the placeholder view if the
    file is missing or raises an error.
    """
    import importlib.util

    page_path = "pages/issue_investigation.py"

    if not os.path.exists(page_path):
        st.warning(
            f"⚠️ Issue Intelligence page not found at `{page_path}`. "
            "Showing summary view instead."
        )
        render_issue_intelligence()
        return

    try:
        spec = importlib.util.spec_from_file_location("issue_investigation", page_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # <-- this is what actually runs the page
    except Exception as e:
        st.error(f"⚠️ Failed to load Issue Intelligence page: {e}")
        render_issue_intelligence()


# ==================== MAIN APP ====================


def main():
    """Main application entry point."""
    render_header()
    render_sidebar()

    # Page routing
    if st.session_state.page == "Overview":
        render_overview()
    elif st.session_state.page == "AI Support Assistant":
        if st.session_state.agent_initialized or init_agent():
            render_chat_interface()
        else:
            st.warning("Please initialize the agent to use the chat interface.")
    elif st.session_state.page == "Issue Intelligence":
        if st.session_state.agent_initialized or init_agent():
            render_issue_intelligence_page()
        else:
            st.warning("Please initialize the agent to use issue intelligence.")
    elif st.session_state.page == "How It Works":
        render_how_it_works()
    elif st.session_state.page == "Activity":
        render_activity()
    elif st.session_state.page == "About":
        render_about()

    # Footer
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
