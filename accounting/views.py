from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator

from accounting.models import Account, Transaction, TransactionCategory, Currency, TransactionTag
import csv


# Create your views here.
def index(request):
    ## return empty json for now
    return JsonResponse({})

def schema(request):
    ## We return the headers schema for the transactions
    headers = [
        'account_id',
        'amount',
        'date',
        'category',
        'description',
        'currency',
        'transaction_type',
        'tags'
    ]
    return JsonResponse({"headers": headers})

@csrf_exempt
def upload_transactions(request):
    if request.method == 'POST':
        transactions = request.FILES.get('transactions_file')
        if not transactions:
            return JsonResponse({"error":"No file uploaded"}, status=400)

        ## Transaction file is a CSV file
        if not transactions.name.endswith('.csv'):
            return JsonResponse({"error":"Invalid file format. Please upload a CSV file."}, status=400)
        ## Process the CSV file
        uploaded_data = csv_to_list(transactions, has_header=True)
        
        for object in uploaded_data:
            # Here you can create Transaction objects or any other processing
            # For example:
            try:
                account = Account.objects.get(id=object['account_id'])
                ## Create transaction category and currency if they do not exist
                if not TransactionCategory.objects.filter(name=object['category']).exists():
                    category = TransactionCategory.objects.create(name=object['category'])
                else:   
                    category = TransactionCategory.objects.get(name=object['category'])
                if not Currency.objects.filter(code=object['currency']).exists():
                    currency = Currency.objects.create(code=object['currency'], name=object['currency'])
                else:
                    currency = Currency.objects.get(code=object['currency'])
                
                ## Tags may be empty or not existent
                if object.get('tags'):
                    transaction_tags = TransactionTag.objects.filter(name__in=object['tags'].split(','))
                else:
                    transaction_tags = TransactionTag.objects.none()
                amount = float(object['amount'])
                if object.get('transaction_type') not in ['credit', 'debit', 'balance']:
                    if amount < 0:
                        transaction_type = 'debit'
                    else:
                        transaction_type = 'credit'
                else:
                    transaction_type = object['transaction_type']
            
                transaction = Transaction(
                    account=account,
                    amount=amount,
                    date=object['date'],
                    category=category,
                    description=object.get('description', ''),
                    currency=currency,
                    transaction_type=transaction_type
                )
                transaction.save()
                transaction.transaction_tags.set(transaction_tags)
            except Exception as e:
                return JsonResponse({"error": str(e)}, status=400)

        # Handle file upload and processing here
        return JsonResponse({"success":"File uploaded successfully"})
    else:
        return JsonResponse({"error":"Upload a file to process transactions"})
    


def csv_to_list(csv_file, has_header=True):
    """
    Convert a CSV file to a list of dictionaries.
    If has_header is True, the first row is used as keys.
    """
    data = []
    text_file = csv_file.read().decode('utf-8')
    reader = csv.DictReader(text_file.splitlines()) if has_header else csv.reader(text_file.splitlines())

    for row in reader:
        data.append(row)
    
    return data