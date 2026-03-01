"""
ScamGuard AI — BERT Arabic Emotion Analyzer
Uses CAMeL-Lab/bert-base-arabic-camelbert-da-sentiment for sentiment analysis
and custom emotion scoring (fear, hope, guilt, urgency).
"""
import re
import logging
from transformers import pipeline

logger = logging.getLogger(__name__)

# ===== Emotion keyword dictionaries =====
FEAR_WORDS = [
    'خوف', 'خائف', 'يخاف', 'رعب', 'مرعب', 'فزع', 'هلاك', 'عذاب', 'عقاب',
    'نار', 'جهنم', 'حساب', 'يوم القيامة', 'الموت', 'القبر', 'ذنب', 'معصية',
    'غضب الله', 'لعنة', 'ويل', 'حذر', 'احذر', 'خطر', 'كارثة', 'مصيبة',
    'ستندم', 'ستخسر', 'سيصيبك', 'مكروه', 'بلاء', 'ابتلاء'
]

HOPE_WORDS = [
    'جنة', 'الفردوس', 'رحمة', 'مغفرة', 'بركة', 'يبارك', 'أجر', 'ثواب',
    'حسنات', 'يضاعف', 'فرج', 'رزق', 'خير', 'نعمة', 'شفاء', 'معجزة',
    'ستسعد', 'ستفرح', 'خبر سعيد', 'ستتحقق', 'أمنية', 'حلم', 'نجاح',
    'ربح', 'مليون', 'ثروة', 'مضمون', 'فوز', 'جائزة'
]

GUILT_WORDS = [
    'لا تتجاهل', 'لا تمرر', 'إثم', 'ذنب', 'عيب', 'حرام', 'تقصير',
    'ستحاسب', 'أمام الله', 'يوم الحساب', 'ألا تستحي', 'ضمير',
    'كيف تنام', 'وأنت تعلم', 'مسؤولية', 'واجب', 'أخوك المسلم',
    'أختك المسلمة', 'يتيم', 'مسكين', 'أرملة', 'فقير'
]

URGENCY_WORDS = [
    'عاجل', 'فوراً', 'الآن', 'بسرعة', 'لا تتأخر', 'لازم', 'ضروري',
    'آخر فرصة', 'قبل فوات', 'اليوم فقط', 'ينتهي', 'عرض محدود',
    'سارع', 'أسرع', 'لا تضيع', 'الحق', 'حالاً', 'هذه اللحظة',
    'طارئ', 'مستعجل', 'خلال ساعة', 'خلال دقائق', 'آخر يوم'
]


class BERTEmotionAnalyzer:
    """Arabic BERT sentiment + emotion intensity analyzer."""

    def __init__(self):
        self.model = None
        self.is_loaded = False

    def load_model(self):
        """Load CAMeL-Lab BERT model (downloads ~500MB first time)."""
        if self.is_loaded:
            return
        try:
            logger.info("جاري تحميل نموذج BERT العربي (CAMeL-Lab)...")
            self.model = pipeline(
                "sentiment-analysis",
                model="CAMeL-Lab/bert-base-arabic-camelbert-da-sentiment",
                device=-1  # CPU mode
            )
            self.is_loaded = True
            logger.info("تم تحميل نموذج BERT بنجاح!")
        except Exception as e:
            logger.error(f"فشل تحميل نموذج BERT: {e}")
            self.is_loaded = False

    def _count_matches(self, text, word_list):
        """Count how many words from a list appear in the text."""
        text_lower = text.lower()
        count = 0
        for word in word_list:
            if word in text_lower:
                count += 1
        return count

    def analyze(self, text):
        """
        Full emotion analysis: BERT sentiment + keyword-based emotion scores.
        Returns dict with sentiment, confidence, and 4 emotion levels.
        """
        result = {
            "sentiment": "neutral",
            "sentiment_ar": "محايد",
            "confidence": 0.0,
            "fear_level": 0.0,
            "hope_level": 0.0,
            "guilt_level": 0.0,
            "urgency_level": 0.0,
            "dominant_emotion": "neutral",
            "dominant_emotion_ar": "محايد",
            "emotional_intensity": 0.0,
            "bert_available": False
        }

        # --- BERT Sentiment ---
        if self.is_loaded and self.model:
            try:
                # BERT max = 512 tokens, truncate text
                truncated = text[:512]
                bert_result = self.model(truncated)
                label = bert_result[0]["label"].lower()
                score = bert_result[0]["score"]

                sentiment_map = {
                    "positive": ("positive", "إيجابي"),
                    "negative": ("negative", "سلبي"),
                    "neutral": ("neutral", "محايد"),
                }
                en, ar = sentiment_map.get(label, ("neutral", "محايد"))
                result["sentiment"] = en
                result["sentiment_ar"] = ar
                result["confidence"] = round(score, 4)
                result["bert_available"] = True
            except Exception as e:
                logger.warning(f"BERT analysis failed: {e}")

        # --- Keyword-based emotion scoring ---
        fear_count = self._count_matches(text, FEAR_WORDS)
        hope_count = self._count_matches(text, HOPE_WORDS)
        guilt_count = self._count_matches(text, GUILT_WORDS)
        urgency_count = self._count_matches(text, URGENCY_WORDS)

        # Normalize to 0-1 scale (cap at 5 matches = 1.0)
        result["fear_level"] = round(min(fear_count / 5, 1.0), 2)
        result["hope_level"] = round(min(hope_count / 5, 1.0), 2)
        result["guilt_level"] = round(min(guilt_count / 5, 1.0), 2)
        result["urgency_level"] = round(min(urgency_count / 5, 1.0), 2)

        # Boost with BERT sentiment
        if result["bert_available"]:
            if result["sentiment"] == "negative" and result["confidence"] > 0.7:
                result["fear_level"] = min(result["fear_level"] + 0.2, 1.0)
                result["urgency_level"] = min(result["urgency_level"] + 0.1, 1.0)
            elif result["sentiment"] == "positive" and result["confidence"] > 0.9:
                result["hope_level"] = min(result["hope_level"] + 0.2, 1.0)

        # Determine dominant emotion
        emotions = {
            "fear": (result["fear_level"], "خوف"),
            "hope": (result["hope_level"], "أمل/إغراء"),
            "guilt": (result["guilt_level"], "ذنب"),
            "urgency": (result["urgency_level"], "استعجال"),
        }
        dominant = max(emotions, key=lambda k: emotions[k][0])
        if emotions[dominant][0] > 0.1:
            result["dominant_emotion"] = dominant
            result["dominant_emotion_ar"] = emotions[dominant][1]

        # Overall emotional intensity
        result["emotional_intensity"] = round(
            (result["fear_level"] + result["hope_level"] +
             result["guilt_level"] + result["urgency_level"]) / 4, 2
        )

        return result


# Singleton instance
bert_analyzer = BERTEmotionAnalyzer()
