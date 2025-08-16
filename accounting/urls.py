from django.urls import path


from . import views, api_views

urlpatterns = [
    path('', views.index, name='index'),
    path('schema/', views.schema, name='schema'),
    path('upload_transactions/', views.upload_transactions, name='upload_transactions'),
    path('api/average', api_views.average, name='average'),
    path('api/transactions', api_views.transactions, name='transactions'),
]