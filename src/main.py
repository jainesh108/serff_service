from fastapi import FastAPI, HTTPException

from src.models.search_model import SearchRequest
from src.scraper.scraper import run_serff_search

app = FastAPI()


@app.post("/search")
async def search_serff(search_request: SearchRequest):
    try:
        results = await run_serff_search(search_request)
        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Automation task failed: {str(e)}")

