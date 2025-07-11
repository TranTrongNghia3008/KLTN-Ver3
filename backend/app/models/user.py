from pydantic import BaseModel, EmailStr
from typing import Optional

class UserIn(BaseModel):
    Name: str
    Email: EmailStr
    Password: str
    Avatar: Optional[str] = "/images/default-user-image.png"
    
class LoginUser(BaseModel):
    Email: EmailStr
    Password: str
