from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from fees.models import Invoice


class PaymentGateway(models.Model):
    """Payment gateway configurations"""

    GATEWAY_CHOICES = [
        ("STRIPE", "Stripe"),
        ("PAYNOW", "PayNow"),
        ("MPESA", "M-Pesa"),
        ("PAYPAL", "PayPal"),
        ("CUSTOM", "Custom Gateway"),
    ]

    name = models.CharField(max_length=100, unique=True)
    gateway_type = models.CharField(max_length=20, choices=GATEWAY_CHOICES)
    is_active = models.BooleanField(default=True)

    # Configuration
    api_key = models.CharField(max_length=255, blank=True)
    secret_key = models.CharField(max_length=255, blank=True)
    webhook_secret = models.CharField(max_length=255, blank=True)

    # Settings
    test_mode = models.BooleanField(
        default=True, help_text="Use test/sandbox environment"
    )
    currency = models.CharField(max_length=3, default="KES")
    supported_payment_methods = models.JSONField(
        default=list, help_text="List of supported payment methods"
    )

    # Fees and limits
    transaction_fee_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=0
    )
    transaction_fee_fixed = models.DecimalField(
        max_digits=10, decimal_places=2, default=0
    )
    min_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_amount = models.DecimalField(max_digits=10, decimal_places=2, default=999999.99)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Payment Gateway"
        verbose_name_plural = "Payment Gateways"

    def __str__(self):
        return f"{self.name} ({self.get_gateway_type_display()})"

    def calculate_fees(self, amount):
        """Calculate transaction fees for a given amount"""
        percentage_fee = (amount * self.transaction_fee_percentage) / 100
        total_fees = percentage_fee + self.transaction_fee_fixed
        return total_fees

    def is_amount_valid(self, amount):
        """Check if amount is within gateway limits"""
        return self.min_amount <= amount <= self.max_amount


class PaymentTransaction(models.Model):
    """Payment transactions"""

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("PROCESSING", "Processing"),
        ("COMPLETED", "Completed"),
        ("FAILED", "Failed"),
        ("CANCELLED", "Cancelled"),
        ("REFUNDED", "Refunded"),
        ("PARTIALLY_REFUNDED", "Partially Refunded"),
    ]

    PAYMENT_METHOD_CHOICES = [
        ("CARD", "Credit/Debit Card"),
        ("BANK_TRANSFER", "Bank Transfer"),
        ("MOBILE_MONEY", "Mobile Money"),
        ("CASH", "Cash"),
        ("CHECK", "Check"),
        ("OTHER", "Other"),
    ]

    # Transaction details
    transaction_id = models.CharField(max_length=100, unique=True)
    invoice = models.ForeignKey(
        Invoice, on_delete=models.CASCADE, related_name="payment_transactions"
    )
    gateway = models.ForeignKey(
        PaymentGateway, on_delete=models.CASCADE, related_name="transactions"
    )

    # Amount and fees
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    gateway_fees = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2)

    # Payment method
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    payment_reference = models.CharField(max_length=100, blank=True)

    # Status and timing
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    initiated_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Gateway response
    gateway_response = models.JSONField(
        default=dict, help_text="Response from payment gateway"
    )
    error_message = models.TextField(blank=True)

    # Metadata
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Payment Transaction"
        verbose_name_plural = "Payment Transactions"

    def __str__(self):
        return f"{self.transaction_id} - {self.amount} {self.gateway.currency}"

    def save(self, *args, **kwargs):
        # Calculate net amount
        if self.amount and self.gateway_fees:
            self.net_amount = self.amount - self.gateway_fees
        else:
            self.net_amount = self.amount

        super().save(*args, **kwargs)

    @property
    def is_successful(self):
        """Check if transaction was successful"""
        return self.status == "COMPLETED"

    @property
    def processing_time(self):
        """Calculate processing time"""
        if self.initiated_at and self.completed_at:
            return (self.completed_at - self.initiated_at).total_seconds()
        return None

    def process_payment(self):
        """Process the payment through the gateway"""
        try:
            # Set status to processing
            self.status = "PROCESSING"
            self.processed_at = timezone.now()
            self.save()

            # Here you would integrate with the actual payment gateway
            # For now, we'll simulate a successful payment
            self.status = "COMPLETED"
            self.completed_at = timezone.now()
            self.save()

            return True
        except Exception as e:
            self.status = "FAILED"
            self.error_message = str(e)
            self.save()
            return False

    def refund_payment(self, amount=None, reason=""):
        """Refund the payment"""
        if amount is None:
            amount = self.amount

        if amount > self.amount:
            raise ValueError("Refund amount cannot exceed original amount")

        # Create refund transaction
        refund = PaymentTransaction.objects.create(
            transaction_id=f"REFUND_{self.transaction_id}",
            invoice=self.invoice,
            gateway=self.gateway,
            amount=-amount,  # Negative amount for refund
            payment_method=self.payment_method,
            status="REFUNDED",
            created_by=self.created_by,
        )

        # Update original transaction status
        if amount == self.amount:
            self.status = "REFUNDED"
        else:
            self.status = "PARTIALLY_REFUNDED"
        self.save()

        return refund


class PaymentMethod(models.Model):
    """Available payment methods"""

    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)

    # Settings
    is_active = models.BooleanField(default=True)
    requires_verification = models.BooleanField(default=False)
    min_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_amount = models.DecimalField(max_digits=10, decimal_places=2, default=999999.99)

    # Fees
    transaction_fee_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=0
    )
    transaction_fee_fixed = models.DecimalField(
        max_digits=10, decimal_places=2, default=0
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Payment Method"
        verbose_name_plural = "Payment Methods"

    def __str__(self):
        return self.name

    def calculate_fees(self, amount):
        """Calculate fees for this payment method"""
        percentage_fee = (amount * self.transaction_fee_percentage) / 100
        total_fees = percentage_fee + self.transaction_fee_fixed
        return total_fees


class PaymentWebhook(models.Model):
    """Webhook events from payment gateways"""

    gateway = models.ForeignKey(
        PaymentGateway, on_delete=models.CASCADE, related_name="webhooks"
    )

    # Webhook details
    event_id = models.CharField(max_length=100, unique=True)
    event_type = models.CharField(max_length=100)
    event_data = models.JSONField(default=dict)

    # Processing
    processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(null=True, blank=True)
    processing_notes = models.TextField(blank=True)

    # Metadata
    received_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-received_at"]
        verbose_name = "Payment Webhook"
        verbose_name_plural = "Payment Webhooks"

    def __str__(self):
        return f"{self.gateway.name} - {self.event_type} ({self.event_id})"

    def mark_processed(self, notes=""):
        """Mark webhook as processed"""
        self.processed = True
        self.processed_at = timezone.now()
        self.processing_notes = notes
        self.save()
