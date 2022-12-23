from django.contrib import admin
from .models import *
from .forms import *
from commands.models import *


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
	list_display = ('id', 'external_id', 'name')
	form = ProfileForm
	verbose_name='Profile'
	verbose_name_plural='Profiles'

@admin.register(MessagePanel)
class MessageAdmin(admin.ModelAdmin):
	list_display = ('id', 'profile','text', 'created')

	# def get_queryset(self,request):
	# 	return

@admin.register(BotsPanel)
class BotsPanelAdmin(admin.ModelAdmin):
	list_display = ('id','bot_id','bot_nickname', 'bot_name')
	form = BotsForm
	verbose_name='Bot'
	verbose_name_plural='Bots'

# @admin.register(HandMadeMessage)
# class HandMadeMessageAdmin(admin.ModelAdmin):
# 	list_display = ('id', 'message')