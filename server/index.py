from flask import Flask, request, jsonify, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from flask_cors import CORS
from flask_restful import Api, Resource
from werkzeug.security import generate_password_hash, check_password_hash
import os
import logging
from werkzeug.utils import secure_filename

# Configure Flask app
app = Flask(__name__)
CORS(app)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:password@localhost/teen_guard_alliance'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
db = SQLAlchemy(app)
api = Api(app)
# Setup Logging
logging.basicConfig(level=logging.DEBUG)
app.logger.setLevel(logging.DEBUG)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(80), nullable=False)
    lastName = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'<User {self.firstName}>'

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

class Resources(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(80), nullable=False)
    introduction = db.Column(db.String(80), nullable=False)
    body = db.Column(db.Text, nullable=False)

class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    contact = db.Column(db.String(200), nullable=True)
    email= db.Column(db.String(200), nullable=True)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)

    
class Provider(db.Model):  # Ensure this model exists
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    role = db.Column(db.String(50), nullable=False)

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
    role = data.get('role')

    if password != cpassword:
        app.logger.error('Passwords do not match')
        return jsonify({'message': 'Passwords do not match'}), 400

    if not all([firstName, lastName, email, password, role]):
        app.logger.error('Missing fields')
        return jsonify({'message': 'Missing fields'}), 400

    try:
        hashed_password = generate_password_hash(password)
        new_user = User(firstName=firstName, lastName=lastName, email=email, password=hashed_password, role=role)
        db.session.add(new_user)
        db.session.commit()
        app.logger.info('User registered successfully')
        return jsonify({'message': 'User registered successfully', 'redirect_url': './login.html'})
    except IntegrityError as e:
        db.session.rollback()
        app.logger.error(f'Email already exists: {e}')
        return jsonify({'message': 'Email already exists', 'error': str(e)}), 409
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'Error registering user: {e}')
        return jsonify({'message': 'An error occurred', 'error': str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not data.get('firstName') or not data.get('password'):
        app.logger.error('FirstName or password missing')
        return jsonify({'message': 'FirstName and password are required'}), 400
    
    firstName = data.get('firstName')
    password = data.get('password')
    
    user = User.query.filter_by(firstName=firstName).first()
    
    if user and check_password_hash(user.password, password):
        app.logger.info(f'Login successful for user: {firstName}')
        
        # Redirect based on user role
        if user.role == 'admin':
            redirect_url = './admin_dashboard.html'
        elif user.role == 'teenager':
            redirect_url = './teenager_dashboard.html'
        elif user.role == 'educator':
            redirect_url = './educator_dashboard.html'
        elif user.role == 'health_care_giver':
            redirect_url = './health_care_provider.html'
        else:
            redirect_url = './login.html'
        
        return jsonify({'message': 'Login successful', 'redirect_url': redirect_url})
    else:
        app.logger.warning(f'Invalid login attempt for user: {firstName}')
        return jsonify({'message': 'Invalid credentials'}), 401


@app.route('/send_chat', methods=['POST'])
def send_chat():
    data = request.json
    new_message = Chat(
        name=data['name'],
        contact=data['contact'],
        email=data['email'],
        subject=data['subject'],
        message=data['message']
    )
    db.session.add(new_message)
    db.session.commit()
    return jsonify({'message': 'Message sent successfully!'})


@app.route('/get_chats', methods=['GET'])
def get_chats():
    try:
        messages = Chat.query.all()
        return jsonify([{
            'id': msg.id,
            'name': msg.name,
            'contact': msg.contact,
            'email':msg.email,
            'subject': msg.subject,
            'message': msg.message,
        } for msg in messages])
    except Exception as e:
        app.logger.error(f'Error retrieving chats: {e}')
        return jsonify({'error': str(e)}), 500

@app.route('/get_providers', methods=['GET'])
def get_providers():
    try:
        providers = Provider.query.filter_by(role='health_care_giver').all()
        return jsonify([{
            'id': provider.id,
            'first_name': provider.first_name
        } for provider in providers])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/transfer_chat', methods=['POST'])
def transfer_chat():
    try:
        data = request.json
        chat_id = data.get('chat_id')
        provider_id = data.get('provider_id')

        chat = Chat.query.get(chat_id)
        if chat:
            chat.status = 'Transferred'
            chat.provider_id = provider_id
            db.session.commit()
            return jsonify({'message': 'Chat successfully transferred'}), 200
        else:
            return jsonify({'message': 'Chat not found'}), 404
    except IntegrityError as e:
        db.session.rollback()
        app.logger.error(f'IntegrityError: {e}')
        return jsonify({'error': 'Database integrity error'}), 500
    except Exception as e:
        app.logger.error(f'Error transferring chat: {e}')
        return jsonify({'error': 'Internal Server Error'}), 500


@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.get_json()
    
    app.logger.debug(f'Received data: {data}')
    
    if not data or not all(key in data for key in ('name', 'email', 'subject', 'message')):
        app.logger.error('Invalid input')
        return jsonify({'error': 'Invalid input'}), 400

    new_message = Message(
        name=data['name'],
        email=data['email'],
        subject=data['subject'],
        message=data['message']
    )
    
    try:
        db.session.add(new_message)
        db.session.commit()
        app.logger.info('Message sent successfully')
        return jsonify({'message': 'Message sent successfully'}), 201
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'Error saving message: {e}')
        return jsonify({'error': 'Internal Server Error'}), 500



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
        
        # if 'picture' not in request.files:
        #     return {'message': 'No picture file'}, 400
        
        # picture = request.files['picture']
        # if picture.filename == '':
        #     return {'message': 'No selected picture'}, 400

        # filename = secure_filename(picture.filename)
        # picture_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        # picture.save(picture_path)

        new_testimony = Testimony(name=name, position=position, message=message, email=email)
        db.session.add(new_testimony)
        db.session.commit()

        return jsonify({
            'id': new_testimony.id,
            'name': new_testimony.name,
            'position': new_testimony.position,
            'message': new_testimony.message,
            'email': new_testimony.email,
            # 'picture': new_testimony.picture,
        })

api.add_resource(TestimonyMessage, '/testimony')



from flask_restful import Resource

class TestimoniesMessage(Resource):
    def get(self):
        testimonies = Testimony.query.all()
        response = []
        
        for testimony in testimonies:
            # picture_url = f"uploads/{os.path.basename(testimony.picture)}"
            
            response.append({
                'id': testimony.id,
                'name': testimony.name,
                'position': testimony.position,
                'message': testimony.message,
                'email': testimony.email,
                # 'picture': picture_url
            })
        
        return jsonify(response)

# Assuming `api` is an instance of `Api` from `flask_restful`
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




if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True, port=3400)
