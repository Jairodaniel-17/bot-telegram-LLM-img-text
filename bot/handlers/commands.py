from telegram import Update
from telegram.ext import ContextTypes
from loguru import logger
import re

# Use relative imports when running as module, absolute when running directly
try:
    from bot.database import set_user_config, get_user_config
except ImportError:
    # Fallback to relative imports when running as module
    from ..database import set_user_config, get_user_config

# El logger se importa desde config.py y ya está configurado con loguru


def escape_markdown(text: str) -> str:
    """Escapa caracteres especiales de MarkdownV2."""
    escape_chars = r"_*[]()~`>#+-=|{}.!"
    return re.sub(f"([{re.escape(escape_chars)}])", r"\\\1", text)


async def handle_error(
    update: Update, context: ContextTypes.DEFAULT_TYPE, error_msg: str
):
    """Maneja errores enviando un mensaje al usuario."""
    logger.error(error_msg)
    if update.message:
        await update.message.reply_text(
            "⚠️ Ocurrió un error. Por favor, inténtalo nuevamente.",
            parse_mode="MarkdownV2",
        )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text(
            escape_markdown(
                "👋 Bienvenido al Bot de LLM\n\n"
                "📌 Comandos disponibles:\n"
                "• /set_api_key <tu_key>\n"
                "• /set_base_url <url>\n"
                "• /set_model <modelo>\n"
                "• /set_system_prompt <texto>\n"
                "• /config_status\n\n"
                "Ejemplo:\n"
                "1. /set_api_key sk-tu_key\n"
                "2. /set_model gpt-4-turbo"
            ),
            parse_mode="MarkdownV2",
        )
    except Exception as e:
        await handle_error(update, context, f"Error en start: {str(e)}")


async def set_api_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not context.args:
            await update.message.reply_text(
                escape_markdown("Uso: /set_api_key tu_api_key"), parse_mode="MarkdownV2"
            )
            return

        api_key = context.args[0].strip()
        user_id = update.effective_user.id

        if set_user_config(user_id, "api_key", api_key):
            await update.message.reply_text(
                escape_markdown("✅ API Key guardada correctamente"),
                parse_mode="MarkdownV2",
            )
            logger.info(f"API Key actualizada para usuario {user_id}")
        else:
            await update.message.reply_text(
                escape_markdown("❌ Error al guardar la API Key"),
                parse_mode="MarkdownV2",
            )

    except Exception as e:
        await handle_error(update, context, f"Error en set_api_key: {str(e)}")


async def set_base_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not context.args:
            await update.message.reply_text(
                escape_markdown("Uso: /set_base_url https://tu.url"),
                parse_mode="MarkdownV2",
            )
            return

        base_url = context.args[0].strip()
        user_id = update.effective_user.id

        if set_user_config(user_id, "base_url", base_url):
            await update.message.reply_text(
                escape_markdown("✅ Base URL guardada correctamente"),
                parse_mode="MarkdownV2",
            )
            logger.info(f"Base URL actualizada para usuario {user_id}: {base_url}")
        else:
            await update.message.reply_text(
                escape_markdown("❌ Error al guardar la Base URL"),
                parse_mode="MarkdownV2",
            )

    except Exception as e:
        await handle_error(update, context, f"Error en set_base_url: {str(e)}")


async def set_model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not context.args:
            await update.message.reply_text(
                escape_markdown("Uso: /set_model nombre_modelo"),
                parse_mode="MarkdownV2",
            )
            return

        model_name = context.args[0].strip()
        user_id = update.effective_user.id

        if set_user_config(user_id, "model_name", model_name):
            await update.message.reply_text(
                escape_markdown(f"✅ Modelo {model_name} guardado correctamente"),
                parse_mode="MarkdownV2",
            )
            logger.info(f"Modelo actualizado para usuario {user_id}: {model_name}")
        else:
            await update.message.reply_text(
                escape_markdown("❌ Error al guardar el modelo"),
                parse_mode="MarkdownV2",
            )

    except Exception as e:
        await handle_error(update, context, f"Error en set_model: {str(e)}")


async def set_system_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not context.args:
            await update.message.reply_text(
                escape_markdown("Uso: /set_system_prompt tu_texto"),
                parse_mode="MarkdownV2",
            )
            return

        prompt = " ".join(context.args).strip()
        user_id = update.effective_user.id

        if set_user_config(user_id, "system_prompt", prompt):
            await update.message.reply_text(
                escape_markdown("✅ System Prompt guardado correctamente"),
                parse_mode="MarkdownV2",
            )
            logger.info(f"System Prompt actualizado para usuario {user_id}")
        else:
            await update.message.reply_text(
                escape_markdown("❌ Error al guardar el System Prompt"),
                parse_mode="MarkdownV2",
            )

    except Exception as e:
        await handle_error(update, context, f"Error en set_system_prompt: {str(e)}")


async def config_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        config = get_user_config(user_id)

        if not config:
            await update.message.reply_text(
                escape_markdown("⚠️ No hay configuración guardada"),
                parse_mode="MarkdownV2",
            )
            return

        status_msg = escape_markdown(
            f"🔍 Configuración actual:\n"
            f"• API Key: {'✅' if config.get('api_key') else '❌'}\n"
            f"• Base URL: {config.get('base_url', 'No configurada')}\n"
            f"• Modelo: {config.get('model_name', 'No configurado')}\n"
            f"• System Prompt: {config.get('system_prompt', 'No configurado')}"
        )

        await update.message.reply_text(status_msg, parse_mode="MarkdownV2")
        logger.info(f"Configuración mostrada para usuario {user_id}")

    except Exception as e:
        await handle_error(update, context, f"Error en config_status: {str(e)}")
