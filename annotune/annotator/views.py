from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import login
from .forms import CustomUserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from .forms import CustomAuthenticationForm
from .forms import FileUploadForm
from .models import UploadedFile, JSONEntry, CSVRow
import json
import csv
from io import StringIO

class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = 'login.html'
    redirect_authenticated_user = True  # Redirect users who are already logged in

    def get_success_url(self):
        return reverse('homepage') 
 
def sign_up(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log the user in immediately after registration
            return redirect(reverse('homepage'))  # Redirect to a home page or dashboard
    else:
        form = CustomUserCreationForm()
    return render(request, 'sign-up.html', {'form': form})
    
@login_required(login_url="")
def homepage(request):
    
    return render(request, "homepage.html")

# @login_required(login_url="") 
def load_files(request):
    form = FileUploadForm()
    uploaded_files = UploadedFile.objects.all()  # Retrieve all uploaded files from the database
    for a in uploaded_files:
        print(a)

    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = form.cleaned_data['uploaded_file']
            file_record = UploadedFile(
                file_name=uploaded_file.name,
                file_type=uploaded_file.content_type,
                size=uploaded_file.size
            )
            file_record.save()
            return redirect('load-files')  # Refresh to display the new file

    return render(request, 'load_files.html', {
        'form': form,
        'uploaded_files': uploaded_files
    })
    

def list_documents(request):
    return render(request, "documents.html", {"range":range(10)})

def label (request):
    documenttext = """A major French union warned of possible strikes, including at hospitals, during 
    the Paris Olympics, when a massive influx of people is in the French capital. Speaking to France 
    Info media on Thursday, the general secretary of the CGT said the union will give a notice of 
    strike in public services during the Games, which are held in July-August. The Paralympics take 
    place in August-September. Paris' tourism office predicts up to 15.9 million people could visit 
    the Paris region during July-September. “We want the government to take immediate action to ensure 
    the success of the Games,” Sophie Binet said. “For this to happen, our warnings must be heeded and 
    the Games must be prepared from a social point of view. We've been saying the same thing for months 
    now, and no one cares. It's getting very tiresome."""

    

    document_id = 1
    number = 1

    label= "Labor Disruption Threat during Paris Olympics"

    explanation = """A French union, CGT, warns of possible strikes during the Paris Olympics due to 
    social concerns. With up to 15.9 million visitors expected, essential services, notably healthcare, 
    could be affected. The union demands government action for the Games' success, highlighting 
    potential labor unrest and logistical challenges."""


    data = {
        "document": documenttext,
        "label":label,
        "explanation":explanation,
        "number": number,
        "range":range(10)
        }

    return render(request, "label.html", context=data)

def label2(request):

    text = """A major French union warned of possible strikes, including at hospitals, during 
    the Paris Olympics, when a massive influx of people is in the French capital. Speaking to France 
    Info media on Thursday, the general secretary of the CGT said the union will give a notice of 
    strike in public services during the Games, which are held in July-August. The Paralympics take 
    place in August-September. Paris' tourism office predicts up to 15.9 million people could visit 
    the Paris region during July-September. “We want the government to take immediate action to ensure 
    the success of the Games,” Sophie Binet said. “For this to happen, our warnings must be heeded and 
    the Games must be prepared from a social point of view. We've been saying the same thing for months 
    now, and no one cares. It's getting very tiresome."""

    recommended_labels = ["first label", "second label", "third label"]

    keywords = {
        "cluster1": ["major", "words", "union", "words", "words", "warned", "words", "during"],
        "cluster2": ["people", "massive", "words2", "influx", "words2", "capital", "words2", "will", "words2"],
        "cluster3": ["want", "point", "view", "cares", "same", "words3", "saying", "words3", "visit"],
        "cluster4": ["major", "words", "union", "words", "words", "warned", "words", "during"],
        "cluster5": ["people", "massive", "words2", "influx", "words2", "capital", "words2", "will", "words2"],
        "cluster6": ["want", "point", "view", "cares", "same", "words3", "saying", "words3", "visit"]

    }

    data = {
        "text":text,
        "recommended_labels": recommended_labels,
        "keywords": keywords
    }

    return render(request, "label2.html", context=data)