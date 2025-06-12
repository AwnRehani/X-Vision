from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas, database
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm
#from app.token import create_access_token
router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Dependency to get DB session
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/signup", response_model=schemas.UserCreate)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = pwd_context.hash(user.password)
    new_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_pw
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return user


@router.post("/login", response_model=schemas.Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    # DEBUG LOG: show what we got
    print(f"➡️ Login attempt: username={form_data.username!r}, password={form_data.password!r}")

    # 1) Fetch the user by email
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    print("   ↳ DB user:", user)

    # 2) Verify credentials
    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
        print("   ↳ Invalid credentials, returning 403")
        raise HTTPException(status_code=403, detail="Invalid credentials")

    # 3) Inline import of token helper
    from app.token import create_access_token

    # 4) Create and return the JWT
    access_token = create_access_token(data={"user_id": user.id})
    print("   ↳ Token generated, returning success")
    return {"access_token": access_token, "token_type": "bearer"}


