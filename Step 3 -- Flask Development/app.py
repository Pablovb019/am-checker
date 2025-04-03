from flask import Flask, render_template, request, jsonify
from urllib.parse import urlparse
from waitress import serve
import requests
import tldextract
import step1.stores.amazon as amazon
from step1.utilities.logger import Logger
import step2.classifier as cl
import db
import gc
from numba import cuda

app = Flask(__name__)
@app.route("/")
@app.route("/index")
def index():
	return render_template("index.html")

@app.route("/result/<product_id>")
def results(product_id):
	Logger.info(f"Loading product and reviews for product_id: '{product_id}'...")
	reviews = db.load_reviews(product_id)
	product = db.load_product(product_id)
	Logger.success(f"Product and reviews loaded successfully for product_id: '{product_id}'.")
	return render_template("result.html", product=product, reviews=reviews)

@app.route('/api/validate-url', methods=['POST'])
def validate_url():
	data = request.json

	parsed = urlparse(data.get('url', ''))
	if not parsed.scheme or not parsed.netloc:
		return jsonify({"isValid": False}), 400, {'Content-Type': 'application/json; charset=utf-8'}

	url = parsed.geturl()

	try:
		header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
		response = requests.get(url, headers=header, timeout=10)
		if response.status_code == 200:
			return jsonify({"isValid": True}), 200, {'Content-Type': 'application/json; charset=utf-8'}
		else:
			return jsonify({"isValid": False}), response.status_code, {'Content-Type': 'application/json; charset=utf-8'}

	except Exception as e:
		return jsonify({"isValid": False, "error": str(e)}), 500, {'Content-Type': 'application/json; charset=utf-8'}

	finally:
		gc.collect()
		cuda.current_context().deallocations.clear()

@app.route('/api/fetch-reviews', methods=['POST'])
def fetch_reviews():
	data = request.json.get('payload', {})
	url = data.get('url', '')

	# Clean URL just in case
	url = url.split("/dp/")[0] + "/dp/" + url.split("/dp/")[1].split("/")[0]  # Remove any extra characters from the URL
	if '?' in url:
		url = url.split("?")[0]

	try:
		country_suffix = tldextract.extract(url).suffix
		product_id, reviews = amazon.amazon_exec(url, country_suffix)
		return jsonify({"product_id": product_id, "reviews": reviews}), 200, {'Content-Type': 'application/json; charset=utf-8'}
	except Exception as e:
		raised_error_message = e.args[0]
		raised_function_name = e.args[1]
		raised_file = e.args[2]
		raised_exception_class = e.args[3]

		Logger.error(f"An error was captured obtaining Amazon reviews. Details below.\n- File: {raised_file}\n- Function: {raised_function_name} \n- Exception: {raised_exception_class}: {raised_error_message}")
		return jsonify({"error": str(e)}), 500, {'Content-Type': 'application/json; charset=utf-8'}
	finally:
		gc.collect()
		cuda.current_context().deallocations.clear()


@app.route('/api/ml-model-analysis', methods=['POST'])
def apply_ml_model():
	data = request.json.get('payload', {})
	product_id = data.get('product_id', '')
	reviews = data.get('reviews', [])

	try:
		results = cl.predict(product_id, reviews)
		return jsonify({"results": results}), 200, {'Content-Type': 'application/json; charset=utf-8'}

	except Exception as e:
		raised_error_message = e.args[0]
		raised_function_name = e.args[1]
		raised_file = e.args[2]
		raised_exception_class = e.args[3]

		Logger.error(f"An error was captured applying the ML model. Details below.\n- File: {raised_file}\n- Function: {raised_function_name} \n- Exception: {raised_exception_class}: {raised_error_message}")
		return jsonify({"error": str(e)}), 500, {'Content-Type': 'application/json; charset=utf-8'}

	finally:
		gc.collect()
		cuda.current_context().deallocations.clear()

if __name__ == '__main__':
	Logger.info("Starting Flask Development")
	# serve(app, host='0.0.0.0', port=8080)
	app.run(debug=True, port=8080, host='0.0.0.0', use_reloader=False)