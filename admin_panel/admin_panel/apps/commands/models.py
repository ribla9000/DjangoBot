from django.db import models
from django.conf import settings
from botpanel.models import *


class AsksForFAQ(models.Model):
	faq_name = models.TextField(max_length=48,
								verbose_name='FAQ',
								help_text='Write Some Question',
								)
	faq_ask = models.TextField(verbose_name='ASK',
							   help_text='...',
								)
	def __str__(self):
		return f'{self.faq_name}'
	
	class Meta:
		verbose_name="FAQ"
		verbose_name_plural = "FAQs"

class ServicesList(models.Model):
	service_name = models.TextField(verbose_name='Service',
							   help_text='...',
								)
	service_price = models.IntegerField(verbose_name='Price',
							   help_text='how much?',
								)
	service_description = models.TextField(verbose_name='Description',
							   help_text='Trala-la',
								)
	
	def __str__(self):
		return f'{self.service_name}'
	
	class Meta:
		verbose_name="Service"


class AdvertisementsCalculator(models.Model):
	advertisement_name = models.TextField(verbose_name='Ad name',
							   			  help_text='...',
								)
	advertisement_income = models.IntegerField(verbose_name='Income',
							   				   help_text='how much?',
								)
	advertisement_expenditure = models.IntegerField(verbose_name='Expenditure',
							   						help_text='how much?',
								)
	advertisement_profit = models.IntegerField(verbose_name='Profit',
							   				   help_text='how much? in %',
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
		verbose_name="Advertisement Calculator"

class CompanyPosts(models.Model):
	person_post = models.TextField(verbose_name='Post in company',
									help_text='Courier/CEO/Head',
								)

	def __str__(self):
		return f'{self.person_post}'

	class Meta:
		verbose_name="POST IN COMPANY"

class StaffinCompany(models.Model):
	person_name = models.TextField(verbose_name='Person name',
							   	   help_text='Alex Wednesday jr.',
								)
	telegram_userid = models.IntegerField(verbose_name='ID',
											blank=False,
											default=None,
								)
	telegram_nickname = models.TextField(verbose_name='Telegram Nickname',
							   	   help_text='Skinny Jeans',
							   	   default=None,
								)
	telegram_username = models.TextField(verbose_name='Telegram Username',
							   	   help_text='@SomeBody',
							   	   default=None,
								)
	person_post = models.ForeignKey(CompanyPosts, on_delete=models.DO_NOTHING, 
										verbose_name='Post in company',	
										default=None)
	person_payment = models.IntegerField(verbose_name='Person payment',
							   			 help_text='how much?',
							   			 blank=False,
								)

	def __str__(self):
		return f'{self.person_name}'
	
	class Meta:
		verbose_name="Staffs"

class ClientsReviews(models.Model):
	review_text = models.TextField(verbose_name='Review Text')
	review_user = models.TextField(verbose_name='User', help_text='Who?', null=True)

	class Meta:
		verbose_name="Client Review"
