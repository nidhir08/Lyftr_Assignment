from fastapi import FastAPI
from .api import router as api_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Lyftr Scraper Assignment")
app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],
  allow_methods=["*"],
  allow_headers=["*"],
)
app.include_router(api_router)
