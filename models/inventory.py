"""
Inventory and asset management models
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, Date, ForeignKey, Enum, Float, Numeric
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum

class ItemCategory(str, enum.Enum):
    BOOKS = "BOOKS"
    EQUIPMENT = "EQUIPMENT"
    UNIFORMS = "UNIFORMS"
    FURNITURE = "FURNITURE"
    ELECTRONICS = "ELECTRONICS"
    LAB_SUPPLIES = "LAB_SUPPLIES"
    SPORTS = "SPORTS"
    STATIONERY = "STATIONERY"
    OTHER = "OTHER"

class ItemStatus(str, enum.Enum):
    AVAILABLE = "AVAILABLE"
    ISSUED = "ISSUED"
    DAMAGED = "DAMAGED"
    LOST = "LOST"
    REPAIR = "REPAIR"
    RETIRED = "RETIRED"

class TransactionType(str, enum.Enum):
    IN = "IN"
    OUT = "OUT"
    TRANSFER = "TRANSFER"
    ADJUSTMENT = "ADJUSTMENT"

class InventoryItem(BaseModel):
    """Inventory item model"""
    __tablename__ = "inventory_items"

    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(Enum(ItemCategory), nullable=False)
    item_code = Column(String(50), unique=True, nullable=False)
    barcode = Column(String(100), nullable=True)
    unit_price = Column(Numeric(10, 2), nullable=True)
    current_stock = Column(Integer, default=0)
    minimum_stock = Column(Integer, default=0)
    maximum_stock = Column(Integer, nullable=True)
    unit_of_measure = Column(String(20), default="pieces")
    supplier = Column(String(200), nullable=True)
    location = Column(String(200), nullable=True)
    status = Column(Enum(ItemStatus), default=ItemStatus.AVAILABLE)
    is_active = Column(Boolean, default=True)

    # Relationships
    transactions = relationship("InventoryTransaction", back_populates="item")
    issues = relationship("ItemIssue", back_populates="item")

    def __str__(self):
        return f"{self.name} ({self.item_code})"

class InventoryTransaction(BaseModel):
    """Inventory transaction model"""
    __tablename__ = "inventory_transactions"

    item_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=False)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=True)
    total_amount = Column(Numeric(10, 2), nullable=True)
    reference_number = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    processed_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    transaction_date = Column(Date, nullable=False)

    # Relationships
    item = relationship("InventoryItem", back_populates="transactions")
    processed_by = relationship("User")

    def __str__(self):
        return f"{self.transaction_type} - {self.item.name} - {self.quantity}"

class ItemIssue(BaseModel):
    """Item issue/return model"""
    __tablename__ = "item_issues"

    item_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=False)
    issued_to_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    issued_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    issue_date = Column(Date, nullable=False)
    expected_return_date = Column(Date, nullable=True)
    actual_return_date = Column(Date, nullable=True)
    status = Column(String(20), default="ISSUED")  # ISSUED, RETURNED, OVERDUE, LOST
    notes = Column(Text, nullable=True)
    condition_on_issue = Column(String(100), nullable=True)
    condition_on_return = Column(String(100), nullable=True)

    # Relationships
    item = relationship("InventoryItem", back_populates="issues")
    issued_to = relationship("User", foreign_keys=[issued_to_id])
    issued_by = relationship("User", foreign_keys=[issued_by_id])

    def __str__(self):
        return f"{self.item.name} issued to {self.issued_to.username}"

class Supplier(BaseModel):
    """Supplier model"""
    __tablename__ = "suppliers"

    name = Column(String(200), nullable=False)
    contact_person = Column(String(100), nullable=True)
    email = Column(String(200), nullable=True)
    phone = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    country = Column(String(100), default="Kenya")
    website = Column(String(200), nullable=True)
    is_active = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)

    # Relationships
    purchases = relationship("PurchaseOrder", back_populates="supplier")

    def __str__(self):
        return self.name

class PurchaseOrder(BaseModel):
    """Purchase order model"""
    __tablename__ = "purchase_orders"

    order_number = Column(String(50), unique=True, nullable=False)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    order_date = Column(Date, nullable=False)
    expected_delivery_date = Column(Date, nullable=True)
    actual_delivery_date = Column(Date, nullable=True)
    total_amount = Column(Numeric(10, 2), nullable=False)
    status = Column(String(20), default="PENDING")  # PENDING, APPROVED, ORDERED, DELIVERED, CANCELLED
    notes = Column(Text, nullable=True)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    approved_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    supplier = relationship("Supplier", back_populates="purchases")
    created_by = relationship("User", foreign_keys=[created_by_id])
    approved_by = relationship("User", foreign_keys=[approved_by_id])
    items = relationship("PurchaseOrderItem", back_populates="purchase_order")

    def __str__(self):
        return f"PO {self.order_number} - {self.supplier.name}"

class PurchaseOrderItem(BaseModel):
    """Purchase order item model"""
    __tablename__ = "purchase_order_items"

    purchase_order_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False)
    received_quantity = Column(Integer, default=0)
    notes = Column(Text, nullable=True)

    # Relationships
    purchase_order = relationship("PurchaseOrder", back_populates="items")
    item = relationship("InventoryItem")

    def __str__(self):
        return f"{self.item.name} - {self.quantity} units"
