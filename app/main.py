from fastapi import FastAPI, UploadFile, HTTPException, Request
from fastapi.responses import HTMLResponse
import markdown
import os
import httpx
import json
from pydantic import BaseModel
from io import BytesIO
from PIL import Image
import base64
from dotenv import load_dotenv
from vectore_store import VectorDatabase


# Model for AI response
class AIResponse(BaseModel):
    class Link(BaseModel):
        url: str
        text: str
    answer: str
    links: list[Link]


# Model for user request
class UserRequest(BaseModel):
    question: str
    image: str = None
    link: str = None


# Utility function to convert image to base64
def image_to_base64(image_file: UploadFile) -> str:
    image = Image.open(image_file.file)
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


# FastAPI app initialization
def create_app():
    load_dotenv()  # Load environment variables from .env file
    app = FastAPI()

    # Initialize the VectorDatabase once
    vectordb = VectorDatabase(json_file="chunk.json")
    return app, vectordb


# Initialize FastAPI app and VectorDatabase instance
app, vectordb = create_app()


# API client function for OpenAI
async def call_aipipe_openai_api(payload: dict):
    AIPIPE_API_KEY = os.getenv("AIPIPE_API_KEY")
    headers = {
        "Authorization": f"Bearer {AIPIPE_API_KEY}",
        "Content-Type": "application/json",
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"https://aipipe.org/openai/v1/chat/completions",
            headers=headers,
            json=payload,
        )
    return response.json()


# Route to serve README content as HTML
@app.get("/", response_class=HTMLResponse)
async def read_readme():
    README_PATH = "../README.md"

    if os.path.exists(README_PATH):
        with open(README_PATH, "r", encoding="utf-8") as f:
            readme_content = f.read()

        html_content = markdown.markdown(readme_content)

        return f"""
        <html>
            <head><title>README</title></head>
            <body>
                <div style="max-width: 800px; margin: 0 auto;">
                    <h1>README</h1>
                    {html_content}
                </div>
            </body>
        </html>
        """
    return HTMLResponse(content="<h1>README.md file not found!</h1>", status_code=404)


# Route for handling the RAG (Retrieve and Generate) query
@app.post("/api/")
async def rag(request: UserRequest):
    body = json.loads(request.json())
    context = []
    retrieved_docs = []
    links = []

    if body.get("link"):
        retrieved_docs = vectordb.search(body["link"])

    if "question" not in body:
        raise HTTPException(status_code=400, detail="Question is required.")
    
    question = body["question"]
    if body.get("image"):
        image = image_to_base64(body["image"])
        retrieved_docs = vectordb.search(image) if not retrieved_docs else retrieved_docs + vectordb.search(image)

    retrieved_docs = vectordb.search(question) if not retrieved_docs else retrieved_docs + vectordb.search(question)
    retrieved_docs = sorted(retrieved_docs, key=lambda d: d.get('distance', float('inf')))
    retrieved_docs = retrieved_docs[:3] if len(retrieved_docs) == 3 else retrieved_docs[:4]

    for doc in retrieved_docs:
        context.append(doc['text'])
        links.append({"url": doc['url'], "text": doc['text']})

    context = "\n".join(context)
    links = links[:3]

    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "system",
                "content": "You are a Virtual Teaching Assistant (TA) for the Tools in Data Science (TDS) course at IIT Madras. Answer student questions clearly, concisely, factually and calculate if necessary. If the answer requires more information, mention that. "
            },
            {
                "role": "user",
                "content": f"""Use the following context to answer the question:

                    {context}

                    Question: {question}
                    Provide a concise answer, and use the context provided to support your response. If the answer requires more information, mention that. Use SPARTAN TONE.
                """
            }
        ]
    }

    result = await call_aipipe_openai_api(payload)
    raw_output = result["choices"][0]["message"]["content"]
    answer = raw_output.strip() if raw_output and raw_output.strip() else "No answer found."
    return {"answer": answer, "links": links}


# Run the app using Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
