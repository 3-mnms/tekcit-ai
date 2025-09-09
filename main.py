from fastapi import FastAPI
from review_ai.server.routes import router as review_router
from userchatbot_ai.server.routes import router as chatbot_router
from activity_ai.server.routes import router as activity_router

app = FastAPI(
    title = "TEKCIT-AI API",
    description="",
    version="1.0.0"
)
app.include_router(review_router, prefix="/review")
app.include_router(chatbot_router, prefix="/chat")
app.include_router(activity_router, prefix="/activity")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8084, reload=True)