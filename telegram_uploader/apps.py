import sys
import os
import logging
import shutil
import string
import random
from django.apps import AppConfig
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from django.template.defaultfilters import slugify
import face_recognition
from PIL import Image, ImageDraw

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

    # Save the original
    original_id = id_generator()
    original_path = f"images/original/{slugify(title)}-{original_id}{file_extension}"
    shutil.move(out, f"media/{original_path}")

    # Watermark and save for authorized users
    watermark = Image.open('watermark.png', 'r').convert("RGBA")
    image_id = id_generator()
    image_path = f"images/auth/{slugify(title)}-{image_id}{file_extension}"
    image = face_recognition.load_image_file(f"media/{original_path}")
    pil_image = Image.fromarray(image).convert("RGBA")
    pil_image.paste(watermark.resize((pil_image.width, pil_image.height)), mask=watermark.resize((pil_image.width, pil_image.height)))
    pil_image.convert("RGB").save(f"media/{image_path}")

    # Create the disguised version for unauthorized users
    disguise = Image.open('disguise.png', 'r')
    face_locations = face_recognition.face_locations(image)

    for (top, right, bottom, left) in face_locations:
        pil_image.paste(disguise.resize((right - left, bottom - top)), (left, top))
    disguised_id = id_generator()
    disguised_path = f"images/anon/{slugify(title)}-{disguised_id}{file_extension}"
    pil_image.convert("RGB").save(f"media/{disguised_path}")

    Photo.objects.create(title=title, image=image_path, disguised_image=disguised_path, original=original_path)

    context.bot.send_message(chat_id=update.message.chat_id, text="Photo uploaded!")

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))
