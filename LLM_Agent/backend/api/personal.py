from typing import Dict, Optional
from fastapi import APIRouter
from pydantic import BaseModel
from backend.database.session import Database
from backend.services.generator import Generator
from backend.services.chat_history import save_chat_history, get_chat_history, get_chat_content

router = APIRouter()
    
class QARequest(BaseModel):
    position: str
    experience: str
    samples: Dict[str, int]

class FollowupRequest(BaseModel):
    position: str
    experience: str
    previous_question: str
    user_answer: str

class FeedbackRequest(BaseModel):
    position: str
    experience: str
    interview_history: Dict[str, list]

class AnswerRequest(BaseModel):
    position: str
    experience: str
    interview_history: Dict[str, list]
    
class ChatHistoryRequest(BaseModel):
    chat_id: str
    user_id: str
    position: str
    experience: str
    timestamp: str

@router.post("/generate/interview")
def generate_interview_api(req: QARequest):
    generator = Generator(use_llm=False, temperature=0.75)
    result = generator.generate_interview(req.position, req.experience, req.samples)
    return result

@router.post("/generate/followup")
def generate_followup_api(req: FollowupRequest):
    generator = Generator(use_llm=True, temperature=0.9)
    followup_question = generator.generate_followup(
        position=req.position,
        experience=req.experience,
        previous_question=req.previous_question,
        user_answer=req.user_answer
    )
    
    return {"text": followup_question}

@router.post("/generate/feedback")
def generate_feedback_api(req: FeedbackRequest):
    generator = Generator(use_llm=True, temperature=0.25)
    feedback = generator.generate_feedback(
        position=req.position,
        experience=req.experience,
        interview_history=req.interview_history
    )
    
    return {"text": feedback}

@router.post("/generate/answer")
def generate_answer_api(req: AnswerRequest):
    generator = Generator(use_llm=True, temperature=0.25)
    answer = generator.generate_answer(
        position=req.position,
        experience=req.experience,
        interview_history=req.interview_history
    )
    
    return {"text": answer} 

@router.post("/save/chat_history")
def save_chat_history_api(req: ChatHistoryRequest):
    save_chat_history(req.chat_id, req.user_id, req.position, req.experience, req.timestamp)
    return {"message": "대화 기록 저장 성공"}

@router.get("/get/chat_history/{user_id}")
def get_chat_history_api(user_id: str):
    result = get_chat_history(user_id)
    return result

@router.get("/get/chat_content/{user_id}/{chat_id}")
def get_chat_content_api(user_id: str, chat_id: str):
    result = get_chat_content(user_id, chat_id)
    return result
