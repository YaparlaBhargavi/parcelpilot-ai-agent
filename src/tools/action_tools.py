# src/tools/action_tools.py
from datetime import datetime, timezone


class ActionTools:
    """Tools for performing actions with confirmation."""

    def __init__(self):
        self.confirmation_required = True
        self.pending_actions = {}
        self.action_counter = 0

    def _get_current_time(self):
        """Get current UTC time with timezone."""
        return datetime.now(timezone.utc)

    def create_escalation(
        self, order_id: str, reason: str, priority: str = "HIGH"
    ) -> dict:
        """Create escalation ticket with confirmation."""
        if self.confirmation_required:
            action_id = f"ESC_{self.action_counter}"
            self.action_counter += 1

            self.pending_actions[action_id] = {
                "type": "escalation",
                "order_id": order_id,
                "reason": reason,
                "priority": priority,
            }

            return {
                "action_id": action_id,
                "action": "escalation",
                "status": "pending_confirmation",
                "data": {
                    "order_id": order_id,
                    "reason": reason,
                    "priority": priority,
                    "timestamp": self._get_current_time().isoformat(),
                },
                "confirmation_needed": True,
                "message": f"Do you want to escalate order {order_id} with priority {priority}?",
            }
        else:
            return self._execute_escalation(order_id, reason, priority)

    def _execute_escalation(self, order_id: str, reason: str, priority: str) -> dict:
        """Actually execute escalation."""
        current_time = self._get_current_time()
        return {
            "action": "escalation",
            "status": "executed",
            "data": {
                "order_id": order_id,
                "reason": reason,
                "priority": priority,
                "timestamp": current_time.isoformat(),
                "ticket_id": f"ESC-{current_time.strftime('%Y%m%d')}-{order_id}",
            },
        }

    def update_ticket(self, ticket_id: str, update_data: dict) -> dict:
        """Update ticket with confirmation."""
        if self.confirmation_required:
            action_id = f"TKT_{self.action_counter}"
            self.action_counter += 1

            self.pending_actions[action_id] = {
                "type": "ticket_update",
                "ticket_id": ticket_id,
                "update_data": update_data,
            }

            return {
                "action_id": action_id,
                "action": "ticket_update",
                "status": "pending_confirmation",
                "data": {
                    "ticket_id": ticket_id,
                    "updates": update_data,
                    "timestamp": self._get_current_time().isoformat(),
                },
                "confirmation_needed": True,
                "message": f"Do you want to update ticket {ticket_id} with these changes?",
            }
        else:
            return self._execute_ticket_update(ticket_id, update_data)

    def _execute_ticket_update(self, ticket_id: str, update_data: dict) -> dict:
        """Actually update ticket."""
        return {
            "action": "ticket_update",
            "status": "executed",
            "data": {
                "ticket_id": ticket_id,
                "updates": update_data,
                "timestamp": self._get_current_time().isoformat(),
            },
        }

    def confirm_action(self, action_id: str) -> dict:
        """Confirm pending action."""
        if action_id in self.pending_actions:
            action = self.pending_actions[action_id]

            # Execute based on type
            if action["type"] == "escalation":
                result = self._execute_escalation(
                    action["order_id"], action["reason"], action["priority"]
                )
            elif action["type"] == "ticket_update":
                result = self._execute_ticket_update(
                    action["ticket_id"], action["update_data"]
                )
            else:
                result = {"status": "error", "message": "Unknown action type"}

            # Remove from pending
            del self.pending_actions[action_id]

            return {
                "status": "confirmed",
                "action_id": action_id,
                "result": result,
                "message": "Action confirmed and executed",
                "timestamp": self._get_current_time().isoformat(),
            }
        else:
            return {"status": "error", "message": "Action not found"}

    def cancel_action(self, action_id: str) -> dict:
        """Cancel pending action."""
        if action_id in self.pending_actions:
            del self.pending_actions[action_id]
            return {
                "status": "cancelled",
                "action_id": action_id,
                "message": "Action cancelled",
                "timestamp": self._get_current_time().isoformat(),
            }
        else:
            return {"status": "error", "message": "Action not found"}

    def get_pending_actions(self) -> dict:
        """Get all pending actions."""
        return {
            "pending_count": len(self.pending_actions),
            "actions": self.pending_actions,
            "timestamp": self._get_current_time().isoformat(),
        }
