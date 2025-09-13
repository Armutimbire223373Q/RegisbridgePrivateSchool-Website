from typing import Dict, List

from django.db.models import Sum
from django.http import HttpRequest
from django.utils import timezone

from students.models import StudentProfile
from teachers.models import TeacherProfile
from parents.models import Parent
from fees.models import Invoice, Payment, InvoiceLine
from public.models import NewsPost
from core_attendance.models import StudentAttendance
from grades.models import Term


def admin_stats(request: HttpRequest) -> Dict[str, object]:
    if not request.path.startswith("/admin/"):
        return {}

    stats = {}
    try:
        stats["admin_total_students"] = StudentProfile.objects.count()
        stats["admin_total_teachers"] = TeacherProfile.objects.count()
        stats["admin_total_parents"] = Parent.objects.count()

        # Term filter
        selected_term = None
        selected_term_id = request.GET.get("term") if hasattr(request, "GET") else None
        if selected_term_id:
            try:
                selected_term = Term.objects.get(id=selected_term_id)
            except Term.DoesNotExist:
                selected_term = None

        invoice_qs = Invoice.objects.filter(status="ISSUED")
        payment_qs = Payment.objects.all()
        if selected_term is not None:
            invoice_qs = invoice_qs.filter(term=selected_term)
            payment_qs = payment_qs.filter(invoice__term=selected_term)

        # More robust issued total using sum of invoice lines to avoid stale total_amount
        total_fees = (
            InvoiceLine.objects.filter(invoice__in=invoice_qs).aggregate(
                total=Sum("amount")
            )["total"]
            or 0
        )
        total_paid = payment_qs.aggregate(total=Sum("amount"))["total"] or 0
        stats["admin_total_fees_issued"] = total_fees
        stats["admin_total_fees_paid"] = total_paid
        stats["admin_total_fees_outstanding"] = total_fees - total_paid
        # Build last 6 months series for charts
        now = timezone.now()
        labels: List[str] = []
        payments_values: List[float] = []
        admissions_values: List[int] = []

        for i in range(5, -1, -1):
            month_ref = (now.replace(day=1) - timezone.timedelta(days=1)).replace(day=1)
            # Recompute correctly by subtracting months cumulatively
            ref_year = now.year
            ref_month = now.month - i
            while ref_month <= 0:
                ref_month += 12
                ref_year -= 1

            labels.append(f"{ref_year}-{ref_month:02d}")

            month_start = timezone.datetime(
                ref_year,
                ref_month,
                1,
                tzinfo=timezone.utc if timezone.is_aware(now) else None,
            )
            if ref_month == 12:
                month_end = timezone.datetime(
                    ref_year + 1, 1, 1, tzinfo=month_start.tzinfo
                )
            else:
                month_end = timezone.datetime(
                    ref_year, ref_month + 1, 1, tzinfo=month_start.tzinfo
                )

            month_payments = payment_qs.filter(
                date__gte=month_start, date__lt=month_end
            )
            payments_sum = month_payments.aggregate(total=Sum("amount"))["total"] or 0
            admissions_count = StudentProfile.objects.filter(
                enrollment_date__gte=month_start, enrollment_date__lt=month_end
            ).count()

            payments_values.append(float(payments_sum))
            admissions_values.append(int(admissions_count))

        stats["chart_payments_labels"] = labels
        stats["chart_payments_values"] = payments_values
        stats["chart_admissions_labels"] = labels
        stats["chart_admissions_values"] = admissions_values

        # Recent activity
        # Recent payments (fallback to id ordering if date is null)
        recent_payments_qs = payment_qs.select_related(
            "invoice", "invoice__student__user"
        )
        if recent_payments_qs.filter(date__isnull=False).exists():
            recent_payments_qs = recent_payments_qs.order_by("-date")
        else:
            recent_payments_qs = recent_payments_qs.order_by("-id")
        stats["recent_payments"] = list(recent_payments_qs[:5])
        stats["recent_admissions"] = list(
            StudentProfile.objects.select_related(
                "user", "classroom", "grade_level"
            ).order_by("-enrollment_date")[:5]
        )
        stats["recent_news"] = list(
            NewsPost.objects.filter(is_published=True).order_by("-published_date")[:5]
        )

        # Today's attendance summary
        today = timezone.now().date()
        att_qs = StudentAttendance.objects.filter(date=today)
        stats["today_attendance_present"] = att_qs.filter(status="PRESENT").count()
        stats["today_attendance_absent"] = att_qs.filter(status="ABSENT").count()
        stats["today_attendance_late"] = att_qs.filter(status="LATE").count()

        # Term selector data
        terms = Term.objects.select_related("academic_year").order_by(
            "-academic_year__start_date", "name"
        )
        stats["filter_terms"] = [
            {"id": t.id, "label": f"{t.academic_year.name} - {t.name}"} for t in terms
        ]
        stats["selected_term_id"] = (
            str(selected_term.id) if selected_term is not None else ""
        )
        stats["selected_term_label"] = (
            f"{selected_term.academic_year.name} - {selected_term.name}"
            if selected_term is not None
            else "All Terms"
        )

    except Exception:
        # Fail silently in admin
        pass

    return stats
