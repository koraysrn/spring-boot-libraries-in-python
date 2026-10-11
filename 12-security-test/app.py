"""FastAPI app used to demonstrate spring-security-test equivalents.

Spring Boot equivalents:
    - @WithMockUser              -> dependency_overrides
    - SecurityIntegrationTest   -> this test suite
    - SecurityContext            -> get_current_user dependency
"""

import jwt
from fastapi import Depends, FastAPI, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

app = FastAPI(title="Finance API - spring-security-test equivalent")

SECRET_KEY = "test-secret-key-that-is-long-enough-for-hs256"
ALGORITHM = "HS256"

bearer_scheme = HTTPBearer(auto_error=False)

USERS = {
    "alice": {"username": "alice", "role": "USER"},
    "admin": {"username": "admin", "role": "ADMIN"},
}


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Security(bearer_scheme),
):
    if credentials is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(
            credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM]
        )
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    username = payload.get("sub")
    user = USERS.get(username)
    if user is None:
        raise HTTPException(status_code=401, detail="Unknown user")
    return user


def require_role(required_role: str):
    def dependency(current_user: dict = Depends(get_current_user)):
        if current_user.get("role") != required_role:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user

    return dependency


@app.get("/public")
def public():
    return {"message": "public"}


@app.get("/me")
def me(current_user: dict = Depends(get_current_user)):
    return current_user


@app.get("/admin/users")
def admin_users(current_user: dict = Depends(require_role("ADMIN"))):
    return list(USERS.values())


@app.post("/auth/login")
def login(payload: dict):
    username = payload.get("username")
    if username not in USERS:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = jwt.encode(
        {"sub": username, "role": USERS[username]["role"]},
        SECRET_KEY,
        algorithm=ALGORITHM,
    )
    return {"access_token": token}
