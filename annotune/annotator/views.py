from django.shortcuts import render, redirect
import requests
import json
from .utils import *
from django.http import JsonResponse
from collections import OrderedDict


all_texts = json.load(open("/Users/danielstephens/Desktop/Annotune-v2/annotune/annotator/congressional_bill_train.json"))
url =  "http://127.0.0.1:1234/"


def sign_up(request):
    email=None
     
    if request.method == 'POST':
        with open('./annotator/static/users.json', "r") as user_file:
            name_string = user_file.read()
            information = json.loads(name_string)

        if email not in information.keys():
        
            # user = requests.post(url + "//create_user")
            # user_id = user.json()['user_id']
            first_name = request.POST['first_name']
            last_name = request.POST['last_name']
            email = request.POST['email']
            password = request.POST['password']

            user_information =  {"first_name": first_name,
                                "last_name": last_name,
                                # "user_id":user_id,
                                "email":email,
                                "password":password
                                }
            information[email]=user_information

            with open("./annotator/static/users.json", "w") as user_file:
                json.dump(information, user_file, indent=4)

        else:
            first_name = information["email"]["first_name"]
            last_name = information["email"]["last_name"]
                

            
        return render(request, "homepage.html")
    


    return render(request, "sign-up.html")

def login(request):

    if request.method == 'POST':
        email = request.POST['email']
         
    return render(request, "login.html")


def homepage(request):
    return render(request, "homepage.html")

def list_documents(request):

    get_topic_list = url + "//get_topic_list" 
        
    topics = requests.post(get_topic_list, json={
                            "user_id": 47,
                            }).json()

    recommended = int(topics["document_id"])

    keywords = topics["keywords"]
    

    return render(request, "documents.html", {"all_texts": all_texts["text"], "clusters": topics["cluster"], "keywords":keywords, "recommended_doc_id" :recommended})

def label (request):
    user_id = 47
    document_id = 10

    get_document_information = url + "get_document_information"
    response = requests.post(get_document_information, json={ "document_id": document_id,
                                                        "user_id":user_id
                                                         }).json()
    documenttext = all_texts["text"][str(5)]

    

    labels = response["llm_labels"]

    explanation = response["description"]


    data = {
        "document": documenttext,
        "labels":labels,
        "explanation":explanation,
        "user_id":user_id,
        "document_id":document_id
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


def skip_document(request):
    current_doc_id = request.POST.get('current_doc_id')
    # next_doc_id = get_next_recommended_document(current_doc_id)
    return redirect('document_view',)


    
    

def get_data(request):
    if request.method == 'POST':
    
        # print(data)  # Check what's being sent to the server
        documenttext = "This is a document"

        request.session["number"]+=1

        document_id = 1
        number = request.session["number"]

        label= "This is the label"

        explanation = "This is the explanation"+ str(number)
        data = {
        "document": documenttext,
        "label":label,
        "explanation":explanation,
        "number": number
        }


        return JsonResponse(data)
    return JsonResponse({'status': 'error'}, status=400)




# def submit_data(request, user_id, document_id, label):
#     print("post request received")
#     # if request.method == 'POST':
#     response_time = request.POST.get('response_time')

#     submit_document = url + "recommend_document"
#     response = requests.post(submit_document, json={
#         "document_id": document_id,
#         "label": label,
#         "user_id": user_id,
#         "response_time": response_time,
#         "description": "no description"
#     }).json()

#     print(document_id, label, user_id, response_time)

#     documenttext = response.get("documenttext", "Document text not available")
#     labels = response.get("llm_labels", [])
#     explanation = response.get("description", "No explanation available")

#     data = {
#         "document": documenttext,
#         "labels": labels,
#         "explanation": explanation,
#     }

#     return JsonResponse(data)
    # return JsonResponse({"error": "IInvalid request method"}, status=400)




def submit_data(request, document_id, label):


    document_id = document_id
    user_id=47
    response_time = "00:00:00"
    submit_document = url + "recommend_document"

    data_to_submit = {
            "document_id": document_id,
            "label": label,
            "user_id": user_id,
            "response_time": response_time,
            "description": "no description"
    }

    print(data_to_submit)
    response = requests.post(submit_document, json=data_to_submit).json()
    print(response)
    document_id = response["document_id"]

    get_document_information = url + "get_document_information"
    response = requests.post(get_document_information, json={ "document_id": document_id,
                                                        "user_id":user_id
                                                         }).json()
    documenttext = all_texts["text"][str(document_id)]

    labels = response["llm_labels"]

    explanation = response["description"]

    data = {
        "document": documenttext,
        "labels":labels,
        "explanation":explanation,
        "user_id":user_id,
        "document_id":document_id,
        }
    

    return JsonResponse(data)
    

   
def get_data(request):
    if request.method == 'POST':
    
        # print(data)  # Check what's being sent to the server
        documenttext = "This is a document"

        request.session["number"]+=1

        document_id = 1
        number = request.session["number"]

        label= "This is the label"

        explanation = "This is the explanation"+ str(number)
        data = {
        "document": documenttext,
        "label":label,
        "explanation":explanation,
        "number": number
        }

        


        return JsonResponse(data)
    return JsonResponse({'status': 'error'}, status=400)