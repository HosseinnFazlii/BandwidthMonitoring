from django.core.management.base import BaseCommand
from telegram.ext import ApplicationBuilder
import logging

class Command(BaseCommand):
    help = 'Run the Telegram bot'

    def handle(self, *args, **kwargs):
        from telegrambot.views import application

        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.INFO
        )

        application.run_polling()
