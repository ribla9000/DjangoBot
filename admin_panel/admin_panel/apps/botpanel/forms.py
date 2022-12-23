from django import forms
from .models import *

class ProfileForm(forms.ModelForm):

	class Meta:
		model = Profile
		fields = (
			'external_id',
			'name',
		)
		widgets = {
			'name': forms.TextInput,
		}

class BotsForm(forms.ModelForm):

	class Meta:
		model = BotsPanel
		fields = (
			'bot_id',
			'bot_name',
			'bot_nickname',
			'bot_token',
		)
		widgets = {
			'bot_name': forms.TextInput,
			'bot_nickname': forms.TextInput,
			'bot_token': forms.TextInput,
		}