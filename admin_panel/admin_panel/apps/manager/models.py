from django.db import models
from django.conf import settings
from botpanel.models import *

class StatusOrder(models.Model):
	status_name = models.TextField(verbose_name='Status of order',help_text='Ordered/Canceled', blank=False)
	is_active = models.BooleanField(default=True,verbose_name='Active?', null=False,)
	def __str__(self):
		return f'{self.status_name}'
	class Meta:
		verbose_name='Status'
		verbose_name_plural='Statuses'


class OrdersFromBot(models.Model):
	user_name = models.TextField(verbose_name='User\'s name', blank=True)
	chat_id_user = models.PositiveIntegerField(verbose_name='User ID',)
	services_name = models.TextField(verbose_name='Service Name', help_text='don\'t touch', blank=True)
	order_price = models.IntegerField(blank=True)
	user_contact_info = models.TextField(verbose_name='User INFO', help_text='don\'t touch', blank=True,)
	is_active = models.ForeignKey(StatusOrder, verbose_name='Status', on_delete=models.DO_NOTHING, default=True,)
	def __str__(self):
		return f'User: {self.user_name},\nservice: {self.services_name} {self.order_price}$,\nstatus: {self.is_active},\nNUMBER: {self.id}'
	class Meta:
		verbose_name='Order'
		verbose_name_plural='Orders'



