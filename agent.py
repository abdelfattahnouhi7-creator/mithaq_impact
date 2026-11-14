# agent.py - أول Agent ديال IMPACT - A: يصلح كود Python بوحدو
import json
import os
from impact_sandbox import run_sandboxed

MAX_TRIES = 3

def run_3_tests(code, func_name):
    """كيشغل 3 Tests وكيرد النتيجة"""
    tests = [
        {"name": "Test 1 - مدخل صحيح", "args": "(5, 3)", "expected": "8", "should_fail": False},
        {"name": "Test 2 - مدخل غالط", "args": "('a', 3)", "expected": None, "should_fail": True},
        {"name": "Test 3 - حالة حدية", "args": "(0, 0)", "expected": "0", "should_fail": False},
    ]
    results = []
    for t in tests:
        test_code = f"{code}\n\ntry:\n    result = {func_name}{t['args']}\n    print('RESULT:' + str(result))\nexcept Exception as e:\n    print('ERROR:' + type(e).__name__ + ': ' + str(e))"
        out = run_sandboxed(test_code)
        # تحليل النتيجة
        if "RESULT:" in out:
            got = out.split("RESULT:")[1].strip().split("\n")[0]
            if t['should_fail']:
                results.append({"test": t['name'], "status": "فشل", "detail": f"كان خاصو يرفض، ولكن رجع: {got}"})
            elif got == t['expected']:
                results.append({"test": t['name'], "status": "نجح", "detail": f"المخرج: {got}"})
            else:
                results.append({"test": t['name'], "status": "فشل", "detail": f"توقعنا {t['expected']}, لقينا {got}"})
        elif "ERROR:" in out:
            err = out.split("ERROR:")[1].strip().split("\n")[0]
            if t['should_fail']:
                results.append({"test": t['name'], "status": "نجح", "detail": f"رفض المدخل الغالط: {err}"})
            else:
                results.append({"test": t['name'], "status": "فشل", "detail": f"خطأ: {err}"})
        else:
            results.append({"test": t['name'], "status": "فشل", "detail": f"مخرج غريب: {out[:200]}"})
    return results

def ask_llm_to_fix(code, failures):
    """هنا فين الـ Agent كيفكر - كيسول النموذج يصلح"""
    # دابا خدامة كـ قاعدة بسيطة، ومن بعد نربطوها بـ API حقيقي
    # مثال: إلا كان المشكل ديال TypeError، كيزيد تحقق من النوع
    if "can only concatenate" in str(failures) or "TypeError" in str(failures):
        fixed = code.replace(
            "def add(a, b):",
            "def add(a, b):\n    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):\n        raise TypeError('المدخلات خاصها تكون أرقام')"
        )
        return fixed, "زدت تحقق من النوع باش يرفض المدخلات الغالطة"
    return code, "ما لقيتش إصلاح تلقائي"

def agent_fix(code, func_name="add"):
    print(f"🤖 Agent بدا - كيجرب الكود...")
    current_code = code
    for attempt in range(1, MAX_TRIES + 1):
        print(f"\n--- محاولة {attempt}/{MAX_TRIES} ---")
        results = run_3_tests(current_code, func_name)
        for r in results:
            print(f"{'✅' if r['status']=='نجح' else '❌'} {r['test']}: {r['detail']}")
        passed = sum(1 for r in results if r['status'] == "نجح")
        if passed == 3:
            print(f"\n🎉 مجرب ✅ - نجحو 3/3 في المحاولة {attempt}")
            return current_code, True
        failures = [r for r in results if r['status'] == "فشل"]
        print(f"\n⚠️ مجرب جزئيا - نجحو {passed}/3 - كنحاول نصلح...")
        current_code, reason = ask_llm_to_fix(current_code, failures)
        print(f"🔧 الإصلاح: {reason}")
    print(f"\n❌ فشل - ما نجحش بعد {MAX_TRIES} محاولات")
    return current_code, False

# --- جرب دابا ---
if __name__ == "__main__":
    # كود خاسر عن قصد - باش تشوف الـ Agent كيصلحو
    broken_code = """def add(a, b):
    return a + b"""
    fixed, ok = agent_fix(broken_code, "add")
    print("\n--- الكود النهائي ---")
    print(fixed)
