def submit_data(request, document_id, label):
    time = datetime.datetime.now().strftime("%d/%m/%y %H:%M:%S")

    if request.method == 'POST':

            data = json.loads(request.body)
            
            label = data.label
            description = data.description
            document_id = data.document_id
            response_time = str(data.response_time)
            user_id = request.session["user_id"]

            request.session["document_ids"].append(document_id)
            request.session["labels"].append(label[0])

            append_to_json_file(request.session["email"], label, document_id, time )


            with open(env("USERS_PATH"), "r") as user_file:
                name_string = user_file.read()
                information = json.loads(name_string)

            past_labels = list(set(information[request.session["email"]]["label"]))

            
            submit_document = url + "recommend_document"
            # print(label.split("divideHere"))
            finalLabel = "\n".join(word for word in label)
            
            print(finalLabel)
            data_to_submit = {
                    "document_id": document_id,
                    "label": finalLabel,
                    "user_id": user_id,
                    "response_time": response_time,
                    "description": description,
            }
            # print(data_to_submit)
            response = requests.post(submit_document, json=data_to_submit).json()
            document_id = response["document_id"]


            # return redirect("fetch-data", user_id=user_id, document_id=document_id)
            all_old_labels = sorted(list(past_labels))

            
            data = get_document_data(url=url, user_id=user_id, document_id=document_id, all_texts=all_texts, old_label=label, all_old_labels=all_old_labels)

            return JsonResponse(data, status=200)


    #     except:
    #         return JsonResponse({'error': 'Invalid JSON'}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=400)

    
    # print(time)




    

    # request.session["document_ids"].append(document_id)
    # request.session["labels"].append(label)
    # document_id = document_id
    # user_id=request.session["user_id"]
    # response_time = str(time)
        

    # submit_document = url + "recommend_document"
    # # print(label.split("divideHere"))
    # finalLabel = "\n".join(word for word in label.split("divideHere") if word!="")
    
    # print(finalLabel)
    # data_to_submit = {
    #         "document_id": document_id,
    #         "label": finalLabel,
    #         "user_id": user_id,
    #         "response_time": response_time,
    #         "description": "no description",
    # }

    # # print(data_to_submit)
    # response = requests.post(submit_document, json=data_to_submit).json()
    # document_id = response["document_id"]


    # # return redirect("fetch-data", user_id=user_id, document_id=document_id)
    # all_old_labels = sorted(list(past_labels))

    
    # data = get_document_data(url=url, user_id=user_id, document_id=document_id, all_texts=all_texts, old_label=label, all_old_labels=all_old_labels)


    # return JsonResponse(data)
