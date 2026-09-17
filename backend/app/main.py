from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import chat, customers, bookings, actions, policies, escalations

app = FastAPI(
    title="Airline Resolution Agent API",
    description=(
        "Deterministic policy-engine-backed API for the Airline Resolution Agent prototype. "
        "All eligibility and compensation decisions are made by app/services/policy_engine.py, "
        "not by an LLM."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # local prototype only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(customers.router)
app.include_router(bookings.router)
app.include_router(chat.router)
app.include_router(actions.router)
app.include_router(policies.router)
app.include_router(escalations.router)


@app.get("/")
def root():
    return {
        "service": "Airline Resolution Agent API",
        "status": "ok",
        "docs": "/docs",
    }


@app.get("/api/health")
def health():
    return {"status": "healthy"}