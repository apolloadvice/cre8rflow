"""
Main FastAPI application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import nlp_edit

# Create FastAPI application
app = FastAPI(
    title="Cre8rFlow Test API",
    description="Test API for Cre8rFlow",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(nlp_edit.router, prefix="/nlp") 