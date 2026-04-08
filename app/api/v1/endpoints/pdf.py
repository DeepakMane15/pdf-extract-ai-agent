import re
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.api.deps import require_roles
from app.core.config import settings
from app.models.user import User, UserRole
from app.schemas.pdf import PdfUploadResponse

router = APIRouter()

_PDF_MAGIC = b'%PDF'
_ALLOWED_CONTENT_TYPES = frozenset({'application/pdf', 'application/x-pdf'})


def _sanitize_original_name(name: str | None) -> str:
    base = Path(name or 'document.pdf').name
    base = re.sub(r'[^a-zA-Z0-9._-]', '_', base)
    if not base.lower().endswith('.pdf'):
        base = f'{base}.pdf'
    return base[:200] if len(base) > 200 else base


@router.post('/upload', response_model=PdfUploadResponse)
async def upload_pdf(
    file: UploadFile = File(..., description='PDF file to store'),
    _: User = Depends(require_roles(UserRole.admin, UserRole.auditor)),
) -> PdfUploadResponse:
    if file.content_type not in _ALLOWED_CONTENT_TYPES and not (
        file.filename and file.filename.lower().endswith('.pdf')
    ):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail='Only PDF uploads are allowed.',
        )

    upload_dir = Path(settings.pdf_upload_dir).resolve()
    upload_dir.mkdir(parents=True, exist_ok=True)

    safe_name = _sanitize_original_name(file.filename)
    stored_name = f'{uuid.uuid4().hex}_{safe_name}'
    dest = upload_dir / stored_name

    body = await file.read()
    if not body:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Empty file.')
    if len(body) > settings.max_pdf_upload_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f'File too large (max {settings.max_pdf_upload_bytes} bytes).',
        )
    if not body.startswith(_PDF_MAGIC):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='File does not look like a valid PDF.',
        )

    dest.write_bytes(body)

    return PdfUploadResponse(
        original_filename=file.filename,
        stored_filename=stored_name,
        content_type=file.content_type,
        size_bytes=len(body),
    )
