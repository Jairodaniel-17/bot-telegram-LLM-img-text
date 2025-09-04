from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    Application,
)
from telegram import BotCommand, Update
from loguru import logger
import signal
import sys

# Use relative imports when running as module, absolute when running directly
try:
    from bot.config import TELEGRAM_TOKEN
    from bot.database import init_db, close_db
    from bot.handlers.commands import (
        start,
        set_api_key,
        set_base_url,
        set_model,
        set_system_prompt,
        config_status,
    )
    from bot.handlers.messages import handle_message
    from bot.handlers.callbacks import handle_button
except ImportError:
    # Fallback to relative imports when running as module
    from .config import TELEGRAM_TOKEN
    from .database import init_db, close_db
    from .handlers.commands import (
        start,
        set_api_key,
        set_base_url,
        set_model,
        set_system_prompt,
        config_status,
    )
    from .handlers.messages import handle_message
    from .handlers.callbacks import handle_button

# El logger se importa desde config.py y ya está configurado con loguru

# Comandos del bot
BOT_COMMANDS = [
    BotCommand("start", "Inicia el bot y muestra el menú"),
    BotCommand("set_api_key", "Configura tu API Key de OpenAI"),
    BotCommand("set_base_url", "Configura la URL base de la API"),
    BotCommand("set_model", "Configura el modelo de IA a usar"),
    BotCommand("set_system_prompt", "Configura el prompt del sistema"),
    BotCommand("config_status", "Muestra la configuración actual"),
]


async def post_init(application: Application) -> None:
    """
    Configuración posterior a la inicialización del bot.

    Args:
        application: Instancia de la aplicación del bot
    """
    try:
        await application.bot.set_my_commands(BOT_COMMANDS)
        logger.info("Comandos del bot configurados correctamente")
        await application.bot.set_my_description(
            "Bot para interactuar con modelos de IA"
        )
    except Exception as e:
        logger.error(f"Error en post_init: {str(e)}", exc_info=True)


def register_handlers(application: Application) -> None:
    """
    Registra todos los manejadores de comandos y mensajes.

    Args:
        application: Instancia de la aplicación del bot
    """
    handlers = [
        CommandHandler("start", start),
        CommandHandler("set_api_key", set_api_key),
        CommandHandler("set_base_url", set_base_url),
        CommandHandler("set_model", set_model),
        CommandHandler("set_system_prompt", set_system_prompt),
        CommandHandler("config_status", config_status),
        CallbackQueryHandler(handle_button),
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message),
        MessageHandler(filters.PHOTO, handle_message),  # Manejo de imágenes
    ]

    for handler in handlers:
        application.add_handler(handler)

    logger.info(f"{len(handlers)} manejadores registrados")


def handle_shutdown(signum, frame) -> None:
    """
    Maneja el cierre limpio de la aplicación.
    """
    logger.info("Recibida señal de apagado. Cerrando el bot...")
    close_db()
    sys.exit(0)


def main() -> None:
    """
    Función principal que inicia y configura el bot.
    """
    try:
        # Configurar manejo de señales para apagado limpio
        signal.signal(signal.SIGINT, handle_shutdown)
        signal.signal(signal.SIGTERM, handle_shutdown)

        # Inicializar base de datos
        init_db()
        logger.info("Base de datos inicializada")

        # Construir y configurar la aplicación
        application = (
            ApplicationBuilder().token(TELEGRAM_TOKEN).post_init(post_init).build()
        )

        # Registrar manejadores
        register_handlers(application)

        logger.info("🤖 Bot iniciado y listo para recibir mensajes")
        print("Bot iniciado correctamente. Presiona Ctrl+C para detenerlo.")

        # Iniciar el bot - Fixed for python-telegram-bot 20.x compatibility
        application.run_polling(
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES,
        )

    except Exception as e:
        logger.critical(f"Error fatal al iniciar el bot: {str(e)}", exc_info=True)
        sys.exit(1)
    finally:
        close_db()
        logger.info("Bot detenido. Recursos liberados.")


if __name__ == "__main__":
    main()
