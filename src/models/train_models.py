import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.svm import LinearSVC
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import joblib
import logging
import os
from scipy.sparse import hstack

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def evaluate_model(model, X_test, y_test, model_name):
    """تقييم النموذج وحساب مقاييس الأداء"""
    logging.info(f"--- تقييم نموذج: {model_name} ---")
    predictions = model.predict(X_test)
    acc = accuracy_score(y_test, predictions)
    report = classification_report(y_test, predictions)
    cm = confusion_matrix(y_test, predictions)

    logging.info(f"Accuracy: {acc:.4f}\n")
    logging.info(f"Classification Report:\n{report}")
    logging.info(f"Confusion Matrix:\n{cm}\n")
    return acc

def main():
    features_path = os.path.join("data", "processed", "engineered_features.csv")
    tfidf_model_path = os.path.join("models", "tfidf_vectorizer.pkl")
    best_model_path = os.path.join("models", "best_scam_detector.pkl")

    if not os.path.exists(features_path) or not os.path.exists(tfidf_model_path):
        logging.error("البيانات أو ملف TF-IDF غير موجود!")
        return

    logging.info("جاري تحميل البيانات والميزات...")
    df = pd.read_csv(features_path, low_memory=False)

    df['cleaned_text'] = df['cleaned_text'].fillna('')

    logging.info(f"حجم البيانات: {len(df):,} سطر")
    logging.info(f"توزيع التصنيفات:\n{df['label'].value_counts()}")

    # Label Encoding
    label_mapping = {
        "Legitimate Religious Post": 0,
        "Suspicious Religious Manipulation": 1,
        "Explicit Religious Scam": 2
    }
    df['Label_Encoded'] = df['label'].map(label_mapping)

    # إزالة الأسطر بدون تصنيف
    df = df.dropna(subset=['Label_Encoded'])
    df['Label_Encoded'] = df['Label_Encoded'].astype(int)

    y = df['Label_Encoded']

    logging.info("جاري تطبيق TF-IDF على النصوص...")
    tfidf = joblib.load(tfidf_model_path)
    X_text_tfidf = tfidf.transform(df['cleaned_text'])

    logging.info("دمج ميزات TF-IDF مع الميزات الهندسية...")
    custom_feature_cols = ['has_account_num', 'financial_request_score', 'urgency_score', 'religious_manipulation_score']
    # إضافة ميزات إضافية إن وجدت
    for col in ['text_length', 'url_count']:
        if col in df.columns:
            custom_feature_cols.append(col)

    custom_features = df[custom_feature_cols].values
    X_combined = hstack([X_text_tfidf, custom_features])

    logging.info("تقسيم البيانات 80/20...")
    X_train, X_test, y_train, y_test = train_test_split(
        X_combined, y, test_size=0.2, random_state=42, stratify=y
    )

    logging.info(f"حجم التدريب: {X_train.shape[0]:,} عينة | حجم الاختبار: {X_test.shape[0]:,} عينة")

    # === تدريب النماذج ===
    models = {
        "SGD Classifier (Fast & Scalable)": SGDClassifier(
            loss='hinge',
            class_weight='balanced',
            max_iter=1000,
            random_state=42,
            n_jobs=-1,
        ),
        "Logistic Regression": LogisticRegression(
            max_iter=1000,
            random_state=42,
            class_weight='balanced',
            solver='saga',
            n_jobs=-1,
        ),
        "Linear SVM": LinearSVC(
            random_state=42,
            dual='auto',
            class_weight='balanced',
            max_iter=2000,
        ),
    }

    best_acc = 0
    best_model_name = ""
    best_model = None

    for name, model in models.items():
        logging.info(f"جاري تدريب نموذج {name}...")
        try:
            model.fit(X_train, y_train)
            acc = evaluate_model(model, X_test, y_test, name)

            if acc > best_acc:
                best_acc = acc
                best_model_name = name
                best_model = model
        except Exception as e:
            logging.error(f"فشل تدريب {name}: {e}")

    logging.info("=" * 60)
    logging.info(f"أفضل نموذج: {best_model_name} بدقة {best_acc:.4f}")
    logging.info("=" * 60)

    logging.info(f"جاري حفظ أفضل نموذج في: {best_model_path}")
    joblib.dump(best_model, best_model_path)
    logging.info("تم الحفظ بنجاح! النموذج جاهز للاستخدام في الـ API.")

if __name__ == "__main__":
    main()
