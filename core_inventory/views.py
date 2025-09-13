from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from .models import InventoryCategory, InventoryItem, StockMovement


@login_required
def inventory_dashboard(request):
    """Main inventory dashboard with overview statistics"""
    if request.user.role not in ["ADMIN", "BOARDING_STAFF"]:
        messages.error(request, "Access denied. Admin or Boarding Staff privileges required.")
        return redirect("dashboard")

    # Get inventory statistics
    total_items = InventoryItem.objects.count()
    low_stock_items = InventoryItem.objects.filter(quantity__lt=10).count()
    total_categories = InventoryCategory.objects.count()
    
    # Recent movements
    recent_movements = StockMovement.objects.select_related('item').order_by('-created_at')[:10]
    
    # Low stock items
    low_stock = InventoryItem.objects.filter(quantity__lt=10).select_related('category')
    
    context = {
        'total_items': total_items,
        'low_stock_items': low_stock_items,
        'total_categories': total_categories,
        'recent_movements': recent_movements,
        'low_stock': low_stock,
    }
    
    return render(request, 'inventory/dashboard.html', context)


@login_required
def inventory_list(request):
    """List all inventory items with search and filtering"""
    if request.user.role not in ["ADMIN", "BOARDING_STAFF"]:
        messages.error(request, "Access denied. Admin or Boarding Staff privileges required.")
        return redirect("dashboard")

    items = InventoryItem.objects.select_related('category').all()
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        items = items.filter(
            Q(name__icontains=search_query) |
            Q(sku__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )
    
    # Category filter
    category_filter = request.GET.get('category', '')
    if category_filter:
        items = items.filter(category_id=category_filter)
    
    # Stock status filter
    stock_filter = request.GET.get('stock', '')
    if stock_filter == 'low':
        items = items.filter(quantity__lt=10)
    elif stock_filter == 'out':
        items = items.filter(quantity=0)
    
    # Pagination
    paginator = Paginator(items, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = InventoryCategory.objects.all()
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'search_query': search_query,
        'category_filter': category_filter,
        'stock_filter': stock_filter,
    }
    
    return render(request, 'inventory/list.html', context)


@login_required
def inventory_detail(request, item_id):
    """Detailed view of an inventory item with movement history"""
    if request.user.role not in ["ADMIN", "BOARDING_STAFF"]:
        messages.error(request, "Access denied. Admin or Boarding Staff privileges required.")
        return redirect("dashboard")

    item = get_object_or_404(InventoryItem, id=item_id)
    movements = StockMovement.objects.filter(item=item).order_by('-created_at')
    
    # Paginate movements
    paginator = Paginator(movements, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'item': item,
        'page_obj': page_obj,
    }
    
    return render(request, 'inventory/detail.html', context)


@login_required
@require_http_methods(["POST"])
def add_stock_movement(request, item_id):
    """Add a new stock movement (in or out)"""
    if request.user.role not in ["ADMIN", "BOARDING_STAFF"]:
        return JsonResponse({'error': 'Access denied'}, status=403)

    item = get_object_or_404(InventoryItem, id=item_id)
    
    try:
        movement_type = request.POST.get('type')
        quantity = int(request.POST.get('quantity', 0))
        note = request.POST.get('note', '')
        
        if movement_type not in ['IN', 'OUT']:
            return JsonResponse({'error': 'Invalid movement type'}, status=400)
        
        if quantity <= 0:
            return JsonResponse({'error': 'Quantity must be positive'}, status=400)
        
        # Check if we have enough stock for OUT movement
        if movement_type == 'OUT' and item.quantity < quantity:
            return JsonResponse({'error': 'Insufficient stock'}, status=400)
        
        # Create movement record
        movement = StockMovement.objects.create(
            item=item,
            kind=movement_type,
            quantity=quantity,
            note=note
        )
        
        # Update item quantity
        if movement_type == 'IN':
            item.quantity += quantity
        else:
            item.quantity -= quantity
        item.save()
        
        return JsonResponse({
            'success': True,
            'new_quantity': item.quantity,
            'movement_id': movement.id
        })
        
    except ValueError:
        return JsonResponse({'error': 'Invalid quantity'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def categories_list(request):
    """List and manage inventory categories"""
    if request.user.role not in ["ADMIN", "BOARDING_STAFF"]:
        messages.error(request, "Access denied. Admin or Boarding Staff privileges required.")
        return redirect("dashboard")

    categories = InventoryCategory.objects.annotate(
        item_count=Sum('items__id')
    ).order_by('name')
    
    context = {
        'categories': categories,
    }
    
    return render(request, 'inventory/categories.html', context)