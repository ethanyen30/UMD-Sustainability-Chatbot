import gradio as gr
from langchain_google_genai import ChatGoogleGenerativeAI
import umd_rag
import pineconing
import importlib

importlib.reload(umd_rag)
importlib.reload(pineconing)

vdb = pineconing.VectorDB()
google_model = "gemini-2.0-flash-lite"
llm = ChatGoogleGenerativeAI(model=google_model)
rag = umd_rag.UMDRAG(vdb, llm)

def gradio_response(input, history=""):
    response = rag.pipe(input)
    return response.content

demo = gr.ChatInterface(fn=gradio_response,
                        title="UMD Sustainability Chatbot",
                        description="This is my DCC Capstone Project",
                        theme="ocean",
                        autofocus=True,
                        autoscroll=True)

demo.launch(debug=True)