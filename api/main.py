"""
ScamGuard AI — Multi-Mode Threat Detection API
v2.0: BERT emotion engine + 6 threat categories + 4 analysis modes
"""
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import joblib
import os
import sys
import re
from scipy.sparse import hstack
import numpy as np
import io
import logging

# Libraries for file/URL processing
import PyPDF2
import docx
import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add project path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.features.build_features import clean_arabic_text
from src.features.threat_patterns import detect_threats, get_mode_info, THREAT_CATEGORIES
from src.models.bert_analyzer import bert_analyzer

# ===== App Setup =====
app = FastAPI(
    title="ScamGuard AI — Multi-Mode Threat Detection",
    description="AI-powered Arabic text threat analysis with BERT emotion engine, 6 threat categories, and 4 analysis modes.",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

# ===== Load ML Models =====
TFIDF_PATH = os.path.join("models", "tfidf_vectorizer.pkl")
MODEL_PATH = os.path.join("models", "best_scam_detector.pkl")

try:
    tfidf_vectorizer = joblib.load(TFIDF_PATH)
    scam_detector_model = joblib.load(MODEL_PATH)
    logger.info("ML models loaded successfully.")
except FileNotFoundError:
    raise RuntimeError("Model files not found! Run training scripts first.")

# Load BERT on startup (background)
@app.on_event("startup")
async def startup_event():
    logger.info("Loading BERT model in background...")
    bert_analyzer.load_model()

# ===== Request Models =====
class PostRequest(BaseModel):
    post_text: str
    mode: Optional[str] = "general"

class UrlRequest(BaseModel):
    url: str
    mode: Optional[str] = "general"

# ===== Feature Extraction (existing SVM) =====
financial_words = ['تبرع', 'ارسل', 'تحويل', 'حساب', 'مبلغ', 'ريال', 'دولار', 'تكلفه', 'تكاليف', 'مساهمه', 'ساهم']
urgency_words = ['عاجل', 'انقذوا', 'استغاثه', 'بسرعه', 'ضروري', 'حرج', 'خطر', 'طرد', 'مستشفي', 'يعاني', 'مريض', 'سرطان', 'يتيم', 'ارمله']
religious_promises = ['ميزان', 'حسنات', 'يضاعف', 'فرج', 'صدقه جاريه', 'يبارك', 'اجر', 'لوجه الله', 'الجنه', 'انشرها', 'تتجاهل', 'اقسم بالله']

def get_custom_features(cleaned_text: str) -> np.ndarray:
    has_account_num = int('<account_num>' in cleaned_text.lower() or '<num>' in cleaned_text.lower())
    financial_request_score = sum(cleaned_text.count(w) for w in financial_words)
    urgency_score = sum(cleaned_text.count(w) for w in urgency_words)
    religious_manipulation_score = sum(cleaned_text.count(w) for w in religious_promises)
    text_length = len(cleaned_text)
    url_count = cleaned_text.lower().count('<url>')
    return np.array([[has_account_num, financial_request_score, urgency_score, religious_manipulation_score, text_length, url_count]])

def extract_keyword_map(text: str):
    detected = []
    text_lower = text.lower()
    for word in financial_words:
        if word in text_lower:
            detected.append({"word": word, "type": "scam", "impact": "High"})
    for word in urgency_words:
        if word in text_lower:
            detected.append({"word": word, "type": "suspicious", "impact": "Medium"})
    for word in religious_promises:
        if word in text_lower:
            detected.append({"word": word, "type": "suspicious", "impact": "Medium"})
    return detected

# ===== File/URL Extraction =====
def extract_text_from_pdf(content: bytes) -> str:
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
    return "".join([page.extract_text() or "" for page in pdf_reader.pages])

def extract_text_from_docx(content: bytes) -> str:
    doc = docx.Document(io.BytesIO(content))
    return "\n".join([para.text for para in doc.paragraphs])

# ===== API Endpoints =====

@app.get("/api/v1/modes")
async def get_modes():
    """Return available analysis modes."""
    return {
        "modes": [
            {**get_mode_info(m), "key": m}
            for m in ["general", "children", "intelligence", "parents"]
        ]
    }

@app.post("/api/v1/analyze")
async def analyze_content(request: PostRequest):
    return perform_analysis(request.post_text, request.mode or "general")

@app.post("/api/v1/analyze-file")
async def analyze_file(file: UploadFile = File(...), mode: str = "general"):
    try:
        extension = file.filename.split(".")[-1].lower()
        content = await file.read()
        text = ""
        if extension == "pdf":
            try: text = extract_text_from_pdf(content)
            except Exception as e: raise HTTPException(400, detail=f"فشل استخراج النص من PDF: {e}")
        elif extension == "docx":
            try: text = extract_text_from_docx(content)
            except Exception as e: raise HTTPException(400, detail=f"فشل استخراج النص من Word: {e}")
        elif extension == "txt":
            try: text = content.decode("utf-8")
            except UnicodeDecodeError: text = content.decode("cp1256", errors="ignore")
        else:
            raise HTTPException(400, detail="صيغة غير مدعومة. يرجى PDF أو Word أو TXT.")
        if not text.strip():
            raise HTTPException(400, detail="لم يتم العثور على نص في الملف.")
        return perform_analysis(text, mode)
    except HTTPException: raise
    except Exception as e:
        raise HTTPException(500, detail=f"خطأ: {e}")

@app.post("/api/v1/analyze-url")
async def analyze_url(request: UrlRequest):
    try:
        response = requests.get(request.url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        for script in soup(["script", "style"]): script.extract()
        text = soup.get_text()
        return perform_analysis(text, request.mode or "general")
    except Exception as e:
        raise HTTPException(400, detail=f"Failed to fetch URL: {e}")

# ===== Core Analysis Engine =====
def perform_analysis(text: str, mode: str = "general"):
    try:
        if not text.strip():
            raise HTTPException(400, detail="لا يوجد نص كافٍ للتحليل.")

        mode = mode if mode in ["general", "children", "intelligence", "parents"] else "general"
        mode_info = get_mode_info(mode)

        # 1. Clean text & SVM classification
        cleaned_text = clean_arabic_text(text)
        text_vector = tfidf_vectorizer.transform([cleaned_text])
        custom_features = get_custom_features(cleaned_text)
        final_features = hstack([text_vector, custom_features])
        prediction = scam_detector_model.predict(final_features)[0]

        labels = {0: "Legitimate Religious Post", 1: "Suspicious Religious Manipulation", 2: "Explicit Religious Scam"}
        labels_ar = {0: "منشور ديني سليم", 1: "تلاعب ديني مشبوه", 2: "احتيال ديني صريح"}
        result_class = labels.get(prediction, "Unknown")
        result_class_ar = labels_ar.get(prediction, "غير معروف")

        risk_score = 0.05
        if prediction == 2: risk_score = 0.95
        elif prediction == 1: risk_score = 0.65

        # 2. Multi-threat detection
        threats = detect_threats(text, mode)

        # Boost risk_score based on threats
        if threats:
            max_threat_score = max(t["score"] for t in threats)
            risk_score = max(risk_score, max_threat_score)

        # 3. BERT emotion analysis (intelligence mode gets full, others get basic)
        emotion_data = None
        if mode == "intelligence" or mode == "general":
            emotion_data = bert_analyzer.analyze(text)
            # Boost risk with high negative + urgency
            if emotion_data and emotion_data.get("bert_available"):
                if emotion_data["sentiment"] == "negative" and emotion_data["confidence"] > 0.8:
                    risk_score = min(risk_score + 0.1, 1.0)
        elif mode == "children":
            emotion_data = bert_analyzer.analyze(text)
        else:
            # Parents mode: basic emotions
            emotion_data = bert_analyzer.analyze(text)

        # 4. Overall danger level
        if risk_score >= 0.8: danger = {"level": "critical", "level_ar": "حرج", "color": "red"}
        elif risk_score >= 0.5: danger = {"level": "high", "level_ar": "مرتفع", "color": "orange"}
        elif risk_score >= 0.3: danger = {"level": "medium", "level_ar": "متوسط", "color": "yellow"}
        else: danger = {"level": "low", "level_ar": "منخفض", "color": "green"}

        # 5. Mode-specific recommendations
        recommendations = generate_recommendations(mode, threats, prediction, risk_score)

        # 6. Build response
        response_data = {
            "original_text": (text[:500] + "...") if len(text) > 500 else text,
            "mode": mode,
            "mode_info": mode_info,
            "classification": result_class,
            "classification_ar": result_class_ar,
            "risk_score": round(float(risk_score), 2),
            "danger": danger,
            "keyword_map": extract_keyword_map(cleaned_text),
            "threats": threats,
            "emotions": emotion_data,
            "insights": {
                "financial_requests_found": bool(custom_features[0][1] > 0),
                "urgency_detected": bool(custom_features[0][2] > 0),
                "emotional_manipulation_detected": bool(custom_features[0][3] > 0)
            },
            "recommendations": recommendations,
            "action_recommended": "block_and_report" if prediction == 2 else "flag_for_review" if prediction == 1 else "safe"
        }

        return {"status": "success", "data": response_data}

    except HTTPException: raise
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        raise HTTPException(500, detail=f"خطأ أثناء التحليل: {e}")


def generate_recommendations(mode, threats, prediction, risk_score):
    """Generate mode-specific recommendations."""
    recs = []

    if mode == "children":
        if any(t["category"] in ["sexual_exploitation", "grooming"] for t in threats):
            recs.append({"severity": "critical", "text_ar": "خطر! تم رصد محاولة استدراج أو استغلال. أبلغ الجهات المختصة فوراً.", "text_en": "DANGER! Grooming/exploitation detected. Report to authorities immediately."})
        if any(t["category"] == "cyberbullying" for t in threats):
            recs.append({"severity": "high", "text_ar": "تنمر إلكتروني مرصود. تحدث مع الطفل وأبلغ المنصة.", "text_en": "Cyberbullying detected. Talk to the child and report to platform."})
        if not threats:
            recs.append({"severity": "low", "text_ar": "لم يتم رصد تهديدات. المحتوى يبدو آمناً للأطفال.", "text_en": "No threats detected. Content appears safe for children."})

    elif mode == "intelligence":
        for t in threats[:3]:
            recs.append({"severity": t["severity_en"], "text_ar": f"🔍 {t['name_ar']}: {t['match_count']} مؤشرات مرصودة (خطورة: {t['severity_ar']})", "text_en": f"🔍 {t['name_en']}: {t['match_count']} indicators detected (Level: {t['severity_en']})"})

    elif mode == "parents":
        if risk_score >= 0.7:
            recs.append({"severity": "critical", "text_ar": "محتوى خطير! راجع محادثات طفلك فوراً.", "text_en": "Dangerous content! Review your child's conversations immediately."})
        elif risk_score >= 0.4:
            recs.append({"severity": "high", "text_ar": "محتوى مشبوه. ناقش هذا المحتوى مع طفلك.", "text_en": "Suspicious content. Discuss this with your child."})
        else:
            recs.append({"severity": "low", "text_ar": "محتوى آمن. لا توجد مخاوف حالياً.", "text_en": "Safe content. No concerns at this time."})

    else:  # general
        if prediction == 2:
            recs.append({"severity": "critical", "text_ar": "احتيال مؤكد. حظر المحتوى والإبلاغ.", "text_en": "Confirmed scam. Block and report."})
        elif prediction == 1:
            recs.append({"severity": "high", "text_ar": "محتوى مشبوه. مراجعة يدوية مطلوبة.", "text_en": "Suspicious content. Manual review needed."})
        else:
            recs.append({"severity": "low", "text_ar": "محتوى سليم.", "text_en": "Content is safe."})

    return recs

# ===== Frontend =====
frontend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
os.makedirs(frontend_path, exist_ok=True)

@app.get("/")
async def serve_dashboard():
    f = os.path.join(frontend_path, "index.html")
    if os.path.exists(f): return FileResponse(f)
    return {"message": "Dashboard not built yet."}

@app.get("/en")
async def serve_english():
    f = os.path.join(frontend_path, "en", "index.html")
    if os.path.exists(f): return FileResponse(f)
    return {"message": "English version not available."}

app.mount("/", StaticFiles(directory=frontend_path), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
