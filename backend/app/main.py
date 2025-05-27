from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth_routes

app = FastAPI()

# CORS để frontend gọi API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # chỉnh theo domain thực tế
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router, prefix="/auth")
