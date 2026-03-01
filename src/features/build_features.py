import pandas as pd
import re
import logging
import os
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# كلمات التوقف العربية الأساسية
ARABIC_STOPWORDS = {
    "في", "من", "على", "إلى", "عن", "بـ", "لـ", "كـ", "و", "أو", "ثم", "حتى",
    "الذي", "التي", "الذين", "اللاتي", "هذا", "هذه", "هؤلاء", "ذلك", "تلك",
    "هو", "هي", "هم", "هن", "نحن", "أنا", "أنت", "أنتم", "كان", "كانت", "يكون",
    "إن", "أن", "قد", "لقد", "هل", "ما", "كيف", "أين", "متى", "ليس", "لا", "لم", "لن", "يا",
    "بعد", "قبل", "بين", "عند", "كل", "بعض", "غير", "ذات", "مثل", "لكن", "او",
    "فقط", "ايضا", "اذا", "حيث", "منذ", "خلال", "ضد", "نحو", "حول", "فوق", "تحت",
}

def clean_arabic_text(text: str) -> str:
    """
    دالة شاملة لتنظيف وتقييس النصوص العربية للمشروع الأمني
    """
    if not isinstance(text, str):
        return ""

    # 1. استبدال الأرقام والحسابات البنكية بـ Token
    text = re.sub(r'(?:\+?\d{1,3}[-.\s]?)?\d{8,20}', ' <ACCOUNT_NUM> ', text)
    text = re.sub(r'\d+', ' <NUM> ', text)

    # 2. استبدال الروابط بـ Token
    text = re.sub(r'http[s]?://\S+', ' <URL> ', text)

    # 3. إزالة mentions و hashtags
    text = re.sub(r'@\w+', ' ', text)
    text = re.sub(r'#', ' ', text)

    # 4. إزالة التشكيل (Arabic Diacritics)
    text = re.sub(r'[\u0617-\u061A\u064B-\u0652]', '', text)

    # 5. التقييس (Normalization)
    text = re.sub(r'[إأآا]', 'ا', text)
    text = re.sub(r'ة', 'ه', text)
    text = re.sub(r'ى', 'ي', text)
    text = re.sub(r'ؤ', 'و', text)
    text = re.sub(r'ئ', 'ي', text)

    # 6. إزالة الرموز وعلامات الترقيم (مع الاحتفاظ بالـ Tokens)
    text = re.sub(r'[^\w\s<>]', ' ', text)

    # 7. إزالة الكلمات الإنجليزية القصيرة (< 3 حروف) والرموز
    text = re.sub(r'\b[a-zA-Z]{1,2}\b', ' ', text)

    # 8. إزالة المسافات المتعددة
    text = re.sub(r'\s+', ' ', text).strip()

    # 9. إزالة كلمات التوقف (Stop words)
    words = text.split()
    words = [word for word in words if word not in ARABIC_STOPWORDS]

    return " ".join(words)

def main():
    input_path = os.path.join("data", "raw", "merged_final_corpus.csv")
    output_path = os.path.join("data", "processed", "cleaned_corpus_v1.csv")

    if not os.path.exists(input_path):
        logging.error(f"لم يتم العثور على الملف: {input_path}")
        return

    logging.info(f"جاري قراءة البيانات من: {input_path}")

    # معالجة بالدفعات للملفات الكبيرة
    chunk_size = 100_000
    total_rows = 0
    first_chunk = True

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    for i, chunk in enumerate(pd.read_csv(input_path, chunksize=chunk_size, low_memory=False)):
        chunk['cleaned_text'] = chunk['text'].astype(str).apply(clean_arabic_text)

        # إزالة النصوص الفارغة
        chunk = chunk[chunk['cleaned_text'].str.strip().astype(bool)]

        total_rows += len(chunk)

        # حفظ تدريجي
        chunk.to_csv(output_path, mode='a' if not first_chunk else 'w',
                     header=first_chunk, index=False, encoding='utf-8-sig')
        first_chunk = False

        logging.info(f"دفعة {i+1}: تم معالجة {total_rows:,} سطر")

    logging.info(f"تمت المعالجة بنجاح! إجمالي: {total_rows:,} سطر → {output_path}")

if __name__ == "__main__":
    main()
