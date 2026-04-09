import re
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.core.config import settings
from app.db.session import get_db
from app.models.pdf_document import DocumentChunk, PdfDocument
from app.models.user import User, UserRole
from app.schemas.pdf import PdfDocumentListItem, PdfUploadResponse
from app.services.pdf_pipeline import process_pdf_file

router = APIRouter()

_PDF_MAGIC = b'%PDF'
_ALLOWED_CONTENT_TYPES = frozenset({'application/pdf', 'application/x-pdf'})


def _sanitize_original_name(name: str | None) -> str:
    base = Path(name or 'document.pdf').name
    base = re.sub(r'[^a-zA-Z0-9._-]', '_', base)
    if not base.lower().endswith('.pdf'):
        base = f'{base}.pdf'
    return base[:200] if len(base) > 200 else base


def _resolved_pdf_path(stored_filename: str) -> Path:
    upload_dir = Path(settings.pdf_upload_dir).resolve()
    if Path(stored_filename).name != stored_filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid stored filename.')
    path = (upload_dir / stored_filename).resolve()
    try:
        path.relative_to(upload_dir)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid file path.') from exc
    return path


@router.get('/documents', response_model=list[PdfDocumentListItem])
def list_my_pdf_documents(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[PdfDocumentListItem]:
    """PDFs uploaded by the current user (by account that performed the upload)."""
    chunk_sq = (
        select(DocumentChunk.document_id, func.count(DocumentChunk.id).label('n'))
        .group_by(DocumentChunk.document_id)
        .subquery()
    )
    stmt = (
        select(PdfDocument, func.coalesce(chunk_sq.c.n, 0).label('chunk_count'))
        .outerjoin(chunk_sq, PdfDocument.id == chunk_sq.c.document_id)
        .where(PdfDocument.uploaded_by_user_id == user.id)
        .order_by(PdfDocument.created_at.desc())
    )
    out: list[PdfDocumentListItem] = []
    for doc, chunk_count in db.execute(stmt).all():
        out.append(
            PdfDocumentListItem(
                id=doc.id,
                original_filename=doc.original_filename,
                stored_filename=doc.stored_filename,
                file_size_bytes=doc.file_size_bytes,
                chunk_count=int(chunk_count),
                processing_error=doc.processing_error,
                created_at=doc.created_at,
            )
        )
    return out


@router.get('/documents/{document_id}/download')
def download_pdf_document(
    document_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> FileResponse:
    """Download the stored PDF file. Any authenticated user may download (shared corpus)."""
    doc = db.get(PdfDocument, document_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Document not found.')
    path = _resolved_pdf_path(doc.stored_filename)
    if not path.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='File missing on disk.')
    download_name = doc.original_filename or doc.stored_filename
    if not download_name.lower().endswith('.pdf'):
        download_name = f'{download_name}.pdf'
    return FileResponse(
        path,
        media_type='application/pdf',
        filename=download_name,
        content_disposition_type='attachment',
    )


@router.post('/upload', response_model=PdfUploadResponse)
async def upload_pdf(
    file: UploadFile = File(..., description='PDF file to store'),
    current_user: User = Depends(require_roles(UserRole.admin, UserRole.auditor)),
    db: Session = Depends(get_db),
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

    doc, chunk_count = process_pdf_file(
        db,
        file_path=dest,
        original_filename=file.filename,
        stored_filename=stored_name,
        file_size_bytes=len(body),
        uploader=current_user,
    )

    ext = doc.extracted_text
    cln = doc.cleaned_text
    return PdfUploadResponse(
        document_id=doc.id,
        original_filename=file.filename,
        stored_filename=stored_name,
        content_type=file.content_type,
        size_bytes=len(body),
        extracted_char_count=len(ext) if ext is not None else None,
        cleaned_char_count=len(cln) if cln is not None else None,
        chunk_count=chunk_count,
        processing_error=doc.processing_error,
    )
