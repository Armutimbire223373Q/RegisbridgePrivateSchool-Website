from decimal import Decimal
from datetime import datetime, timedelta
import json
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Sum, Q, Count
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.utils import timezone

from students.models import StudentProfile, GradeLevel
from .models import FeeStructure, Invoice, InvoiceLine, Payment, Receipt
from .forms import (
    FeeStructureForm,
    InvoiceForm,
    InvoiceLineForm,
    PaymentForm,
    BulkInvoiceForm,
    PaymentReportForm,
)
from reports.utils import generate_fee_invoice_pdf


@login_required
def invoices_list(request):
    """List invoices with filtering and pagination"""
    invoices = Invoice.objects.select_related("student__user").prefetch_related(
        "lines", "payments"
    )

    # Filtering
    status = request.GET.get("status")
    student_id = request.GET.get("student")
    term = request.GET.get("term")

    if status:
        invoices = invoices.filter(status=status)
    if student_id:
        invoices = invoices.filter(student_id=student_id)
    if term:
        invoices = invoices.filter(term__icontains=term)

    invoices = invoices.order_by("-issue_date")

    # Pagination
    paginator = Paginator(invoices, 25)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Summary statistics
    total_invoices = invoices.count()
    total_amount = invoices.aggregate(Sum("total_amount"))["total_amount__sum"] or 0
    paid_invoices = invoices.filter(status="PAID").count()

    context = {
        "page_obj": page_obj,
        "invoices": page_obj,
        "total_invoices": total_invoices,
        "total_amount": total_amount,
        "paid_invoices": paid_invoices,
        "students": StudentProfile.objects.select_related("user").all(),
        "invoice_statuses": Invoice.STATUS_CHOICES,
    }
    return render(request, "fees/invoices_list.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def create_invoice(request):
    """Create new invoice"""
    if request.method == "POST":
        form = InvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.status = Invoice.ISSUED
            invoice.save()

            # Handle invoice lines
            descriptions = request.POST.getlist("descriptions")
            amounts = request.POST.getlist("amounts")
            total = Decimal("0")

            for desc, amt in zip(descriptions, amounts):
                if desc and amt:
                    amount = Decimal(amt)
                    InvoiceLine.objects.create(
                        invoice=invoice, description=desc, amount=amount
                    )
                    total += amount

            invoice.total_amount = total
            invoice.save()

            messages.success(request, f"Invoice {invoice.id} created successfully.")
            return redirect("fees_invoices")
    else:
        form = InvoiceForm()

    # Get fee structures for suggestions
    fee_structures = FeeStructure.objects.filter(active=True).select_related(
        "grade_level"
    )

    return render(
        request,
        "fees/create_invoice.html",
        {"form": form, "fee_structures": fee_structures},
    )


@require_http_methods(["GET", "POST"])
def issue_invoice(request, student_id: int):
    student = get_object_or_404(
        StudentProfile.objects.select_related("user", "grade_level"), id=student_id
    )
    if request.method == "POST":
        term = request.POST.get("term", "")
        descriptions = request.POST.getlist("desc")
        amounts = request.POST.getlist("amount")
        due_date_str = request.POST.get("due_date")

        invoice = Invoice.objects.create(
            student=student,
            term=term,
            status=Invoice.ISSUED,
            due_date=(
                datetime.strptime(due_date_str, "%Y-%m-%d").date()
                if due_date_str
                else None
            ),
        )
        total = Decimal("0")
        for d, a in zip(descriptions, amounts):
            if not d or not a:
                continue
            amt = Decimal(a)
            InvoiceLine.objects.create(invoice=invoice, description=d, amount=amt)
            total += amt
        invoice.total_amount = total
        invoice.save()

        # Auto-generate receipt number if payment is made immediately
        payment_amount = request.POST.get("immediate_payment")
        if payment_amount:
            amount = Decimal(payment_amount)
            if amount > 0:
                payment = Payment.objects.create(
                    invoice=invoice,
                    amount=amount,
                    method=request.POST.get("payment_method", Payment.CASH),
                    reference=request.POST.get("payment_reference", ""),
                )

                # Create receipt
                receipt_number = f"RCT{payment.id:06d}"
                Receipt.objects.create(payment=payment, number=receipt_number)

                # Update invoice status
                if amount >= invoice.total_amount:
                    invoice.status = Invoice.PAID
                else:
                    invoice.status = Invoice.PARTIAL
                invoice.save()

        messages.success(request, f"Invoice {invoice.id} issued.")
        return redirect(reverse("fees_invoices"))

    # Suggest fee structures
    fee_structs = FeeStructure.objects.filter(
        grade_level=student.grade_level, active=True
    )
    return render(
        request,
        "fees/issue_invoice.html",
        {"student": student, "fee_structs": fee_structs},
    )


@login_required
@require_http_methods(["GET", "POST"])
def record_payment(request, invoice_id: int):
    invoice = get_object_or_404(
        Invoice.objects.select_related("student__user"), id=invoice_id
    )

    if request.method == "POST":
        form = PaymentForm(request.POST, invoice=invoice)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.invoice = invoice
            payment.save()

            # Create receipt automatically
            receipt_number = f"RCT{payment.id:06d}"
            Receipt.objects.create(payment=payment, number=receipt_number)

            # Update invoice status
            paid = sum(p.amount for p in invoice.payments.all())
            if paid >= invoice.total_amount:
                invoice.status = Invoice.PAID
            elif paid > 0:
                invoice.status = Invoice.PARTIAL
            else:
                invoice.status = Invoice.ISSUED
            invoice.save()

            messages.success(request, f"Payment recorded. Receipt: {receipt_number}")
            return redirect(reverse("fees_invoices"))
    else:
        form = PaymentForm(invoice=invoice)

    # Calculate outstanding balance
    paid_amount = sum(p.amount for p in invoice.payments.all())
    outstanding = invoice.total_amount - paid_amount

    return render(
        request,
        "fees/record_payment.html",
        {
            "invoice": invoice,
            "form": form,
            "outstanding": outstanding,
            "paid_amount": paid_amount,
        },
    )


@login_required
def receipt_view(request, payment_id: int):
    payment = get_object_or_404(
        Payment.objects.select_related("invoice__student__user"), id=payment_id
    )
    receipt, created = Receipt.objects.get_or_create(
        payment=payment, defaults={"number": f"RCT{payment.id:06d}"}
    )
    return render(
        request, "fees/receipt.html", {"payment": payment, "receipt": receipt}
    )


@login_required
@permission_required("fees.add_feestructure")
def bulk_invoice_creation(request):
    """Create bulk invoices for a grade level"""
    if request.method == "POST":
        form = BulkInvoiceForm(request.POST)
        if form.is_valid():
            grade_level = form.cleaned_data["grade_level"]
            term = form.cleaned_data["term"]
            due_date = form.cleaned_data["due_date"]
            fee_structures = form.cleaned_data["fee_structures"]

            students = StudentProfile.objects.filter(
                grade_level=grade_level, user__is_active=True
            )

            created_count = 0
            for student in students:
                # Check if invoice already exists
                existing = Invoice.objects.filter(student=student, term=term).exists()

                if not existing:
                    invoice = Invoice.objects.create(
                        student=student,
                        term=term,
                        due_date=due_date,
                        status=Invoice.ISSUED,
                    )

                    total = Decimal("0")
                    for fee_struct in fee_structures:
                        InvoiceLine.objects.create(
                            invoice=invoice,
                            description=f"{fee_struct.get_fee_type_display()} - {term}",
                            amount=fee_struct.amount,
                        )
                        total += fee_struct.amount

                    invoice.total_amount = total
                    invoice.save()
                    created_count += 1

            messages.success(
                request, f"Created {created_count} invoices for {grade_level}"
            )
            return redirect("fees_invoices")
    else:
        form = BulkInvoiceForm()

    return render(request, "fees/bulk_invoice.html", {"form": form})


@login_required
def financial_reports(request):
    """Generate financial reports"""
    form = PaymentReportForm(request.GET or None)

    # Base queryset
    payments = Payment.objects.select_related("invoice__student__user")
    invoices = Invoice.objects.select_related("student__user")

    # Apply filters
    if form.is_valid():
        if form.cleaned_data["date_from"]:
            payments = payments.filter(date__gte=form.cleaned_data["date_from"])
            invoices = invoices.filter(issue_date__gte=form.cleaned_data["date_from"])

        if form.cleaned_data["date_to"]:
            payments = payments.filter(date__lte=form.cleaned_data["date_to"])
            invoices = invoices.filter(issue_date__lte=form.cleaned_data["date_to"])

        if form.cleaned_data["payment_method"]:
            payments = payments.filter(method=form.cleaned_data["payment_method"])

        if form.cleaned_data["student"]:
            student = form.cleaned_data["student"]
            payments = payments.filter(invoice__student=student)
            invoices = invoices.filter(student=student)

        if form.cleaned_data["status"]:
            invoices = invoices.filter(status=form.cleaned_data["status"])

    # Calculate statistics
    total_revenue = payments.aggregate(Sum("amount"))["amount__sum"] or 0
    total_outstanding = (
        invoices.exclude(status="PAID").aggregate(Sum("total_amount"))[
            "total_amount__sum"
        ]
        or 0
    )

    # Payment method breakdown
    payment_methods = (
        payments.values("method")
        .annotate(total=Sum("amount"), count=Count("id"))
        .order_by("method")
    )

    # Monthly revenue (last 12 months)
    monthly_revenue = []
    for i in range(12):
        month_start = timezone.now().replace(day=1) - timedelta(days=i * 30)
        month_end = month_start + timedelta(days=30)
        revenue = (
            payments.filter(date__gte=month_start, date__lt=month_end).aggregate(
                Sum("amount")
            )["amount__sum"]
            or 0
        )
        monthly_revenue.append(
            {"month": month_start.strftime("%Y-%m"), "revenue": revenue}
        )

    context = {
        "form": form,
        "total_revenue": total_revenue,
        "total_outstanding": total_outstanding,
        "payment_methods": payment_methods,
        "monthly_revenue": reversed(monthly_revenue),
        "recent_payments": payments.order_by("-date")[:10],
    }

    return render(request, "fees/financial_reports.html", context)


@login_required
def fee_structure_list(request):
    """List fee structures"""
    fee_structures = FeeStructure.objects.select_related("grade_level").order_by(
        "grade_level__name", "fee_type"
    )
    return render(
        request, "fees/fee_structure_list.html", {"fee_structures": fee_structures}
    )


@login_required
@permission_required("fees.add_feestructure")
def create_fee_structure(request):
    """Create fee structure"""
    if request.method == "POST":
        form = FeeStructureForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Fee structure created successfully.")
            return redirect("fees_fee_structure_list")
    else:
        form = FeeStructureForm()

    return render(request, "fees/create_fee_structure.html", {"form": form})


@login_required
def invoice_detail(request, invoice_id):
    """Invoice detail view"""
    invoice = get_object_or_404(
        Invoice.objects.select_related("student__user").prefetch_related(
            "lines", "payments__receipt"
        ),
        id=invoice_id,
    )

    paid_amount = sum(p.amount for p in invoice.payments.all())
    outstanding = invoice.total_amount - paid_amount

    return render(
        request,
        "fees/invoice_detail.html",
        {"invoice": invoice, "paid_amount": paid_amount, "outstanding": outstanding},
    )


@login_required
def search_students(request):
    """AJAX endpoint to search students"""
    query = request.GET.get("q", "")
    if len(query) >= 2:
        students = StudentProfile.objects.filter(
            Q(user__first_name__icontains=query)
            | Q(user__last_name__icontains=query)
            | Q(user__username__icontains=query)
        ).select_related("user")[:10]

        results = [
            {
                "id": student.id,
                "text": f"{student.user.get_full_name()} ({student.user.username})",
            }
            for student in students
        ]

        return JsonResponse({"results": results})

    return JsonResponse({"results": []})


@login_required
def download_invoice_pdf(request, invoice_id):
    """Download invoice as PDF"""
    invoice = get_object_or_404(Invoice, id=invoice_id)
    
    # Permission check
    if request.user.role == "PARENT":
        try:
            parent_profile = request.user.parent_profile
            if not parent_profile.can_access_student(invoice.student):
                messages.error(request, "Access denied to invoice information.")
                return redirect("parents:children_list")
        except:
            messages.error(request, "Parent profile not found.")
            return redirect("dashboard")
    elif request.user.role == "STUDENT":
        if invoice.student.user != request.user:
            messages.error(request, "Access denied to invoice information.")
            return redirect("dashboard")
    elif request.user.role not in ["ADMIN", "TEACHER"]:
        messages.error(request, "Access denied.")
        return redirect("dashboard")
    
    return generate_fee_invoice_pdf(invoice)


@login_required
def download_receipt_pdf(request, payment_id):
    """Download payment receipt as PDF"""
    payment = get_object_or_404(Payment, id=payment_id)
    invoice = payment.invoice
    
    # Permission check (same as invoice)
    if request.user.role == "PARENT":
        try:
            parent_profile = request.user.parent_profile
            if not parent_profile.can_access_student(invoice.student):
                messages.error(request, "Access denied to receipt information.")
                return redirect("parents:children_list")
        except:
            messages.error(request, "Parent profile not found.")
            return redirect("dashboard")
    elif request.user.role == "STUDENT":
        if invoice.student.user != request.user:
            messages.error(request, "Access denied to receipt information.")
            return redirect("dashboard")
    elif request.user.role not in ["ADMIN", "TEACHER"]:
        messages.error(request, "Access denied.")
        return redirect("dashboard")
    
    # Generate receipt PDF (reusing invoice PDF generator for now)
    return generate_fee_invoice_pdf(invoice)


@login_required
def student_invoices(request):
    """Student view of their invoices"""
    if request.user.role != "STUDENT":
        messages.error(request, "Access denied.")
        return redirect("dashboard")
    
    try:
        student_profile = StudentProfile.objects.get(user=request.user)
    except StudentProfile.DoesNotExist:
        messages.error(request, "Student profile not found.")
        return redirect("dashboard")
    
    invoices = Invoice.objects.filter(student=student_profile).prefetch_related(
        'lines', 'payments__receipt'
    ).order_by('-issue_date')
    
    context = {
        'student_profile': student_profile,
        'invoices': invoices,
    }
    
    return render(request, 'fees/student_invoices.html', context)


@login_required
def parent_child_invoices(request, student_id):
    """Parent view of their child's invoices"""
    if request.user.role != "PARENT":
        messages.error(request, "Access denied.")
        return redirect("dashboard")
    
    try:
        parent_profile = request.user.parent_profile
    except:
        messages.error(request, "Parent profile not found.")
        return redirect("dashboard")
    
    student = get_object_or_404(StudentProfile, id=student_id)
    
    if not parent_profile.can_access_student(student):
        messages.error(request, "Access denied to student information.")
        return redirect("parents:children_list")
    
    invoices = Invoice.objects.filter(student=student).prefetch_related(
        'lines', 'payments__receipt'
    ).order_by('-issue_date')
    
    context = {
        'parent_profile': parent_profile,
        'student': student,
        'invoices': invoices,
    }
    
    return render(request, 'fees/parent_child_invoices.html', context)
