import json

from flask import request, Response
from flask_restful import Resource
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from constants import SLACK_API_TOKEN
from helper import extract_text_from_pdf, extract_summary, write_summary_to_file, get_answers_from_llm, post_to_slack

# Initialize Slack client with token
slack_client = WebClient(token=SLACK_API_TOKEN)


class UploadPdf(Resource):
    """
    Flask-Restful Resource for handling PDF uploads.
    """

    def post(self):
        """
        Handles POST requests to upload a PDF, extract text, summarize it, and save the summary.
        """
        # Retrieve file from the request
        file = request.files.get('file')

        # Validate file
        if not file or file.filename == '':
            return Response(json.dumps({"error": "No selected file"}), status=400)

        if not file.filename.endswith('.pdf'):
            return Response(json.dumps({"error": "Invalid file type. Only PDF is supported."}), status=400)

        # Extract text from the PDF file
        extracted_text = extract_text_from_pdf(file)
        if extracted_text is None:
            return Response(json.dumps({"error": "Failed to extract text from PDF"}), status=500)

        # Generate a summary of the extracted text
        extracted_summary = extract_summary(extracted_text)
        if extracted_summary is None:
            return Response(json.dumps({"error": "Something went wrong, please try again later!"}), status=500)

        # Write the summary to a file
        if not write_summary_to_file(extracted_summary):
            return Response(json.dumps({"error": "Something went wrong, please try again later!"}), status=500)

        return Response(json.dumps({"message": "File processed successfully"}), status=200)


class AskQuestion(Resource):
    """
    Flask-Restful Resource for handling questions based on uploaded PDF summaries.
    """

    def post(self):
        """
        Handles POST requests to answer questions based on the summarized text from the uploaded PDF.
        """
        # Retrieve questions from the request
        params = request.get_json()
        questions = params.get('questions')

        # Validate questions input
        if not questions:
            return Response(json.dumps({"error": "No questions provided"}), status=400)

        # Get answers from LLM based on summarized text
        answers = get_answers_from_llm(questions)

        try:
            # Post answers to Slack
            post_to_slack(slack_client, answers)
        except SlackApiError as e:
            print(f"Slack API error: {e.response['error']}")

        return Response(json.dumps({"message": "Questions answered and sent to Slack", "answers": answers}), status=200)
