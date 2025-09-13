from django.contrib import admin
from .models import (
    InventoryCategory,
    Supplier,
    InventoryItem,
    StockMovement,
    LibraryCheckout,
    ProcurementRequest,
    ProcurementRequestItem,
    InventoryAudit,
    InventoryAuditItem,
)


@admin.register(InventoryCategory)
class InventoryCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "is_library")
    list_filter = ("is_library",)
    search_fields = ("name",)


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("name", "contact_person", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "contact_person")


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ("name", "sku", "category", "quantity", "unit", "is_active")
    list_filter = ("category", "is_active")
    search_fields = ("name", "sku", "barcode")


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ("item", "movement_type", "quantity", "created_at")
    list_filter = ("movement_type", "created_at")


@admin.register(LibraryCheckout)
class LibraryCheckoutAdmin(admin.ModelAdmin):
    list_display = ("item", "borrower", "status", "checkout_date", "due_date")
    list_filter = ("status", "checkout_date", "due_date")


class ProcurementRequestItemInline(admin.TabularInline):
    model = ProcurementRequestItem
    extra = 0


@admin.register(ProcurementRequest)
class ProcurementRequestAdmin(admin.ModelAdmin):
    list_display = ("request_number", "title", "status", "priority", "requested_date")
    list_filter = ("status", "priority", "requested_date")
    inlines = [ProcurementRequestItemInline]


class InventoryAuditItemInline(admin.TabularInline):
    model = InventoryAuditItem
    extra = 0


@admin.register(InventoryAudit)
class InventoryAuditAdmin(admin.ModelAdmin):
    list_display = ("audit_number", "title", "status", "planned_date")
    list_filter = ("status", "planned_date")
    inlines = [InventoryAuditItemInline]
