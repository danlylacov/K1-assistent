import aiohttp
from pathlib import Path
from typing import List, Optional, Union
from app.core.config import BOT_TOKEN


class TelegramService:
    """Сервис для работы с Telegram Bot API"""
    
    BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
    
    async def send_message(self, chat_id: int, text: str, parse_mode: str = "HTML") -> dict:
        """Отправка сообщения пользователю"""
        async with aiohttp.ClientSession() as session:
            url = f"{self.BASE_URL}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": parse_mode
            }
            
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error = await response.json()
                    raise Exception(f"Telegram API error: {error}")

    async def send_photo(
        self,
        chat_id: int,
        photo: Union[bytes, Path],
        caption: Optional[str] = None,
        filename: str = "photo.jpg",
        parse_mode: str = "HTML",
    ) -> dict:
        """Отправка фото (с подписью)"""
        async with aiohttp.ClientSession() as session:
            url = f"{self.BASE_URL}/sendPhoto"
            data = aiohttp.FormData()
            data.add_field("chat_id", str(chat_id))
            if caption:
                data.add_field("caption", caption)
                data.add_field("parse_mode", parse_mode)

            if isinstance(photo, Path):
                data.add_field("photo", photo.open("rb"), filename=photo.name)
            else:
                data.add_field("photo", photo, filename=filename)

            async with session.post(url, data=data) as response:
                if response.status == 200:
                    return await response.json()
                error = await response.json()
                raise Exception(f"Telegram API error: {error}")

    async def send_document(
        self,
        chat_id: int,
        document: Union[bytes, Path],
        caption: Optional[str] = None,
        filename: str = "file",
        parse_mode: str = "HTML",
    ) -> dict:
        """Отправка файла (document)"""
        async with aiohttp.ClientSession() as session:
            url = f"{self.BASE_URL}/sendDocument"
            data = aiohttp.FormData()
            data.add_field("chat_id", str(chat_id))
            if caption:
                data.add_field("caption", caption)
                data.add_field("parse_mode", parse_mode)

            if isinstance(document, Path):
                data.add_field("document", document.open("rb"), filename=document.name)
            else:
                data.add_field("document", document, filename=filename)

            async with session.post(url, data=data) as response:
                if response.status == 200:
                    return await response.json()
                error = await response.json()
                raise Exception(f"Telegram API error: {error}")

    async def send_with_attachment(
        self,
        chat_id: int,
        text: str,
        attachment: Optional[Union[bytes, Path]] = None,
        attachment_type: Optional[str] = None,
        attachment_name: Optional[str] = None,
    ) -> dict:
        """
        Отправка текста + (опционально) вложения.
        attachment_type: 'photo' | 'document' | None
        """
        if not attachment:
            return await self.send_message(chat_id, text)

        if attachment_type == "photo":
            return await self.send_photo(chat_id, attachment, caption=text or None, filename=attachment_name or "photo.jpg")

        return await self.send_document(chat_id, attachment, caption=text or None, filename=attachment_name or "file")
    
    async def send_broadcast(self, chat_ids: List[int], text: str) -> dict:
        """Отправка рассылки нескольким пользователям"""
        results = {
            "success": [],
            "failed": []
        }
        
        for chat_id in chat_ids:
            try:
                result = await self.send_message(chat_id, text)
                results["success"].append({"chat_id": chat_id, "result": result})
            except Exception as e:
                results["failed"].append({"chat_id": chat_id, "error": str(e)})
        
        return results

    async def send_broadcast_with_attachment(
        self,
        chat_ids: List[int],
        text: str,
        attachment: Optional[Union[bytes, Path]] = None,
        attachment_type: Optional[str] = None,
        attachment_name: Optional[str] = None,
    ) -> dict:
        """Рассылка текста + (опционально) вложения"""
        results = {"success": [], "failed": []}
        for chat_id in chat_ids:
            try:
                result = await self.send_with_attachment(
                    chat_id,
                    text,
                    attachment=attachment,
                    attachment_type=attachment_type,
                    attachment_name=attachment_name,
                )
                results["success"].append({"chat_id": chat_id, "result": result})
            except Exception as e:
                results["failed"].append({"chat_id": chat_id, "error": str(e)})
        return results
    
    async def get_chat(self, chat_id: int) -> dict:
        """Получение информации о чате"""
        async with aiohttp.ClientSession() as session:
            url = f"{self.BASE_URL}/getChat"
            params = {"chat_id": chat_id}
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error = await response.json()
                    raise Exception(f"Telegram API error: {error}")


telegram_service = TelegramService()

