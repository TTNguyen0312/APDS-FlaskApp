from flask import Flask, render_template

app = Flask(__name__)



@app.route('/')
def home():
    return render_template("search.html")

# give the same view an extra endpoint called 'search'
app.add_url_rule("/search", endpoint="search", view_func=home)

if __name__ == '__main__':
    app.run(debug=True)