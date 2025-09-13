from django.urls import path
from . import views

app_name = "inventory"

urlpatterns = [
    path("", views.inventory_dashboard, name="dashboard"),
    path("items/", views.inventory_list, name="list"),
    path("items/<int:item_id>/", views.inventory_detail, name="detail"),
    path("items/<int:item_id>/movement/", views.add_stock_movement, name="add_movement"),
    path("categories/", views.categories_list, name="categories"),
]
