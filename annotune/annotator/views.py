from django.shortcuts import render, redirect
import requests
import json
from .utils import *
from django.http import JsonResponse
from collections import OrderedDict
import datetime
from django.contrib.auth import logout
import random
from django.contrib import messages

 
all_texts = json.load(open("/Users/danielstephens/Desktop/Annotune-v2/bills_preprocessed.json"))
url =  "http://127.0.0.1:1234/"
 
 
def sign_up(request):
    email=None
     
    if request.method == 'POST':
        with open('./annotator/static/users.json', "r") as user_file:
            name_string = user_file.read()
            information = json.loads(name_string)

        if email not in information.keys():
        
            user = requests.get(url + "//create_user")
            user_id = user.json()['user_id']
            first_name = request.POST['first_name']
            last_name = request.POST['last_name']
            email = request.POST['email']
            password = request.POST['password']
            time = datetime.datetime.now().strftime("%d/%m/%y %H:%M:%S")

            user_information =  {"first_name": first_name,
                                "last_name": last_name,
                                "user_id":user_id,
                                "email":email,
                                "password":password,
                                "document_id" : [],
                                "label": [],
                                "labels" :{},
                                "start_time": time,
                                "date": datetime.datetime.now().strftime("%d/%m/%y")
                                }
            information[email]=user_information

            with open("./annotator/static/users.json", "w") as user_file:
                json.dump(information, user_file, indent=4)

            request.session["email"] = email
            request.session["user_id"] = user_id
            request.session["labels"] = []
            request.session["document_ids"]= []
            request.session["start_time"] = time
            return render(request, "homepage.html")

        return redirect("login", {"time":datetime.datetime.now().strftime("%d/%m/%y %H:%M:%S")})
            
    return render(request, "sign-up.html", {"time":datetime.datetime.now().strftime("%d/%m/%y %H:%M:%S")})


def login(request):

    if request.method == 'POST':

        email = request.POST['email']
        with open('./annotator/static/users.json', "r") as user_file:
            name_string = user_file.read()
            information = json.loads(name_string)

        if email not in information.keys():
            return redirect("sign-up")
        
        else:
            request.session["email"] = information[email]["email"]
            request.session["user_id"] = information[email]["user_id"]
            request.session["labels"] = information[email]["label"],
            request.session["document_ids"]= information[email]["document_id"]
            request.session["start_time"]= information[email]["start_time"]

            return redirect("homepage", user_id=information[email]["user_id"] )


         
    return render(request, "login.html")


def homepage(request, user_id):
    print(request.session["start_time"])
    return render(request, "homepage.html", {"user_id": request.session["user_id"], "time":request.session["start_time"]})

def list_documents(request, user_id):

    get_topic_list = url + "//get_topic_list" 
        
    topics = requests.post(get_topic_list, json={
                            "user_id": request.session["user_id"]
                            }).json()

    # recommended = int(topics["document_id"])

    # keywords = topics["keywords"]

    a, b, c, d = truncated_data(topics, all_texts)
    
    
  

    return render(request, "documents.html", {"all_texts": a, "clusters": d, "keywords":b, "recommended_doc_id" :c, "user_id":request.session["user_id"], "time":request.session["start_time"]})

def label (request,user_id, document_id):
    user_id = request.session["user_id"]
    

    get_document_information = url + "get_document_information"
    response = requests.post(get_document_information, json={ "document_id": document_id,
                                                        "user_id":user_id
                                                         }).json()

    documenttext = all_texts["text"][str(5)]

    

    original_labels = response["llm_labels"]
    most_confident = original_labels[0]
    labels = random.sample(original_labels, len(original_labels))
    print(labels)

    explanation = response["description"]

    confidence = str(response["confident"]).lower()
    

    print(request.session["document_ids"])
    data = {
        "document": documenttext,
        "labels":labels,
        "explanation":explanation,
        "user_id":user_id,
        "document_id":document_id,
        "confidence" :confidence,
        "time":request.session["start_time"],
        "most_confident":most_confident
        }

    return render(request, "label.html", context=data)



def skip_document(request):
    current_doc_id = request.POST.get('current_doc_id')

    return redirect('document_view')



def submit_data(request, document_id, label):
    time=datetime.datetime.now().strftime("%d/%m/%y %H:%M:%S")
    print(time)


    append_to_json_file(request.session["email"], label, document_id, time )

    request.session["document_ids"].append(document_id)
    request.session["labels"].append(label)
    document_id = document_id
    user_id=request.session["user_id"]
    response_time = str(time)
    submit_document = url + "recommend_document"

    data_to_submit = {
            "document_id": document_id,
            "label": label,
            "user_id": user_id,
            "response_time": response_time,
            "description": "no description",
    }

    # print(data_to_submit)
    response = requests.post(submit_document, json=data_to_submit).json()
    print(response)
    document_id = response["document_id"]


    # return redirect("fetch-data", user_id=user_id, document_id=document_id)


    
    data = get_document_data(url=url, user_id=user_id, document_id=document_id, all_texts=all_texts)


    return JsonResponse(data)


def fetch_data(request, user_id, document_id):
    data = get_document_data(url=url, user_id=user_id, document_id=document_id, all_texts=all_texts)
    return JsonResponse(data)

def skip_document(request):
    next_document_link = url + "/skip_document" 
        
    response = requests.post(next_document_link, json={
                            "user_id": request.session["user_id"]
                            }).json()
    
    return JsonResponse({"document_id":response["document_id"]})

 
    




def get_all_documents(request ):
 
    data = {"document_ids": request.session["document_ids"][::-1],
            "labels": request.session["labels"][0][::-1]}
    return JsonResponse(data)
    

def logout_view(request):
    logout(request)
    return redirect('login')  