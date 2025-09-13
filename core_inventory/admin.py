from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered
from .models import InventoryItem


class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "quantity")
    list_filter = ("category",)
    search_fields = ("name",)


try:
    admin.site.register(InventoryItem, InventoryItemAdmin)
except AlreadyRegistered:
    pass
