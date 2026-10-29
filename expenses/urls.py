from django.urls import path

from .views import (
    dashboard,
    expense_list,
    expense_detail,
    expense_create,
    expense_update,
    expense_delete,
    monthly_report,
    category_summary,
)


urlpatterns = [

    path(
        '',
        dashboard,
        name='dashboard'
    ),

    path(
        'expenses/',
        expense_list,
        name='expense_list'
    ),

    path(
        'expenses/add/',
        expense_create,
        name='expense_create'
    ),

    path(
        'expenses/<int:pk>/',
        expense_detail,
        name='expense_detail'
    ),

    path(
        'expenses/<int:pk>/edit/',
        expense_update,
        name='expense_update'
    ),

    path(
        'expenses/<int:pk>/delete/',
        expense_delete,
        name='expense_delete'
    ),

    path(
        'reports/monthly/',
        monthly_report,
        name='monthly_report'
    ),

    path(
        'reports/categories/',
        category_summary,
        name='category_summary'
    ),
]