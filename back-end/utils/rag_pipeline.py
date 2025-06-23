from utils.data_indexing_pipeline import generate_gemini_embedding, generate_sparse_embedding, create_qdrant_client
from qdrant_client import models
from config import settings
import google.generativeai as genai
from qdrant_client import QdrantClient

genai.configure(api_key=settings.GEMINI_KEY)
QDRANT_STORAGE_PATH = "./qdrant_storage"

def hybrid_search(query: str, collection_name: str, top_k: int = 5, dense_weight: float = 0.7, sparse_weight: float = 0.3):

    try:
        query_dense_embedding = generate_gemini_embedding(query)
        query_sparse_embedding = generate_sparse_embedding(query)
        qdrant_client = QdrantClient(url="http://127.0.0.1:6333", prefer_grpc=False)

        points, _ = qdrant_client.scroll(
            collection_name=collection_name,
            limit=5,
            with_payload=True,
            with_vectors=False 
        )
        print(points,"This is test whether vector database is populated or not")
        
        dense_results = qdrant_client.search(
            collection_name=collection_name,
            query_vector=models.NamedVector(
                name="dense_vectors",
                vector=query_dense_embedding
            ),
            limit=top_k * 2,
            with_payload=True,
            with_vectors=False
        )
        print(f"Dense results: {dense_results}")
        # Perform sparse vector search
        sparse_results = qdrant_client.search(
            collection_name=collection_name,
            query_vector=models.NamedSparseVector(
                name="sparse_vectors",
                vector=query_sparse_embedding
            ),
            limit=top_k * 2,  
            with_payload=True,
            with_vectors=False
        )
        print(f"Sparse results: {sparse_results}")
        
        combined_results = {}
        
        for result in dense_results:
            doc_id = result.id
            combined_results[doc_id] = {
                'dense_score': result.score * dense_weight,
                'sparse_score': 0.0,
                'payload': result.payload,
                'id': result.id
            }

        for result in sparse_results:
            doc_id = result.id
            if doc_id in combined_results:
                combined_results[doc_id]['sparse_score'] = result.score * sparse_weight
            else:
                combined_results[doc_id] = {
                    'dense_score': 0.0,
                    'sparse_score': result.score * sparse_weight,
                    'payload': result.payload,
                    'id': result.id
                }
        print(f"Combined results: {combined_results}")
        final_results = []
        for doc_id, data in combined_results.items():
            final_score = data['dense_score'] + data['sparse_score']
            
            class HybridResult:
                def __init__(self, id, score, payload):
                    self.id = id
                    self.score = score
                    self.payload = payload
            
            final_results.append(HybridResult(doc_id, final_score, data['payload']))
        
        final_results.sort(key=lambda x: x.score, reverse=True)
        print(f"Final sorted results: {final_results}")
        return final_results[:top_k]
        
    except Exception as e:
        print(f"Error during hybrid search: {e}")
        return []


def prompt_expansion(query: str, chat_history: list):
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        prompt = f"""
        Based on the following chat history, please expand the user's query to include more context.
        
        Chat History:
        {chat_history}
        
        User's Query: {query}
        
        Expanded Query:
        """
        
        response = model.generate_content(prompt)
        expanded_query = response.text.strip()
        return expanded_query
        
    except Exception as e:
        print(f"Error generating expanded query with Gemini: {e}")
        expanded_query = f"Error generating expanded query: {e}"
        return query

def create_chat_name(chat_history: list):
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        prompt = f"""
        Based on the following chat history, Please provide a title to the conversation that's taking place. The conversation name should no longer than 5 words.
        No additional information is needed, just the conversation name
        
        Chat History:
        {chat_history}
        
        
        chat_name:
        """
        
        response = model.generate_content(prompt)
        expanded_query = response.text.strip()
        return expanded_query
        
    except Exception as e:
        print(f"Error generating expanded query with Gemini: {e}")
        expanded_query = f"Error generating expanded query: {e}"
        return "New Chat"

def query_with_gemini_generation(query: str, collection_name: str, top_k: int = 3, 
                                dense_weight: float = 0.7, sparse_weight: float = 0.3):
    print(f"Querying with Gemini: {query}")
    search_results = hybrid_search(query, collection_name, top_k, dense_weight, sparse_weight)
    print(f"Search results: {search_results}")
    
    context_texts = []
    retrieved_docs = []
    
    for result in search_results:
        context_texts.append(result.payload["text"])
    
    context = "\n\n".join(context_texts)
    

    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        prompt = f"""
        Based on the following context information, please answer the user's question.
        If the answer cannot be found in the context, please say so.
        
        Context:
        {context}
        
        Question: {query}
        
        Answer:
        """
        
        response = model.generate_content(prompt)
        generated_response = response.text
        print(f"Generated response: {generated_response}")
        
    except Exception as e:
        print(f"Error generating response with Gemini: {e}")
        generated_response = f"Error generating response: {e}"
    
    return {
        "query": query,
        "retrieved_documents": retrieved_docs,
        "generated_response": generated_response
    }
    
def query_with_gemini_generation_stream(query: str, collection_name: str, top_k: int = 3, 
                                      dense_weight: float = 0.7, sparse_weight: float = 0.3):
    """Generator function that yields streaming response chunks."""
    print(f"Querying with Gemini (streaming): {query}")
    
    try:
        # Get search results (same as before)
        search_results = hybrid_search(query, collection_name, top_k, dense_weight, sparse_weight)
        print(f"Search results: {search_results}")
        
        context_texts = []
        for result in search_results:
            context_texts.append(result.payload["text"])
        
        context = "\n\n".join(context_texts)
        
        # Generate streaming response
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        prompt = f"""
        Based on the following context information, please answer the user's question.
        If the answer cannot be found in the context, please say so.
        
        Context:
        {context}
        
        Question: {query}
        
        Answer:
        """
        
        # Use streaming generation
        response = model.generate_content(prompt, stream=True)
        
        for chunk in response:
            if chunk.text:
                yield {
                    "content": chunk.text,
                    "type": "content",
                    "done": False
                }
        
        # Send completion signal
        yield {
            "content": "",
            "type": "done", 
            "done": True
        }
        
    except Exception as e:
        print(f"Error generating streaming response with Gemini: {e}")
        yield {
            "content": f"Error generating response: {e}",
            "type": "error",
            "done": True
        }