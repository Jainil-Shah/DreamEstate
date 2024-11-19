from flask import Flask, render_template, jsonify, request, redirect, url_for,  flash, session
from database import load_buyers_from_db, load_sellers_from_db, add_user_to_db, get_user_by_email, get_user_by_id, add_property_to_db, load_properties_from_db, delete_user_from_db, update_user_in_db, load_seller_properties_from_db, soldout_property, add_blog_to_db, load_blogs_from_db, get_properties_count_from_db, add_enquiry_to_db, get_enquiries_for_seller, store_verification_code, get_stored_verification_code, mark_user_as_verified
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
from werkzeug.utils import secure_filename  # Secure the File Uploads
from flask_mail import Mail, Message
import random
import string
from urllib.parse import quote_plus, quote  


app = Flask(__name__)


# Configure Flask-Mail for Gmail SMTP
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'dreamestate1212@gmail.com'  # Your Gmail address
app.config['MAIL_PASSWORD'] = 'wcje wqik iquf pmsa'  # Your Gmail password (or App Password)
app.config['MAIL_DEFAULT_SENDER'] = 'dreamestate1212@gmail.com'

mail = Mail(app)


# Login (session):
app.secret_key = 'secret_key_1234'  #secure key
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirect users to 'login' route if not authenticated

class User(UserMixin):
    def __init__(self, id, name, email, phone=None, role=None):
        self.id = id
        self.name = name
        self.email = email
        self.phone = phone
        self.role = role

    @staticmethod
    def from_db_row(row):
        return User(
            id=row['id'], 
            name=row['name'], 
            email=row['email'],  
            phone=row.get('phone'), 
            role=row.get('role')
        )
    
@login_manager.user_loader
def load_user(user_id):
    # Retrieve role from the session
    role = session.get('role')
    user_data = get_user_by_id(user_id, role)
    if user_data:
        return User.from_db_row(user_data)
    return None

    
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.form.to_dict() # Convert ImmutableMultiDict to regular dict

        email = request.form['email']
        password = request.form['password']
        role = data.get('role')

        # Debug print to verify role
        print(f"Role received: {role}")

        if not email or not password or not role:
            flash('Missing required fields.')
            return redirect(url_for('login'))

        user_data = get_user_by_email(email, role)
        if user_data and user_data['password'] == password:  # Basic check; use hashing in production
            user = User.from_db_row(user_data)
            login_user(user)
            session['role'] = role  # Store the role in the session
            flash('Logged in successfully.')
            return redirect(url_for('home'))  # Redirect to a protected route
        else:
            flash('Invalid email or password.')

    return render_template('login.html')


# @app.route('/login')
# def login():
#     return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    role = session.get('role')
    user_data = get_user_by_id(current_user.id, role) 
    return render_template('dashboard.html', user=user_data, role=role)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('login'))

@app.route('/')
def home():
    # Check if the user is logged in
    if current_user.is_authenticated:
        user_name = current_user.name 
        role = session.get('role')  # Get the role from the session
    else:
        user_name = None
        role = None

    return render_template('home.html', user_name=user_name, role=role)












@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/buyer/registration', methods=['POST'])
def register_user():
    data = request.form.to_dict()

    # Generate a verification code (random string)
    verification_code = ''.join(random.choices(string.ascii_letters + string.digits, k=6))

    # Send verification email
    email = data['email']
    send_verification_email(email, verification_code)

    # Store the verification code in the temporary verification table
    store_verification_code(email, data['role'], verification_code)

    # Store the data and verification code in the session
    session['registration_data'] = data
    session['verification_code'] = verification_code

    # # Add the user data to the appropriate table (buyer or seller)
    # add_user_to_db(data)

    # Redirect to the verify_email route, passing the email and code
    return redirect(url_for('verify_email', email=email))

@app.route('/verify-email')
def verify_email():
    # Get the email and code from the request arguments
    email = request.args.get('email')
    code = request.args.get('code')

    # Render the verify_email.html template, passing the email and code
    return render_template('verify_email.html', email=email, code=code)

@app.route('/verify/<email>/<code>', methods=['GET'])
def verify_account(email, code):
    # Retrieve the verification code for this email from the user_verifications table
    # stored_code = get_stored_verification_code(email)
    stored_code = session.get('verification_code')
    data = session.get('registration_data')
    
    if stored_code and stored_code == code:

        # Add the user data to the appropriate table (buyer or seller)
        add_user_to_db(data)

        print(f"stored_code: {stored_code}")
        print(f"code: {code}")

        # Mark the user as verified in the user_verifications table
        mark_user_as_verified(email)

        flash("Your account has been verified. You can now log in.")
        return redirect(url_for('login'))
    else:
        return "Invalid verification code", 400

def send_verification_email(email, verification_code):
    # Generate the correct URL with both email and code
    verification_url = url_for('verify_account', email=email, code=verification_code, _external=True)
    print(f"Generated verification URL: {verification_url}")  # Check generated URL

    msg = Message("Email Verification", recipients=[email])
    msg.body = f"Your verification code is {verification_code}."
    mail.send(msg)


# def send_verification_email(email, verification_code):
#     # encoded_email = quote(email)  # Encode email to ensure it's URL-safe
#     verification_url = url_for('verify_account', email=email, code=verification_code, _external=True)
#     print(f"Generated verification URL: {verification_url}")  # Debugging

#     msg = Message("Email Verification", recipients=[email])
#     msg.body = f"Your verification code is {verification_code}."
#     try:
#         mail.send(msg)
#     except Exception as e:
#         print(f"Error sending email: {e}")





 
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Fetch the admin user data by email and role
        user_data = get_user_by_email(email, 'admin')

        # Verify the user's credentials
        if user_data and user_data['password'] == password:
            user = User.from_db_row(user_data)
            login_user(user)
            session['role'] = 'admin'
            flash('Admin logged in successfully.')
            return redirect(url_for('admin'))
        else:
            flash('Invalid admin credentials.')
            return render_template('admin_login.html')

    return render_template('admin_login.html')
 



@app.route('/sell_property')
def sell_property():
    return render_template('sell_property.html')

UPLOAD_FOLDER = 'static/properties'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/submit_property', methods=['POST'])
def submit_property():
    # Check if the user is logged in
    if not current_user.is_authenticated:
        return redirect(url_for('login'))  # Redirect to login if not authenticated

    # Retrieve form data
    # property_type = request.form['property_type']
    # address = request.form['address']
    # rent = request.form['rent']
    # price = request.form['price']
    # property_images = request.files['property_images']

    # Set the status internally 
    status = 'not sold'

    file = request.files['property_images']

    # Check if a file was uploaded and if it's allowed
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Save the property details to the database
        data = {
            'seller_id': current_user.id,  # Get seller_id from the current logged-in user
            'type': request.form['property_type'],
            'price': request.form['price'],
            'rent': request.form['rent'],
            'address': request.form['address'],
            'city': request.form['city'],
            'status': 'not sold',  # Default status
            'photo': file_path  # Save the file path in the database
        }

        add_property_to_db(data)

        return redirect(url_for('home')) 
    
    else:
        flash('Invalid file type')
        return "File type not allowed"



@app.route('/properties')
@login_required
def properties():
    page = request.args.get('page', 1, type=int)
    items_per_page = 4

    # Retrieve filter parameters
    filters = {
        "type": request.args.get('type', ''),
        "price_min": request.args.get('price_min', type=int),
        "price_max": request.args.get('price_max', type=int),
        "rent_min": request.args.get('rent_min', type=int),
        "rent_max": request.args.get('rent_max', type=int),
        "city": request.args.get('city', ''),
        "sold_status": request.args.get('sold_status', default='not sold', type=str)
    }

    # Apply filters to count and load properties
    total_properties = get_properties_count_from_db(filters)
    property_list = load_properties_from_db(page, items_per_page, filters)

    total_pages = (total_properties + items_per_page - 1) // items_per_page
    if page > total_pages:
        page = total_pages

    return render_template('properties.html', properties=property_list, page=page, total_pages=total_pages, filters=filters)


@app.route('/send_enquiry', methods=['GET', 'POST'])
@login_required
def send_enquiry():
    # Retrieve the form data and current user details
    property_id = request.form['property_id']
    seller_id = request.form['seller_id']
    buyer_id = current_user.id  # Get the logged-in buyer's ID
    user_message = request.form['user_message']

    print(property_id, seller_id, buyer_id, user_message)
    # Store the inquiry in the enquires table
    add_enquiry_to_db(seller_id=seller_id, buyer_id=buyer_id, property_id=property_id, message=user_message)

    # Provide feedback to the user
    flash("Your enquiry has been sent successfully!", "success")
    return render_template('home.html')


@app.route('/seller_enquires')
def seller_enquires():
    role = session.get('role')
    user_data = get_user_by_id(current_user.id, role) 
    # Query to get enquiries for the current seller
    enquires = get_enquiries_for_seller(current_user.id)
    return render_template('seller_enquires.html', user=user_data, role=role, enquires=enquires)




#Admin:
@app.route('/admin')
def admin():
    buyers = load_buyers_from_db()
    sellers = load_sellers_from_db()
    return render_template('admin.html', buyers=buyers, sellers=sellers)


# @app.route('/edit_user/<int:id>', methods=['GET', 'POST'])
# def edit_user(id):
#     # Fetch the role from the query parameters
#     role = request.args.get('role')


@app.route('/edit_user_form/<int:id>')
def edit_user_form(id):
    id = id
    return render_template('edit_user_from.html', id=id)


@app.route('/edit_user/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_user(id):
    data = request.form.to_dict()  # Convert ImmutableMultiDict to regular dict
    id = id
    role = session.get('role')
    # Ensure the user has the right to edit
    if role not in ['admin', 'buyer', 'seller']:
        return redirect(url_for('dashboard'))
    update_user_in_db(id, data, role)
    return redirect(url_for('dashboard'))


@app.route('/delete_user/<int:id>', methods=['GET', 'POST'])
def delete_user(id):
    # Fetch the role from the query parameters
    role = request.args.get('role')
    if role not in ['buyer', 'seller']:
        return redirect(url_for('dashboard'))
    delete_user_from_db(role, id)
    return redirect(url_for('admin'))



@app.route('/myproperties')
def myproperties():
    id = current_user.id
    role = session.get('role')
    property_list = load_seller_properties_from_db(id)  # Fetch the properties for current seller
    return render_template('seller_specific_properties.html', properties=property_list, role=role)


@app.route('/soldout/<int:property_id>')
@login_required
def soldout(property_id):
    soldout_property(property_id)
    return redirect(url_for('myproperties'))




#---------------------------------------------------WORKING ON---------------------------------------------------------# 

@app.route('/write_blog')
@login_required
def write_blog():
    return render_template('write_blog.html')



@app.route('/blogs')
@login_required
def blogs():
    blog_list = load_blogs_from_db()
    return render_template('blogs.html', blogs=blog_list)



UPLOAD_FOLDER_BLOG = 'static/blogs_images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER_BLOG'] = UPLOAD_FOLDER_BLOG

@app.route('/submit_blog',  methods=['POST'])
def submit_blog():
    # Retrieve form data
    # heading = request.form['heading']
    # content = request.form['content']
    # like = request.form['like_count']

    file = request.files['property_images']

    # Check if a file was uploaded and if it's allowed
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER_BLOG'], filename)
        file.save(file_path)

        # Save the blog details to the database
        data = {
            'user_id': current_user.id,
            'heading': request.form['heading'],
            'content': request.form['content'],
            'like': request.form['like_count'],
            'photo': file_path  # Save the file path in the database
        }

        print(f"User ID: {data['user_id']}, Heading: {data['heading']}, Content: {data['content']}, Photo: {data['photo']}")

        add_blog_to_db(data)

        return redirect(url_for('home')) 
    
    else:
        flash('Invalid file type')
        return "File type not allowed"


#----------------------------------------------------------------------------------------------------------------------# 





#Json:
@app.route('/api/users')
def list_buyers():
    buyers = load_buyers_from_db()
    return jsonify(buyers)






# @app.route('/admin_login')
# def admin_login():
#     return render_template('admin_login.html')