const user_id = document.getElementById("user_id").textContent;  
var document_id = document.getElementById("document_id").textContent; 
const manualLabelSubmit = document.getElementById('manualLabelSubmit');
const suggestedLabels = document.querySelectorAll('.suggested-label-btn');

toggleExplanationBtn.addEventListener('click', function() {
    if (explanationDiv.style.display === 'none') {
        explanationDiv.style.display = 'block';
        toggleExplanationBtn.textContent = 'Hide Explanation';
    } else {
        explanationDiv.style.display = 'none';
        toggleExplanationBtn.textContent = 'Show Explanation';
    }
});

var label;
console.log(document_id)




function sendData(label) {
    const dataToSend = JSON.stringify({
        message: "Hello, server! The timer is resuming.",
        time: new Date().toISOString()
    });
    
    url_base = "submit/";
    url = url_base+document_id+"/" +label+"/";

    fetch(url, {
        method: "POST",
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')  // Function to get CSRF token from cookies
        },
        body: dataToSend
    })
    .then(response => response.json())
    .then(data => {
        console.log('Success:', data);
        document.getElementById('document_id').textContent = data.document_id;
            document.getElementById('documentText').textContent = data.document;
            document.getElementById('explanationDiv').textContent = data.explanation;
            document.getElementById('user_id').textContent = data.user_id;
        })
    .catch(error => console.error('Error:', error));
}

// Set up the buttons with event listeners
function setupButtons() {
    
    document.getElementById('manualLabelSubmit').addEventListener('click', sendData(document.getElementById("manualLabelInput").value));
   
}

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



suggestedLabels.forEach(button => {
    button.addEventListener('click', function() {
        sendData(this.textContent.trim());
    });
});

manualLabelSubmit.addEventListener('click', function() {
    const manualLabelInput = document.getElementById('manualLabelInput');
    sendData(manualLabelInput.value.trim());
    manualLabelInput.value = null;

});