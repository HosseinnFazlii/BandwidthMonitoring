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

# States for the conversation
(
    HOSTNAME,
    IP_ADDRESS,
    API_KEY,
    API_PASSWORD,
    PANEL_IPADDRESS,
    VPS_ID,
    PANEL_PORT,
    TELEGRAM_API_TOKEN,
    CHAT_ID1,
    CHAT_ID2,
    USED_BANDWIDTH,
    LIMIT_BANDWIDTH,
    FREE_BANDWIDTH,
    SCHEME,
    ADMIN_ID,
    ROLE,
) = range(16)

# Define the general keyboard
def get_general_keyboard(user_id):
    if user_id == SUPERADMIN_ID:
        keyboard = [
            [KeyboardButton('List Servers'), KeyboardButton('Help')],
            [KeyboardButton('Admin')]
        ]
    else:
        keyboard = [
            [KeyboardButton('List Servers'), KeyboardButton('Help')]
        ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# Define the bot commands and handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    await sync_to_async(UserProfile.objects.get_or_create)(user_id=user_id)
    keyboard = get_general_keyboard(user_id)
    await update.message.reply_text(
        f'Welcome to the Django monitoring bot! Your user ID is {user_id}. Use the keyboard below to navigate:',
        reply_markup=keyboard
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    commands = [
        '/start - Start the bot',
        '/help - Show this help message',
        '/status - Get the current server status',
        '/registerserver - Register a new server',
        '/listservers - List all registered servers',
    ]
    if update.message.from_user.id == SUPERADMIN_ID:
        commands.append('/admin - Manage admins (Superadmin only)')
    await update.message.reply_text(
        '\n'.join(commands),
        reply_markup=get_general_keyboard(update.message.from_user.id)
    )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status_info = "Server is up and running."  # Replace with actual status info
    await update.message.reply_text(status_info)

# Conversation entry point for registering a server
async def register_server(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['user_id'] = update.message.from_user.id
    await update.message.reply_text('Please enter the hostname of the server:')
    return HOSTNAME

async def hostname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['hostname'] = update.message.text
    await update.message.reply_text('Please enter the IP address of the server:')
    return IP_ADDRESS

async def ip_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['ip_address'] = update.message.text
    await update.message.reply_text('Please enter the API key:')
    return API_KEY

async def api_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['api_key'] = update.message.text
    await update.message.reply_text('Please enter the API password:')
    return API_PASSWORD

async def api_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['api_password'] = update.message.text
    await update.message.reply_text('Please enter the panel IP address:')
    return PANEL_IPADDRESS

async def panel_ipaddress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['panel_ipaddress'] = update.message.text
    await update.message.reply_text('Please enter the VPS ID:')
    return VPS_ID

async def vps_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['vps_id'] = update.message.text
    await update.message.reply_text('Please enter the panel port:')
    return PANEL_PORT

async def panel_port(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['panel_port'] = update.message.text
    await update.message.reply_text('Please enter the Telegram API token:')
    return TELEGRAM_API_TOKEN

async def telegram_api_token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['telegramAPItoken'] = update.message.text
    await update.message.reply_text('Please enter the first chat ID:')
    return CHAT_ID1

async def chat_id1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['chat_ID1'] = update.message.text
    await update.message.reply_text('Please enter the second chat ID:')
    return CHAT_ID2

async def chat_id2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['chat_ID2'] = update.message.text
    await update.message.reply_text('Please enter the used bandwidth in GB:')
    return USED_BANDWIDTH

async def used_bandwidth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['used_bandwidth_gb'] = update.message.text
    await update.message.reply_text('Please enter the limit bandwidth in GB:')
    return LIMIT_BANDWIDTH

async def limit_bandwidth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['limit_bandwidth_gb'] = update.message.text
    await update.message.reply_text('Please enter the free bandwidth in GB:')
    return FREE_BANDWIDTH

async def free_bandwidth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['free_bandwidth_gb'] = update.message.text
    await update.message.reply_text('Please enter the scheme (http/https):')
    return SCHEME

async def scheme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['scheme'] = update.message.text

    # Save the data to the database using sync_to_async
    await sync_to_async(Server.objects.create)(
        hostname=context.user_data['hostname'],
        ip_address=context.user_data['ip_address'],
        api_key=context.user_data['api_key'],
        api_password=context.user_data['api_password'],
        panel_ipaddress=context.user_data['panel_ipaddress'],
        vps_id=context.user_data['vps_id'],
        panel_port=context.user_data['panel_port'],
        telegramAPItoken=context.user_data['telegramAPItoken'],
        chat_ID1=context.user_data['chat_ID1'],
        chat_ID2=context.user_data['chat_ID2'],
        used_bandwidth_gb=context.user_data['used_bandwidth_gb'],
        limit_bandwidth_gb=context.user_data['limit_bandwidth_gb'],
        free_bandwidth_gb=context.user_data['free_bandwidth_gb'],
        scheme=context.user_data['scheme'],
        user_id=context.user_data['user_id'],  # Save the user ID
    )

    await update.message.reply_text('Server registered successfully!', reply_markup=get_general_keyboard(update.message.from_user.id))
    return ConversationHandler.END

# Fallback handler
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Registration cancelled.', reply_markup=get_general_keyboard(update.message.from_user.id))
    return ConversationHandler.END

# Handler to list all servers for the current user
async def list_servers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_profile = await sync_to_async(UserProfile.objects.get)(user_id=user_id)
    if user_profile.role in ['superadmin', 'admin']:
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
        f"Telegram API Token: {server.telegramAPItoken}\n"
        f"Chat ID 1: {server.chat_ID1}\n"
        f"Chat ID 2: {server.chat_ID2}\n"
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

# Handler to manage admins (Superadmin only)
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id != SUPERADMIN_ID:
        await update.message.reply_text('Access denied.')
        return

    await update.message.reply_text('Please enter the user ID of the new admin:')
    return ADMIN_ID

async def admin_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['admin_id'] = update.message.text
    await update.message.reply_text('Please enter the role (admin/user):')
    return ROLE

async def role(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_id = context.user_data['admin_id']
    role = update.message.text

    if role not in ['admin', 'user']:
        await update.message.reply_text('Invalid role. Please enter "admin" or "user".')
        return ROLE

    await sync_to_async(UserProfile.objects.update_or_create)(
        user_id=admin_id,
        defaults={'role': role}
    )

    await update.message.reply_text(f'User {admin_id} has been assigned the role {role}.')
    return ConversationHandler.END

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

# Define conversation handler with states
conv_handler = ConversationHandler(
    entry_points=[CommandHandler('registerserver', register_server)],
    states={
        HOSTNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, hostname)],
        IP_ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, ip_address)],
        API_KEY: [MessageHandler(filters.TEXT & ~filters.COMMAND, api_key)],
        API_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, api_password)],
        PANEL_IPADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, panel_ipaddress)],
        VPS_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, vps_id)],
        PANEL_PORT: [MessageHandler(filters.TEXT & ~filters.COMMAND, panel_port)],
        TELEGRAM_API_TOKEN: [MessageHandler(filters.TEXT & ~filters.COMMAND, telegram_api_token)],
        CHAT_ID1: [MessageHandler(filters.TEXT & ~filters.COMMAND, chat_id1)],
        CHAT_ID2: [MessageHandler(filters.TEXT & ~filters.COMMAND, chat_id2)],
        USED_BANDWIDTH: [MessageHandler(filters.TEXT & ~filters.COMMAND, used_bandwidth)],
        LIMIT_BANDWIDTH: [MessageHandler(filters.TEXT & ~filters.COMMAND, limit_bandwidth)],
        FREE_BANDWIDTH: [MessageHandler(filters.TEXT & ~filters.COMMAND, free_bandwidth)],
        SCHEME: [MessageHandler(filters.TEXT & ~filters.COMMAND, scheme)],
        ADMIN_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_id)],
        ROLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, role)],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
)

application.add_handler(CommandHandler('start', start))
application.add_handler(CommandHandler('help', help_command))
application.add_handler(CommandHandler('status', status))
application.add_handler(conv_handler)
application.add_handler(CommandHandler('listservers', list_servers))
application.add_handler(CommandHandler('admin', admin))  # Add this command for managing admins
application.add_handler(MessageHandler(filters.TEXT & filters.Regex('^(Help)$'), help_button))
application.add_handler(MessageHandler(filters.TEXT & filters.Regex('^(List Servers)$'), list_servers))
application.add_handler(CallbackQueryHandler(server_details, pattern='^\d+$'))
application.add_handler(CallbackQueryHandler(delete_server, pattern='^delete_server$'))
application.add_handler(CallbackQueryHandler(back_to_list, pattern='^back_to_list$'))

if __name__ == "__main__":
    application.run_polling()
