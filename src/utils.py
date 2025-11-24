import os, json

def read_text_files_in_dir(dir_path):
    docs = []
    if not os.path.exists(dir_path):
        return docs
    for fname in sorted(os.listdir(dir_path)):
        full = os.path.join(dir_path, fname)
        if os.path.isfile(full) and fname.lower().endswith('.txt'):
            with open(full, 'r', encoding='utf-8') as f:
                docs.append({'id': fname, 'text': f.read()})
    return docs

def read_json_files_in_dir(dir_path):
    docs = []
    if not os.path.exists(dir_path):
        return docs
    
    for fname in sorted(os.listdir(dir_path)):
        full = os.path.join(dir_path, fname)
        if os.path.isfile(full) and fname.lower().endswith('.json'):
            with open(full, 'r', encoding='utf-8') as f: 
                try:
                    content = f.read()
                    docs.extend(json.loads(f'[{content}]'))
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON in file {fname}: {e}")
    return docs