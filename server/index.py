from flask import Flask, request, jsonify, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from flask_cors import CORS
from flask_restful import Api, Resource
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:password@localhost/teen_guard_alliance'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # It's a good practice to disable this unless needed
app.config['UPLOAD_FOLDER'] = 'uploads'
db = SQLAlchemy(app)
api = Api(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(80), nullable=False)
    lastName = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)  # Ensure email is unique
    password = db.Column(db.String(80), nullable=False)
    cpassword = db.Column(db.String(80), nullable=False)
    
    def __repr__(self):
        return '<User %r>' % self.firstName


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"Message('{self.name}', '{self.email}', '{self.subject}', '{self.message}')"
    
class Testimony(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    position = db.Column(db.String(80), nullable=False)
    message = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    picture = db.Column(db.String(120), nullable=False)

class Resources(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(80), nullable=False)
    introduction = db.Column(db.String(80), nullable=False)
    body = db.Column(db.Text, nullable=False)

class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    contact = db.Column(db.String(200), nullable=True)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"Chat('{self.name}', '{self.contact}','{self.subject}', '{self.message}')"
# Create all tables if they do not exist
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return 'Welcome to Teen Guard Alliance.'

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    firstName = data.get('firstName')
    lastName = data.get('lastName')
    email = data.get('email')
    password = data.get('password')
    cpassword = data.get('cpassword')
    
    if password != cpassword:
        return jsonify({'message': 'Passwords do not match'}), 400
    
    try:
        new_user = User(firstName=firstName, lastName=lastName, email=email, password=password, cpassword=cpassword)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'User registered successfully', 'redirect_url': './login.html'})
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({'message': 'Username or email already exists', 'error': str(e)}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'An error occurred', 'error': str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    firstName = data.get('firstName')
    password = data.get('password')
    user = User.query.filter_by(firstName=firstName, password=password).first()
    if user:
        return jsonify({'message': 'Login successful', 'redirect_url': './dashboard.html'})
    else:
        return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.get_json()

    if not data or not all(key in data for key in ('name', 'email', 'subject', 'message')):
        return jsonify({'error': 'Invalid input'}), 400

    new_message = Message(
        name=data['name'],
        email=data['email'],
        subject=data['subject'],
        message=data['message']
    )
    
    db.session.add(new_message)
    db.session.commit()
    
    return jsonify({'message': 'Message sent successfully'}), 201

@app.route('/messages', methods=['GET'])
def get_messages():
    messages = Message.query.all()
    return jsonify([{
        'name': msg.name,
        'email': msg.email,
        'subject': msg.subject,
        'message': msg.message,
    } for msg in messages])

class TestimonyMessage(Resource):
    def post(self):
        name = request.form['name']
        position = request.form['position']
        message = request.form['message']
        email = request.form['email']
        
        if 'picture' not in request.files:
            return {'message': 'No picture file'}, 400
        
        picture = request.files['picture']
        if picture.filename == '':
            return {'message': 'No selected picture'}, 400

        filename = secure_filename(picture.filename)
        picture_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        picture.save(picture_path)

        new_testimony = Testimony(name=name, position=position, message=message, email=email, picture=picture_path)
        db.session.add(new_testimony)
        db.session.commit()

        return jsonify({
            'id': new_testimony.id,
            'name': new_testimony.name,
            'position': new_testimony.position,
            'message': new_testimony.message,
            'email': new_testimony.email,
            'picture': new_testimony.picture
        })

api.add_resource(TestimonyMessage, '/testimony')

class TestimoniesMessage(Resource):
    def get(self):
        testimonies = Testimony.query.all()
        response = []
        
        for testimony in testimonies:
            picture_url = f"uploads/{os.path.basename(testimony.picture)}"
            
            response.append({
                'id': testimony.id,
                'name': testimony.name,
                'position': testimony.position,
                'message': testimony.message,
                'email': testimony.email,
                'picture': picture_url
            })
        
        return jsonify(response)

api.add_resource(TestimoniesMessage, '/testimonies')

class ResourceEndpoint(Resource):
    def post(self):
        data = request.get_json()

        if not data or not all(key in data for key in ('subject', 'introduction', 'body')):
            return {'message': 'Missing fields'}, 400

        new_resource = Resources(
            subject=data['subject'],
            introduction=data['introduction'],
            body=data['body']
        )

        db.session.add(new_resource)
        db.session.commit()

        return jsonify({
            'id': new_resource.id,
            'subject': new_resource.subject,
            'introduction': new_resource.introduction,
            'body': new_resource.body
        })

api.add_resource(ResourceEndpoint, '/resources')


@app.route('/send_chat', methods=['POST'])
def send_chat():
    data = request.get_json()
    if not data or not all(key in data for key in ('name','contact','subject', 'message')):
        return jsonify({'error': 'Invalid input'}), 400

    new_chat = Chat(
        name=data['name'],
        contact=data['contact'],
        subject=data['subject'],
        message=data['message']
    )
    
    db.session.add(new_chat)
    db.session.commit()
    
    return jsonify({'message': 'Chat sent successfully'}), 201

@app.route('/chats', methods=['GET'])
def get_chats():
    chats = Chat.query.all()
    return jsonify([{
       
        'name': chat.name,
        'contact': chat.contact,
        'subject': chat.subject,
        'message': chat.message,
    } for chat in chats])


if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True, port=3400)
