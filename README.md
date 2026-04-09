# ERP - Stock Management and Transfer System (Django REST Framework)

## Overview

This project is a backend system built using Django REST Framework to manage branch-level inventory and stock transfers between branches.

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/srimaha0801/ERP.git
cd ERP
```

### 2. Create Virtual Environment

```bash
python3.12 -m venv venv
```

Activate the virtual environment:

- Windows:
```bash
venv\Scripts\activate
```

- Linux/Mac:
```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file in the project root and add:

```env
SECRET_KEY="django-insecure-cs#gs(a@n#83d6is!156ol0c^%_h*7og2&r()$$3pf7(z3g)7-"

```

---

## Database Setup

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## Create Superuser

```bash
python manage.py createsuperuser
```

---

## Run the Application

```bash
python manage.py runserver
```

The application will be available at:
http://127.0.0.1:8000/

---

## Run Tests

```bash
python manage.py test
```
