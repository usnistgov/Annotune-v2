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
from collections import defaultdict



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

            return redirect("pretext", user_id=information[email]["user_id"] )


         
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

    
    logout(request)
    return redirect('login')  


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
    

    
    response = { "drawing relations between mathematical concepts": {
                    "documents" : [1, 2, 3, 4, 5, 6, 7],
                    "description" : "drawing relations between mathematical concepts.This is the description"
                },
                "classroom management teaching": {
                "documents" : [11, 21, 31, 41, 51, 61, 71],
                "description" : "classroom management teaching.This is the description"
            }
        }
    # print(response.keys())
    


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
        question2 = request.POST['question2']
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


def post_text(request):
    with open(env("USERS_PATH"), "r") as user_file:
        name_string = user_file.read()
        information = json.loads(name_string)

    # print(all_texts)

    data = information[request.session["email"]]["labels"]

        # Preparing data structure for the dashboard
    dashboard_data = {
        "labels_counts": defaultdict(int),  # To count occurrences of each label
        "documents": []  # To hold document details
    }

    for doc_key, details in data.items():
        doc_id = details["document_id"]
        label = details["labels"]
        text = all_texts["text"].get(str(doc_id), "Text not available")  # Retrieve the text or default to a placeholder
        
        # Update label counts for the bar chart
        dashboard_data["labels_counts"][label] += 1
        
        # Add document details for the table
        dashboard_data["documents"].append({
            "document_id": doc_id,
            "labels": label,
            "text": text
        })

    # Convert the defaultdict to a regular dict before passing to JSON
    dashboard_data["labels_counts"] = dict(dashboard_data["labels_counts"])

    # Convert to JSON format to pass to JavaScript
    dashboard_json = json.dumps(dashboard_data)

    # Print or return the JSON structure (you might pass this to your template)
    # print(dashboard_json)

    return render(request, "post_test.html", {'dashboard_json': dashboard_json})