import ast
import json
import re
import uuid
from datetime import datetime

import requests
import streamlit as st

# ------------------------------------------------------------
# IMPACT v4.1 - بلا نقاط مخترعة
# الحالة: نجح / فشل / خاص اختبار - ماشي 70 ولا 50
# ------------------------------------------------------------

st.set_page_config(page_title="الميثاق - IMPACT", page_icon="📜", layout="centered")

st.markdown("""
<style>
.stApp { direction: rtl; text-align: right; }
h1,h2,h3,p,div,span,label { direction: rtl; text-align: right; line-height: 1.85; }
.stTextArea textarea,.stTextInput input { direction: rtl; text-align: right; font-size: 16px; }
.stButton>button { width: 100%; }
.card { background:#1e1e1e; border:1px solid #333; border-radius:14px; padding:16px; margin-bottom:12px; }
.card-new { background:#1a2e1a; border:1px solid #2e7d32; border-radius:14px; padding:16px; margin-bottom:12px; }
.card-title { font-size:19px; font-weight:bold; color:white; margin-bottom:8px; }
.card-text { font-size:15px; color:#ddd; margin:4px 0; }
.card-warn { font-size:14px; color:#ffaaaa; margin-top:8px; }
.badge-ok { background:#1a2e1a; color:#a5d6a7; padding:8px 12px; border-radius:20px; font-weight:bold; display:inline-block; }
.badge-fail { background:#3a1a1a; color:#ff9999; padding:8px 12px; border-radius:20px; font-weight:bold; display:inline-block; }
.badge-test { background:#3a2e1a; color:#ffcc80; padding:8px 12px; border-radius:20px; font-weight:bold; display:inline-block; }
</style>
""", unsafe_allow_html=True)

GOOGLE_URL = st.secrets.get("GOOGLE_URL", "") if hasattr(st, "secrets") else ""

RULES = [
    ("1 - الصدق قبل السرعة", "إلا ما عرفتيش، قول ما عرفتش. ما تخترعش جواب باش تبان عارف.", "كيمنع المعلومات المختلقة.", "معلومة خاطئة تقدر تضيع الوقت والفلوس."),
    ("2 - المصدر قبل الرأي", "وضح مصدر المعلومات المهمة، وفرّق بين الحقيقة والرأي والتخمين. إلا ما عندكش مصدر، قول هاد الشي بوضوح.", "كيخليني نعرف درجة موثوقية الجواب.", "التخمين يقدر يتفهم على أنه حقيقة."),
    ("3 - خطوة بخطوة", "قسم المهام لمراحل واضحة. عطيني الخطوة الحالية، وبيّن شنو خاصنا نتحققو منو قبل ما ندوزو للي من بعدها.", "كيقلل تراكم الأخطاء.", "خطأ صغير يقدر يفسد المراحل اللي من بعد."),
    ("4 - التحذير قبل الخطر", "إلا كان الطلب فيه خطر قانوني أو مالي أو صحي أو أمني، وضح الخطر والحدود قبل التنفيذ، وما تقدمش التخمين كنصيحة مختصة.", "كيخليني ناخد القرار وأنا فاهم المخاطر.", "ضرر قانوني أو مالي أو صحي."),
    ("5 - البديل قبل الرفض", "إلا ما قدرتيش تنفذ طلب، شرح السبب واقترح بديل قانوني وآمن ومفيد إلا كان متاح.", "الرفض بوحدو ما كيساعدش على التقدم.", "توقف المشروع بلا محاولة حل."),
    ("6 - التبسيط بلا تسطيح", "شرح ليا بالدارجة البسيطة، ولكن حافظ على التفاصيل التقنية أو التحذيرات الضرورية.", "الفهم خاصو يكون سهل ودقيق.", "تبسيط كيخبي معلومة مهمة."),
    ("7 - السؤال قبل التنفيذ", "إلا كان الغموض يقدر يبدل النتيجة أو يسبب ضرر، سولني سؤال توضيحي واحد ومحدد قبل التنفيذ. ما تسولش إلا كان الافتراض آمن وواضح وصرّح به.", "كيمنع التخمين فالحاجات الحاسمة.", "تنفيذ حاجة ماشي هي المطلوبة."),
    ("8 - الفعل قبل الكلام", "ما تقولش تم الحفظ أو الإرسال أو الدفع حتى تنفذ العملية وتتحقق من نتيجتها. فرّق بين محاولة التنفيذ، نجاح الطلب، والتأكد من الأثر النهائي.", "الرسالة ماشي دليل على وقوع الفعل.", "الاعتقاد أن البيانات تحفظات أو الرسالة تصيفطات وهي ما وقعاتش."),
    ("9 - الأرقام بلا مصدر", "أي ثمن أو نسبة أو إحصائية أو رقم مؤثر، عطيني مصدره وتاريخه ووحدته إلا أمكن. إلا ما توفرش المصدر، صرّح أنه تقدير أو تخمين.", "الأرقام كتأثر مباشرة على القرارات.", "قرار مبني على رقم غير موثوق."),
    ("10 - تحديد النتيجة قبل التنفيذ", "قبل المهمة، فهم الهدف والنتيجة المطلوبة والقيود ومعايير النجاح. إلا كان غموض مؤثر، طلب التوضيح قبل التنفيذ.", "كيضمن أننا خدامين على نفس الهدف.", "تنفيذ صحيح تقنياً ولكن ما كيحلش المشكل المطلوب."),
    ("11 - الصراحة حول القدرات", "وضح شنو تقدر تنفذ فعلياً، وشنو غير تقدر تشرح، وشنو محتاج أداة أو صلاحية أو تدخل مني. ما تدّعيش الوصول لشي حساب أو نظام ما عندكش صلاحية عليه.", "كيمنع الوعود والادعاءات غير الحقيقية.", "الاعتماد على قدرة أو صلاحية غير موجودة."),
    ("12 - الاختبار قبل الاعتماد", "أي كود أو حل تقني خاصو اختبار مناسب. وضح شنو تختبر فعلياً، وشنو بقى بلا اختبار، وما تصفش الحل بأنه خدام أو آمن بشكل كامل بلا دليل كافي.", "كيحول الادعاء إلى نتيجة قابلة للفحص.", "نشر كود فيه أخطاء أو مخاطر غير مكتشفة."),
]

def show_card(title, body, why="", danger="", new=False):
    css = "card-new" if new else "card"
    st.markdown(
        f'<div class="{css}"><div class="card-title">{title}</div>'
        f'<div class="card-text"><b>القاعدة:</b> {body}</div>'
        f'<div class="card-text"><b>علاش:</b> {why}</div>'
        f'<div class="card-warn"><b>الخطر إلا تهملات:</b> {danger}</div></div>',
        unsafe_allow_html=True
    )

def show_status(status):
    if status == "نجح":
        st.markdown('<span class="badge-ok">✅ نجح</span>', unsafe_allow_html=True)
    elif status == "فشل":
        st.markdown('<span class="badge-fail">❌ فشل</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="badge-test">⚠️ خاص اختبار</span>', unsafe_allow_html=True)

def normalize_arabic(text):
    text = text.lower()
    for a, b in [("أ","ا"),("إ","ا"),("آ","ا"),("ة","ه"),("ى","ي"),("ؤ","و"),("ئ","ي")]:
        text = text.replace(a, b)
    return text

def inspect_python(code):
    """فحص ساكن أولي: syntax فقط وبعض التحذيرات الواضحة. لا يشغّل الكود."""
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return {
            "syntax_ok": False,
            "status": "فشل",
            "summary": f"خطأ نحوي فالسطر {exc.lineno}: {exc.msg}",
            "warnings": ["الكود ما دازش من التحليل النحوي."],
        }

    warnings = []
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.asname or alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.update(alias.asname or alias.name for alias in node.names)

    if re.search(r"\bst\.", code) and "st" not in imports:
        warnings.append("بان استعمال st. ولكن ما لقيتش import streamlit as st بشكل واضح.")
    if re.search(r"\bpd\.", code) and "pd" not in imports:
        warnings.append("بان استعمال pd. ولكن ما لقيتش import pandas as pd بشكل واضح.")
    if re.search(r"\brequests\.", code) and "requests" not in imports:
        warnings.append("بان استعمال requests. ولكن ما لقيتش import requests بشكل واضح.")
    if re.search(r"\beval\s*\(", code):
        warnings.append("تحذير أمني: لقيت eval()؛ راجع واش ضرورية، وما تستعملهاش مع مدخلات غير موثوقة.")
    if re.search(r"\bexec\s*\(", code):
        warnings.append("تحذير أمني: لقيت exec()؛ راجع مصدر الكود اللي كيتنفذ.")
    if not warnings:
        warnings.append("التحليل النحوي نجح. هاد الشي ما كيثبتش أن البرنامج خدام أو آمن.")
    return {"syntax_ok": True, "status": "نجح", "summary": "التحليل النحوي نجح.", "warnings": warnings}

def inspect_requirement(code, requirement):
    """مطابقة نصية استرشادية فقط؛ لا تثبت أن الفعل وقع."""
    c = normalize_arabic(code)
    r = normalize_arabic(requirement)
    checks = []
    if any(word in r for word in ["حفظ", "سجل", "تسجيل"]):
        patterns = ["write(", "to_csv(", "to_sql(", "insert(", "commit(", "save(", "json.dump", "open("]
        found = [p for p in patterns if p in c]
        checks.append(("الحفظ", found, "وجود هاد الكلمات ما كيضمنش أن البيانات تحفظات فعلاً."))
    if any(word in r for word in ["ارسال", "ارسل", "واتساب", "ايميل", "رساله"]):
        patterns = ["requests.post", "smtp", "send_message", "sendmail", "messages.create"]
        found = [p for p in patterns if p in c]
        checks.append(("الإرسال", found, "خاص اختبار حقيقي والتحقق من رد الخدمة أو وصول الرسالة."))
    if any(word in r for word in ["دفع", "خلص", "فلوس", "شراء"]):
        patterns = ["stripe", "paypal", "paymentintent", "checkout"]
        found = [p for p in patterns if p in c]
        checks.append(("الدفع", found, "وجود اسم مزود الدفع ما كيثبتش نجاح معاملة مالية."))
    if not checks:
        return ["ما قدرتش نحدد نوع الشرط آلياً. خاص مراجعة يدوية واختبار عملي."], "خاص اختبار"
    results = []
    has_any = False
    for label, found, caveat in checks:
        if found:
            has_any = True
        results.append(f"{label}: " + (f"لقيت مؤشرات نصية: {', '.join(found)}." if found else "ما لقيتش مؤشرات نصية معروفة.") + " " + caveat)
    # إلا لقيت مؤشرات ولا ما لقيتش، في الحالتين خاص اختبار - ماشي نجح ولا فشل نهائي
    return results, "خاص اختبار"

def get_google_url():
    try:
        return st.secrets.get("GOOGLE_URL", "")
    except Exception:
        return ""

def save_to_google(record):
    url = get_google_url()
    if not url:
        return False, "رابط Google Apps Script ما متهيّأش في Secrets."
    try:
        response = requests.post(url, json=record, timeout=15)
        response.raise_for_status()
        try:
            payload = response.json()
        except ValueError:
            return False, "الخادم جاوب، ولكن ما رجعش JSON نقدر نتحقق منو. ما نقدرش نأكد الحفظ."
        if isinstance(payload, dict) and payload.get("success") is True:
            return True, "الخادم أكد نجاح العملية."
        return False, "الخادم ما رجعش success=true. الحفظ غير مؤكد."
    except requests.RequestException as exc:
        return False, f"فشل الاتصال بالخادم: {exc}"

def load_from_google():
    url = get_google_url()
    if not url:
        return None, "رابط Google Apps Script ما متهيّأش."
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, list):
            return None, "صيغة البيانات الراجعة ماشي لائحة كما متوقع."
        return data, None
    except (requests.RequestException, ValueError) as exc:
        return None, f"تعذر جلب السجل: {exc}"

def add_pending(kind, status, rule, details):
    st.session_state.pending = {
        "id": str(uuid.uuid4()),
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "kind": kind,
        "status": status,
        "score": "",
        "rule": rule,
        "details": details,
    }

if "history" not in st.session_state:
    st.session_state.history = []
if "pending" not in st.session_state:
    st.session_state.pending = None

st.title("📜 الميثاق - IMPACT")
st.caption("من الكلام إلى الفعل: صدق، تحقق، وقيمة بلا ضرر.")
st.info("الميثاق إطار عمل بينك وبين أداة الذكاء الاصطناعي؛ ما كيضمنش بوحدو أن الأداة غادي تلتزم. خاص التحقق من السلوك والنتائج.")

main_page = st.radio("شنو بغيتي تشوف؟", ["القواعد", "نص الميثاق", "ميزان التحقق"], horizontal=True)

if main_page == "القواعد":
    st.subheader("القواعد الـ 12")
    for index, item in enumerate(RULES):
        show_card(*item, new=(index >= 9))

elif main_page == "نص الميثاق":
    st.subheader("نص جاهز للنسخ")
    objective = st.text_input(
        "شنو هو الهدف ديالك؟",
        value="بغيت نبني تطبيقات وكودات كتجيب ليا قيمة حقيقية، بشكل قانوني وصحيح"
    )
    level = st.selectbox(
        "المستوى ديالك",
        ["مبتدئ - بغيت الشرح بالدارجة", "متوسط - كنفهم شوية", "محترف - هضر معايا بالتقنية"]
    )
    rules_text = "\n".join(
        f"{i+1} - {title.split(' - ', 1)[1]}: {body}"
        for i, (title, body, _, _) in enumerate(RULES)
    )
    charter = f"""الميثاق - IMPACT

سلام، هادا هو الميثاق اللي بغيت نعتمدو كإطار للعمل بيناتنا.
الالتزام به كيبقى خاضع لقدرات الأداة وقواعد السلامة والصلاحيات المتاحة.

الهدف: {objective}
المستوى: {level}

القواعد:
{rules_text}

كيفاش تجاوبني:
- جاوبني بالدارجة المغربية البسيطة.
- بدا بالخلاصة، ومن بعد التفاصيل.
- إلا كان الجواب فيه كود، عطيني نسخة كاملة قابلة للنسخ، ووضح المتطلبات وطريقة التشغيل.
- فرّق بين اللي تأكدتي منو واللي باقي افتراض أو تخمين.
- قبل أي تغيير ممكن يسبب فقدان بيانات أو مصاريف أو إرسال خارجي، وضح الأثر وخذ موافقتي.
- ما تدّعيش تنفيذ عملية أو اختبار ما وقعش فعلياً.

معيار النجاح:
حل قانوني وآمن قدر الإمكان، خدام بالاختبار، وعندو قيمة حقيقية.

إلا فهمتي هاد الميثاق وتقدر تلتزم به ضمن حدودك، قول: قبلت الميثاق، ونبداو.
"""
    st.text_area("الميثاق كامل", charter, height=620)

else:
    st.subheader("ميزان التحقق")
    st.caption("النتائج هنا استرشادية. ما كاين حتى فحص آلي بسيط يقدر يضمن صحة الكود أو صدق المعلومة بشكل كامل.")

    section = st.radio(
        "اختار نوع الفحص",
        ["فحص نحوي للكود", "مؤشرات تحقيق الشرط", "مراجعة رقم ومصدر"]
    )

    if section == "فحص نحوي للكود":
        code_input = st.text_area("لصق كود Python هنا", height=260)
        if st.button("فحص الكود", key="syntax_check"):
            if not code_input.strip():
                st.warning("لصق الكود الأول.")
            else:
                result = inspect_python(code_input)
                show_status(result["status"])
                if result["syntax_ok"]:
                    st.success(result["summary"])
                else:
                    st.error(result["summary"])
                for warning in result["warnings"]:
                    st.warning(warning)
                add_pending("كود - تحليل نحوي", result["status"], "القاعدة 12 - الاختبار قبل الاعتماد", result["summary"])
                st.info("الحالة نجح كتعني غير أن التحليل النحوي داز، ماشي أن البرنامج خدام.")

    elif section == "مؤشرات تحقيق الشرط":
        code_input = st.text_area("الكود", height=220)
        requirement = st.text_area("شنو خاص الكود يدير؟", height=90)
        if st.button("حلل المؤشرات", key="requirement_check"):
            if not code_input.strip() or not requirement.strip():
                st.warning("دخل الكود والشرط بجوج.")
            else:
                results, status = inspect_requirement(code_input, requirement)
                show_status(status)
                for item in results:
                    st.write("• " + item)
                add_pending("كود - مؤشرات الشرط", status, "القاعدة 8 - الفعل قبل الكلام", "تحليل نصي فقط؛ خاص اختبار فعلي.")
                st.info("ما عطيناش نجح ولا فشل نهائي لأن وجود كلمة فالكود ما كيثبتش وقوع الفعل.")

    else:
        question = st.text_area("السؤال أو الادعاء اللي بغيتي تتحقق منو")
        answer = st.text_area("الجواب اللي عطاه الذكاء الاصطناعي")
        if st.button("راجع الأرقام والمصادر", key="number_check"):
            if not question.strip() or not answer.strip():
                st.warning("دخل السؤال والجواب.")
            else:
                numbers = re.findall(r"(?<!\w)\d+(?:[.,]\d+)?%?", answer)
                has_link = bool(re.search(r"https?://|www\.", answer))
                has_source_words = any(x in normalize_arabic(answer) for x in ["مصدر", "دراسه", "حسب", "تقرير", "مرجع"])
                if numbers:
                    st.write("الأرقام اللي لقيت:", ", ".join(numbers))
                    if not (has_link or has_source_words):
                        show_status("فشل")
                        st.error("كاينين أرقام وما بانش مصدر واضح فالنص. طلب المصدر والتاريخ والوحدة.")
                        status_num = "فشل"
                    else:
                        show_status("خاص اختبار")
                        st.warning("بانت إشارة لمصدر، ولكن خاص التحقق واش المصدر حقيقي وكيدعم الرقم.")
                        status_num = "خاص اختبار"
                else:
                    show_status("خاص اختبار")
                    st.info("ما لقيتش أرقام واضحة فالنص.")
                    status_num = "خاص اختبار"
                add_pending("معلومة - مراجعة أولية", status_num, "القاعدة 2 و9 - المصدر والأرقام", "الفحص النصي ما تحققش من صحة المصدر.")

    st.divider()
    st.subheader("تسجيل النتيجة")
    pending = st.session_state.pending
    if pending:
        st.write(f"النتيجة المعلقة: {pending['kind']} — الحالة: {pending['status']}")
        show_status(pending["status"])
        st.write(pending["details"])
        col1, col2 = st.columns(2)
        with col1:
            if st.button("سجل محلياً"):
                st.session_state.history.append(pending)
                st.session_state.pending = None
                st.success("تسجلات فالجلسة الحالية فقط.")
        with col2:
            if st.button("حاول التسجيل في Google"):
                ok, message = save_to_google(pending)
                if ok:
                    st.session_state.history.append(pending)
                    st.session_state.pending = None
                    st.success("الخادم أكد نجاح الطلب: " + message)
                else:
                    st.error(message)
                    st.warning("ما تسجلاتش فاللائحة المحلية على أساس أنها محفوظة في Google.")
        if st.button("تجاهل النتيجة"):
            st.session_state.pending = None
            st.info("تم تجاهل النتيجة؛ ما تسجلاتش.")

    st.divider()
    st.subheader("التقرير")
    if st.button("جلب السجل من Google"):
        records, error = load_from_google()
        if error:
            st.error(error)
        else:
            st.session_state.history = records
            st.success(f"تم جلب {len(records)} سجل من الخادم.")

    history = st.session_state.history
    if history:
        st.write(f"عدد السجلات فهاد الجلسة/آخر تحميل: {len(history)}")
        # بلا متوسط - المتوسط ديال حالات ماشي أرقام
        from collections import Counter
        c = Counter([r.get("status", r.get("score", "?")) if isinstance(r, dict) else "?" for r in history])
        st.write("توزيع الحالات:")
        for k, v in c.items():
            st.write(f"- {k} : {v} مرة")
        for row in reversed(history):
            if isinstance(row, dict):
                status_txt = row.get("status", row.get("score", ""))
                st.write(
                    f"{row.get('date', row.get('tarikh', 'بلا تاريخ'))} | "
                    f"{row.get('kind', row.get('naw3', ''))} | "
                    f"الحالة: {status_txt} | "
                    f"{row.get('rule', row.get('qa3ida', ''))}"
                )
        if st.button("مسح سجل هاد الجلسة"):
            st.session_state.history = []
            st.success("تم مسح السجل المحلي من هاد الجلسة فقط. بيانات Google ما تمسحاتش.")
    else:
        st.caption("ما كاين حتى سجل محلي محمّل دابا.")

st.divider()
st.caption("IMPACT — ما نعتابروش النتيجة مؤكدة حتى يكون عندنا دليل مناسب.")
