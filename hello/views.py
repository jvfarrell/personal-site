import requests
from django.shortcuts import render
from django.http import HttpResponse
import hello.quotes
from .models import Greeting

# Create your views here.
def index(request):
    r = requests.get('http://httpbin.org/status/418')
    print(r.text)
    return HttpResponse('<pre>' + r.text + '</pre>')


def db(request):

    greeting = Greeting()
    greeting.save()

    greetings = Greeting.objects.all()

    return render(request, 'db.html', {'greetings': greetings})


def resume(request):
    return render(request, 'resume.html')


def home(request):
    qotd = hello.quotes.get_random_quote()
    return render(request, 'homepage.html', {'daily_quote': qotd, 'quotes': hello.quotes.quotes})


def quote(request):
    return render(request, 'quote.html', {'quote': hello.quotes.get_random_quote()})


def nfl_analytics(request):
    return render(request, 'nfl_analytics.html')


def videos_page(request):
    return render(request, 'youtube_links.html')