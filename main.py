from fastapi import FastAPI
from review_ai.server.routes import router as review_router
from userchatbot_ai.server.routes import router as chatbot_router

app = FastAPI(
    title = "TEKCIT-AI API",
    description="",
    version="1.0.0"
)
app.include_router(review_router, prefix="/review")
app.include_router(chatbot_router, prefix="/chat")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("review_ai.server.main:app", host="0.0.0.0", port=8084, reload=True)