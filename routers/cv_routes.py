import json

from fastapi import APIRouter, UploadFile, File, HTTPException

from services.cv_service import (
    extract_pdf_text,
    analyze_cv_with_ai
)

from services.matching_service import match_jobs


router = APIRouter(
    prefix="/api/v1/cv",
    tags=["CV"]
)


@router.post("/analyze")
async def analyze_cv(file: UploadFile = File(...)):

    allowed_extensions = {".pdf", ".doc", ".docx"}

    filename = file.filename or ""

    extension = (
        "." + filename.rsplit(".", 1)[1].lower()
        if "." in filename
        else ""
    )

    # File validation
    if extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Only PDF, DOC, and DOCX files are allowed."
        )

    # Read file
    file_bytes = await file.read()

    # PDF text extraction
    if extension == ".pdf":

        cv_text = extract_pdf_text(file_bytes)

        if not cv_text:
            raise HTTPException(
                status_code=400,
                detail="Could not extract text from this PDF."
            )

    else:

        raise HTTPException(
            status_code=501,
            detail="DOC and DOCX extraction will be added next."
        )

    try:

        # AI CV Analysis
        analysis = analyze_cv_with_ai(cv_text)

        # Job Matching
        job_matches = match_jobs(analysis)

        # Final Response
        return {
            "success": True,
            "message": "CV analyzed successfully",
            "analysis": analysis,
            "job_matches": job_matches
        }

    except json.JSONDecodeError:

        raise HTTPException(
            status_code=502,
            detail="AI returned invalid JSON."
        )

    except Exception as error:

        print("AI ERROR:", repr(error))

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )