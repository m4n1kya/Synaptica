import ast
import json

with open('found_html.txt', 'r', encoding='utf-8') as f:
    content = f.read().strip()

# It's a JSON string or Python string literal. Let's try json.loads if it starts with quote
if content.startswith('"'):
    try:
        content = json.loads(content)
    except Exception as e:
        content = ast.literal_eval(content)

with open('decoded_html.html', 'w', encoding='utf-8') as f:
    f.write(content)
