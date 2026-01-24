from fastapi import APIRouter, HTTPException, UploadFile, File
from app.services.rag_service import rag_service
from app.models.schemas import DocumentsListResponse

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("", response_model=DocumentsListResponse)
async def get_documents():
    """Получение списка документов"""
    try:
        return await rag_service.get_documents()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("")
async def add_document(file: UploadFile = File(...)):
    """Добавление документа"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"Получен файл для загрузки: {file.filename}, content_type: {file.content_type}")
        content = await file.read()
        logger.info(f"Прочитано байт: {len(content)}")
        result = await rag_service.add_document(content, file.filename)
        logger.info(f"Документ успешно добавлен: {result}")
        return result
    except Exception as e:
        logger.error(f"Ошибка при добавлении документа: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{doc_id}")
async def delete_document(doc_id: str):
    """Удаление документа"""
    try:
        result = await rag_service.delete_document(doc_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

