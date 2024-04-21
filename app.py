from flask import Flask, request, jsonify
from PIL import Image
from flask_cors import CORS
import google.generativeai as genai
import os
import json

app = Flask(__name__)
CORS(app)

# Configure Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Static input prompt
input_prompt = """
               You are an expert in understanding invoices.
               You will receive input images as invoices &
               you will have to extract these fields (site_vente,type,numero_facture,reference,date,client_facture,client_intitule,client_commande,tiers_payeur,client_groupe,etat,devise,debut_echeance,type_paiement,date_debut_periode,date_fin_periode,document) and return it as a json object
               & if you didnt find a field leave it blank
               """


# Function to extract fields from the invoice using Gemini API
def extract_invoice_fields(invoice_image):
    # Initialize the GenerativeModel for extracting fields
    model = genai.GenerativeModel('gemini-pro-vision')

    # Generate content using the static input prompt and the image
    response = model.generate_content(["", invoice_image, input_prompt])

    # Parse the response and extract the fields
    fields = response.text.split("\n")
    extracted_fields = {}
    for field in fields:
        if ":" in field:
            key, value = field.split(":")
            key = key.strip().strip('"')  # Remove leading/trailing whitespace and double quotes
            value = value.strip().strip('"').rstrip(
                ',')  # Remove leading/trailing whitespace, double quotes, and commas
            extracted_fields[key] = value

    # Remove unwanted characters from field values
    for key, value in extracted_fields.items():
        extracted_fields[key] = value.replace('"', '').strip()

    return extracted_fields


@app.route('/extract_fields', methods=['POST'])
def extract_fields():
    # Check if image file is present in the request
    if 'invoice_image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    # Get the image file from the request
    invoice_image = Image.open(request.files['invoice_image'])

    # Extract fields using Gemini API
    extracted_fields = extract_invoice_fields(invoice_image)

    # Return extracted fields as JSON response
    return jsonify(extracted_fields)


if __name__ == '__main__':
    app.run(debug=True)
