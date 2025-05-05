import os
import sys
import json
from backend.database.session import Database

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import Config

def save_chat_history(chat_id: str, user_id: str, position: str, experience: str, timestamp: str):
    with Database() as db:
        db.execute(
            "INSERT INTO chat_history (id, user_id, position_name, experience, created_at) VALUES (%s, %s, %s, %s, %s)",
            (chat_id, user_id, position, experience, timestamp),
            commit=True
        )
        
def get_chat_history(user_id: str):
    with Database() as db:
        result = db.execute(
            "SELECT * FROM chat_history WHERE user_id = %s ORDER BY created_at DESC",
            (user_id,)
        ).fetchall()
    return result

def get_chat_content(user_id: str, chat_id: str):    
    chat_data_path = f"{Config.CHAT_HISTORY_PATH}/{user_id}/{chat_id}.json"
    
    with open(chat_data_path, 'r', encoding='utf-8') as f:
        chat_data = json.load(f)
    
    info_data = chat_data["interview_info"]
    message_data = chat_data["conversation"]["messages"]
    feedback_data = chat_data["feedback"]["text"]
    example_answers_data = chat_data["example_answers"]["text"]
    
    return {
        "info": info_data,
        "messages": message_data,
        "feedback": feedback_data,
        "example_answers": example_answers_data
    }
