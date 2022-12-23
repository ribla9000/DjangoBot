from django.contrib import admin
from .models import *

@admin.register(StatusOrder)
class StatusOrderAdmin(admin.ModelAdmin):
	list_display = ('id', 'status_name', 'is_active')

@admin.register(OrdersFromBot)
class OrdersFromBotAdmin(admin.ModelAdmin):
	list_display = ('id', 'user_name', 'order_price', 'services_name', 'is_active')

