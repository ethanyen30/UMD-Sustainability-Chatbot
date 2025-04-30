import gradio as gr
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from my_utils import read_text_file

load_dotenv()

information = []

def check_info(info):
    model = "gemini-2.0-flash"
    llm = ChatGoogleGenerativeAI(model=model)
    prompt = read_text_file("form_submission/sus_check_prompt.txt") + f"\n{info}"
    llm_answer = llm.invoke(prompt).content

    output = ""
    if llm_answer.lower() == 'yes':
        information.append(info)
        output = "Thank you! Your fact is valid and will be sent to the database!"
        print("good")
    else:
        output = llm_answer
        print("bad")

    # first is to reset the input message    
    return "", output

def reset():
    return ""


theme = gr.themes.Glass(
    text_size="lg"
)

with gr.Blocks(theme=theme) as demo:
    intro_text = read_text_file("form_submission/intro.txt")
    intro = gr.Markdown(intro_text)

    fact = gr.Textbox(
        placeholder="Enter Fact Here!",
        label="Fact:"
    )
    
    output = gr.Textbox(show_label=False)

    fact.submit(fn=check_info, inputs=fact, outputs=[fact, output], api_name="check_info")
    fact.input(fn=reset, outputs=output, api_name="reset")

demo.launch()