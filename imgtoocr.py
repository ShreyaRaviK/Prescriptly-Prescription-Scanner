import google.generativeai as genai
import PIL.Image
import json

# Configure your API key
genai.configure(api_key="AIzaSyAJTKMVCl-SGu92abhNbU-Zriz6ZmAL0wY")  # Replace with your actual API key

def image_to_text(image_path):
    """Sends an image to Gemini and returns the extracted text."""
    model = genai.GenerativeModel('gemini-1.5-pro')

    try:
        img = PIL.Image.open(image_path)  # Load the image

        response = model.generate_content([
            "Extract the text from this prescription image.",
            img,
        ])

        return response.text.strip() if response else None

    except FileNotFoundError:
        print(f"Error: Image not found at {image_path}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def extract_prescription_data(text):
    """Extracts structured prescription data from the text using Gemini."""
    model = genai.GenerativeModel('gemini-1.5-pro')

    prompt = f"""
    Extract structured prescription information from the following text and return a JSON object that strictly follows this schema:
    
    Schema:
    {{
        "name": "Patient's full name",
        "dob": "YYYY-MM-DD",
        "age": 30,
        "date": "YYYY-MM-DD",
        "medications": [
            {{
                "name": "Medicine name",
                "frequency": "How often to take the medicine (e.g., 3 times a day)"
            }}
        ]
    }}

    Text:
    ```
    {text}
    ```

    Return only a valid JSON object without any extra text, explanations, or comments.
    """

    response = model.generate_content(prompt)

    try:
        json_str = response.text.strip()
        json_start = json_str.find("{")
        json_end = json_str.rfind("}") + 1
        json_str = json_str[json_start:json_end]  # Extract just the JSON part

        prescription_data = json.loads(json_str)  # Parse JSON
        return prescription_data
    except json.JSONDecodeError:
        print("Error: Could not parse prescription data. Raw response:")
        print(response.text)  # Print response to debug
        return None

# Add this at the bottom of your existing imagetoocr.py
if __name__ == "__main__":
    # Example usage
    image_path = "1.webp"  # Replace with the path to your image file
    extracted_text = image_to_text(image_path)

    if extracted_text:
        prescription_data = extract_prescription_data(extracted_text)
        
        if prescription_data:
            print("Structured Prescription Data:")
            print(json.dumps(prescription_data, indent=2))