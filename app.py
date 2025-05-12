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
    # current_query_metadata = my_utils.organize_retrieval(response['metadata'])
    bot_message = response['answer'].content
    chat_history.append({"role": "user", "content": message})
    chat_history.append({"role": "assistant", "content": bot_message})
    rendered_metadata = render_retrievals(response['metadata'])
    return "", chat_history, response['metadata']

theme = gr.themes.Glass(
    primary_hue="green",
    secondary_hue="green",
    text_size="lg",
    font=gr.themes.GoogleFont("Inconsolata"),
    font_mono="Consolas"
)

with gr.Blocks(theme=theme) as demo:
    
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

            # Side to display metadata
            # with gr.Column(scale=1):
            #     metadata = gr.Markdown(
            #         value="### 📄 Retrieved Metadata",
            #         label="Metadata",
            #         height=500,
            #         container=True
            #     )
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

                    for item in retrievals[0:3]:
                        item_id = item.get("id", "N/A")
                        score = round(item.get("score", 0), 4)
                        content = item.get("metadata", {}).get("Content", "")
                        
                        preview = content[:200] + "..." if len(content) > 200 else content
                        
                        with gr.Accordion(label=f"ID: {item_id} | Score: {score}") as acc:
                            gr.Markdown(f"**Content:** {preview}")
                            if len(content) > 200:
                                gr.Markdown(f"<details><summary>Show full content</summary><p>{content}</p></details>")
                            if item['namespace'] != 'own_data':
                                link = item.get("metadata", {}).get("Link", "#")
                                gr.Markdown(f"[🔗 Link]({link})")

                
    # Enter own facts tab
    with gr.Tab("Enter Your Own Facts!"):
        gr.Markdown(my_utils.read_text_file('datafiles/intro_texts/own_data_intro.txt', False))

        fact = gr.Textbox(
            placeholder="Enter Fact Here!",
            label="Fact:"
        )

        output = gr.Markdown(show_label=False, container=False)

        fact.submit(fn=check_info, inputs=fact, outputs=[fact, output], api_name="check_info")
        
        with gr.Accordion("See all added data:", open=False) as accordion:
            added_data = gr.Markdown(show_label=False)
        accordion.expand(fn=get_added_data, outputs=added_data)
        
demo.launch(debug=True)