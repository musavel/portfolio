from fastapi import APIRouter
from pydantic import BaseModel
from backend.services.generator import Generator

router = APIRouter()

class JDRequest(BaseModel):
    position: str
    experience: str
    
class QARequest(BaseModel):
    position: str
    experience: str
    num: int

@router.post("/generate/description")
def generate_description_api(req: JDRequest):
    generator = Generator(use_llm=True, temperature=0.5)
    result = generator.generate_description(req.position, req.experience)
    return {"text": result}

@router.post("/generate/question")
def generate_question_api(req: QARequest):
    generator = Generator(use_llm=True, temperature=0.5)
    result = generator.generate_question(req.position, req.experience, req.num)
    return {"text": result}