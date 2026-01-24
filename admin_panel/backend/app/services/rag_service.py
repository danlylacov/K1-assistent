import aiohttp
from typing import Optional, Dict
from app.core.config import RAG_API_URL


class RAGService:
    """Сервис для работы с RAG API"""
    
    async def get_documents(self) -> Dict:
        """Получение списка документов"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{RAG_API_URL}/documents") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error = await response.json()
                    raise Exception(f"RAG API error: {error.get('detail', 'Unknown error')}")
    
    async def add_document(self, file_content: bytes, filename: str) -> Dict:
        """Добавление документа"""
        import logging
        logger = logging.getLogger(__name__)
        
        async with aiohttp.ClientSession() as session:
            data = aiohttp.FormData()
            data.add_field('file', file_content, filename=filename, content_type='application/octet-stream')
            
            logger.info(f"Отправка файла в RAG API: {filename}, размер: {len(file_content)} байт")
            
            async with session.post(f"{RAG_API_URL}/documents", data=data) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"Файл успешно загружен в RAG API: {result}")
                    return result
                else:
                    error_text = await response.text()
                    logger.error(f"Ошибка RAG API: {response.status}, {error_text}")
                    try:
                        error = await response.json()
                        raise Exception(f"RAG API error: {error.get('detail', 'Unknown error')}")
                    except:
                        raise Exception(f"RAG API error: {error_text}")
    
    async def delete_document(self, doc_id: str) -> Dict:
        """Удаление документа"""
        async with aiohttp.ClientSession() as session:
            async with session.delete(f"{RAG_API_URL}/documents/{doc_id}") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error = await response.json()
                    raise Exception(f"RAG API error: {error.get('detail', 'Unknown error')}")
    
    async def update_config(self, config: Dict) -> Dict:
        """Обновление конфигурации RAG"""
        async with aiohttp.ClientSession() as session:
            async with session.put(f"{RAG_API_URL}/config/settings", json=config) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error = await response.json()
                    raise Exception(f"RAG API error: {error.get('detail', 'Unknown error')}")
    
    async def get_config(self) -> Dict:
        """Получение текущей конфигурации RAG"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{RAG_API_URL}/config/settings") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error = await response.json()
                    raise Exception(f"RAG API error: {error.get('detail', 'Unknown error')}")

    async def update_prompt(self, prompt: str) -> Dict:
        """Обновление промпта"""
        async with aiohttp.ClientSession() as session:
            async with session.put(f"{RAG_API_URL}/config/prompt", json={"prompt": prompt}) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error = await response.json()
                    raise Exception(f"RAG API error: {error.get('detail', 'Unknown error')}")

    async def get_prompt(self) -> Dict:
        """Получение текущего промпта"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{RAG_API_URL}/config/prompt") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error = await response.json()
                    raise Exception(f"RAG API error: {error.get('detail', 'Unknown error')}")


rag_service = RAGService()

