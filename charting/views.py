from django.shortcuts import render
from accounting.models import Account, Transaction
from django.db.models import Sum
import json
from django.core.paginator import Paginator

def transactions(request):
    transaction_list = Transaction.objects.all().order_by('-date')
    paginator = Paginator(transaction_list, 25)  # 25 transactions per page

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'charting/transactions.html', {'page_obj': page_obj})

def index(request):

    """Render the index page for charting."""

    # Get all accounts
    accounts = Account.objects.all()

    # Get all months present in transactions
    transactions = Transaction.objects.all()
    months = set()
    for t in transactions:
        month = t.date.strftime('%Y-%m')
        months.add(month)
    months = sorted(list(months))

    # Prepare data for each account
    datasets = []
    datasets_core = []
    for account in accounts:
        # For each month, compute the sum of transactions for this account up to that month
        progression = []
        progression_core = []
        for month in months:
            progression.append(account.end_of_month_balance(int(month.split('-')[0]), 
                                                            int(month.split('-')[1])))
            # We get all transaction in the year/month and also filter by CORE tag
            # This is to get the CORE progression
            core_qs = account.transactions.filter(date__month=int(month.split('-')[1]), 
                                                  date__year=int(month.split('-')[0]), 
                                                  transaction_tags__name='CORE',
                                                  transaction_type__in=['debit'])
            
            account_core_sum = core_qs.aggregate(sum=Sum('amount'))['sum'] or 0
            progression_core.append(float(abs(account_core_sum)))
    

        datasets.append({
            'label': account.name,
            'data': progression,
            'fill': False
        })
        datasets_core.append({
            'label': f"{account.name} - CORE",
            'data': progression_core,
            'fill': False
        })

    chart_data = {
        'labels': months,
        'datasets': datasets
    }

    core_chart_data = {
        'labels': months,
        'datasets': datasets_core
    }

    return render(request, 'charting/index.html', {
        'chart_data': json.dumps(chart_data),
        'core_chart_data': json.dumps(core_chart_data),
    })

