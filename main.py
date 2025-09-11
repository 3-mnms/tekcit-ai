from fastapi import FastAPI
from review_ai.server.routes import router as review_router
from userchatbot_ai.server.routes import router as chatbot_router
from activity_ai.server.routes import router as activity_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title = "TEKCIT-AI API",
    description="",
    version="1.0.0"
)

origins = [
    "https://m.rookies-tekcit.com",
    "http://localhost:3000"
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(review_router, prefix="/review")
app.include_router(chatbot_router, prefix="/chat")
app.include_router(activity_router, prefix="/activity")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8084, reload=True)