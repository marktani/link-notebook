#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Notebook bot to send websites as a PDF to your email."""

import logging
import pdfkit
import cuid
import datetime
import sendgrid
import re
import base64
import os
from telegram.ext import Updater, CommandHandler
from sendgrid.helpers.mail import *


# initialize a map of Telegram user id to email address
userconfig = {}

SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

helpText = 'Hi! I can send websites as a PDF to your email address.\nTo get started, run `/setEmail <your@email.com>`.\nThen you can run `/note http://example.com` to convert a website to a PDF and send it to your email address.\nRun `/help` to show this message again.'


def start(bot, update):
    update.message.reply_text(helpText)


def help(bot, update):
    update.message.reply_text(helpText)


def note(bot, update):
    if os.getenv('LINK_NOTEBOOK_DEBUG'):
        userconfig[update.message.chat.id] = os.getenv('DEBUG_EMAIL')

    if userconfig[update.message.chat.id]:
        timestamp = datetime.datetime.today().isoformat()
        cuidStamp = cuid.cuid()
        website = update.message.text.split()[1]
        output = f'{timestamp}_{cuidStamp}.pdf'

        pdfkit.from_url(website, output)

        with open(output, "rb") as file:
            data = file.read()

        encoded = base64.b64encode(data).decode()

        attachment = Attachment()
        attachment.content = encoded
        attachment.type = 'application/pdf'
        attachment.filename = output
        attachment.disposition = 'attachment'
        attachment.content_id = 'Note'

        sg = sendgrid.SendGridAPIClient(apikey=SENDGRID_API_KEY)
        from_email = Email(os.getenv('FROM_EMAIL'))
        to_email = Email(userconfig[update.message.chat.id])
        subject = f'A new note from notebook-bot for {update.message.chat.first_name}!'
        content = Content('text/plain', f'Hi {update.message.chat.first_name}, here is a note for you!')

        mail = Mail(from_email, subject, to_email, content)
        mail.add_attachment(attachment)

        response = sg.client.mail.send.post(request_body=mail.get())
        print(response.status_code)
        print(response.body)
        print(response.headers)
        update.message.reply_text(f'Sent the PDF to {userconfig[update.message.chat.id]}!')
    else:
        update.message.reply_text('To start, set a recipient email address using `/setEmail my@email.com`!')


def setEmail(bot, update):
    newEmail = update.message.text.split()[1]
    chatId = update.message.chat.id

    # thanks https://stackoverflow.com/a/8022584/1176596
    if not re.match(r"[^@]+@[^@]+\.[^@]+", newEmail):
        update.message.reply_text('This is not a valid email address! Try again.')
    else:
        userconfig[chatId] = newEmail
        update.message.reply_text('Successfully saved email address.')


def debug(bot, update):
    print(update.message)
    print(userconfig)


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    updater = Updater(os.getenv('TELEGRAM_BOT_TOKEN'))

    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('help', help))
    dispatcher.add_handler(CommandHandler('note', note))
    dispatcher.add_handler(CommandHandler('setEmail', setEmail))

    if os.getenv('LINK_NOTEBOOK_DEBUG'):
        dispatcher.add_handler(CommandHandler('debug', debug))

    dispatcher.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
