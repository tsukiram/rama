
# from flask import Flask, render_template, request, jsonify, send_file
# import os
# import json
# import zipfile
# import google.generativeai as genai
# import re
# from io import BytesIO

# app = Flask(__name__)

# # Konfigurasi API
# genai.configure(api_key="AIzaSyCQR3E3kru000LRka7RRjR0mD2Q9pmWEcc")

# # Inisialisasi model
# model = genai.GenerativeModel('gemini-1.5-flash')
# chat = model.start_chat(history=[])
# finalOutput = []
# namaWebsite = ""
# deskripsiWebsite = ""
# current_progress = 0
# zip_buffer = None  # Variabel global untuk menyimpan file ZIP di memori

# def extract_json(text):
#     pattern = r'```json\s+(.*?)\s+```'
#     match = re.search(pattern, text, re.DOTALL)
    
#     if match:
#         json_content = match.group(1)
#         return json_content
#     else:
#         return None

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/api/generate', methods=['POST'])
# def generate():
#     global namaWebsite, deskripsiWebsite, finalOutput, current_progress, chat, zip_buffer

#     query = request.json['query']
    
#     # Reset variables
#     finalOutput = []
#     namaWebsite = ""
#     deskripsiWebsite = ""
#     current_progress = 0
#     chat = model.start_chat(history=[])
#     zip_buffer = BytesIO()  # Inisialisasi buffer ZIP baru

#     # Inisiasi
#     with open('iteration/init.txt', 'r') as m:
#         init = m.read()
#     chat.send_message(init)
#     current_progress = 10

#     # Generate Nama Website
#     with open('iteration/it1.txt', 'r') as m:
#         first = m.read()
#     response = chat.send_message(first + query)
#     namaWebsite = response.text
#     current_progress = 20

#     # Generate File HTML
#     with open('iteration/it2.txt', 'r') as m:
#         query = m.read()
#     response = chat.send_message(query)
#     extracted_json = extract_json(response.text)
#     if extracted_json:
#         parsed_files = json.loads(extracted_json)
#         finalOutput.extend(parsed_files)
#         current_progress = 40

#     # Generate File CSS
#     with open('iteration/it3.txt', 'r') as m:
#         query = m.read()
#     response = chat.send_message(query)
#     extracted_json = extract_json(response.text)
#     if extracted_json:
#         parsed_files = json.loads(extracted_json)
#         finalOutput.extend(parsed_files)
#         current_progress = 60

#     # Generate Deskripsi Website
#     with open('iteration/it4.txt', 'r') as m:
#         query = m.read()
#     response = chat.send_message(query)
#     deskripsiWebsite = response.text
#     current_progress = 80

#     # Membuat file ZIP di memori
#     with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
#         for file in finalOutput:
#             zipf.writestr(file['dir'], file['content'])
        
#         # Menambahkan gambar dari folder 'images'
#         images_folder = 'images'
#         target_folder = 'project-root/assets/images'
#         for root, dirs, files in os.walk(images_folder):
#             for file in files:
#                 image_path = os.path.join(root, file)
#                 relative_path_in_zip = os.path.join(target_folder, os.path.relpath(image_path, start=images_folder))
#                 zipf.write(image_path, relative_path_in_zip)
    
#     current_progress = 100

#     return jsonify({
#         'name': namaWebsite,
#         'description': deskripsiWebsite,
#         'files': finalOutput
#     })

# @app.route('/api/progress')
# def progress():
#     global current_progress
#     return jsonify({'progress': current_progress})

# @app.route('/api/download')
# def download():
#     global zip_buffer
#     if zip_buffer:
#         zip_buffer.seek(0)  # Kembali ke awal buffer
#         return send_file(
#             zip_buffer,
#             mimetype='application/zip',
#             as_attachment=True,
#             download_name='Ram-AI.zip'
#         )
#     else:
#         return "No generated content available", 404

# if __name__ == '__main__':
#     app.run(debug=True)
from flask import Flask, render_template, request, jsonify, send_file
import os
import json
import zipfile
import google.generativeai as genai
import re
from io import BytesIO
from flask_caching import Cache
import uuid
import threading

app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# Konfigurasi API
genai.configure(api_key="AIzaSyCQR3E3kru000LRka7RRjR0mD2Q9pmWEcc")

# Inisialisasi model
model = genai.GenerativeModel('gemini-1.5-flash')

def extract_json(text):
    pattern = r'```json\s+(.*?)\s+```'
    match = re.search(pattern, text, re.DOTALL)
    
    if match:
        json_content = match.group(1)
        return json_content
    else:
        return None

@app.route('/')
def index():
    return render_template('index.html')

def process_generation(task_id, query):
    chat = model.start_chat(history=[])
    finalOutput = []
    namaWebsite = ""
    deskripsiWebsite = ""
    zip_buffer = BytesIO()

    # Inisiasi
    with open('iteration/init.txt', 'r') as m:
        init = m.read()
    chat.send_message(init)
    cache.set(f'task_{task_id}', 10)

    # Generate Nama Website
    with open('iteration/it1.txt', 'r') as m:
        first = m.read()
    response = chat.send_message(first + query)
    namaWebsite = response.text
    cache.set(f'task_{task_id}', 20)

    # Generate File HTML
    with open('iteration/it2.txt', 'r') as m:
        query = m.read()
    response = chat.send_message(query)
    extracted_json = extract_json(response.text)
    if extracted_json:
        parsed_files = json.loads(extracted_json)
        finalOutput.extend(parsed_files)
    cache.set(f'task_{task_id}', 40)

    # Generate File CSS
    with open('iteration/it3.txt', 'r') as m:
        query = m.read()
    response = chat.send_message(query)
    extracted_json = extract_json(response.text)
    if extracted_json:
        parsed_files = json.loads(extracted_json)
        finalOutput.extend(parsed_files)
    cache.set(f'task_{task_id}', 60)

    # Generate Deskripsi Website
    with open('iteration/it4.txt', 'r') as m:
        query = m.read()
    response = chat.send_message(query)
    deskripsiWebsite = response.text
    cache.set(f'task_{task_id}', 80)

    # Membuat file ZIP di memori
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in finalOutput:
            zipf.writestr(file['dir'], file['content'])
        
        # Menambahkan gambar dari folder 'images'
        images_folder = 'images'
        target_folder = 'project-root/assets/images'
        for root, dirs, files in os.walk(images_folder):
            for file in files:
                image_path = os.path.join(root, file)
                relative_path_in_zip = os.path.join(target_folder, os.path.relpath(image_path, start=images_folder))
                zipf.write(image_path, relative_path_in_zip)
    
    cache.set(f'task_{task_id}', 100)
    cache.set(f'result_{task_id}', {
        'name': namaWebsite,
        'description': deskripsiWebsite,
        'files': finalOutput,
        'zip_buffer': zip_buffer.getvalue()
    })

@app.route('/api/generate', methods=['POST'])
def generate():
    query = request.json['query']
    task_id = str(uuid.uuid4())
    
    threading.Thread(target=process_generation, args=(task_id, query)).start()
    
    return jsonify({'task_id': task_id})

@app.route('/api/progress/<task_id>')
def progress(task_id):
    progress = cache.get(f'task_{task_id}')
    if progress is None:
        return jsonify({'error': 'Task not found'}), 404
    return jsonify({'progress': progress})

@app.route('/api/result/<task_id>')
def get_result(task_id):
    result = cache.get(f'result_{task_id}')
    if result is None:
        return jsonify({'error': 'Result not found'}), 404
    return jsonify({
        'name': result['name'],
        'description': result['description'],
        'files': result['files']
    })

@app.route('/api/download/<task_id>')
def download(task_id):
    result = cache.get(f'result_{task_id}')
    if result is None:
        return "No generated content available", 404
    
    zip_buffer = BytesIO(result['zip_buffer'])
    zip_buffer.seek(0)
    return send_file(
        zip_buffer,
        mimetype='application/zip',
        as_attachment=True,
        download_name='Ram-AI.zip'
    )

if __name__ == '__main__':
    app.run(debug=True)