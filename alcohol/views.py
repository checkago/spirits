from django.shortcuts import render


def index(request):
    title = 'Moscow Spirits'
    return render(request, 'index.html', {'title': title})
