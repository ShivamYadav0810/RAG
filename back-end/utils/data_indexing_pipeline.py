import os
import google.generativeai as genai
from qdrant_client import QdrantClient, models
from langchain.text_splitter import RecursiveCharacterTextSplitter
from fastembed import SparseTextEmbedding
import warnings
from config import settings
from PyPDF2 import PdfReader
from bs4 import BeautifulSoup
import uuid
from crud.upload import FileCrud
from tqdm import tqdm

warnings.filterwarnings("ignore")
genai.configure(api_key=settings.GEMINI_KEY)


# instead of QdrantClient(path=...)
qdrant_client = QdrantClient(url="http://127.0.0.1:6333", prefer_grpc=False)


sparse_embed_model = SparseTextEmbedding(model_name=settings.SPARSE_EMBEDDING_MODEL)
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separators=["\n\n", "\n", " ", ""]
)
dense_vector_size = 768

def create_qdrant_client(collection_name: str):
    """Creates a Qdrant client for the specified collection."""
    try:
        print(f"Creating Qdrant client for collection: {collection_name}")
        qdrant_client.recreate_collection(
            collection_name=collection_name,
            vectors_config={
                "dense_vectors": models.VectorParams(size=dense_vector_size, distance=models.Distance.COSINE)
            },
            sparse_vectors_config={
                "sparse_vectors": models.SparseVectorParams(
                    index=models.SparseIndexParams(on_disk=True)
                )
            }
        )
        return qdrant_client
    except Exception as e:
        print(f"Error adding data to vector store: {e}")
        return None


def generate_gemini_embedding(text: str, model_name: str = settings.GEMINI_EMBEDDING_MODEL):
    """Generates a dense embedding for the given text using the Gemini API."""
    try:
        response = genai.embed_content(
            model=model_name,
            content=text,
            task_type="RETRIEVAL_DOCUMENT"
        )
        return response['embedding']
    except Exception as e:
        print(f"Error generating Gemini embedding: {e}")
        return None

def generate_sparse_embedding(text: str):
    """Generates a sparse embedding for the given text using fastembed (BM25)."""
    try:
        sparse_embedding_generator = sparse_embed_model.embed(text)
        sparse_embedding_list = list(sparse_embedding_generator)

        sparse_embedding_object = sparse_embedding_list[0]

        return models.SparseVector(
            indices=sparse_embedding_object.indices.tolist(),
            values=sparse_embedding_object.values.tolist()
        )
    except Exception as e:
        print(f"Error generating sparse embedding: {e}")
        return None

def extract_text_from_pdf(file_path):
    """Extracts text from a PDF file."""
    try:   
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""

def extract_text_from_html(file_path):
    """Extracts text from an HTML file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            
            soup = BeautifulSoup(file, 'html.parser')
            text = soup.get_text(separator=' ', strip=True)
            return text
    except Exception as e:
        print(f"Error extracting text from HTML: {e}")
        return ""


def extract_text(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.pdf':
        return extract_text_from_pdf(file_path)
    elif ext in ['.html', '.htm']:
        return extract_text_from_html(file_path)
    else:
        raise ValueError("Unsupported file type")

def add_data_to_vector_store(user_id: str) -> bool:
    try:
        chunks = []
        collection_name = f"{user_id}_collection"
        files = FileCrud.get_files_by_userid(user_id=user_id)
        for file in files:
            print(f"Going through file {file}")
            file_id = file[0]
            file_name = file[2]
            
            file_path = os.path.join(settings.UPLOAD_DIR, user_id, file_name)
            content = extract_text(file_path)
           
            doc_chunks = text_splitter.split_text(content)
            print(f"Document chunks created with length {len(doc_chunks)}")
            for _, chunk in enumerate(doc_chunks):
                chunks.append({
                    "id": str(uuid.uuid4()),
                    "text": str(chunk),
                    "metadata": {"file_id": str(file_id), "user_id": str(user_id)}
                })
            print(f"Chunking completed with total chunks are {len(chunks)}")

        qdrant_client = create_qdrant_client(collection_name)
        print("Client created successfully")

        points_to_upsert = []
        for chunk in tqdm(chunks):
            dense_embedding = generate_gemini_embedding(chunk["text"])
            sparse_embedding = generate_sparse_embedding(chunk["text"])
            if dense_embedding and sparse_embedding:
                points_to_upsert.append(
                    models.PointStruct(
                        id=chunk["id"],
                        vector={
                            "dense_vectors": dense_embedding,
                            "sparse_vectors": sparse_embedding
                        },
                        payload={"text": chunk["text"], **chunk["metadata"]}
                    )
                )

        if points_to_upsert:
            try:
                print(f"Upserting data ")
                qdrant_client.upsert(
                    collection_name=collection_name,
                    wait=True,
                    points=points_to_upsert
                )
                print(f"Successfully upserted {len(points_to_upsert)} hybrid points into '{collection_name}'.")
            except Exception as e:
                print(f"Error upserting points: {e}")
        else:
            print("No embeddings generated to upsert.")
        
    except Exception as e:
        print(f"Error processing file: {e}")
        return False
    
