from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from starlette.status import HTTP_303_SEE_OTHER
from fastapi import Cookie
from . import database, models, schemas, auth, weather

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

# Mount static directory
app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Show login form
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/do-login")
def do_login(request: Request, email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(models.User).filter_by(email=email).first()
    if not user or not auth.verify_password(password, user.hashed_password):
        raise HTTPException(401, "Invalid credentials")
    token = auth.create_access_token({"sub": user.email})
    response = RedirectResponse("/dashboard", status_code=HTTP_303_SEE_OTHER)
    # Store token as a cookie
    response.set_cookie(key="access_token", value=f"Bearer {token}", httponly=True)
    return response


@app.get("/logout")
def logout():
    response = RedirectResponse("/", status_code=HTTP_303_SEE_OTHER)
    response.delete_cookie("access_token")
    return response


# Show register form
@app.get("/register", response_class=HTMLResponse)
def show_register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

# Register new user
@app.post("/register")
def register(email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    if db.query(models.User).filter_by(email=email).first():
        raise HTTPException(400, "User already exists")
    hashed = auth.get_password_hash(password)
    user = models.User(email=email, hashed_password=hashed)
    db.add(user)
    db.commit()
    return RedirectResponse("/", status_code=HTTP_303_SEE_OTHER)

# Login (POST only – don't open it in browser)
@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter_by(email=form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(401, "Invalid credentials")
    token = auth.create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}

# Dashboard view

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(
    request: Request,
    access_token: str = Cookie(default=None),
    db: Session = Depends(get_db)
):
    # If the token cookie is missing, redirect to login
    if not access_token:
        return RedirectResponse("/", status_code=HTTP_303_SEE_OTHER)

    # Remove "Bearer " prefix if present
    token = access_token.replace("Bearer ", "")

    # Decode the JWT token
    payload = auth.decode_access_token(token)
    if not payload:
        raise HTTPException(401, "Invalid token")

    # Get the user from DB
    user = db.query(models.User).filter_by(email=payload["sub"]).first()

    # Fetch weather only if location is set
    weather_data = weather.get_weather(user.city, user.country) if user.city and user.country else None

    # Render the dashboard
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": user,
        "weather": weather_data
    })


# Update location

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
