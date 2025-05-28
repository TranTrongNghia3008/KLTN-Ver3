from fastapi import APIRouter, HTTPException, Depends
from app.models.user import UserIn, UserOut, LoginUser
from app.services.auth_service import register_user, authenticate_user
from app.utils.security import create_access_token

router = APIRouter()

@router.post("/register")
def register(user: UserIn):
    if user.Email is None:
        raise HTTPException(status_code=400, detail="Email is required")
    user_id = register_user(user)
    if not user_id:
        raise HTTPException(status_code=400, detail="Email already registered")
    return {"message": "User registered successfully"}

@router.post("/login")
def login(user: LoginUser):
    user_db = authenticate_user(user.Email, user.Password)
    if not user_db:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = create_access_token(data={"sub": user_db["Email"]})
    return {"access_token": token, "token_type": "bearer", "user": UserOut(**user_db)}

@router.post("/logout")
def logout():
    # Frontend can remove token, backend can manage blacklist if needed
    return {"message": "Logout successful"}
