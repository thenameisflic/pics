import sys
import os
import logging
import shutil
from django.apps import AppConfig
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from django.template.defaultfilters import slugify

# .env support
import environ
env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)
# reading .env file
environ.Env.read_env()

class TelegramUploaderConfig(AppConfig):
    name = 'telegram_uploader'

    def ready(self):
        if 'runserver' not in sys.argv:
            return True

        updater = Updater(token=env('TELEGRAM_TOKEN'), use_context=True)
        dispatcher = updater.dispatcher
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
        start_handler = CommandHandler('start', start)
        dispatcher.add_handler(start_handler)
        photo_handler = MessageHandler(Filters.photo, photo)
        dispatcher.add_handler(photo_handler)
        updater.start_polling()

def start(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text="Send me a photo to upload it!")

def photo(update, context):
    from photos.models import Photo
    out = update.message.photo[-1].get_file().download()
    filename, file_extension = os.path.splitext(out)
    title = update.message.caption if update.message.caption else out
    path = f"media/images/{slugify(title)}{file_extension}"
    shutil.move(out, path)
    image = f"images/{slugify(title)}{file_extension}"
    Photo.objects.create(title=title, image=image)
    context.bot.send_message(chat_id=update.message.chat_id, text="Photo uploaded!")
