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

def organize_retrieval(retrieved, top_k=3):
    res = f"Top {top_k} retrieved documents:\n"
    for i in range(top_k):
        id = retrieved[i]['id']
        score = retrieved[i]['score']
        data = retrieved[i]['metadata']['Content']
        link = retrieved[i]['metadata']['Link']

        formatted = (
            f"{i+1}. {id}\n"
            f"- Text: {data}\n"
            f"- Link: {link}\n"
            f"- Score: {score}\n"
        )
        res += formatted + "\n"

    return res
