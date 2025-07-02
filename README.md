# 🌤️ Personal Weather Dashboard

A secure, user-friendly weather tracking web application built using **FastAPI**, **SQLite**, and the **OpenWeatherMap API**. Users can register, log in with JWT-based authentication, set or auto-detect their location, and view real-time weather updates for that location.

---

## 🔧 Features

- 🔐 **User Authentication** with JWT (JSON Web Token)
  - Secure login and registration
  - Tokens include expiry for session security
- 👤 **User Profile Management**
  - Stores email, hashed password, and location (city/country)
- ☁️ **Weather Integration**
  - Displays current temperature, humidity, and condition using OpenWeatherMap
- 📍 **Auto-Detect Location**
  - Uses browser's Geolocation API to fetch coordinates
- 🌐 **Minimal Frontend**
  - Separate login, register, and dashboard pages
  - Clean CSS per page (login.css, register.css, dashboard.css)
- 🚪 **Logout Functionality**
  - Deletes JWT token from browser to end session

---

## 📁 Project Structure

weather_dashboard/
├── app/
│ ├── main.py # FastAPI entry point
│ ├── auth.py # JWT, password hashing
│ ├── database.py # SQLAlchemy + SQLite config
│ ├── models.py # User model
│ ├── schemas.py # Pydantic schemas
│ ├── weather.py # Weather API integration
│ ├── templates/ # HTML templates
│ │ ├── login.html
│ │ ├── register.html
│ │ └── dashboard.html
│ └── static/ # CSS files
│ ├── login.css
│ ├── register.css
│ └── dashboard.css
├── .env # API key and config variables
├── requirements.txt
└── README.md


---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/personal-weather-dashboard.git
cd personal-weather-dashboard


### 2. Create Virtual Environment

python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

### 3. Install Dependencies

pip install -r requirements.txt

### 4. Set Up .env

Create a .env file in the root directory and add your OpenWeatherMap API key:

OPENWEATHER_API_KEY=your_openweathermap_api_key

Get a free API key from: https://openweathermap.org/api

### 5. Run the App

uvicorn app.main:app --reload

Visit: http://127.0.0.1:8000

### 🧪 Testing the App
🔸 Register
Go to /register, create a new user.

Passwords are securely hashed using bcrypt.

🔸 Login
Use your credentials to log in.

JWT token is stored in the browser via cookie.

Redirects to /dashboard.

🔸 Dashboard
View weather for your saved location.

Update location manually or use “Auto-detect Location” to get GPS-based weather.

🔸 Logout
Click logout to delete token and return to login screen.

### 🛡️ Security Notes
Passwords are hashed using bcrypt

JWT includes exp claim (1-hour expiry)

All sensitive routes require authentication

Tokens are stored in HTTP-only cookies (secure against XSS)

### 📦 Dependencies

fastapi
uvicorn
sqlalchemy
python-jose[cryptography]
passlib[bcrypt]
python-dotenv
requests
jinja2


pip install -r requirements.txt


### 🧠 Highlights / Learnings

Implemented full JWT-based auth in FastAPI

Integrated external REST API (OpenWeatherMap)

Used Geolocation API in frontend

Managed secure cookies, form-based login, and token handling

Applied modern web development practices

### 🙋‍♂️ About Me
👋 I’m Vishal Kumar, a Computer Science graduate passionate about building secure, scalable, and user-friendly applications.

## 📬 Contact
📧 Email: vishal843327k@gmail.com
💼 LinkedIn: linkedin.com/in/vishal843327
