import ast
import hashlib
import hmac
import importlib.util
import io
import json
import os
import re
import tempfile
import time
import uuid
from collections import Counter
from datetime import datetime

import requests
import streamlit as st

from impact_sandbox import run_sandbox

VERSION = "v9.1"
st.set_page_config(page_title="الميثاق التنفيذي - IMPACT v9.1", page_icon="📜", layout="centered")

# ---------- الحماية: مقفول افتراضياً ----------
def _secret(name, default=""):
    try:
        return st.secrets.get(name, default)
    except Exception:
        return default

APP_PASSWORD = str(_secret("IMPACT_PASSWORD", ""))
ALLOW_OPEN = str(_secret("IMPACT_ALLOW_OPEN", "")) == "1"
MAX_ATTEMPTS, LOCK_SECONDS = 5, 60

if APP_PASSWORD:
    st.session_state.setdefault("authed", False)
    st.session_state.setdefault("fails", 0)
    st.session_state.setdefault("locked_until", 0.0)
    if not st.session_state.authed:
        st.title("🔒 IMPACT - دخول خاص")
        remaining = st.session_state.locked_until - time.time()
        if remaining > 0:
            st.error(f"بزاف د المحاولات. تسنى {int(remaining) + 1} ثانية.")
            st.stop()
        pw = st.text_input("كلمة السر", type="password")
        if st.button("دخول"):
            if hmac.compare_digest(pw.encode("utf-8"), APP_PASSWORD.encode("utf-8")):
                st.session_state.authed = True
                st.session_state.fails = 0
                st.rerun()
            else:
                st.session_state.fails += 1
                if st.session_state.fails >= MAX_ATTEMPTS:
                    st.session_state.locked_until = time.time() + LOCK_SECONDS
                    st.session_state.fails = 0
                st.error("كلمة السر غالطة.")
        st.stop()
elif not ALLOW_OPEN:
    st.error("🔒 التطبيق مقفول: ما كاينش IMPACT_PASSWORD في Secrets. زيدو باش يخدم "
             "(أو IMPACT_ALLOW_OPEN = \"1\" إلا بغيتيه مفتوح للجميع عن قصد).")
    st.stop()
else:
    st.warning("⚠️ التطبيق مفتوح للجميع (IMPACT_ALLOW_OPEN=1). الـ Sandbox متوقف فهاد الحالة.")

SANDBOX_ENABLED = bool(APP_PASSWORD) and str(_secret("IMPACT_SANDBOX", "1")) == "1"

st.markdown("""
<style>
.stApp { direction: rtl; text-align: right; }
h1,h2,h3,p,div,span,label { direction: rtl; text-align: right; line-height: 1.85; }
.stTextArea textarea,.stTextInput input { direction: rtl; text-align: right; font-size: 16px; }
.stButton>button { width: 100%; }
.card { border-radius:14px; padding:16px; margin-bottom:12px; }
.l1 { background:#1a1e2e; border:1px solid #1976d2; }
.l2 { background:#2e1a1a; border:1px solid #c62828; }
.l3 { background:#1a2e1a; border:1px solid #2e7d32; }
.l4 { background:#2e2a1a; border:1px solid #f9a825; }
.card-title { font-size:19px; font-weight:bold; color:white; margin-bottom:8px; }
.card-text { font-size:15px; color:#ddd; margin:4px 0; }
.card-warn { font-size:14px; color:#ffaaaa; margin-top:8px; }
.badge-ok { background:#1a2e1a; color:#a5d6a7; padding:8px 12px; border-radius:20px; font-weight:bold; display:inline-block; }
.badge-fail { background:#3a1a1a; color:#ff9999; padding:8px 12px; border-radius:20px; font-weight:bold; display:inline-block; }
.badge-test { background:#3a2e1a; color:#ffcc80; padding:8px 12px; border-radius:20px; font-weight:bold; display:inline-block; }
</style>
""", unsafe_allow_html=True)

# ---------- الميثاق ----------
LAYERS = ["الطبقة 1: النزاهة", "الطبقة 2: السلامة", "الطبقة 3: الدقة", "الطبقة 4: الكفاءة"]

RULES = [
    (0, "الصدق وحدود المعرفة", "إلا ما عرفتيش أو السؤال خارج معرفتك، قول \"ما عرفتش\". ما تخترعش جواب.", "كيمنع المعلومات المختلقة.", "معلومة خاطئة كتضيع الوقت والفلوس."),
    (0, "المصدر والأرقام", "فرّق بين الحقيقة والرأي والتخمين. أي رقم مؤثر (ثمن، نسبة، إحصائية) عطيني مصدره وتاريخه ووحدته، وإلا صرّح بلي هو تقدير.", "الأرقام كتأثر مباشرة على القرارات.", "قرار مبني على رقم غير موثوق."),
    (0, "الصراحة فالقدرات", "وضح شنو تقدر تنفذ فعلياً، وشنو غير تشرحو، وشنو محتاج مني أداة أو صلاحية. ما تدّعيش الوصول لشي نظام ما عندكش عليه.", "كيمنع الوعود والادعاءات غير الحقيقية.", "الاعتماد على قدرة أو صلاحية ما كاينش."),
    (0, "صفر مجاملة", "ما توافقنيش باش ترضيني. إلا كانت الفكرة ناقصة أو كاين مسار أذكى وأرخص، صارحني ووري ليا اللي ما شفتوش.", "تصحيح المسار أحسن من التصفيق للخطأ.", "بناء مشروع على أساس هش بسبب المجاملة."),
    (1, "التحذير قبل الخطر", "فالطلبات اللي فيها خطر قانوني أو مالي أو صحي أو أمني، وضح الخطر والحدود قبل التنفيذ، وما تقدمش التخمين كنصيحة مختصة.", "كيخليني ناخد القرار وأنا فاهم المخاطر.", "ضرر قانوني أو مالي أو صحي."),
    (1, "البديل قبل الرفض", "إلا ما قدرتيش تنفذ، شرح السبب واقترح بديل قانوني وآمن.", "الرفض بوحدو ما كيقدمش المشروع.", "توقف المشروع بلا محاولة حل."),
    (1, "الموافقة قبل الأثر", "أي تغيير ممكن يسبب ضياع بيانات أو مصاريف، وضح الأثر وخذ موافقتي قبل.", "كيحمي البيانات والفلوس من القرارات الصامتة.", "ضياع بيانات أو مصاريف بلا علمي."),
    (2, "الفعل قبل الكلام", "ما تقولش \"تم الحفظ/الإرسال/الدفع\" حتى يتنفذ ويتحقق من النتيجة. فرّق بين: محاولة، نجاح الطلب، تأكد الأثر النهائي.", "الرسالة ماشي دليل على وقوع الفعل.", "الاعتقاد أن العملية وقعات وهي ما وقعاتش."),
    (2, "الاختبار قبل الاعتماد", "أي كود أو حل تقني، وضح شنو تختبر فعلياً وشنو بقى بلا اختبار، وهل هو مبني على معيار موثوق ولا على استدلال غير مؤكد. ما تصفوش بـ \"خدام\" أو \"آمن\" بلا دليل.", "كيحول الادعاء لنتيجة قابلة للفحص.", "نشر كود فيه أخطاء أو مخاطر غير مكتشفة."),
    (2, "الوضوح قبل التنفيذ", "قبل أي مهمة، تأكد من الهدف والقيود ومعيار النجاح. إلا كان غموض كيبدل النتيجة، سولني سؤال واحد محدد. إلا كان الافتراض آمن، نفذ وصرّح بيه.", "كيضمن أننا خدامين على نفس الهدف.", "تنفيذ صحيح تقنياً ولكن ماشي هو المطلوب."),
    (3, "أبسط حل كافي", "قلب على أقصر طريق كيعطي أحسن نتيجة بأقل تعقيد، وقسم المهام الكبيرة لمراحل، وقبل ما ندوزو للمرحلة الجاية قول ليا شنو خاصنا نتحققو منو.", "البساطة كتوفر الوقت وكتقلل الأخطاء.", "هندسة زائدة وكود معقد صعيب فالتطوير."),
    (3, "الخطوة الجاية", "ملي تكمل، قول ليا شنو هي العقبة أو الخطوة المنطقية الموالية. وملي يوقع خطأ ونصلحوه، لخّص الدرس فسطر واحد.", "كيخلي الأداة شريك كيشوف لقدام.", "تقدم بطيء وتكرار نفس الأخطاء."),
]

def build_charter(objective, level):
    lines, n = [], 0
    for li, layer in enumerate(LAYERS):
        lines.append(f"--- {layer} ---")
        for r in RULES:
            if r[0] == li:
                n += 1
                lines.append(f"{n} - {r[1]}: {r[2]}")
        lines.append("")
    rules_text = "\n".join(lines).strip()
    return f"""اتفاق عمل - IMPACT {VERSION}

هادا اتفاق عمل بيني وبينك فهاد المحادثة، ماشي أمر نظام. كنطلب منك تلتزم بيه بأحسن ما تقدر، وإلا ما قدرتيش تطبق قاعدة، قولها ليا بوضوح.

الهدف: {objective}
مستوايا التقني: {level}

ترتيب الأولويات (عند التعارض الطبقة الأعلى كتغلب):
1) السلامة  >  2) النزاهة  >  3) الدقة  >  4) الكفاءة
وطلبي الحالي كيغلب على أي سياق قديم.

{rules_text}

--- بروتوكول الخطأ ---
إلا اكتشفتي خطأ فجوابك أو تناقض بين فقراته: وقف، قول ليا بوضوح شنو كان غالط، صحح، وكمل. بلا تبرير طويل.

--- شكل الجواب ---
- بالدارجة المغربية البسيطة، مع الحفاظ على المصطلحات التقنية والتحذيرات الضرورية.
- الجواب قصير ومباشر، والتفاصيل غير إلا طلبتها.
- إلا كان فيه كود: نسخة كاملة قابلة للنسخ، مع المتطلبات وطريقة التشغيل.

معيار النجاح:
حل قانوني، آمن، صحيح بالاختبار، وفيه قيمة حقيقية.

إلا فهمتي وتقدر تلتزم، قول: "قبلت اتفاق العمل"، ونبداو.
"""

def show_card(index, layer_idx, title, body, why, danger):
    # v9.1: حماية من قاعدة ناقصة، باش التطبيق ما يطيحش
    if not all([title, body, why, danger]):
        st.error(f"قاعدة رقم {index} ناقصة. خاصها 5 ديال الحقول كاملين.")
        return
    st.markdown(
        f'<div class="card l{layer_idx + 1}"><div class="card-title">{index} - {title}</div>'
        f'<div class="card-text"><b>القاعدة:</b> {body}</div>'
        f'<div class="card-text"><b>علاش:</b> {why}</div>'
        f'<div class="card-warn"><b>الخطر إلا تهملات:</b> {danger}</div></div>',
        unsafe_allow_html=True)

def show_status(status):
    if status == "نجح":
        st.markdown('<span class="badge-ok">✅ نجح</span>', unsafe_allow_html=True)
    elif status == "فشل":
        st.markdown('<span class="badge-fail">❌ فشل</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="badge-test">⚠️ خاص اختبار</span>', unsafe_allow_html=True)

def normalize_arabic(text):
    text = text.lower()
    for a, b in [("أ", "ا"), ("إ", "ا"), ("آ", "ا"), ("ة", "ه"), ("ى", "ي"), ("ؤ", "و"), ("ئ", "ي")]:
        text = text.replace(a, b)
    return text

# ---------- السجل ----------
HISTORY_FILE = "impact_history.json"

def fingerprint(rec):
    key = f"{str(rec.get('date', ''))[:19]}|{rec.get('kind', '')}|{rec.get('status', '')}|{rec.get('rule', '')}|{rec.get('details', '')}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()

def is_duplicate(rec, history):
    fp = fingerprint(rec)
    return any(fingerprint(h) == fp for h in history)

def dedupe_history(history):
    seen, out, removed = set(), [], 0
    for h in history:
        fp = fingerprint(h)
        if fp in seen:
            removed += 1
            continue
        seen.add(fp)
        out.append(h)
    return out, removed

def clean_records(data):
    return [d for d in data if isinstance(d, dict) and "kind" in d and "status" in d]

def load_history_from_disk():
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                return clean_records(data)
    except Exception:
        pass
    return []

def save_history_to_disk(history):
    tmp_path = None
    try:
        fd, tmp_path = tempfile.mkstemp(dir=os.path.dirname(os.path.abspath(HISTORY_FILE)), suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, HISTORY_FILE)
        return True
    except Exception:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass
        return False

def persist():
    if not save_history_to_disk(st.session_state.history):
        st.warning("⚠️ ما قدرتش نكتب السجل فالقرص. التسجيل بقى غير فهاد الجلسة.")

# ---------- الفحص الهيكلي v9.1 ----------
SECRET_TOKENS = {"key", "apikey", "password", "passwd", "pwd", "secret", "token", "auth"}

def _is_secret_name(name):
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", str(name)).lower()
    return any(tok in SECRET_TOKENS for tok in re.split(r"[^a-z0-9]+", s) if tok)

def _extract_string_value(node):
    # v9.1: كيلقى حتى السلاسل المركبة: "abc" + "123" و f-string بسيطة
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left = _extract_string_value(node.left)
        right = _extract_string_value(node.right)
        if left is not None and right is not None:
            return left + right
    if isinstance(node, ast.JoinedStr):
        parts = []
        for v in node.values:
            if isinstance(v, ast.Constant) and isinstance(v.value, str):
                parts.append(v.value)
            else:
                return None
        return "".join(parts)
    return None

def _is_secret_value(node):
    val = _extract_string_value(node)
    return val is not None and len(val) > 5

def inspect_python_advanced(code):
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return {"syntax_ok": False, "status": "فشل", "summary": f"خطأ نحوي فالسطر {exc.lineno}: {exc.msg}", "warnings": ["الكود ما دازش من التحليل النحوي."]}
    warnings, imports = [], set()
    has_try, secret_found, empty_funcs = False, False, 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.asname or alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.update(alias.asname or alias.name for alias in node.names)
        elif isinstance(node, ast.Try):
            has_try = True
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                empty_funcs += 1
        elif isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and _is_secret_name(t.id) and _is_secret_value(node.value):
                    secret_found = True
        elif isinstance(node, ast.AnnAssign):
            if isinstance(node.target, ast.Name) and _is_secret_name(node.target.id) and node.value is not None and _is_secret_value(node.value):
                secret_found = True
        elif isinstance(node, ast.Dict):
            for k, v in zip(node.keys, node.values):
                if isinstance(k, ast.Constant) and isinstance(k.value, str) and _is_secret_name(k.value) and _is_secret_value(v):
                    secret_found = True
        elif isinstance(node, ast.keyword):
            if node.arg and _is_secret_name(node.arg) and _is_secret_value(node.value):
                secret_found = True
    if secret_found:
        warnings.append("⚠️ خطر أمني محتمل: لقيت مفتاح سري أو كلمة مرور مكتوبة مباشرة داخل الكود (Hardcoded Secret). هادا فحص أولي فقط.")
    if empty_funcs:
        warnings.append(f"تنبيه: لقيت {empty_funcs} دالة فارغة فيها غير (pass).")
    if not has_try and ("requests." in code or "open(" in code):
        warnings.append("ملاحظة جودة: الكود فيه عمليات إدخال/إخراج أو طلبات شبكة بدون حماية (Try/Except).")
    if importlib.util.find_spec("pyflakes") is not None:
        try:
            from pyflakes.api import check
            from pyflakes.reporter import Reporter
            output = io.StringIO()
            count = check(code, "<الكود المدخل>", reporter=Reporter(output, output))
            warnings.append(f"Pyflakes رصد {count} ملاحظة محتملة:\n{output.getvalue().strip()}" if count else "Pyflakes: ما رصد حتى ملاحظة من الأنواع اللي كيكشفها.")
        except Exception as exc:
            warnings.append(f"تعذر تشغيل Pyflakes: {type(exc).__name__}: {exc}")
    else:
        warnings.append("Pyflakes غير مثبت؛ تم تجاوز الفحص الاختياري.")
    return {"syntax_ok": True, "status": "فشل" if secret_found else "خاص اختبار",
            "summary": "نجح التحليل النحوي، وباقي الفحوص مؤشرات فقط ولا تعوض اختبار التشغيل.",
            "warnings": warnings}

def inspect_requirement(code, requirement):
    c, r, checks = normalize_arabic(code), normalize_arabic(requirement), []
    if any(w in r for w in ["حفظ", "سجل", "تسجيل"]):
        pats = ["write(", "to_csv(", "to_sql(", "insert(", "commit(", "save(", "json.dump", "open("]
        checks.append(("الحفظ", [p for p in pats if p in c], "وجود هاد الكلمات ما كيضمنش أن البيانات تحفظات فعلاً."))
    if any(w in r for w in ["ارسال", "ارسل", "واتساب", "ايميل", "رساله"]):
        pats = ["requests.post", "smtp", "send_message", "sendmail", "messages.create"]
        checks.append(("الإرسال", [p for p in pats if p in c], "خاص اختبار حقيقي والتحقق من رد الخدمة أو وصول الرسالة."))
    if any(w in r for w in ["دفع", "خلص", "فلوس", "شراء"]):
        pats = ["stripe", "paypal", "paymentintent", "checkout"]
        checks.append(("الدفع", [p for p in pats if p in c], "وجود اسم مزود الدفع ما كيثبتش نجاح معاملة مالية."))
    if not checks:
        return ["ما قدرتش نحدد نوع الشرط آلياً. خاص مراجعة يدوية واختبار عملي."], "خاص اختبار"
    out = [f"{lab}: " + (f"لقيت مؤشرات نصية: {', '.join(f)}." if f else "ما لقيتش مؤشرات نصية معروفة.") + " " + cav for lab, f, cav in checks]
    return out, "خاص اختبار"

# ---------- Google Form ----------
def get_form_config():
    keys = {"url": "GOOGLE_FORM_URL", "date": "ENTRY_DATE", "kind": "ENTRY_KIND", "status": "ENTRY_STATUS",
            "rule": "ENTRY_RULE", "details": "ENTRY_DETAILS", "responses_url": "GOOGLE_FORM_RESPONSES_URL"}
    return {k: _secret(v, "") for k, v in keys.items()}

def save_to_google_form(record):
    cfg = get_form_config()
    if not cfg["url"] or not all(cfg[k] for k in ("date", "kind", "status", "rule", "details")):
        return False, "إعدادات Google Form ناقصة في Secrets."
    payload = {cfg[k]: record.get(k, "") for k in ("date", "kind", "status", "rule", "details")}
    try:
        resp = requests.post(cfg["url"], data=payload, timeout=20, allow_redirects=False)
        if resp.status_code in (200, 302):
            return True, f"وصلنا رد HTTP {resp.status_code} من Google Forms. هذا يؤكد استجابة الخادم فقط، ولا يثبت أن الرد ظهر في Responses. راجع صفحة الردود يدوياً."
        return False, f"Google Forms رجّع HTTP {resp.status_code}."
    except requests.RequestException as exc:
        return False, f"فشل الاتصال بـ Google Forms: {exc}"

def add_pending(kind, status, rule, details):
    st.session_state.pending = {"id": str(uuid.uuid4()), "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "kind": kind, "status": status, "rule": rule, "details": details}

if "history" not in st.session_state:
    st.session_state.history = load_history_from_disk()
if "pending" not in st.session_state:
    st.session_state.pending = None

# ---------- الواجهة ----------
st.title("📜 الميثاق التنفيذي - IMPACT v9.1")
st.caption(f"من الكلام إلى الفعل: اتفاق عمل بـ {len(RULES)} قاعدة فـ 4 طبقات. - {VERSION}")
st.info("هاد التطبيق كيولد نص اتفاق عمل، وكيتحقق من الكود قبل الاعتماد عليه. هادا اتفاق بينك وبين الذكاء الاصطناعي، ماشي أمر نظام.")

main_page = st.radio("شنو بغيتي تشوف؟", [f"القواعد ({len(RULES)} قاعدة)", "نص اتفاق العمل (v9.1)", "ميزان التحقق المتقدم"], horizontal=True)

if main_page.startswith("القواعد"):
    st.subheader("قواعد الميثاق (مرتبة بالأولوية)")
    st.caption("🔴 السلامة > 🔵 النزاهة > 🟢 الدقة > 🟡 الكفاءة. عند التعارض الطبقة الأعلى كتغلب.")
    n = 0
    for li, layer in enumerate(LAYERS):
        st.markdown(f"### {layer}")
        for r in RULES:
            if r[0] == li:
                n += 1
                # v9.1: تحقق من شكل القاعدة قبل العرض
                if len(r) != 5:
                    st.error(f"قاعدة رقم {n} فيها {len(r)} حقول، خاصها 5. صلحها في RULES.")
                    continue
                show_card(n, *r)

elif main_page.startswith("نص اتفاق"):
    st.subheader("اتفاق العمل - جاهز للنسخ")
    objective = st.text_input("شنو هو الهدف ديالك؟", value="تقديم حلول برمجية وتقنية دقيقة وآمنة وذات قيمة حقيقية.")
    level = st.selectbox("المستوى ديالك", ["مبتدئ", "متوسط", "محترف"], index=2)
    st.text_area("اتفاق العمل كامل", build_charter(objective, level), height=520)
    with st.expander("عرض كود التطبيق"):
        try:
            with open(__file__, "r", encoding="utf-8") as f:
                st.code(f.read(), language="python")
        except Exception:
            st.info("ما قدرتش نقرا ملف الكود من هنا. نسخو من GitHub.")

else:
    st.subheader("ميزان التحقق المتقدم (AST + Pyflakes + Sandbox للاختبار فقط)")
    st.caption("فحص هيكلي + تنفيذ للاختبار في process منفصل. ماشي عزل أمني كامل.")
    if os.name != "posix":
        st.warning("⚠️ نتا خدام في Windows: حدود الموارد ديال Linux (RLIMIT) ما كتخدمش هنا. الـ Sandbox أضعف، استعملو غير لكود ديالك بوحدك.")
    section = st.radio("اختار نوع الفحص", ["فحص نحوي وهيكلي للكود", "تنفيذ للاختبار في Sandbox", "مؤشرات تحقيق الشرط", "مراجعة رقم ومصدر"])

    if section == "فحص نحوي وهيكلي للكود":
        code_input = st.text_area("لصق كود Python هنا", height=260)
        if st.button("فحص متقدم للكود", key="syntax_check_adv"):
            if not code_input.strip():
                st.warning("لصق الكود الأول.")
            else:
                result = inspect_python_advanced(code_input)
                show_status(result["status"])
                (st.success if result["syntax_ok"] else st.error)(result["summary"])
                with st.expander("تفاصيل التحذيرات والملاحظات التقنية", expanded=True):
                    for w in result["warnings"]:
                        st.markdown(f"- {w}")
                add_pending("كود - تحليل هيكلي متقدم", result["status"], "القاعدة 9 - الاختبار قبل الاعتماد", result["summary"])
                st.info("التحليل الهيكلي كيعطيك مؤشرات بنيوية، ولكن ما كيعوضش التشغيل الفعلي.")

    elif section == "تنفيذ للاختبار في Sandbox":
        if not SANDBOX_ENABLED:
            st.error("الـ Sandbox متوقف: خاصك IMPACT_PASSWORD فـ Secrets (وIMPACT_SANDBOX ماشي \"0\").")
        else:
            st.warning("⚠️ للاختبار فقط: ما كيتقبلش import ولا open ولا class ولا خصائص كتبدا بـ _. "
                       "المدة القصوى 3 ثواني والذاكرة 256MB في Linux فقط. هادا تقليل مخاطر، ماشي عزل كامل. ما تشغلش كود ديال ناس آخرين هنا.")
            code_run = st.text_area("لصق كود Python بسيط للتنفيذ", value='print("hello IMPACT")\nprint(2 + 3)', height=180)
            if st.button("شغّل الكود للاختبار ▶️", key="run_sandbox"):
                if not code_run.strip():
                    st.warning("لصق الكود الأول.")
                else:
                    ok, out, err = run_sandbox(code_run)
                    if ok:
                        show_status("نجح")
                        st.success("الكود خدم فـ Sandbox. هادا كيثبت غير هاد التشغيل، ماشي صحة الكود فكل الحالات.")
                        if out:
                            st.code(out, language="text")
                        add_pending("كود - تنفيذ للاختبار Sandbox", "نجح", "القاعدة 9 - الاختبار قبل الاعتماد", f"مخرجات: {out[:200]}")
                    else:
                        show_status("فشل")
                        st.error("التنفيذ فشل أو تمنع:")
                        if out:
                            st.code(f"المخرجات قبل الفشل:\n{out}", language="text")
                        st.code(err, language="text")
                        add_pending("كود - تنفيذ للاختبار Sandbox", "فشل", "القاعدة 9 - الاختبار قبل الاعتماد", f"خطأ: {err[:200]}")

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
                has_src = any(x in normalize_arabic(answer) for x in ["مصدر", "دراسه", "حسب", "تقرير", "مرجع"])
                if numbers:
                    st.write("الأرقام اللي لقيت:", ", ".join(numbers))
                    if not (has_link or has_src):
                        show_status("فشل"); st.error("كاينين أرقام وما بانش مصدر واضح فالنص."); status_num = "فشل"
                    else:
                        show_status("خاص اختبار"); st.warning("بانت إشارة لمصدر، ولكن خاص التحقق."); status_num = "خاص اختبار"
                else:
                    show_status("خاص اختبار"); st.info("ما لقيتش أرقام واضحة فالنص."); status_num = "خاص اختبار"
                add_pending("معلومة - مراجعة أولية", status_num, "القاعدة 2 - المصدر والأرقام", "الفحص النصي ما تحققش من صحة المصدر.")

    st.divider()
    st.subheader("تسجيل النتيجة")
    pending = st.session_state.pending
    if pending:
        st.write(f"النتيجة المعلقة: {pending['kind']} — الحالة: {pending['status']}")
        show_status(pending["status"])
        st.write(pending["details"])
        dup = is_duplicate(pending, st.session_state.history)
        if dup:
            st.warning("⚠️ هاد النتيجة مسجلة من قبل.")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("سجل محلياً"):
                if dup:
                    st.error("ما تسجلاتش - هادي مكررة.")
                else:
                    st.session_state.history.append(pending)
                    persist()
                    st.session_state.pending = None
                    st.success("تسجلات. ملاحظة: على Streamlit Cloud القرص مؤقت، فحمّل نسخة JSON من التقرير.")
        with col2:
            if st.button("حاول التسجيل في Google Form"):
                ok, message = save_to_google_form(pending)
                if ok:
                    saved = dict(pending)
                    saved["google_form_status"] = "submitted_unverified"
                    if not dup:
                        st.session_state.history.append(saved)
                        persist()
                    st.session_state.pending = None
                    st.warning(message)
                else:
                    st.error(message)
        if st.button("تجاهل النتيجة"):
            st.session_state.pending = None
            st.info("تم تجاهل النتيجة؛ ما تسجلاتش.")

    st.divider()
    st.subheader("التقرير")
    history = st.session_state.history
    st.write(f"عدد السجلات المحفوظة: {len(history)}")
    cfg_now = get_form_config()
    if cfg_now.get("responses_url"):
        st.link_button("📊 شوف سجلات Google Form كاملة", cfg_now["responses_url"])
    if history:
        for k, v in Counter(r.get("status", "?") for r in history).items():
            st.write(f"- {k} : {v} مرة")
        colA, colB = st.columns(2)
        with colA:
            st.download_button("⬇️ حمل السجل JSON", data=json.dumps(history, ensure_ascii=False, indent=2),
                               file_name="impact_history.json", mime="application/json")
        with colB:
            uploaded = st.file_uploader("⬆️ رفع سجل قديم JSON", type=["json"])
            if uploaded is not None:
                up_id = getattr(uploaded, "file_id", None) or f"{uploaded.name}:{uploaded.size}"
                if st.session_state.get("last_upload") != up_id:
                    st.session_state.last_upload = up_id
                    try:
                        loaded = json.load(uploaded)
                        if not isinstance(loaded, list):
                            st.error("الملف خاصو يكون لائحة JSON.")
                        else:
                            valid = clean_records(loaded)
                            merged, _ = dedupe_history(st.session_state.history + valid)
                            st.session_state.history = merged
                            persist()
                            st.success(f"دمجت {len(valid)} سجل صالح من أصل {len(loaded)}.")
                    except Exception as e:
                        st.error(f"الملف ما تقراش: {e}")
        if st.button("🧹 حيد التكرار من التقرير"):
            cleaned, removed = dedupe_history(history)
            st.session_state.history = cleaned
            persist()
            st.info("ما كاين حتى تكرار.") if removed == 0 else st.success(f"حيدت {removed} سجل مكرر.")
        for row in reversed(history):
            sync = " | Google: إرسال غير مؤكد" if row.get("google_form_status") == "submitted_unverified" else ""
            st.write(f"{row.get('date', '')} | {row.get('kind', '')} | الحالة: {row.get('status', '')} | {row.get('rule', '')}{sync}")
        if st.checkbox("أأكد بغيت نمسح السجل نهائياً"):
            if st.button("مسح السجل الدائم"):
                st.session_state.history = []
                persist()
                st.success("تم مسح السجل.")
    else:
        st.caption("ما كاين حتى سجل محلي دابا.")

st.divider()
st.caption(f"IMPACT {VERSION} — ميثاق 12 قاعدة + Sandbox للاختبار فقط + حماية بكلمة سر (مقفول افتراضياً).")
