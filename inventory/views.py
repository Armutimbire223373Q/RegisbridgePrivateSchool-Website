from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db.models import Q, Sum, Count
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import timedelta

from students.models import StudentProfile
from .models import (
    InventoryItem,
    InventoryCategory,
    StockMovement,
    LibraryCheckout,
    ProcurementRequest,
    ProcurementRequestItem,
    Supplier,
    InventoryAudit,
    InventoryAuditItem,
)


@login_required
def inventory_dashboard(request):
    """Inventory dashboard with key metrics"""
    # Key metrics
    total_items = InventoryItem.objects.filter(is_active=True).count()
    low_stock_items = InventoryItem.objects.filter(
        quantity__lte=models.F("min_stock_level"), is_active=True
    ).count()
    out_of_stock_items = InventoryItem.objects.filter(
        quantity=0, is_active=True
    ).count()

    # Library metrics
    active_checkouts = LibraryCheckout.objects.filter(status="ACTIVE").count()
    overdue_items = LibraryCheckout.objects.filter(
        status="ACTIVE", due_date__lt=timezone.now().date()
    ).count()

    # Recent activity
    recent_movements = StockMovement.objects.select_related("item", "created_by")[:10]
    recent_checkouts = LibraryCheckout.objects.select_related(
        "item", "borrower__user"
    ).order_by("-checkout_date")[:10]

    # Procurement requests
    pending_requests = ProcurementRequest.objects.filter(
        status__in=["DRAFT", "SUBMITTED"]
    ).count()

    context = {
        "total_items": total_items,
        "low_stock_items": low_stock_items,
        "out_of_stock_items": out_of_stock_items,
        "active_checkouts": active_checkouts,
        "overdue_items": overdue_items,
        "recent_movements": recent_movements,
        "recent_checkouts": recent_checkouts,
        "pending_requests": pending_requests,
    }

    return render(request, "inventory/dashboard.html", context)


@login_required
def item_list(request):
    """List inventory items with filtering"""
    items = InventoryItem.objects.select_related("category", "supplier").filter(
        is_active=True
    )

    # Filtering
    category_id = request.GET.get("category")
    search = request.GET.get("search")
    stock_status = request.GET.get("stock_status")

    if category_id:
        items = items.filter(category_id=category_id)

    if search:
        items = items.filter(
            Q(name__icontains=search)
            | Q(sku__icontains=search)
            | Q(description__icontains=search)
        )

    if stock_status == "low":
        items = items.filter(quantity__lte=models.F("min_stock_level"))
    elif stock_status == "out":
        items = items.filter(quantity=0)

    # Pagination
    paginator = Paginator(items, 25)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    categories = InventoryCategory.objects.all()

    return render(
        request,
        "inventory/item_list.html",
        {
            "page_obj": page_obj,
            "categories": categories,
            "current_filters": request.GET,
        },
    )


@login_required
def item_detail(request, item_id):
    """Item detail view"""
    item = get_object_or_404(InventoryItem, id=item_id)

    # Recent movements
    movements = item.movements.select_related("created_by")[:20]

    # Library checkouts if applicable
    checkouts = None
    if item.category.is_library:
        checkouts = item.checkouts.select_related("borrower__user")[:20]

    return render(
        request,
        "inventory/item_detail.html",
        {"item": item, "movements": movements, "checkouts": checkouts},
    )


@login_required
@permission_required("inventory.add_stockmovement")
def stock_movement(request, item_id):
    """Create stock movement"""
    item = get_object_or_404(InventoryItem, id=item_id)

    if request.method == "POST":
        movement_type = request.POST.get("movement_type")
        quantity = int(request.POST.get("quantity", 0))
        reason = request.POST.get("reason", "")
        notes = request.POST.get("notes", "")
        unit_cost = request.POST.get("unit_cost", 0)
        reference_number = request.POST.get("reference_number", "")

        # Validate quantity for OUT movements
        if movement_type in ["OUT", "DAMAGED"] and quantity > item.quantity:
            messages.error(
                request,
                f"Cannot remove {quantity} items. Only {item.quantity} available.",
            )
            return redirect("inventory_item_detail", item_id=item.id)

        # Create movement
        movement = StockMovement.objects.create(
            item=item,
            movement_type=movement_type,
            quantity=quantity if movement_type == "IN" else -quantity,
            reason=reason,
            notes=notes,
            unit_cost=float(unit_cost) if unit_cost else 0,
            reference_number=reference_number,
            created_by=request.user,
        )

        messages.success(request, f"Stock movement recorded for {item.name}")
        return redirect("inventory_item_detail", item_id=item.id)

    return render(request, "inventory/stock_movement.html", {"item": item})


@login_required
def library_dashboard(request):
    """Library management dashboard"""
    # Metrics
    total_books = InventoryItem.objects.filter(category__is_library=True).count()
    checked_out = LibraryCheckout.objects.filter(status="ACTIVE").count()
    overdue = LibraryCheckout.objects.filter(
        status="ACTIVE", due_date__lt=timezone.now().date()
    ).count()

    # Recent activity
    recent_checkouts = LibraryCheckout.objects.select_related(
        "item", "borrower__user"
    ).order_by("-checkout_date")[:10]

    due_soon = LibraryCheckout.objects.filter(
        status="ACTIVE", due_date__lte=timezone.now().date() + timedelta(days=3)
    ).select_related("item", "borrower__user")[:10]

    return render(
        request,
        "inventory/library_dashboard.html",
        {
            "total_books": total_books,
            "checked_out": checked_out,
            "overdue": overdue,
            "recent_checkouts": recent_checkouts,
            "due_soon": due_soon,
        },
    )


@login_required
def checkout_book(request):
    """Checkout a book to a student"""
    if request.method == "POST":
        item_id = request.POST.get("item_id")
        borrower_id = request.POST.get("borrower_id")
        due_date = request.POST.get("due_date")
        notes = request.POST.get("notes", "")

        item = get_object_or_404(InventoryItem, id=item_id, category__is_library=True)
        borrower = get_object_or_404(StudentProfile, id=borrower_id)

        # Check availability
        if item.available_quantity <= 0:
            messages.error(request, f"{item.name} is not available for checkout")
            return redirect("inventory_library_dashboard")

        # Create checkout
        checkout = LibraryCheckout.objects.create(
            item=item,
            borrower=borrower,
            due_date=due_date,
            checkout_notes=notes,
            checked_out_by=request.user,
        )

        # Create stock movement
        StockMovement.objects.create(
            item=item,
            movement_type=StockMovement.OUT,
            quantity=1,
            reason="Library book checkout",
            notes=f"Checked out to {borrower.user.get_full_name()}",
            created_by=request.user,
        )

        messages.success(
            request, f"Book checked out to {borrower.user.get_full_name()}"
        )
        return redirect("inventory_library_dashboard")

    # Get available books and students
    books = InventoryItem.objects.filter(category__is_library=True, is_active=True)
    students = StudentProfile.objects.select_related("user").filter(
        user__is_active=True
    )

    return render(
        request, "inventory/checkout_book.html", {"books": books, "students": students}
    )


@login_required
def return_book(request, checkout_id):
    """Return a checked out book"""
    checkout = get_object_or_404(LibraryCheckout, id=checkout_id, status="ACTIVE")

    if request.method == "POST":
        return_notes = request.POST.get("return_notes", "")
        condition = request.POST.get("condition", "good")

        # Calculate fine if overdue
        if checkout.is_overdue:
            daily_rate = float(request.POST.get("daily_fine_rate", "1.00"))
            checkout.fine_amount = checkout.calculate_fine(daily_rate)

        # Return the book
        checkout.return_item(returned_to=request.user, return_notes=return_notes)

        if condition == "damaged":
            checkout.status = "DAMAGED"
            checkout.save()

        messages.success(
            request, f"Book returned by {checkout.borrower.user.get_full_name()}"
        )
        return redirect("inventory_library_dashboard")

    return render(request, "inventory/return_book.html", {"checkout": checkout})


@login_required
def checkout_list(request):
    """List library checkouts"""
    checkouts = LibraryCheckout.objects.select_related("item", "borrower__user")

    # Filtering
    status = request.GET.get("status")
    if status:
        checkouts = checkouts.filter(status=status)

    # Pagination
    paginator = Paginator(checkouts, 25)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "inventory/checkout_list.html",
        {"page_obj": page_obj, "status_choices": LibraryCheckout.STATUS_CHOICES},
    )


@login_required
def procurement_dashboard(request):
    """Procurement requests dashboard"""
    requests = ProcurementRequest.objects.select_related("requested_by")

    # Summary statistics
    total_requests = requests.count()
    pending = requests.filter(status__in=["DRAFT", "SUBMITTED"]).count()
    approved = requests.filter(status="APPROVED").count()

    # Recent requests
    recent_requests = requests.order_by("-requested_date")[:10]

    return render(
        request,
        "inventory/procurement_dashboard.html",
        {
            "total_requests": total_requests,
            "pending": pending,
            "approved": approved,
            "recent_requests": recent_requests,
        },
    )


@login_required
def create_procurement_request(request):
    """Create new procurement request"""
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        justification = request.POST.get("justification")
        priority = request.POST.get("priority", "MEDIUM")
        required_date = request.POST.get("required_date")

        # Create request
        proc_request = ProcurementRequest.objects.create(
            title=title,
            description=description,
            justification=justification,
            priority=priority,
            required_date=required_date,
            requested_by=request.user,
        )

        # Handle items
        item_descriptions = request.POST.getlist("item_descriptions")
        item_quantities = request.POST.getlist("item_quantities")
        item_prices = request.POST.getlist("item_prices")

        total_estimated = 0
        for desc, qty, price in zip(item_descriptions, item_quantities, item_prices):
            if desc and qty and price:
                qty = int(qty)
                price = float(price)

                ProcurementRequestItem.objects.create(
                    request=proc_request,
                    description=desc,
                    quantity_requested=qty,
                    estimated_unit_price=price,
                )
                total_estimated += qty * price

        proc_request.estimated_total = total_estimated
        proc_request.save()

        messages.success(
            request, f"Procurement request {proc_request.request_number} created"
        )
        return redirect("inventory_procurement_dashboard")

    return render(request, "inventory/create_procurement_request.html")


@login_required
def search_items(request):
    """AJAX endpoint to search inventory items"""
    query = request.GET.get("q", "")
    category_id = request.GET.get("category")

    items = InventoryItem.objects.filter(is_active=True)

    if query:
        items = items.filter(Q(name__icontains=query) | Q(sku__icontains=query))

    if category_id:
        items = items.filter(category_id=category_id)

    items = items[:10]

    results = [
        {
            "id": item.id,
            "text": f"{item.name} ({item.sku}) - Qty: {item.available_quantity}",
            "available": item.available_quantity,
        }
        for item in items
    ]

    return JsonResponse({"results": results})


@login_required
def low_stock_report(request):
    """Report of low stock items"""
    low_stock_items = InventoryItem.objects.filter(
        quantity__lte=models.F("min_stock_level"), is_active=True
    ).select_related("category", "supplier")

    return render(
        request, "inventory/low_stock_report.html", {"low_stock_items": low_stock_items}
    )


@login_required
def overdue_books_report(request):
    """Report of overdue library books"""
    overdue_checkouts = (
        LibraryCheckout.objects.filter(
            status="ACTIVE", due_date__lt=timezone.now().date()
        )
        .select_related("item", "borrower__user")
        .order_by("due_date")
    )

    return render(
        request,
        "inventory/overdue_books_report.html",
        {"overdue_checkouts": overdue_checkouts},
    )
