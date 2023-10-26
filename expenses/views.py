from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Category, Expense
import json
# Create your views here.
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.core.paginator import Paginator
import json
from django.http import JsonResponse
from userpreferences.models import UserPreference
from datetime import date, timedelta
from django.views.generic import TemplateView
from django.db.models import Sum


def search_expenses(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')
        expenses = Expense.objects.filter(
            amount__istartswith=search_str, owner=request.user) | Expense.objects.filter(
            date__istartswith=search_str, owner=request.user) | Expense.objects.filter(
            description__icontains=search_str, owner=request.user) | Expense.objects.filter(
            category__icontains=search_str, owner=request.user)
        data = expenses.values()
        return JsonResponse(list(data), safe=False)


@login_required(login_url='/authentication/login')
def index(request):
    categories = Category.objects.all()
    expenses = Expense.objects.filter(owner=request.user).order_by('-date')
    paginator = Paginator(expenses, 5)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator,page_number)

    # Check if UserPreference exists for the current user, or create one with defaults
    try:
        user_preference = UserPreference.objects.get(user=request.user)
    except UserPreference.DoesNotExist:
        # If it doesn't exist, create one with default values
        user_preference = UserPreference.objects.create(user=request.user, currency='USD')

    currency = user_preference.currency

    context = {
        'expenses': expenses,
        'page_obj': page_obj,
        'currency': currency  # Currency is now retrieved from user_preference
    }
    return render(request, 'expenses/index.html', context)

@login_required(login_url='/authentication/login')
# @csrf_exemp
def add_expense(request):
    categories = Category.objects.all()
    context = {
        'categories': categories,
        'values': request.POST
    }
    if request.method == 'GET':
        return render(request, 'expenses/add_expense.html', context)

    if request.method == 'POST':
        amount = request.POST.get('amount')

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'expenses/add_expense.html', context)
        description = request.POST.get('description')
        date = request.POST.get('expense_date')
        category = request.POST.get('category')

        if not description:
            messages.error(request, 'description is required')
            return render(request, 'expenses/add_expense.html', context)

        Expense.objects.create(owner=request.user, amount=amount, date=date,
                               category=category, description=description)
        messages.success(request, 'Expense saved successfully')

        return redirect('expenses')


@login_required(login_url='/authentication/login')
def expense_edit(request, id):
    expense = Expense.objects.get(pk=id)
    categories = Category.objects.all()
    context = {
        'expense': expense,
        'values': expense,
        'categories': categories
    }
    if request.method == 'GET':
        return render(request, 'expenses/edit-expense.html', context)
    if request.method == 'POST':
        amount = request.POST['amount']

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'expenses/edit-expense.html', context)
        description = request.POST['description']
        date = request.POST['expense_date']
        category = request.POST['category']

        if not description:
            messages.error(request, 'description is required')
            return render(request, 'expenses/edit-expense.html', context)

        expense.owner = request.user
        expense.amount = amount
        expense. date = date
        expense.category = category
        expense.description = description

        expense.save()
        messages.success(request, 'Expense updated  successfully')

        return redirect('expenses')


def delete_expense(request, id):
    expense = Expense.objects.get(pk=id)
    expense.delete()
    messages.success(request, 'Expense removed')
    return redirect('expenses')


############  GPT Generated  ###########

def expense_category_summary(request):
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
        # Default to last 6 months if the timeframe is not recognized
        start_date, end_date = six_months_ago, today

    expenses = Expense.objects.filter(
        owner=request.user, date__range=(start_date, end_date)
    )

    category_data = (
        expenses.values("category")
        .annotate(total_amount=Sum("amount"))
        .order_by("category")
    )

    final_report = {entry["category"]: entry["total_amount"] for entry in category_data}

    return JsonResponse({"expense_category_data": final_report}, safe=False)

###############################################################

class ChartView(TemplateView):
    template_name = 'expenses/stats.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["qs"] = Expense.objects.all()
        return context
    
