from django.shortcuts import render, redirect
import requests
import json
from .utils import *
from django.http import JsonResponse
from collections import OrderedDict
import datetime
from django.contrib.auth import logout
import random
from pytz import timezone
eastern = timezone('US/Eastern')
import environ

env = environ.Env()



 
all_texts = json.load(open("./annotator/bills_preprocessed.json"))
url =  env("URL")
 
 
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
            time = datetime.datetime.now(eastern).strftime("%d/%m/%y %H:%M:%S")
            print(time)

            user_information =  {"first_name": first_name,
                                "last_name": last_name,
                                "user_id":user_id,
                                "email":email,
                                "password":password,
                                "document_id" : [],
                                "label": [],
                                "labels" :{},
                                "start_time": time,
                                "date": datetime.datetime.now(eastern).strftime("%d/%m/%y"),
                                "pageTimes": [],
                                "hoverTimes":[]
                                }
            information[email]=user_information

            with open("./annotator/static/users.json", "w") as user_file:
                json.dump(information, user_file, indent=4)

            request.session["email"] = information[email]["email"]
            request.session["user_id"] = information[email]["user_id"]
            request.session["labels"] = information[email]["label"],
            request.session["document_ids"]= information[email]["document_id"]
            request.session["start_time"]= information[email]["start_time"]

            return redirect("homepage", user_id=information[email]["user_id"] )

        return redirect("login", {"time":datetime.datetime.now(eastern).strftime("%d/%m/%y %H:%M:%S")})
            
    return render(request, "sign-up.html", {"time":datetime.datetime.now(eastern).strftime("%d/%m/%y %H:%M:%S")})


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
    return render(request, "homepage.html", {"user_id": request.session["user_id"], "start_time":request.session["start_time"]})

def list_documents(request, user_id):

    get_topic_list = url + "//get_topic_list" 
        
    topics = requests.post(get_topic_list, json={
                            "user_id": request.session["user_id"]
                            }).json()

    # recommended = int(topics["document_id"])

    # keywords = topics["keywords"]

    a, b, c, d = truncated_data(topics, all_texts)

    print(type(request.session["user_id"]))
  

    return render(request, "documents.html", {"all_texts": a, "clusters": d, "keywords":b, "recommended_doc_id" :c, "user_id":request.session["user_id"], "start_time":request.session["start_time"]})


def label (request,user_id, document_id):
    user_id = request.session["user_id"]
    

    get_document_information = url + "get_document_information"
    response = requests.post(get_document_information, json={ "document_id": document_id,
                                                        "user_id":user_id
                                                         }).json()
    # print(response.keys())
    documenttext = all_texts["text"][str(document_id)]

    with open('./annotator/static/users.json', "r") as user_file:
        name_string = user_file.read()
        information = json.loads(name_string)

    past_labels = list(set(information[request.session["email"]]["label"]))

    

    original_labels = response["llm_labels"]

    most_confident = original_labels[0]
    labels = random.sample(original_labels, len(original_labels))

    explanation = response["description"]

    confidence = str(response["confident"]).lower()


    #Take it off
###################################
    conf =random.randint(1, 1000)
    if conf%2 ==0:
        confidence="true"
    else:
        confidence="false"
################################## 

    print(past_labels)
    
    # old_labels = request.session["labels"]
    # if len(old_labels)==0:
    #     all_old_labels = []
    # else:

    #     all_old_labels = sorted(list(set(request.session["labels"][0])))
    # print(request.session["labels"])
    # all_old_labels = []
    data = {
        "document": documenttext,
        "labels":labels,
        "explanation":explanation,
        "user_id":user_id,
        "document_id":document_id,
        "confidence" :confidence,
        "time":request.session["start_time"],
        "most_confident":most_confident,
        "all_old_labels": past_labels,
        "auto":"true",
        "start_time":request.session["start_time"]
        
        }

    return render(request, "label.html", context=data)



def skip_document(request):
    current_doc_id = request.POST.get('current_doc_id')

    return redirect('document_view')



def submit_data(request, document_id, label):
    time = datetime.datetime.now().strftime("%d/%m/%y %H:%M:%S")
    # print(time)



    append_to_json_file(request.session["email"], label, document_id, time )

    with open('./annotator/static/users.json', "r") as user_file:
        name_string = user_file.read()
        information = json.loads(name_string)

    past_labels = list(set(information[request.session["email"]]["label"]))

    request.session["document_ids"].append(document_id)
    request.session["labels"].append(label)
    document_id = document_id
    user_id=request.session["user_id"]
    response_time = str(time)
    submit_document = url + "recommend_document"
    # print(label.split("divideHere"))
    finalLabel = "\n".join(word for word in label.split("divideHere") if word!="")
    
    print(finalLabel)
    data_to_submit = {
            "document_id": document_id,
            "label": finalLabel,
            "user_id": user_id,
            "response_time": response_time,
            "description": "no description",
    }

    # print(data_to_submit)
    response = requests.post(submit_document, json=data_to_submit).json()
    document_id = response["document_id"]


    # return redirect("fetch-data", user_id=user_id, document_id=document_id)
    all_old_labels = sorted(list(past_labels))

    
    data = get_document_data(url=url, user_id=user_id, document_id=document_id, all_texts=all_texts, old_label=label, all_old_labels=all_old_labels)


    return JsonResponse(data)


def fetch_data(request, user_id, document_id):
    with open('./annotator/static/users.json', "r") as user_file:
        name_string = user_file.read()
        information = json.loads(name_string)

    past_labels = list(set(information[request.session["email"]]["label"]))
    all_old_labels = sorted(list(past_labels))


    data = get_document_data(url=url, user_id=user_id, document_id=document_id, all_texts=all_texts, all_old_labels=all_old_labels)
    return JsonResponse(data)

def skip_document(request):
    next_document_link = url + "/skip_document" 
        
    response = requests.post(next_document_link, json={
                            "user_id": request.session["user_id"]
                            }).json()
    
    return JsonResponse({"document_id":response["document_id"]})

 
def labeled(request):

    data = {

        'status':"200: SUCCESS",
        "data": "data"
    }
    return JsonResponse(data)




def get_all_documents(request ):
 
    data = {"document_ids": request.session["document_ids"][::-1],
            "labels": request.session["labels"][0][::-1]}
    print(data["document_ids"])
    return JsonResponse(data)
    

def logout_view(request):
    with open('./annotator/static/users.json', "r") as user_file:
        name_string = user_file.read()
        information = json.loads(name_string)
    information[request.session["email"]]["logoutTime"] = datetime.datetime.now().strftime("%d/%m/%y %H:%M:%S")

    
    logout(request)
    return redirect('login')  

def display (request, user_id):
    response = requests.post(url+"/display", json={
    "user_id":request.session["user_id"]}).json()
    print(response)

    all_items = []
    all_labelled_data = {}

    for id, items in response.items():
        all_items.append(flatten_extend(items))
        all_labelled_data[id] = flatten_extend(items)
    labeled_texts = flatten_extend(all_items)
    
    all_text = sort_labeled(all_texts, labeled_texts)
    print(all_text)

    remainingDocuments = [x for x in list(all_texts['text'].keys()) if x not in labeled_texts]
    document_id = random.choice(remainingDocuments)

    data = {
        "all_texts":all_text,
        "labels":all_labelled_data,
        "user_id": request.session["user_id"],
        "start_time": request.session["start_time"],
        "document_id":document_id,
    }

    # return render(request, 'labeled.html', context=data)

    


    return render(request, "labeled.html", context=data)


def append_time(request, pageName):

    data = {
         "page":pageName,
         "time": datetime.datetime.now(eastern).strftime("%d/%m/%y %H:%M:%S")
    }

    with open('./annotator/static/users.json', "r") as user_file:
        name_string = user_file.read()
        information = json.loads(name_string)
    information[request.session["email"]]["pageTimes"].append(data)

    with open("./annotator/static/users.json", "w") as user_file:
                json.dump(information, user_file, indent=4)

    data = {
         "code" : 200,
         "status" : "Success"
    }
    return JsonResponse(data)


def relabel(request, document_id, given_label):
    
    get_document_information = url + "get_document_information"
    response = requests.post(get_document_information, json={ "document_id": document_id,
                                                        "user_id":request.session["user_id"]
                                                            }).json()
    # print(response.keys())
    documenttext = all_texts["text"][str(document_id)]
    original_labels = response["llm_labels"]
    most_confident = original_labels[0]
    labels = random.sample(original_labels, len(original_labels))

    explanation = response["description"]

    confidence = str(response["confident"]).lower()

#Take it off
###################################
    conf =random.randint(1, 1000)
    if conf%2 ==0:
        confidence="true"
    else:
        confidence="false"
##################################
        
    old_labels = request.session["labels"]
    if len(old_labels)==0:
        all_old_labels = []
    else:

        all_old_labels = sorted(list(set(request.session["labels"][0])))
    print(request.session["labels"])
    all_old_labels = []
    data = {
        "document": documenttext,
        "labels":labels,
        "explanation":explanation,
        "user_id":request.session["user_id"],
        "document_id":document_id,
        "confidence" :confidence,
        "time":request.session["start_time"],
        "most_confident":most_confident,
        "all_old_labels": all_old_labels,
        "auto":"true",
        "start_time":request.session["start_time"],
        "label":given_label,
        "relabel": "true"
        
        }

    return render(request, "label.html", context=data)

def log_hover(request, document_id, hover_time):
    with open('./annotator/static/users.json', "r") as user_file:
        name_string = user_file.read()
        information = json.loads(name_string)
    information[request.session["email"]]["hoverTimes"].append({"document_id": document_id, 
                                                                "hover_time": hover_time})
    
    with open("./annotator/static/users.json", "w") as user_file:
                json.dump(information, user_file, indent=4)

    return JsonResponse({
        "code": 200,
        "msg": "SUCCESS"
    })



