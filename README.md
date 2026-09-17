# Lumiansh Django Shop 

Lumiansh Django Shop is a **Django-based e-commerce web application** built as a practical project to understand how a complete online shopping system works using Python and Django.

The project includes product browsing, product details, purchasing flow, customer information, and an admin dashboard for managing products.

---

##  Features

### Customer Side

* 🏠 Home page
* 🛍️ Product listing
* 🔎 Product browsing
* 📦 Product details
* 🛒 Buy / purchase flow
* 👤 Customer information
* ✅ Order success page
* 📱 Responsive web pages

### Admin Side

* 🔐 Admin login
* 📊 Admin dashboard
* ➕ Add products
* ✏️ Update product information
* 🗑️ Manage products
* 👥 View customer/order information

### Backend

* Django-based backend
* SQLite database for development
* Django ORM for database operations
* Django migrations
* Custom management command for seed data

---

##  Tech Stack

| Technology       | Purpose                    |
| ---------------- | -------------------------- |
| Python           | Backend programming        |
| Django           | Web framework              |
| SQLite           | Development database       |
| HTML             | Page structure             |
| CSS              | Styling                    |
| Django Templates | Dynamic frontend rendering |

---

##  Project Structure

```text
lumiansh_project/
│
├── manage.py
├── requirements.txt
├── .gitignore
│
├── lumiansh_project/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── shop/
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── urls.py
│   ├── views.py
│   ├── tests.py
│   │
│   ├── management/
│   │   └── commands/
│   │       └── seed_data.py
│   │
│   ├── migrations/
│   │
│   └── templates/
│       └── shop/
│           ├── base.html
│           ├── home.html
│           ├── products.html
│           ├── buy.html
│           ├── buy_landing.html
│           ├── success.html
│           ├── admin_login.html
│           ├── admin_dashboard.html
│           ├── admin_product_form.html
│           └── about_customers.html
│
└── README.md
```

---

##  Setup & Installation

### 1. Clone the repository

```bash
git clone https://github.com/AnshikaAgarwall/lumiansh_django_project.git
cd lumiansh_django_project
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the virtual environment

**Windows:**

```bash
venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Run migrations

```bash
python manage.py migrate
```

### 6. Start the development server

```bash
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

---

##  Seed Sample Data

The project includes a custom Django management command for adding sample shop data.

```bash
python manage.py seed_data
```

---

##  Database

The project uses **SQLite** during development.

The local database file is intentionally excluded from Git using `.gitignore`.

This means a new developer can clone the project and create a fresh database using:

```bash
python manage.py migrate
```

---

##  Dependencies

Project dependencies are stored in:

```text
requirements.txt
```

To install them:

```bash
pip install -r requirements.txt
```

This makes it easier to recreate the development environment on another system.

---

##  Git & Environment

The following files are excluded from version control:

```text
__pycache__/
*.pyc
venv/
env/
sms_env/
db.sqlite3
.env
```

This keeps generated files, virtual environments, local databases, and environment-specific configuration out of the repository.

---

##  What I Learned

Through this project, I practiced:

* Django project and app structure
* URL routing
* Django views
* Models and database relationships
* Django ORM
* Forms and user input
* Templates and template inheritance
* CRUD operations
* Django migrations
* Admin functionality
* Authentication concepts
* Static files and frontend integration
* Custom management commands
* Git and GitHub project management
* Managing Python dependencies using `requirements.txt`

---

## Future Improvements

Some possible improvements for future versions:

* User registration and login
* Shopping cart
* Wishlist
* Product search and filtering
* Product categories
* Order history
* Payment gateway integration
* Better form validation
* Improved responsive UI
* Production database
* Environment variables for sensitive settings
* Deployment to a cloud platform

---

##  Project Status

**Status:** Completed learning/project version

This project represents my practical work with **Python and Django**, from creating the backend structure to working with models, templates, database operations, and GitHub.

---



**Anshika Agarwall**

GitHub: [@AnshikaAgarwall](https://github.com/AnshikaAgarwall)

---

Repository

If you find this project useful, feel free to explore the repository and its development history.

**Lumiansh Django Shop**

https://github.com/AnshikaAgarwall/lumiansh_django_project
