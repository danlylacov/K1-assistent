from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from RAG_API.app.core.config import UPLOAD_DIR
from RAG_API.app.services.rag_service import rag_service
from RAG_API.app.models.schemas import DocumentsListResponse

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("", response_model=DocumentsListResponse)
async def get_all_documents():
    """Получение списка всех документов в базе знаний"""
    try:
        result = await rag_service.get_all_documents()
        return DocumentsListResponse(**result)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении списка документов: {str(e)}")


@router.post("")
async def add_document(file: UploadFile = File(...)):
    """Добавление документа в базу знаний"""
    import logging
    logger = logging.getLogger(__name__)
    
    file_path = UPLOAD_DIR / file.filename
    
    try:
        logger.info(f"Получен файл: {file.filename}, размер: {file.size}")
        
        # Убеждаемся, что директория существует
        UPLOAD_DIR.mkdir(exist_ok=True)
        logger.info(f"Директория для загрузки: {UPLOAD_DIR}, существует: {UPLOAD_DIR.exists()}")
        
        # Сохраняем файл
        content = await file.read()
        logger.info(f"Прочитано байт: {len(content)}")
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        logger.info(f"Файл сохранен: {file_path}")
        
        # Обрабатываем документ
        count = await rag_service.ingest_document(str(file_path))
        logger.info(f"Документ обработан, создано чанков: {count}")
        
        return JSONResponse({
            "status": "success",
            "message": f"Документ добавлен. Создано {count} чанков",
            "chunks_count": count
        })
    except RuntimeError as e:
        logger.error(f"RuntimeError при обработке документа: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Ошибка при обработке документа: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ошибка при обработке документа: {str(e)}")
    finally:
        # Удаляем временный файл
        if file_path.exists():
            try:
                file_path.unlink()
                logger.info(f"Временный файл удален: {file_path}")
            except Exception as e:
                logger.warning(f"Не удалось удалить временный файл: {e}")


@router.delete("/{doc_id}")
async def delete_document(doc_id: str):
    """Удаление документа из базы знаний"""
    try:
        deleted_count = await rag_service.delete_document(doc_id)
        
        if deleted_count is not None:
            return JSONResponse({
                "status": "success",
                "message": f"Удалено {deleted_count} чанков документа {doc_id}"
            })
        else:
            raise HTTPException(status_code=404, detail=f"Документ {doc_id} не найден")
    except HTTPException:
        raise
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при удалении: {str(e)}")


@router.put("/{doc_id}")
async def update_document(doc_id: str, file: UploadFile = File(...)):
    """Обновление документа в базе знаний"""
    try:
        # Сначала удаляем старый документ
        await delete_document(doc_id)
    except HTTPException as e:
        # Если документ не найден, продолжаем (может быть новый документ)
        if e.status_code != 404:
            raise
    
    # Затем добавляем новый
    return await add_document(file)

