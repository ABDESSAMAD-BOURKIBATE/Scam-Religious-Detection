import pandas as pd
import logging
import os
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def contains_any(text, keywords):
    """تتحقق مما إذا كان النص يحتوي على أي كلمة من الكلمات المفتاحية"""
    if pd.isna(text):
        return False
    text = str(text).lower()
    return any(keyword in text for keyword in keywords)

def main():
    input_file = os.path.join("data", "raw", "TweetsStreamingTotal.csv")
    output_scam = os.path.join("data", "raw", "real_scam_tweets.csv")
    output_legit = os.path.join("data", "raw", "real_legit_tweets.csv")
    output_suspicious = os.path.join("data", "raw", "real_suspicious_tweets.csv")

    if not os.path.exists(input_file):
        logging.error(f"لم يتم العثور على الملف الضخم: {input_file}")
        return

    # === كلمات مفتاحية موسعة لكل فئة ===

    # 1. كلمات الاحتيال المالي/الديني (Scam)
    scam_keywords = [
        'تبرع', 'تحويل بنكي', 'رقم الحساب', 'حساب الراجحي', 'حساب الاهلي',
        'سداد', 'ديون', 'كفالة', 'محتاج', 'تكفل', 'مساعدة مالية',
        'ارسل', 'حوالة', 'stc pay', 'تكاليف علاج', 'علاج مكلف',
        'عملية جراحية', 'غسيل كلى', 'مستشفى', 'مريض بالسرطان',
        'اقسم بالله محتاج', 'تكفون ساعدوني', 'محتاجين تبرعات',
        'ارسلوا على', 'حولوا على', 'رقم الايبان', 'آيبان',
        'يتيم محتاج', 'ارملة محتاجة', 'اسرة محتاجة', 'فقير محتاج',
        'حالة انسانية', 'نداء استغاثة', 'انقذوا', 'ساعدوهم',
    ]

    # 2. كلمات المحتوى الديني المشبوه (Suspicious)
    suspicious_keywords = [
        'انشرها', 'لا تتجاهل', 'اقسم بالله', 'من نشر', 'ستسمع خبر',
        'تتجاهل', 'ان تجاهلت', 'شارك المنشور', 'شارك الرسالة',
        'رايت النبي', 'في المنام', 'معجزة', 'اكتب سبحان الله',
        'ان لم تنشر', 'ستندم', 'لن تصدق', 'كتبت اسم الله',
        'شارك ولك الاجر', 'انشر تؤجر', 'لا تخلي الرسالة تقف عندك',
        'اذا حذفت', 'ابتزاز', 'فك السحر', 'علاج روحاني',
        'شيخ معالج', 'رقية', 'فتح النصيب', 'جلب الحبيب',
    ]

    # 3. كلمات المحتوى الديني الشرعي (Legitimate)
    legit_keywords = [
        'قال الله تعالى', 'قال رسول الله', 'صلى الله عليه وسلم',
        'حديث', 'تفسير', 'فتوى', 'خطبة الجمعة', 'درس ديني',
        'صيام', 'زكاة الفطر', 'حكم شرعي', 'اذكار', 'دعاء',
        'القران الكريم', 'سورة', 'بسم الله الرحمن الرحيم',
        'صلاة', 'رمضان', 'عيد الفطر', 'عيد الاضحى', 'الحج',
        'العمرة', 'مكة', 'المدينة', 'المسجد الحرام', 'المسجد النبوي',
        'تلاوة', 'قارئ', 'شيخ', 'عالم', 'فقه', 'اصول الفقه',
        'سنة نبوية', 'هدي النبي', 'بر الوالدين', 'صلة الرحم',
        'التوبة', 'الاستغفار', 'الصبر', 'التوكل', 'الاخلاص',
    ]

    logging.info(f"بدء فحص الملف الضخم: {input_file}")
    logging.info(f"كلمات الاحتيال: {len(scam_keywords)} | المشبوه: {len(suspicious_keywords)} | الشرعي: {len(legit_keywords)}")

    chunk_size = 200_000
    df_iterator = pd.read_csv(input_file, chunksize=chunk_size,
                              encoding='utf-8', on_bad_lines='skip',
                              engine='python', quoting=3)

    total_processed = 0
    saved_scam = 0
    saved_suspicious = 0
    saved_legit = 0
    start_time = time.time()

    # حدود الاستخراج لكل فئة
    MAX_SCAM = 500_000
    MAX_SUSPICIOUS = 300_000
    MAX_LEGIT = 1_200_000

    first_scam = True
    first_suspicious = True
    first_legit = True

    try:
        for i, chunk in enumerate(df_iterator):
            total_processed += len(chunk)

            # التحقق من الحدود
            if saved_scam >= MAX_SCAM and saved_suspicious >= MAX_SUSPICIOUS and saved_legit >= MAX_LEGIT:
                logging.info("تم الوصول إلى الحد الأقصى لجميع الفئات!")
                break

            # البحث عن عمود النص
            if 'text' not in chunk.columns:
                text_col = None
                for col in chunk.columns:
                    if 'text' in col.lower() or 'tweet' in col.lower():
                        text_col = col
                        break
                if not text_col:
                    continue
            else:
                text_col = 'text'

            chunk[text_col] = chunk[text_col].astype(str)

            # === استخراج تغريدات الاحتيال ===
            if saved_scam < MAX_SCAM:
                scam_mask = chunk[text_col].apply(lambda x: contains_any(x, scam_keywords))
                scam_tweets = chunk[scam_mask]
                if not scam_tweets.empty:
                    remaining = MAX_SCAM - saved_scam
                    scam_tweets = scam_tweets.head(remaining)
                    saved_scam += len(scam_tweets)
                    scam_tweets.to_csv(output_scam, mode='a', header=first_scam, index=False, encoding='utf-8-sig')
                    first_scam = False

            # === استخراج تغريدات مشبوهة ===
            if saved_suspicious < MAX_SUSPICIOUS:
                susp_mask = chunk[text_col].apply(lambda x: contains_any(x, suspicious_keywords) and not contains_any(x, scam_keywords))
                susp_tweets = chunk[susp_mask]
                if not susp_tweets.empty:
                    remaining = MAX_SUSPICIOUS - saved_suspicious
                    susp_tweets = susp_tweets.head(remaining)
                    saved_suspicious += len(susp_tweets)
                    susp_tweets.to_csv(output_suspicious, mode='a', header=first_suspicious, index=False, encoding='utf-8-sig')
                    first_suspicious = False

            # === استخراج تغريدات دينية شرعية ===
            if saved_legit < MAX_LEGIT:
                legit_mask = chunk[text_col].apply(
                    lambda x: contains_any(x, legit_keywords) and not contains_any(x, scam_keywords) and not contains_any(x, suspicious_keywords)
                )
                legit_tweets = chunk[legit_mask]
                if not legit_tweets.empty:
                    remaining = MAX_LEGIT - saved_legit
                    legit_tweets = legit_tweets.head(remaining)
                    saved_legit += len(legit_tweets)
                    legit_tweets.to_csv(output_legit, mode='a', header=first_legit, index=False, encoding='utf-8-sig')
                    first_legit = False

            # تقرير التقدم كل 5 دفعات
            if (i + 1) % 5 == 0:
                elapsed = (time.time() - start_time) / 60
                logging.info(
                    f"الدفعة {i+1} | تم فحص: {total_processed:,} | "
                    f"احتيال: {saved_scam:,} | مشبوه: {saved_suspicious:,} | شرعي: {saved_legit:,} | "
                    f"الوقت: {elapsed:.1f} دقيقة"
                )

    except Exception as e:
        logging.error(f"حدث خطأ أثناء فحص الدفعات: {e}")

    end_time = time.time()
    elapsed_time = (end_time - start_time) / 60

    logging.info("=" * 60)
    logging.info("انتهت عملية الاستخراج الكبير!")
    logging.info(f"المدة المستغرقة: {elapsed_time:.2f} دقيقة")
    logging.info(f"إجمالي الأسطر المفحوصة: {total_processed:,}")
    logging.info(f"تغريدات احتيال: {saved_scam:,}")
    logging.info(f"تغريدات مشبوهة: {saved_suspicious:,}")
    logging.info(f"تغريدات شرعية: {saved_legit:,}")
    logging.info(f"المجموع الكلي: {saved_scam + saved_suspicious + saved_legit:,}")
    logging.info("=" * 60)

if __name__ == "__main__":
    main()
