# pages/issue_investigation.py
import streamlit as st
import pandas as pd
import time
import html as html_lib
from datetime import datetime, timedelta
import random
import plotly.graph_objects as go
import plotly.express as px

# REMOVED: st.set_page_config() - already called in app.py

# ==================== CUSTOM CSS ====================
st.markdown(
    """
<style>
    /* ===== GLOBAL ===== */
    .stApp {
        background: #0a0e17;
    }

    /* ===== HEADER ===== */
    .page-header {
        margin-bottom: 1.5rem;
    }

    .page-title {
        color: #ffffff !important;
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        margin: 0 !important;
    }

    .page-subtitle {
        color: rgba(255,255,255,0.3) !important;
        font-size: 0.9rem !important;
        margin: 0.2rem 0 0 0 !important;
        font-weight: 400;
    }

    /* ===== METRICS ===== */
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 0.8rem;
        margin: 1rem 0;
    }

    .metric-card {
        background: rgba(255,255,255,0.03);
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid rgba(255,255,255,0.04);
        text-align: center;
        transition: all 0.2s ease;
        cursor: default;
    }

    .metric-card:hover {
        background: rgba(255,255,255,0.05);
        border-color: rgba(255,255,255,0.08);
        transform: translateY(-2px);
    }

    .metric-value {
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: #ffffff !important;
        line-height: 1.2;
    }

    .metric-value.danger { color: #f5576c !important; }
    .metric-value.warning { color: #f093fb !important; }
    .metric-value.success { color: #43e97b !important; }
    .metric-value.info { color: #4facfe !important; }

    .metric-label {
        color: rgba(255,255,255,0.35) !important;
        font-size: 0.7rem !important;
        margin-top: 0.2rem;
        font-weight: 400;
    }

    .metric-change {
        font-size: 0.6rem !important;
        margin-top: 0.1rem;
    }

    .metric-change.up { color: #f5576c !important; }
    .metric-change.down { color: #43e97b !important; }
    .metric-change.stable { color: #f093fb !important; }

    /* ===== ISSUE CARDS ===== */
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

    .issue-detail-item .value { color: rgba(255,255,255,0.5) !important; }

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

    /* ===== INVESTIGATION RESULTS ===== */
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

    /* ===== SEARCH INPUT ===== */
    .stTextInput input,
    div[data-baseweb="input"] input,
    div[data-baseweb="base-input"] input {
        background: transparent !important;
        color: #ffffff !important;
        font-size: 0.9rem !important;
    }

    .stTextInput div[data-baseweb="base-input"],
    div[data-baseweb="input"] {
        background: rgba(255,255,255,0.04) !important;
        border-radius: 25px !important;
        border: 1px solid rgba(255,255,255,0.06) !important;
    }

    .stTextInput input::placeholder {
        color: rgba(255,255,255,0.35) !important;
    }

    .stTextInput div[data-baseweb="base-input"]:focus-within {
        border-color: rgba(74, 108, 247, 0.4) !important;
        background: rgba(255,255,255,0.06) !important;
        box-shadow: 0 0 0 3px rgba(74, 108, 247, 0.08);
    }

    /* ===== SELECTBOX ===== */
    div[data-baseweb="select"] > div {
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid rgba(255,255,255,0.06) !important;
        border-radius: 25px !important;
    }

    div[data-baseweb="select"] * {
        color: #ffffff !important;
    }

    div[data-baseweb="select"] svg {
        fill: rgba(255,255,255,0.5) !important;
    }

    div[data-baseweb="popover"] {
        background: #12182a !important;
    }

    div[data-baseweb="popover"] ul {
        background: #12182a !important;
    }

    div[data-baseweb="popover"] li {
        color: #ffffff !important;
        background: transparent !important;
    }

    div[data-baseweb="popover"] li:hover {
        background: rgba(255,255,255,0.08) !important;
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

    /* ===== DIVIDER ===== */
    hr {
        border-color: rgba(255,255,255,0.04) !important;
        margin: 1rem 0 !important;
    }

    /* ===== INFO BOXES ===== */
    .stAlert {
        background: rgba(255,255,255,0.03) !important;
        border: 1px solid rgba(255,255,255,0.04) !important;
        color: rgba(255,255,255,0.6) !important;
    }

    .stAlert .stAlertIcon { color: #4facfe !important; }

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

    /* ===== BACK BUTTON ===== */
    .back-button-container { text-align: center; padding: 1rem 0; }

    /* ===== RESPONSIVE ===== */
    @media (max-width: 768px) {
        .metric-grid { grid-template-columns: repeat(2, 1fr); }
        .issue-header { flex-direction: column; align-items: flex-start; gap: 0.3rem; }
        .issue-details { flex-direction: column; gap: 0.3rem; }
    }

    /* ===== TREND INDICATOR ===== */
    .trend-up { color: #f5576c; }
    .trend-down { color: #43e97b; }
    .trend-stable { color: #f093fb; }

    /* ===== STATUS TIMELINE ===== */
    .timeline-item {
        display: flex;
        align-items: center;
        padding: 0.3rem 0;
        border-bottom: 1px solid rgba(255,255,255,0.02);
    }

    .timeline-time {
        color: rgba(255,255,255,0.2);
        font-size: 0.65rem;
        min-width: 60px;
    }

    .timeline-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        margin: 0 0.8rem;
    }

    .timeline-dot.completed { background: #43e97b; }
    .timeline-dot.in-progress { background: #f093fb; }
    .timeline-dot.failed { background: #f5576c; }

    .timeline-content {
        color: rgba(255,255,255,0.4);
        font-size: 0.8rem;
    }

    .timeline-content strong {
        color: rgba(255,255,255,0.6);
    }
</style>
""",
    unsafe_allow_html=True,
)

# ==================== SESSION STATE ====================
if "agent" not in st.session_state:
    # Use mock agent if real agent is not available
    try:
        from src.agent import ParcelPilotAgent

        user_context = {"role": "operations", "user_id": "ops_user"}
        st.session_state.agent = ParcelPilotAgent(user_context)
    except Exception as e:
        # Use a simple mock agent for the issue investigation page
        class MockInvestigationAgent:
            def investigate_issue(self, issue_name, details):
                return f"""🔍 **Investigation Results for {issue_name}**

**Root Cause:** {details.get("root_cause", "Unknown")}

**Recommendation:** {details.get("recommendation", "Escalate to operations team")}

**Key Findings:**
- Severity: {details.get("severity", "Unknown")}
- Tickets affected: {details.get("tickets", 0)}
- Affected customers: {", ".join(details.get("affected_customers", []))}
- Trend: {details.get("trend", "Stable")}
- Avg resolution time: {details.get("avg_resolution_time", "Unknown")}

**Next Steps:**
1. Review the root cause analysis above
2. Implement the recommended action
3. Monitor for recurrence

📄 **Sources:** Issue investigation database, operational metrics"""

            def process_query(self, query):
                return "I'm a mock agent for issue investigation."

        st.session_state.agent = MockInvestigationAgent()

if "investigation_results" not in st.session_state:
    st.session_state.investigation_results = {}

if "investigation_timeline" not in st.session_state:
    st.session_state.investigation_timeline = []

# ==================== HEADER ====================
st.markdown(
    """
<div class="page-header">
    <h1 class="page-title">🔍 Issue Intelligence</h1>
    <p class="page-subtitle">
        Detect recurring operational problems and investigate their likely causes using support data and product knowledge.
    </p>
</div>
""",
    unsafe_allow_html=True,
)

# ==================== DATA ====================
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

# ==================== METRICS ====================
st.markdown('<div class="metric-grid">', unsafe_allow_html=True)

total_tickets = sum(i["tickets"] for i in issues.values())
high_severity = sum(1 for i in issues.values() if i["severity"] == "HIGH")
increasing = sum(1 for i in issues.values() if "↑" in i["trend"])
avg_tickets_per_issue = total_tickets / len(issues)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        f"""
    <div class="metric-card">
        <div class="metric-value info">{len(issues)}</div>
        <div class="metric-label">Total Issues</div>
        <div class="metric-change stable">Active</div>
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
        <div class="metric-change up">⚠️ Needs attention</div>
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
        <div class="metric-change stable">Avg {avg_tickets_per_issue:.0f} per issue</div>
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
        <div class="metric-change up">📈 Monitor closely</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

st.markdown("</div>", unsafe_allow_html=True)

# ==================== CHARTS ====================
st.markdown("---")
st.markdown(
    """
<h3 style="color: rgba(255,255,255,0.6); font-size: 1rem; font-weight: 600; margin: 0 0 0.8rem 0;">📊 Issue Distribution</h3>
""",
    unsafe_allow_html=True,
)

col1, col2 = st.columns(2)

with col1:
    severity_counts = {}
    for issue in issues.values():
        severity = issue["severity"]
        severity_counts[severity] = severity_counts.get(severity, 0) + 1

    fig1 = go.Figure(
        data=[
            go.Pie(
                labels=list(severity_counts.keys()),
                values=list(severity_counts.values()),
                hole=0.4,
                marker_colors=["#f5576c", "#f093fb", "#43e97b"],
                textfont_color="rgba(255,255,255,0.6)",
            )
        ]
    )
    fig1.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="rgba(255,255,255,0.4)",
        height=250,
        margin=dict(t=0, b=0, l=0, r=0),
    )
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    fig2 = go.Figure(
        data=[
            go.Bar(
                x=list(issues.keys()),
                y=[i["tickets"] for i in issues.values()],
                marker_color=[
                    "#f5576c"
                    if i["severity"] == "HIGH"
                    else "#f093fb"
                    if i["severity"] == "MEDIUM"
                    else "#43e97b"
                    for i in issues.values()
                ],
                text=[i["tickets"] for i in issues.values()],
                textposition="outside",
                textfont_color="rgba(255,255,255,0.4)",
            )
        ]
    )
    fig2.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="rgba(255,255,255,0.4)",
        height=250,
        margin=dict(t=0, b=30, l=0, r=0),
        showlegend=False,
        xaxis=dict(
            tickfont_color="rgba(255,255,255,0.3)", gridcolor="rgba(255,255,255,0.03)"
        ),
        yaxis=dict(
            tickfont_color="rgba(255,255,255,0.3)", gridcolor="rgba(255,255,255,0.03)"
        ),
    )
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# ==================== FILTER ====================
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


# ==================== INVESTIGATION HELPER ====================
_FALLBACK_MARKERS = (
    "i'm not sure how to help",
    "try one of these",
    "i don't understand",
    "i'm not sure what you mean",
)


def _looks_like_fallback(text: str) -> bool:
    if not text:
        return True
    lowered = text.lower()
    return any(marker in lowered for marker in _FALLBACK_MARKERS)


def _synthesize_summary(issue_name: str, details: dict) -> str:
    customers = ", ".join(details["affected_customers"])
    return (
        f'The "{issue_name}" issue is currently rated {details["severity"]} severity '
        f"and has affected {details['tickets']} tickets since it was first detected on "
        f"{details['first_detected']}, impacting {customers}.\n\n"
        f"Root cause: {details['root_cause']}.\n\n"
        f"Trend: {details['trend']} ({details['trend_percentage']}% change), with an "
        f"average resolution time of {details['avg_resolution_time']} and {details['sla_impact']} "
        f"SLA impact.\n\n"
        f"Recommended action: {details['recommendation']}."
    )


def run_investigation(issue_name: str, details: dict) -> str:
    agent = st.session_state.get("agent")

    if agent is not None:
        if hasattr(agent, "investigate_issue"):
            try:
                response = agent.investigate_issue(issue_name, details)
                if isinstance(response, str) and not _looks_like_fallback(response):
                    return response
            except Exception:
                pass

        try:
            query = (
                f'Investigation request for operational issue "{issue_name}". '
                f"Known data: severity={details['severity']}, tickets={details['tickets']}, "
                f"suspected root cause={details['root_cause']}, "
                f"trend={details['trend']} ({details['trend_percentage']}%), "
                f"affected customers={', '.join(details['affected_customers'])}. "
                f"Confirm or refine the root cause and provide a specific, actionable "
                f"recommendation for the operations team."
            )
            response = agent.process_query(query)
            if isinstance(response, str) and not _looks_like_fallback(response):
                return response
        except Exception:
            pass

    return _synthesize_summary(issue_name, details)


# ==================== ISSUES LIST ====================
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

        # Investigation controls
        col1, col2 = st.columns([3, 1])
        with col1:
            st.info(f"💡 **Root Cause:** {details['root_cause']}")
            st.success(f"✅ **Recommendation:** {details['recommendation']}")
        with col2:
            if st.button(
                "🔍 Investigate", key=f"invest_{issue_name}", use_container_width=True
            ):
                with st.spinner(f"Analyzing {issue_name}..."):
                    try:
                        response_text = run_investigation(issue_name, details)

                        st.session_state.investigation_results[issue_name] = {
                            "timestamp": datetime.now().strftime("%I:%M %p"),
                            "response": response_text,
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

                    except Exception as e:
                        st.error(f"Error: {str(e)}")

        # Show investigation results if available
        if issue_name in st.session_state.investigation_results:
            result = st.session_state.investigation_results[issue_name]
            with st.expander("📋 Investigation Results", expanded=True):
                safe_response = html_lib.escape(str(result["response"]))
                safe_response = safe_response.replace("\n\n", "<br><br>").replace(
                    "\n", "<br>"
                )

                st.markdown(
                    f"""<div class="investigation-container">
<div class="investigation-title">🔍 Investigation Summary</div>
<div style="color: rgba(255,255,255,0.6); font-size: 0.85rem; line-height: 1.6;">
{safe_response}
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
</div>""",
                    unsafe_allow_html=True,
                )

        st.markdown("---")

# ==================== INVESTIGATION TIMELINE ====================
if st.session_state.investigation_timeline:
    st.markdown(
        """
    <h3 style="color: rgba(255,255,255,0.6); font-size: 1rem; font-weight: 600; margin: 1rem 0 0.8rem 0;">📋 Investigation Timeline</h3>
    """,
        unsafe_allow_html=True,
    )

    for item in reversed(st.session_state.investigation_timeline[-10:]):
        dot_class = "completed"
        st.markdown(
            f"""
        <div class="timeline-item">
            <span class="timeline-time">{item["time"]}</span>
            <span class="timeline-dot {dot_class}"></span>
            <span class="timeline-content">
                <strong>Investigated</strong> {item["issue"]}
            </span>
        </div>
        """,
            unsafe_allow_html=True,
        )

    if st.button("Clear Timeline", type="secondary"):
        st.session_state.investigation_timeline = []
        st.rerun()

# ==================== BACK BUTTON ====================
st.markdown('<div class="back-button-container">', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("← Back to Assistant", use_container_width=True):
        st.switch_page("app.py")

st.markdown("</div>", unsafe_allow_html=True)

# ==================== FOOTER ====================
st.markdown(
    """
<div style="text-align: center; padding: 1rem 0; color: rgba(255,255,255,0.1); font-size: 0.65rem; border-top: 1px solid rgba(255,255,255,0.02); margin-top: 1rem;">
    🔍 Proactive Issue Detection & Investigation • ParcelPilot AI
</div>
""",
    unsafe_allow_html=True,
)
