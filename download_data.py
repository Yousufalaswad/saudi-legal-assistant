from datasets import load_dataset
import json
import os

os.makedirs("data/datasets", exist_ok=True)

print("Downloading Arabic Legal Judgment dataset...")
try:
    dataset = load_dataset("mbayan/Arabic-LJP", trust_remote_code=True)
    
    cases = []
    for split in dataset:
        for item in dataset[split]:
            text = ""
            for key, value in item.items():
                if isinstance(value, str) and value.strip():
                    text += f"{key}: {value}\n"
            if text.strip():
                cases.append(text.strip())
    
    output_path = "data/datasets/arabic_legal_cases.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(cases, f, ensure_ascii=False, indent=2)
    
    print(f"Saved {len(cases)} cases to {output_path}")

except Exception as e:
    print(f"Dataset download failed: {e}")
    print("Creating sample dataset instead...")
    
    sample_cases = [
        "نوع القضية: نزاع عمالي\nالموضوع: مطالبة بصرف مكافأة نهاية الخدمة\nالحكم: يحق للموظف الحصول على مكافأة نهاية الخدمة بعد سنتين من العمل المتواصل وفقاً للمادة 84 من نظام العمل",
        "نوع القضية: نزاع إيجاري\nالموضوع: طرد المستأجر بدون إشعار مسبق\nالحكم: يجب على المالك إعطاء إشعار مدته 90 يوماً قبل إخلاء العقار وفقاً لنظام الإيجار",
        "Case type: Labor dispute\nSubject: Unpaid wages claim\nRuling: Employee entitled to full wages for work performed. Employer must pay within 7 days of resignation per Article 90 of Saudi Labor Law",
        "Case type: Rental dispute\nSubject: Security deposit refusal\nRuling: Landlord must return deposit within 30 days unless documented damages exist per tenancy regulations",
        "نوع القضية: مخالفة مرورية\nالموضوع: الاعتراض على مخالفة سرعة\nالحكم: يحق للسائق الاعتراض خلال 30 يوماً من تاريخ المخالفة عبر منصة أبشر",
        "Case type: Traffic violation\nSubject: Speed camera fine dispute\nRuling: Driver has 30 days to dispute via Absher platform. Fine waived if camera malfunction proven",
        "نوع القضية: نزاع عمالي\nالموضوع: حساب مكافأة نهاية الخدمة\nالحكم: تحسب المكافأة بواقع أجر نصف شهر عن كل سنة من السنوات الخمس الأولى وأجر شهر عن كل سنة بعد ذلك",
        "Case type: Enforcement court\nSubject: Bounced cheque collection\nRuling: Creditor can file directly via Nafith platform. Debtor has 5 days to pay before enforcement measures including travel ban",
    ]
    
    with open("data/datasets/arabic_legal_cases.json", "w", encoding="utf-8") as f:
        json.dump(sample_cases, f, ensure_ascii=False, indent=2)
    
    print(f"Created sample dataset with {len(sample_cases)} cases")

print("Done!")