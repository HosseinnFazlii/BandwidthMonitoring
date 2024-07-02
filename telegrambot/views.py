from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from telegram import Update, Bot
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters, CallbackContext
import json

TELEGRAM_TOKEN = '7440118014:AAGraEs0pKtqjLCq2E6hK_i7tg2sFM2pkk4'
bot = Bot(token=TELEGRAM_TOKEN)

def start(update: Update, context: CallbackContext):
    update.message.reply_text('Welcome to the Django monitoring bot! Use /help to see available commands.')

def help(update: Update, context: CallbackContext):
    commands = [
        '/start - Start the bot',
        '/help - Show this help message',
        '/status - Get the current server status',
    ]
    update.message.reply_text('\n'.join(commands))

def status(update: Update, context: CallbackContext):
    # Here you should integrate your Django logic to get the server status
    status_info = "Server is up and running."  # Replace with actual status info
    update.message.reply_text(status_info)

@csrf_exempt
def webhook(request):
    if request.method == 'POST':
        update = Update.de_json(json.loads(request.body), bot)
        dispatcher.process_update(update)
    return JsonResponse({'status': 'ok'})

dispatcher = Dispatcher(bot, None, workers=0)
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('help', help))
dispatcher.add_handler(CommandHandler('status', status))

