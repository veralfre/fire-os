from django.db import models
from hashlib import sha256
# Create your models here.

class Account(models.Model):
    class Meta:
        verbose_name_plural = "Accounts"
    id = models.CharField(primary_key=True)
    name = models.CharField(max_length=100)
    # Balance is the sum of all transactions in this account
    # It can be positive or negative
    # It can also be zero
    child_of = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    def __str__(self):
        return f"{self.name} - {self.get_balance()}"

    def get_balance(self):
        all_transactions = self.transactions.all().order_by('date')
        sum = 0
        for transaction in all_transactions:
            if transaction.transaction_type == 'balance':
                sum = transaction.amount
            else:
                sum += transaction.amount
        return sum 
    

## TransactionCategory
## User Can add more categories on the run
class TransactionCategory(models.Model):
    class Meta:
        verbose_name_plural = "Transaction Categories"
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    
class Currency(models.Model):
    class Meta:
        verbose_name_plural = "Currencies"
    # Id must be unique but provided by the user
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=3, unique=True)  # e.g., 'USD', 'EUR'
    name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.code} - {self.name}"

class TransactionTag(models.Model): 
    class Meta:
        verbose_name_plural = "Transaction Tags"  
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Transaction(models.Model):
    class Meta:
        verbose_name_plural = "Transactions"
        ordering = ["-date"]



    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(TransactionCategory, on_delete=models.CASCADE, related_name='transactions')
    description = models.TextField(blank=True, null=True)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='transactions')
    transaction_tags = models.ManyToManyField(TransactionTag, blank=True, related_name='transactions')
    # transaction_type can be 'credit' or 'debit' or 'balance'
    transaction_type = models.CharField(max_length=10, choices=[
        ('credit', 'Credit'),
        ('debit', 'Debit'),
        ('balance', 'Balance')
    ])
    date = models.DateTimeField()
    # id may be provided by the user, if not it's hash of the transaction details
    id = models.CharField(max_length=100, primary_key=True, unique=True)

    def __str__(self):
        simple_date = self.date.strftime('%Y-%m-%d %H:%M') if self.date else ''
        return f"[{self.transaction_type}][{simple_date}] {self.description} : {self.amount} - [{self.account.name}]"
    
    def save(self, *args, **kwargs):
        if not self.id:
            hash_input = f"{self.account_id}{self.amount}{self.date}{self.category_id}{self.currency_id}{self.description}"
            self.id = sha256(hash_input.encode('utf-8')).hexdigest()[:100]
        super().save(*args, **kwargs)