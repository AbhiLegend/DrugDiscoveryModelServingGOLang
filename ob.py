from flask import Flask, request, jsonify, send_file
from rdkit import Chem
from rdkit.Chem import AllChem, Draw
import numpy as np
import openvino.runtime as ov
import io
import os

app = Flask(__name__)

# Load OpenVINO model
model_path = 'lipophilicity_openvino.xml'  # Replace with your model path
core = ov.Core()
compiled_model = core.compile_model(model_path, "CPU")

# Function to convert SMILES to fingerprints
def smiles_to_fp(smiles, n_bits=2048):
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:  # Check if the molecule is valid
        return None
    fp = AllChem.GetMorganFingerprintAsBitVect(mol, radius=2, nBits=n_bits)
    return np.array(fp)

# Function to convert a molecule to an image
# Function to convert a molecule to an image using an alternative method
def mol_to_image(mol):
    if mol:
        temp_file = "temp_molecule_image.png"  # Temporary file name
        Draw.MolToFile(mol, temp_file)  # Save the molecule image to a file

        # Read the saved image file into a BytesIO object
        with open(temp_file, 'rb') as image_file:
            img_byte_arr = io.BytesIO(image_file.read())

        os.remove(temp_file)  # Clean up: remove the temporary file
        img_byte_arr.seek(0)
        return img_byte_arr
    return None

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    smiles = data['smiles']
    mol = Chem.MolFromSmiles(smiles)

    if mol is None:
        return jsonify({'error': 'Invalid SMILES string'})

    fp = smiles_to_fp(smiles)
    if fp is None:  # Check if the fingerprint was successfully generated
        return jsonify({'error': 'Invalid SMILES string'})

    input_tensor = np.array([fp], dtype=np.float32)

    # OpenVINO inference
    ov_input_tensor = ov.Tensor(input_tensor)
    result = compiled_model([ov_input_tensor])[0]
    prediction = result[0]

    # Generate molecule image
    img_io = mol_to_image(mol)
    if img_io:
        img_io.seek(0)  # Reset the file pointer to the beginning of the stream
        response = send_file(
            img_io,
            mimetype='image/png',
            as_attachment=True,  # Indicates that this should be downloaded as an attachment
            download_name='molecule.png'  # Set the default download name
        )
        return response
    else:
        return jsonify({'prediction': prediction.tolist(), 'error': 'Failed to generate molecule image'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
