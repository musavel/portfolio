from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel, EmailStr
from backend.database.session import Database
from backend.core.security import hash_password, verify_password, create_jwt
import uuid
import jwt

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import Config

router = APIRouter()

class MemberCreate(BaseModel):
    email: EmailStr
    password: str
    user_type: str

class MemberLogin(BaseModel):
    email: EmailStr
    password: str
    user_type: str

@router.post("/register")
def signup(member: MemberCreate):
    hashed_password = hash_password(member.password)
    member_id = str(uuid.uuid4())

    with Database() as db:
        try:
            db.execute(
                "INSERT INTO members (id, email, password_hash, user_type) VALUES (%s, %s, %s, %s)", 
                (member_id, member.email, hashed_password, member.user_type), 
                commit=True
            )
        except Exception:
            raise HTTPException(status_code=400, detail="이미 가입된 이메일 입니다.")
    
    return {"message": "회원가입 성공"}

@router.post("/login")
def login(member: MemberLogin, request: Request):
    with Database() as db:
        cur = db.execute(
            "SELECT * FROM members WHERE email = %s AND user_type = %s", 
            (member.email, member.user_type)
        )
        db_member = cur.fetchone()

    if db_member is None:
        raise HTTPException(status_code=401, detail="등록되지 않은 계정입니다.")
    if not verify_password(member.password, db_member["password_hash"]):
        raise HTTPException(status_code=401, detail="비밀번호가 틀렸습니다.")

    token = create_jwt(member.email, member.user_type)  # user_type 추가

    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": db_member["id"],
        "email": db_member["email"],
        "user_type": db_member["user_type"]
    }
    
def get_current_user(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="인증 토큰이 필요합니다.")
    
    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
        email = payload["sub"]
        user_type = payload["user_type"]  # JWT에서 user_type도 가져옴
        
        # DB에서 email과 user_type 모두 확인
        with Database() as db:
            cur = db.execute(
                "SELECT email, user_type FROM members WHERE email = %s AND user_type = %s",
                (email, user_type)
            )
            user = cur.fetchone()
            
            if not user:
                raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
            
            return {"email": user["email"], "user_type": user["user_type"]}
            
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="토큰이 만료되었습니다.")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.")

@router.get("/me")
def get_user_info(current_user: dict = Depends(get_current_user)):
    with Database() as db:
        cur = db.execute(
            "SELECT email, user_type FROM members WHERE email = %s AND user_type = %s",
            (current_user["email"], current_user["user_type"])
        )
        user = cur.fetchone()
        
        if not user:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
        
        return {
            "email": user["email"],
            "user_type": user["user_type"]
        }