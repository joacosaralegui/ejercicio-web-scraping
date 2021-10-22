from typing import Dict
from fastapi import APIRouter, HTTPException

from app.api import services
from app.api.models import CrawlResponse, CrawlRequest
from typing import Dict
from datetime import datetime

# This endpoints router
router = APIRouter()

@router.post("/scraping/", response_model=CrawlResponse)
async def get_links_on_website(payload : CrawlRequest):
    url = payload.url

    return await services.handle_scraping_request(url)
