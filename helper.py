import os
from concurrent.futures import ThreadPoolExecutor, as_completed

from openai import OpenAI
from PyPDF2 import PdfReader
import tiktoken
from slack_sdk.errors import SlackApiError

from constants import OPENAI_KEY

# Initialize OpenAI client with API key
client = OpenAI(api_key=OPENAI_KEY)


def extract_text_from_pdf(file):
    """
    Extracts text from a PDF file using PyPDF2.

    Args:
        file: File object representing the uploaded PDF.

    Returns:
        str: Extracted text from the PDF.
    """
    try:
        # Initialize PdfReader object from the file stream
        reader = PdfReader(file.stream)
        text = ""

        # Extract text from each page
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return None


def read_summary_from_file():
    """
    Reads the summary from the saved text file.

    Returns:
        str: Summary text.
    """
    try:
        text_file = os.path.join(os.path.dirname(__file__), 'extracted_summary.txt')
        with open(text_file, 'r') as file:
            return file.read()
    except Exception as e:
        print(f"Error reading summary from file: {e}")
        return None


def split_text_into_chunks(text, max_tokens_per_chunk=7000):
    """
    Splits text into chunks to ensure it meets token limits for GPT-4.

    Args:
        text (str): Text to split.
        max_tokens_per_chunk (int): Maximum number of tokens per chunk.

    Returns:
        list: List of text chunks.
    """
    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(text)
    chunks = []
    current_chunk = []

    for token in tokens:
        current_chunk.append(token)
        if len(current_chunk) >= max_tokens_per_chunk:
            chunks.append(encoding.decode(current_chunk))
            current_chunk = []

    if current_chunk:
        chunks.append(encoding.decode(current_chunk))

    return chunks


def summarize_text(text, max_output_tokens=1500):
    """
    Summarizes text using GPT-4.

    Args:
        text (str): Text to summarize.
        max_output_tokens (int): Maximum tokens for the output summary.

    Returns:
        str: Summary of the text.
    """
    try:
        response = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=[{"role": "user", "content": f"Summarize the following text: {text}"}],
            max_tokens=max_output_tokens,
            temperature=0.5
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error summarizing text: {e}")
        return None


def extract_summary(extracted_text):
    """
    Extracts a summary from the given text by summarizing chunks and combining them.

    Args:
        extracted_text (str): Text extracted from PDF.

    Returns:
        str: Final summarized text.
    """
    # Split text into chunks
    chunks = split_text_into_chunks(extracted_text)

    # Summarize each chunk concurrently
    summaries = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        future_to_chunk = {executor.submit(summarize_text, chunk): chunk for chunk in chunks}
        for future in as_completed(future_to_chunk):
            summaries.append(future.result())

    # Combine all summaries into a single text
    combined_summary = " ".join(summaries)

    # If combined summary is too long, summarize again
    if len(tiktoken.get_encoding("cl100k_base").encode(combined_summary)) > 7000:
        return summarize_text(combined_summary)

    return combined_summary


def get_answers_from_llm(questions):
    """
    Retrieves answers from OpenAI's LLM based on summarized text and provided questions.

    Args:
        questions (list): List of questions to answer.

    Returns:
        list: List of dictionaries containing question and answer pairs.
    """
    try:
        summarized_text = read_summary_from_file()
        if not summarized_text:
            return [{"question": q, "answer": "Data Not Available"} for q in questions]

        answers = []

        for question in questions:
            prompt = (
                f"Based on the following text:\n{summarized_text}\n\n"
                f"Answer the question: {question}"
            )

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150
            )

            answer = response.choices[0].message.content.strip()

            if not answer or len(answer.split()) < 3:  # Assume low confidence
                answer = "Data Not Available"

            answers.append({"question": question, "answer": answer})

        return answers
    except Exception as e:
        print(f"Error getting answers: {e}")
        return []


def write_summary_to_file(extracted_summary):
    """
    Writes the extracted summary to a text file.

    Args:
        extracted_summary (str): The summary to write.

    Returns:
        bool: True if writing was successful, False otherwise.
    """
    try:
        text_file = os.path.join(os.path.dirname(__file__), 'extracted_summary.txt')
        with open(text_file, 'w') as file:
            file.write(extracted_summary)
        return True
    except Exception as e:
        print(f"Error writing summary to file: {e}")
        return False


def post_to_slack(slack_client, answers):
    """
    Posts the answers to a specified Slack channel.

    Args:
        slack_client: Initialized Slack WebClient.
        answers (list): List of answers to post.

    Returns:
        response: Slack API response.
    """
    channel_id = "#your-slack-channel"  # Replace with your Slack channel ID
    message = "\n".join([f"Q: {item['question']} A: {item['answer']}" for item in answers])

    try:
        response = slack_client.chat_postMessage(
            channel=channel_id,
            text=message
        )
        return response
    except SlackApiError as e:
        print(f"Failed to post to Slack: {e.response['error']}")
        return None
