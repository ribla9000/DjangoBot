from django.db import models
from django.core.management.base import BaseCommand,  no_translations
from django.conf import settings
import telegram
# from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, Message 
# from telegram.ext import Updater, ContextTypes, CommandHandler, MessageHandler, Updater, CallbackQueryHandler, ContextTypes, ExtBot, Defaults, ConversationHandler, Filters, PicklePersistence
# from telegram.utils.request import Request
from telegram.constants import ParseMode
import asyncio
from botpanel.models import *
from commands.models import *
import datetime
import django.db
import logging
import time
from multiprocessing import Pool, pool
from asgiref.sync import async_to_sync, sync_to_async
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
    ExtBot,
)
Filters = filters
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
async def send_faq(update: Update, context: ContextTypes) -> None:
	chat_id = update.message.chat_id
	text = update.message.text
	send_text = update.message
	all_faqs = AsksForFAQ.objects.all()
	await send_text.reply_text(text='THERE ARE FAQs: ',)
	for faq in all_faqs:
		await update.message.reply_text(text=f'*{faq.faq_name}*\n\n{faq.faq_ask}',parse_mode=ParseMode.MARKDOWN_V2)

@logerrors
async def send_reviews(update: Update, context: ContextTypes) -> None:
	chat_id = update.message.chat_id
	text = update.message.text
	all_reviews = ClientsReviews.objects.all()
	for review in all_reviews:
		await update.message.reply_text(text=f'.{review.review_user}\n\n{review.review_text}',)

@logerrors
async def send_services(update: Update, context: ContextTypes) -> None:
	chat_id = update.message.chat_id
	text = update.message.text
	all_services = ServicesList.objects.all()
	for service in all_services:
		await update.message.reply_text(text=f'{service.id} {service.service_name}:\nPrice: {service.service_price} \nDescription: {service.service_description}')

@logerrors
async def start(update: Update, context: ContextTypes) -> int: #/start
	chat_id = update.message.chat_id
	text = update.message.text
	send_text = update.effective_message
	await send_text.reply_text(text='''Hi there! What service do you want?\nIf you don\'t know any services, just text \'/services\', to order write \'/buy\'
									\nNext step: Choose ID (the number before the name)	''',)

	return CHOOSING

@logerrors
def service_choice(update: Update, context: ContextTypes, ) -> int: #CHOOSING
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
def customize_choice(update: Update, context: ContextTypes) -> int:
	update.message.reply_text('Do you want to order one more?\nYes/No')
	if update.message.text == 'Yes':
		return CHOOSING
	else:
		update.message.reply_text('Okey, its done')
		return TYPING_CHOICE

@logerrors
def huuh(update: Update, context: ContextTypes) -> int:
	update.message.reply_text(text='Done')
	return CHOOSING

@logerrors
def done(update: Update, context: ContextTypes) -> int:
	if 'choice' in context.user_data:
		del context.user_data['choice']
	return ConversationHandler.END

async def send_hi(update: Update, context: ContextTypes):
	await update.message.reply_text(text='Hi')

async def talk_2(update: Update, context: ContextTypes):
	text = update.message.text
	send_text = update.effective_message
	chat_id = update.message.chat_id
	await send_text.reply_text(text=f'Ur name is {text}')

class Command(BaseCommand):
	help = 'Telegram-Bot'
	def handle(self, *args, **options):
		application = Application.builder().token(settings.TOKEN).build()
		application.add_handler(CommandHandler('faq',send_faq))
		application.add_handler(CommandHandler('hi',send_hi))
		print(application.bot.get_me())

		#Commands

		conv_handler = ConversationHandler(
	    	entry_points=[CommandHandler('start', start)],
	        states={ 
	            CHOOSING: [
	                MessageHandler(
	                    Filters.TEXT, service_choice
	                ),
	                MessageHandler(Filters.TEXT, customize_choice),
	            ],
	            TYPING_CHOICE: [
	                # MessageHandler(Filters.TEXT & ~(Filters.COMMAND | Filters.Regex('^Done$')), huuh),
	                MessageHandler(Filters.TEXT & ~(Filters.COMMAND | Filters.Regex('^Done$')),huuh),
	            ],
	            TYPING_REPLY: [
	                MessageHandler(Filters.TEXT,customize_choice),

	            ],
	        },
	        
	        fallbacks=[CommandHandler('done', huuh)], 
		)
		application.add_handler(conv_handler)
		application.add_handler(CommandHandler('faq', send_faq))
		application.add_handler(CommandHandler('review', send_reviews,))
		application.add_handler(CommandHandler('services', send_services,))
		application.add_handler(MessageHandler(Filters.TEXT, do_echo))
		application.run_polling()		

		


		

		



