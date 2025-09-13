from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask import request, jsonify
import os
from functions.predict import fused_predict
import pandas as pd
from nltk.tokenize import RegexpTokenizer
from functions.tokenizer import tokenize_df


app = Flask(__name__)

db_path = os.path.join(os.path.dirname(__file__), 'data/sdms.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Clothes(db.Model):
    ClothingID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ClothTitle = db.Column(db.String, nullable=False)
    ClothDescription = db.Column(db.Text, nullable=True)
    Department = db.Column(db.String, nullable=True)
    ClassName = db.Column(db.String, nullable=True)
    DivisionName = db.Column(db.String, nullable=True)
    PositiveFeedbackCount = db.Column(db.Integer, default=0)

    def json(self):
        return {
            'ClothingID': self.ClothingID,
            'ClothTitle': self.ClothTitle,
            'ClothDescription': self.ClothDescription,
            'Department': self.Department,
            'ClassName': self.ClassName,
            'DivisionName': self.DivisionName,
            'PositiveFeedbackCount': self.PositiveFeedbackCount
        }
        
        
class Reviews(db.Model):
    ReviewID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ClothingID = db.Column(db.Integer, db.ForeignKey('clothes.ClothingID'), nullable=False)
    Age = db.Column(db.Integer, nullable=True)
    ReviewTitle = db.Column(db.String, nullable=False)
    ReviewText = db.Column(db.Text, nullable=False)
    Rating = db.Column(db.Integer, nullable=False)
    Recommended = db.Column(db.Integer, nullable=False)  # 0 or 1

    def json(self):
        return {
            "ReviewID": self.ReviewID,
            "ClothingID": self.ClothingID,
            "Age": self.Age,
            "ReviewTitle": self.ReviewTitle,
            "ReviewText": self.ReviewText,
            "Rating": self.Rating,
            "Recommended": self.Recommended
        }



@app.route('/clothes')
def index():
    clothes = Clothes.query.all()
    clothes = [cloth.json() for cloth in clothes]
    return clothes

@app.route('/reviews')
def get_reviews():
    reviews = Reviews.query.all()
    reviews = [review.json() for review in reviews]
    return reviews

@app.route('/clothes/<int:clothId>', methods=['GET'])
def get_cloth_by_id(clothId):
    cloth = Clothes.query.filter_by(ClothingID=clothId).first()
    if not cloth:
        return jsonify({"items": []}), 404   # return empty list if not found

    return jsonify({
        "items": [cloth.json()]   # wrap inside `items` list
    })
    

@app.route('/reviews/<int:clothId>', methods=['GET'])
def get_review_by_clothid(clothId):
    reviews = Reviews.query.filter_by(ClothingID=clothId).all()
    if not reviews:
        return jsonify({"items": []}), 404   # return empty list if not found

    return jsonify({
        "items": [review.json() for review in reviews]   # wrap inside `items` list
    })


@app.route('/search', methods=['POST'])
def search():
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form  # fallback to form data

    keyword = data.get("keyword", "").lower()
    if not keyword:
        return jsonify({"message": "No keyword provided"}), 400

    # Simple plural handling
    if keyword.endswith("es"):
        singular = keyword[:-2]
    elif keyword.endswith("s"):
        singular = keyword[:-1]
    else:
        singular = keyword + "s"

    results = Clothes.query.filter(
        (Clothes.ClothTitle.ilike(f"%{keyword}%")) | 
        (Clothes.ClothTitle.ilike(f"%{singular}%")) |
        (Clothes.ClothDescription.ilike(f"%{keyword}%")) |
        (Clothes.ClothDescription.ilike(f"%{singular}%"))
    ).all()

    return jsonify({
        "count": len(results),
        "items": [c.json() for c in results]
    })



@app.route('/add-cloth', methods=['POST'])
def add_cloth():
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form  # fallback to form data

    new_item = Clothes(
        ClothTitle=data.get('ClothTitle'),
        ClothDescription=data.get('ClothDescription'),
        Department=data.get('Department'),
        ClassName=data.get('ClassName'),
        DivisionName=data.get('DivisionName'),
        PositiveFeedbackCount=data.get('PositiveFeedbackCount', 0)
    )

    db.session.add(new_item)
    db.session.commit()

    return jsonify(new_item.json()), 201

@app.route('/add-review', methods=['POST'])
def add_review():
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form  # fallback to form data

    # --- Create new Review ---
    new_item = Reviews(
        ClothingID=data.get('ClothingID'),
        ReviewTitle=data.get('Title'),
        ReviewText=data.get('Description'),   # assuming you named column "Text" in Reviews model
        Age=data.get('Age'),
        Rating=data.get('Rating'),
        Recommended=0   # default, will update after fused_predict
    )
    db.session.add(new_item)
    db.session.commit()

    # --- Run prediction ---
    # Combine ReviewTitle and ReviewText safely
    combined_text = f"{new_item.ReviewTitle or ''} {new_item.ReviewText or ''}".strip()

    # Wrap into a DataFrame
    predict_df = pd.DataFrame({"Text": [combined_text]})

    # Apply tokenizer
    predict_df["tokens"] = tokenize_df(predict_df["Text"])

    # Pass tokenized data to fused_predict
    prediction_result = fused_predict(predict_df["tokens"], word_dict={})
    recommend = int(prediction_result["fused_prediction"])  # 0 or 1
    new_item.Recommended = recommend

    # --- Update PositiveFeedbackCount if recommended ---
    # if recommend == 1:
    #     cloth = Clothes.query.get(new_item.ClothingID)
    #     if cloth:
    #         cloth.PositiveFeedbackCount = cloth.PositiveFeedbackCount + 1

    db.session.commit()

    return {
        "message": "Review added successfully",
        "review": new_item.json(),
        "prediction": recommend
    }, 201





if __name__ == '__main__':
    app.run(debug=True)