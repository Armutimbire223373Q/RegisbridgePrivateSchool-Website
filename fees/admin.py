from django.contrib import admin
from .models import FeeStructure, Invoice, InvoiceLine, Payment, Receipt


class InvoiceLineInline(admin.TabularInline):
    model = InvoiceLine
    extra = 0


@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ("grade_level", "fee_type", "term", "amount", "active")
    list_filter = ("fee_type", "term", "active")


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "student",
        "term",
        "status",
        "total_amount",
        "issue_date",
        "due_date",
    )
    list_filter = ("status", "term")
    inlines = [InvoiceLineInline]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "invoice", "amount", "method", "date")
    list_filter = ("method", "date")


@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = ("number", "payment", "created_at")


# Register your models here.
