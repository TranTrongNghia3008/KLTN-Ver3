from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth_routes
from app.routes.chatbot_routes import router as chatbot_router
from app.routes.session_routes import router as session_router
from app.routes.conversations import router as conversation_router
from app.routes.detect import router as detect
from app.routes.cheapfake_routers import router as cheapfake_router
from app.routes.deepfake_routers import router as deepfake_router

app = FastAPI()

# CORS để frontend gọi API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # chỉnh theo domain thực tế
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Hello from Render!"}

app.include_router(auth_routes.router, prefix="/auth")
app.include_router(chatbot_router)
app.include_router(session_router)
app.include_router(conversation_router)
app.include_router(cheapfake_router)
app.include_router(deepfake_router)
app.include_router(detect, prefix="/deepfake")
