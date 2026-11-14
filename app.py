import ast
import hashlib
import re
import uuid
from datetime import datetime

import requests
import streamlit as st

st.set_page_config(page_title="الميثاق التنفيذي - IMPACT", page_icon="📜", layout="centered")

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
    ("13 - السياق قبل التنفيذ", "اعتمد على السياق العام والمشاريع السابقة ديالي بلا ما تفرض عليا نعاود نفس المعلومات، ولكن ديما عطيني الأولوية لطلبي الحالي إلى تعارض مع القديم.", "كيخلي الأداة ذكية وكتفهمك على الطاير بلا تكرار.", "تضييع الوقت فإعادة شرح الأساسيات أو التمسك بمعلومات قديمة."),
    ("14 - التفكير النقدي وتحدي الافتراضات", "ما توافقنيش غير باش ترضيني. إلا شفتي الفكرة ديالي ناقصة، فيها ثغرة، أو كاين مسار أذكى وأرخص، صارحني بها ووريني زاوية النظر اللي ما شفتهاش.", "الذكاء الحقيقي هو تصحيح المسار ماشي التصفيق للخطأ.", "الوقوع ففخ المجاملة وبناء مشاريع على أساس هش."),
    ("15 - الكفاءة وأقل جهد ممكن", "ديما قلب ليا على أقصر وأبسط طريق كيعطي 80% من النتيجة بـ 20% من الجهد. ما تعقدش الحلول التقنية إلا ما كانش التعقيد ضروري.", "البساطة هي قمة الذكاء الهندسي وكتوفر الوقت والموارد.", "الغرق فالهندسة الزائدة وكود معقد صعيب فالتطوير."),
    ("16 - التعلم والذاكرة التراكمية", "ملي يوقع خطأ فالكود أو الفهم ونصلحوه، لخّص ليا الدرس المستفاد فسطر واحد باش ما نطيحوش فنفس الحفرة مرة أخرى.", "كيحول كل فشل لرصيد معرفي كيزيد يطور جودة العمل.", "الدوران فحلقة مفرغة وتكرار نفس الأخطاء التقنية."),
    ("17 - التوقّع الاستباقي للخطوة الجاية", "ملي تكمل المهمة الحالية، ما توقفش. اقترح عليا بذكاء شنو هي العقبة أو الخطوة المنطقية اللي غادي تواجهني من بعد، وعطيني مفتاحها.", "كينقل الأداة من منفّذ أورام لشريك استراتيجي كيشوف لقدام.", "التقدم ببطء شديد لأنك ديما خاصك تفكر فكل خطوة بوحدك."),
]

def show_card(title, body, why="", danger="", new=False):
    css = "card-new" if new else "card"
    st.markdown(f'<div class="{css}"><div class="card-title">{title}</div><div class="card-text"><b>القاعدة:</b> {body}</div><div class="card-text"><b>علاش:</b> {why}</div><div class="card-warn"><b>الخطر إلا تهملات:</b> {danger}</div></div>', unsafe_allow_html=True)

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

def fingerprint(rec):
    date_only = str(rec.get('date',''))[:10]
    key = f"{date_only}|{rec.get('kind','')}|{rec.get('status','')}|{rec.get('rule','')}|{rec.get('details','')}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()

def is_duplicate(rec, history):
    fp = fingerprint(rec)
    for h in history:
        if isinstance(h, dict) and fingerprint(h) == fp:
            return True
    return False

def dedupe_history(history):
    seen = set()
    out = []
    removed = 0
    for h in history:
        if not isinstance(h, dict):
            continue
        fp = fingerprint(h)
        if fp in seen:
            removed += 1
            continue
        seen.add(fp)
        out.append(h)
    return out, removed

def _is_secret_name(name):
    name = str(name).lower()
    return any(sec in name for sec in ["key", "password", "secret", "token", "auth"])

def _is_secret_value(node):
    return isinstance(node, ast.Constant) and isinstance(node.value, str) and len(node.value) > 5

def inspect_python_advanced(code):
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return {"syntax_ok": False, "status": "فشل", "summary": f"خطأ نحوي فالسطر {exc.lineno}: {exc.msg}", "warnings": ["الكود ما دازش من التحليل النحوي."]}
    warnings = []
    imports = set()
    has_try_except = False
    hardcoded_secret_found = False
    empty_functions = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.asname or alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.update(alias.asname or alias.name for alias in node.names)
        elif isinstance(node, ast.Try):
            has_try_except = True
        elif isinstance(node, ast.FunctionDef):
            if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                empty_functions += 1
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and _is_secret_name(target.id) and _is_secret_value(node.value):
                    hardcoded_secret_found = True
                if isinstance(target, ast.Name) and isinstance(node.value, ast.Dict):
                    for k, v in zip(node.value.keys, node.value.values):
                        if isinstance(k, ast.Constant) and isinstance(k.value, str) and _is_secret_name(k.value) and _is_secret_value(v):
                            hardcoded_secret_found = True
        elif isinstance(node, ast.AnnAssign):
            if isinstance(node.target, ast.Name) and _is_secret_name(node.target.id) and node.value is not None and _is_secret_value(node.value):
                hardcoded_secret_found = True
        elif isinstance(node, ast.Dict):
            for k, v in zip(node.keys, node.values):
                if isinstance(k, ast.Constant) and isinstance(k.value, str) and _is_secret_name(k.value) and _is_secret_value(v):
                    hardcoded_secret_found = True
    if not imports:
        warnings.append("ملاحظة: ما كاين حتى import مسجل فالعقد البرمجية.")
    if hardcoded_secret_found:
        warnings.append("⚠️ خطر أمني محتمل: لقيت مفتاح سري أو كلمة مرور مكتوبة مباشرة داخل الكود (Hardcoded Secret).")
    if empty_functions > 0:
        warnings.append(f"تنبيه: لقيت {empty_functions} دالة فارغة فيها غير (pass) وما مكتوباش فيها اللوجيك ديالها.")
    if not has_try_except and ("requests." in code or "open(" in code):
        warnings.append("ملاحظة جودة: الكود فيه عمليات إدخال/إخراج أو طلبات شبكة بدون حماية (Try/Except).")
    if not warnings:
        warnings.append("التحليل الهيكلي متقدم: الكود نقي وما لقيتش ثغرات أو أخطاء بنيوية ظاهرة.")
    return {"syntax_ok": True, "status": "فشل" if hardcoded_secret_found else "نجح", "summary": "التحليل الهيكلي المتقدم تم بنجاح.", "warnings": warnings}

def inspect_requirement(code, requirement):
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
    for label, found, caveat in checks:
        results.append(f"{label}: " + (f"لقيت مؤشرات نصية: {', '.join(found)}." if found else "ما لقيتش مؤشرات نصية معروفة.") + " " + caveat)
    return results, "خاص اختبار"

# --- v6.2 NEW: زيدنا رابط Responses ---
def get_form_config():
    try:
        if not hasattr(st, "secrets"):
            return {"url": "", "date": "", "kind": "", "status": "", "rule": "", "details": "", "responses_url": ""}
        return {
            "url": st.secrets.get("GOOGLE_FORM_URL", ""),
            "date": st.secrets.get("ENTRY_DATE", ""),
            "kind": st.secrets.get("ENTRY_KIND", ""),
            "status": st.secrets.get("ENTRY_STATUS", ""),
            "rule": st.secrets.get("ENTRY_RULE", ""),
            "details": st.secrets.get("ENTRY_DETAILS", ""),
            "responses_url": st.secrets.get("GOOGLE_FORM_RESPONSES_URL", ""),
        }
    except Exception:
        return {"url": "", "date": "", "kind": "", "status": "", "rule": "", "details": "", "responses_url": ""}

def save_to_google_form(record):
    cfg = get_form_config()
    if not cfg["url"] or not cfg["date"]:
        return False, "إعدادات Google Form ما متهيّأش في Secrets."
    payload = {
        cfg["date"]: record.get("date", ""),
        cfg["kind"]: record.get("kind", ""),
        cfg["status"]: record.get("status", ""),
        cfg["rule"]: record.get("rule", ""),
        cfg["details"]: record.get("details", ""),
    }
    try:
        resp = requests.post(cfg["url"], data=payload, timeout=15)
        if resp.status_code in (200, 302):
            return True, "تم إرسال النتيجة لـ Google Form. تحقق منها في Responses."
        return False, f"Google Form جاوب بـ {resp.status_code}."
    except requests.RequestException as exc:
        return False, f"فشل الاتصال: {exc}"

def add_pending(kind, status, rule, details):
    st.session_state.pending = {"id": str(uuid.uuid4()), "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "kind": kind, "status": status, "rule": rule, "details": details}

if "history" not in st.session_state:
    st.session_state.history = []
if "pending" not in st.session_state:
    st.session_state.pending = None

st.title("📜 الميثاق التنفيذي - IMPACT")
st.caption("من الكلام إلى الفعل: الأمر التنفيذي السيادي للذكاء الاصطناعي.")
st.info("هاد التطبيق كيولد النص التنفيذي اللي كيجبر أي ذكاء اصطناعي يخدم تحت 17 قاعدة ملزمة، وكيتحقق من الكود ديالو قبل الاعتماد عليه.")

main_page = st.radio("شنو بغيتي تشوف؟", ["القواعد (17 قاعدة)", "نص الميثاق التنفيذي", "ميزان التحقق المتقدم"], horizontal=True)

if main_page == "القواعد (17 قاعدة)":
    st.subheader("قواعد الميثاق التنفيذي الكاملة")
    st.caption("🟢 القواعد الملونة بالأخضر هي الإضافات الذكية للجيل الثاني (من 13 لـ 17).")
    for index, item in enumerate(RULES):
        show_card(*item, new=(index >= 12))

elif main_page == "نص الميثاق التنفيذي":
    st.subheader("الأمر التنفيذي - جاهز للنسخ")
    objective = st.text_input("شنو هو الهدف ديالك؟", value="بغيت نبني تطبيقات وكودات كتجيب ليا قيمة حقيقية، بشكل ذكي، قانوني وصحيح")
    level = st.selectbox("المستوى ديالك", ["مبتدئ - بغيت الشرح بالدارجة", "متوسط - كنفهم شوية", "محترف - هضر معايا بالتقنية"])
    rules_text = "\n".join(f"{i+1} - {title.split(' - ', 1)[1]}: {body}" for i, (title, body, _, _) in enumerate(RULES))
    charter = f"""الميثاق التنفيذي - IMPACT - الأمر التنفيذي السيادي

هادا أمر تنفيذي ملزم، ماشي اقتراح.
من دابا، أي جواب منك خاصو يخضع لـ 17 قاعدة اللي لتحت، بلا استثناء.
إلا تعارضت قاعدة مع عادة ديالك، القاعدة هي اللي كتغلب.

الهدف: {objective}
المستوى: {level}

القواعد الـ 17 الملزمة:
{rules_text}

كيفاش تنفذ:
- جاوبني بالدارجة المغربية البسيطة مع الحفاظ على الدقة.
- طبق السياق الذكي، التفكير النقدي، والحلول الأكثر كفاءة وأقل جهداً.
- إلا كان الجواب فيه كود، عطيني نسخة كاملة قابلة للنسخ، ووضح المتطلبات وطريقة التشغيل.
- فرّق بين اللي تأكدتي منو واللي باقي افتراض أو تخمين.
- قبل أي تغيير ممكن يسبب فقدان بيانات أو مصاريف، وضح الأثر وخذ موافقتي.
- ما تدّعيش تنفيذ عملية أو اختبار ما وقعش فعلياً.
- اقترح عليا ديما الخطوة الاستباقية الموالية.

معيار النجاح:
حل قانوني، آمن، ذكي، خدام بالاختبار، وعندو قيمة حقيقية.

إلا فهمتي هاد الأمر التنفيذي وتقدر تلتزم به، قول: قبلت الأمر التنفيذي، ونبداو.
"""
    st.text_area("الأمر التنفيذي كامل", charter, height=520)
    with st.expander("عرض أو نسخ كود التطبيق كاملاً"):
        try:
            with open(__file__, "r", encoding="utf-8") as f:
                source_code = f.read()
            st.code(source_code, language="python")
        except Exception:
            st.info("ما قدرتش نقرا ملف الكود من هنا. نسخو من GitHub.")

else:
    st.subheader("ميزان التحقق المتقدم (AST Analysis)")
    st.caption("فحص هيكلي ذكي للكود يكتشف الأخطاء النحوية، الدوال الفارغة، غياب حماية الاستثناءات، والمفاتيح المكشوفة.")
    section = st.radio("اختار نوع الفحص", ["فحص نحوي والهيكلي للكود", "مؤشرات تحقيق الشرط", "مراجعة رقم ومصدر"])

    if section == "فحص نحوي والهيكلي للكود":
        code_input = st.text_area("لصق كود Python هنا", height=260)
        if st.button("فحص متقدم للكود", key="syntax_check_adv"):
            if not code_input.strip():
                st.warning("لصق الكود الأول.")
            else:
                result = inspect_python_advanced(code_input)
                show_status(result["status"])
                if result["syntax_ok"]:
                    st.success(result["summary"])
                else:
                    st.error(result["summary"])
                with st.expander("تفاصيل التحذيرات والملاحظات التقنية", expanded=True):
                    for warning in result["warnings"]:
                        st.markdown(f"- {warning}")
                add_pending("كود - تحليل هيكلي متقدم", result["status"], "القاعدة 12 - الاختبار قبل الاعتماد", result["summary"])
                st.info("التحليل الهيكلي كيعطيك مؤشرات بنيوية، ولكن ما كيعوضش التشغيل الفعلي (Runtime Test).")

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
        if is_duplicate(pending, st.session_state.history):
            st.warning("⚠️ هاد النتيجة مسجلة من قبل في هاد الجلسة.")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("سجل محلياً"):
                if is_duplicate(pending, st.session_state.history):
                    st.error("ما تسجلاتش - هادي مكررة.")
                else:
                    st.session_state.history.append(pending)
                    st.session_state.pending = None
                    st.success("تسجلات فالجلسة الحالية فقط.")
        with col2:
            if st.button("حاول التسجيل في Google Form"):
                ok, message = save_to_google_form(pending)
                if ok:
                    if not is_duplicate(pending, st.session_state.history):
                        st.session_state.history.append(pending)
                    st.session_state.pending = None
                    st.success(message)
                else:
                    st.error(message)
        if st.button("تجاهل النتيجة"):
            st.session_state.pending = None
            st.info("تم تجاهل النتيجة؛ ما تسجلاتش.")

    st.divider()
    st.subheader("التقرير")
    # --- v6.2 NEW: عداد + زر Responses ---
    st.write(f"عدد السجلات فهاد الجلسة (محلي): {len(st.session_state.history)}")
    st.caption("Google Form ما كيرجعش السجلات للتطبيق. العدد الكامل كاين غير في Google Form > Responses.")
    cfg_now = get_form_config()
    if cfg_now.get("responses_url"):
        st.link_button("📊 شوف سجلات Google Form كاملة", cfg_now["responses_url"])
    else:
        st.info("زيد GOOGLE_FORM_RESPONSES_URL في Secrets باش يبان ليك زر سجلات Google Form هنا.")
    st.caption("Google Form ما كيرجعش السجلات للتطبيق. باش تشوف السجلات الكاملة، سير لـ Google Form > Responses > View in Sheets.")
    history = st.session_state.history
    if history:
        st.write(f"عدد السجلات فهاد الجلسة: {len(history)}")
        from collections import Counter
        c = Counter([r.get("status", "?") if isinstance(r, dict) else "?" for r in history])
        st.write("توزيع الحالات:")
        for k, v in c.items():
            st.write(f"- {k} : {v} مرة")
        if st.button("🧹 حيد التكرار من التقرير"):
            cleaned, removed = dedupe_history(history)
            st.session_state.history = cleaned
            if removed == 0:
                st.info("ما كاين حتى تكرار. التقرير نقي.")
            else:
                st.success(f"حيدت {removed} سجل مكرر. دابا التقرير فيه {len(cleaned)} سجل نقي.")
        for row in reversed(history):
            if isinstance(row, dict):
                st.write(f"{row.get('date','')} | {row.get('kind','')} | الحالة: {row.get('status','')} | {row.get('rule','')}")
        if st.button("مسح سجل هاد الجلسة"):
            st.session_state.history = []
            st.success("تم مسح السجل المحلي من هاد الجلسة فقط. بيانات Google Form ما تمسحاتش.")
    else:
        st.caption("ما كاين حتى سجل محلي دابا.")

st.divider()
st.caption("IMPACT التنفيذي v6.2 — ما نعتابروش النتيجة مؤكدة حتى يكون عندنا دليل مناسب.")
