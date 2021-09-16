from django.shortcuts import render


def index(request):
    title = 'Moscow Spirits'
    description = 'Крафтовые алкогольные напитки'
    return render(request, 'index.html', {'title': title, 'description': description})
