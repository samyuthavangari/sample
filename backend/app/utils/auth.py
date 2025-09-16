# backend/app/utils/auth.py
from flask_jwt_extended import jwt_required, get_jwt

def role_required(role):
    def wrapper(fn):
        @jwt_required()
        def decorator(*args, **kwargs):
            claims = get_jwt()
            # identity stored as {"id": id, "role": role} — adjust if you used different claim
            identity = claims.get("sub") or claims.get("identity") or claims
            user_role = None
            if isinstance(identity, dict):
                user_role = identity.get("role") or identity.get("role")
            else:
                user_role = claims.get("role")
            if user_role != role:
                return {"error": "Unauthorized"}, 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper
