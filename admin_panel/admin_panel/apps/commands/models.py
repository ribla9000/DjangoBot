from django.db import models
from django.conf import settings
from botpanel.models import *


class AsksForFAQ(models.Model):
	faq_name = models.TextField(max_length=48,
								verbose_name='FAQ',
								help_text='Какой-то вопрос',
								)
	faq_ask = models.TextField(verbose_name='ASK',
							   help_text='Ответ',
								)
	def __str__(self):
		return f'{self.faq_name}'
	
	class Meta:
		verbose_name="FAQ"
		verbose_name_plural = "FAQ"

class ServicesList(models.Model):
	service_name = models.TextField(verbose_name='Услуга',
							   help_text='Имя услуги',
								)
	service_price = models.IntegerField(verbose_name='Цена',
							   help_text='Цена за единицу',
								)
	service_description = models.TextField(verbose_name='Description',
							   help_text='Опишите услугу',
								)
	
	def __str__(self):
		return f'{self.service_name}'
	
	class Meta:
		verbose_name="Сервис"
		verbose_name_plural='Сервисы'

class AdvertisementsCalculator(models.Model):
	advertisement_name = models.TextField(verbose_name='Название рекламы',
							   			  help_text='Гугл Адс',
								)
	advertisement_income = models.IntegerField(verbose_name='Вложения',
							   				   help_text='Сколько',
								)
	advertisement_expenditure = models.IntegerField(verbose_name='Потери',
							   						help_text='Сколько',
								)
	advertisement_profit = models.IntegerField(verbose_name='Доход',
							   				   help_text='Результат в %, оставьте это поле пустым',
							   				   blank=True,
								)

	def save(self, *args, **kwargs):
		price_per_ad = self.advertisement_expenditure
		self.price_per_ad = price_per_ad
		self.advertisement_profit=((self.advertisement_income-self.price_per_ad)/self.price_per_ad)*100
		super(AdvertisementsCalculator, self).save(*args, **kwargs)

	def __str__(self):
		return f'{self.advertisement_name}'
	
	class Meta:
		verbose_name="Калькулятор рекламы"
		verbose_name_plural='Калькулятор рекламы'

# class CompanyPosts(models.Model):
# 	person_post = models.TextField(verbose_name='Должность',
# 									help_text='Курьер/CEO/Глава',
# 								)

# 	def __str__(self):
# 		return f'{self.person_post}'

# 	class Meta:
# 		verbose_name="Должность"
# 		verbose_name_plural = 'Должности'

# class StaffinCompany(models.Model):
# 	person_name = models.TextField(verbose_name='Имя человека',
# 							   	   help_text='Alex Wednesday jr.',
# 								)
# 	telegram_userid = models.IntegerField(verbose_name='ID телеграмма',
# 											blank=False,
# 											default=None,
# 								)
# 	telegram_nickname = models.TextField(verbose_name='Telegram никнейм',
# 							   	   help_text='Skinny Jeans',
# 							   	   default=None,
# 								)
# 	telegram_username = models.TextField(verbose_name='Telegram имя',
# 							   	   help_text='@SomeBody',
# 							   	   default=None,
# 								)
# 	person_post = models.ForeignKey(CompanyPosts, on_delete=models.DO_NOTHING, 
# 										verbose_name='Должность',	
# 										default=None)
# 	person_payment = models.IntegerField(verbose_name='Зарплата',
# 							   			 blank=False,
# 								)

# 	def __str__(self):
# 		return f'{self.person_name}'
	

class ClientsReviews(models.Model):
	review_text = models.TextField(verbose_name='Отзывы')
	review_user = models.TextField(verbose_name='Пользователь который оставил',null=True)
	review_username = models.TextField(verbose_name='Пользователь который оставил',null=True, blank=False)
	review_chat_id = models.IntegerField(verbose_name='ID пользователя', default=0)

	class Meta:
		verbose_name="Отзыв пользователя"
		verbose_name_plural='Отзыв пользователя'
