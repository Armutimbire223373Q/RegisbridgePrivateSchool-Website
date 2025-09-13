from django.urls import path
from . import views

urlpatterns = [
    # Invoice management
    path("invoices/", views.invoices_list, name="fees_invoices"),
    path("invoices/create/", views.create_invoice, name="fees_create_invoice"),
    path(
        "invoices/<int:invoice_id>/", views.invoice_detail, name="fees_invoice_detail"
    ),
    path("invoices/bulk/", views.bulk_invoice_creation, name="fees_bulk_invoice"),
    path("issue/<int:student_id>/", views.issue_invoice, name="fees_issue"),
    # Payment management
    path("pay/<int:invoice_id>/", views.record_payment, name="fees_pay"),
    path("receipt/<int:payment_id>/", views.receipt_view, name="fees_receipt"),
    # Fee structure management
    path("fee-structures/", views.fee_structure_list, name="fees_fee_structure_list"),
    path(
        "fee-structures/create/",
        views.create_fee_structure,
        name="fees_create_fee_structure",
    ),
    # Reports
    path("reports/", views.financial_reports, name="fees_financial_reports"),
    # PDF Downloads
    path("invoice/<int:invoice_id>/pdf/", views.download_invoice_pdf, name="fees_download_invoice_pdf"),
    path("receipt/<int:payment_id>/pdf/", views.download_receipt_pdf, name="fees_download_receipt_pdf"),
    # Student and Parent Views
    path("student/invoices/", views.student_invoices, name="fees_student_invoices"),
    path("parent/child/<int:student_id>/invoices/", views.parent_child_invoices, name="fees_parent_child_invoices"),
    # AJAX endpoints
    path("api/search-students/", views.search_students, name="fees_search_students"),
]
