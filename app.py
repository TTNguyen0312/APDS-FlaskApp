from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask import request, jsonify
import os

app = Flask(__name__)

db_path = os.path.join(os.path.dirname(__file__), 'sdms.db')
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

@app.route('/')
def index():
    clothes = Clothes.query.all()
    clothes = [cloth.json() for cloth in clothes]
    return clothes

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



@app.route('/add', methods=['POST'])
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


if __name__ == '__main__':
    app.run(debug=True)