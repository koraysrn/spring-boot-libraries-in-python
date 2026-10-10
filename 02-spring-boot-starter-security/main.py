"""
Python equivalent of the spring-boot-starter-security library.

Spring Boot equivalents:
    - SecurityFilterChain                      -> FastAPI dependencies
    - Authentication                           -> JWT bearer tokens + user lookup
    - Authorization                            -> role based dependency checks
    - BCryptPasswordEncoder                    -> the bcrypt library
    - UsernamePasswordAuthenticationFilter     -> the /auth/login endpoint

This module demonstrates authentication, authorization, password hashing,
JWT issuance and validation with a focus on non-happy-path resilience.
"""

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

import security
from models import Token, User, UserCreate
from store import user_store

app = FastAPI(title="Finance API - Python equivalent of spring-boot-starter-security")

# A dummy hash is verified for unknown users so that the response time does
# not reveal whether a username exists (timing attack protection).
DUMMY_PASSWORD_HASH = security.hash_password("dummy-password-for-timing")


def seed_users():
    if user_store.get_by_username("admin") is None:
        user_store.create("admin", security.hash_password("adminpass123"), "ADMIN")
    if user_store.get_by_username("alice") is None:
        user_store.create("alice", security.hash_password("alicepass123"), "USER")


seed_users()


@app.post("/auth/register", response_model=User, status_code=201)
def register(payload: UserCreate):
    if user_store.get_by_username(payload.username) is not None:
        raise HTTPException(status_code=409, detail="Username already exists")
    password_hash = security.hash_password(payload.password)
    user = user_store.create(payload.username, password_hash, role="USER")
    return user


@app.post("/auth/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = user_store.get_by_username(form_data.username)
    if user is None:
        # Run a hash comparison anyway to keep timing consistent with the
        # existing-user path and avoid username enumeration through timing.
        security.verify_password(form_data.password, DUMMY_PASSWORD_HASH)
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not security.verify_password(form_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = security.create_access_token(
        {"sub": user["username"], "role": user["role"]}
    )
    return {"access_token": token, "token_type": "bearer"}


@app.get("/public")
def public():
    return {"message": "Public endpoint, no authentication required"}


@app.get("/me", response_model=User)
def me(current_user: dict = Depends(security.get_current_user)):
    return current_user


@app.get("/admin/users", response_model=list[User])
def admin_users(current_user: dict = Depends(security.require_role("ADMIN"))):
    return user_store.all()
