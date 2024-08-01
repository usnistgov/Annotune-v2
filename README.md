# Annotune - Annotation, Text Understanding, and Navigation Engine

Annotune is a web application for labeling documents and providing explanations using Large Language Models (LLMs). The application allows users to upload documents, receive suggested labels, manually add labels, and get explanations for the labeled documents. Users can also skip documents they do not wish to label.

## Table of Contents

- [Features](#features)
- [Technologies Used](#technologies-used)
- [Installation](#installation)
- [Usage](#usage)
- [Endpoints](#endpoints)
- [Contributing](#contributing)
- [License](#license)

## Features

- Receive LLM suggested labels for documents.
- Manually input and submit labels.
- View explanations for labeled documents.
- Skip documents and move to the next recommended document.
- View labeled documents
## Technologies Used

- Python
- Django
- HTML/CSS (Bootstrap)
- JavaScript

## Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/yourusername/annotune.git
    cd annotune
    ```

2. **Create a virtual environment and activate it:**

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. **Install the required packages:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Set up the database:**

    ```bash
    python manage.py migrate
    ```


5. **Create a superuser:**

    ```bash
    python manage.py createsuperuser
    ```

7. **Set environment variables:**
    ``` bash
    Create a .env file in the root directory and set the environment variables
    ALLOW_HOST=
    URL=
    DATAPATH=
    USERS_PATH=
    STATIC_ROOT=

    ```

6. **Run the development server:**

    ```bash
    python manage.py runserver
    ```

## Usage

1. **Access the application:**
   
    Open your web browser and navigate to `http://127.0.0.1:8000`.

2. **Upload a document:**

    Use the upload form to submit a document. The document will be displayed, and you will receive LLM suggested labels.

3. **Label a document:**

    - Click on a suggested label to submit it.
    - Enter a label manually and click the "Submit" button to add it.

4. **View explanation:**

    Click the "Show Explanation" button to toggle the explanation for the labeled document.

5. **Skip a document:**

    Click the "Skip" button to move to the next recommended document.

## Endpoints

- `GET /`: Home page to upload and label documents.
- `POST /submit/<int:user_id>/<int:document_id>/<str:label>/`: Endpoint to submit a label for a document.
- `POST /skip/`: Endpoint to skip a document and move to the next one.

## Contributing

1. **Fork the repository.**
2. **Create a new branch:**

    ```bash
    git checkout -b feature/your-feature-name
    ```

3. **Make your changes and commit them:**

    ```bash
    git commit -m 'Add some feature'
    ```

4. **Push to the branch:**

    ```bash
    git push origin feature/your-feature-name
    ```

5. **Create a pull request.**

## License

This project is licensed under the NIST License. See the [LICENSE](LICENSE) file for details.
