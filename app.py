import gradio as gr
from langchain_google_genai import ChatGoogleGenerativeAI
import umd_rag
import pineconing
import my_utils

"""
Initiate everything needed for the app (chatbot)
"""
vdb = pineconing.VectorDB()
google_model = "gemini-2.0-flash-lite"
llm = ChatGoogleGenerativeAI(model=google_model)
rag = umd_rag.UMDRAG(vdb, llm)

"""
This function checks whether the inputted info is related to sustainability at UMD:
Inputs:
    info: str
    - whatever data the user inputs
Outpus:
    (str, str):
    first str is to reset the input box
    second str is the output message (whether yes or no)
"""
def check_info(info: str):
    model = "gemini-2.0-flash"
    llm = ChatGoogleGenerativeAI(model=model)
    prompt = my_utils.read_text_file("datafiles/sus_check_prompt.txt") + f"\n{info}"
    llm_answer = llm.invoke(prompt).content

    output = ""
    if llm_answer.lower() == 'yes':
        output = "Thank you! Your fact is valid and will be sent to the database!"
        vdb.upsert_own_data(info)
    else:
        output = "Sorry. Try to mention something related to sustainability at UMD."

    return "", output

def get_added_data():
    ids = []
    for v in vdb.index.list(namespace='own_data'):
        ids.extend(v)

    fr = vdb.index.fetch(ids=ids, namespace='own_data')
    vectors = fr.vectors #dict

    added_data = []
    for key in sorted(vectors.keys()):
        value = vectors[key]
        added_data.append(value.metadata['Content'])
    
    return "- " + "\n- ".join(added_data)

def gradio_response(message, chat_history):
    response = rag.pipe(message, include_metadata=True)
    current_query_metadata = my_utils.organize_retrieval(response['metadata'])
    bot_message = response['answer'].content
    chat_history.append({"role": "user", "content": message})
    chat_history.append({"role": "assistant", "content": bot_message})

    return "", chat_history, current_query_metadata

theme = gr.themes.Glass(
    primary_hue="green",
    secondary_hue="green",
    spacing_size="lg",
    text_size="lg",
    font=gr.themes.GoogleFont("Inconsolata"),
    font_mono="Consolas"
)

with gr.Blocks(theme=theme) as demo:
    with gr.Tab("Chatbot"):
        
        with gr.Row():
            with gr.Column(scale=3):
                chatbot = gr.Chatbot(type="messages")
                msg = gr.Textbox(show_label=False,
                                 placeholder='Ask here!',
                                 max_length=200)
                clear = gr.ClearButton([msg, chatbot])

            with gr.Column(scale=1):
                metadata = gr.Markdown(value="Metadata",
                                       height=580,
                                       container=True)
            
            msg.submit(
                fn=gradio_response,
                inputs=[msg, chatbot],
                outputs=[msg, chatbot, metadata]
            )
        
    with gr.Tab("Enter Your Own Facts!"):
        own_data_intro_text = my_utils.read_text_file("datafiles/own_data_intro.txt")
        gr.Markdown(own_data_intro_text)

        fact = gr.Textbox(
            placeholder="Enter Fact Here!",
            label="Fact:"
        )
        
        output = gr.Markdown(show_label=False, container=False)

        fact.submit(fn=check_info, inputs=fact, outputs=[fact, output], api_name="check_info")
        
        with gr.Accordion("See all added data:", open=False) as accordion:
            added_data = gr.Textbox(lines=10, interactive=False, show_label=False)
        accordion.expand(fn=get_added_data, outputs=added_data)
    
    with gr.Sidebar():
        gr.Markdown("**Introduction**")
        chatbot_intro_text = my_utils.read_text_file('datafiles/chatbot_intro.txt')
        gr.Markdown(chatbot_intro_text)


demo.launch(debug=True)