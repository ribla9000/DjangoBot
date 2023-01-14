from django.db import models
from django.core.management.base import BaseCommand
from django.conf import settings
from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, Message, ChatMemberUpdated, ChatMember, Chat
from telegram.ext import (
	Updater, CallbackContext, 
	CommandHandler, MessageHandler,
	Updater, CallbackQueryHandler, 
	Defaults, ConversationHandler, 
	Filters, PicklePersistence, 
	ChatMemberHandler
	)
from telegram.utils.request import Request
from telegram import ParseMode
import telepot
from botpanel.models import BotsPanel
from commands.models import AsksForFAQ, ServicesList, ClientsReviews
from manager.models import OrdersFromBot, StatusOrder

PRE_CHANGE_STATUS,CHOOSING, CHANGE_STATUS, CHANGE_STATUS_COMPLETE, CANCEL = range(5)
WORK_START, WORK_CHOOSED = range(2)
WISHLIST,WISHLIST_STATUS = range(2)

choosed_order_id = list()
choosed_new_status_id = list()
choosed_wish_order = list()

#CONSTANTS
managers_id_chat = #YOUR CHAT_ID(GROUP 1)
courier_id_chat = #YOUR SECOND CHAT_ID(GROUP 2)

'''
Try and except must be here for a 2 variant of handlers (CallBackQuery_handler and Message_handler)
'''


def logerrors(f):
	def inner(*args,**kwargs):
		try:
			return f(*args,**kwargs)

		except Exception as e:
			error_message = f'ERROR: {e}'
			print(error_message)
			raise e
	return inner


def keyboard_cols(buttons, cols):
	menu = [buttons[i:i + cols] for i in range(0, len(buttons), cols)]
	return menu


#??????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????


@logerrors
def send_chatid(update: Update, context: CallbackContext):
	chat_id = update.message.chat_id
	update.message.reply_text(text=f'{chat_id}', quote=False)


@logerrors
def help_message(update: Update, context: CallbackContext) -> int:
	managers_chat = managers_id_chat
	courier_chat = courier_id_chat
	current_chat = update.message.chat_id

	if current_chat == managers_chat:
		update.message.reply_text(text='Напишите /inorder -для изменения статуса, Если вы хотите, чтобы груз забрали, то меняйте статус на [3], после чего его увидят курьеры \
			\nнапишите /canceled - для просмотра отмененных заказов.\nнапишите /confirned - для просмотра ожидающих к доставке  \
			\nДля редактирования статуса В РАССМОТРЕНИИ напишите\'/wishlist\''
			 ,quote=False)

	elif current_chat == courier_chat:
		update.message.reply_text(text='Напишите /take - чтобы взять заказ')

	else:
		update.message.reply_text(text='Ваш чат не соответствует настройкам, посмотрите настройки')


#___________________________?LIST OF WAITING?:::WISHLIST:::____________________________________________
@logerrors
def wish_list_pre_change(update: Update, context: CallbackContext):
	text = update.message.text
	send_text = update.message
	all_orders = OrdersFromBot.objects.filter(is_active__id=4)
	reply = "В РАССМОТРЕНИИ\n\n"

	for waiting_order in all_orders:
		reply+= f'{waiting_order}\n\n'

	keyboard=[InlineKeyboardButton(i.id, callback_data=i.id) for i in all_orders]
	update.message.reply_text(quote=False, text=f'{reply}\n\nВыберите номер!', reply_markup=InlineKeyboardMarkup(keyboard_cols(keyboard,cols=4)))

	return WISHLIST


@logerrors
def wish_list_pre_change_status(update, context):
	query = update.callback_query
	query.answer()
	current_order = OrdersFromBot.objects.filter(id=query.data,is_active__id=4)
	reply = "||СТАТУСЫ||\n\n"
	
	if len(choosed_wish_order)>0:
		del choosed_wish_order[::]	
	choosed_wish_order.append(query.data)

	for status in StatusOrder.objects.all():
			reply += f'{status.id}: {status.status_name}\n\n'

	keyboard=[InlineKeyboardButton(i.id, callback_data=i.id) for i in StatusOrder.objects.all()]
	query.message.reply_text(text=f'{reply}\n\nВыберите новый статус', quote=False, reply_markup=InlineKeyboardMarkup(keyboard_cols(keyboard, cols=4)))

	return WISHLIST_STATUS


@logerrors
def wish_list_change(update, context):
	query = update.callback_query
	query.answer()
	current_order = OrdersFromBot.objects.filter(id=int(choosed_wish_order[0]),is_active__id=4)

	for thing in current_order:
		OrdersFromBot(
			id=thing.id,
			user_name=thing.user_name,
			chat_id_user=thing.chat_id_user,
			services_name=thing.services_name,
			order_price=thing.order_price,
			user_contact_info=thing.user_contact_info,
			is_active_id=int(query.data),
			).save()
	for updated in OrdersFromBot.objects.filter(id=int(choosed_wish_order[0]), is_active__id=int(query.data)):
		query.message.reply_text(text=f'Заказ был изменен. Его новые данные:\n{updated} ')
	del choosed_wish_order[0]
	return ConversationHandler.END


#_________________________________?END OF WAITING?__________________________________________



@logerrors
def chat_send_canceled(update: Update, context: CallbackContext) -> int:
	text = update.message.text
	send_text = update.message
	all_orders = OrdersFromBot.objects.filter(is_active__id=2)
	reply = 'ОТМЕНЕННЫЕ!\n\n'
	
	for orders in all_orders:
		reply += f'{orders}\n\n'
	send_text.reply_text(text=f'{reply}', quote=False)


@logerrors
def chat_send_waiting(update: Update, context: CallbackContext) -> int:
	text = update.message.text
	send_text = update.message
	all_orders = OrdersFromBot.objects.filter(is_active__id=3)
	reply = 'ОЖИДАЮЩИЕ ДОСТАВКИ!\n\n'
	
	for orders in all_orders:
		reply += f'{orders}\n\n'
	send_text.reply_text(text=f'{reply}', quote=False)

#_________________________________________________________________________________________________#

@logerrors
def chat_send_orders(update: Update, context: CallbackContext) -> int:
	group_id = update.message.chat_id
	text = update.message.text
	send_text = update.message
	all_orders = OrdersFromBot.objects.filter(is_active__id=1)
	chat_id = update.message.chat_id
	new_chat = managers_id_chat
	reply = 'ЗАКАЗЫ!\n\n'
	i = 0
	keyboard = [[InlineKeyboardButton('Да', callback_data='1'), InlineKeyboardButton('Нет', callback_data='2')]]
	
	if group_id == new_chat:

		for orders in all_orders:
				reply += (f'{orders}' + '\n\n')
				i += 1
		if i > 0:
			send_text.reply_text(text=reply, quote=False) 		
			send_text.reply_text(text=f'Хотите изменить статус заказа?\nДа/Нет',reply_markup=InlineKeyboardMarkup(keyboard) ,quote=False)
			return PRE_CHANGE_STATUS
		else:
			send_text.reply_text(text='Ничего нет!', quote=False)
			return ConversationHandler.END
	else:
		send_text.reply_text(text='...')
		return ConversationHandler.END


@logerrors
def chat_pre_change_status(update: Update, context: CallbackContext) -> int: 
	try:
		text = update.message.text
		send_text = update.message

		if text.lower()=='да':
			send_text.reply_text(text=f'Выберите номер заказа, которому стоит изменить статус', quote=False)
			return CHOOSING
			
		elif text.lower()=='нет':
			send_text.reply_text(text=f'Хорошо, приятно провести время)', quote=False)
			return ConversationHandler.END
		else:
			send_text.reply_text(text=f'Что-то не так,введите /inorder', quote=False)
			return ConversationHandler.END
	except:
		query = update.callback_query
		query.answer()
		all_orders = OrdersFromBot.objects.filter(is_active__id=1)
		keyboard=[InlineKeyboardButton(i.id, callback_data=i.id) for i in all_orders]

		if query.data == '1':
			query.edit_message_text('Выберите номер заказа, которому стоит изменить статус',reply_markup=InlineKeyboardMarkup(keyboard_cols(keyboard,cols=4)))
			return CHOOSING
		elif query.data == '2':
			query.edit_message_text('Хорошо, приятно провести время',)
			return ConversationHandler.END


@logerrors
def chat_chosing_id(update: Update, context: CallbackContext) -> int: 
	try:
		text = update.message.text
		send_text = update.message
		all_orders = OrdersFromBot.objects.filter(is_active__id=1, id=int(text))

		for order in all_orders:
			send_text.reply_text(text=f'Ваш выбор: {text}\n{order}', quote=False)
			choosed_order_id.append(order.id)
			send_text.reply_text(text=f'Какой статус вы хотите?', quote=False)

			return CHANGE_STATUS
	except:
		query = update.callback_query
		query.answer()
		all_orders = OrdersFromBot.objects.filter(is_active__id=1, id=int(query.data))
		reply = 'Статусы:\n'
		keyboard = [[InlineKeyboardButton(i.id, callback_data=i.id) for i in StatusOrder.objects.all()]]

		for status in StatusOrder.objects.all():
			reply += f'{status.id}: {status.status_name}\n\n'

		for order in all_orders:
			query.message.reply_text(text=f'Ваш выбор: {query.data}\n{order}', quote=False,)
			query.message.reply_text(text='Какой статус нужно поставить сейчас?'+f"\n{reply}", quote=False,reply_markup=InlineKeyboardMarkup(keyboard))
			choosed_order_id.append(order.id)	
		
		return CHANGE_STATUS


@logerrors
def chat_chosing_new_status(update: Update, context: CallbackContext) -> int: #CHANGE_STATUS
	
	all_orders = OrdersFromBot.objects
	count_order = 0
	new_chat = courier_id_chat
	
	try:
		text = update.message.text
		send_text = update.message

		for order in all_orders.filter(id=choosed_order_id[0]):
			choosed_new_status_id.append(int(text))

			OrdersFromBot(
				id = order.id,
				user_name= order.user_name,
				chat_id_user = order.chat_id_user,
				services_name = order.services_name,
				order_price = order.order_price,
				user_contact_info = order.user_contact_info,
				is_active_id = choosed_new_status_id[0],
				).save()

		for current_order in all_orders.filter(id=choosed_order_id[0]):
			send_text.reply_text(text=f'Выполнено!\n\n{current_order}')

		for waiting_order in all_orders.filter(is_active__id=3):
			count_order += 1

		context.bot.send_message(text=f'Ребят у вас {count_order} заказ/ов, которые нужно срочно выполнить! :)', chat_id=new_chat,)
		context.bot.send_message(text=f'Ваш заказ рассмотрели и теперь он находится в статусе: {current_order.is_active__status_name}', chat_id=current_order.chat_id_user)

		del choosed_new_status_id[0] 
		del choosed_order_id[0]
		return ConversationHandler.END

	except:
		query = update.callback_query
		query.answer()
		for order in all_orders.filter(id=choosed_order_id[0]):
			choosed_new_status_id.append(int(query.data))

			OrdersFromBot(
				id = order.id,
				user_name= order.user_name,
				chat_id_user = order.chat_id_user,
				services_name = order.services_name,
				order_price = order.order_price,
				is_active_id = choosed_new_status_id[0],
				user_contact_info = order.user_contact_info,
				).save()

		for current_order in all_orders.filter(id=choosed_order_id[0]):
			query.message.reply_text(text=f'Выполнено!\n\n{current_order}')

		for waiting_order in all_orders.filter(is_active__id=3):
			count_order += 1

		context.bot.send_message(text=f'Ребят у вас {count_order} заказ/ов, которые нужно срочно выполнить!\nВведите /take:)', chat_id=new_chat,)

		del choosed_new_status_id[0] 
		del choosed_order_id[0]
		return ConversationHandler.END


@logerrors
def chat_cancel(update: Update, context: CallbackContext) -> int:
	update.message.reply_text(text='Отменено', quote=False)
	return ConversationHandler.END
#______________________________________________________________________________________________________________________#
#____________________________________GROUP2____________________________________________________________________________#

@logerrors
def work_group_start(update: Update, context: CallbackContext) -> int:
	text = update.message.text
	send_text = update.message.reply_text
	waiting_for_bring_objects = OrdersFromBot.objects
	group_id = update.message.chat_id
	new_chat = courier_id_chat
	reply = 'Заказы!\n\n'
	keyboard = [InlineKeyboardButton(i.id, callback_data=i.id) for i in waiting_for_bring_objects.filter(is_active__id=3)]

	if group_id == new_chat:

		for order in waiting_for_bring_objects.filter(is_active__id=3):
			reply+=f'{order}\n\n'
		send_text(text=f'{reply}\nВыберите заказ который нужно выполнить.\n\nНапишите номер или нажмите на кнопку!', 
					quote=False,
					reply_markup=InlineKeyboardMarkup(keyboard_cols(keyboard, 4)),
				)

		return WORK_CHOOSED

	else:
		send_text(text='У вас нет прав для использования этой команды', quote=False)
		return ConversationHandler.END


@logerrors
def work_group_choose_order_to_bring(update: Update, context: CallbackContext) -> int:
	bring_objects = OrdersFromBot.objects
	new_chat = managers_id_chat

	try:
		text = update.message.text
		send_text = update.message.reply_text

		for order in bring_objects.filter(is_active__id=3,id=int(text)):
			if int(text) == order.id and (order.is_active_id==3):
				send_text(text=f'Ваш заказ:\n{order}\nИнфо: {order.user_contact_info}')
				OrdersFromBot(
					id = order.id,
					user_name= order.user_name,
					chat_id_user = order.chat_id_user,
					services_name = order.services_name,
					order_price = order.order_price,
					is_active_id = 5,
					user_contact_info = order.user_contact_info,
					).save()
				
				context.bot.send_message(chat_id=new_chat,text=f'Номер заказа: {order.id}\nТелеграмм: @{order.user_name}\nУслуга:  \
					{order.services_name} {order.order_price}$\nВыполняется @{update.message.from_user.username} доставщиком',)
			elif (order.is_active_id != 3) or (int(text) != order.id):
				send_text(text="Что-то тут не так\nНапишите /take")
				return ConversationHandler.END

		return ConversationHandler.END

	except:
		query = update.callback_query
		query.answer()

		for order in bring_objects.filter(is_active__id=3,id=int(query.data)):
			query.message.reply_text(f'Ваш заказ:\n{order}\n', quote=False)
			OrdersFromBot(
				id = order.id,
				user_name= order.user_name,
				chat_id_user = order.chat_id_user,
				services_name = order.services_name,
				order_price = order.order_price,
				user_contact_info = order.user_contact_info,
				is_active_id = 5,
				).save()

			context.bot.send_message(chat_id=new_chat,text=f'Номер заказа: {order.id}\nТелеграмм: @{order.user_name}\nУслуга:  \
					{order.services_name} {order.order_price}$\nВыполняется @{query.from_user.username} доставщиком',)

			context.bot.send_message(chat_id=order.chat_id_user, text=f'Ваш заказ взял @{query.from_user.username}, Для связи с ним - напишите ему')
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
		
		conv_handler_for_managers = ConversationHandler(
			entry_points=[CommandHandler('inorder', chat_send_orders)],
			states={

					PRE_CHANGE_STATUS: [
							MessageHandler(Filters.text, chat_pre_change_status),
							CallbackQueryHandler(chat_pre_change_status),
							],
					CHOOSING: [	MessageHandler(Filters.text, chat_chosing_id),
								CallbackQueryHandler(chat_chosing_id),
								],
					CHANGE_STATUS: [
									MessageHandler(Filters.text, chat_chosing_new_status),
									CallbackQueryHandler(chat_chosing_new_status),
									],
			},
			fallbacks=[MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^Done$')), chat_cancel),],
			allow_reentry=True,
		)

		conv_handler_for_courier = ConversationHandler(
			entry_points=[CommandHandler('take', work_group_start)],
			states={

			WORK_CHOOSED: [MessageHandler(Filters.text, work_group_choose_order_to_bring,),
							CallbackQueryHandler(work_group_choose_order_to_bring),
							], 
			},
			fallbacks=[CommandHandler('cancel', chat_cancel)],
			allow_reentry=True,
			)

		conv_handler_wishlist = ConversationHandler(
				entry_points=[CommandHandler('wishlist',wish_list_pre_change)],

				states={

					WISHLIST: [CallbackQueryHandler(wish_list_pre_change_status)],
					WISHLIST_STATUS: [CallbackQueryHandler(wish_list_change)]

				},

			fallbacks=[MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^Done$')), chat_cancel),],
			allow_reentry=True,
			)

		dp.add_handler(conv_handler_for_managers)
		dp.add_handler(conv_handler_for_courier)
		dp.add_handler(conv_handler_wishlist)
		dp.add_handler(CommandHandler('canceled', chat_send_canceled))
		dp.add_handler(CommandHandler('confirned', chat_send_waiting))
		dp.add_handler(CommandHandler('help', help_message))
		dp.add_handler(CommandHandler('chatid', send_chatid))

		updater.start_polling(allowed_updates=Update.ALL_TYPES)
		updater.idle()