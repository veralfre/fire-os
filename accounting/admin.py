from django.contrib import admin
import accounting.models as models


## I want to register all the model objects in the admin panel 

admin.site.register(models.Account) 
# They will be sorted by date 
admin.site.register(models.Transaction)
admin.site.register(models.TransactionCategory)
admin.site.register(models.Currency)
admin.site.register(models.TransactionTag)


