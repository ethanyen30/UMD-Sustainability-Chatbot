from langsmith import traceable
from dotenv import load_dotenv
import my_utils

class UMDRAG:

    def __init__(self, vdb, model):
        load_dotenv(override=True)
        self.vector_storage = vdb
        self.model = model

    @traceable(
        run_type='retriever'
    )
    def retrieve(self, query, top_k=10):
        matched = self.vector_storage.search(query, top_k)
        return matched
    
    def create_prompt(self, retrieval, query):
        system_instruction = my_utils.read_text_file('datafiles/model_instruction.txt')
        context = ""
        for retrieved in retrieval:
            namespace = retrieved['namespace']
            content_data = retrieved['metadata']

            if namespace == 'file_data':
                context += f"Site Title: {content_data['Site_Title']}\n"
                context += f"Header: {content_data['Header']}\n"

            elif namespace == 'own_data':
                pass
            context += f"Text: {content_data['Content']}\n\n"

        prompt = f"Here are your instructions: \n {system_instruction} \n \
                        Here is the context provided to answer the query.\n \
                        Context: {context}\nQuestion: {query}\nAnswer:"
        return prompt
    
    def generate(self, prompt):
        return self.model.invoke(prompt)
    
    @traceable(
        run_type='chain',
        metadata={"ls_provider": "google_genai", "ls_model_name": "gemini-2.0-flash-lite"}
    )
    def pipe(self, query, include_metadata=False):
        retrieval = self.retrieve(query)
        prompt = self.create_prompt(retrieval, query)
        answer = self.generate(prompt)
        return {
            'answer': answer,
            'metadata': retrieval if include_metadata else []
        }
