from flask import Flask, request, send_file, render_template_string, jsonify
from pypdf import PdfWriter, PdfReader
import io
import os
import re

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

@app.route('/split', methods=['POST'])
def split_pdf_route():
    if 'file' not in request.files:
        return "No file part in the request", 400
    
    file = request.files['file']
    
    if file.filename == '':
        return "No file selected for splitting", 400
    if not file.filename.lower().endswith('.pdf'):
        return "Invalid file type. Only PDFs are allowed.", 400
    
    # Get the page range
    page_selection = request.form.get('pageSelection', 'all')
    custom_range = request.form.get('customRange', '')
    
    # Save the uploaded file temporarily
    temp_file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(temp_file_path)
    
    try:
        # Read the PDF file
        reader = PdfReader(temp_file_path)
        total_pages = len(reader.pages)
        writer = PdfWriter()
        
        # Process page selection
        selected_pages = []
        
        if page_selection == 'all':
            selected_pages = list(range(total_pages))
        elif page_selection == 'odd':
            selected_pages = list(range(0, total_pages, 2))
        elif page_selection == 'even':
            selected_pages = list(range(1, total_pages, 2))
        elif page_selection == 'custom' and custom_range:
            # Process the custom range string (e.g. "1-4,7,9-10")
            # Convert to 0-indexed
            for part in custom_range.split(','):
                if '-' in part:
                    start, end = map(int, part.split('-'))
                    selected_pages.extend(range(start - 1, end))
                else:
                    selected_pages.append(int(part) - 1)
                    
            # Filter out pages that are out of range
            selected_pages = [p for p in selected_pages if 0 <= p < total_pages]
        
        # Add selected pages to the writer
        for page_num in selected_pages:
            writer.add_page(reader.pages[page_num])
        
        # Write the output PDF
        output_pdf_stream = io.BytesIO()
        writer.write(output_pdf_stream)
        writer.close()
        output_pdf_stream.seek(0)
        
        # Clean up temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            
        return send_file(
            output_pdf_stream,
            as_attachment=True,
            download_name='split.pdf',
            mimetype='application/pdf'
        )
    except Exception as e:
        # Clean up in case of error
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        app.logger.error(f"Error splitting PDF: {e}")
        return str(e), 500

@app.route('/preview', methods=['POST'])
def preview_pdf():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No file selected for preview"}), 400
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({"error": "Invalid file type. Only PDFs are allowed."}), 400
    
    # Save the uploaded file temporarily
    temp_file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(temp_file_path)
    
    try:
        # Get total pages count
        reader = PdfReader(temp_file_path)
        total_pages = len(reader.pages)
        
        # Clean up temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            
        return jsonify({
            "success": True,
            "totalPages": total_pages,
            "filename": file.filename
        })
    except Exception as e:
        # Clean up in case of error
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
