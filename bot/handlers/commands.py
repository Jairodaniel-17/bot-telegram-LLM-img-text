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
        text = (
            "👋 Bienvenido al Bot de LLM\n\n"
            "📌 Comandos disponibles:\n"
            "• /start - Muestra este mensaje\n"
            "• /help - Ayuda detallada y modelos disponibles\n"
            "• /set_api_key &lt;tu_key&gt; - Configura tu API Key\n"
            "• /set_base_url &lt;url&gt; - Configura la URL base de la API\n"
            "• /set_model &lt;modelo&gt; - Configura el modelo de IA\n"
            "• /set_system_prompt &lt;texto&gt; - Configura el prompt del sistema\n"
            "• /config_status - Muestra la configuración actual\n\n"
            "Ejemplos:\n"
            "<pre>/set_api_key sk-tu_key</pre>\n"
            "<pre>/set_model gpt-4-turbo</pre>\n"
            "<pre>/set_base_url https://api.openai.com/v1</pre>\n"
            "<pre>/set_system_prompt Tu prompt aquí</pre>"
        )
        await update.message.reply_text(text, parse_mode="HTML")
    except Exception as e:
        await handle_error(update, context, f"Error en start: {str(e)}")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        help_text = escape_markdown(
            "🔧 **Ayuda del Bot de LLM**\n\n"
            "**Modelos recomendados:**\n"
            "• `gpt-4-turbo` - OpenAI GPT-4 (texto)\n"
            "• `gpt-4o` - OpenAI GPT-4o (multimodal)\n"
            "• `gpt-3.5-turbo` - OpenAI GPT-3.5 (texto, más económico)\n"
            "• `claude-3-opus` - Anthropic Claude (texto)\n"
            "• `claude-3-sonnet` - Anthropic Claude (texto)\n\n"
            "**Proveedores compatibles:**\n"
            "• OpenAI: `https://api.openai.com/v1`\n"
            "• Anthropic: `https://api.anthropic.com`\n"
            "• OpenRouter: `https://openrouter.ai/api/v1`\n"
            "• Local: `http://localhost:1234/v1`\n\n"
            "**Configuración paso a paso:**\n"
            "1. `/set_api_key tu_api_key`\n"
            "2. `/set_base_url https://tu.proveedor.com/v1`\n"
            "3. `/set_model nombre_modelo`\n"
            "4. `/config_status` para verificar\n\n"
            "**Soporte multimodal:**\n"
            "Envía una foto + texto para análisis con modelos que lo soporten."
        )
        await update.message.reply_text(help_text, parse_mode="MarkdownV2")
    except Exception as e:
        await handle_error(update, context, f"Error en help: {str(e)}")


async def set_api_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not context.args:
            await update.message.reply_text(
    "Uso:\n```\n/set_api_key tu_api_key\n```",
    parse_mode="MarkdownV2"
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
                escape_markdown("Uso:\n```\n/set_base_url https://tu.url\n```"),
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
                escape_markdown("Uso:\n```\n/set_model nombre_modelo\n```"),
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
                escape_markdown("Uso:\n```\n/set_system_prompt tu_texto\n```"),
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


async def test_config(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando para probar la configuración paso a paso."""
    try:
        user_id = update.effective_user.id
        
        # Obtener configuración actual
        config = get_user_config(user_id)
        
        # Verificar cada campo
        missing_fields = []
        if not config.get("api_key"):
            missing_fields.append("API Key")
        if not config.get("base_url"):
            missing_fields.append("Base URL")
        if not config.get("model_name"):
            missing_fields.append("Modelo")
        
        if not missing_fields:
            await update.message.reply_text(
                "✅ ¡Configuración completa! Puedes enviar mensajes ahora."
            )
            return
        
        # Mostrar qué falta configurar
        missing_text = "\n".join([f"• {field}" for field in missing_fields])
        await update.message.reply_text(
            f"⚠️ **Configuración incompleta**\n\n"
            f"**Faltan configurar:**\n{missing_text}\n\n"
            f"**Comandos para configurar:**\n"
            f"• ```/set_api_key tu_api_key```\n"
            f"• ```/set_base_url https://tu.proveedor.com/v1```\n"
            f"• ```/set_model nombre_modelo```\n\n"
            f"**Ejemplo completo:**\n"
            f"1. ```/set_api_key sk-1234567890abcdef```\n"
            f"2. ```/set_base_url https://api.openai.com/v1```\n"
            f"3. ```/set_model gpt-4-turbo```\n"
            f"4. ```/test_config``` para verificar"
        )
        
    except Exception as e:
        await update.message.reply_text(f"❌ Error en test_config: {str(e)}")
        logger.error(f"Error en test_config: {str(e)}", exc_info=True)
