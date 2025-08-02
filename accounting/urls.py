from django.urls import path


from . import views 

urlpatterns = [
    path('', views.index, name='index'),
    path('schema/', views.schema, name='schema'),
    path('upload_transactions/', views.upload_transactions, name='upload_transactions'),
]