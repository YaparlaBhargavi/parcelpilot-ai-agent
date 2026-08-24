# src/security/access_control.py
import os
from datetime import datetime, timedelta

# Try to import jwt, but provide fallback if not installed
try:
    import jwt

    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False
    print("⚠️ PyJWT not installed. Using simplified auth.")


class AccessControl:
    """Access control for the ParcelPilot AI Agent."""

    def __init__(self):
        self.secret_key = os.getenv("SECRET_KEY", "dev_secret_key_12345")
        self.users = {
            "support_agent": {
                "role": "support_agent",
                "permissions": ["read", "escalate", "ticket_update"],
            },
            "operations": {
                "role": "operations",
                "permissions": ["read", "escalate", "ticket_update", "system_override"],
            },
            "viewer": {"role": "viewer", "permissions": ["read"]},
        }

    def authenticate(self, user_id, role):
        """Authenticate user and create token."""
        if role in self.users:
            if JWT_AVAILABLE:
                # Use JWT if available
                token = jwt.encode(
                    {
                        "user_id": user_id,
                        "role": role,
                        "exp": datetime.utcnow() + timedelta(hours=24),
                    },
                    self.secret_key,
                    algorithm="HS256",
                )
                return token
            else:
                # Simple token for testing
                return f"test_token_{user_id}_{role}"
        return None

    def verify_token(self, token):
        """Verify JWT token."""
        if not token:
            return None

        if JWT_AVAILABLE:
            try:
                payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
                return payload
            except jwt.ExpiredSignatureError:
                return None
            except jwt.InvalidTokenError:
                return None
        else:
            # Simple verification for testing
            if token.startswith("test_token_"):
                parts = token.split("_")
                if len(parts) >= 3:
                    return {
                        "user_id": parts[2],
                        "role": parts[3] if len(parts) > 3 else "support_agent",
                    }
            return None

    def check_permission(self, user_context, action):
        """Check if user has permission for action."""
        if not user_context:
            return False
        role = user_context.get("role", "viewer")
        user_permissions = self.users.get(role, {}).get("permissions", [])
        return action in user_permissions

    def can_access_order(self, user_context, order_id):
        """Check if user can access specific order."""
        if not user_context:
            return False

        role = user_context.get("role", "viewer")

        # Operations can access everything
        if role == "operations":
            return True

        # Support agents can access their supported accounts
        if role == "support_agent":
            supported_accounts = user_context.get("supported_accounts", [])
            # In production, this would check if the order belongs to a supported account
            return True

        # Viewers can only read
        if role == "viewer":
            return True

        return False

    def get_user_role(self, user_context):
        """Get user role from context."""
        if not user_context:
            return "viewer"
        return user_context.get("role", "viewer")
