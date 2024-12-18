# chatbot.py
import os
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
from agents import select_saying, synthesize_response, refine_prompt

os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Connect to Qdrant
client = QdrantClient(host="localhost", port=6333)

# Initialize Sentence Transformer model
embedder = SentenceTransformer('all-MiniLM-L6-v2')

# Collection name
collection_name = "imam_ali_sayings"

def create_collection():
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE)
    )
    print(f"Collection '{collection_name}' created successfully!", end="\n\n")

def insert_sayings(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            sayings = [line.strip() for line in f if line.strip()]
        
        embeddings = embedder.encode(sayings)
        
        points = [
            PointStruct(id=i, vector=emb.tolist(), payload={"text": text})
            for i, (emb, text) in enumerate(zip(embeddings, sayings))
        ]
        
        client.upsert(collection_name=collection_name, points=points)
        print(f"Inserted {len(sayings)} sayings into the collection.")
    except Exception as e:
        print(f"Error inserting sayings: {e}")

def search_sayings(query, top_k=3):
    query_vector = embedder.encode([query])[0].tolist()
    search_result = client.search(
        collection_name=collection_name,
        query_vector=query_vector,
        limit=top_k
    )
    
    retrieved_sayings = []
    for result in search_result:
        if result.payload:
            retrieved_sayings.append(result.payload['text'])
    return retrieved_sayings

def parse_saying(saying):
    point = saying.find('.')
    serial_no, saying = saying[:point], saying[point+2:]
    return serial_no, saying

def main(user_query):
    file_path = "files/peak-of-eloquence.txt"
    
    # Create collection and insert data if needed
    try:
        create_collection()
        insert_sayings(file_path)
    except:
        pass
    
    # Process the query
    refined_query = refine_prompt(user_query)
    sayings_list = search_sayings(refined_query)
    saying = select_saying(sayings_list, user_query)
    serial_no, saying = parse_saying(saying)
    response = synthesize_response(serial_no, saying, user_query)
    return response
    
