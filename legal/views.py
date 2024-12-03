from django.shortcuts import render

def terms(request):
    return render(request, 'legal/terms.html')
