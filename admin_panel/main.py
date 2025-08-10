import os
import sys

# Проверка существования критических файлов
required_files = [
    'bot/keyboards.py',
    'admin_panel/static'
]

for file in required_files:
    if not os.path.exists(file):
        print(f"CRITICAL ERROR: Missing file/directory - {file}")
        sys.exit(1)
import os
from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from bot.database import Database

app = FastAPI()
security = HTTPBasic()

app.mount("/static", StaticFiles(directory="admin_panel/static"), name="static")
templates = Jinja2Templates(directory="admin_panel/templates")

def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    correct_password = os.getenv("ADMIN_PASSWORD")
    if credentials.password != correct_password:
        raise HTTPException(
            status_code=401,
            detail="Неверный пароль",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

@app.get("/", response_class=HTMLResponse)
async def admin_redirect(request: Request):
    return RedirectResponse("/admin")

@app.get("/admin", response_class=HTMLResponse)
async def admin_panel(
    request: Request, 
    username: str = Depends(get_current_username),
    msg: str = "",
    error: str = ""
):
    db = Database()
    anime_list = db.get_all_anime()
    return templates.TemplateResponse(
        "admin.html", 
        {
            "request": request,
            "anime_list": anime_list,
            "msg": msg,
            "error": error
        }
    )

@app.post("/add_anime")
async def add_anime(
    request: Request,
    title: str = Form(...),
    voiceover: str = Form(...),
    description: str = Form(""),
    poster_url: str = Form(""),
    username: str = Depends(get_current_username)
):
    db = Database()
    try:
        anime_id = db.add_anime(title, voiceover, description, poster_url)
        return RedirectResponse(
            "/admin?msg=Аниме успешно добавлено", 
            status_code=303
        )
    except Exception as e:
        return RedirectResponse(
            f"/admin?error={str(e)}", 
            status_code=303
        )

@app.post("/add_episode")
async def add_episode(
    request: Request,
    anime_id: int = Form(...),
    episode_number: int = Form(...),
    vk_url: str = Form(...),
    username: str = Depends(get_current_username)
):
    db = Database()
    try:
        db.add_episode(anime_id, episode_number, vk_url)
        return RedirectResponse(
            "/admin?msg=Серия успешно добавлена", 
            status_code=303
        )
    except Exception as e:
        return RedirectResponse(
            f"/admin?error={str(e)}", 
            status_code=303
  )
