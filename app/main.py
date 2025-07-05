from fastapi import FastAPI, Depends, HTTPException, Request, Form, Cookie
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from starlette.status import HTTP_303_SEE_OTHER
from datetime import datetime
import csv
import io

hourly_data = []

from . import database, models, schemas, auth, weather

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Dependency for DB session
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Show login page
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# Perform login
@app.post("/do-login")
def do_login(request: Request, email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(models.User).filter_by(email=email).first()
    if not user or not auth.verify_password(password, user.hashed_password):
        raise HTTPException(401, "Invalid credentials")

    token = auth.create_access_token({"sub": user.email})
    response = RedirectResponse("/dashboard", status_code=HTTP_303_SEE_OTHER)
    response.set_cookie(key="access_token", value=f"Bearer {token}", httponly=True)
    return response

# Perform logout
@app.get("/logout")
def logout():
    response = RedirectResponse("/", status_code=HTTP_303_SEE_OTHER)
    response.delete_cookie("access_token")
    return response

# Show register form
@app.get("/register", response_class=HTMLResponse)
def show_register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

# Register user
@app.post("/register")
def register(email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    if db.query(models.User).filter_by(email=email).first():
        raise HTTPException(400, "User already exists")

    hashed = auth.get_password_hash(password)
    user = models.User(email=email, hashed_password=hashed)
    db.add(user)
    db.commit()
    return RedirectResponse("/", status_code=HTTP_303_SEE_OTHER)

# Token endpoint for OAuth2
@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter_by(email=form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(401, "Invalid credentials")

    token = auth.create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}

# Dashboard route
from datetime import datetime, timedelta
import pytz
from .models import WeatherLog  # ensure this is imported

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(
    request: Request,
    access_token: str = Cookie(default=None),
    db: Session = Depends(get_db)
):
    if not access_token:
        return RedirectResponse("/", status_code=HTTP_303_SEE_OTHER)

    token = access_token.replace("Bearer ", "")
    payload = auth.decode_access_token(token)
    if not payload:
        raise HTTPException(401, "Invalid token")

    user = db.query(models.User).filter_by(email=payload["sub"]).first()
    weather_data = weather.get_weather(user.city, user.country) if user.city and user.country else None

    if weather_data:
        india = pytz.timezone("Asia/Kolkata")
        now = datetime.now(india)

        # ✅ Create a new weather log
        new_log = WeatherLog(
            user_id=user.id,
            timestamp=now,
            temperature=weather_data["main"]["temp"],
            humidity=weather_data["main"]["humidity"],
            condition=weather_data["weather"][0]["description"]
        )

        db.add(new_log)

        # ✅ Delete logs older than 24 hours for this user
        cutoff = now - timedelta(hours=24)
        db.query(WeatherLog).filter(
            WeatherLog.user_id == user.id,
            WeatherLog.timestamp < cutoff
        ).delete()

        db.commit()

        # Optional: keep in-memory hourly_data list updated
        hourly_data.append({
            "time": now.strftime("%Y-%m-%d %H:%M"),
            "temperature": weather_data["main"]["temp"],
            "humidity": weather_data["main"]["humidity"],
            "condition": weather_data["weather"][0]["description"]
        })

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": user,
        "weather": weather_data
    })


# Update location route
@app.post("/update-location")
def update_location(
    city: str = Form(...),
    country: str = Form(...),
    access_token: str = Cookie(default=None),
    db: Session = Depends(get_db)
):
    if not access_token:
        raise HTTPException(401, "Not authenticated")

    token = access_token.replace("Bearer ", "")
    payload = auth.decode_access_token(token)
    if not payload:
        raise HTTPException(401, "Invalid token")

    user = db.query(models.User).filter_by(email=payload["sub"]).first()
    user.city = city
    user.country = country
    db.commit()

    return RedirectResponse("/dashboard", status_code=HTTP_303_SEE_OTHER)

# ✅ Download CSV route
@app.get("/download_csv")
def download_csv(access_token: str = Cookie(default=None), db: Session = Depends(get_db)):
    if not access_token:
        raise HTTPException(401, "Not authenticated")

    token = access_token.replace("Bearer ", "")
    payload = auth.decode_access_token(token)
    if not payload:
        raise HTTPException(401, "Invalid token")

    user = db.query(models.User).filter_by(email=payload["sub"]).first()
    logs = db.query(models.WeatherLog).filter_by(user_id=user.id).order_by(models.WeatherLog.timestamp.asc()).all()

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["Time", "Temperature", "Humidity", "Condition"])

    for log in logs:
        writer.writerow([
            log.timestamp.strftime("%Y-%m-%d %H:%M"),
            log.temperature,
            log.humidity,
            log.condition
        ])

    buffer.seek(0)
    return StreamingResponse(buffer, media_type="text/csv", headers={
        "Content-Disposition": "attachment; filename=weather_hourly_data.csv"
    })
