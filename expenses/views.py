from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Sum, Count
from django.http import Http404
from django.utils import timezone

from .models import Expense
from .forms import ExpenseForm


@login_required
def dashboard(request):

    user_expenses = Expense.objects.filter(
        user=request.user
    )

    today = timezone.localdate()

    total_spent = (
        user_expenses.aggregate(
            total=Sum('amount')
        )['total'] or 0
    )

    this_month = (
        user_expenses
        .filter(
            date__year=today.year,
            date__month=today.month
        )
        .aggregate(total=Sum('amount'))['total'] or 0
    )

    today_spent = (
        user_expenses
        .filter(date=today)
        .aggregate(total=Sum('amount'))['total'] or 0
    )

    tx_count = user_expenses.count()

    category_summary = (
        user_expenses
        .values('category')
        .annotate(
            total=Sum('amount'),
            count=Count('id')
        )
        .order_by('-total')
    )

    recent_expenses = user_expenses.order_by(
        '-date',
        '-created_at'
    )[:5]

    context = {
        'total_spent': total_spent,
        'this_month': this_month,
        'today_spent': today_spent,
        'tx_count': tx_count,
        'category_summary': category_summary,
        'recent_expenses': recent_expenses,
    }

    return render(
        request,
        'expenses/dashboard.html',
        context
    )


@login_required
def expense_list(request):

    expenses = Expense.objects.filter(
        user=request.user
    )

    search_term = request.GET.get(
        'search',
        ''
    )

    category = request.GET.get(
        'category',
        ''
    )

    payment_method = request.GET.get(
        'payment_method',
        ''
    )

    start_date = request.GET.get(
        'start_date',
        ''
    )

    end_date = request.GET.get(
        'end_date',
        ''
    )

    order = request.GET.get(
        'order',
        '-date'
    )

    if search_term:
        expenses = expenses.filter(
            title__icontains=search_term
        )

    if category:
        expenses = expenses.filter(
            category=category
        )

    if payment_method:
        expenses = expenses.filter(
            payment_method=payment_method
        )

    if start_date:
        expenses = expenses.filter(
            date__gte=start_date
        )

    if end_date:
        expenses = expenses.filter(
            date__lte=end_date
        )

    if order not in ['date', '-date', 'amount', '-amount']:
        order = '-date'

    expenses = expenses.order_by(order)

    paginator = Paginator(
        expenses,
        10
    )

    page_number = request.GET.get('page')

    page_obj = paginator.get_page(
        page_number
    )

    context = {
        'page_obj': page_obj,
        'categories': Expense.CATEGORY_CHOICES,
        'payment_methods': Expense.PAYMENT_CHOICES,
        'search_term': search_term,
        'selected_category': category,
        'selected_payment': payment_method,
        'start_date': start_date,
        'end_date': end_date,
        'selected_order': order,
    }

    return render(
        request,
        'expenses/expense_list.html',
        context
    )


@login_required
def expense_detail(request, pk):

    expense = get_object_or_404(
        Expense,
        pk=pk,
        user=request.user
    )

    return render(
        request,
        'expenses/expense_detail.html',
        {'expense': expense}
    )


@login_required
def expense_create(request):

    if request.method == 'POST':

        form = ExpenseForm(
            request.POST
        )

        if form.is_valid():

            expense = form.save(
                commit=False
            )

            expense.user = request.user

            expense.save()

            return redirect(
                'expense_list'
            )

    else:

        form = ExpenseForm()

    return render(
        request,
        'expenses/expense_form.html',
        {
            'form': form,
            'title': 'Add Expense'
        }
    )


@login_required
def expense_update(request, pk):

    expense = get_object_or_404(
        Expense,
        pk=pk
    )

    if expense.user != request.user:
        raise Http404

    if request.method == 'POST':

        form = ExpenseForm(
            request.POST,
            instance=expense
        )

        if form.is_valid():

            form.save()

            return redirect(
                'expense_detail',
                pk=expense.pk
            )

    else:

        form = ExpenseForm(
            instance=expense
        )

    return render(
        request,
        'expenses/expense_form.html',
        {
            'form': form,
            'title': 'Edit Expense'
        }
    )


@login_required
def expense_delete(request, pk):

    expense = get_object_or_404(
        Expense,
        pk=pk
    )

    if expense.user != request.user:
        raise Http404

    if request.method == 'POST':

        expense.delete()

        return redirect(
            'expense_list'
        )

    return render(
        request,
        'expenses/expense_confirm_delete.html',
        {'expense': expense}
    )


@login_required
def monthly_report(request):

    today = timezone.localdate()

    month = int(
        request.GET.get(
            'month',
            today.month
        )
    )

    year = int(
        request.GET.get(
            'year',
            today.year
        )
    )

    user_expenses = Expense.objects.filter(
        user=request.user
    )

    monthly_expenses = user_expenses.filter(
        date__year=year,
        date__month=month
    )

    total = (
        monthly_expenses.aggregate(
            total=Sum('amount')
        )['total'] or 0
    )

    highest = monthly_expenses.order_by(
        '-amount'
    ).first()

    category_summary = (
        monthly_expenses
        .values('category')
        .annotate(
            total=Sum('amount'),
            count=Count('id')
        )
        .order_by('-total')
    )

    context = {
        'month': month,
        'year': year,
        'total': total,
        'highest': highest,
        'category_summary': category_summary,
    }

    return render(
        request,
        'expenses/monthly_report.html',
        context
    )


@login_required
def category_summary(request):

    user_expenses = Expense.objects.filter(
        user=request.user
    )

    summary = (
        user_expenses
        .values('category')
        .annotate(
            total=Sum('amount'),
            count=Count('id')
        )
        .order_by('-total')
    )

    return render(
        request,
        'expenses/category_summary.html',
        {'summary': summary}
    )