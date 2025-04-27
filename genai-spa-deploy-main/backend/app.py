from flask import Flask, request, jsonify
import jwt
import datetime
from flask_cors import CORS
from functools import wraps
from pymongo import MongoClient

app = Flask(__name__)
CORS(app)

# SECRET KEY for JWT
app.config['SECRET_KEY'] = 'your_super_secret_key'

# MongoDB Atlas connection
client = MongoClient('mongodb+srv://khearn2:TQAteslCZE9CvmyE@k08cluster.rpfuvgm.mongodb.net/?retryWrites=true&w=majority&appName=K08Cluster')
db = client['k08db']         # Database name
chart_collection = db['charts']  # Collection name

# --- JWT validation decorator ---
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split()[1]

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = data['user']
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401

        return f(current_user, *args, **kwargs)
    return decorated


# --- Login Route ---
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if username.lower() == 'kyle' and password.lower() == 'kyle':
        token = jwt.encode({
            'user': username,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }, app.config['SECRET_KEY'], algorithm='HS256')

        return jsonify({'token': token})

    return jsonify({'message': 'Invalid credentials'}), 401

# --- Chart Data Endpoints ---
@app.route('/chart1')
@token_required
def chart1(current_user):
    chart = chart_collection.find_one({'chart': 'chart1'})
    if chart:
        return jsonify({
            "labels": chart['labels'],
            "data": chart['data']
        })
    else:
        return jsonify({'message': 'Chart1 not found'}), 404

@app.route('/chart2')
@token_required
def chart2(current_user):
    chart = chart_collection.find_one({'chart': 'chart2'})
    if chart:
        return jsonify({
            "labels": chart['labels'],
            "data": chart['data']
        })
    else:
        return jsonify({'message': 'Chart2 not found'}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3000)
