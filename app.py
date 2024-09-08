# app.py
from flask import Flask, render_template, request, jsonify, send_file
import os
import json
import zipfile
import google.generativeai as genai
import re
from io import BytesIO

app = Flask(__name__)

# Konfigurasi API
genai.configure(api_key="AIzaSyCQR3E3kru000LRka7RRjR0mD2Q9pmWEcc")

# Inisialisasi model
model = genai.GenerativeModel('gemini-1.5-flash')
chat = model.start_chat(history=[])
finalOutput = []
namaWebsite = ""
deskripsiWebsite = ""
generation_complete = False
zip_buffer = None  # Variabel global untuk menyimpan file ZIP di memori

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

@app.route('/api/generate', methods=['POST'])
def generate():
    global namaWebsite, deskripsiWebsite, finalOutput, generation_complete, chat, zip_buffer
    query = request.json['query']

    # Reset variables
    finalOutput = []
    namaWebsite = ""
    deskripsiWebsite = ""
    generation_complete = False
    chat = model.start_chat(history=[])
    zip_buffer = BytesIO()  # Inisialisasi buffer ZIP baru

    # Inisiasi
    with open('iteration/init.txt', 'r') as m:
        init = m.read()
    chat.send_message(init)

    # Generate Nama Website
    with open('iteration/it1.txt', 'r') as m:
        first = m.read()
    response = chat.send_message(first + query)
    namaWebsite = response.text

    # Generate File HTML
    with open('iteration/it2.txt', 'r') as m:
        query = m.read()
    response = chat.send_message(query)
    extracted_json = extract_json(response.text)
    if extracted_json:
        parsed_files = json.loads(extracted_json)
        finalOutput.extend(parsed_files)

    # Generate File CSS
    with open('iteration/it3.txt', 'r') as m:
        query = m.read()
    response = chat.send_message(query)
    extracted_json = extract_json(response.text)
    if extracted_json:
        parsed_files = json.loads(extracted_json)
        finalOutput.extend(parsed_files)

    # Generate Deskripsi Website
    with open('iteration/it4.txt', 'r') as m:
        query = m.read()
    response = chat.send_message(query)
    deskripsiWebsite = response.text

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

    generation_complete = True
    return jsonify({
        'name': namaWebsite,
        'description': deskripsiWebsite,
        'files': finalOutput
    })

@app.route('/api/progress')
def progress():
    global generation_complete
    return jsonify({'complete': generation_complete})

@app.route('/api/download')
def download():
    global zip_buffer
    if zip_buffer:
        zip_buffer.seek(0)  # Kembali ke awal buffer
        return send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name='Ram-AI.zip'
        )
    else:
        return "No generated content available", 404

if __name__ == '__main__':
    app.run(debug=True)
