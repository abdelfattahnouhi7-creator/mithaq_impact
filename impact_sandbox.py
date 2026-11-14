"""IMPACT v9.1 - Sandbox للاختبار فقط، ماشي عزل أمني.

تنبيه صريح: هادي طبقات تقليل مخاطر (AST + بيئة فارغة + حدود موارد + مهلة)،
ماشي حاجز أمني كامل. باش تحمي سيرفر حقيقي، خاصك container/gVisor أو خدمة تنفيذ خارجية.
ما تشغلش كود ديال ناس ما كتعرفهمش هنا.
"""
import ast
import os
import subprocess
import sys
import tempfile

TIMEOUT_SEC = 3
MAX_OUTPUT = 10_000
MAX_FILE_BYTES = 1_000_000
MAX_CODE_CHARS = 20_000
MAX_MEMORY = 256 * 1024 * 1024

ALLOWED_BUILTINS = [
    "print", "len", "range", "str", "int", "float", "bool", "list", "dict", "set",
    "tuple", "sum", "min", "max", "abs", "round", "sorted", "enumerate", "zip",
    "reversed", "map", "filter", "any", "all", "isinstance", "divmod", "pow",
    "Exception", "ValueError", "TypeError", "ZeroDivisionError", "IndexError", "KeyError",
]

BLOCKED_NAMES = {
    "eval", "exec", "compile", "open", "input", "globals", "locals", "vars", "dir",
    "getattr", "setattr", "delattr", "hasattr", "breakpoint", "help", "exit", "quit",
    "memoryview", "type", "object", "super", "classmethod", "staticmethod", "property",
    "builtins", "__import__",
}

RUNNER = r'''
import sys, builtins
ALLOWED = %r
code = sys.stdin.read()
safe = {n: getattr(builtins, n) for n in ALLOWED}
g = {"__builtins__": safe, "__name__": "__sandbox__"}
try:
    exec(compile(code, "<sandbox>", "exec"), g)
except BaseException as e:
    tb = e.__traceback__
    line = None
    while tb is not None:
        if tb.tb_frame.f_code.co_filename == "<sandbox>":
            line = tb.tb_lineno
        tb = tb.tb_next
    where = f" (سطر {line})" if line else ""
    print(f"{type(e).__name__}: {e}{where}", file=sys.stderr)
    sys.exit(1)
''' % (ALLOWED_BUILTINS,)

def validate_code(code):
    if len(code) > MAX_CODE_CHARS:
        return f"⛔ الكود طويل بزاف (الحد {MAX_CODE_CHARS} حرف)."
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return f"خطأ نحوي فالسطر {exc.lineno}: {exc.msg}"
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            return "⛔ ممنوع: أي import (لا os ولا requests ولا غيرهم). جرب كود بلا import."
        if isinstance(node, ast.Attribute) and node.attr.startswith("_"):
            return f"⛔ ممنوع: الوصول للخاصية '{node.attr}' (الخصائص اللي كتبدا بـ _ مقفولة)."
        if isinstance(node, ast.Name) and (node.id in BLOCKED_NAMES or node.id.startswith("__")):
            return f"⛔ ممنوع: استعمال '{node.id}' فـ Sandbox."
        if isinstance(node, (ast.Global, ast.Nonlocal)):
            return "⛔ ممنوع: global / nonlocal."
        if isinstance(node, ast.ClassDef):
            return "⛔ ممنوع: تعريف class فـ Sandbox (استعمل دوال بسيطة)."
    return None

def _limits():
    import resource
    resource.setrlimit(resource.RLIMIT_CPU, (TIMEOUT_SEC, TIMEOUT_SEC))
    resource.setrlimit(resource.RLIMIT_AS, (MAX_MEMORY, MAX_MEMORY))
    resource.setrlimit(resource.RLIMIT_FSIZE, (MAX_FILE_BYTES, MAX_FILE_BYTES))
    resource.setrlimit(resource.RLIMIT_NPROC, (0, 0))
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    os.setsid()

def run_sandbox(code):
    err = validate_code(code)
    if err:
        return False, "", err
    posix = os.name == "posix"
    # v9.1: في Windows ما كاينش حدود موارد، كنعلمو بيها صراحة
    if not posix:
        err = "تحذير: نتا في Windows، حدود الموارد ديال Linux ما كتطبقش. استعمل هاد الـ Sandbox غير لكود ديالك."
        # كنبقاو خدامين، ولكن بالتحذير، ماشي بالوهم ديال الأمان
    with tempfile.TemporaryDirectory() as cwd, \
            tempfile.TemporaryFile() as fo, tempfile.TemporaryFile() as fe:
        try:
            proc = subprocess.run(
                [sys.executable, "-I", "-S", "-c", RUNNER],
                input=code.encode("utf-8"),
                stdout=fo, stderr=fe, cwd=cwd, env={},
                timeout=TIMEOUT_SEC + 2,
                preexec_fn=_limits if posix else None,
            )
        except subprocess.TimeoutExpired:
            return False, "", f"⏱️ الكود خذا أكثر من {TIMEOUT_SEC} ثواني - تقتل. يمكن فيه boucle لا نهائية."
        except Exception as exc:
            return False, "", f"تعذر تشغيل Sandbox: {type(exc).__name__}: {exc}"
        fo.seek(0); fe.seek(0)
        out = fo.read(MAX_OUTPUT + 1).decode("utf-8", "replace")
        errtxt = fe.read(MAX_OUTPUT + 1).decode("utf-8", "replace")
    out = out[:MAX_OUTPUT] + ("\n...[تقطع المخرج]" if len(out) > MAX_OUTPUT else "")
    if proc.returncode == 0:
        return True, out, errtxt[:MAX_OUTPUT]
    if proc.returncode < 0:
        sig = -proc.returncode
        reason = {24: "تجاوز وقت المعالج", 25: "المخرج كبير بزاف", 9: "تقتل (موارد)", 11: "تعطل (غالباً الذاكرة)"}.get(sig, f"تقتل بالإشارة {sig}")
        return False, out, f"⛔ العملية {reason}."
    return False, out, errtxt[:MAX_OUTPUT] or f"فشل (رمز {proc.returncode})."
