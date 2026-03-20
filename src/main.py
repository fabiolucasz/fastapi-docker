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

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.post("/login/access-token")
def login(db: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
          ) -> Token:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = crud.authenticate(
        db=db, 
        email=form_data.username, 
        password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    elif not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return Token(
        access_token=security.create_access_token(
            user.id, expires_delta=access_token_expires
        )
    )
    
@app.post("/signup", response_model=schemas.User)
async def create_user(db: SessionDep, user: schemas.UserCreate):
    db_user = crud.get_user(db=db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered",
        )
    return crud.create_user(db, user)

@app.get("/users/me", response_model=schemas.User)
async def read_users_me(current_user: CurrentUser, db: SessionDep):
    db_user = crud.get_user(db, user_id=current_user.id)
    return db_user


@app.middleware("http")
async def add_process_time_header_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

@app.get("/")
async def home():
    return {"message": "Welcome to the API"}