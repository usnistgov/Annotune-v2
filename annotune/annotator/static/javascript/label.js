document.addEventListener('DOMContentLoaded', () => {
    const confidence = document.getElementById('confidence');
    const manualLabelInput = document.getElementById('manualLabelInput');
    const manualLabelSubmit = document.getElementById('manualLabelSubmit');
    const userId = document.getElementById('user_id').textContent.trim();
    const domain = window.location.origin;
    const previousButton = document.getElementById('previousButton');
    const nextButton = document.getElementById('nextButton');
    const alertDiv = document.getElementById('myalert');
    const loaderOverlay = document.getElementById('loaderOverlay');
    const datalistElement = document.getElementById('labelOptions');

    let documentsData = [];
    let currentIndex = -1;

    

    console.log('User ID:', userId);
    console.log('Domain:', domain);

    function addSuggestedLabelListeners() {
        document.querySelectorAll('.suggested-label-btn').forEach(button => {
            button.addEventListener('click', () => {
                manualLabelInput.value = button.textContent.trim();
            });
        });
    }

    addSuggestedLabelListeners();

    function sendData() {
        const documentId = document.getElementById('document_id').textContent.trim();
        var label =getInputValue();
        // console.log(label[0])
        var descriptionData = document.getElementById("textArea").value;
        console.log(descriptionData)
        removeInputs();

        const dataToSend = JSON.stringify({
            document_id: documentId,
            label: label,
            description : descriptionData, 
            user_id: userId,
            response_time: new Date().toISOString()
        });
        // console.log(dataToSend);

        showLoader();

        fetch(`/submit/${documentId}/${label[0]}/`, {
            method: "POST",
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: dataToSend
        })
            .then(response => response.json())
            .then(data => {
                console.log('Success:', data);
                updatePage(data);
                // console.log(data)
                showAlert(`${data.old_label[0].toUpperCase()} was submitted successfully`);
                hideLoader();
            })
            .catch(error => console.error('Error:', error));
    }

    manualLabelSubmit.addEventListener('click', sendData);

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie) {
            const cookies = document.cookie.split(';');
            for (let cookie of cookies) {
                cookie = cookie.trim();
                if (cookie.startsWith(`${name}=`)) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function loadDocument(index) {
        const documentData = documentsData[index];
        fetch(`/fetch_data/${userId}/${documentData.id}/`)
            .then(response => response.json())
            .then(data => {
                updatePage(data);
                showAlert(`You are viewing document ${data.document_id}`);
            })
            .catch(error => console.error('Error fetching document:', error));
    }

    function updatePage(data) {
        document.getElementById('document_id').textContent = data.document_id;
        document.getElementById('documentText').textContent = data.document;
        document.getElementById('most_confident').textContent = data.most_confident;
        document.getElementById('explanationDiv').textContent = data.explanation;
        
        confidence.textContent = data.confidence;
        manualLabelInput.value = "";
        const newOptions = data.all_old_labels;
        // console.log(newOptions)
        // Clear existing options
        datalistElement.innerHTML = '';

        // Add new options
        newOptions.forEach(optionValue => {
            const newOption = document.createElement('option');
            newOption.value = optionValue;
            datalistElement.appendChild(newOption);
        });


        ['redArrow', 'labelEnter', 'greenArrow', 'submitEnter'].forEach(id => {
            const element = document.getElementById(id);
            if (element) element.style.display = 'none';
        });

        manualLabelSubmit.classList.remove('highlight-green');
        manualLabelInput.classList.remove('highlight');
        confidenceDetector(data.confidence, data.most_confident);

        const suggestedLabelsContainer = document.getElementById('suggestedLabels');
        suggestedLabelsContainer.innerHTML = '';
        // document.getElementById("textarea-container").click()


        data.labels.forEach(label => {
            const button = document.createElement('button');
            button.id = label;
            button.type = 'button';
            button.className = 'btn btn-label suggested-label-btn m-1';
            button.textContent = label;
            suggestedLabelsContainer.appendChild(button);
        });

        addSuggestedLabelListeners();
        toggleSubmitButton();

        // Attach the function to the document's click and input events
        $("#textarea-container").hide();
        // Optionally clear the text area
        $("#textarea-container textarea").val('');
    }

    previousButton.addEventListener('click', event => {
        event.preventDefault();

        fetch('/get_all_documents/')
            .then(response => response.json())
            .then(data => {
                documentsData = data.document_ids.map((id, index) => ({ id, label: data.labels[index] }));

                if (currentIndex < documentsData.length - 1) {
                    currentIndex++;
                    loadDocument(currentIndex);
                }
            })
            .catch(error => console.error('Error fetching documents data:', error));
    });

    nextButton.addEventListener('click', event => {
        event.preventDefault();

        if (currentIndex > 0) {
            currentIndex--;
            loadDocument(currentIndex);
        } else {
            fetch('/skip_document/')
                .then(response => response.json())
                .then(data => {
                    currentIndex = -1;
                    const url = `/fetch_data/${userId}/${data.document_id}/`;

                    fetch(url)
                        .then(response => response.json())
                        .then(data => {
                            updatePage(data);
                            showAlert('You skipped the previous document');
                        })
                        .catch(error => console.error('Error fetching document:', error));
                });
        }
    });

    function showAlert(message) {
        alertDiv.style.display = 'flex';
        alertDiv.textContent = message;
        setTimeout(() => {
            alertDiv.style.display = 'none';
        }, 3000);
    }

    function hideLoader() {
        loaderOverlay.style.display = 'none';
    }

    function showLoader() {
        loaderOverlay.style.display = 'flex';
        window.addEventListener('load', hideLoader);
    }

    hideLoader();

    function confidenceDetector(confidence, mostConf) {
        if (confidence.textContent == "true") {
            document.getElementById('greenArrow').style.display = 'block';
            document.getElementById('submitEnter').style.display = 'block';
            manualLabelSubmit.classList.add('highlight-green');
            manualLabelInput.value = mostConf;
            document.getElementById("confText").innerText = `The model recommends ${mostConf} as the most relevant label. Please submit the label ${mostConf} or choose from the existing labels or create your own label`;
        } else {
            document.getElementById('redArrow').style.display = 'block';
            document.getElementById('labelEnter').style.display = 'block';
            manualLabelInput.classList.add('highlight');
            document.getElementById("confText").innerText = "The model needs your help on choosing from the label suggestions, the existing labels or you can create your own label";
        }
    }

    confidenceDetector(confidence, document.getElementById('most_confident').textContent);
    
    function removeInputs(){
        var inputContainer = document.getElementById('inputContainer');
        var inputTexts = inputContainer.getElementsByClassName("input-group mb-3 label-input-group");
        var inputNumber = inputTexts.length;
            // Click the button three times with a small delay between each click
        for (let i = 0; i < inputNumber-1; i++) {
            document.getElementById('removeInput').click();
        }
    
        
    }

    function getInputValue(){
        // Select all input elements with the class "input-group mb-3 label-input-group"
        let inputs = document.querySelectorAll('.input-group.mb-3.label-input-group input');
        // Initialize an array to store the text values
        let texts = [];
        let final_label = []

        // Iterate through each input element and get its value
        inputs.forEach(input => {
            texts.push(input.value);
            final_label.push(input.value);
        });
        // Log the collected text values
        // console.log(texts);

        return  final_label
    }
    toggleSubmitButton()

    // Function to enable or disable the submit button based on input value
    function toggleSubmitButton() {
        var inputField = document.getElementById('manualLabelInput');
        var submitButton = document.getElementById('manualLabelSubmit');

        if (inputField.value.trim() === "") {
            submitButton.disabled = true;
        } else {
            submitButton.disabled = false;
        }
    }


    // Attach the function to the document's click and input events
    document.addEventListener('input', toggleSubmitButton);
    document.addEventListener('click', toggleSubmitButton);


    

            

        

        
    
    


});
