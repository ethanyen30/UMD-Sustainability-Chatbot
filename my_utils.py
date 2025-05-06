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
    for i in range(min(len(retrieved), top_k)):
        namespace = retrieved[i]['namespace']
        formatted = ""
        
        id = retrieved[i]['id']
        formatted += f"\n**{i+1}.** {id}\n"

        data = retrieved[i]['metadata']['Content']
        formatted += f"- Text: {data}\n"
        
        if namespace == 'file_data':
            link = retrieved[i]['metadata']['Link']
            formatted += f"- Link: {link}\n"

        score = retrieved[i]['score']
        formatted += f"- Score: {score}\n"

        res += formatted + "\n"

    return res
