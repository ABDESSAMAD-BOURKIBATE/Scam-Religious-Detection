import pandas as pd
import numpy as np
import logging
import os
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# === نظام تصنيف متقدم بالنقاط (Scoring System) ===

# كلمات احتيال صريح مع أوزان
SCAM_SIGNALS = {
    'high': {  # وزن 3
        'words': ['تحويل بنكي', 'رقم الحساب', 'حساب الراجحي', 'حساب الاهلي', 'آيبان', 'ايبان',
                  'ارسلوا على', 'حولوا على', 'stc pay', 'تكفون ساعدوني',
                  'محتاجين تبرعات', 'اقسم بالله محتاج', 'حالة انسانية حرجة'],
        'weight': 3
    },
    'medium': {  # وزن 2
        'words': ['تبرع', 'تبرعات', 'مساعده ماليه', 'مساعدة مالية', 'سداد', 'ديون', 'كفالة',
                  'محتاج', 'تكفل', 'ارسل', 'حوالة', 'مبلغ', 'ريال', 'دولار',
                  'علاج مكلف', 'عملية جراحية', 'غسيل كلى', 'مريض بالسرطان',
                  'تكاليف علاج', 'تكاليف مستشفى', 'انقذوا', 'نداء استغاثة'],
        'weight': 2
    },
    'low': {  # وزن 1
        'words': ['يتيم', 'ارملة', 'اسرة فقيرة', 'محتاج', 'ساعدوهم', 'لوجه الله',
                  'صدقة جارية', 'ميزان حسناتكم', 'اجر', 'فرج', 'يبارك'],
        'weight': 1
    }
}

# كلمات مشبوهة مع أوزان
SUSPICIOUS_SIGNALS = {
    'high': {
        'words': ['انشرها ولا تتجاهل', 'ان تجاهلت', 'ان لم تنشر', 'رايت النبي في المنام',
                  'فك السحر', 'علاج روحاني', 'شيخ معالج', 'جلب الحبيب', 'فتح النصيب',
                  'ستسمع خبر', 'معجزه', 'لن تصدق ماذا'],
        'weight': 3
    },
    'medium': {
        'words': ['انشرها', 'لا تتجاهل', 'اقسم بالله', 'شارك المنشور', 'شارك الرسالة',
                  'اكتب سبحان الله', 'شارك ولك الاجر', 'انشر تؤجر',
                  'لا تخلي الرسالة تقف', 'اذا حذفت', 'ستندم', 'رقية'],
        'weight': 2
    },
    'low': {
        'words': ['من نشر', 'في المنام', 'كتبت اسم الله', 'ابتزاز'],
        'weight': 1
    }
}

# كلمات دينية شرعية (إيجابية - تقلل من احتمال الاحتيال)
LEGIT_SIGNALS = [
    'قال الله تعالى', 'قال رسول الله', 'صلى الله عليه وسلم',
    'حديث', 'تفسير', 'فتوى', 'خطبة', 'درس ديني',
    'القران الكريم', 'سورة', 'صيام', 'صلاة', 'رمضان',
    'اذكار', 'دعاء', 'الحج', 'العمرة', 'تلاوة', 'فقه',
    'سنة نبوية', 'هدي النبي', 'بر الوالدين', 'صلة الرحم',
    'التوبة', 'الاستغفار', 'الصبر', 'التوكل', 'الاخلاص',
    'حكم شرعي', 'عيد', 'مكة', 'المدينة',
]

def calculate_score(text, signals_dict):
    """حساب نقاط التصنيف بناءً على الكلمات المفتاحية وأوزانها"""
    text = str(text).lower()
    score = 0
    for level, data in signals_dict.items():
        for word in data['words']:
            if word in text:
                score += data['weight']
    return score

def classify_real_tweet(text: str) -> str:
    """
    تصنيف ذكي بنظام النقاط:
    - حساب نقاط الاحتيال والمشبوه والشرعي
    - التصنيف بناءً على أعلى نقاط
    """
    text = str(text).lower()

    scam_score = calculate_score(text, SCAM_SIGNALS)
    susp_score = calculate_score(text, SUSPICIOUS_SIGNALS)
    legit_score = sum(1 for word in LEGIT_SIGNALS if word in text)

    # قواعد التصنيف
    if scam_score >= 4:
        return "Explicit Religious Scam"
    elif scam_score >= 2 and legit_score < 2:
        return "Explicit Religious Scam"
    elif susp_score >= 3:
        return "Suspicious Religious Manipulation"
    elif susp_score >= 1 and scam_score >= 1:
        return "Suspicious Religious Manipulation"
    else:
        return "Legitimate Religious Post"

def main():
    scam_file = os.path.join("data", "raw", "real_scam_tweets.csv")
    suspicious_file = os.path.join("data", "raw", "real_suspicious_tweets.csv")
    legit_file = os.path.join("data", "raw", "real_legit_tweets.csv")
    synthetic_file = os.path.join("data", "raw", "scam_religious_corpus_v1.csv")
    merged_output = os.path.join("data", "raw", "merged_final_corpus.csv")

    all_dfs = []

    # === 1. تحميل التغريدات الحقيقية من الفئات الثلاث ===
    for filepath, default_label in [
        (scam_file, "Explicit Religious Scam"),
        (suspicious_file, "Suspicious Religious Manipulation"),
        (legit_file, "Legitimate Religious Post"),
    ]:
        if os.path.exists(filepath):
            logging.info(f"جاري تحميل: {filepath}")
            df = pd.read_csv(filepath, low_memory=False)

            # البحث عن عمود النص
            text_col = None
            for col in df.columns:
                if 'text' in col.lower() or 'tweet' in col.lower():
                    text_col = col
                    break
            if not text_col:
                logging.warning(f"لم يتم العثور على عمود النص في {filepath}")
                continue

            df = df[[text_col]].copy()
            df.rename(columns={text_col: 'text'}, inplace=True)
            df['text'] = df['text'].astype(str)

            # تصنيف ذكي بدلاً من استخدام التصنيف الافتراضي فقط
            logging.info(f"التصنيف الذكي لـ {len(df):,} تغريدة...")
            df['label'] = df['text'].apply(classify_real_tweet)
            df['source'] = 'Real Twitter Data'

            # إزالة المكررات
            df.drop_duplicates(subset=['text'], inplace=True)

            logging.info(f"  → {len(df):,} تغريدة فريدة")
            logging.info(f"  → التوزيع: {df['label'].value_counts().to_dict()}")
            all_dfs.append(df)
        else:
            logging.warning(f"ملف غير موجود: {filepath}")

    # === 2. تحميل البيانات الاصطناعية ===
    if os.path.exists(synthetic_file):
        logging.info(f"جاري تحميل البيانات الاصطناعية: {synthetic_file}")
        df_synth = pd.read_csv(synthetic_file)

        # حساب التوازن المطلوب
        real_total = sum(len(df) for df in all_dfs)
        # نضيف بيانات اصطناعية بنسبة 20% من البيانات الحقيقية لسد فجوات الفئات
        SYNTH_SIZE = min(int(real_total * 0.2), len(df_synth))
        
        if SYNTH_SIZE > 0:
            df_synth_sampled = df_synth.sample(n=SYNTH_SIZE, random_state=42)
            logging.info(f"أخذ {SYNTH_SIZE:,} عينة اصطناعية (20% من الحقيقي)")
            all_dfs.append(df_synth_sampled)

    if not all_dfs:
        logging.error("لا توجد بيانات للدمج!")
        return

    # === 3. الدمج النهائي ===
    logging.info("جاري دمج جميع البيانات...")
    df_final = pd.concat(all_dfs, ignore_index=True)

    # خلط البيانات
    df_final = df_final.sample(frac=1, random_state=42).reset_index(drop=True)

    # إزالة المكررات النهائية
    before = len(df_final)
    df_final.drop_duplicates(subset=['text'], inplace=True)
    logging.info(f"إزالة {before - len(df_final):,} تغريدة مكررة")

    logging.info(f"جاري حفظ المدونة النهائية في: {merged_output}")
    df_final.to_csv(merged_output, index=False, encoding='utf-8-sig')

    logging.info("=" * 60)
    logging.info("اكتمل دمج البيانات بنجاح!")
    logging.info(f"إجمالي البيانات النهائية: {len(df_final):,} سطر")
    logging.info(f"\nتوزيع التصنيفات:\n{df_final['label'].value_counts()}")
    logging.info(f"\nتوزيع المصادر:\n{df_final['source'].value_counts()}")
    logging.info("=" * 60)

if __name__ == "__main__":
    main()
