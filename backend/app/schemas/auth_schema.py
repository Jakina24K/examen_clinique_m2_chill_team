from pydantic import BaseModel

class LoginRequest(BaseModel):
    email : str
    mot_de_passe : str

class LoginResponse(BaseModel):
    token : str
    role : str
    
    class Config:
        from_attributes = True

class RegisterRequest(BaseModel):
    nom: str
    prenom: str 
    email: str
    mot_de_passe: str

class RegisterResponse(BaseModel):
    id: str
    nom: str
    prenom: str
    
    class Config:
        from_attributes = True

class CurrentUserResponse(BaseModel):
    id: str
    nom: str
    prenom: str
    role: str
    
    class Config:
        from_attributes = True

