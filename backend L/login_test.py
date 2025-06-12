from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

app = FastAPI()

class Token(BaseModel):
    access_token: str
    token_type: str

@app.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username != "awn@example.com" or form_data.password != "secret123":
        raise HTTPException(status_code=403, detail="Invalid credentials")

    return {
        "access_token": "this-is-a-fake-token",
        "token_type": "bearer"
    }
