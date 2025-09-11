from flask import Flask, render_template, jsonify, request, url_for
from collections import defaultdict
from datetime import datetime
from typing import DefaultDict, List, Dict, Any
import uuid

app = Flask(__name__)

reviews_store: DefaultDict[str, List[Dict[str, Any]]] = defaultdict(list)

# In-memory store (mock)
reviews_store: DefaultDict[str, List[Dict[str, Any]]] = defaultdict(list)

def make_review(cloth_id: str, title: str, text: str) -> Dict[str, Any]:
    return {
        "reviewId": str(uuid.uuid4()),
        "clothId": str(cloth_id),
        "reviewTitle": title,
        "reviewText": text,
        "recommended": False, 
        "positiveFeedbackCount": 0,
        "createdAt": datetime.utcnow().isoformat() + "Z",
    }

def seed_mock_reviews() -> None:
    # seed ít review cho demo
    if not reviews_store["1"]:
        reviews_store["1"].extend([
            make_review("1", "Nice quality", "Fabric is soft and comfy. True to size."),
            make_review("1", "Good but a bit thin", "Looks great, slightly thin for winter."),
            make_review("1", "Not my style", "Color looks different from photos on my screen."),
        ])
    if not reviews_store["2"]:
        reviews_store["2"].extend([
            make_review("2", "Excellent fit", "Fits perfectly. Will buy again."),
        ])

seed_mock_reviews()

@app.route('/')
def home():
    return render_template('landingPage.html')

@app.route('/item/<int:cloth_id>', methods=['GET'])
def item_detail(cloth_id):
    # MOCK demo
    images = [
        url_for('static', filename='img/clothes.jpg'),
        url_for('static', filename='img/placeholder-120x120.png'),
        url_for('static', filename='img/placeholder-120x120.png'),
        url_for('static', filename='img/placeholder-120x120.png'),
        url_for('static', filename='img/placeholder-120x120.png'),
        url_for('static', filename='img/placeholder-120x120.png'),
    ]
    # dữ liệu “cloth” theo spec
    cloth = {
        "clothTitle": f"Clothes {cloth_id}",
        "clothDescription": "This is a sample product detail page.",
        "price": 100000,
        "brand": "Business’ name",
        "images": images,
    }

    # --- Content negotiation: JSON khi Accept: application/json hoặc ?format=json ---
    wants_json = (
        request.args.get("format") == "json" or
        request.accept_mimetypes["application/json"] >= request.accept_mimetypes["text/html"]
    )
    if wants_json:
        return jsonify({"items": [cloth]})

    # --- HTML (server-side render) ---
    product = {
        "id": cloth_id,
        "name": cloth["clothTitle"],
        "description": cloth["clothDescription"],
        "price": cloth["price"],
        "brand": cloth["brand"],
        "main_image": images[0] if images else None,
        "thumbs": images[1:] if len(images) > 1 else [],
    }
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

if __name__ == '__main__':
    app.run(debug=True)