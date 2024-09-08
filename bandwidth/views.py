import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ConversationHandler,
    ContextTypes,
)
import json
from asgiref.sync import sync_to_async
from decouple import config
from bandwidth.models import Server, UserProfile

logger = logging.getLogger(__name__)

# Load environment variables
TELEGRAM_TOKEN = config('TELEGRAM_TOKEN')
SUPERADMIN_ID = config('SUPERADMIN_ID', default=None, cast=int)

# Define the general keyboard
def get_general_keyboard(user_id):
    keyboard = [
        [KeyboardButton('List Servers'), KeyboardButton('Help')]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# Define the bot commands and handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_profile, created = await sync_to_async(UserProfile.objects.get_or_create)(user_id=user_id)
    keyboard = get_general_keyboard(user_id)
    await update.message.reply_text(
        f'Welcome to the Django monitoring bot! Your user ID is {user_id}. Use the keyboard below to navigate:',
        reply_markup=keyboard
    )
    await list_servers(update, context)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    commands = [
        '/start - Start the bot',
        '/help - Show this help message',
        '/listservers - List all registered servers',
    ]
    await update.message.reply_text(
        '\n'.join(commands),
        reply_markup=get_general_keyboard(update.message.from_user.id)
    )

# Handler to list all servers for the current user
async def list_servers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id == SUPERADMIN_ID:
        servers = await sync_to_async(list)(Server.objects.all())
    else:
        servers = await sync_to_async(list)(Server.objects.filter(user_id=user_id))

    if not servers:
        await update.message.reply_text('No servers registered.', reply_markup=get_general_keyboard(update.message.from_user.id))
        return

    keyboard = [
        [InlineKeyboardButton(server.hostname, callback_data=str(server.id))] for server in servers
    ]
    reply_markup_inline = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Select a server:', reply_markup=reply_markup_inline)

# Handler to show server details when a server is selected
async def server_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    server_id = int(query.data)
    context.user_data['selected_server_id'] = server_id
    server = await sync_to_async(Server.objects.get)(id=server_id)

    details = (
        f"Hostname: {server.hostname}\n"
        f"IP Address: {server.ip_address}\n"
        f"API Key: {server.api_key}\n"
        f"API Password: {server.api_password}\n"
        f"Panel IP Address: {server.panel_ipaddress}\n"
        f"VPS ID: {server.vps_id}\n"
        f"Panel Port: {server.panel_port}\n"
        f"Used Bandwidth (GB): {server.used_bandwidth_gb}\n"
        f"Limit Bandwidth (GB): {server.limit_bandwidth_gb}\n"
        f"Free Bandwidth (GB): {server.free_bandwidth_gb}\n"
        f"Scheme: {server.scheme}\n"
    )

    keyboard = [
        [InlineKeyboardButton("Delete Server", callback_data='delete_server')],
        [InlineKeyboardButton("Back to Server List", callback_data='back_to_list')]
    ]
    reply_markup_inline = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text=details, reply_markup=reply_markup_inline)

# Handler to delete a server
async def delete_server(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    server_id = context.user_data.get('selected_server_id')
    if server_id:
        await sync_to_async(Server.objects.filter(id=server_id).delete)()
        await query.edit_message_text(text="Server deleted successfully.")
    else:
        await query.edit_message_text(text="Error: Server not found.")

    # After deleting, show the updated server list
    await list_servers(query, context)

# Handler to go back to the server list
async def back_to_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await list_servers(query, context)

# Handler for Help button
async def help_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await help_command(update, context)

@csrf_exempt
def webhook(request):
    if request.method == 'POST':
        update = Update.de_json(json.loads(request.body))
        application.update_queue.put_nowait(update)
    return JsonResponse({'status': 'ok'})

application = Application.builder().token(TELEGRAM_TOKEN).build()

application.add_handler(CommandHandler('start', start))
application.add_handler(CommandHandler('help', help_command))
application.add_handler(CommandHandler('listservers', list_servers))
application.add_handler(MessageHandler(filters.TEXT & filters.Regex('^(Help)$'), help_button))
application.add_handler(MessageHandler(filters.TEXT & filters.Regex('^(List Servers)$'), list_servers))
application.add_handler(CallbackQueryHandler(server_details, pattern='^\d+$'))
application.add_handler(CallbackQueryHandler(delete_server, pattern='^delete_server$'))
application.add_handler(CallbackQueryHandler(back_to_list, pattern='^back_to_list$'))

if __name__ == "__main__":
    application.run_polling()