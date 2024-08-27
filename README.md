# PDF Upload and Question Answering API

## Overview

This Flask application provides a simple RESTful API for uploading PDF files and asking questions about the content of those files. It utilizes OpenAI's GPT-4o-mini model to generate summaries and answer questions based on the extracted text from the PDFs. The application also integrates with Slack to post generated answers to a specified Slack channel.

## Features

- **PDF Upload**: Allows users to upload PDF files and extract text from them.
- **Text Summarization**: Summarizes the extracted text using OpenAI's GPT-4o-mini model.
- **Question Answering**: Accepts questions related to the uploaded PDF content and provides answers using OpenAI's GPT-4o-mini model.
- **Slack Integration**: Posts answers to a specified Slack channel.

## API Endpoints

### 1. Upload PDF

- **URL**: `/v1/upload/`
- **Method**: `POST`
- **Description**: Uploads a PDF file and extracts text from it.
- **Request**:
  - `file`: PDF file to be uploaded.
- **Response**:
  - `200 OK`: File uploaded successfully.
  - `400 Bad Request`: No file provided or invalid file type.
- **Example**:
  ```bash
  curl --location 'http://0.0.0.0:5000/v1/upload/' \
    --header 'Content-Type: multipart/form-data' \
    --form 'file=@"/Users/ma1568/Downloads/handbook.pdf"'

### 2. Ask Questions

- **URL**: `/v1/ask/`
- **Method**: `POST`
- **Description**: Accepts a list of questions related to the uploaded PDF content and returns answers.
- **Request**:
  - `questions`: JSON array of questions.
- **Response**:
  - `200 OK`: Answers processed successfully.
  - `400 Bad Request`: No questions provided.
  - `500 Internal Server Error`: Error posting answers to Slack.
- **Example**:
  ```bash
  curl --location 'http://0.0.0.0:5000/v1/ask/' \
    --header 'Content-Type: application/json' \
    --data '{
        "questions": ["What is the name of the company?", "Who is the CEO of the company?", "What is their vacation policy?", "What is the termination policy?"]
    }'
  

## Getting Started

### Prerequisites

- Python 3.7 or later
- `pip` (Python package manager)
- An OpenAI API key
- A Slack API token with permission to post messages

### Installation

1. **Clone the repository**:

    ```bash
    git clone https://github.com/your-username/your-repo-name.git
    cd your-repo-name
    ```

2. **Create and activate a virtual environment**:

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install the required packages**:

    ```bash
    pip install -r requirements.txt
    ```

4. **Set up environment variables**:

    Create a `.env` file in the project root directory and add the following:

    ```env
    OPENAI_KEY=your_openai_api_key
    SLACK_API_TOKEN=your_slack_api_token
    ```

### Running the Application

1. **Run the Flask application**:

    ```bash
    flask run
    ```

   The application will start on `http://127.0.0.1:5000`.

### Running Tests

To run the unit tests, execute:

```bash
python -m unittest test_cases.py
```

### Assumptions

1. User will provide valid PDF files for upload.
2. Questions will be provided in a JSON array format.
3. Slack integration is optional and can be configured based on the user's requirements.
