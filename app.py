import logging
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import pandas as pd
import numpy as np
import os
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Activation, Dropout, LeakyReLU
from PIL import Image
from fungsi import make_model
import requests
from bs4 import BeautifulSoup
from flask_cors import CORS

# Konfigurasi logging
logging.basicConfig(level=logging.DEBUG)

# =[Variabel Global]=============================

app = Flask(__name__, static_url_path='/static')
CORS(app)

app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.JPG']
app.config['UPLOAD_PATH'] = './static/images/uploads/'

model = None

NUM_CLASSES = 2
bottle_class = ["HDPE", "PET"]

# Memuat model
try:
    model = make_model()
    model.load_weights("DenseNet201.h5")
    logging.debug("Model loaded successfully")
except Exception as e:
    logging.error(f"Error loading model: {e}")

# =[Routing]=====================================

# [Routing untuk Halaman Utama atau Home]
@app.route("/")
def beranda():
    return render_template('index.html')

# [Routing untuk API]
@app.route("/api/deteksi", methods=['POST'])
def apiDeteksi():
    try:
        logging.debug("Received request for /api/deteksi")

        # Set nilai default untuk hasil prediksi dan gambar yang diprediksi
        hasil_prediksi = '(none)'
        gambar_prediksi = '(none)'
        akurasi_prediksi = 0.0

        # Get File Gambar yg telah diupload pengguna
        uploaded_file = request.files['file']
        filename = secure_filename(uploaded_file.filename)

        logging.debug(f"Filename received: {filename}")

        # Periksa apakah ada file yg dipilih untuk diupload
        if filename != '':
            # Set/mendapatkan extension dan path dari file yg diupload
            file_ext = os.path.splitext(filename)[1]
            gambar_prediksi = '/static/images/uploads/' + filename

            logging.debug(f"File extension: {file_ext}, file path: {gambar_prediksi}")

            # Periksa apakah extension file yg diupload sesuai (jpg)
            if file_ext in app.config['UPLOAD_EXTENSIONS']:
                # Simpan Gambar
                uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
                logging.debug(f"File saved to {gambar_prediksi}")

                # Memuat Gambar
                test_image = Image.open('.' + gambar_prediksi)

                # Mengubah Ukuran Gambar
                test_image_resized = test_image.resize((224, 224))

                # Konversi Gambar ke Array
                image_array = np.array(test_image_resized)
                test_image_x = (image_array / 255.0) - 0.5
                test_image_x = np.expand_dims(test_image_x, axis=0)

                # Prediksi Gambar
                y_pred_test_single = model.predict(test_image_x)
                y_pred_test_classes_single = np.argmax(y_pred_test_single, axis=1)
                akurasi_prediksi = np.max(y_pred_test_single)

                hasil_prediksi = bottle_class[y_pred_test_classes_single[0]]

                logging.debug(f"Prediction: {hasil_prediksi}, Accuracy: {akurasi_prediksi}")

                # Return hasil prediksi dengan format JSON
                return jsonify({
                    "prediksi": hasil_prediksi,
                    "gambar_prediksi": gambar_prediksi,
                    "akurasi": float(akurasi_prediksi)
                })
            else:
                logging.debug("Invalid file extension")
                return jsonify({
                    "prediksi": hasil_prediksi,
                    "gambar_prediksi": gambar_prediksi,
                    "akurasi": akurasi_prediksi
                })
    except Exception as e:
        logging.error(f"Error during prediction: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/get-news', methods=['GET'])
def get_news():
    try:
        logging.debug("Fetching news from URL")
        url = 'https://www.nytimes.com/search?dropmab=false&query=plastic%20bottle%20waste&sort=newest'
        response = requests.get(url)
        response.raise_for_status()
        logging.debug("Successfully fetched news data")

        soup = BeautifulSoup(response.text, 'html.parser')

        articles = soup.find_all('div', class_='css-1i8vfl5')
        berita = []

        logging.debug(f"Found {len(articles)} articles")
        for article in articles[:3]:
            title_tag = article.find('h4')
            summary_tag = article.find('p', class_='css-16nhkrn')
            link_tag = article.find('a')
            image_tag = article.find('img', class_='css-rq4mmj')

            title = title_tag.text.strip() if title_tag else 'No title'
            summary = summary_tag.text.strip() if summary_tag else ''
            link = link_tag['href'] if link_tag else '#'
            image = image_tag['src'] if image_tag else ''

            if not link.startswith('http'):
                link = 'https://www.nytimes.com/' + link

            logging.debug(f"Article title: {title}, link: {link}")
            berita.append({'title': title, 'summary': summary, 'link': link, 'image': image})

        return jsonify(berita)
    except Exception as e:
        logging.error(f"Error during web scraping: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Run Flask di localhost
    app.run(host="localhost", port=5000, debug=True)
