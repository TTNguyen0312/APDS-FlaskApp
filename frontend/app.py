import os
import requests
from flask import Flask, render_template, jsonify, request, url_for
from collections import defaultdict
from datetime import datetime
from typing import DefaultDict, List, Dict, Any
import uuid
from dotenv import load_dotenv
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
CORS(app)

reviews_store: DefaultDict[str, List[Dict[str, Any]]] = defaultdict(list)
backend_url = os.environ.get("BACKEND_URL", "http://localhost:3000")

@app.route('/')
def home():
    try:
        print(f"{backend_url}/clothes")
        response = requests.get(f"{backend_url}/clothes")
        response.raise_for_status()
        items = response.json()
    except Exception as e:
        print("Error fetching clothes:", e)
        items = []
    return render_template("landingPage.html", items=items)


@app.route('/item/<int:cloth_id>', methods=['GET'])
def item_detail(cloth_id):
    try:
        response = requests.get(f"{backend_url}/clothes/{cloth_id}")
        response.raise_for_status()
        data = response.json()
        # assuming API returns a dict with keys: ClothTitle, ClothDescription, Department, DivisionName, price, images
        cloth = data.get("items", [{}])[0]
        reviews_response = requests.get(f"{backend_url}/reviews/{cloth_id}", timeout=5)
        reviews = reviews_response.json().get("items", []) if reviews_response.status_code == 200 else []

    except requests.RequestException as e:
        # fallback if API fails
        return f"Error fetching cloth data: {e}", 500

    # --- Content negotiation: JSON ---
    wants_json = (
        request.args.get("format") == "json" or
        request.accept_mimetypes["application/json"] >= request.accept_mimetypes["text/html"]
    )
    if wants_json:
        return jsonify({"items": [cloth]})

    # --- HTML render ---
    product = {
        "id": cloth_id,
        "ClothTitle": cloth.get("ClothTitle", f"Clothes {cloth_id}"),
        "ClothDescription": cloth.get("ClothDescription", "No description available."),
        "ClassName": cloth.get("ClassName", "Class"),
        "Department": cloth.get("Department", "Fashion"),
        "DivisionName": cloth.get("DivisionName", "Division"),
        "price": cloth.get("price", 0),
        "images": cloth.get("images", []),
        "main_image": cloth.get("images", [None])[0],
        "reviews": reviews
    }

    return render_template('productDetail.html', product=product, backend_url=backend_url)


# ---------- CREATE REVIEW (POST /review) ----------
@app.post('/add-review')
def create_review():
    try:
        data = request.get_json(force=True) or {}
    except Exception:
        return jsonify({"message": "Invalid JSON body", "review": None}), 400

    # Validate required fields
    cloth_id = str(data.get("ClothingID") or 0).strip()
    title = (data.get("ReviewTitle") or "").strip()
    text = (data.get("ReviewText") or "").strip()

    if not cloth_id:
        return jsonify({"message": "ClothingID is required", "review": None}), 400
    if not title:
        return jsonify({"message": "ReviewTitle is required", "review": None}), 400
    if not text:
        return jsonify({"message": "ReviewText is required", "review": None}), 400

    try:
        # Forward request to backend API
        response = requests.post(
            f"{backend_url}/add-review",
            json={
                "ClothingID": cloth_id,
                "Title": title,
                "Description": text,
                "Age": data.get("Age"),
                "Rating": data.get("Rating"),
            },
        )
    except requests.RequestException as e:
        return jsonify({"message": f"Failed to reach backend API: {str(e)}", "review": None}), 502

    if response.status_code != 201:
        return jsonify({"message": "Backend API error", "details": response.text, "review": None}), response.status_code

    return jsonify(response.json()), 201

# ---------- GET ALL REVIEWS OF A CLOTH (GET /review/<clothId>) ----------
@app.get('/review/<cloth_id>')
def get_reviews(cloth_id):
    try:
        # Call your backend API
        response = requests.get(f"{backend_url}/reviews/{cloth_id}", timeout=5)
    except requests.RequestException as e:
        return jsonify({"message": f"Failed to reach backend API: {str(e)}", "review": []}), 502

    if response.status_code != 200:
        return jsonify({"message": "Backend API error", "details": response.text, "review": []}), response.status_code

    # Return backend JSON as-is (or reformat if needed)
    return jsonify(response.json()), 200

@app.route('/search')
def search():
    keyword = request.args.get("q", "").strip()
    page = request.args.get("page", 1, type=int)
    sort = request.args.get("sort", "relevance")
    order = request.args.get("order", "asc")
    per_page = 12

    products = []
    total = 0
    if keyword:
        response = requests.post(f"{backend_url}/search", json={"keyword": keyword})
        products = response.json().get("items", [])
        total = response.json().get("count", 0)

    # Calculate total pages safely
    total_pages = (total + per_page - 1) // per_page if total else 1

    # Slice products for the current page
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    paginated_products = products[start_idx:end_idx]

    # Compute safe page range for template
    start_page = max(1, page - 2)
    end_page = min(total_pages, page + 2)

    return render_template(
        "search.html",
        q=keyword,
        items=paginated_products,
        total=total,
        page=page,
        total_pages=total_pages,
        sort=sort,
        order=order,
        start_page=start_page,
        end_page=end_page
    )



if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # default to 8000 locally
    app.run(host="0.0.0.0", port=port, debug=True)