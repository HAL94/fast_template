from app.core.schema import BaseModel


class RegisterUserDto(BaseModel):
    full_name: str
    email: str
    password: str


class LoginUserDto(BaseModel):
    email: str
    password: str


class UserSession(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
