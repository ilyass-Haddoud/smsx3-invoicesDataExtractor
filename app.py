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

input_prompt = """
               You are an expert in understanding invoices.
               You will receive input images as invoices &
               you will have to extract these fields (site_vente,numero_facture,type_facture,numero_piece,date,fournisseur,raison_sociale,devise(EUR,USD,MAD,...),debut_echeance,adresse,condition_paiement,etat_facture,total_ttc(just the number(pos or neg) without the currency)) and return it as a json object
               & if you didnt find a field leave it blank(empty string)
               """


def extract_invoice_fields(invoice_image):
    model = genai.GenerativeModel('gemini-pro-vision')

    response = model.generate_content(["", invoice_image, input_prompt])

    fields = response.text.split("\n")
    extracted_fields = {}
    for field in fields:
        if ":" in field:
            key, value = field.split(":")
            key = key.strip().strip('"')
            value = value.strip().strip('"').rstrip(
                ',')
            extracted_fields[key] = value

    for key, value in extracted_fields.items():
        extracted_fields[key] = value.replace('"', '').strip()

    return extracted_fields


@app.route('/extract_fields', methods=['POST'])
def extract_fields():
    print(request.files)
    if 'document' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    invoice_image = Image.open(request.files['document'])

    extracted_fields = extract_invoice_fields(invoice_image)

    return jsonify(extracted_fields)


if __name__ == '__main__':
    app.run(debug=True)
