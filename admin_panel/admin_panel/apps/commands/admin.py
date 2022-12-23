from django.contrib import admin
from commands.models import *
from .forms import *
from django_object_actions import DjangoObjectActions
from django.http import HttpResponseRedirect

# @admin.register(CommandsForButtons)
# class CommandsForButtonsAdmin(admin.ModelAdmin):
# 	list_display = ('id', 'command_name', 'command_text',)
# 	inlines = [ButtonsAdminInline]
# 	form = CommandsForButtonsForm

@admin.register(AsksForFAQ)
class AsksForFAQAdmin(admin.ModelAdmin):
	list_display = ('id', 'faq_name')

@admin.register(ServicesList)
class ServicesCalculatorAdmin(admin.ModelAdmin):
	list_display = ('id', 'service_name')

@admin.register(AdvertisementsCalculator)
class AdvertisementsCalculatorAdmin(admin.ModelAdmin):
	list_display = ('id', 'advertisement_name')

@admin.register(CompanyPosts)
class CompanyPostAdmin(admin.ModelAdmin):
	list_display = ('id', 'person_post')

@admin.register(StaffinCompany)
class StaffinCompanyAdmin(admin.ModelAdmin):
	list_display = ('id', 'person_name')

@admin.register(ClientsReviews)
class ClientsReviewsAdmin(admin.ModelAdmin):
	list_display = ('id','review_user','review_text')
