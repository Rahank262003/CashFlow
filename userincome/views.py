from decimal import Decimal
from django.shortcuts import render, redirect
from expenses.models import Expense
from .models import Source, UserIncome
from django.core.paginator import Paginator
from userpreferences.models import UserPreference
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import json
from userpreferences.models import UserPreference
from django.http import JsonResponse
from datetime import date,timedelta
from django.db.models import Sum
from .models import UserIncome,Budget
from django.views.generic import TemplateView



def search_income(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')
        income = UserIncome.objects.filter(
            amount__istartswith=search_str, owner=request.user) | UserIncome.objects.filter(
            date__istartswith=search_str, owner=request.user) | UserIncome.objects.filter(
            description__icontains=search_str, owner=request.user) | UserIncome.objects.filter(
            source__icontains=search_str, owner=request.user)
        data = income.values()
        return JsonResponse(list(data), safe=False)


@login_required(login_url='/authentication/login')
def index(request):
    categories = Source.objects.all()
    income = UserIncome.objects.filter(owner=request.user)
    paginator = Paginator(income, 5)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)
    currency = UserPreference.objects.get(user=request.user).currency
    context = {
        'income': income,
        'page_obj': page_obj,
        'currency': currency
    }
    return render(request, 'income/index.html', context)


@login_required(login_url='/authentication/login')
def add_income(request):
    sources = Source.objects.all()
    context = {
        'sources': sources,
        'values': request.POST
    }
    if request.method == 'GET':
        return render(request, 'income/add_income.html', context)

    if request.method == 'POST':
        amount = request.POST['amount']

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'income/add_income.html', context)
        description = request.POST['description']
        date = request.POST['income_date']
        source = request.POST['source']

        if not description:
            messages.error(request, 'description is required')
            return render(request, 'income/add_income.html', context)

        UserIncome.objects.create(owner=request.user, amount=amount, date=date,
                                  source=source, description=description)
        messages.success(request, 'Record saved successfully')

        return redirect('income')


@login_required(login_url='/authentication/login')
def income_edit(request, id):
    income = UserIncome.objects.get(pk=id)
    sources = Source.objects.all()
    context = {
        'income': income,
        'values': income,
        'sources': sources
    }
    if request.method == 'GET':
        return render(request, 'income/edit_income.html', context)
    if request.method == 'POST':
        amount = request.POST['amount']

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'income/edit_income.html', context)
        description = request.POST['description']
        date = request.POST['income_date']
        source = request.POST['source']

        if not description:
            messages.error(request, 'description is required')
            return render(request, 'income/edit_income.html', context)
        income.amount = amount
        income. date = date
        income.source = source
        income.description = description

        income.save()
        messages.success(request, 'Record updated  successfully')

        return redirect('income')


def delete_income(request, id):
    income = UserIncome.objects.get(pk=id)
    income.delete()
    messages.success(request, 'record removed')
    return redirect('income')



def income_category_summary(request):
    today = date.today()
    six_months_ago = today - timedelta(days=30 * 6)
    three_months_ago = today - timedelta(days=30 * 3)
    last_month_start = today.replace(day=1) - timedelta(days=1)
    last_month_end = today.replace(day=1)

    # Determine the timeframe based on query parameters
    timeframe = request.GET.get("timeframe", "last6months")

    if timeframe == "last6months":
        start_date, end_date = six_months_ago, today
    elif timeframe == "last3months":
        start_date, end_date = three_months_ago, today
    elif timeframe == "lastmonth":
        start_date, end_date = last_month_start, last_month_end
    else:
        start_date, end_date = six_months_ago, today

    incomes = UserIncome.objects.filter(
        owner=request.user, date__range=(start_date, end_date)
    )

    category_data = (
        incomes.values("source")
        .annotate(total_amount=Sum("amount"))
        .order_by("source")
    )

    final_report = {entry["source"]: entry["total_amount"] for entry in category_data}

    return JsonResponse({"income_category_data": final_report}, safe=False)



class ChartView(TemplateView):
    template_name = 'income/income_stats.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["qs"] = UserIncome.objects.all()
        return context
    

from .models import Budget
from .forms import BudgetForm
def budget(request):
    budget_data = Budget.objects.first()

    if request.method == 'POST':
        form = BudgetForm(request.POST)
        if form.is_valid():
            if budget_data:
                budget_data.total_budget = form.cleaned_data['total_budget']
                budget_data.start_date = form.cleaned_data['start_date']
                budget_data.end_date = form.cleaned_data['end_date']
                budget_data.save()
            else:
                Budget.objects.create(**form.cleaned_data)
            return redirect('budget')

    else:
        form = BudgetForm(instance=budget_data)
    total_expenses = Decimal(Expense.objects.all().aggregate(total=Sum('amount'))['total'] or 0)
    difference = budget_data.total_budget - total_expenses

    return render(request, 'income/budget.html', {'form': form, 'budget_data': budget_data, 'total_expenses': total_expenses, 'difference': difference})
