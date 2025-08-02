from django.shortcuts import render

# Create your views here.

def index(request):
    ## We want to return a simple index page with a graph 
    return render(request, 'charting/index.html')

