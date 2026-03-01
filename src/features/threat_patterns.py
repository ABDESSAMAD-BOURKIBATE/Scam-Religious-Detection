"""
ScamGuard AI — Multi-Threat Pattern Detection
6 threat categories with Arabic keyword patterns, weights, and severity levels.
"""

# ===== THREAT CATEGORIES =====

THREAT_CATEGORIES = {
    "religious_scam": {
        "name_ar": "احتيال ديني",
        "name_en": "Religious Scam",
        "icon": "fa-mosque",
        "color": "red",
        "severity_base": 4,
        "keywords": [
            {"word": "تبرع", "weight": 3}, {"word": "ارسل", "weight": 2},
            {"word": "تحويل", "weight": 3}, {"word": "حساب", "weight": 3},
            {"word": "مبلغ", "weight": 3}, {"word": "ريال", "weight": 2},
            {"word": "دولار", "weight": 2}, {"word": "زكاة", "weight": 1},
            {"word": "صدقة", "weight": 2}, {"word": "لوجه الله", "weight": 2},
            {"word": "ميزان حسناتكم", "weight": 3}, {"word": "يضاعف", "weight": 2},
            {"word": "صدقه جاريه", "weight": 2}, {"word": "فرج", "weight": 1},
            {"word": "انشرها", "weight": 2}, {"word": "لا تتجاهل", "weight": 2},
            {"word": "اقسم بالله", "weight": 2}, {"word": "ساهم", "weight": 2},
            {"word": "عملية جراحية", "weight": 3}, {"word": "مريض", "weight": 2},
            {"word": "يتيم", "weight": 2}, {"word": "أرملة", "weight": 2},
            {"word": "محتاج", "weight": 1}, {"word": "STC Pay", "weight": 4},
            {"word": "الراجحي", "weight": 3}, {"word": "الأهلي", "weight": 3},
        ]
    },

    "sexual_exploitation": {
        "name_ar": "استغلال جنسي",
        "name_en": "Sexual Exploitation",
        "icon": "fa-shield-halved",
        "color": "darkred",
        "severity_base": 5,
        "keywords": [
            {"word": "تعال خاص", "weight": 4}, {"word": "أرسلي صورتك", "weight": 5},
            {"word": "أرسلي صورة", "weight": 5}, {"word": "صور خاصة", "weight": 5},
            {"word": "فيديو خاص", "weight": 5}, {"word": "كاميرا", "weight": 2},
            {"word": "جسمك", "weight": 4}, {"word": "جسدك", "weight": 4},
            {"word": "حبيبتي", "weight": 2}, {"word": "حبيبي", "weight": 2},
            {"word": "نلتقي", "weight": 2}, {"word": "وحدنا", "weight": 3},
            {"word": "لوحدنا", "weight": 3}, {"word": "بدون ما يدري", "weight": 4},
            {"word": "بدون ما تدري", "weight": 4}, {"word": "بدون ما يعرف", "weight": 4},
            {"word": "عيب تخاف", "weight": 3}, {"word": "ما حد يعرف", "weight": 4},
            {"word": "سيكريت", "weight": 3}, {"word": "سناب خاص", "weight": 3},
        ]
    },

    "grooming": {
        "name_ar": "استدراج",
        "name_en": "Grooming / Luring",
        "icon": "fa-user-secret",
        "color": "orange",
        "severity_base": 5,
        "keywords": [
            {"word": "ثق بي", "weight": 3}, {"word": "ثقي فيني", "weight": 3},
            {"word": "سر بيننا", "weight": 5}, {"word": "سرنا", "weight": 4},
            {"word": "لا تخبر أحد", "weight": 5}, {"word": "لا تخبري", "weight": 5},
            {"word": "لا تقول لأحد", "weight": 5}, {"word": "ما بيننا", "weight": 3},
            {"word": "أنت كبير", "weight": 2}, {"word": "أنتي كبيرة", "weight": 2},
            {"word": "ناضج", "weight": 2}, {"word": "ناضجة", "weight": 2},
            {"word": "هديه لك", "weight": 2}, {"word": "هدية", "weight": 1},
            {"word": "أعطيك", "weight": 2}, {"word": "أعلمك", "weight": 1},
            {"word": "تعالي عندي", "weight": 3}, {"word": "تعال عندي", "weight": 3},
            {"word": "أحبك", "weight": 2}, {"word": "عمرك كم", "weight": 3},
            {"word": "وين تسكن", "weight": 4}, {"word": "وين بيتكم", "weight": 4},
            {"word": "اسم مدرستك", "weight": 5}, {"word": "بأي صف", "weight": 3},
        ]
    },

    "cyberbullying": {
        "name_ar": "تنمر إلكتروني",
        "name_en": "Cyberbullying",
        "icon": "fa-face-angry",
        "color": "purple",
        "severity_base": 3,
        "keywords": [
            {"word": "غبي", "weight": 3}, {"word": "غبية", "weight": 3},
            {"word": "قبيح", "weight": 3}, {"word": "قبيحة", "weight": 3},
            {"word": "بشع", "weight": 3}, {"word": "ما تستاهل", "weight": 3},
            {"word": "ما تستاهلين", "weight": 3}, {"word": "فاشل", "weight": 3},
            {"word": "فاشلة", "weight": 3}, {"word": "حقير", "weight": 4},
            {"word": "كلب", "weight": 4}, {"word": "حمار", "weight": 3},
            {"word": "تافه", "weight": 3}, {"word": "تافهة", "weight": 3},
            {"word": "اطلع", "weight": 2}, {"word": "انقلعي", "weight": 3},
            {"word": "اسكت", "weight": 2}, {"word": "اسكتي", "weight": 2},
            {"word": "لا أحد يحبك", "weight": 4}, {"word": "ما لك أصحاب", "weight": 3},
            {"word": "أكرهك", "weight": 3}, {"word": "انتحر", "weight": 5},
            {"word": "انتحري", "weight": 5}, {"word": "ما تنفع", "weight": 3},
        ]
    },

    "financial_fraud": {
        "name_ar": "احتيال مالي",
        "name_en": "Financial Fraud",
        "icon": "fa-sack-dollar",
        "color": "gold",
        "severity_base": 4,
        "keywords": [
            {"word": "ربح مضمون", "weight": 5}, {"word": "استثمار", "weight": 2},
            {"word": "عرض محدود", "weight": 3}, {"word": "عوائد", "weight": 3},
            {"word": "أرباح يومية", "weight": 5}, {"word": "فوركس", "weight": 3},
            {"word": "تداول", "weight": 2}, {"word": "عملات رقمية", "weight": 3},
            {"word": "بيتكوين", "weight": 2}, {"word": "كريبتو", "weight": 2},
            {"word": "مشروع ناجح", "weight": 2}, {"word": "فرصة ذهبية", "weight": 4},
            {"word": "لن تتكرر", "weight": 3}, {"word": "دخل شهري", "weight": 3},
            {"word": "بدون مجهود", "weight": 4}, {"word": "من البيت", "weight": 1},
            {"word": "اضغط الرابط", "weight": 4}, {"word": "رابط التسجيل", "weight": 4},
            {"word": "ادخل بياناتك", "weight": 5}, {"word": "رقم البطاقة", "weight": 5},
            {"word": "الرقم السري", "weight": 5}, {"word": "OTP", "weight": 4},
        ]
    },

    "manipulation": {
        "name_ar": "تلاعب نفسي",
        "name_en": "Psychological Manipulation",
        "icon": "fa-brain",
        "color": "teal",
        "severity_base": 3,
        "keywords": [
            {"word": "أقسم بالله", "weight": 2}, {"word": "والله العظيم", "weight": 2},
            {"word": "لازم الحين", "weight": 3}, {"word": "بسرعة", "weight": 2},
            {"word": "قبل ما يفوت", "weight": 3}, {"word": "آخر فرصة", "weight": 3},
            {"word": "إذا تحبني", "weight": 3}, {"word": "إذا تحبيني", "weight": 3},
            {"word": "أثبت حبك", "weight": 3}, {"word": "أثبتي حبك", "weight": 3},
            {"word": "ما تثق فيني", "weight": 3}, {"word": "ما تثقين", "weight": 3},
            {"word": "الكل يسوي كذا", "weight": 3}, {"word": "عادي", "weight": 1},
            {"word": "لا تكون جبان", "weight": 3}, {"word": "لا تكوني", "weight": 2},
            {"word": "ترا بقول", "weight": 4}, {"word": "بفضحك", "weight": 5},
            {"word": "عندي صورك", "weight": 5}, {"word": "عندي محادثاتك", "weight": 5},
        ]
    },

    "extremism": {
        "name_ar": "تطرف كراهية",
        "name_en": "Extremism & Terrorism",
        "icon": "fa-biohazard",
        "color": "darkred",
        "severity_base": 5,
        "keywords": [
            {"word": "الجهاد", "weight": 5}, {"word": "استهداف", "weight": 5},
            {"word": "قيام الخلافة", "weight": 5}, {"word": "الدولة الإسلامية", "weight": 4},
            {"word": "الدولة الكافرة", "weight": 5}, {"word": "كافر", "weight": 3},
            {"word": "كفار", "weight": 3}, {"word": "حلال الدم", "weight": 5},
            {"word": "انضموا إلينا", "weight": 4}, {"word": "أعددنا العدة", "weight": 4},
            {"word": "السلاح", "weight": 4}, {"word": "تدمير", "weight": 4},
            {"word": "أعداء الدين", "weight": 4}, {"word": "طاغية", "weight": 3},
            {"word": "طواغيت", "weight": 4}, {"word": "المرتدين", "weight": 4},
            {"word": "عملية استشهادية", "weight": 5}, {"word": "تفجير", "weight": 5},
            {"word": "نحر", "weight": 5}, {"word": "نصرة الحق", "weight": 2},
        ]
    }
}

# ===== Mode configurations =====
MODE_THREATS = {
    "general": list(THREAT_CATEGORIES.keys()),
    "children": ["sexual_exploitation", "grooming", "cyberbullying", "manipulation"],
    "intelligence": list(THREAT_CATEGORIES.keys()),
    "parents": list(THREAT_CATEGORIES.keys()),
}


def detect_threats(text, mode="general"):
    """
    Detect threats in text based on mode.
    Returns list of detected threats with scores.
    """
    text_lower = text.lower()
    active_threats = MODE_THREATS.get(mode, MODE_THREATS["general"])
    results = []

    for cat_key in active_threats:
        cat = THREAT_CATEGORIES[cat_key]
        matched_words = []
        total_weight = 0

        for kw in cat["keywords"]:
            if kw["word"] in text_lower:
                matched_words.append({
                    "word": kw["word"],
                    "weight": kw["weight"],
                })
                total_weight += kw["weight"]

        if matched_words:
            # Calculate threat score (0-1)
            max_possible = sum(k["weight"] for k in cat["keywords"][:8])  # Top 8
            score = min(total_weight / max(max_possible, 1), 1.0)

            # Severity: low (1-2), medium (3), high (4), critical (5)
            severity = min(cat["severity_base"] + (len(matched_words) // 3), 5)
            severity_labels = {
                1: ("low", "منخفض"), 2: ("low", "منخفض"),
                3: ("medium", "متوسط"), 4: ("high", "مرتفع"),
                5: ("critical", "حرج")
            }

            results.append({
                "category": cat_key,
                "name_ar": cat["name_ar"],
                "name_en": cat["name_en"],
                "icon": cat["icon"],
                "color": cat["color"],
                "score": round(score, 2),
                "severity": severity,
                "severity_en": severity_labels[severity][0],
                "severity_ar": severity_labels[severity][1],
                "matched_words": matched_words,
                "match_count": len(matched_words),
            })

    # Sort by score descending
    results.sort(key=lambda x: x["score"], reverse=True)
    return results


def get_mode_info(mode):
    """Return display info for a mode."""
    modes = {
        "general": {
            "name_ar": "كشف عام",
            "name_en": "General Detection",
            "icon": "fa-shield-halved",
            "description_ar": "فحص شامل لجميع أنواع التهديدات",
            "description_en": "Comprehensive scan for all threat types",
        },
        "children": {
            "name_ar": "حماية الأطفال",
            "name_en": "Children Protection",
            "icon": "fa-child-reaching",
            "description_ar": "كشف الاستدراج والتنمر والاستغلال الجنسي",
            "description_en": "Detect grooming, bullying & sexual exploitation",
        },
        "intelligence": {
            "name_ar": "تحليل استخباراتي",
            "name_en": "Intelligence Analysis",
            "icon": "fa-user-secret",
            "description_ar": "تحليل عميق مع BERT ومصفوفة مخاطر كاملة",
            "description_en": "Deep analysis with BERT emotion engine & risk matrix",
        },
        "parents": {
            "name_ar": "مراقبة الوالدين",
            "name_en": "Parents Monitoring",
            "icon": "fa-people-roof",
            "description_ar": "تنبيهات مبسطة بالألوان مع توصيات واضحة",
            "description_en": "Simplified color-coded alerts with clear recommendations",
        },
    }
    return modes.get(mode, modes["general"])
