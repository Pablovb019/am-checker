import inspect

from flask import Flask, render_template, request, jsonify, session, after_this_request
from urllib.parse import urlparse
from waitress import serve
from datetime import datetime, timedelta
from werkzeug.middleware.proxy_fix import ProxyFix

import requests
import secrets
import tldextract
import step1.stores.amazon as amazon
from step1.utilities.logger import Logger
import step2.classifier as cl
import db
import gc
import os
from numba import cuda

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")
tracked_ids = set()

def load_tracked_ids():
	try:
		tracked_ids = db.get_tracked_ids()
		return tracked_ids
	except Exception as e:
		Logger.error(f"An error occurred while loading tracked IDs: {e}")
		return set()

def get_full_class_name(obj):
	module = obj.__class__.__module__
	if module is None or module == str.__class__.__module__:
		return obj.__class__.__name__
	return module + '.' + obj.__class__.__name__

@app.before_request
def track_new_user():
	if request.endpoint == "static":
		return

	device_id = request.cookies.get("device_id")
	if not device_id:
		device_id = secrets.token_hex(16)
		@after_this_request
		def set_device_id(response):
			response.set_cookie("device_id", device_id, max_age=60*60*24*365, httponly=True)
			return response

	if device_id in tracked_ids:
		Logger.info(f"User already tracked. Device ID: {device_id}")
		return

	try:
		db.insert_new_user(device_id)
		tracked_ids.add(device_id)
		Logger.warning(f"New user detected. Device ID: {device_id}")
	except Exception as e:
		error_message = e.args[0]
		function_name = inspect.currentframe().f_code.co_name
		exception_class = get_full_class_name(e)
		file_name = os.path.basename(__file__)

		Logger.error(f"An error was captured inserting new user. Details below.\n- File: {file_name}\n- Function: {function_name} \n- Exception: {exception_class}: {error_message}")
@app.route("/")
@app.route("/index")
def index():
	Logger.info("Loading main page...")
	return render_template("index.html")

@app.route("/result/<product_id>")
def results(product_id):
	Logger.info(f"Loading product and reviews for product_id: '{product_id}'...")
	try:
		reviews = db.load_reviews(product_id)
		product = db.load_product(product_id)

		for review in reviews:
			date_split = str(review['date']).split("-")
			review['date'] = f"{date_split[2]}/{date_split[1]}/{date_split[0]}"

		Logger.success(f"Product and reviews loaded successfully for product_id: '{product_id}'.")

		authenticity_distribution = {
			'0-20': int(0),
			'20-40': int(0),
			'40-60': int(0),
			'60-80': int(0),
			'80-100': int(0)
		}

		for review in reviews:
			score = review['ml_predict'] * 100
			if score <= 20:
				authenticity_distribution['0-20'] += 1
			elif score <= 40:
				authenticity_distribution['20-40'] += 1
			elif score <= 60:
				authenticity_distribution['40-60'] += 1
			elif score <= 80:
				authenticity_distribution['60-80'] += 1
			else:
				authenticity_distribution['80-100'] += 1

		authenticity_distribution = {k: int(v) for k, v in authenticity_distribution.items()}
		return render_template("analysis.html", product=product, reviews=reviews, authenticity_distribution=authenticity_distribution)
	except Exception as e:
		error_message = e.args[0]
		function_name = inspect.currentframe().f_code.co_name
		exception_class = get_full_class_name(e)
		file_name = os.path.basename(__file__)

		Logger.error(f"An error was captured loading product and reviews. Details below.\n- File: {file_name}\n- Function: {function_name} \n- Exception: {exception_class}: {error_message}")
		return render_template("error.html", error_route="Result"), 500


@app.route("/recent")
def recents():
	Logger.info("Loading recent products...")
	time_threshold = datetime.now() - timedelta(hours=24)
	try:
		recent_products = db.get_recent_products(time_threshold)
		Logger.success(f"Recent products loaded successfully.")
		return render_template("recent.html", recent_products=recent_products)
	except Exception as e:
		error_message = e.args[0]
		function_name = inspect.currentframe().f_code.co_name
		exception_class = get_full_class_name(e)
		file_name = os.path.basename(__file__)

		Logger.error(f"An error was captured loading recent products. Details below.\n- File: {file_name}\n- Function: {function_name} \n- Exception: {exception_class}: {error_message}")
		return render_template("error.html", error_route="Recents"), 500

@app.route("/stats")
def stats():
	Logger.info("Loading site statistics...")
	try:
		site_stats = db.get_site_stats()
		Logger.success(f"Site statistics loaded successfully.")
		return render_template("stats.html", site_stats=site_stats)
	except Exception as e:
		error_message = e.args[0]
		function_name = inspect.currentframe().f_code.co_name
		exception_class = get_full_class_name(e)
		file_name = os.path.basename(__file__)

		Logger.error(f"An error was captured loading site stats. Details below.\n- File: {file_name}\n- Function: {function_name} \n- Exception: {exception_class}: {error_message}")
		return render_template("error.html", error_route="Stats"), 500

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
	Logger.info("Starting Flask Server. Initialising Waitress WSGI server...")
	tracked_ids.update(load_tracked_ids()) # Load tracked IDs into memory
	serve(app, host='0.0.0.0', port=5000, threads=8)
	# app.run(debug=True, host='0.0.0.0', use_reloader=False)
