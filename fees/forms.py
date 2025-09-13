from django import forms
from django.contrib.auth.models import User
from decimal import Decimal
from students.models import StudentProfile, GradeLevel
from .models import FeeStructure, Invoice, InvoiceLine, Payment, Receipt


class FeeStructureForm(forms.ModelForm):
    class Meta:
        model = FeeStructure
        fields = ["grade_level", "fee_type", "term", "amount", "active"]
        widgets = {
            "grade_level": forms.Select(attrs={"class": "form-control"}),
            "fee_type": forms.Select(attrs={"class": "form-control"}),
            "term": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "e.g., Term 1 / 2025"}
            ),
            "amount": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
            "active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class InvoiceForm(forms.ModelForm):
    student_search = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Search student by name or admission number",
                "id": "student-search",
            }
        ),
        help_text="Type to search for a student",
    )

    class Meta:
        model = Invoice
        fields = ["student", "term", "due_date", "status"]
        widgets = {
            "student": forms.Select(attrs={"class": "form-control"}),
            "term": forms.TextInput(attrs={"class": "form-control"}),
            "due_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "status": forms.Select(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["student"].queryset = StudentProfile.objects.select_related(
            "user"
        ).all()


class InvoiceLineForm(forms.ModelForm):
    class Meta:
        model = InvoiceLine
        fields = ["description", "amount"]
        widgets = {
            "description": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Fee description"}
            ),
            "amount": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
        }


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ["amount", "method", "reference", "date"]
        widgets = {
            "amount": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
            "method": forms.Select(attrs={"class": "form-control"}),
            "reference": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Reference number"}
            ),
            "date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        invoice = kwargs.pop("invoice", None)
        super().__init__(*args, **kwargs)

        if invoice:
            # Calculate remaining balance
            paid_amount = sum(p.amount for p in invoice.payments.all())
            remaining = invoice.total_amount - paid_amount
            self.fields["amount"].widget.attrs["max"] = str(remaining)
            self.fields["amount"].help_text = f"Outstanding balance: {remaining}"


class BulkInvoiceForm(forms.Form):
    grade_level = forms.ModelChoiceField(
        queryset=GradeLevel.objects.all(),
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    term = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Term 1 / 2025"}
        )
    )
    due_date = forms.DateField(
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        required=False,
    )
    fee_structures = forms.ModelMultipleChoiceField(
        queryset=FeeStructure.objects.none(),
        widget=forms.CheckboxSelectMultiple(attrs={"class": "form-check-input"}),
        help_text="Select the fees to include in bulk invoices",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["fee_structures"].queryset = FeeStructure.objects.filter(
            active=True
        )


class PaymentReportForm(forms.Form):
    date_from = forms.DateField(
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        required=False,
    )
    date_to = forms.DateField(
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        required=False,
    )
    payment_method = forms.ChoiceField(
        choices=[("", "All Methods")] + list(Payment.METHOD_CHOICES),
        widget=forms.Select(attrs={"class": "form-control"}),
        required=False,
    )
    student = forms.ModelChoiceField(
        queryset=StudentProfile.objects.select_related("user").all(),
        widget=forms.Select(attrs={"class": "form-control"}),
        required=False,
        empty_label="All Students",
    )
    status = forms.ChoiceField(
        choices=[("", "All Status")] + list(Invoice.STATUS_CHOICES),
        widget=forms.Select(attrs={"class": "form-control"}),
        required=False,
    )
