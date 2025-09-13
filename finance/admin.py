from django.contrib import admin
from .models import FeeStructure, Invoice, Payment


@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ("name", "amount", "is_boarding")
    list_filter = ("is_boarding",)


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("student", "term", "year", "total_amount", "is_paid")
    list_filter = ("term", "year", "is_paid")
    inlines = [PaymentInline]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("invoice", "amount", "method", "paid_at", "received_by")
    list_filter = ("method", "paid_at")
