from django.db import models
from django.core.management.base import BaseCommand
from django.conf import settings
import telegram
from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, Message 
from telegram.ext import Updater, CallbackContext, CommandHandler, MessageHandler, Updater, CallbackQueryHandler, ContextTypes, ExtBot, Defaults, ConversationHandler, Filters, PicklePersistence
from telegram.utils.request import Request
from telegram import ParseMode
from botpanel.models import *
from commands.models import *
import datetime
import django.db
import time
import logging
from typing import Dict
import telepot

CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)

def logerrors(f):
	def inner(*args,**kwargs):
		try:
			return f(*args,**kwargs)

		except Exception as e:
			error_message = f'ERROR: {e}'
			print(error_message)
			raise e
	return inner

@logerrors
def do_echo(update, context):
	print('do_echo')
	chat_id = update.message.chat_id
	text = update.message.text
	p, _ = Profile.objects.get_or_create(
		external_id=chat_id,
		defaults={
			'name': update.message.from_user.username,
		}
	)
	MessagePanel(
		profile=p,
		text=text,
	).save()

@logerrors
def send_faq(update: Update, context: CallbackContext) -> None:
	chat_id = update.message.chat_id
	text = update.message.text
	all_faqs = AsksForFAQ.objects.all()
	update.message.reply_text(text='THERE ARE FAQs: ',)
	for faq in all_faqs:
		update.message.reply_text(text=f'*{faq.faq_name}*\n\n{faq.faq_ask}',parse_mode=ParseMode.MARKDOWN_V2)

@logerrors
def send_reviews(update: Update, context: CallbackContext) -> None:
	chat_id = update.message.chat_id
	text = update.message.text
	all_reviews = ClientsReviews.objects.all()
	for review in all_reviews:
		update.message.reply_text(text=f'.{review.review_user}\n\n{review.review_text}',)

@logerrors
def send_services(update: Update, context: CallbackContext) -> None:
	chat_id = update.message.chat_id
	text = update.message.text
	all_services = ServicesList.objects.all()
	for service in all_services:
		update.message.reply_text(text=f'{service.id} {service.service_name}:\nPrice: {service.service_price} \nDescription: {service.service_description}')

@logerrors
def start(update: Update, context: CallbackContext) -> int: #/start
	chat_id = update.message.chat_id
	text = update.message.text
	send_text = update.effective_message
	send_text.reply_text(text='''Hi there! What service do you want?\nIf you don\'t know any services, just text \'/services\', to order write \'/buy\'
									\nNext step: Choose ID (the number before the name)	''',)

	return CHOOSING

@logerrors
def service_choice(update: Update, context: CallbackContext) -> int: #CHOOSING
	text = update.message.text
	context.user_data['choice'] = text
	all_services = ServicesList.objects
	if text[0]=='/':
		pass
	else:	
		for service in all_services.filter(id=text):
			print(service.id)
			if int(text) == service.id:
				update.message.reply_text(text=f'Your choice: {text}, {service.service_name}, {service.service_price}$')
			else:
				update.message.reply_text(text='try again')
		return TYPING_REPLY

@logerrors
def customize_choice(update: Update, context: CallbackContext) -> int:
	update.message.reply_text('Do you want to order one more?\nYes/No')
	if update.message.text == 'Yes':
		return CHOOSING
	else:
		update.message.reply_text('Okey, its done')
		return TYPING_CHOICE

@logerrors
def huuh(update: Update, context: CallbackContext) -> int:
	update.message.reply_text(text='Done')
	return CHOOSING

@logerrors
def done(update: Update, context: CallbackContext) -> int:
	if 'choice' in context.user_data:
		del context.user_data['choice']
	return ConversationHandler.END

#class и тд.тп для такой простенькой команды как python manage.py bot
class Command(BaseCommand):
	help = 'Telegram-Bot'
	def handle(self, *args, **options):
		persistence = PicklePersistence(filename='bot')
		request = Request(
			connect_timeout=10,
		)
		bot = ExtBot(
			request=request,
			token=settings.TOKEN,
		)
		to_bot_panel, _  = BotsPanel.objects.get_or_create(
			bot_id = bot.get_me().id,
			bot_name = bot.get_me().first_name,
			bot_nickname= bot.get_me().username,
			bot_token= bot.token
		)
		print(bot.get_me())
		updater = Updater(
			bot=bot,
			persistence=persistence,
			use_context=True,
		)
		dp = updater.dispatcher
		
		#Commands

		conv_handler = ConversationHandler(
        	entry_points=[CommandHandler('start', start)],
	        states={ 
	            CHOOSING: [
	                MessageHandler(
	                    Filters.text, service_choice
	                ),
	                MessageHandler(Filters.text, customize_choice),
	            ],
	            TYPING_CHOICE: [
	                # MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^Done$')), huuh),
	                MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^Done$')),huuh),
	            ],
	            TYPING_REPLY: [
	                MessageHandler(Filters.text,customize_choice),

	            ],
	        },
	        
	        fallbacks=[CommandHandler('done', huuh)], 
    	)
		dp.add_handler(conv_handler)
		dp.add_handler(CommandHandler('faq', send_faq,))
		dp.add_handler(CommandHandler('review', send_reviews,))
		dp.add_handler(CommandHandler('services', send_services,))
		dp.add_handler(MessageHandler(Filters.text, do_echo))
			
		updater.start_polling()
		updater.idle()

		

		



