import time
from datetime import timedelta
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm

from src.core import crud, models, schemas, security
from src.core.config import settings
from src.core.db import engine
from src.core.deps import CurrentUser, SessionDep
from src.core.schemas import Token
from src.core.logging_config import log_auth_attempt, log_user_operation
from src.core.metrics import MetricsManager, metrics_endpoint
from src.core.rate_limiter import check_rate_limit, login_limiter, signup_limiter, check_brute_force, reset_failed_attempts

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.post("/login/access-token")
def login(request: Request, db: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
          ) -> Token:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    client_ip = request.client.host
    
    # Verificar rate limit
    check_rate_limit(request, login_limiter, "/login/access-token")
    
    # Verificar brute force
    if check_brute_force(client_ip, form_data.username):
        log_auth_attempt(
            email=form_data.username,
            ip=client_ip,
            success=False,
            reason="brute_force_detected",
            endpoint="/login/access-token"
        )
        MetricsManager.record_auth_attempt("blocked", client_ip, "/login/access-token")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many failed attempts. Please try again later."
        )
    
    user = crud.authenticate(
        db=db, 
        email=form_data.username, 
        password=form_data.password
    )
    
    if not user:
        log_auth_attempt(
            email=form_data.username,
            ip=client_ip,
            success=False,
            reason="invalid_credentials",
            endpoint="/login/access-token"
        )
        MetricsManager.record_auth_attempt("failed", client_ip, "/login/access-token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    elif not security.verify_password(form_data.password, user.hashed_password):
        log_auth_attempt(
            email=form_data.username,
            ip=client_ip,
            success=False,
            reason="invalid_password",
            endpoint="/login/access-token"
        )
        MetricsManager.record_auth_attempt("failed", client_ip, "/login/access-token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Login bem-sucedido
    reset_failed_attempts(client_ip, form_data.username)
    log_auth_attempt(
        email=form_data.username,
        ip=client_ip,
        success=True,
        endpoint="/login/access-token"
    )
    MetricsManager.record_auth_attempt("success", client_ip, "/login/access-token")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return Token(
        access_token=security.create_access_token(
            user.id, expires_delta=access_token_expires
        )
    )
    
@app.post("/signup", response_model=schemas.User)
async def create_user(request: Request, db: SessionDep, user: schemas.UserCreate):
    client_ip = request.client.host
    
    # Verificar rate limit
    check_rate_limit(request, signup_limiter, "/signup")
    
    db_user = crud.get_user(db=db, email=user.email)
    if db_user:
        log_user_operation(
            operation="user_creation",
            user_id=0,
            success=False,
            details={"email": user.email, "reason": "email_exists"}
        )
        MetricsManager.record_user_operation("create", "failed")
        raise HTTPException(
            status_code=400,
            detail="Email already registered",
        )
    
    try:
        created_user = crud.create_user(db, user)
        log_user_operation(
            operation="user_creation",
            user_id=created_user.id,
            success=True,
            details={"email": user.email}
        )
        MetricsManager.record_user_operation("create", "success")
        return created_user
    except Exception as e:
        log_user_operation(
            operation="user_creation",
            user_id=0,
            success=False,
            details={"email": user.email, "error": str(e)}
        )
        MetricsManager.record_user_operation("create", "error")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

@app.get("/users/me", response_model=schemas.User)
async def read_users_me(request: Request, current_user: CurrentUser, db: SessionDep):
    start_time = time.time()
    
    try:
        db_user = crud.get_user(db, user_id=current_user.id)
        
        # Registra métricas de validação de token
        validation_time = time.time() - start_time
        MetricsManager.record_token_validation_time(validation_time)
        
        log_user_operation(
            operation="get_user_profile",
            user_id=current_user.id,
            success=True
        )
        MetricsManager.record_user_operation("read", "success")
        
        return db_user
    except Exception as e:
        log_user_operation(
            operation="get_user_profile",
            user_id=current_user.id,
            success=False,
            details={"error": str(e)}
        )
        MetricsManager.record_user_operation("read", "error")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@app.middleware("http")
async def add_process_time_header_middleware(request: Request, call_next):
    start_time = time.time()
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Registra métricas da requisição
        MetricsManager.record_request_time(
            method=request.method,
            endpoint=request.url.path,
            status="success" if response.status_code < 400 else "error",
            duration=process_time
        )
        
        response.headers["X-Process-Time"] = str(process_time)
        return response
    except Exception as e:
        process_time = time.time() - start_time
        
        # Registra métricas de erro
        MetricsManager.record_request_time(
            method=request.method,
            endpoint=request.url.path,
            status="error",
            duration=process_time
        )
        
        raise e

@app.get("/")
async def home():
    return {
        "message": "Welcome to the FastAPI Authentication API",
        "version": "1.0.0",
        "endpoints": {
            "auth": {
                "login": "/login/access-token",
                "signup": "/signup"
            },
            "user": {
                "me": "/users/me"
            },
            "monitoring": {
                "metrics": "/metrics",
                "docs": "/docs"
            }
        }
    }

@app.get("/metrics")
async def metrics():
    """Endpoint Prometheus para métricas"""
    return metrics_endpoint()