import os
from azure.identity import DefaultAzureCredential
from langchain_openai import AzureChatOpenAI
import openai
import json
import requests

import re
import fitz  # PyMuPDF
import requests

# Set the OpenAI API environment variables
os.environ["OPENAI_API_TYPE"] = "azure_ad"
os.environ["AZURE_OPENAI_ENDPOINT"] = "https://{your-custom-endpoint}.openai.azure.com/"
os.environ["AZURE_DEPLOYMENT"] = "o4-mini-3"
os.environ["OPENAI_API_VERSION"] = "2024-12-01-preview"

DEPLOYMENT_NAME = os.environ["AZURE_DEPLOYMENT"]  # Your deployed OpenAI model name

credential = DefaultAzureCredential()
# or openai.api_key = "YOUR_API_KEY"   # Replace with your OpenAI key

# Define a function that retrieves an access token (Code will change as per the authentication method)
def get_azure_token():
    token = credential.get_token("https://cognitiveservices.azure.com/.default")
    return token.token  # Return only the access token string

client = openai.AzureOpenAI(
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_version=os.environ["OPENAI_API_VERSION"],
    azure_ad_token_provider=get_azure_token,  # Use managed identity authentication
)


# --- Step 1: Math Tool ---
def is_math_query(query):
    # Normalize
    q = query.lower().strip()
    q = q.replace("x", "*").replace("×", "*").replace("divide", "/").replace("multiplied by", "*")
    
    # Look for math keywords or patterns
    math_patterns = [
        r'what is [0-9\+\-\*/x÷ ]+\??',
        r'^[0-9\+\-\*/ ().]+$',
        r'[0-9]+ (plus|minus|times|divided by) [0-9]+'
    ]
    for pat in math_patterns:
        if re.search(pat, q):
            return True
    return False

def solve_math(query):
    try:
        # Normalize operators
        expr = query.lower()
        expr = expr.replace("what is", "").replace("?", "").replace("x", "*").replace("×", "*")
        expr = expr.replace("plus", "+").replace("minus", "-")
        expr = expr.replace("times", "*").replace("divided by", "/")
        return eval(expr.strip())
    except Exception as e:
        return f"Error solving math: {e}"

# --- Step 2: PDF Understanding Tool ---
def search_pdf(query, pdf_path="sample.pdf"):
    doc = fitz.open(pdf_path)
    text_chunks = []
    for page in doc:
        text_chunks.append(page.get_text())
    all_text = " ".join(text_chunks)

    # Ask LLM to answer from PDF text
    response = client.chat.completions.create(
        model= DEPLOYMENT_NAME,
        messages=[
            {"role": "system", "content": "You are a helpful assistant that answers based only on the provided PDF text. "
            "If answer is not found, give me result as 'No relevant information found.'."},
            {"role": "user", "content": f"PDF Content: {all_text[:50000]}\n\nQuestion: {query}\n\nAnswer from PDF in your own words:"}
        ]
    )
    return response.choices[0].message.content

# --- Step 3: Web Search Tool ---
def web_search(query):

    # you can alternatively use google search API, if you have a key for it
    url = f"https://api.duckduckgo.com/?q={query}&format=json"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    data = response.json()
    top_results = data.get("AbstractText", "No results found.")

    if not top_results:
        return "No web results."

    # Summarize using LLM
    response = client.chat.completions.create(
        model= DEPLOYMENT_NAME,
        messages=[
            {"role": "system", "content": "You are a helpful AI agent that summarizes search results."},
            {"role": "user", "content": f"Summarize this for the question '{query}': {top_results}"}
        ]
    )
    return response.choices[0].message.content

# --- Step 4: AI Agent Controller ---
def ai_agent(query, pdf_path="sample.pdf"):
    if is_math_query(query):
        return f"Answer (Math): {solve_math(query)}"
    
    pdf_answer = search_pdf(query, pdf_path)
    if pdf_answer and "No relevant information found." not in pdf_answer:
        return f"Answer (PDF): {pdf_answer}"
    
    return f"Answer (Web): {web_search(query)}"

# --- Run Agent ---
if __name__ == "__main__":
    query = input("Ask me anything: ")
    answer = ai_agent(query, pdf_path="sample.pdf")
    print(answer)
