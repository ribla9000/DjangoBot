from django.db import models
from django.core.management.base import BaseCommand
from django.conf import settings
from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, Message, ChatMemberUpdated
from telegram.ext import Updater, CallbackContext, CommandHandler, MessageHandler, Updater, CallbackQueryHandler,Defaults, ConversationHandler, Filters, PicklePersistence, ChatMemberHandler
from telegram.utils.request import Request
from telegram import ParseMode
import telepot
from botpanel.models import BotsPanel
from commands.models import AsksForFAQ, ServicesList, ClientsReviews
from manager.models import OrdersFromBot, StatusOrder



CANCEL_TEXT,START_TEXT,CHOOSING,ASK_FOR,DONE_ORDER = range(5)

ordered_service = list()
ordered_service_price = list()


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

#___________________________________________________________________________________________________________#

def help(update: Update, context: CallbackContext):
	update.message.reply_text(text='Write thoose commands:\n/faq \n/review \n/services - services')

def start(update: Update, context: CallbackContext) -> int: #/start
	chat_id = update.message.chat_id
	text = update.message.text
	send_text = update.effective_message
	send_text.reply_text(text=f'Hi! My name is Nick!\nTo help write - \'/help\' To start text \'/order\'',)

@logerrors
def info_for_user(update: Update, context: CallbackContext) -> int:
	chat_id = update.message.chat_id
	text = update.message.text
	send_text = update.effective_message
	send_text.reply_text(text=f'''Hi there,{update.message.from_user.first_name}! \nWhat service do you want?\nIf you don\'t know any services, just text \'/services\'
										\nNext step: Choose ID (the number before the name)	''',)

	return CHOOSING


@logerrors
def service_choice(update: Update, context: CallbackContext) -> int: #CHOOSING
	text = update.message.text
	all_services = ServicesList.objects
	
	for service in all_services.filter(id=int(text)):
		if (int(text) == service.id):
			update.message.reply_text(text=f'Your choice: {service.id}, {service.service_name}, {service.service_price}$\nDo you want to change ur service?\n\'Yes/No\'')
			ordered_service.append(service.service_name)
			ordered_service_price.append(service.service_price)
			return ASK_FOR
		else:
			update.message.reply_text(text='try again')
			return CHOOSING


@logerrors
def customize_choice(update: Update, context: CallbackContext) -> int:
	text = update.message.text
	send_text = update.message
	chat_id = update.message.chat_id
	new_chat = -1001727568926

	if (text == 'Yes') or (text == 'yes') :
		send_text.reply_text(text=f'Okey, choose a new service')
		del ordered_service[0]
		del ordered_service_price[0]
		return CHOOSING
	elif (text=='No') or (text=='no'):
		send_text.reply_text('Next step: Write ur contact info and a problem \n(number-+711520323, Tanziro, Deamon\'s street\nMy sword is broken.idk to do)')
		OrdersFromBot(
			user_name=f'{update.message.from_user.first_name}',
			chat_id_user = chat_id,
			services_name = ordered_service[0],
			order_price = ordered_service_price[0],
			).save()
		return DONE_ORDER
	else:
		update.message.reply_text(text='Failed! Choose again new number (service number)!')
		del ordered_service[0]
		del ordered_service_price[0]		
		return CHOOSING

def user_self_info(update: Update, context: CallbackContext):
	text = update.message.text
	send_text = update.message.reply_text
	chat_id = update.message.chat_id
	new_chat = -1001727568926
	for edit in OrdersFromBot.objects.filter(chat_id_user=chat_id,):
		pass

	OrdersFromBot(
		id=edit.id,
		user_name=f'{update.message.from_user.first_name}',
		chat_id_user = chat_id,
		services_name = edit.services_name,
		order_price = edit.order_price,
		user_contact_info = text,
		).save()
	send_text(text=f'It\'s done!')

	for new_order in OrdersFromBot.objects.filter(chat_id_user=chat_id,id=edit.id):
		pass
	context.bot.send_message(text=f'You have a new order! \nNUMBER: {new_order.id}\nUser: {new_order.user_name}\nSERVICE: {new_order.services_name} {new_order.order_price}$\nINFO: {new_order.user_contact_info}', chat_id=new_chat)

	del ordered_service[0]
	del ordered_service_price[0]

	return ConversationHandler.END
#__________________________________________________________________________________________________________#

@logerrors
def done_order(update: Update, context: CallbackContext) -> int:
	update.message.reply_text(text='Done')
	return CANCEL_TEXT

@logerrors
def cancel_text(update: Update, context: CallbackContext) -> int:
	return ConversationHandler.END

#___________________________________________________________________________________________________________#


class Command(BaseCommand):
	help = 'Telegram-Bot'
	def handle(self, *args, **options):
		persistence = PicklePersistence(filename='bot')
		request = Request(
			connect_timeout=10,
		)
		bot = Bot(
			request=request,
			token=settings.TOKEN_BOT,
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
        	entry_points=[CommandHandler('order', info_for_user)],
	        states={
	        	CANCEL_TEXT: [CommandHandler('cancel', cancel_text),
	        				  ],
	        	START_TEXT: [MessageHandler(Filters.text, info_for_user),],
	        	CHOOSING: [CommandHandler('services', send_services), MessageHandler(Filters.text, service_choice), ],
	        	ASK_FOR: [MessageHandler(Filters.text, customize_choice),],
	        	DONE_ORDER: [MessageHandler(Filters.text, user_self_info),],
	        },
	        
	        fallbacks=[CommandHandler('done', done_order)], 
    	)

		dp.add_handler(CommandHandler('help', help))
		dp.add_handler(CommandHandler('start', start))
		dp.add_handler(CommandHandler('faq', send_faq,))
		dp.add_handler(CommandHandler('review', send_reviews,))
		dp.add_handler(CommandHandler('services', send_services,))
		dp.add_handler(conv_handler)

			
		updater.start_polling()
		updater.idle()

		

		



