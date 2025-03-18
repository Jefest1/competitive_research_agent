from fastapi import APIRouter, Depends, HTTPException
from dependencies.research_agent import CompetitiveResearchAgent
from core.config import settings
from core.exceptions import (
    CompetitiveResearchException,
    APIKeyError,
    SearchError,
    ModelProcessingError
)
from schemas.models import ResearchRequest, ResearchReport
from datetime import datetime

router = APIRouter()


def get_research_agent():
    try:
        return CompetitiveResearchAgent(
            # Use your Groq API key here.
            groq_api_key=settings.GROQ_API_KEY
        )
    except APIKeyError as e:
        raise HTTPException(
            status_code=500, detail=f"Authentication failed: {str(e)}")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to initialize research agent: {str(e)}")


@router.post("/generate-report/", response_model=ResearchReport)
async def generate_research_report(
    request: ResearchRequest,
    agent: CompetitiveResearchAgent = Depends(get_research_agent)
):
    try:
        if request.end_date < request.start_date:
            raise HTTPException(
                status_code=400, detail="End date must be after start date")
        if len(request.competitors) > 10:
            raise HTTPException(
                status_code=400, detail="Maximum 10 competitors allowed per request")

        report = await agent.generate_report(
            competitors=request.competitors,
            start_date=request.start_date,
            end_date=request.end_date
        )
        return report

    except APIKeyError as e:
        raise HTTPException(status_code=500, detail=f"API key error: {str(e)}")
    except SearchError as e:
        raise HTTPException(
            status_code=502, detail=f"Search service error: {str(e)}")
    except ModelProcessingError as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing search results: {str(e)}")
    except CompetitiveResearchException as e:
        raise HTTPException(
            status_code=500, detail=f"Research generation failed: {str(e)}")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Unexpected error: {str(e)}")
