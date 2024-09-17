from django.shortcuts import render, redirect, HttpResponse
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
from collections import defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np




env = environ.Env()



 
all_texts = json.load(open(env("DATAPATH")))
url =  env("URL")
 
 
def sign_up(request):
    email=None
     
    if request.method == 'POST':
        with open(env("USERS_PATH"), "r") as user_file:
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
                                "hoverTimes":[],
                                "pretest":[],
                                "postTest":[],
    
                                }
            information[email]=user_information

            with open(env("USERS_PATH"), "w") as user_file:
                json.dump(information, user_file, indent=4)

            request.session["email"] = information[email]["email"]
            request.session["user_id"] = information[email]["user_id"]
            request.session["labels"] = information[email]["label"],
            request.session["document_ids"]= information[email]["document_id"]
            request.session["start_time"]= information[email]["start_time"]

            return redirect("pretext", user_id=information[email]["user_id"] )

        return redirect("login", {"time":datetime.datetime.now(eastern).strftime("%d/%m/%y %H:%M:%S")})
            
    return render(request, "sign-up.html", {"time":datetime.datetime.now(eastern).strftime("%d/%m/%y %H:%M:%S")})


def login(request):

    if request.method == 'POST':

        email = request.POST['email']
        with open(env('USERS_PATH'), "r") as user_file:
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

            return redirect("homepage", user_id=information[email]["user_id"])
    

         
    return render(request, "login.html")


def homepage(request, user_id):
    print(request.session["start_time"])
    return render(request, "homepage.html", {"user_id": request.session["user_id"], "start_time":request.session["start_time"]})

def list_documents(request, user_id, recommendation):
    request.session["isManual"]=False

    get_topic_list = url + "//get_topic_list" 
        
    topics = requests.post(get_topic_list, json={
                            "user_id": request.session["user_id"]
                            }).json()

    a, b, c, d = truncated_data(topics, all_texts)
    # print(b)

    print(type(request.session["user_id"]))
  

    return render(request, "documents.html", {"all_texts": a, "clusters": d, "keywords":b, "recommended_doc_id" :c, "user_id":request.session["user_id"], "start_time":request.session["start_time"], "recommendation": recommendation})


def label (request,user_id, document_id, recommendation):
    user_id = user_id
    

    get_document_information = url + "get_document_information"
    response = requests.post(get_document_information, json={ "document_id": document_id,
                                                        "user_id":user_id
                                                         }).json()
    # print(response.keys())
    documenttext = all_texts["text"][str(document_id)]

    with open(env("USERS_PATH"), "r") as user_file:
        name_string = user_file.read()
        information = json.loads(name_string)

    past_labels = list(set(information[request.session["email"]]["label"]))

    

    original_labels = response["llm_labels"]

    most_confident = original_labels[0]
    labels = random.sample(original_labels, len(original_labels))

    explanation = response["description"]

    confidence = str(response["confident"]).lower()


#     #Take it off
# ###################################
#     conf =random.randint(1, 1000)
#     if conf%2 ==0:
#         confidence="true"
#     else:
#         confidence="false"
# ################################## 

#     print(past_labels)
    
    # old_labels = request.session["labels"]
    # if len(old_labels)==0:
    #     all_old_labels = []
    # else:

    #     all_old_labels = sorted(list(set(request.session["labels"][0])))
    # print(request.session["labels"])
    # all_old_labels = []

    # documenttext = """teacher: All right. I heard lots of - wait. Let me stop the music. I heard lots of, "
    #                 That's the way it is." My question is, what is the relationship between this circle and this circle, and this circle?
    #                 Why? How? What is it? What is the relationship between all of them? Because this circle is really big, right, compared to this one.
    #                 Student C, tell me what you got.
    #                 <br>
    #                 <br>
    #                 student: It's always 3.14 because the circumference divided by the diameter equals pi.
    #                 <br><br>
    #                 teacher: The circumference divided by the diameter is always going to be pi. It doesn't matter how big or how small your circle is.
    #                 You can take any circle, measure the circumference, stretch it across the diameter, and it's always going to be 3.14. Student A?"""


    data = {
        "document": documenttext,
        "labels":labels,
        "explanation":explanation,
        "user_id":user_id,
        "document_id":document_id,
        "confidence" :confidence,
        "time":datetime.datetime.now(eastern).strftime("%d/%m/%y %H:%M:%S"),
        "most_confident":most_confident,
        "all_old_labels": past_labels,
        "auto":None,
        "start_time":request.session["start_time"],
        "recommendation": recommendation
        
        }

    return render(request, "label.html", context=data)



def skip_document(request):
    current_doc_id = request.POST.get('current_doc_id')

    return redirect('document_view')



def submit_data(request, document_id, label):
    time = datetime.datetime.now().strftime("%d/%m/%y %H:%M:%S")

    if request.method == 'POST':
            
        # try:
        data = json.loads(request.body)
        label = data["label"]
        description = data["description"]
        document_id = int(data["document_id"])
        response_time = str(data["response_time"])
        manualStatus = str(data["manualStatus"])
        user_id = request.session["user_id"]
        pageTime = str(data["pageTime"])
        print(pageTime)

        request.session["document_ids"].append(document_id)
        request.session["labels"].append(label[0])

        append_to_json_file(request.session["email"], label[0], document_id, time, pageTime)


        with open(env("USERS_PATH"), "r") as user_file:
            name_string = user_file.read()
            information = json.loads(name_string)

        past_labels = list(set(information[request.session["email"]]["label"]))

        if request.session["isManual"]==False:

            submit_document = url + "recommend_document"

            finalLabel = "\n".join(word for word in label)
        
        

            data_to_submit = {
                "document_id": document_id,
                "label": finalLabel,
                "user_id": user_id,
                "response_time": response_time,
                "description": description,
            }

            response = requests.post(submit_document, json=data_to_submit).json()
            document_id = response["document_id"]

        else:
            labeledDocuments = list(set(information[request.session["email"]]["document_id"]))
            remainingDocuments = [x for x in list(all_texts['text'].keys()) if int(x) not in labeledDocuments]
            
            

           
            if document_id not in remainingDocuments:
                document_id = random.choice(remainingDocuments)

        
        all_old_labels = sorted(list(past_labels))
        # print("allllllllll", all_old_labels)
        

        if manualStatus == "true":

            text = all_texts["text"][str(document_id)]
            
            data = {
                "all_old_labels": all_old_labels,
                "document":text,
                "document_id": document_id,
                "old_label": label[0]
                
            }
            
        else:
            
            data = get_document_data(url=url, user_id=user_id, document_id=document_id, all_texts=all_texts, old_label=label, all_old_labels=all_old_labels)
            
        return JsonResponse(data, status=200)


        # except:
        #     return JsonResponse({'error': 'Invalid JSON'}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=400)




def fetch_data(request, user_id, document_id):
    with open(env("USERS_PATH"), "r") as user_file:
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

 
# def labeled(request):

#     data = {

#         'status':"200: SUCCESS",
#         "data": "data"
#     }
#     return JsonResponse(data)




def get_all_documents(request ):
 
    data = {"document_ids": request.session["document_ids"][::-1],
            "labels": request.session["labels"][0][::-1]}
    print(data["document_ids"])

    return JsonResponse(data)
    

def logout_view(request):
    with open(env("USERS_PATH"), "r") as user_file:
        name_string = user_file.read()
        information = json.loads(name_string)
    information[request.session["email"]]["logoutTime"] = datetime.datetime.now().strftime("%d/%m/%y %H:%M:%S")

    
    # logout(request)



    return redirect('post-test')  


def display(request, user_id, recommendation):

    # response = requests.post(url+"/display", json={
    # "user_id":request.session["user_id"]}).json()
 
    # response = { "between the": {
    #                 "documents" : [1, 2, 3, 4, 5, 6, 7],
    #                 "description" : "drawing relations between mathematical concepts.This is the description"
    #             },
    #             "label2": {
    #             "documents" : [11, 21, 31, 41, 51, 61, 71],
    #             "description" : "This is the description"
    #         }
    #     }
    
    # Sanitize the response keys to replace spaces with underscores
    

    
    response = { "med arithmetic concepts": {'description': 'Dummy description', 'documents': [24, 60, 191, 193, 212, 263]}, 
                "classroom management teaching": {
                "documents" : [11, 21, 31, 41, 51, 61, 71],
                "description" : "classroom management teaching.This is the description"
            }
        }
    # print(response.keys())
    # response = {'med:_arithmetic_concepts': {'description': 'Dummy description', 'documents': [24, 60, 191, 193, 212, 263]}, 
    #             'med:_comparing_and_ordering_decimals': {'description': 'Dummy description', 'documents': [8, 9, 10, 14, 26, 30, 40, 42, 45, 47, 56, 57, 59, 62, 71, 76, 92, 98, 99, 100, 101, 112, 118, 130, 131, 155, 157, 158, 164, 167, 175, 179, 181, 202, 205, 206, 207, 208, 210, 211, 218, 225, 226, 227, 230, 241, 242, 243, 247, 249, 257, 267, 271, 276, 279, 281, 291, 292, 293, 295, 297]}, 
    #             'med:_mathematical_concepts': {'description': 'Dummy description', 'documents': [3, 61, 83, 90, 96, 125, 176, 200, 221, 253, 261, 265, 270, 282]}, 
    #             'pos:_interactive_problemsolving_in_math': {'description': 'Dummy description', 'documents': [34, 70, 79, 91]}}


    response = {label.replace(' ', '_'): value for label, value in response.items()}
    all_items1 = []

    for id, items in response.items():
        all_items1.append(items["documents"])

    labeled_texts1 = flatten_extend(all_items1)

    all_text1 = sort_labeled(all_texts, labeled_texts1)

    # all_items = []
    # all_labelled_data = {}





    # for id, items in response.items():
    #     all_items.append(flatten_extend(items))

    #     all_labelled_data[id] = {"documents":flatten_extend(items),
    #                              "description": "this is a description"}
    # labeled_texts = flatten_extend(all_items)
    # all_text = sort_labeled(all_texts, labeled_texts)


    remainingDocuments = [x for x in list(all_texts['text'].keys()) if x not in labeled_texts1]
    document_id = random.choice(remainingDocuments)

    # print(all_text[""]) 
    # print(all_labelled_data.keys())



    data = {
        "all_texts":all_text1,
        "labels": response,
        "user_id": request.session["user_id"],
        "start_time": request.session["start_time"],
        "document_id":document_id,
        "recommendation":recommendation
    }

    # return render(request, 'labeled.html', context=data)

    return render(request, "labeled.html", context=data)




def append_time(request, pageName):
    response = requests.post(url+"/display", json={
    "user_id":request.session["user_id"]}).json()



    data = {
         "page":pageName,
         "time": datetime.datetime.now(eastern).strftime("%d/%m/%y %H:%M:%S")
    }

    with open(env("USERS_PATH"), "r") as user_file:
        name_string = user_file.read()
        information = json.loads(name_string)
    information[request.session["email"]]["pageTimes"].append(data)

    with open(env("USERS_PATH"), "w") as user_file:
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
    # conf =random.randint(1, 1000)
    # if conf%2 ==0:
    #     confidence="true"
    # else:
    #     confidence="false"
##################################
    
    # confidence="true"
    
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
    with open(env("USERS_PATH"), "r") as user_file:
        name_string = user_file.read()
        information = json.loads(name_string)
    information[request.session["email"]]["hoverTimes"].append({"document_id": document_id, 
                                                                "hover_time": hover_time})
    
    with open(env("USERS_PATH"), "w") as user_file:
                json.dump(information, user_file, indent=4)

    return JsonResponse({
        "code": 200,
        "msg": "SUCCESS"
    })

def manualDocumentsList(request, user_id):
    request.session["isManual"]=True

    with open(env("USERS_PATH"), "r") as user_file:
        name_string = user_file.read()
        information = json.loads(name_string)

    labeledDocuments = list(set(information[request.session["email"]]["document_id"]))
    # remainingDocuments = [x for x in list(all_texts['text'].keys()) if int(x) not in labeledDocuments]
    remaining_texts = all_texts["text"]
    
    remaining_texts = {k: v for k, v in remaining_texts.items() if int(k) not in labeledDocuments}

    return render(request, "manualText.html", context={"all_texts":remaining_texts, "user_id": user_id, "start_time": str(request.session["start_time"])})


def manualLabeledList(request, user_id):
    request.session["isManual"]=True

    with open(env("USERS_PATH"), "r") as user_file:
        name_string = user_file.read()
        information = json.loads(name_string)

    all_labelled_data = get_all_labeled(request.session["email"])
    aaaa = list(set(information[request.session["email"]]["document_id"]))

    all_text  = sort_labeled(all_texts, aaaa)
    # print(all_labelled_data)
    
    data = {
        "all_texts":all_text,
        "labels":all_labelled_data,
        "user_id": request.session["user_id"],
        "start_time": request.session["start_time"],
    }

    return render(request, 'manualLabeledList.html', context=data)



    # return render(request, "manualLabeledList.html", context={"all_texts":remaining_texts, "user_id": user_id, "start_time": str(request.session["start_time"])})



def manualLabel(request, user_id, document_id):
    text = all_texts["text"][str(document_id)]
    with open(env("USERS_PATH"), "r") as user_file:
        name_string = user_file.read()
        information = json.loads(name_string)

    past_labels = list(set(information[request.session["email"]]["label"]))

    
    data = {
        "document": text,
        "user_id":user_id,
        "document_id":document_id,
        "time":request.session["start_time"],
        "all_old_labels": past_labels,
        "start_time":request.session["start_time"]
        
        }
    


    return render(request, "manualLabel.html", context=data)


def pre_text(request, user_id):
    # Define the path to the JSON file
    json_file_path = '/Users/danielstephens/Desktop/Annotune-v2/user_data/try.json'

    if request.method == 'POST':
        # Get form data
        question1 = request.POST['question1']
        question2 = request.POST['likert']
        # Add other questions if there are more

        # Structure the data as a dictionary
        user_data = {
            "responses": {
                "question1": question1,
                "question2": question2,
                # Add other questions if necessary
            }
        }

        with open(env("USERS_PATH"), "r") as user_file:
            name_string = user_file.read()
            information = json.loads(name_string)
            information[request.session["email"]]["pretest"]=user_data
        
        with open(env("USERS_PATH"), "w") as user_file:
                json.dump(information, user_file, indent=4)
        # # Check if the file exists, and if it does, read the existing data
        # if os.path.exists(json_file_path):
        #     with open(json_file_path, 'r') as file:
        #         existing_data = json.load(file)
        # print(user_data)
        # else:
        #     existing_data = {}

        # Update the existing data with the new user's data
        # existing_data[user_id] = user_data

        # # Write the updated data back to the JSON file
        # with open(json_file_path, 'w') as file:
        #     json.dump(existing_data, file, indent=4)

        # Redirect or render a success page if needed
        return render(request, "homepage.html", context={"user_id": user_id, "start_time": request.session["start_time"]})

    # If the request method is GET, simply render the form
    return render(request, "questions.html", context={"user_id": user_id})



import json
from sklearn.feature_extraction.text import TfidfVectorizer
from django.shortcuts import render, redirect
from django.http import JsonResponse

def post_text(request):
    response = {
    "first label": {
        "documents": [45, 123, 67, 512, 298],
        "description": "My name is Sara Elizabeth Porter. I can recite the periodic table from memory and can play 4 musical instruments."
    },
    "second label": {
        "documents": [312, 199, 87, 405, 678, 223, 501],
        "description": "My name is Jacob Alexander Lee. I can solve a Rubik's cube in under 30 seconds and have visited 23 countries."
    },
    "third label": {
        "documents": [59, 376, 287, 13, 105, 498, 42, 610],
        "description": "My name is Emily Grace Thompson. I am fluent in 3 languages and have a black belt in Taekwondo."
    },
    "fourth label": {
        "documents": [92, 201, 64, 321],
        "description": "My name is Matthew Oliver Davis. I have completed 5 marathons and I’m an expert in wildlife photography."
    },
    "fifth label": {
        "documents": [152, 89, 403, 56, 487, 310, 641],
        "description": "My name is Abigail Charlotte Evans. I know all the flags of the world and can bake 50 different types of cakes."
    },
    "sixth label": {
        "documents": [304, 75, 17, 423, 401, 214],
        "description": "My name is Ethan Michael Harris. I can code in 7 programming languages and have published 3 research papers."
    },
    "seventh label": {
        "documents": [12, 207, 333, 441, 561],
        "description": "My name is Sophia Isabella King. I’ve visited 30 national parks and I’m an amateur astronomer with my own telescope."
    },
    "eighth label": {
        "documents": [77, 213, 487, 134, 256, 361, 488, 105, 699],
        "description": "My name is Lucas Benjamin Wright. I have a collection of over 500 comic books and can play chess blindfolded."
    },
    "ninth label": {
        "documents": [122, 400, 502, 623],
        "description": "My name is Ava Sophia Carter. I’m a certified scuba diver and know the history of all major world civilizations."
    },
    "tenth label": {
        "documents": [321, 210, 157, 441, 97, 510],
        "description": "My name is James William Clark. I can juggle 5 balls and have hiked the tallest peaks on 4 different continents."
    },
    "eleventh label": {
        "documents": [333, 198, 246, 411, 500, 321, 590],
        "description": "My name is Olivia Grace Johnson. I can solve complex math problems in my head and I’ve painted over 100 portraits."
    },
    "twelfth label": {
        "documents": [17, 250, 92, 105, 367, 199, 43, 120, 552],
        "description": "My name is Alexander Noah Parker. I have memorized every Shakespeare play and I can run a mile in under 6 minutes."
    },
    "thirteenth label": {
        "documents": [301, 412, 58, 92, 612, 241],
        "description": "My name is Emily Claire Bennett. I have a pilot’s license and I can write backwards with both hands."
    },
    "fourteenth label": {
        "documents": [52, 321, 299, 450, 89, 313],
        "description": "My name is Benjamin David Moore. I’ve competed in international chess tournaments and can make pottery."
    },
    "fifteenth label": {
        "documents": [201, 177, 98, 301, 505, 476],
        "description": "My name is Charlotte Rose Foster. I’ve worked as a lifeguard and I can draw hyperrealistic portraits."
    },
    "sixteenth label": {
        "documents": [95, 134, 217, 378, 523],
        "description": "My name is Jackson Daniel Miller. I can surf big waves and have studied marine biology."
    },
    "seventeenth label": {
        "documents": [210, 431, 56, 194, 87, 642],
        "description": "My name is Grace Olivia Ward. I’m an experienced mountain climber and know sign language."
    },
    "eighteenth label": {
        "documents": [77, 256, 341, 411],
        "description": "My name is Noah Samuel Stewart. I can solve complex physics problems and know advanced origami."
    },
    "nineteenth label": {
        "documents": [399, 125, 78, 503],
        "description": "My name is Mia Scarlett Turner. I’ve performed on Broadway and I’m a certified yoga instructor."
    },
    "twentieth label": {
        "documents": [134, 231, 487, 310, 650],
        "description": "My name is William Michael Carter. I can play 5 different sports and have written a novel."
    },
    "twenty-first label": {
        "documents": [204, 98, 51, 354],
        "description": "My name is Isabella Evelyn Adams. I’m a skilled photographer and have backpacked across 10 countries."
    },
    "twenty-second label": {
        "documents": [389, 47, 205, 660],
        "description": "My name is Henry Jacob Brooks. I’ve built my own computer and I’m a professional video game player."
    },
    "twenty-third label": {
        "documents": [309, 156, 99, 413, 589],
        "description": "My name is Amelia Rose Bailey. I’ve competed in national debates and I’m an expert on ancient mythology."
    },
    "twenty-fourth label": {
        "documents": [201, 78, 432, 513],
        "description": "My name is Mason Alexander Ross. I can play 6 musical instruments and have published a poetry book."
    },
    "twenty-fifth label": {
        "documents": [412, 222, 134, 508],
        "description": "My name is Harper Lily Cooper. I’ve studied neuroscience and can sculpt miniature figures."
    },
    "twenty-sixth label": {
        "documents": [312, 199, 451, 603, 243],
        "description": "My name is Samuel Ryan Lee. I have a black belt in Karate and I’m a professional photographer."
    },
    "twenty-seventh label": {
        "documents": [99, 304, 157, 641],
        "description": "My name is Ella Claire Kelly. I can play chess at a national level and have won photography contests."
    },
    "twenty-eighth label": {
        "documents": [400, 213, 98, 540],
        "description": "My name is Lucas Oliver Phillips. I’m an expert drone pilot and have traveled to 18 countries."
    },
    "twenty-ninth label": {
        "documents": [256, 103, 87, 604, 399],
        "description": "My name is Avery Sophia Murphy. I’m a certified scuba diver and I’ve run 3 marathons."
    },
    "thirtieth label": {
        "documents": [321, 189, 210, 556],
        "description": "My name is Logan Alexander Scott. I can play 4 musical instruments and am a professional skateboarder."
    },
    "thirty-first label": {
        "documents": [134, 258, 99, 500, 621],
        "description": "My name is Chloe Grace Richardson. I’ve studied paleontology and I’m an expert in 3D modeling."
    },
    "thirty-second label": {
        "documents": [450, 210, 57, 611, 442],
        "description": "My name is Elijah Michael Mitchell. I’ve completed 3 triathlons and have designed my own clothing line."
    },
    "thirty-third label": {
        "documents": [388, 187, 42, 521],
        "description": "My name is Sophie Elizabeth Hernandez. I can speak 4 languages and I’m a skilled equestrian."
    },
    "thirty-fourth label": {
        "documents": [223, 459, 176, 606],
        "description": "My name is Jackson William Foster. I’ve competed in fencing tournaments and am a robotics enthusiast."
    },
    "thirty-fifth label": {
        "documents": [321, 148, 70, 509, 666],
        "description": "My name is Ella Mia Lopez. I’m a professional ballet dancer and have written a book on nutrition."
    },
    "thirty-sixth label": {
        "documents": [125, 299, 458, 511],
        "description": "My name is Ethan Andrew Howard. I’ve built a 3D printer and have won national science competitions."
    },
    "thirty-seventh label": {
        "documents": [201, 77, 389, 564],
        "description": "My name is Lillian Grace Young. I’m a professional violinist and I’ve studied ancient Greek history."
    },
    "thirty-eighth label": {
        "documents": [451, 243, 310, 642, 215],
        "description": "My name is Lucas James Sullivan. I’m an avid rock climber and have trained as a stunt performer."
    },
    "thirty-ninth label": {
        "documents": [129, 501, 220, 334],
        "description": "My name is Avery Lily Edwards. I’m an expert cook and I’ve traveled to 15 different national parks."
    },
    "fortieth label": {
        "documents": [504, 156, 602, 78],
        "description": "My name is Olivia Sophie Carter. I’ve painted over 50 landscapes and can knit intricate patterns."
    }
}



    # Load all texts (document data from the file)
    all_texts = json.load(open(env("DATAPATH")))

    # Filter documents from the all_texts using the document ids from response
    combined_documents = [str(doc) for item in response.values() for doc in item['documents']]
    filtered_texts = {doc_id: all_texts["text"][doc_id] for doc_id in combined_documents if doc_id in all_texts["text"]}

    # Prepare structured data with labels, texts, and descriptions
    structured_data = {}
    descriptions = {}
    for label, details in response.items():
        description = details.get('description', 'No description available')

        descriptions[label]=description
        for doc_id in details['documents']:
            doc_id_str = str(doc_id)
            text = filtered_texts.get(doc_id_str, "Text not available")
            structured_data[doc_id_str] = {
                "text": text,
                "label": label,
            }


    # Prepare texts for TF-IDF vectorization
    document_ids = list(filtered_texts.keys())
    document_texts = list(filtered_texts.values())

    # Perform TF-IDF vectorization using scikit-learn
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(document_texts)
    feature_names = vectorizer.get_feature_names_out()

    # Convert TF-IDF matrix to dictionary structure for frontend
    tfidf_data = {}
    for i, doc_id in enumerate(document_ids):
        tfidf_data[doc_id] = {feature_names[j]: tfidf_matrix[i, j] for j in range(len(feature_names)) if tfidf_matrix[i, j] > 0}

    # Convert the structured data and TF-IDF data to JSON format
    dashboard_data = json.dumps(structured_data, indent=4)
    tfidf_json = json.dumps(tfidf_data, indent=4)
    

    if request.method == 'POST':
        # Handle form submission
        question1 = request.POST["question1"]
        question2 = request.POST["likert"]

        # Simulate storing user data (adjust as per your logic)
        user_data = {"responses": {"question1": question1, "question2": question2}}
        print(user_data)
        
        # Save data (adjust the path and method as needed)
        with open(env("USERS_PATH"), "r") as user_file:
            information = json.load(user_file)
            information[request.session["email"]]["postTest"] = user_data

        # Logout and redirect after submission
        logout(request)
        return redirect("thankYou")

    # Pass structured data and TF-IDF to the template
    return render(request, "post_test.html", {
        'dashboard_json': dashboard_data,
        'tfidf_json': tfidf_json,
        "user_id": request.session.get("user_id"),
        "descriptions": json.dumps(descriptions, indent=4)
    })


def thankYou(request):
    logout(request)
    
    # Clear the session explicitly
    # request.session.flush()

    return render(request, "thankYou.html")






    # return render(request, "post_test.html",context=context)

    # return HttpResponse("amen")

