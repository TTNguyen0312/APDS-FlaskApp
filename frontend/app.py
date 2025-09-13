import os

import requests
from flask import Flask, render_template, jsonify, request, url_for
from collections import defaultdict
from datetime import datetime
from typing import DefaultDict, List, Dict, Any
import uuid
from dotenv import load_dotenv


load_dotenv()

app = Flask(__name__)

reviews_store: DefaultDict[str, List[Dict[str, Any]]] = defaultdict(list)
backend_url = os.getenv("BACKEND_URL", "http://localhost:5000")

@app.route('/')
def home():
    try:
        response = requests.get(f"{backend_url}/clothes")
        response.raise_for_status()
        items = response.json()
    except Exception as e:
        print("Error fetching clothes:", e)
        items = []
    return render_template("LandingPage.html", items=items)


@app.route('/item/<int:cloth_id>', methods=['GET'])
def item_detail(cloth_id):
    try:
        response = requests.get(f"{backend_url}/clothes/{cloth_id}")
        response.raise_for_status()
        data = response.json()
        # assuming API returns a dict with keys: ClothTitle, ClothDescription, Department, DivisionName, price, images
        cloth = data.get("items", [{}])[0]
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
    }
    print("Product details:", product)

    return render_template('ProductDetail.html', product=product)


# ---------- CREATE REVIEW (POST /review) ----------
@app.post('/review')
def create_review():
    try:
        data = request.get_json(force=True) or {}
    except Exception:
        return jsonify({"message": "Invalid JSON body", "review": None}), 400

    cloth_id = str(data.get("clothId") or "").strip()
    title = (data.get("reviewTitle") or "").strip()
    text = (data.get("reviewText") or "").strip()

    if not cloth_id:
        return jsonify({"message": "clothId is required", "review": None}), 400
    if not title:
        return jsonify({"message": "reviewTitle is required", "review": None}), 400
    if not text:
        return jsonify({"message": "reviewText is required", "review": None}), 400

    review = make_review(cloth_id, title, text)
    reviews_store[cloth_id].insert(0, review)

    return jsonify({"message": "successfully created", "review": review}), 201

# ---------- GET ALL REVIEWS OF A CLOTH (GET /review/<clothId>) ----------
@app.get('/review/<cloth_id>')
def get_reviews(cloth_id):
    items = list(reviews_store.get(str(cloth_id), []))
    items.sort(key=lambda r: r.get("createdAt", ""), reverse=True)
    return jsonify({"message": "success", "review": items}), 200

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
    app.run(host="127.0.0.1", port=8000, debug=True)