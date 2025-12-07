import gradio as gr
from langchain_google_genai import ChatGoogleGenerativeAI
from PIL import Image
import umd_rag
import pineconing
import my_utils

"""
Initiate everything needed for the app (chatbot)
"""
vdb = pineconing.VectorDB()
google_model = "gemini-2.5-flash-lite"
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
    prompt = my_utils.read_text_file("datafiles/sus_check_prompt.txt") + f"\n{info}"
    llm_answer = llm.invoke(prompt).content

    output = ""
    if llm_answer.lower() == 'yes':
        output = "Thank you! Your fact is valid and will be sent to the database!"
        vdb.upsert_own_data(info)
    else:
        output = "Sorry. Try to mention something related to sustainability at UMD."

    return "", output

# Function when user wants to see added data
def get_added_data():
    ids = []
    for v in vdb.index.list(namespace='own_data'):
        ids.extend(v)

    fr = vdb.index.fetch(ids=ids, namespace='own_data')
    vectors = fr.vectors # dict

    added_data = []
    for key in sorted(vectors.keys()):
        value = vectors[key]
        added_data.append(f"ID: {key}, Info: {value.metadata['Content']}")
    
    return "- " + "\n- ".join(added_data) + "\n---"

# Function when user wants to delete some user added data
def delete_added_data(id):
    return "", vdb.delete_by_id(id, 'own_data')

# Chatbot function
def gradio_response(message, chat_history):
    response = rag.pipe(message, include_metadata=True, top_k=6, retrieval_thresh=0.5)
    bot_message = response['answer'].content
    chat_history.append({"role": "user", "content": message})
    chat_history.append({"role": "assistant", "content": bot_message})
    return "", chat_history, response['metadata']

# Theme
theme = gr.themes.Glass(
    primary_hue="green",
    secondary_hue="green",
    text_size="lg",
    font=gr.themes.GoogleFont("Inconsolata"),
    font_mono="Consolas"
)

# App
with gr.Blocks(theme=theme) as demo:
    gr.HTML(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inconsolata&display=swap');

        * {
            font-family: 'Inconsolata', monospace !important;
        }
        </style>
        """
    )
    
    # Introduction Tab
    with gr.Tab("Introduction"):

        # Welcome (Intro)
        gr.Markdown(my_utils.read_text_file('datafiles/intro_texts/intro.txt', False))

        # Nav and Notes
        with gr.Row():
            gr.Markdown(my_utils.read_text_file('datafiles/intro_texts/intro_nav.txt', False))
            gr.Markdown(my_utils.read_text_file('datafiles/intro_texts/intro_notes.txt', False))
        gr.Markdown("---")

        # Tools and Stats
        with gr.Row():
            gr.Markdown(my_utils.read_text_file('datafiles/intro_texts/intro_tools.txt', False))
            gr.Markdown(my_utils.read_text_file('datafiles/intro_texts/intro_stats.txt', False))
        gr.Markdown("---")

        # How and Image
        with gr.Row():
            gr.Markdown(my_utils.read_text_file('datafiles/intro_texts/intro_how.txt', False))
            diagram = Image.open('datafiles/RAG_Pipeline.jpg')
            width, height = diagram.size
            diagram = diagram.resize((width // 4, height // 4))
            gr.Image(diagram)
        gr.Markdown("---")

        # About
        with gr.Row():
            gr.Markdown(my_utils.read_text_file('datafiles/intro_texts/intro_about.txt', False))
        gr.Markdown("---")

        # Contact
        gr.Markdown(my_utils.read_text_file('datafiles/intro_texts/intro_contact.txt', False))

    # Chatbot Tab
    with gr.Tab("Chatbot"):
        gr.Markdown(my_utils.read_text_file('datafiles/intro_texts/chatbot_intro.txt', False))

        # Layout
        with gr.Row():

            # Chatbot column
            with gr.Column(scale=2):
                chatbot = gr.Chatbot(type="messages")
                msg = gr.Textbox(show_label=False,
                                    placeholder='Ask here!',
                                    max_length=200)
                clear = gr.ClearButton([msg, chatbot])

            # Metadata column with dynamics
            with gr.Column(scale=1):
                gr.Markdown("### 📄 Retrieved Metadata")
                metadata = gr.State([])
                    
                msg.submit(
                    fn=gradio_response,
                    inputs=[msg, chatbot],
                    outputs=[msg, chatbot, metadata]
                )

                @gr.render(inputs=metadata)
                def render_retrievals(retrievals):
                    if len(retrievals) == 0:
                        gr.Markdown("No data retrieved.")

                    for idx, item in enumerate(retrievals[0:3]):
                        item_id = item.get("id", "N/A")
                        score = round(item.get("score", 0), 4)
                        content = item.get("metadata", {}).get("Content", "")
                        
                        preview = content[:150] + "..." if len(content) > 150 else content
                        
                        with gr.Accordion(f"{idx+1}. ID: {item_id} | Score: {score}"):
                            if item['namespace'] != 'own_data':
                                link = item.get("metadata", {}).get("Link", "#")
                                gr.Markdown(f"🔗 Link: {link}")
                            else:
                                gr.Markdown("User entered data:")
                            gr.Markdown(f"**Content Preview:** {preview}")
                            if len(content) > 150:
                                gr.Markdown(f"<details><summary>Show full content</summary><p>{content}</p></details>")

                
    # Enter own facts tab
    with gr.Tab("Enter Your Own Facts!"):
        gr.Markdown(my_utils.read_text_file('datafiles/intro_texts/own_data_intro.txt', False))

        fact = gr.Textbox(
            placeholder="Enter Fact Here!",
            label="Fact:"
        )
        added_output = gr.Markdown(show_label=False, container=False)
        fact.submit(fn=check_info, inputs=fact, outputs=[fact, added_output], api_name="check_info")
        
        with gr.Accordion("See all added data (Click again to reload):", open=False) as accordion:
            added_data = gr.Markdown(show_label=False)
            gr.Markdown(my_utils.read_text_file('datafiles/intro_texts/own_data_delete.txt', False))
            wrong = gr.Textbox(
                placeholder="Enter ID number here",
                label="Delete:",
                interactive=True
            )
            deleted_output = gr.Markdown(show_label=False)
            wrong.submit(fn=delete_added_data, inputs=wrong, outputs=[wrong, deleted_output])
        accordion.expand(fn=get_added_data, outputs=added_data)
        
        

demo.launch(debug=True)