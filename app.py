from flask import Flask, request, send_file, render_template_string
from pypdf import PdfWriter
import io
import os

app = Flask(__name__)

# In-memory storage for uploaded files for simplicity in this example
# For a production app, consider a more robust storage solution or temporary file handling.
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    # Serve the index.html file
    # For simplicity, reading it and rendering as a string.
    # In a larger app, you'd use render_template with a templates folder.
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        return render_template_string(html_content)
    except FileNotFoundError:
        return "index.html not found. Make sure it's in the same directory as app.py.", 404


@app.route('/merge', methods=['POST'])
def merge_pdfs_route():
    if 'files' not in request.files:
        return "No files part in the request", 400
    
    files = request.files.getlist('files')
    
    if len(files) < 1:
        return "No files selected for merging", 400
    
    for file in files:
        if file.filename == '':
            return "One or more files have no selected file name", 400
        if not file.filename.lower().endswith('.pdf'):
            return "Invalid file type. Only PDFs are allowed.", 400

    writer = PdfWriter()
    
    try:
        temp_file_paths = [] # Keep track of temp files for cleanup
        for file_storage in files:
            temp_file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_storage.filename)
            file_storage.save(temp_file_path)
            temp_file_paths.append(temp_file_path)
            writer.append(temp_file_path)

        output_pdf_stream = io.BytesIO()
        writer.write(output_pdf_stream)
        writer.close()
        output_pdf_stream.seek(0)

        # Clean up temporary files
        for temp_file_path in temp_file_paths:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
        
        return send_file(
            output_pdf_stream,
            as_attachment=True,
            download_name='merged.pdf',
            mimetype='application/pdf'
        )
    except Exception as e:
        # Clean up in case of error
        for temp_file_path in temp_file_paths:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
        app.logger.error(f"Error merging PDFs: {e}")
        return str(e), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
