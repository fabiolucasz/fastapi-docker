
from sqlalchemy.exc import ArgumentError
from sqlalchemy.orm import Session
from src.core import models,schemas
from src.core.security import verify_password, get_password_hash

def get_user(
    db: Session,
    user_id: int | None = None,
    email: str | None = None,
    ):
    if not any([user_id, email]):
        raise ArgumentError("Either user_id or email must be provided")
    query = db.query(models.User)
    if user_id:
        query = query.filter(models.User.id == user_id)
    if email:
        query = query.filter(models.User.email == email)
    user = query.first()
    return user

def get_users(db: Session, skip: int = 0, limit: int = 100):
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
        email=user.email, 
        hashed_password=get_password_hash(user.password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate(db: Session, email: str, password: str):
    db_user = get_user(db, email=email)
    if not db_user or not verify_password(password, db_user.hashed_password):
        return None
    return db_user
