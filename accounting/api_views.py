from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import F, Avg, Count
from django.db.models.functions import ExtractYear as Year, ExtractMonth as Month, ExtractDay as Day
from django.core.paginator import Paginator

from accounting.models import Transaction
from django.db.models.functions import ExtractYear, ExtractMonth
import datetime


@csrf_exempt
def average(request):
    """
    API endpoint to return aggregated transaction data.
    Accepts GET requests with optional 'range' query parameter ('yearly', 'monthly', 'daily').
    Groups transactions by category and date range, returning average and count per group.
    Response: JSON with status and data list.
    """
    if request.method == 'GET':
        aggregation_range = request.GET.get('range', 'monthly')
        if aggregation_range not in ['yearly', 'monthly', 'daily']:
            return JsonResponse({'error': 'Invalid range specified'}, status=400)

        transaction_values = None
        if aggregation_range == 'yearly':
            transaction_values = Transaction.objects.values(
                cat=F('category__name'),
                year=Year('date'))
        elif aggregation_range == 'monthly':
            transaction_values = Transaction.objects.values(
                cat=F('category__name'),
                year=Year('date'),
                month=Month('date'))
        elif aggregation_range == 'daily':
            transaction_values = Transaction.objects.values(
                cat=F('category__name'),
                year=Year('date'),
                month=Month('date'),
                day=Day('date'))

        average_amount = list(transaction_values.annotate(
            avg_amount=Avg('amount'),
            count_amount=Count('amount'),
        ).order_by('year', 'month', 'cat'))

        return JsonResponse({'status': 'ok', 'data': average_amount}, safe=False)

    return JsonResponse({'error': 'Invalid request method'}, status=400)


@csrf_exempt
def transactions(request):
    """
    API endpoint to return paginated transactions.
    Accepts GET requests with optional 'accountId' query parameter to filter by account.
    Returns paginated results (10 per page) using 'page' query parameter.
    Response: JSON with transaction data.
    """
    account_id = request.GET.get('accountId')
    if account_id:
        transactions = Transaction.objects.filter(account_id=account_id)
    else:
        transactions = Transaction.objects.all()

    # Paginate transactions by size (100 per page)
    paginator = Paginator(transactions, 100)
    page_number = request.GET.get('page')
    try:
        page_number = int(page_number)
        if page_number < 1:
            page_number = 1
    except (TypeError, ValueError):
        page_number = 1
    page_obj = paginator.get_page(page_number)

    # Serialize the data
    data = {
        "page": page_number,
        "transactions": list(page_obj.object_list.values()),
        "count": paginator.count,
        "has_next": page_obj.has_next(),
        "has_previous": page_obj.has_previous(),
    }
    return JsonResponse(data)