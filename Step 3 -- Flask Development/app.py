from flask import Flask, render_template, request, jsonify
from waitress import serve
import requests

import tldextract
import step1.stores.amazon as amazon
import step1.utilities.globals as gl

app = Flask(__name__)

@app.route("/")
@app.route("/index")
def index():
	return render_template("index.html")


@app.route('/api/validate-url', methods=['POST'])
def validate_url():
	data = request.json
	url = data.get('url', '')

	try:
		header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
		response = requests.get(url, headers=header, timeout=10)
		if response.status_code == 200:
			return jsonify({"isValid": True}), 200
		else:
			return jsonify({"isValid": False}), response.status_code

	except Exception as e:
		return jsonify({"isValid": False, "error": str(e)}), 500

@app.route('/api/fetch-reviews', methods=['POST'])
def fetch_reviews():
	data = request.json
	url = data.get('url', '')

	# Clean URL just in case
	url = url.split("/dp/")[0] + "/dp/" + url.split("/dp/")[1].split("/")[0]  # Remove any extra characters from the URL
	if '?' in url:
		url = url.split("?")[0]

	try:
		country_suffix = tldextract.extract(url).suffix
		product_info, reviews = amazon.amazon_exec(url, country_suffix)
		return jsonify({"product_info": product_info, "reviews": reviews}), 200
	except Exception as e:
		return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
	print("Starting Flask Development")
	# serve(app, host='0.0.0.0', port=8080)
	app.run(debug=True, port=8080, host='0.0.0.0', use_reloader=False)