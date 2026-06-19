from fastapi import FastAPI

from recommendation.router import router as recommendation_router
from chatbot.router import router as chatbot_router
from risk_assessment.router import router as risk_assessment_router
from roi_prediction.router import router as roi_prediction_router

app = FastAPI(title="Igudar AI Microservice", version="1.0.0")

app.include_router(recommendation_router)
app.include_router(chatbot_router)
app.include_router(risk_assessment_router)
app.include_router(roi_prediction_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
