from flask import Flask, request, jsonify, render_template
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
import os

app = Flask(__name__)

# Load the model (make sure the correct path is provided)
model = load_model('saved_models/autism_model_v1.keras')  # Update the model path

@app.route('/')
def index():
    return render_template('index.html')  # Serve the HTML form

@app.route('/predict', methods=['POST'])
def predict():
    # Check if the 'file' part is in the request
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    # If the file is empty
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        # Save the file temporarily
        file_path = os.path.join('temp', file.filename)
        file.save(file_path)

        # Resize the image
        img = image.load_img(file_path, target_size=(64, 72))  # Resize to (64, 72) to match 4608 features (64*72 = 4608)

        # Convert the image to a numpy array
        img_array = image.img_to_array(img)

        # Flatten the image array
        img_array = img_array.flatten()

        # Reshape to match the expected input shape (1, 4608)
        img_array = np.expand_dims(img_array, axis=0)

        # Normalize the image
        img_array /= 255.0


        # Predict the class
        prediction = model.predict(img_array)


        # Remove the temporary file after prediction
        os.remove(file_path)

        return jsonify({'prediction': prediction.tolist()})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)


