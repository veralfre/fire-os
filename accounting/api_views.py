from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import F, Avg, Count
from django.db.models.functions import ExtractYear as Year, ExtractMonth as Month, ExtractDay as Day

from accounting.models import Transaction

@csrf_exempt
def average(request):


    if request.method == 'GET':
        ## Check from query string the aggregation range (yearly, monthly, daily)
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

        ## We group by year/month and then we group them by categories

        average_amount = list(transaction_values.annotate(
            avg_amount=Avg('amount'),
            count_amount=Count('amount'),
        ).order_by('year', 'month', 'cat'))

        return JsonResponse({'status': 'ok', 'data': average_amount}, safe=False)
    

    return JsonResponse({'error': 'Invalid request method'}, status=400)