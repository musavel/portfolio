from fastapi import FastAPI
from backend.api import auth
from backend.api import company
from backend.api import personal

app = FastAPI()
app.include_router(auth.router, prefix='/auth')
app.include_router(company.router, prefix='/company')
app.include_router(personal.router, prefix='/personal')
