from flask import Flask, render_template, request, redirect, url_for, session
import os
from werkzeug.utils import secure_filename
from imgtoocr import image_to_text, extract_prescription_data
from medicinename import main as get_medication_info  # Import medication info function

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session storage
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024

# Create uploads directory if it doesn't exist
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def translate_text(data, tgt="hi"):  # Placeholder translation function
    """Simulates translation without external dependencies."""
    if tgt == "English":
        return data  # No translation needed
    # Simulate translation by returning the same text
    return data  # Replace this with actual logic if needed

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/set_language', methods=['POST'])
def set_language():
    selected_language = request.form.get('language')
    session['language'] = selected_language
    return '', 204  # Return success response

@app.route('/')
def index():
    selected_language = session.get('language', 'English')  # Default to English
    return render_template('index.html', language=selected_language)

@app.route('/medication', methods=['POST'])
def medication_info():
    med_name = request.form.get('med_name')
    selected_language = session.get('language', 'English')

    if not med_name:
        return 'No medication specified'
    
    try:
        medication_data = get_medication_info(med_name)
        
        # Simulate translation for medication details if not English
        if selected_language != "English":
            for key in ['name', 'description', 'dosage', 'side_effects', 'warnings']:
                if key in medication_data:
                    medication_data[key] = translate_text(medication_data[key], tgt=selected_language)

        return render_template('medication_details.html', 
                               medication=medication_data, 
                               med_name=med_name, 
                               language=selected_language)
    except Exception as e:
        return f'Error retrieving medication information: {str(e)}'

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    
    file = request.files['file']
    
    if file.filename == '':
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        extracted_text = image_to_text(file_path)
        
        if not extracted_text:
            return 'Failed to extract text from image'
        
        prescription_data = extract_prescription_data(extracted_text)
        print("Extracted Text:", prescription_data)
        if not prescription_data:
            return 'Failed to process prescription data'
        
        # Get selected language
        selected_language = session.get('language', 'English')

        # Simulate translation for prescription data if not English
        if selected_language != "English":
            prescription_data = translate_text(prescription_data, tgt=selected_language)
            print("Translated Prescription Data:", prescription_data)

        return render_template('result.html', 
                               data=prescription_data,
                               image_path=file_path,
                               language=selected_language)
    
    return 'Invalid file type. Allowed types: png, jpg, jpeg, gif'

if __name__ == '__main__':
    app.run(debug=True)