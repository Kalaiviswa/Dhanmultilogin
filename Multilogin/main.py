from fastapi import FastAPI, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from jinja2 import Environment, FileSystemLoader
import uvicorn

from database import Base, engine, SessionLocal
from models import User
from utils import hash_password, verify_password

# Configurations
app = FastAPI()
jinja_env = Environment(loader=FileSystemLoader("templates"))

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Routes
@app.get("/", response_class=HTMLResponse)
def home():
    template = jinja_env.get_template("home.html")
    return HTMLResponse(template.render())

@app.get("/login", response_class=HTMLResponse)
def login_page():
    template = jinja_env.get_template("login.html")
    return HTMLResponse(template.render())

@app.post("/login")
def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid username or password")
    if user.broker_configured:
        return RedirectResponse("/dashboard", status_code=302)
    else:
        return RedirectResponse("/broker-setup", status_code=302)

@app.get("/register", response_class=HTMLResponse)
def registration_page():
    template = jinja_env.get_template("register.html")
    return HTMLResponse(template.render())

@app.post("/register")
def register(username: str = Form(...), email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    hashed_password = hash_password(password)
    new_user = User(username=username, email=email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    return RedirectResponse("/login", status_code=302)

@app.get("/forgot-password", response_class=HTMLResponse)
def forgot_password_page():
    template = jinja_env.get_template("forgot_password.html")
    return HTMLResponse(template.render())

@app.get("/broker-setup", response_class=HTMLResponse)
def broker_setup_page():
    template = jinja_env.get_template("broker_setup.html")
    return HTMLResponse(template.render())

@app.post("/broker-setup")
def broker_setup(api_key: str = Form(...), api_secret: str = Form(...), db: Session = Depends(get_db)):
    # Assume user is already authenticated (this example lacks auth middleware for brevity)
    user = db.query(User).filter(User.id == 1).first()  # Replace with actual user session logic
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    user.broker_configured = True
    db.commit()
    return RedirectResponse("/dashboard", status_code=302)

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard_page():
    template = jinja_env.get_template("dashboard.html")
    return HTMLResponse(template.render())

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
