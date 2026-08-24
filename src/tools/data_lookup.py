# src/tools/data_lookup.py
from src.database.database import DatabaseManager
from src.security.access_control import AccessControl


class DataLookupTool:
    """Tool for looking up structured data from Excel/SQLite database."""

    def __init__(self):
        self.db = DatabaseManager()
        self.access_control = AccessControl()

    def lookup_order(self, order_id, user_context):
        """Look up order details with access control."""
        # Security check
        if not self.access_control.can_access_order(user_context, order_id):
            return {"error": "Access denied"}

        result = self.db.lookup_order(order_id)
        if result is not None and not result.empty:
            return result.to_dict("records")[0]
        return {"error": "Order not found"}

    def lookup_account(self, account_name):
        """Look up account details."""
        result = self.db.lookup_account(account_name)
        if result is not None and not result.empty:
            return result.to_dict("records")[0]
        return {"error": "Account not found"}

    def lookup_ticket(self, ticket_id):
        """Look up ticket details."""
        result = self.db.lookup_ticket(ticket_id)
        if result is not None and not result.empty:
            return result.to_dict("records")[0]
        return {"error": "Ticket not found"}

    def calculate_service_credit(self, order_id, issue_duration_hours):
        """Calculate service credit based on SLA."""
        # This would use SLA thresholds from documents and Excel
        if issue_duration_hours > 4:
            return {"credit_percentage": 100, "amount": "Full refund"}
        elif issue_duration_hours > 2:
            return {"credit_percentage": 50, "amount": "50% of order value"}
        else:
            return {"credit_percentage": 0, "amount": "No credit"}

    def get_customer_orders(self, customer_id):
        """Get all orders for a customer."""
        sql = f"SELECT * FROM orders WHERE customer_id = '{customer_id}'"
        return self.db.query(sql)
