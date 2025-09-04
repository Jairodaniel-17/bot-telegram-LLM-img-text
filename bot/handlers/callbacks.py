from telegram import Update
from telegram.ext import ContextTypes


async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "config_api_key":
        await query.edit_message_text(
            "🔑 Usa: `/set_api_key TU_API_KEY`", parse_mode="Markdown"
        )
    elif data == "config_base_url":
        await query.edit_message_text(
            "🌐 Usa: `/set_base_url TU_BASE_URL`", parse_mode="Markdown"
        )
    elif data == "config_model":
        await query.edit_message_text(
            "🤖 Usa: `/set_model TU_MODELO`", parse_mode="Markdown"
        )
    elif data == "config_prompt":
        await query.edit_message_text(
            "📝 Usa: `/set_system_prompt TU_PROMPT`", parse_mode="Markdown"
        )
    elif data == "show_config":
        config = context.user_data.get("config", {})
        await query.edit_message_text(
            f"⚙️ Config actual:\n`{config}`", parse_mode="Markdown"
        )
    else:
        await query.edit_message_text("❌ Opción desconocida.")
