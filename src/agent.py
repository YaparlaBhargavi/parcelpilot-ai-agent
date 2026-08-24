# src/agent.py
"""
ParcelPilot AI Support Agent

Main responsibilities:
- Route user questions to the correct capability.
- Search company documents through DocumentSearchTool.
- Look up structured order/ticket/account data through DataLookupTool.
- Perform protected actions through ActionTools.
- Require confirmation before state-changing actions.
- Combine structured data + document evidence for multi-step questions.
- Apply source priority and report conflicts/uncertainty.
- Investigate dashboard-reported operational issues (issue_investigation page).
"""

import difflib
import json
import logging
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from src.security.access_control import AccessControl
from src.tools.action_tools import ActionTools
from src.tools.data_lookup import DataLookupTool
from src.tools.document_search import DocumentSearchTool


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ParcelPilotAgent:
    """Main agent orchestrating document search, data lookup, reasoning, and actions."""

    # Representative keywords per intent, used for typo-tolerant fuzzy
    # fallback matching when a query doesn't hit any exact pattern above.
    # Only meaningful topic words go here (not generic verbs like "show"
    # or "list") so a bare vague word doesn't trigger a misleading search.
    FUZZY_INTENT_KEYWORDS = {
        "document_search": [
            "policy",
            "policies",
            "sop",
            "guide",
            "agreement",
            "contract",
            "terms",
            "conditions",
            "documentation",
        ],
        "data_lookup": [
            "order",
            "ticket",
            "account",
            "customer",
            "lookup",
            "status",
            "details",
        ],
        "action": [
            "escalate",
            "escalation",
            "refund",
            "approve",
            "cancel",
        ],
    }

    # Phrases that signal "just show/find/open the document" rather than
    # a reasoning question. Checked together with DOCUMENT_NOUNS below.
    RETRIEVAL_INTENT_PHRASES = [
        "show me",
        "show the",
        "display the",
        "pull up",
        "get me the",
        "find the",
        "open the",
        "view the",
        "look at the",
    ]

    DOCUMENT_NOUNS = [
        "agreement",
        "policy",
        "policies",
        "contract",
        "sop",
        "guide",
        "document",
        "documentation",
        "terms",
    ]

    def __init__(self, user_context: dict):
        self.document_search = DocumentSearchTool()
        self.data_lookup = DataLookupTool()
        self.action_tools = ActionTools()
        self.access_control = AccessControl()

        self.user_context = user_context or {}
        self.conversation_history: List[Dict[str, Any]] = []

        # Higher number = higher authority.
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

    # ============================================================
    # MAIN ENTRY POINT
    # ============================================================

    def _get_current_time(self) -> datetime:
        return datetime.now(timezone.utc)

    def process_query(self, query: str) -> str:
        """Process one user query and return a user-friendly response."""
        query = (query or "").strip()

        if not query:
            return "Please enter a question or request."

        self.conversation_history.append(
            {
                "role": "user",
                "content": query,
                "timestamp": self._get_current_time().isoformat(),
            }
        )

        try:
            intent = self._determine_intent(query)

            if intent == "action":
                result = self._handle_action(query)
            elif intent == "multi_step":
                result = self._handle_multi_step(query)
            elif intent == "data_lookup":
                result = self._handle_data_lookup(query)
            elif intent == "document_search":
                result = self._handle_document_search(query)
            else:
                result = self._handle_general(query)

        except Exception:
            logger.exception("Unexpected error while processing query")
            result = (
                "⚠️ **Something went wrong**\n\n"
                "I could not complete that request. "
                "Please try again with the order ID, ticket ID, or account name if applicable."
            )

        self.conversation_history.append(
            {
                "role": "assistant",
                "content": result,
                "timestamp": self._get_current_time().isoformat(),
            }
        )

        return result

    # ============================================================
    # INTENT DETECTION
    # ============================================================

    def _determine_intent(self, query: str) -> str:
        """Determine the most appropriate capability for the query."""
        text = query.lower().strip()

        if len(text) < 3:
            return "general"

        # Actions must be checked first.
        action_patterns = [
            "escalate",
            "create escalation",
            "raise escalation",
            "refund",
            "approve",
            "modify",
            "update",
            "delete",
            "remove",
            "change status",
            "cancel order",
        ]
        if any(pattern in text for pattern in action_patterns):
            return "action"

        # Plain "show/find/open the document" requests are document
        # retrieval, even if they happen to mention a customer name.
        # This MUST be checked before the has_entity/topic-word check
        # below, otherwise "show me the Northstar agreement" gets
        # misrouted into multi-step reasoning just because it contains
        # both an account name and the word "agreement" -- it isn't
        # asking a question, it's asking to see a document.
        is_retrieval_phrasing = any(p in text for p in self.RETRIEVAL_INTENT_PHRASES)
        mentions_document_noun = any(n in text for n in self.DOCUMENT_NOUNS)
        if is_retrieval_phrasing and mentions_document_noun:
            return "document_search"

        # Questions that require combining multiple sources.
        reasoning_patterns = [
            "can ",
            "should ",
            "would ",
            "could ",
            "eligible",
            "without fee",
            "without a fee",
            "fee applies",
            "waive",
            "override",
            "compensation",
            "service credit",
            "credit",
            "sla",
            "why ",
            "reason",
            "compare",
            "is this allowed",
            "does the agreement",
            "does the contract",
        ]

        has_entity = bool(
            self._extract_order_id(query)
            or self._extract_ticket_id(query)
            or self._extract_account_name(query)
        )

        if any(pattern in text for pattern in reasoning_patterns):
            return "multi_step"

        if has_entity and any(
            word in text
            for word in [
                "policy",
                "agreement",
                "contract",
                "fee",
                "charge",
                "cancel",
                "eligible",
                "sla",
                "credit",
                "why",
                "should",
            ]
        ):
            return "multi_step"

        # Direct structured-data requests.
        data_patterns = [
            "look up",
            "lookup",
            "show me",
            "details for",
            "status of",
            "find order",
            "find ticket",
            "find account",
            "order ",
            "ord-",
            "ticket ",
            "tkt-",
            "tck-",
            "account ",
            "customer ",
        ]
        if any(pattern in text for pattern in data_patterns):
            return "data_lookup"

        # Document questions. Note: "polic" (not "policy") catches
        # "policy", "policies", and the common typo "polices" all in
        # one substring check.
        document_patterns = [
            "polic",  # policy / policies / polices (typo)
            "sop",
            "guide",
            "agreement",
            "contract",
            "terms",
            "conditions",
            "documentation",
            "what is",
            "how to",
            "tell me about",
            "explain",
        ]
        if any(pattern in text for pattern in document_patterns):
            return "document_search"

        # Fuzzy fallback for typos / phrasing we didn't anticipate.
        fuzzy_intent = self._fuzzy_intent_match(text)
        if fuzzy_intent:
            return fuzzy_intent

        return "general"

    def _fuzzy_intent_match(self, text: str) -> Optional[str]:
        """Typo-tolerant fallback intent matching."""
        words = re.findall(r"[a-zA-Z][a-zA-Z\-]*", text)
        if not words:
            return None

        best_intent = None
        best_ratio = 0.0

        for word in words:
            if len(word) < 4:
                continue

            for intent_name, keywords in self.FUZZY_INTENT_KEYWORDS.items():
                matches = difflib.get_close_matches(word, keywords, n=1, cutoff=0.8)
                if not matches:
                    continue

                ratio = difflib.SequenceMatcher(None, word, matches[0]).ratio()
                if ratio > best_ratio:
                    best_ratio = ratio
                    best_intent = intent_name

        return best_intent

    # ============================================================
    # DOCUMENT SEARCH
    # ============================================================

    def _handle_document_search(self, query: str) -> str:
        """Search company documents."""
        try:
            account_name = self._extract_account_name(query)
            results = self._search_documents_with_fallback(
                query, account_name=account_name
            )

            if not results or not results.get("results"):
                return self._format_no_results(query)

            return self._format_document_results(results)

        except Exception:
            logger.exception("Document search error")
            return (
                "⚠️ **Document search failed**\n\n"
                "I could not search the support documents right now."
            )

    # ------------------------------------------------------------
    # Search fallback
    # ------------------------------------------------------------

    def _generate_query_variants(self, query: str) -> List[str]:
        """Generate simplified fallback variants of a natural-language query."""
        variants = [query]

        text = query.strip()

        cleaned = re.sub(r"[?!.]+$", "", text).strip()
        if cleaned and cleaned != text:
            variants.append(cleaned)

        lower = cleaned.lower()

        question_prefixes = [
            "what is the ",
            "what is ",
            "what are the ",
            "what are ",
            "how do i ",
            "how do we ",
            "how to ",
            "can you tell me about the ",
            "can you tell me about ",
            "tell me about the ",
            "tell me about ",
            "explain the ",
            "explain ",
            "describe the ",
            "describe ",
            "information on the ",
            "information on ",
            "show me all ",
            "show me the ",
            "show me ",
            "show all ",
            "list all ",
            "display all ",
        ]
        for prefix in question_prefixes:
            if lower.startswith(prefix):
                stripped = lower[len(prefix) :].strip()
                if stripped:
                    variants.append(stripped)
                break

        stopwords = {
            "what",
            "is",
            "are",
            "the",
            "a",
            "an",
            "of",
            "for",
            "to",
            "on",
            "in",
            "and",
            "how",
            "do",
            "does",
            "did",
            "i",
            "we",
            "you",
            "me",
            "about",
            "this",
            "that",
            "tell",
            "can",
            "could",
            "would",
            "should",
            "please",
            "show",
            "all",
            "list",
            "display",
            "give",
        }
        words = re.findall(r"[a-zA-Z][a-zA-Z\-]*", lower)
        keywords = [w for w in words if w not in stopwords]
        if keywords:
            variants.append(" ".join(keywords))

        seen = set()
        unique_variants = []
        for variant in variants:
            normalized = variant.strip()
            key = normalized.lower()
            if normalized and key not in seen:
                seen.add(key)
                unique_variants.append(normalized)

        return unique_variants

    def _search_documents_with_fallback(
        self,
        query: str,
        account_name: Optional[str] = None,
    ) -> Optional[dict]:
        """Try the query, then progressively simpler variants, until one hits.

        account_name (if known) is forwarded to DocumentSearchTool on every
        attempt so that a wrong-customer agreement can never be returned
        for a question about a specific, named account.
        """
        last_results = None

        for variant in self._generate_query_variants(query):
            try:
                results = self.document_search.search(
                    variant, account_name=account_name
                )
            except Exception:
                logger.exception("Document search failed for variant: %s", variant)
                continue

            last_results = results

            if results and results.get("results"):
                return results

        return last_results

    def _format_document_results(self, results: dict) -> str:
        """Format document search results."""
        response = "📄 **Document Search Results**\n\n"

        if results.get("conflicts"):
            response += "⚠️ **Policy conflicts detected** ⚠️\n\n"
            for conflict in results["conflicts"]:
                response += f"- {conflict['resolution']}\n"
            response += "\n"

        if not results.get("results"):
            response += "No relevant documents found.\n"
            return response

        for i, result in enumerate(results["results"], 1):
            response += f"**Result {i}: {result['source']}**\n"
            response += f"   • Priority: {result['priority']}\n"
            response += f"   • Type: {result.get('type', 'Unknown')}\n"
            content = result["content"][:200]
            if len(result["content"]) > 200:
                content += "..."
            response += f"   • Content: {content}\n\n"

        response += "**📚 Sources:**\n"
        for source in results["sources"]:
            response += f"✓ {source}\n"

        return response

    # ============================================================
    # STRUCTURED DATA LOOKUP
    # ============================================================

    def _handle_data_lookup(self, query: str) -> str:
        """Look up an order, ticket, or account."""
        try:
            order_id = self._extract_order_id(query)
            ticket_id = self._extract_ticket_id(query)
            account_name = self._extract_account_name(query)

            if order_id:
                result = self.data_lookup.lookup_order(order_id, self.user_context)

                if not result or "error" in result:
                    return f"❌ {result.get('error', 'Order not found.')}"

                return self._format_order_data(result)

            if ticket_id:
                result = self.data_lookup.lookup_ticket(ticket_id)

                if not result or "error" in result:
                    return f"❌ {result.get('error', 'Ticket not found.')}"

                return self._format_ticket_data(result)

            if account_name:
                result = self.data_lookup.lookup_account(account_name)

                if not result or "error" in result:
                    return f"❌ {result.get('error', 'Account not found.')}"

                return self._format_account_data(result)

            return self._format_data_help()

        except Exception:
            logger.exception("Data lookup error")
            return (
                "⚠️ **Data lookup failed**\n\n"
                "I could not retrieve the requested operational data."
            )

    def _format_order_data(self, data: dict) -> str:
        response = "📋 **Order Details**\n\n"
        for key, value in data.items():
            response += f"• **{key}**: {value}\n"
        return response

    def _format_ticket_data(self, data: dict) -> str:
        response = "🎫 **Ticket Details**\n\n"
        for key, value in data.items():
            response += f"• **{key}**: {value}\n"
        return response

    def _format_account_data(self, data: Any) -> str:
        response = "🏢 **Account Details**\n\n"
        if isinstance(data, dict):
            for key, value in data.items():
                response += f"• **{key}**: {value}\n"
        else:
            response += str(data)
        return response

    def _format_data_help(self) -> str:
        return """I couldn't identify a specific record.

**You can provide:**
- 📋 Order ID: `ORD-1001`
- 🎫 Ticket ID: `TKT-501`
- 🏢 Account name: `Northstar`

Example: **Look up order ORD-1001**
"""

    # ============================================================
    # ACTIONS
    # ============================================================

    def _handle_action(self, query: str) -> str:
        """Handle state-changing actions with confirmation."""
        try:
            if not self.access_control.check_permission(self.user_context, "escalate"):
                return (
                    "🔒 **Access denied**\n\n"
                    "Your current role does not have permission to perform this action."
                )

            order_id = self._extract_order_id(query)
            ticket_id = self._extract_ticket_id(query)

            if not order_id and not ticket_id:
                return self._format_action_help()

            if "escalate" in query.lower():
                target = order_id or ticket_id

                result = self.action_tools.create_escalation(target, "User request")

                if not result:
                    return "⚠️ The escalation service returned no result."

                if result.get("status") == "pending_confirmation":
                    return self._format_action_confirmation(result)

                if result.get("status") in {"success", "completed"}:
                    return self._format_completed_action(result)

                return self._format_action_result(result)

            return self._format_action_help()

        except Exception:
            logger.exception("Action error")
            return "⚠️ **Action failed**\n\nI could not process the requested action."

    def _format_action_help(self) -> str:
        return """⚡ **Available Action**

I can create an escalation for an order or ticket.

Examples:
- **Escalate order ORD-1001**
- **Escalate ticket TKT-501**

I will ask for confirmation before the action is completed.
"""

    def _format_action_confirmation(self, result: dict) -> str:
        data = result.get("data") or {}

        response = """⚠️ **ACTION REQUIRES CONFIRMATION**

"""
        response += str(result.get("message", "This action is ready to be confirmed."))
        response += "\n\n**ACTION DETAILS**\n"

        if isinstance(data, dict):
            for key, value in data.items():
                response += f"• **{key}**: {value}\n"
        else:
            response += f"• {data}\n"

        response += (
            "\n**Please confirm or cancel this action.**\n"
            "\n> The action has NOT been completed yet."
        )

        return response

    def _format_completed_action(self, result: dict) -> str:
        data = result.get("data") or {}

        response = "✅ **ACTION COMPLETED**\n\n"
        response += str(result.get("message", "The requested action was completed."))

        if isinstance(data, dict) and data:
            response += "\n\n**Details**\n"
            for key, value in data.items():
                response += f"• **{key}**: {value}\n"

        return response

    def _format_action_result(self, result: dict) -> str:
        status = result.get("status", "unknown")
        return (
            f"⚠️ **Action status: {status}**\n\n"
            f"{result.get('message', 'The action could not be completed.')}"
        )

    # ============================================================
    # MULTI-STEP REASONING
    # ============================================================

    def _handle_multi_step(self, query: str) -> str:
        """Answer a complex question using data + document evidence."""
        try:
            entities = self._extract_entities(query)
            evidence = self._gather_evidence(query, entities)
            analysis = self._analyze_evidence(query, evidence, entities)

            return self._format_analysis_response(query, evidence, analysis, entities)

        except Exception:
            logger.exception("Multi-step reasoning error")
            return (
                "⚠️ **Analysis failed**\n\n"
                "I could not safely determine the answer from the available evidence."
            )

    def _extract_entities(self, query: str) -> dict:
        text = query.lower()

        return {
            "order_id": self._extract_order_id(query),
            "ticket_id": self._extract_ticket_id(query),
            "account_name": self._extract_account_name(query),
            "cancellation_mentioned": ("cancel" in text or "cancellation" in text),
            "fee_mentioned": any(
                word in text for word in ["fee", "charge", "cost", "penalty"]
            ),
            "sla_mentioned": ("sla" in text or "service level" in text),
            "credit_mentioned": any(
                word in text for word in ["credit", "compensation", "service credit"]
            ),
        }

    def _gather_evidence(self, query: str, entities: dict) -> dict:
        """Gather structured and unstructured evidence."""
        evidence: Dict[str, Any] = {
            "order": None,
            "account": None,
            "ticket": None,
            "customer_agreement": [],
            "current_policy": [],
            "current_sop": [],
            "product_guide": [],
            "deprecated_policy": [],
            "search_results": {},
        }

        # Structured data
        if entities.get("order_id"):
            order = self.data_lookup.lookup_order(
                entities["order_id"], self.user_context
            )
            evidence["order"] = order

            if isinstance(order, dict):
                account_from_order = (
                    order.get("account_name")
                    or order.get("customer")
                    or order.get("account")
                )
                if account_from_order:
                    entities["account_name"] = account_from_order

        if entities.get("ticket_id"):
            ticket = self.data_lookup.lookup_ticket(entities["ticket_id"])
            evidence["ticket"] = ticket

            if isinstance(ticket, dict):
                account_from_ticket = (
                    ticket.get("account_name")
                    or ticket.get("customer")
                    or ticket.get("account")
                )
                if account_from_ticket:
                    entities["account_name"] = account_from_ticket

        if entities.get("account_name"):
            evidence["account"] = self.data_lookup.lookup_account(
                entities["account_name"]
            )

        account_name = entities.get("account_name")

        # Document search
        search_terms = [query]

        if account_name:
            search_terms.append(str(account_name))

        if entities.get("cancellation_mentioned"):
            search_terms.append("cancellation")

        if entities.get("fee_mentioned"):
            search_terms.append("cancellation fee")

        if entities.get("sla_mentioned"):
            search_terms.append("SLA service level")

        if entities.get("credit_mentioned"):
            search_terms.append("service credit compensation")

        unique_terms = []
        seen_terms = set()
        for term in search_terms:
            normalized = term.strip().lower()
            if normalized and normalized not in seen_terms:
                seen_terms.add(normalized)
                unique_terms.append(term)

        # Track which sources we've already stored per doc_type so the
        # same document isn't added multiple times just because it
        # matched several of the search terms above (with slightly
        # different scores each time, which would defeat a naive
        # dict-equality dedup check).
        seen_sources: Dict[str, set] = {
            doc_type: set()
            for doc_type in evidence
            if isinstance(evidence[doc_type], list)
        }

        for term in unique_terms:
            # Forward account_name on every call so a wrong-customer
            # agreement is filtered out at the source, not just
            # deprioritized after the fact.
            results = self._search_documents_with_fallback(
                term, account_name=account_name
            )

            if not results or not results.get("results"):
                continue

            for result in results["results"]:
                doc_type = self._classify_document_result(result)

                if doc_type not in evidence or not isinstance(evidence[doc_type], list):
                    continue

                source_key = result.get("source", result.get("title", "Unknown"))
                if source_key in seen_sources[doc_type]:
                    continue
                seen_sources[doc_type].add(source_key)

                normalized_result = dict(result)
                normalized_result["type"] = doc_type

                if not normalized_result.get("priority"):
                    normalized_result["priority"] = self.source_priority_values.get(
                        doc_type, 50
                    )

                evidence[doc_type].append(normalized_result)

        # General search
        general_results = self._search_documents_with_fallback(
            query, account_name=account_name
        )
        if general_results and general_results.get("results"):
            evidence["search_results"]["general"] = general_results["results"]

        return evidence

    def _classify_document_result(self, result: dict) -> str:
        raw_type = str(result.get("type", "")).lower().strip()

        aliases = {
            "customer_agreement": "customer_agreement",
            "agreement": "customer_agreement",
            "contract": "customer_agreement",
            "current_policy": "current_policy",
            "policy": "current_policy",
            "current_sop": "current_sop",
            "sop": "current_sop",
            "product_guide": "product_guide",
            "guide": "product_guide",
            "deprecated_policy": "deprecated_policy",
            "old_policy": "deprecated_policy",
        }

        if raw_type in aliases:
            return aliases[raw_type]

        source_text = " ".join(
            [
                str(result.get("source", "")),
                str(result.get("title", "")),
                str(result.get("name", "")),
            ]
        ).lower()

        if "agreement" in source_text or "contract" in source_text:
            return "customer_agreement"
        if "deprecated" in source_text or "v2" in source_text:
            return "deprecated_policy"
        if "sop" in source_text:
            return "current_sop"
        if "product" in source_text or "guide" in source_text:
            return "product_guide"
        if "policy" in source_text:
            return "current_policy"

        return "current_policy"

    # ============================================================
    # EVIDENCE ANALYSIS
    # ============================================================

    def _analyze_evidence(self, query: str, evidence: dict, entities: dict) -> dict:
        """Analyze evidence without hard-coding customer-specific answers."""
        analysis = {
            "conflicts": [],
            "applicable_rules": [],
            "decision": {
                "answer": "Unable to determine from available evidence",
                "reason": "There is not enough reliable evidence.",
                "confidence": "Low",
            },
            "confidence": "Low",
            "missing_info": [],
        }

        if not self._has_useful_evidence(evidence):
            analysis["missing_info"].append(
                "No relevant documents or structured data were found."
            )
            return analysis

        applicable_rules = self._determine_applicable_rules(evidence, entities)
        analysis["applicable_rules"] = applicable_rules

        if not applicable_rules:
            analysis["missing_info"].append(
                "No applicable rule was found in the available documents."
            )
            return analysis

        conflicts = self._detect_conflicts(evidence, applicable_rules)
        analysis["conflicts"] = conflicts

        decision = self._make_decision(
            query, evidence, entities, applicable_rules, conflicts
        )

        analysis["decision"] = decision
        analysis["confidence"] = decision.get("confidence", "Low")

        if decision["answer"].startswith("Unable to determine"):
            analysis["missing_info"].append(
                "The available evidence does not clearly support a single answer."
            )

        return analysis

    def _has_useful_evidence(self, evidence: dict) -> bool:
        for key, value in evidence.items():
            if key == "search_results":
                continue

            if isinstance(value, list) and value:
                return True

            if isinstance(value, dict) and value and "error" not in value:
                return True

        return False

    def _determine_applicable_rules(self, evidence: dict, entities: dict) -> list:
        """Select document rules relevant to the question.

        When we know which account the question is about, a
        customer_agreement chunk that belongs to a *different* named
        account is excluded outright -- it should never be able to win
        the "highest priority rule" slot just because it happened to be
        gathered during a broader search term.
        """
        applicable_rules = []
        account_name = entities.get("account_name")
        account_key = account_name.strip().lower() if account_name else None

        for source_type in self.source_priority:
            results = evidence.get(source_type, [])

            for result in results:
                content = str(result.get("content", "")).strip()
                if not content:
                    continue

                source_file = str(result.get("source", result.get("title", "Unknown")))

                if account_key and source_type == "customer_agreement":
                    matches_account = (
                        account_key in source_file.lower()
                        or account_key in content.lower()
                    )
                    if not matches_account:
                        continue

                if not self._is_relevant_to_query(content, entities):
                    continue

                priority = self.source_priority_values.get(source_type, 50)

                supplied_priority = result.get("priority")
                if isinstance(supplied_priority, (int, float)):
                    priority = supplied_priority

                applicable_rules.append(
                    {
                        "source": source_type,
                        "label": self.source_priority_labels.get(
                            source_type, source_type
                        ),
                        "priority": priority,
                        "content": content[:1200],
                        "source_file": source_file,
                    }
                )

        applicable_rules.sort(key=lambda item: item["priority"], reverse=True)

        return applicable_rules

    def _is_relevant_to_query(self, content: str, entities: dict) -> bool:
        content_lower = content.lower()

        requested_topics = []

        if entities.get("cancellation_mentioned"):
            requested_topics.extend(["cancel", "cancellation"])

        if entities.get("fee_mentioned"):
            requested_topics.extend(["fee", "charge", "cost", "penalty"])

        if entities.get("sla_mentioned"):
            requested_topics.extend(["sla", "service level"])

        if entities.get("credit_mentioned"):
            requested_topics.extend(["credit", "compensation"])

        if not requested_topics:
            return True

        return any(topic in content_lower for topic in requested_topics)

    # ============================================================
    # CONFLICT DETECTION
    # ============================================================

    def _detect_conflicts(self, evidence: dict, applicable_rules: list) -> list:
        conflicts = []

        if len(applicable_rules) < 2:
            return conflicts

        for i in range(len(applicable_rules)):
            for j in range(i + 1, len(applicable_rules)):
                rule1 = applicable_rules[i]
                rule2 = applicable_rules[j]

                if not self._texts_contradict(rule1["content"], rule2["content"]):
                    continue

                if rule1["priority"] >= rule2["priority"]:
                    winner, loser = rule1, rule2
                else:
                    winner, loser = rule2, rule1

                conflicts.append(
                    {
                        "source1": rule1["label"],
                        "source2": rule2["label"],
                        "winner": winner["label"],
                        "loser": loser["label"],
                        "resolution": (
                            f"{winner['label']} takes precedence "
                            f"(priority {winner['priority']} > {loser['priority']})"
                        ),
                        "priority1": rule1["priority"],
                        "priority2": rule2["priority"],
                    }
                )

        return conflicts

    def _texts_contradict(self, text1: str, text2: str) -> bool:
        if not text1 or not text2:
            return False

        t1 = text1.lower()
        t2 = text2.lower()

        t1_positive = self._POSITIVE_FEE_RE.search(t1) is not None
        t1_negative = self._NEGATIVE_FEE_RE.search(t1) is not None
        t2_positive = self._POSITIVE_FEE_RE.search(t2) is not None
        t2_negative = self._NEGATIVE_FEE_RE.search(t2) is not None

        return (t1_positive and t2_negative) or (t1_negative and t2_positive)

    # ============================================================
    # DECISION
    # ============================================================

    # --------------------------------------------------------------
    # Regex-based fee/waiver language detection.
    #
    # Real policy/agreement text rarely uses the exact literal phrases
    # ("no fee", "fee applies") a naive substring check looks for --
    # it says things like "no cancellation fee", "no special
    # cancellation-fee waiver", "subject to the standard fee", etc.
    # These patterns are written generically (no customer names) and
    # tolerate a few words / a hyphen between the trigger word and
    # "fee" so real phrasing is actually caught.
    #
    # IMPORTANT: negative (fee-applies) patterns are checked BEFORE
    # positive (no-fee) patterns, because phrases like "no special
    # cancellation-fee waiver" contain "no ... fee" as a substring but
    # actually mean the opposite (no waiver exists, so the fee stands).
    # --------------------------------------------------------------
    _NEGATIVE_FEE_RE = re.compile(
        r"("
        r"fee\s+applies"
        r"|fee\s+is\s+required"
        r"|cannot\s+cancel"
        r"|cancellation\s+is\s+prohibited"
        r"|no\s+(?:special\s+)?[\w-]+(?:\s+[\w-]+){0,2}\s+waiver"  # "no special cancellation-fee waiver"
        r"|not\s+eligible\s+for\s+(?:a\s+)?waiver"
        r"|subject\s+to\s+the\s+standard\s+[\w-]+(?:\s+[\w-]+){0,2}\s*fee"
        r"|standard\s+[\w-]+(?:\s+[\w-]+){0,2}\s*fee\s+applies"
        r")",
        re.IGNORECASE,
    )

    _POSITIVE_FEE_RE = re.compile(
        r"("
        r"no\s+[\w-]+(?:\s+[\w-]+){0,3}\s*fee\b"  # "no cancellation fee", "no fee"
        r"|without\s+[\w-]+(?:\s+[\w-]+){0,3}\s*fee\b"
        r"|fee\s+(?:is\s+|will\s+be\s+)?waived"
        r"|free\s+cancellation"
        r"|no\s+charge"
        r")",
        re.IGNORECASE,
    )

    _ALLOWED_CANCEL_RE = re.compile(
        r"\b(?:can\s+cancel|cancellation\s+(?:is\s+)?allowed|may\s+cancel)\b",
        re.IGNORECASE,
    )
    _DISALLOWED_CANCEL_RE = re.compile(
        r"\b(?:cannot\s+cancel|cancellation\s+is\s+prohibited)\b", re.IGNORECASE
    )

    _POSITIVE_CREDIT_RE = re.compile(
        r"(eligible\s+for\s+(?:a\s+)?credit|credit\s+will\s+be\s+issued|credit\s+applies)",
        re.IGNORECASE,
    )
    _NEGATIVE_CREDIT_RE = re.compile(
        r"(not\s+eligible|no\s+credit|credit\s+does\s+not\s+apply)",
        re.IGNORECASE,
    )

    def _make_decision(
        self,
        query: str,
        evidence: dict,
        entities: dict,
        applicable_rules: list,
        conflicts: list,
    ) -> dict:
        """Make a decision from retrieved evidence. No hard-coded customer answers."""
        decision = {
            "answer": "Unable to determine from available evidence",
            "reason": "The evidence is insufficient.",
            "confidence": "Low",
        }

        if not applicable_rules:
            return decision

        highest_rule = applicable_rules[0]
        content = highest_rule["content"]

        topic = self._detect_topic(entities, query)

        answer = self._extract_rule_answer(content, topic)

        if answer is None:
            decision["answer"] = (
                "I found relevant evidence, but it does not clearly "
                "support a definitive decision."
            )
            decision["reason"] = (
                f"The most relevant source is "
                f"{highest_rule['label']} "
                f"({highest_rule['source_file']}), but its text does "
                "not contain a sufficiently clear rule for this question."
            )
            decision["confidence"] = "Low"
            return decision

        decision["answer"] = answer

        if conflicts:
            decision["reason"] = (
                f"Conflicting guidance was found. "
                f"{highest_rule['label']} has the highest applicable "
                f"priority and was used to resolve the conflict."
            )
        else:
            decision["reason"] = (
                f"Based on {highest_rule['label']} ({highest_rule['source_file']})."
            )

        decision["confidence"] = self._decision_confidence(
            applicable_rules, conflicts, answer
        )

        return decision

    def _detect_topic(self, entities: dict, query: str) -> str:
        text = query.lower()

        if entities.get("cancellation_mentioned"):
            return "cancellation"
        if entities.get("credit_mentioned"):
            return "credit"
        if entities.get("sla_mentioned"):
            return "sla"
        if entities.get("fee_mentioned"):
            return "fee"
        if "refund" in text:
            return "refund"

        return "general"

    def _extract_rule_answer(self, content: str, topic: str) -> Optional[str]:
        """Convert clear retrieved policy language into a user-friendly answer.

        Uses the generic regex patterns above instead of rigid literal
        substrings, so phrasing like "no cancellation fee" or "no
        special cancellation-fee waiver" is actually recognized. Checks
        the fee-applies (negative) case first since it can otherwise be
        masked by a "no ... fee" substring match.
        """
        if topic in {"cancellation", "fee"}:
            if self._NEGATIVE_FEE_RE.search(content):
                return "The applicable cancellation fee applies."

            if self._POSITIVE_FEE_RE.search(content):
                return "Cancellation without the standard fee is allowed according to the applicable policy."

            if self._ALLOWED_CANCEL_RE.search(content):
                return (
                    "The available policy allows cancellation, but the retrieved "
                    "evidence does not clearly state whether a fee is waived."
                )

            if self._DISALLOWED_CANCEL_RE.search(content):
                return "The available policy does not allow cancellation in this situation."

        if topic == "credit":
            if self._POSITIVE_CREDIT_RE.search(content):
                return "The available policy indicates that a service credit may apply."

            if self._NEGATIVE_CREDIT_RE.search(content):
                return "The available policy indicates that a service credit does not apply."

        if topic == "sla":
            if "sla" in content.lower() or "service level" in content.lower():
                return (
                    "The retrieved documents contain SLA information. "
                    "See the cited evidence below for the applicable requirement."
                )

        return None

    def _decision_confidence(
        self, applicable_rules: list, conflicts: list, answer: str
    ) -> str:
        if not applicable_rules:
            return "Low"

        highest = applicable_rules[0]["priority"]

        if conflicts and highest >= 100:
            return "High"

        if highest >= 90:
            return "High"

        if highest >= 85:
            return "Medium-High"

        if highest >= 70:
            return "Medium"

        return "Low"

    def _calculate_confidence(
        self, evidence: dict, applicable_rules: list, conflicts: list
    ) -> str:
        """Backward-compatible confidence helper."""
        if not applicable_rules:
            return "Low"

        return self._decision_confidence(applicable_rules, conflicts, "")

    # ============================================================
    # RESPONSE FORMATTING (conversational multi-step Q&A)
    # ============================================================

    def _format_analysis_response(
        self,
        query: str,
        evidence: dict,
        analysis: dict,
        entities: dict,
    ) -> str:
        lines: List[str] = []

        decision = analysis.get("decision", {})

        lines.append("**🤖 ANSWER**")
        lines.append(
            decision.get("answer", "Unable to determine from available evidence.")
        )
        lines.append("")

        lines.append("**💡 WHY**")
        lines.append(decision.get("reason", "Insufficient evidence."))
        lines.append("")

        lines.append("**📊 DATA USED**")
        data_used = []

        if entities.get("order_id"):
            data_used.append(f"Order: {entities['order_id']}")

        if entities.get("ticket_id"):
            data_used.append(f"Ticket: {entities['ticket_id']}")

        if entities.get("account_name"):
            data_used.append(f"Customer: {entities['account_name']}")

        if evidence.get("account"):
            data_used.append("Account record retrieved")

        if not data_used:
            data_used.append("No specific structured record identified.")

        lines.extend(f"• {item}" for item in data_used)
        lines.append("")

        lines.append("**📚 EVIDENCE**")
        evidence_found = False

        for source_type in self.source_priority:
            results = evidence.get(source_type, [])

            for result in results[:2]:
                source = result.get("source", result.get("title", "Unknown source"))
                lines.append(f"• {self.source_priority_labels[source_type]}: {source}")
                evidence_found = True

        if not evidence_found:
            lines.append("• No relevant documents found.")

        lines.append("")

        lines.append("**🏆 SOURCE PRIORITY**")
        lines.append(
            " > ".join(
                f"{self.source_priority_labels[source]} ({self.source_priority_values[source]})"
                for source in self.source_priority
            )
        )
        lines.append("")

        if analysis.get("conflicts"):
            lines.append("**⚠️ CONFLICTS**")

            for conflict in analysis["conflicts"]:
                lines.append(f"• {conflict['source1']} vs {conflict['source2']}")
                lines.append(f"  Resolution: {conflict['resolution']}")

            lines.append("")

        lines.append("**🎯 CONFIDENCE**")
        lines.append(analysis.get("confidence", decision.get("confidence", "Low")))
        lines.append("")

        if analysis.get("missing_info"):
            lines.append("**❗ MISSING INFORMATION**")

            for item in analysis["missing_info"]:
                lines.append(f"• {item}")

            lines.append("")

        return "\n".join(lines)

    def _format_no_results(self, query: str) -> str:
        return f"""I searched for information about **"{query}"** but could not find a relevant document.

**Try:**
- "What is the cancellation policy?"
- "Show me the Northstar agreement"
- "What are the SLA response times?"
"""

    # ============================================================
    # DASHBOARD-DRIVEN ISSUE INVESTIGATION
    # ============================================================

    def investigate_issue(
        self, issue_name: str, issue_data: Optional[dict] = None
    ) -> str:
        """Investigate a known operational issue reported by the dashboard."""
        issue_name = (issue_name or "").strip()
        issue_data = issue_data or {}

        if not issue_name:
            return "Please provide an issue name to investigate."

        self.conversation_history.append(
            {
                "role": "user",
                "content": f"[Issue Investigation] {issue_name}",
                "timestamp": self._get_current_time().isoformat(),
            }
        )

        try:
            gathered_evidence = self._gather_issue_evidence(issue_name, issue_data)
            response = self._format_issue_investigation(
                issue_name, issue_data, gathered_evidence
            )
        except Exception:
            logger.exception("Issue investigation error for: %s", issue_name)
            response = self._format_issue_investigation_fallback(issue_name, issue_data)

        self.conversation_history.append(
            {
                "role": "assistant",
                "content": response,
                "timestamp": self._get_current_time().isoformat(),
            }
        )

        return response

    def _gather_issue_evidence(self, issue_name: str, issue_data: dict) -> dict:
        gathered: Dict[str, List[dict]] = {
            source_type: [] for source_type in self.source_priority
        }

        search_terms = [issue_name]

        root_cause = issue_data.get("root_cause")
        if root_cause:
            search_terms.append(str(root_cause))

        search_terms.append(f"{issue_name} SOP")
        search_terms.append(f"{issue_name} troubleshooting")

        for customer in issue_data.get("affected_customers", []) or []:
            search_terms.append(f"{customer} {issue_name}")

        seen_terms = set()
        unique_terms = []
        for term in search_terms:
            normalized = term.strip()
            key = normalized.lower()
            if normalized and key not in seen_terms:
                seen_terms.add(key)
                unique_terms.append(normalized)

        seen_sources: Dict[str, set] = {source_type: set() for source_type in gathered}

        for term in unique_terms:
            try:
                results = self._search_documents_with_fallback(term)
            except Exception:
                logger.exception(
                    "Document search failed during issue investigation for term: %s",
                    term,
                )
                continue

            if not results or not results.get("results"):
                continue

            for result in results["results"]:
                doc_type = self._classify_document_result(result)

                if doc_type not in gathered:
                    continue

                source_key = result.get("source", result.get("title", "Unknown"))
                if source_key in seen_sources[doc_type]:
                    continue
                seen_sources[doc_type].add(source_key)

                normalized_result = dict(result)
                normalized_result["type"] = doc_type

                if not normalized_result.get("priority"):
                    normalized_result["priority"] = self.source_priority_values.get(
                        doc_type, 50
                    )

                gathered[doc_type].append(normalized_result)

        return gathered

    def _format_issue_investigation(
        self,
        issue_name: str,
        issue_data: dict,
        gathered_evidence: dict,
    ) -> str:
        lines: List[str] = []

        lines.append(f"**🔍 INVESTIGATION: {issue_name}**")
        lines.append("")

        lines.append("**🤖 ROOT CAUSE**")
        root_cause = (
            issue_data.get("root_cause")
            or "Not yet determined from available operational data."
        )
        lines.append(str(root_cause))
        lines.append("")

        lines.append("**📊 OPERATIONAL SNAPSHOT**")
        snapshot: List[str] = []

        if issue_data.get("tickets") is not None:
            snapshot.append(f"Tickets affected: {issue_data['tickets']}")
        if issue_data.get("severity"):
            snapshot.append(f"Severity: {issue_data['severity']}")
        if issue_data.get("trend"):
            pct = issue_data.get("trend_percentage")
            pct_str = f" ({pct}%)" if pct is not None else ""
            snapshot.append(f"Trend: {issue_data['trend']}{pct_str}")
        if issue_data.get("avg_resolution_time"):
            snapshot.append(f"Avg resolution time: {issue_data['avg_resolution_time']}")
        if issue_data.get("sla_impact"):
            snapshot.append(f"SLA impact: {issue_data['sla_impact']}")
        if issue_data.get("first_detected"):
            snapshot.append(f"First detected: {issue_data['first_detected']}")
        if issue_data.get("affected_customers"):
            snapshot.append(
                "Affected customers: " + ", ".join(issue_data["affected_customers"])
            )

        if not snapshot:
            snapshot.append("No structured metrics were provided for this issue.")

        lines.extend(f"• {item}" for item in snapshot)
        lines.append("")

        lines.append("**📚 SUPPORTING EVIDENCE**")
        evidence_found = False

        for source_type in self.source_priority:
            results = gathered_evidence.get(source_type, [])

            for result in results[:2]:
                source = result.get("source", result.get("title", "Unknown source"))
                lines.append(f"• {self.source_priority_labels[source_type]}: {source}")
                evidence_found = True

        if not evidence_found:
            lines.append(
                "• No directly relevant documents were found in the knowledge base for this issue."
            )
        lines.append("")

        lines.append("**✅ RECOMMENDATION**")
        recommendation = issue_data.get("recommendation") or (
            "Escalate to the relevant operations owner for further review."
        )
        lines.append(str(recommendation))

        return "\n".join(lines)

    def _format_issue_investigation_fallback(
        self, issue_name: str, issue_data: dict
    ) -> str:
        lines: List[str] = []

        lines.append(f"**🔍 INVESTIGATION: {issue_name}**")
        lines.append("")
        lines.append(
            "⚠️ Document search was unavailable, so this summary is based only "
            "on known operational data."
        )
        lines.append("")

        lines.append("**🤖 ROOT CAUSE**")
        lines.append(str(issue_data.get("root_cause") or "Unknown"))
        lines.append("")

        lines.append("**✅ RECOMMENDATION**")
        lines.append(
            str(
                issue_data.get("recommendation")
                or "Escalate to the relevant operations owner for further review."
            )
        )

        return "\n".join(lines)

    # ============================================================
    # EXTRACTION HELPERS
    # ============================================================

    def _extract_order_id(self, query: str) -> Optional[str]:
        match = re.search(r"\bORD-\d+\b", query.upper())
        return match.group(0) if match else None

    def _extract_ticket_id(self, query: str) -> Optional[str]:
        match = re.search(r"\b(?:TKT|TCK)-\d+\b", query.upper())
        return match.group(0) if match else None

    def _extract_account_name(self, query: str) -> Optional[str]:
        known_accounts = ["Northstar", "LumenWorks", "Beacon"]
        text = query.lower()

        for account in known_accounts:
            if account.lower() in text:
                return account

        return None

    # ============================================================
    # GENERAL / HELP
    # ============================================================

    def _handle_general(self, query: str) -> str:
        normalized = query.lower().strip()

        greetings = {
            "hello",
            "hi",
            "hey",
            "good morning",
            "good afternoon",
            "good evening",
        }

        if normalized in greetings:
            return """👋 **Hello! I'm ParcelPilot.**

I'm an AI support agent for logistics operations.

**I can help with:**

📄 **Document Search**
Find policies, SOPs, agreements and operational guidance.

📊 **Data Lookup**
Check orders, tickets and customer accounts.

🧠 **Evidence-Based Reasoning**
Combine operational data with company documents.

⚡ **Actions**
Create escalations with human confirmation.

**Try:**
- "What is the cancellation policy?"
- "Look up order ORD-1001"
- "Can Northstar cancel this order without a fee?"
- "Escalate ticket TKT-501"
"""

        try:
            results = self._search_documents_with_fallback(
                query, account_name=self._extract_account_name(query)
            )
        except Exception:
            logger.exception("Fallback document search failed in _handle_general")
            results = None

        if results and results.get("results"):
            return self._format_document_results(results)

        return f"""I'm not sure how to help with **"{query}"**.

Try one of these:

📄 "What is the cancellation policy?"
📊 "Look up order ORD-1001"
🧠 "Can this customer cancel without a fee?"
⚡ "Escalate ticket TKT-501"
"""
