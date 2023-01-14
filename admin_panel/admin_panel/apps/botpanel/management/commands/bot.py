from django.db import models
from django.core.management.base import BaseCommand
from django.conf import settings
from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, Message, ChatMemberUpdated
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
from botpanel.models import BotsPanel
from commands.models import AsksForFAQ, ServicesList, ClientsReviews
from manager.models import OrdersFromBot, StatusOrder

#STATES
CANCEL_TEXT,START_TEXT,CHOOSING,ASK_FOR,DONE_ORDER, RETURN_TO_START = range(6)
REVIEW_START= range(1)

#CALLBACK
SERVICES, TAKE, RETURN = range(3)

#CONSTANTS
ordered_service = list()
ordered_service_price = list()
managers_id_chat = #YOUR FIRST GROUP


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
def send_faq(update: Update, context: CallbackContext) -> None:
	chat_id = update.message.chat_id
	text = update.message.text
	all_faqs = AsksForFAQ.objects.all()
	update.message.reply_text(text='Ответы на часто задаваемые вопросы!: ',)
	reply = ''
	
	for faq in all_faqs:
		reply += f"*{faq.faq_name}* {faq.faq_ask}" + "\n\n"
	update.message.reply_text(text=f'{reply}',parse_mode=ParseMode.MARKDOWN)

@logerrors
def send_reviews(update: Update, context: CallbackContext) -> None:
	chat_id = update.message.chat_id
	text = update.message.text
	all_reviews = ClientsReviews.objects.all()
	reply = 'Отзывы!\n\n'

	for review in all_reviews:
		reply += (f'*{review.review_user}*\n__{review.review_text}__' + '\n')
	
	update.message.reply_text(text=f'{reply}' + '\nЕсли хочешь оставить свой отзыв, нажмите на /myreview', parse_mode=ParseMode.MARKDOWN)


#________________Conv_handler-User review___________________#

@logerrors
def user_typeing_review(update: Update, context: CallbackContext) -> None:
	chat_id = update.message.chat_id

	if ClientsReviews.objects.filter(review_chat_id=chat_id):
		update.message.reply_text(text='Вы уже оставляли отзыв))')
		return ConversationHandler.END
	
	else:
		update.message.reply_text(text='Оставьте свой отзыв :)')
		return REVIEW_START

@logerrors
def user_create_review(update: Update, context: CallbackContext) -> None:
	chat_id = update.message.chat_id
	text = update.message.text
	all_reviews = ClientsReviews.objects.all()
	ClientsReviews(
		review_text=text,
		review_user=update.message.from_user.first_name,
		review_username=update.message.from_user.username,
		review_chat_id=chat_id,
		).save()
	
	update.message.reply_text('Спасибо за отзыв')
	return ConversationHandler.END

#________________END OF CONV_HANDLER USER review_________________________#

@logerrors
def send_services(update: Update, context: CallbackContext) -> None:
	all_services = ServicesList.objects.all()
	reply = 'Наши услуги! :)\n\n'
	for service in all_services:
		reply += f'{service.id}: {service.service_name}:\nЦена: {service.service_price}руб \nОписание: {service.service_description}' + "\n\n"
	try:
		keyboard = [InlineKeyboardButton(i.id, callback_data=i.id) for i in all_services]
		query = update.callback_query
		query.answer()
		query.edit_message_text(text=f"{reply}")
		query.message.reply_text(text='\nЭто номера услуг, представленных выше, просто нажмите на одну из кнопок',reply_markup=InlineKeyboardMarkup(keyboard_cols(keyboard, cols=4)))
		return CHOOSING
	
	except:
		chat_id = update.message.chat_id
		update.message.reply_text(text=reply)

# ___________________________________________________________________________________________________________#

def help_message(update: Update, context: CallbackContext):
	if update.message.chat_id == managers_id_chat:
		return
	
	update.message.reply_text(text='Напишите эти комманды:\n/faq - Ответы на часто задаваемы вопросы \n/review - просмотреть отзывы \n/services - наши сервисы \
									\n/order - заказать сервисы')


def start(update: Update, context: CallbackContext) -> int: #/start
	chat_id = update.message.chat_id
	text = update.message.text
	send_text = update.effective_message
	send_text.reply_text(text=f'Хай! Моё имя {context.bot.get_me().first_name}!\nТребуется помощь? Напиши - \'/help\' \nДля заказа напиши \'/order\'',)


@logerrors
def info_for_user(update: Update, context: CallbackContext) -> int:
	
	keyboard = [
		[
			InlineKeyboardButton(f'Список сервисов', callback_data=str(SERVICES)),
		]
	]
	try:
		chat_id = update.message.chat_id
		text = update.message.text
		send_text = update.effective_message
		send_text.reply_text(text=f'''Привет,{update.message.from_user.first_name}! \nКакую услугу вы хотите?''', 
									reply_markup=InlineKeyboardMarkup(keyboard),
							)
	except:
		query = update.callback_query
		query.answer()
		query.message.reply_text(text=f'''Привет,{update.callback_query.from_user.first_name}! \nКакую услугу вы хотите?''', 
									reply_markup=InlineKeyboardMarkup(keyboard),)

	return CHOOSING


@logerrors
def service_choice(update: Update, context: CallbackContext) -> int:
	
	all_services = ServicesList.objects

	try:
		text = update.message.text
		for service in all_services.filter(id=int(text)):
			if (int(text) == service.id):
				update.message.reply_text(text=f'Вы выбрали это: \nНомер услуги:{service.id}, \
				\nУслуга:{service.service_name},\n Цена услуги:{service.service_price}$\nХотите изменить услугу?\n\'Да/Нет\'')
				ordered_service.append(service.service_name)
				ordered_service_price.append(service.service_price)
				return ASK_FOR
			else:
				update.message.reply_text(text='Хмммм, попробуйте снова... Выберите номер услуги/напишите его')
				return CHOOSING
	except:
		query = update.callback_query
		query.answer()
		keyboard = [[InlineKeyboardButton('Да!', callback_data='1')],[InlineKeyboardButton('Нет!',callback_data='2')]]
		for service in all_services.filter(id=int(query.data)):
			query.edit_message_text(
				text=f'Вы выбрали это: \nНомер услуги: {service.id}, \
						\nУслуга: {service.service_name},\nЦена услуги: {service.service_price}руб\nХотите изменить услугу?\n\'Да/Нет\'',
				reply_markup=InlineKeyboardMarkup(keyboard)
				)
			ordered_service.append(service.service_name)
			ordered_service_price.append(service.service_price)

		return ASK_FOR


@logerrors
def customize_choice(update: Update, context: CallbackContext) -> int:
	new_chat = managers_id_chat

	try:
		query = update.callback_query
		query.answer()
		chat_id = query.message.chat_id

		if query.data == '1':
			keyboard = [[InlineKeyboardButton('Вернусться к выбору',callback_data=str(RETURN))]]
			query.edit_message_text(text=f'Выберите другую услугу', reply_markup=InlineKeyboardMarkup(keyboard))
			del ordered_service[0]
			del ordered_service_price[0]
			return RETURN_TO_START
			
		elif query.data == '2':
			query.message.reply_text('Заполните свои контакты и оставьте свой комментарий, порядок не имеет значения. \
				\n{Номер} +711520323,\n{Имя} Булкин Виталий Андреевич,\n{Адрес} г.Минск, р-н Николаевки, дом 13Б, кв 19\n{Что произошло} Сломался выключатель)')
			OrdersFromBot(
				user_name=f'{query.message.from_user.username}',
				chat_id_user = chat_id,
				services_name = ordered_service[0],
				order_price = ordered_service_price[0],
				).save()
			return DONE_ORDER

	except:
		text = update.message.text
		send_text = update.message
		chat_id = update.message.chat_id
		if text.lower() == 'да':
			send_text.reply_text(text=f'Выберите другую услугу')
			del ordered_service[0]
			del ordered_service_price[0]
			return CHOOSING
		elif text.lower() == 'нет':
			send_text.reply_text('Заполни свои контакты и оставь свой комментарий, порядок не имеет значения. \
				\n{Номер} +711520323,\n{Имя} Булкин Виталий Андреевич,\n{Адрес} г.Минск, р-н Николаевки, дом 13Б, кв 19\n{Что произошло} Сломался выключатель)')
			OrdersFromBot(
				user_name=f'{update.message.from_user.first_name}',
				chat_id_user = chat_id,
				services_name = ordered_service[0],
				order_price = ordered_service_price[0],
				).save()
			return DONE_ORDER
		else:
			update.message.reply_text(text='Что-то пошло не так, выберите новую услугу: Введите номер')
			del ordered_service[0]
			del ordered_service_price[0]		
			return CHOOSING


def user_self_info(update: Update, context: CallbackContext):
	new_chat = managers_id_chat

	text = update.message.text
	send_text = update.message.reply_text
	chat_id = update.message.chat_id

	for edit in OrdersFromBot.objects.filter(chat_id_user=chat_id,):
		pass

	OrdersFromBot(
		id=edit.id,
		user_name=f'{update.message.from_user.username}',
		chat_id_user = chat_id,
		services_name = edit.services_name,
		order_price = edit.order_price,
		user_contact_info = text,
		).save()
	send_text(text=f'Ваш заказ поступил нашим менеджерам. Ожидайте - не скучайте :)!')

	for new_order in OrdersFromBot.objects.filter(chat_id_user=chat_id,id=edit.id):
		pass
	context.bot.send_message(text=f'У вас новый заказ! \nНомер заказа: {new_order.id}\nПользователь: {new_order.user_name} \
		\nУслуга: {new_order.services_name} {new_order.order_price}$\nИнфо: {new_order.user_contact_info}\nНапишите \"/inorder@Testing_ManagersDB_bot\" чтобы изменять статус заказа', chat_id=new_chat)

	del ordered_service[0]
	del ordered_service_price[0]

	return ConversationHandler.END

#_____________________________________________________________________________________________________#

@logerrors
def done_order(update: Update, context: CallbackContext) -> int:
	update.message.reply_text(text='Хопа')
	return CANCEL_TEXT


@logerrors
def cancel_text(update: Update, context: CallbackContext) -> int:
	return ConversationHandler.END

#______________________________Main class________________________________________________________________________#


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
        	entry_points=[CommandHandler('order', info_for_user),],
	        states={
	        	RETURN_TO_START: [CallbackQueryHandler(info_for_user, pattern="^" + str(RETURN) + "$")],
	        	CANCEL_TEXT: [CommandHandler('cancel', cancel_text),],
	        	START_TEXT: [MessageHandler(Filters.text, info_for_user),],

	        	CHOOSING: [
	        	CommandHandler('services', send_services), 
	        	MessageHandler(Filters.text, service_choice), 
	        	CallbackQueryHandler(send_services, pattern="^" + str(SERVICES) + "$"),
	        	CallbackQueryHandler(service_choice,),
	        	],
	        	ASK_FOR: [
	        				CallbackQueryHandler(customize_choice),
	        				MessageHandler(Filters.text, customize_choice),
						],

	        	DONE_ORDER: [
	        			MessageHandler(Filters.text, user_self_info),
	        			
	        	],
	        },
	        
	        fallbacks=[CommandHandler('done', done_order)],
	        allow_reentry=True,
    	)

		type_review = ConversationHandler(
    		entry_points=[CommandHandler('myreview',user_typeing_review),],
    		states={
    			REVIEW_START: [
    				MessageHandler(Filters.text, user_create_review)
    			],
    		},
    		fallbacks=[CommandHandler('done', done_order)],

    		)
		dp.add_handler(type_review)
		dp.add_handler(CommandHandler('help', help_message))
		dp.add_handler(CommandHandler('start', start))
		dp.add_handler(CommandHandler('faq', send_faq,))
		dp.add_handler(CommandHandler('review', send_reviews,))
		dp.add_handler(CommandHandler('services', send_services,))
		dp.add_handler(conv_handler)

			
		updater.start_polling()
		updater.idle()

		

		



