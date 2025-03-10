"""Backend API for the AI Agent Multi-Model Platform."""

from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, constr
from typing import List, Dict, Any, Optional
import jwt
import os
import socket
from datetime import datetime, timedelta
import logging
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from passlib.context import CryptContext
import secrets
import re
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Importaciones del proyecto
from langchain_agent_project.models import Base, User, Chat, Message
from langchain_agent_project.agents.multi_model_agent import MultiModelAgent

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def find_available_port(start_port: int = 8000, max_port: int = 8100) -> int:
    """Find an available port starting from start_port."""
    for port in range(start_port, max_port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind(('localhost', port))
                return port
            except OSError:
                continue
    raise RuntimeError(f"No available ports found between {start_port} and {max_port}")

# Puerto para la aplicación
PORT = int(os.getenv('API_PORT', find_available_port()))
HOST = os.getenv('API_HOST', 'localhost')

logger.info(f"Server will start on {HOST}:{PORT}")

# Configuración de la base de datos
SQLALCHEMY_DATABASE_URL = os.getenv('DATABASE_URL', "postgresql://postgres:postgres@localhost:5432/agent_db")
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Configuración de JWT
SECRET_KEY = os.getenv('SECRET_KEY', secrets.token_urlsafe(64))  # Genera una clave segura por defecto
ALGORITHM = os.getenv('JWT_ALGORITHM', "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', 30))

if os.getenv('SECRET_KEY') is None:
    logger.warning("No SECRET_KEY provided in environment variables. Using a generated key - this is secure but tokens will be invalidated on server restart.")

# Configuración de seguridad
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Configuración de CORS
ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000').split(',')

app = FastAPI(
    title="AI Agent Multi-Model Platform",
    description="API para la plataforma de agentes IA multi-modelo",
    version="1.0.0"
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configuración de seguridad para contraseñas
PASSWORD_MIN_LENGTH = 8
PASSWORD_PATTERN = re.compile(r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$')

class UserCreate(BaseModel):
    email: EmailStr
    username: constr(min_length=3, max_length=50)
    password: constr(min_length=PASSWORD_MIN_LENGTH)

    @validator('password')
    def validate_password(cls, v):
        if not PASSWORD_PATTERN.match(v):
            raise ValueError(
                'La contraseña debe tener al menos 8 caracteres, '
                'una letra, un número y un carácter especial'
            )
        return v

# SQL Injection Prevention
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# Modelos Pydantic para la API
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class ChatCreate(BaseModel):
    title: str

class MessageCreate(BaseModel):
    content: str
    role: str = "user"

# Funciones de utilidad
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except jwt.JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    return user

# Rutas de la API
@app.post("/token", response_model=Token)
@limiter.limit("5/minute")
async def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        # Añadir delay para prevenir timing attacks
        await asyncio.sleep(0.1)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users/", response_model=None)
@limiter.limit("3/minute")
async def create_user(
    request: Request,
    user: UserCreate,
    db: Session = Depends(get_db)
):
    # Validaciones adicionales
    if len(user.username) < 3:
        raise HTTPException(status_code=400, detail="El nombre de usuario debe tener al menos 3 caracteres")
    
    if not re.match(r'^[a-zA-Z0-9_-]+$', user.username):
        raise HTTPException(status_code=400, detail="El nombre de usuario solo puede contener letras, números, guiones y guiones bajos")
    
    # Verificar usuario existente
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Nombre de usuario ya registrado")
    
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email ya registrado")
    
    # Hash de la contraseña
    hashed_password = get_password_hash(user.password)
    
    # Crear usuario con datos sanitizados
    db_user = User(
        email=user.email.lower().strip(),
        username=user.username.strip(),
        hashed_password=hashed_password
    )
    
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return {"message": "Usuario creado exitosamente"}
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al crear usuario: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al crear usuario")

@app.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return {
        "username": current_user.username,
        "email": current_user.email,
        "id": current_user.id
    }

@app.post("/chats/", response_model=None)
async def create_chat(
    chat: ChatCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_chat = Chat(
        title=chat.title,
        user_id=current_user.id
    )
    db.add(db_chat)
    db.commit()
    db.refresh(db_chat)
    return db_chat

@app.get("/chats/", response_model=List[Dict])
async def get_user_chats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    chats = db.query(Chat).filter(Chat.user_id == current_user.id).all()
    return [{"id": chat.id, "title": chat.title, "created_at": chat.created_at} for chat in chats]

@app.post("/chats/{chat_id}/messages/", response_model=None)
async def create_message(
    chat_id: int,
    message: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    chat = db.query(Chat).filter(Chat.id == chat_id, Chat.user_id == current_user.id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    db_message = Message(
        chat_id=chat_id,
        content=message.content,
        role=message.role
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    
    # TODO: Aquí se procesará el mensaje con el agente de IA
    # Por ahora, solo devolvemos un mensaje de eco
    assistant_message = Message(
        chat_id=chat_id,
        content=f"Echo: {message.content}",
        role="assistant"
    )
    db.add(assistant_message)
    db.commit()
    
    return {
        "user_message": db_message,
        "assistant_message": assistant_message
    }

@app.get("/chats/{chat_id}/messages/", response_model=List[Dict])
async def get_chat_messages(
    chat_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    chat = db.query(Chat).filter(Chat.id == chat_id, Chat.user_id == current_user.id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    messages = db.query(Message).filter(Message.chat_id == chat_id).order_by(Message.created_at).all()
    return [{
        "id": msg.id,
        "content": msg.content,
        "role": msg.role,
        "created_at": msg.created_at
    } for msg in messages]

@app.get("/health")
async def health_check():
    """Verificar el estado del servicio."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT) 