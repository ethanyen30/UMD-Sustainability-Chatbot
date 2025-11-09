# UMD-Sustainability-Chatbot

To access and play around with the chatbot, follow this [link](https://huggingface.co/spaces/ethanyen30/UMD-Sustainability-Chatbot). 

> This link does not open in new tab.

General information is in the link.

## File Information
Here I will describe what's in each file. Let's go through it from the top to bottom based on how you'll see it in the repo. I'll look at just the files first.

### .gitattributes
This contains the type of files to track with lfs. Here I am tracking jpg.
> Note: I am unsure how this is different from the 'gitattributes' (no dot) file

### .gitignore
This contains the files in my local repo that I'm ignoring so I don't push it to here. Mainly it is just venv and env and also my hf token.

### README.me
This is the readme for the huggingface space to help with initializing.

### __init__.py
This makes it so that files in this repo are sort of like packages so I can use certain functions across files. This was created to help with my my_utils.py file.

### app.py
This is the main file that contains all the frontend ui stuff (gradio). It is called app.py because the huggingface space needs a file called that.

### data processing.ipynb
This is just a notebook to look at the data. I didn't really do much in here but if anybody wants to look more into the data and process it more, then this is the place to do it.

### everything.ipynb
This is a notebook that sort of initiates the RAG pipeline from the data collection to the vector storage and the retrieval and generation process. I use this to run short scripts to modify the vector database mostly. Also, if I want to rescrape the data for a more updated model.

### gitattributes
This came with the creation of the hf space so I didn't want to remove or change it. Again, like above, I don't know if this can be merged with the '.gitattributes' (yes dot) file or not.

### my_utils.py
This is a helper file with helper functions that can be used throughout the repo. I'm only using one which is the read_text_file function:
``` def read_text_file(file) ```

### pineconing.py
Here we connect to the pinecone database and I created a class around it and wrapped a few functions. This is used to initialize the database in other files.

### requirements.txt
These are the installation requirements. There's a lot but I'll list the main ones:
- bs4 (web scraping)
- pinecone (vector db)
- langchain_google_genai (for model and embeddings)
- langchain (tracing code for langsmith)

### umd_rag.py
This is a class that models the RAG pipeline. It contains the methods used in RAG like retrieving and generating. A cool thing is that it can be intiated with any model.

### umd_webscraper.py
This contains the class that scrapes the UMD sustainability data. It is a little specific as it can only scrape based on a specific layout of the websites.
