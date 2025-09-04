from telegram import Update, PhotoSize
from telegram.ext import ContextTypes
from bot.database import get_user_config
from core.pipeline import run_pipeline
from loguru import logger
import os
import tempfile
from typing import Optional
from bot.security import (
    CompositeGuard,
    RateLimitGuard,
    MessageLengthGuard,
    ImageSizeGuard,
)
from bot.security import (
    CompositeSanitizer,
    TrimSanitizer,
    ControlCharsSanitizer,
)

# El logger se importa desde config.py y ya está configurado con loguru


_message_guard = CompositeGuard(
    RateLimitGuard(max_requests=6, window_seconds=10),
    MessageLengthGuard(max_chars=4000),
    ImageSizeGuard(max_bytes=5 * 1024 * 1024),
)

_sanitizer = CompositeSanitizer(
    TrimSanitizer(),
    ControlCharsSanitizer(),
    # No escapar aquí si el modelo no requiere Markdown; mantenemos el texto limpio por seguridad básica
)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Maneja los mensajes de texto y fotos del usuario, procesándolos con el LLM adecuado.

    Args:
        update: Objeto Update de Telegram
        context: Contexto de la aplicación

    Raises:
        Exception: Propaga excepciones no manejadas con logging
    """
    image_path = None
    processing_msg = None

    try:
        # Validar que el mensaje tenga contenido
        if not update.message or not update.effective_user:
            logger.warning("Mensaje sin contenido o usuario no válido")
            return

        # Obtener configuración del usuario
        user_id = update.effective_user.id
        config = get_user_config(user_id)

        # Validar configuración
        if not config or not config.get("api_key") or not config.get("model_name"):
            await update.message.reply_text(
                "⚠️ Configuración incompleta. Necesitas:\n"
                "1. Establecer API key con /set_api_key\n"
                "2. Elegir modelo con /set_model"
            )
            return

        # Obtener texto de entrada (puede ser None si solo envía imagen)
        user_input = update.message.text or ""
        user_input = _sanitizer.sanitize(user_input)

        # Manejar imagen si está presente
        image_size_bytes = None
        if update.message.photo:
            # Validación de tamaño antes de descargar
            last_photo = update.message.photo[-1]
            try:
                image_size_bytes = getattr(last_photo, "file_size", None)
            except Exception:
                image_size_bytes = None

            # Pasar por guardias de seguridad
            violation = _message_guard.check(
                {
                    "user_id": user_id,
                    "text": user_input,
                    "image_size_bytes": image_size_bytes,
                    "is_command": False,
                }
            )
            if violation:
                await update.message.reply_text(violation)
                return

            image_path = await download_photo(last_photo, context.bot)
            if not image_path:
                await update.message.reply_text("⚠️ No pude procesar la imagen adjunta")
                return

            if not user_input:
                user_input = (
                    "Describe la imagen"  # Texto por defecto si solo envía imagen
                )

        # Pasar por guardias para mensajes solo de texto
        if not update.message.photo:
            violation = _message_guard.check(
                {
                    "user_id": user_id,
                    "text": user_input,
                    "image_size_bytes": image_size_bytes,
                    "is_command": False,
                }
            )
            if violation:
                await update.message.reply_text(violation)
                return

        # Notificar al usuario que se está procesando
        processing_msg = await update.message.reply_text(
            "⏳ Procesando tu solicitud..."
        )

        # Ejecutar el pipeline
        output = run_pipeline(
            config=config, user_input=user_input, image_path=image_path
        )

        # Limpiar archivo temporal si existe
        if image_path:
            await cleanup_temp_file(image_path)

        # Editar el mensaje original con la respuesta
        await context.bot.edit_message_text(
            text=f"🤖 Respuesta:\n\n{output}",
            chat_id=processing_msg.chat_id,
            message_id=processing_msg.message_id,
        )

    except Exception as e:
        logger.error(f"Error en handle_message: {str(e)}", exc_info=True)

        # Limpieza en caso de error
        if image_path and os.path.exists(image_path):
            await cleanup_temp_file(image_path)

        error_msg = "⚠️ Ocurrió un error al procesar tu solicitud. Intenta nuevamente."
        if update.message:
            await update.message.reply_text(error_msg)


async def download_photo(photo: PhotoSize, bot) -> Optional[str]:
    """
    Descarga la foto enviada por el usuario a un directorio temporal del sistema.

    Args:
        photo: Objeto PhotoSize de Telegram
        bot: Instancia del bot para descargar el archivo

    Returns:
        str: Ruta local del archivo descargado o None si falla
    """
    try:
        file = await bot.get_file(photo.file_id)

        # Crear directorio temporal seguro
        temp_dir = os.path.join(tempfile.gettempdir(), "telegram_bot_images")
        os.makedirs(temp_dir, exist_ok=True)

        # Obtener extensión del archivo
        file_extension = "jpg"
        if hasattr(file, "file_path") and file.file_path:
            _, ext = os.path.splitext(file.file_path)
            if ext and ext.lower().lstrip(".") in ["jpg", "jpeg", "png", "webp"]:
                file_extension = ext.lower().lstrip(".")

        # Crear ruta segura
        file_path = os.path.join(temp_dir, f"{file.file_id}.{file_extension}")

        # Descargar archivo
        await file.download_to_drive(custom_path=file_path)

        logger.info(f"Imagen descargada correctamente en: {file_path}")
        return file_path

    except Exception as e:
        logger.error(f"Error al descargar foto: {str(e)}", exc_info=True)
        return None


async def cleanup_temp_file(file_path: str) -> None:
    """
    Elimina de forma segura un archivo temporal.

    Args:
        file_path: Ruta del archivo a eliminar
    """
    try:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Archivo temporal eliminado: {file_path}")
    except Exception as e:
        logger.error(f"Error al eliminar archivo temporal: {str(e)}", exc_info=True)
