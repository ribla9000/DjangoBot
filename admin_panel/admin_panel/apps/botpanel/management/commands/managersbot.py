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

PRE_CHANGE_STATUS,CHOOSING, CHANGE_STATUS, CHANGE_STATUS_COMPLETE, CANCEL = range(5)
WORK_START, WORK_CHOOSED = range(2)
choosed_order_id = list()
choosed_new_status_id = list()


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
def chat_send_canceled(update: Update, context: CallbackContext) -> int:
	text = update.message.text
	send_text = update.message
	all_orders = OrdersFromBot.objects.filter(is_active__id=2)

	for orders in all_orders:
		send_text.reply_text(text=f'{orders}', quote=False)

@logerrors
def chat_send_waiting(update: Update, context: CallbackContext) -> int:
	text = update.message.text
	send_text = update.message
	all_orders = OrdersFromBot.objects.filter(is_active__id=3)

	for orders in all_orders:
		send_text.reply_text(text=f'{orders}', quote=False)

#_________________________________________________________________________________________________#

@logerrors
def chat_send_orders(update: Update, context: CallbackContext) -> int:
	group_id = update.message.chat_id
	text = update.message.text
	send_text = update.message
	all_orders = OrdersFromBot.objects.filter(is_active__id=1)
	chat_id = update.message.chat_id
	new_chat = -1001727568926
	reply = 'ORDERS!\n\n'
	i = 0

	if group_id == new_chat:

		for orders in all_orders:
				reply += (f'{orders}' + '\n\n')
				i += 1
		if i > 0:
			send_text.reply_text(text=reply+'END', quote=False) 		
			send_text.reply_text(text=f'Would u like to change a status? Yes/No', quote=False)
			return PRE_CHANGE_STATUS
		else:
			send_text.reply_text(text='There are nothing!', quote=False)
			return ConversationHandler.END
	else:
		send_text.reply_text(text='...')
		return ConversationHandler.END

@logerrors
def chat_pre_change_status(update: Update, context: CallbackContext) -> int: 
	text = update.message.text
	send_text = update.message

	if (text =='Yes') or (text =='yes'):
		send_text.reply_text(text=f'Choose a number', quote=False)
		return CHOOSING
		
	elif (text =='No') or (text =='no'):
		send_text.reply_text(text=f'Okey! Have a nice day!', quote=False)
		return ConversationHandler.END
	else:
		send_text.reply_text(text=f'Something wrong... Text /inorder', quote=False)
		return ConversationHandler.END

@logerrors
def chat_chosing_id(update: Update, context: CallbackContext) -> int: 
	text = update.message.text
	send_text = update.message
	all_orders = OrdersFromBot.objects.filter(is_active__id=1, id=int(text))

	for order in all_orders:
		send_text.reply_text(text=f'Your choice: {text}\n{order}', quote=False)
		choosed_order_id.append(order.id)
		send_text.reply_text(text=f'What status do ya want?\n1:In order\n2:Canceled\n3:Waiting for bring\n\nWrite only number like \'1\'', quote=False)

		return CHANGE_STATUS

@logerrors
def chat_chosing_new_status(update: Update, context: CallbackContext) -> int: #CHANGE_STATUS
	text = update.message.text
	send_text = update.message
	all_orders = OrdersFromBot.objects
	count_order = 0
	new_chat = -760321418

	for order in all_orders.filter(id=choosed_order_id[0]):
		choosed_new_status_id.append(int(text))

		OrdersFromBot(
			id = order.id,
			user_name= order.user_name,
			chat_id_user = order.chat_id_user,
			services_name = order.services_name,
			order_price = order.order_price,
			is_active_id = choosed_new_status_id[0],
			).save()

	for current_order in all_orders.filter(id=choosed_order_id[0]):
		send_text.reply_text(text=f'complited!\n\n{current_order}')

	for waiting_order in all_orders.filter(is_active__id=3):
		count_order += 1

	context.bot.send_message(text=f'Guys, you have {count_order} orders you must complete! :)', chat_id=new_chat,)

	del choosed_new_status_id[0] 
	del choosed_order_id[0]
	return ConversationHandler.END


@logerrors
def chat_cancel(update: Update, context: CallbackContext) -> int:
	update.message.reply_text(text='Canceled', quote=False)
	return ConversationHandler.END
#______________________________________________________________________________________________________________________#
#____________________________________GROUP2____________________________________________________________________________#

@logerrors
def work_group_start(update: Update, context: CallbackContext) -> int:
	text = update.message.text
	send_text = update.message.reply_text
	waiting_for_bring_objects = OrdersFromBot.objects
	group_id = update.message.chat_id
	new_chat = -760321418
	reply = 'ORDERS!\n\n'
	if group_id == new_chat:

		for order in waiting_for_bring_objects.filter(is_active__id=3):
			reply+=f'{order}\n\n'
		send_text(text=f'{reply}'+'\nEND', quote=False)
		send_text(text='Choose some order to complete it.\n\nWrite a number!', quote=False)

		return WORK_CHOOSED

	else:
		send_text(text='You are haven\'t permissions here!', quote=False)
		return ConversationHandler.END

@logerrors
def work_group_choose_order_to_bring(update: Update, context: CallbackContext) -> int:
	text = update.message.text
	send_text = update.message.reply_text
	bring_objects = OrdersFromBot.objects
	new_chat = -1001727568926

	for order in bring_objects.filter(is_active__id=3,id=int(text)):
		if int(text) == order.id and (order.is_active_id==3):
			send_text(text=f'Your Order is \n{order}\nuser-info: {order.user_contact_info}')
			OrdersFromBot(
				id = order.id,
				user_name= order.user_name,
				chat_id_user = order.chat_id_user,
				services_name = order.services_name,
				order_price = order.order_price,
				is_active_id = 6,
				).save()
			
			context.bot.send_message(chat_id=new_chat,text=f'The order Number: {order.id}\nUser-telegram: {order.user_name}\nService:  \
				{order.services_name} {order.order_price}$\nIn progress by @{update.message.from_user.username} ',)
		elif (order.is_active_id != 3) or (int(text) != order.id):
			send_text(text="No... try again.\nWrite /take")
			return ConversationHandler.END

	return ConversationHandler.END


class Command(BaseCommand):
	help = 'Telegram-Bot'
	def handle(self, *args, **options):
		request = Request(
			connect_timeout=10,			
		)
		bot = Bot(
			request=request,
			token=settings.TOKEN_MANAGER_BOT,	
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
			use_context=True,
		)
		dp = updater.dispatcher
		
		conv_handler = ConversationHandler(
			entry_points=[CommandHandler('inorder', chat_send_orders)],
			states={
					PRE_CHANGE_STATUS: [MessageHandler(Filters.text, chat_pre_change_status)],
					CHOOSING: [MessageHandler(Filters.text, chat_chosing_id)],
					CHANGE_STATUS: [MessageHandler(Filters.text, chat_chosing_new_status)],
			},
			fallbacks=[MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^Done$')), chat_cancel),],
			allow_reentry=True,
		)

		conv_handler_work = ConversationHandler(
			entry_points=[CommandHandler('take', work_group_start)],
			states={
			WORK_CHOOSED: [MessageHandler(Filters.text, work_group_choose_order_to_bring,)], 
			},
			fallbacks=[CommandHandler('cancel', chat_cancel)],
			allow_reentry=True,
			)

		dp.add_handler(conv_handler)
		dp.add_handler(conv_handler_work)
		dp.add_handler(CommandHandler('canceled', chat_send_canceled))
		dp.add_handler(CommandHandler('confirned', chat_send_waiting))
		
		updater.start_polling()
		updater.idle()