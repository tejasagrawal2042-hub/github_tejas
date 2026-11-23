import os
import json
from flask import Flask, redirect, render_template, request, url_for , jsonify
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import PyMongoError
app = Flask(__name__)
MONGO_URI = os.getenv("MONGO_URI")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data.json")
client = MongoClient(MONGO_URI)
db = client["mydatabase"] 
collection = db["users"]  
todo_collection = db["todos"]

@app.route("/submittodoitem", methods=["POST"])
def submit_todo_item():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided."}), 400

    item_name = data.get("itemName", "").strip()
    item_description = data.get("itemDescription", "").strip()

    if not item_name or not item_description:
        return jsonify({"error": "Both Item Name and Item Description are required."}), 400

    try:
        todo_collection.insert_one({
            "itemName": item_name,
            "itemDescription": item_description
        })
        return jsonify({"message": "To-Do item added successfully!"}), 201
    except PyMongoError as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

@app.route("/api", methods=["GET"])
def get_data():
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
        return jsonify(data)
    
@app.route("/", methods=["GET", "POST"])
def index():
    error = None
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        if not name or not email:
            error = "Both Name and Email are required."
            return render_template("form.html", error=error)

        try:
            collection.insert_one({"name": name, "email": email})
            return redirect(url_for("success"))
        except PyMongoError as e:
            error = f"Database error: {str(e)}"
        except Exception as e:
            error = f"An unexpected error occurred: {str(e)}"
    return render_template("form.html", error=error)

@app.route("/success")
def success():
    return render_template("success.html")

if __name__ == "__main__":
    app.run(debug=True)
