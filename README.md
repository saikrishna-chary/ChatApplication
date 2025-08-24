# 💬 Real-Time Chat Application

A real-time chat application built with **Django, Django Channels, Redis, and MySQL**.  
It supports **one-to-one and group chat**, with features like **media sharing, emoji support, message deletion, and smart timestamps**.  

---

## ✨ Features
- **One-to-One Chat** – Private messaging with timestamps.  
- **Group Chat** – Group creation, member management, and admin-only deletion.  
- **Real-Time Messaging** – Powered by WebSockets (Django Channels + Redis).  
- **Media Sharing** – Send and receive images/files in chat.  
- **User Authentication** – Custom login/registration with email/OTP.  
- **Message Controls** – Emoji support and delete option.  

---

## 🛠 Tech Stack
- **Backend:** Python, Django, Django Channels  
- **Database:** MySQL, Redis  
- **Frontend:** HTML, CSS, JavaScript  
- **Tools:** Git, GitHub, PyCharm / VS Code  

---

## ⚙️ Installation & Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/saikrishna-chary/hospital_management.git
   cd hospital_management


## Create a Virtual Environment
  - python -m venv venv
  - Activate on Windows
  - venv\Scripts\activate
  - Activate on Linux/Mac
  - source venv/bin/activate


## Install Dependencies
- pip install -r requirements.txt

## Configure Database
  - Open settings.py.
  - Update the DATABASES section with your MySQL username, password, and database name. Example:
  - DATABASES = {
  - 'default': {
       - 'ENGINE': 'django.db.backends.mysql',
       - 'NAME': 'hospital_db',
       - 'USER': 'root',
       - 'PASSWORD': 'yourpassword',
       - 'HOST': '127.0.0.1',
       - 'PORT': '3306',
     - }
   - }
## Start Redis Server
   - Windows: redis-server
   - Linux/Mac: sudo service redis-server start

## Apply Migrations
  - python manage.py makemigrations
  - python manage.py migrate

## Run Development Server
   - python manage.py runserver


---
#  🚀 Deployment Instructions (Render)
## 1. Push Code to GitHub
  - Make sure your code, requirements.txt, and Procfile are committed and pushed.
## 2. Create Render App
  - Go to Render
  - Create a new Web Service.
  - Connect your GitHub repo.
## 3. Configure Environment Variables
  - In Render Dashboard → Environment, set:
  - SECRET_KEY=your-django-secret
  - DEBUG=False
  - DATABASE_URL=mysql://user:password@host:port/chat_db
  - REDIS_URL=redis://host:port
  - ALLOWED_HOSTS=your-app.onrender.com
---
