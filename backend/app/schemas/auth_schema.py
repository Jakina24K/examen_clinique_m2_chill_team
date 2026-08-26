from pydantic import BaseModel, EmailStr, ConfigDict

class LoginRequest(BaseModel):
    email: EmailStr
    mot_de_passe: str

class LoginResponse(BaseModel):
    token: str
    token_type: str = "bearer"
    role: str
    
    model_config = ConfigDict(from_attributes=True)

class RegisterRequest(BaseModel):
    nom: str
    prenom: str 
    email: EmailStr
    mot_de_passe: str

class RegisterResponse(BaseModel):
    id: str
    nom: str
    prenom: str
    email: EmailStr
    role: str
    
    model_config = ConfigDict(from_attributes=True)

class CurrentUserResponse(BaseModel):
    id: str
    nom: str
    prenom: str
    email: EmailStr
    role: str
    actif: bool
    
    model_config = ConfigDict(from_attributes=True)