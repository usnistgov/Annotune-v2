document.addEventListener('DOMContentLoaded', function () {
    const confidence = document.getElementById('confidence').textContent.trim();
    const auto = document.getElementById('auto').textContent.trim();
    const manualLabelInput = document.getElementById('manualLabelInput');
    const manualLabelSubmit = document.getElementById('manualLabelSubmit');
    const userId = document.getElementById('user_id').textContent.trim();
    const domain = window.location.origin;
    const previousButton = document.getElementById('previousButton');
    const nextButton = document.getElementById('nextButton');

    let documentsData = [];
    let currentIndex = -1;

    console.log('User ID:', userId);
    console.log('Domain:', domain);

    // Function to add event listeners to suggested label buttons
    function addSuggestedLabelListeners() {
        document.querySelectorAll('.suggested-label-btn').forEach(button => {
            button.addEventListener('click', function () {
                manualLabelInput.value = this.textContent.trim();
            });
        });
    }

    addSuggestedLabelListeners();

    // // Toggle explanation
    // document.getElementById('toggleExplanationBtn').addEventListener('click', function () {
    //     const explanationDiv = document.getElementById('explanationDiv');
    //     if (explanationDiv.style.display === 'none') {
    //         explanationDiv.style.display = 'block';
    //         this.textContent = 'Hide Explanation';
    //     } else {
    //         explanationDiv.style.display = 'none';
    //         this.textContent = 'Show Explanation';
    //     }
    // });

    // Function to send data
    function sendData() {
        const documentId = document.getElementById('document_id').textContent.trim();
        const label = manualLabelInput.value.trim();
        const dataToSend = JSON.stringify({
            document_id: documentId,
            label: label,
            user_id: userId,
            response_time: new Date().toISOString()
        });

        fetch(`/submit/${documentId}/${label}/`, {
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
                // fadeOutIn(document.body);
                manualLabelInput.value = "";
            })
            .catch(error => console.error('Error:', error));
    }

    // Event listener for submit button
    manualLabelSubmit.addEventListener('click', sendData);

    // Function to get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // // Function to add fade transition
    // function fadeOutIn(element) {
    //     element.classList.add('fade');
    //     setTimeout(() => {
    //         element.classList.remove('fade');
    //     }, 1000);
    // }

    // Function to load document based on current index
    function loadDocument(index) {
        const documentData = documentsData[index];
        console.log('Loading document:', documentData);
        fetch(`/fetch_data/${userId}/${documentData.id}/`)
            .then(response => response.json())
            .then(data => {
                updatePage(data);
            })
            .catch(error => console.error('Error fetching document:', error));
    }

    function updatePage(data) {
        document.getElementById('document_id').textContent = data.document_id;
        document.getElementById('documentText').textContent = data.document;
        document.getElementById('most_confident').textContent = data.most_confident;

        const suggestedLabelsContainer = document.getElementById('suggestedLabels');
        suggestedLabelsContainer.innerHTML = '';
        console.log(data.labels)
        data.labels.forEach(label => {
            const button = document.createElement('button');
            button.id = label;
            button.type = 'button';
            button.className = 'btn btn-label suggested-label-btn m-1';
            button.textContent = label;
            suggestedLabelsContainer.appendChild(button);
        });

        // Add event listeners to the newly created buttons
        addSuggestedLabelListeners();
    }

    // Event listener for the previous button
    previousButton.addEventListener('click', function (event) {
        event.preventDefault();

        fetch('/get_all_documents/')
            .then(response => response.json())
            .then(data => {
                documentsData = data.document_ids.map((id, index) => {
                    return { id: id, label: data.labels[index] };
                });

                // Load the previous document
                if (currentIndex < documentsData.length - 1) {
                    currentIndex++;
                    console.log('Current Index (Previous):', currentIndex);
                    loadDocument(currentIndex);
                }
            })
            .catch(error => console.error('Error fetching documents data:', error));
    });

    // Event listener for the next button
    nextButton.addEventListener('click', function (event) {
        event.preventDefault();

        if (currentIndex > 0) {
            currentIndex--;
            console.log('Current Index (Next):', currentIndex);
            loadDocument(currentIndex);
        } else {
            // No next document, call skip_document view
            fetch('/skip_document/')
                .then(response => response.json())
                .then(data => {
                    console.log(data.document_id)
                    currentIndex =  - 1;
                    // loadDocument(currentIndex);
                    console.log(currentIndex)
                    console.log(userId)
                    const url = `/fetch_data/${userId}/${data.document_id}/`;
    
                    fetch(url)
                        .then(response => response.json())
                        .then(data => {
                            updatePage(data);
            })
            .catch(error => console.error('Error fetching document:', error));

        })

    }});


});
