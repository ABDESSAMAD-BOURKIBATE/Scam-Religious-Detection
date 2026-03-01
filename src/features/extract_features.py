import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib
import logging
import os
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def extract_custom_features(df):
    """
    استخراج الخصائص الدلالية (Semantic Features) من النصوص.
    """
    logging.info("استخراج الخصائص الدلالية...")

    df['cleaned_text'] = df['cleaned_text'].astype(str)

    # 1. وجود أرقام حسابات
    df['has_account_num'] = df['cleaned_text'].str.contains(
        '<account_num>|<num>', case=False, na=False).astype(int)

    # 2. نقاط الطلب المالي
    financial_words = ['تبرع', 'ارسل', 'تحويل', 'حساب', 'مبلغ', 'ريال', 'دولار',
                       'تكلفه', 'تكاليف', 'مساهمه', 'ساهم', 'سداد', 'ديون', 'كفاله',
                       'حواله', 'ايبان', 'بنكي']
    financial_pattern = '|'.join(financial_words)
    df['financial_request_score'] = df['cleaned_text'].str.count(financial_pattern)

    # 3. نقاط الاستعجال
    urgency_words = ['عاجل', 'انقذوا', 'استغاثه', 'بسرعه', 'ضروري', 'حرج', 'خطر',
                     'طرد', 'مستشفي', 'يعاني', 'مريض', 'سرطان', 'يتيم', 'ارمله',
                     'محتاج', 'تكفون', 'ساعدوني', 'حاله انسانيه']
    urgency_pattern = '|'.join(urgency_words)
    df['urgency_score'] = df['cleaned_text'].str.count(urgency_pattern)

    # 4. نقاط التلاعب الديني
    religious_promises = ['ميزان', 'حسنات', 'يضاعف', 'فرج', 'صدقه جاريه', 'يبارك',
                          'اجر', 'لوجه الله', 'الجنه', 'انشرها', 'تتجاهل',
                          'اقسم بالله', 'شارك ولك', 'لا تبخل', 'صدقه']
    promise_pattern = '|'.join(religious_promises)
    df['religious_manipulation_score'] = df['cleaned_text'].str.count(promise_pattern)

    # 5. طول النص
    df['text_length'] = df['cleaned_text'].apply(len)

    # 6. عدد الروابط
    df['url_count'] = df['cleaned_text'].str.count('<url>')

    return df

def main():
    input_path = os.path.join("data", "processed", "cleaned_corpus_v1.csv")
    output_features_path = os.path.join("data", "processed", "engineered_features.csv")
    tfidf_model_path = os.path.join("models", "tfidf_vectorizer.pkl")

    if not os.path.exists(input_path):
        logging.error(f"لم يتم العثور على الملف: {input_path}")
        return

    logging.info(f"جاري تحميل البيانات المنظفة من: {input_path}")
    df = pd.read_csv(input_path, low_memory=False)

    df['cleaned_text'] = df['cleaned_text'].fillna('')

    logging.info(f"حجم البيانات: {len(df):,} سطر")

    logging.info("استخراج الخصائص الذكية...")
    df = extract_custom_features(df)

    logging.info("تجهيز TF-IDF Vectorizer...")
    # زيادة max_features وإضافة sublinear_tf لأداء أفضل مع البيانات الكبيرة
    tfidf = TfidfVectorizer(
        max_features=10000,
        ngram_range=(1, 2),
        sublinear_tf=True,        # تحسين الأداء مع البيانات الكبيرة
        min_df=5,                  # تجاهل الكلمات النادرة جداً
        max_df=0.95,               # تجاهل الكلمات الشائعة جداً
    )

    logging.info("تدريب TF-IDF على النصوص...")
    tfidf.fit(df['cleaned_text'])

    logging.info(f"حفظ نموذج TF-IDF في: {tfidf_model_path}")
    os.makedirs(os.path.dirname(tfidf_model_path), exist_ok=True)
    joblib.dump(tfidf, tfidf_model_path)

    logging.info(f"حفظ البيانات مع الخصائص في: {output_features_path}")
    df.to_csv(output_features_path, index=False, encoding='utf-8-sig')

    logging.info("تمت هندسة الخصائص بنجاح!")
    logging.info(f"عدد الخصائص في TF-IDF: {len(tfidf.vocabulary_)}")
    print(df[['has_account_num', 'financial_request_score', 'urgency_score', 'religious_manipulation_score']].describe())

if __name__ == "__main__":
    main()
