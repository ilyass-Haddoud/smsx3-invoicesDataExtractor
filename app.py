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
               Vous êtes chargé d'extraire des informations à partir de factures.
                Vous recevrez des images en entrée représentant des factures, et vous devez extraire les champs suivants (site, typeFacture, dateComptable, tiers, devise, documentOrigine, dateOrigine, totalHTLignes, totalTaxes, montantTTC). Pour chaque article de la facture, il doit y avoir les champs suivants (article, designation, uniteFacturation, quantiteFacturee, prixNet, montantLigneHT).
                Le résultat doit être sous format d'un objet JSON. Pour le champ 'items', il doit être un tableau d'objets représentant les articles de la facture, comme indiqué dans l'exemple ci-dessous. Les clés de l'objet doivent rester les mêmes que celles fournies dans l'exemple. Si un champ n'est pas trouvé, il doit être laissé vide (chaîne vide).
                Pour chaque article, tu inclus un code unique
                Exemple de réponse :
                {
                    "site": "",
                    "typeFacture": "",
                    "dateComptable": "",
                    "tiers": "",
                    "devise": "",
                    "documentOrigine": "",
                    "dateOrigine": "",
                    "totalHTLignes": ,
                    "totalTaxes": ,
                    "montantTTC": ,
                    "items": [
                        {
                            "code": "";
                            "article": "",
                            "designation": "",
                            "uniteFacturation": "",
                            "quantiteFacturee": ,
                            "prixNet": ,
                            "montantLigneHT": ,
                        }
                    ]
                }
               """


def extract_invoice_fields(invoice_image):
    model = genai.GenerativeModel('gemini-pro-vision')

    response = model.generate_content(["", invoice_image, input_prompt])
    response_text = response.text

    # Trouver l'indice de début et de fin des balises "```json"
    start_index = response_text.find("```json") + len("```json")
    end_index = response_text.rfind("```")

    # Extraire le contenu JSON entre les balises
    json_content = response_text[start_index:end_index].strip()

    # Charger le JSON
    response_json = json.loads(json_content)
    return response_json


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
