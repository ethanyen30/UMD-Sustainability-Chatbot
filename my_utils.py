"""
Takes a file and returns a string of the whole file
Replaces all newlines with a space to sort of 'concatenate'
everything together.
"""
def read_text_file(file):
    with open(file, 'r') as f:
        text = f.read()
        text = text.replace("\n", " ")
    return text