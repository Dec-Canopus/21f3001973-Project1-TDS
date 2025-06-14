import chromadb
import json
import base64
import requests
from io import BytesIO
from PIL import Image
import torch
import re
import numpy as np
from transformers import CLIPProcessor, CLIPModel


# Reference: https://medium.com/thedeephub/building-clip-model-from-scratch-using-pytorch-contrastive-learning-image-pretraining-4cac7c298586
class CLIPEmbedClient:
    def __init__(self, model_name="openai/clip-vit-base-patch32"):  ## need this model for image embedding
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = CLIPModel.from_pretrained(model_name).to(self.device)
        self.processor = CLIPProcessor.from_pretrained(model_name, use_fast=False)

    ## Reference: https://huggingface.co/docs/transformers/model_doc/clip#transformers.CLIPModel

    def _encode_text(self, texts):
        inputs = self.processor(text=texts, return_tensors="pt", padding=True, truncation=True)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        with torch.no_grad():
            return self.model.get_text_features(**inputs).cpu().numpy()

    def _encode_image(self, image: Image.Image):
        inputs = self.processor(images=image, return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        with torch.no_grad():
            return self.model.get_image_features(**inputs).cpu().numpy()
    
    def __call__(self, input: str) -> np.ndarray:
        return self._encode_text([input])[0] if isinstance(input, str) else self._encode_image(input) if isinstance(input, Image.Image) else None
    
class VectorDatabase:
    def __init__(self, json_file: str = "articles_rag.json", db_path: str = "vector_db"):
        self.json_file = json_file
        self.db_path = db_path
        self.new_client = False

        ## Intialize the vector database
        self.client = chromadb.PersistentClient(path=db_path)
        self.embedder = CLIPEmbedClient()
        self.collection = self._initialize_collection()
        print(f"Initialized vector database at {db_path}")
        if self.collection and self.new_client:
            self._load_json_data()
            self.add_documents()

    def _load_json_data(self):
        with open(self.json_file, "r", encoding="utf-8") as f:
            self.documents = json.load(f)
        print(f"Loaded {len(self.documents)} documents from {self.json_file}")

    def _initialize_collection(self):
        try:
            client_temp = self.client.create_collection(
                name="articles",
                embedding_function=None
            )
            self.new_client = True
            return client_temp
        except Exception as e:
            self.new_client = False
            ## should be called when vector_store is initialized twice (should not happen for this project)
            print(f"Cannot create collection: {e}")
            return self.client.get_collection(name="articles")

    # def _extract_image_urls(self, content):
    #     return [url for url in content.split() if url.lower().endswith((".jpg", ".jpeg", ".png")) and url.lower().startswith(("http"))]

    # def _fetch_image_embedding(self, url):
    #     try:
    #         response = requests.get(url, timeout=10)
    #         img = Image.open(BytesIO(response.content)).convert("RGB")
    #         return self.embedder._encode_image(img)
    #     except Exception:
    #         return None

    # def _remove_urls(self, content):
    #     unwanted_url_pattern = r'https?://[^\s]+'
    #     content = re.sub(unwanted_url_pattern, '', content)
    #     content = re.sub(r'\s+', ' ', content).strip()
        
    #     return content

    def add_documents(self):
        # count = 0
        all_docs = [doc["content"] for doc in self.documents]
        print(f"Added docs to the vector database.")
        all_ids = [str(doc["id"]) for doc in self.documents]
        print(f"Added ids to the vector database.")
        all_urls=[doc["url"] for doc in self.documents]
        print(f"Added urls to the vector database.")
        all_embeddings = self.embedder._encode_text(all_docs)
        print(f"Added embeddings to the vector database.")

        self.collection.add(
                documents=all_docs,
                ids=all_ids,
                metadatas= [{"url": url} for url in all_urls],
                embeddings=all_embeddings.tolist()
            )
        print(f"Added {len(all_ids)} documents to the vector database.")
            # content = self._remove_urls(document["content"])
            

            # if image_embeddings:
            #     # this make combined embedded weight from text 50% and image 50%
            #     image_embeddings = np.vstack(image_embeddings) 
            #     avg_image_embedding = image_embeddings.mean(axis=0)
            #     combined_embedding = (text_embedding + avg_image_embedding) / 2
            # else:
            #     combined_embedding = text_embedding
            # # print(text_embedding)
            # # print(image_embeddings)
            # print(combined_embedding)


    def search(self, question, base64_img=None, n_results=3):

        text_emb = self.embedder._encode_text([question])[0]
        # print(question)
        results = self.collection.query(query_embeddings=[text_emb], n_results=n_results)
        return [
            {
                "id": id,
                "text": text,
                "distance": distance,
                "url": metadata["url"]
            }
            for id, text, distance, metadata in zip(results["ids"][0], results["documents"][0], results["distances"][0], results["metadatas"][0])
        ]

    def get_document_by_id(self, id: str):
        return self.collection.get(ids=[id])

# def main():
#     vector_db = VectorDatabase()
#     vector_db.add_documents()

    # query = input("Enter your search query: ")
    # results = vector_db.search_similar(query, n_results=3)
    # print(f"Search Results for '{query}':")
    # for result in results:
    #     print(f"ID: {result['id']}, Title: {result['metadata']['title']}, URL: {result['metadata']['url']}, Distance: {result['distance']}")

    # doc_id = results[0]['id']
    # doc = vector_db.get_document_by_id(doc_id)
    # print(f"\nFetched Document by ID {doc_id}:")
    # print(doc)


# if __name__ == "__main__":
#     main()