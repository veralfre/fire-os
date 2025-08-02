from django.shortcuts import render
from accounting.models import Account, Transaction
from django.db.models import Sum
import json
from collections import defaultdict
from django.utils.timezone import make_aware
import datetime
# Create your views here.

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
            progression_core.append(account.end_of_month_balance(int(month.split('-')[0]), 
                                                                int(month.split('-')[1]), 
                                                                tags=['CORE']))
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
        'core_chart_data': json.dumps(core_chart_data)
    })

