import sys
import logging
import shutil
from django.apps import AppConfig
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

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
    context.bot.send_message(chat_id=update.message.chat_id, text="I'm a bot, please talk to me!")

def photo(update, context):
    from photos.models import Photo
    out = update.message.photo[-1].get_file().download()
    path = f"media/images/{out}"
    shutil.move(out, path)
    image = f"images/{out}"
    Photo.objects.create(title=out, image=image)
    context.bot.send_message(chat_id=update.message.chat_id, text="Photo uploaded!")
