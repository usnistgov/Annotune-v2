from django.shortcuts import render, HttpResponse

# Create your views here.
def login(request):
    return  render (request, "login.html")

def sign_up(request):
    return  render (request, "sign-up.html")

def homepage(request):
    return render(request, "homepage.html")