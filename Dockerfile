# سحب نسخة بايثون الرسمية المدعومة بمتصفحات Playwright من ماكروسوفت
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

# تحديد مجلد العمل داخل السيرفر
WORKDIR /app

# نسخ ملف المتطلبات وتثبيته
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ باقي ملفات المشروع داخل الحاوية
COPY . .

# إنشاء مجلد الجلسات بشكل افتراضي
RUN mkdir -p sessions

# تشغيل السيرفر
CMD ["python", "main.py"]
