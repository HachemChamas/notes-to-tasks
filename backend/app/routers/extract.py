"""POST /extract: paste notes, get back suggested tasks (not saved yet)."""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.extractor import ExtractionError, TaskExtractor, get_extractor
from app.models import Note, User
from app.schemas import ExtractRequest, ExtractResponse

router = APIRouter(tags=["extract"])


@router.post("/extract", response_model=ExtractResponse)
def extract_tasks(
    data: ExtractRequest,
    db: Session = Depends(get_db),
    extractor: TaskExtractor = Depends(get_extractor),
):
    """Ask the AI for tasks in the notes.

    The notes are saved (so approved tasks can link back to them), but the
    tasks are only suggestions. The frontend shows them for review and then
    calls POST /tasks/bulk with the ones the user approved.
    """
    # Tell the AI who is already on the board, so "ada" matches "Ada".
    team = list(db.scalars(select(User.name).order_by(User.name)))

    try:
        suggestions = extractor.extract(
            data.text, data.meeting_date or date.today(), team
        )
    except ExtractionError as error:
        raise HTTPException(status_code=error.status_code, detail=error.message)

    note = Note(content=data.text)
    db.add(note)
    db.commit()
    db.refresh(note)
    return ExtractResponse(note_id=note.id, tasks=suggestions)
