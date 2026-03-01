import pandas as pd
import random
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


scam_templates = [
    "يا أهل الخير والإحسان، {victim_status} يحتاج إلى {medical_need} سريعة قبل فوات الأوان. تبرعوا لوجه الله على الحساب: {account_num}. الدال على الخير كفاعله.",
    "{urgency_phrase}! {victim_status} لا يجد قوت يومه. ساهموا معنا في تفريج كربته. {religious_promise}. للتبرع المرجو التحويل إلى {account_num}.",
    "مشروع بناء مسجد في {location} بحاجة ماسة لدعمكم. {religious_promise}. اغتنم الأجر وساهم عبر {account_num}.",
    "{urgency_phrase}، عائلة مهددة بالطرد بسبب الديون. من ينقذهم {religious_promise}؟ رقم الحساب البنكي للتبرع: {account_num}.",
    "كفالة أيتام في {location} تنتظركم. بادروا بالخير وساهموا ولو بالقليل عبر {account_num}. {religious_promise}.",
    "حالة إنسانية حرجة! {victim_status} يعاني من مرض عضال. نناشد أهل القلوب الرحيمة. التبرع المباشر على {account_num}.",
    "رسالة من أختكم في الله، أحتاج مساعدة مالية عاجلة {medical_need}. {religious_promise}. هذا رقمي وحسابي {account_num}.",
    "{urgency_phrase}. ساهم في حفر بئر في {location}. {religious_promise}. تكلفة المساهمة 100 ريال فقط على {account_num}.",
    "من يفرج عني كربتي {religious_promise}؟ أنا {victim_status} وعليّ ديون ثقيلة. أرجوكم ساعدوني عبر {account_num}.",
    "حملة تبرعات عاجلة لإنقاذ {victim_status}. {religious_promise}. لا تبخلوا بصدقاتكم، أرسل المال الآن على {account_num}."
]

victim_statuses = ["أرملة رزقها مقطوع", "شاب مريض", "أب لعائلة كبيرة", "يتيم", "مريض بالسرطان", "طالب علم محتاج", "امرأة مسنة", "أسرة فقيرة"]
medical_needs = ["عملية جراحية", "شراء دواء غالي", "غسيل كلى", "تكاليف مستشفى", "علاج مكلف"]
account_nums = ["SA12345678901234567890", "0123456789", "+966500000000", "STC Pay 0555555555", "حساب الراجحي 12345"]
religious_promises = ["يجعلها الله في ميزان حسناتكم", "والله يضاعف لمن يشاء", "من فرج عن مؤمن فرج الله عنه", "صدقة جارية لك ولوالديك", "يبارك الله في رزقك", "وقانا الله وإياكم شر الأمراض", "أجرك على الله"]
urgency_phrases = ["عاجل جداً", "أنقذوا حياة", "نداء استغاثة", "يا باغي الخير أقبل", "لله يا محسنين"]
locations = ["دولة فقيرة", "قرية نائية", "إفريقيا", "منطقة محتاجة"]

def generate_scam_samples(n=1000):
    samples = []
    for _ in range(n):
        template = random.choice(scam_templates)
        text = template.format(
            victim_status=random.choice(victim_statuses),
            medical_need=random.choice(medical_needs),
            account_num=random.choice(account_nums),
            religious_promise=random.choice(religious_promises),
            urgency_phrase=random.choice(urgency_phrases),
            location=random.choice(locations)
        )
        samples.append({"text": text, "label": "Explicit Religious Scam", "source": "Synthetic Generator"})
    return samples


legit_templates = [
    "من هدي النبي ﷺ في التعامل مع الجار الإحسان إليه وعدم إيذائه. وهذا من كمال الإيمان.",
    "فتاوى: هل يجوز إخراج زكاة الفطر نقداً؟ اختلف العلماء في ذلك، والراجح عند طائفة جوازه للحاجة.",
    "الصدقة تطفئ غضب الرب. احرصوا على الصدقة الخفية فهي أبلغ في الإخلاص وأقرب للقبول.",
    "ملخص خطبة الجمعة اليوم: بر الوالدين هو طريقك إلى الجنة، فلا تغفل عن رضاهما.",
    "القرآن الكريم شفاء لما في الصدور، فاجعل لك ورداً يومياً لا تتركه مهما شغلتك الدنيا.",
    "تذكير بصيام الأيام البيض للشهر الهجري الحالي، نسأل الله أن يتقبل منا ومنكم صالح الأعمال.",
    "حكم من حلف على يمين ثم رأى غيرها خيراً منها: يُكفّر عن يمينه ويفعل الذي هو خير.",
    "الدعاء سلاح المؤمن، فلا تبخل على نفسك وإخوانك بالدعاء في ظهر الغيب.",
    "أعلن مركز الملك سلمان للإغاثة عن وصول طائرات المساعدات الإنسانية إلى المتضررين في المنطقة.",
    "تفسير قوله تعالى (إن مع العسر يسراً): فيها بشارة عظيمة بأن الفرج قريب بعد الضيق."
]

def generate_legit_samples(n=1000):
    samples = []
    for _ in range(n):
        text = random.choice(legit_templates)
        # Adding slight variations
        if random.random() > 0.5:
             text = text + " " + random.choice(["والله أعلم.", "نسأل الله الهداية.", "تقبل الله.", "جزاكم الله خيرا."])
        samples.append({"text": text, "label": "Legitimate Religious Post", "source": "Synthetic Generator"})
    return samples


suspicious_templates = [
    "إذا نشرت هذه الرسالة لعشرة أشخاص ستسمع خبراً سعيداً غداً، وإذا تجاهلتها سيصيبك مكروه!",
    "هل تحب الله ورسوله؟ إذن لا تتجاهل هذا المنشور واكتب 'يا رب' وشاركه في 5 مجموعات.",
    "أقسم بالله العظيم أنني رأيت النبي في المنام وقال لي من ينشر هذه الرسالة يُرزق بمال وفير.",
    "صورة لاسم الله مكتوبة في السحاب! سبحان الله، لا تخرج قبل أن تكتب سبحان الله.",
    "هذا الدعاء معجزة، من قاله 100 مرة اليوم ستحل جميع مشاكله المالية فورا."
]

def generate_suspicious_samples(n=500):
   samples = []
   for _ in range(n):
       text = random.choice(suspicious_templates)
       samples.append({"text": text, "label": "Suspicious Religious Manipulation", "source": "Synthetic Generator"})
   return samples


def main():
    logging.info("Starting data generation for Scam Religious Corpus...")
    
    
    scam_data = generate_scam_samples(400000)
    legit_data = generate_legit_samples(400000)
    suspicious_data = generate_suspicious_samples(200000)
    
    all_data = scam_data + legit_data + suspicious_data
    random.shuffle(all_data) 
    
    df = pd.DataFrame(all_data)
    
    # Save the dataset
    output_dir = os.path.join("data", "raw")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "scam_religious_corpus_v1.csv")
    
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    logging.info(f"Successfully generated {len(df)} samples and saved to {output_path}")
    
    # Print label distribution
    logging.info("\nLabel Distribution:")
    logging.info(df['label'].value_counts())

if __name__ == "__main__":
    main()
