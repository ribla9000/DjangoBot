from django.db import models
from django.conf import settings
from commands.models import * 

class Profile(models.Model):
	
	external_id = models.PositiveIntegerField(
		verbose_name='User ID',
		unique=True,
	)
	
	name = models.TextField(
		verbose_name='User Name'
	)

	def __str__(self):
		return f'#{self.external_id} @{self.name}'

	class Meta:
		verbose_name='Profile'
		verbose_name_plural='Profiles'



class BotsPanel(models.Model):
	
	bot_id = models.PositiveIntegerField(
		verbose_name='BOT ID',
		unique=True,
	)
	bot_name = models.TextField(
		verbose_name='Bot Name'
	)
	bot_nickname = models.TextField(
		verbose_name='@telegram'
	)
	bot_token = models.TextField(
		verbose_name='Token',
	)
	
	def __str__(self):
		return f'#{self.bot_id} @{self.bot_nickname} {self.bot_name} {self.bot_token}'

	class Meta:

		verbose_name='Bot'
		verbose_name_plural='Bots'

class MessagePanel(models.Model):
	
	profile = models.ForeignKey(
		to='botpanel.Profile',
		verbose_name='Profile',
		on_delete=models.PROTECT,
	)
	text = models.TextField(
		verbose_name='Text',
	)
	created= models.DateTimeField(
		verbose_name='Get Time',
		auto_now_add=True,
	)

	def __str__(self):
		return f'Message {self.text} from @{self.profile} at {self.created}'
	
	class Meta:
		verbose_name='Message'
		verbose_name_plural='Messages'