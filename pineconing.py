from pinecone import Pinecone, ServerlessSpec

import json
import re
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

class VectorDB:
    
    """
    Initiates a pinecone index and embeddings:
    self.index
    self.embedding_model
    """
    def __init__(self):

        # Load environment variables from .env
        load_dotenv(override=True)

        """
        Index for SentenceTransformer embeddings: "umdsustainabilitychatbot"
        - dimension: 384

        Index for GoogleGenerativeAI embeddings (from langchain_google_genai): "umdsustainabilitychatbot2" - USE THIS
        - dimension: 768
        """
        pc = Pinecone()
        index_name = "umdsustainabilitychatbot2"
        existing_indexes = [index["name"] for index in pc.list_indexes()]

        # create only if it doesn't exist already
        if index_name not in existing_indexes:
            print("Index doesn't exist. Creating...")
            pc.create_index(
                name=index_name,
                dimension= 768, # Add embedding dimensions
                metric= "cosine",   # Add your similarity metric
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1"
            )
        )
        else:
            print("Index exists already")

        self.index = pc.Index(index_name)

        """
        Loading embedding model:
        - SentenceTransformer (all-MiniLM-L6-v2)
        - GoogleGenerativeAIEmbeddings (models/embedding-001)
        """
        self.embedding_model = GoogleGenerativeAIEmbeddings(model='models/embedding-001')
 
    # Files must be in a list format
    def upsert_files(self, files: list):

        # Inner helper function to get the name of a 'json' file
        def get_file_name(fname):
            file_re = re.compile(r'^umd_([A-Za-z0-9]*)_data.json$')

            matched = re.match(file_re, fname)
            if matched:
                return matched.group(1)
            else:
                raise Exception("Not good file name")

        total_to_upsert = [] # List for all vectors that will be upserted

        # Go through all the files
        for file in files:
            with open(file, 'r', encoding="utf-8") as f:
                data = json.load(f)

            fname = get_file_name(file)

            content = [] # list for the content of one file

            # Loop through all the data in one file
            for d in data:
                content.append(d['Content'])
            embedded_content = self.embedding_model.embed_documents(content) # Embed in batches because it's faster
            print(f"Embedding everything from {fname} data")

            # Create pinecone type of data
            batch = []
            for i, d in enumerate(data):
                pinecone_form = {}
                pinecone_form["id"] = f"{fname}_{i}"
                pinecone_form["values"] = embedded_content[i]
                pinecone_form["metadata"] = d

                batch.append(pinecone_form)

            total_to_upsert.extend(batch)

        # upserting 200 vectors batch by batch
        batch_size = 200
        for i in range(len(total_to_upsert) // batch_size + 1):
            start = i*batch_size
            stop = start + batch_size if len(total_to_upsert) - start > 200 else len(total_to_upsert)
            self.index.upsert(namespace="file_data", vectors=total_to_upsert[start:stop])
            print(f"Upserting batch {i}")


    # Upsert random data by ourselves
    def upsert_own_data(self, our_data):

        # Get current own data id count
        with open("own_data_id_count.txt", 'r+') as file:
            id = int(file.read())
            file.seek(0)
            file.write(str(id + 1))

        embedded = self.embedding_model.embed_query(our_data)
        pinecone_form = {}
        pinecone_form["id"] = f"own_data_{id}"
        pinecone_form["values"] = embedded
        pinecone_form["metadata"] = {"text": our_data}

        self.index.upsert(namespace="own_data", vectors=[pinecone_form])

    def search(self, query, top_k=10):
        # embed the query
        query_embedding = self.embedding_model.embed_query(query)

        # Query Pinecone for the top_k most relevant chunks
        # <code to query index>
        search_results = self.index.query_namespaces(
            namespaces=['file_data', 'own_data'],
            metric='cosine',
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )

        return search_results.matches
