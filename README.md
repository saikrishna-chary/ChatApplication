# 💬 Real-Time Chat Application

A real-time chat application built with **Django, Django Channels, Redis, and MySQL**.  
It supports **one-to-one and group chat**, with features like **media sharing, message deletion, and smart timestamps**.  

---

## ✨ Features
- **One-to-One Chat** – Private messaging with timestamps.  
- **Group Chat** – Group creation, member management, and admin-only deletion.  
- **Real-Time Messaging** – Powered by WebSockets (Django Channels + Redis).  
- **Media Sharing** – Send and receive images/files in chat.  
- **User Authentication** – Custom login/registration with email/OTP.  
- **Message Controls** – Delete option.  

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
   git clone https://github.com/saikrishna-chary/chat_application.git
   cd chat_application



## Create a Virtual Environment
  - python -m venv venv
  - Activate on Windows : - venv\Scripts\activate
  - Activate on Linux/Mac :  - source venv/bin/activate


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

## 4. Deploy

  - Render will automatically install dependencies, run migrations, and start your app.
  - Your app will be live at: - https://your-app.onrender.com

## 📂 Project Structure 
  - chat_application/
  - │  
  - ├── chat/                # Main app (models, views, consumers)
  - ├── templates/           # HTML templates
  - ├── static/              # CSS/JS/static files
  - ├── chat_application/    # Project config (settings.py, asgi.py, urls.py)
  - ├── media/               # Uploaded media files 
  - ├── manage.py
  - ├── requirements.txt
  - └── README.md
 
## 📌 Project Setup Timeline (Major Steps We Did)
  - Created Django Project & App (chat_project → chat).
  - Custom User Model with email login and OTP verification.
  - One-to-One Chat with WebSockets (username-based routing).
  - Group Chat with room creation, member management, and admin controls.
  - Integrated Redis for WebSocket communication and message storage.
  - Added Features: Media sharing, emoji support, message deletion, and smart timestamps.
  - Frontend Pages: Login, Register, Chat Window, Group Chat UI.
  - Deployment Setup: Requirements file, Procfile, environment variables for Render.
---

--- 
## 📧 Author
   - Sai Krishna
   - GitHub: saikrishna-chary
   - LinkedIn: linkedin.com/in/saikrishna-thumoju-bab1b026b
   - Email: saikrishna70950@gmail.com
---
