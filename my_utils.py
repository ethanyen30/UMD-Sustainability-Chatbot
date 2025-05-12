"""
Takes a file and returns a string of the whole file
If specified, replaces all newlines with a space to sort of 'concatenate'
everything together.
Inputs:
    file: file path
    concat (default True): concatenates all new lines if true, otherwise just leave it
Outputs:
    text in string format
"""
def read_text_file(file, concat=True):
    with open(file, 'r', encoding='utf-8') as f:
        text = f.read()
        if concat:
            text = text.replace("\n", " ")
    return text