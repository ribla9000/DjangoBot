from django.db import models
from django.conf import settings
from botpanel.models import *

class StatusOrder(models.Model):
	status_name = models.TextField(verbose_name='Статус заказа',blank=False)
	is_active = models.BooleanField(default=True,verbose_name='Активен?', null=False,)
	def __str__(self):
		return f'{self.status_name}'
	class Meta:
		verbose_name='Статус'
		verbose_name_plural='Статусы'


class OrdersFromBot(models.Model):
	user_name = models.TextField(verbose_name='Имя пользователя', blank=True)
	chat_id_user = models.PositiveIntegerField(verbose_name='ID пользователя',)
	services_name = models.TextField(verbose_name='Наименование услуги', blank=True)
	order_price = models.IntegerField(blank=True,verbose_name='Цена заказа')
	user_contact_info = models.TextField(verbose_name='Информация о пользователе',blank=True,)
	is_active = models.ForeignKey(StatusOrder, verbose_name='Статус', on_delete=models.DO_NOTHING, default=True,)
	def __str__(self):
		return f'Пользователь: @{self.user_name},\nУслуга: {self.services_name} {self.order_price}руб,\nСтатус: {self.is_active},\nНомер заказа: {self.id}\nИнформация от пользователя: {self.user_contact_info}'
	class Meta:
		verbose_name='Заказ'
		verbose_name_plural='Заказы'



