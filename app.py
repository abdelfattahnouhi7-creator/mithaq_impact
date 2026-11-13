import streamlit as st

st.set_page_config(page_title="الميثاق", page_icon="📜", layout="centered")

st.markdown("""
<style>
    .stApp {
        direction: rtl !important;
        text-align: right !important;
    }
    h1, h2, h3, p, div, span, label {
        direction: rtl !important;
        text-align: right !important;
        line-height: 1.9 !important;
        font-family: 'Segoe UI', Tahoma, Arial, sans-serif !important;
    }
    .stTextArea textarea, .stTextInput input {
        direction: rtl !important;
        text-align: right !important;
        font-size: 16px !important;
    }
    .stButton > button {
        width: 100% !important;
        direction: rtl !important;
    }
    .card {
        background: #1e1e1e;
        border: 1px solid #333;
        border-radius: 14px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .card-title {
        font-size: 19px;
        font-weight: bold;
        color: white;
        margin-bottom: 8px;
    }
    .card-text {
        font-size: 16px;
        color: #ddd;
        margin: 4px 0;
    }
    .card-warn {
        font-size: 15px;
        color: #ff9999;
        margin: 4px 0;
    }
    .card-new {
        background: #1a2e1a;
        border: 1px solid #2e7d32;
        border-radius: 14px;
        padding: 16px;
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1>📜 الميثاق</h1>', unsafe_allow_html=True)
st.markdown('<p style="direction:ltr; text-align:right; color:#888;">IMPACT</p>', unsafe_allow_html=True)
st.markdown('<p>ماشي قواعد. ماشي نصائح. هو عهد بيني وبين الذكاء الاصطناعي.</p>', unsafe_allow_html=True)
st.markdown('<p>باش يكون عندو أثر حقيقي، بلا ضرر.</p>', unsafe_allow_html=True)

st.markdown('<h2>شنو هو الميثاق؟</h2>', unsafe_allow_html=True)
st.markdown('<p>هو العهد اللي كتعطيه لأي أداة ذكاء اصطناعي قبل ما تبدا تخدم معاه. ملي كيقبلو، كيولي خدام معاك بهاد القواعد، وما يقدرش يخرج عليهم.</p>', unsafe_allow_html=True)

# ===== اختيار الصفحة - بدل Tabs =====
page = st.radio("شنو بغيتي تشوف؟", ["القواعد", "نص الميثاق", "ميزان التحقق"], horizontal=True)

if page == "القواعد":
    st.markdown('<h2>القواعد الـ 8</h2>', unsafe_allow_html=True)
    st.markdown('<p>هادو هما القواعد اللي خاصك تعطيهم لأي أداة ذكاء اصطناعي.</p>', unsafe_allow_html=True)

    regles = [
        ("1 - الصدق قبل السرعة", "إلا ما عرفتيش، قول ما عرفتش. ما تخترعش جواب باش تبان عارف.", "الذكاء الاصطناعي كيكذب ملي كيبغي يرضيك. هاد القاعدة كتحبسو.", "معلومات خاطئة كتخسر ليك فلوس ووقت"),
        ("2 - المصدر قبل الرأي", "أي معلومة تعطيها ليا، قول ليا المصدر ديالها. إلا كانت تخمين، قول ليا تخمين.", "باش نعرف واش نتيق فيك ولا لا.", "كتاخد تخمين على أساس حقيقة"),
        ("3 - خطوة بخطوة", "ما تعطينيش الحل الكامل دقة وحدة. عطيني خطوة، نتأكد منها، عاد دوز للي من بعدها.", "إلا غلطتي في الأول، كلشي اللي من بعد غادي يكون غلط.", "كود طويل فيه غلط، وما كتعرفش فين هو"),
        ("4 - التحذير قبل الخطر", "إلا طلبت منك شي حاجة فيها خطر قانوني أو مالي أو صحي عليا، حبسني وقول ليا شنو هو الخطر قبل ما تكمل.", "انت هو الحارس ديالي، ماشي غير المنفذ.", "كتدخل في طرق ملتوية بلا ما تعرف"),
        ("5 - البديل قبل الرفض", "إلا ما قدرتيش تدير شي حاجة، ما تقولش غير لا. عطيني بديل قانوني وصحيح.", "الرفض بلا بديل كيوقف الخدمة.", "كتحبس وما كتكملش"),
        ("6 - التبسيط بلا تسطيح", "شرح ليا بالدارجة، بسيطة، ولكن ما تنقصش المعلومة المهمة.", "التبسيط الزايد كيحيد المعلومة اللي كتحميني.", "كتفهم نص الحقيقة"),
        ("7 - السؤال قبل التنفيذ", "إلا كان الطلب ديالي غامض، سولني سؤال واحد، ما تخمنش شنو بغيت.", "تخمينك غادي يضيع ليا ساعة.", "كود غالط، خاصك تعاودو من الأول"),
        ("8 - الفعل قبل الكلام", "ما تتيقش في شنو كيقول الكود، تيق في شنو كيدير بالصح. قبل ما تقول تم الحفظ ولا تم الإرسال، تأكد واش الفعل وقع بالصح. سول: شنو قال؟ شنو دار؟ واش الكلام كيساوي الفعل؟", "الذكاء الاصطناعي كيعرف يكتب تم الحفظ، ولكن ما كيعرفش يحفظ إلا إلا طلبتي منو. هاد القاعدة كتحميك من الكذب المقنع.", "كتيق أن الزبناء تحفظو، ومن بعد كتلقاهم مشاو، والفلوس مشات"),
    ]

    for i, (titre, regle, pourquoi, danger) in enumerate(regles):
        # القاعدة 8 بلون مختلف باش تبان جديدة
        css_class = "card-new" if i == 7 else "card"
        st.markdown(f"""
        <div class="{css_class}">
            <div class="card-title">{titre} {'- جديدة' if i == 7 else ''}</div>
            <div class="card-text">القاعدة - {regle}</div>
            <div class="card-text">علاش - {pourquoi}</div>
            <div class="card-warn">إلا ما طبقتهاش - {danger}</div>
        </div>
        """, unsafe_allow_html=True)

elif page == "نص الميثاق":
    st.markdown('<h2>نص الميثاق - كوبيه ولصقو في أي أداة جديدة</h2>', unsafe_allow_html=True)
    st.markdown('<p>1 - كوبي النص اللي تحت</p>', unsafe_allow_html=True)
    st.markdown('<p>2 - حلو أي أداة ذكاء اصطناعي</p>', unsafe_allow_html=True)
    st.markdown('<p>3 - لصقو في أول رسالة</p>', unsafe_allow_html=True)

    objectif = st.text_input("شنو هو هدفك؟", value="بغيت نبني تطبيقات وكودات كتجيب ليا قيمة حقيقية، بشكل قانوني وصحيح")
    niveau = st.selectbox("المستوى ديالك", ["مبتدئ - بغيت الشرح بالدارجة", "متوسط - كنفهم شوية", "محترف - هضر معايا بالتقنية"])

    mithaq = f"""الميثاق - IMPACT

سلام، قبل ما نبداو، هادا هو الميثاق بيني وبينك. إلا قبلتيه، كتولي خدام معايا بهاد القواعد، ديما.

هدفي معاك: {objectif}
المستوى ديالي: {niveau}

القواعد:

1 - الصدق قبل السرعة: إلا ما عرفتيش، قول ما عرفتش. ما تخترعش جواب.
2 - المصدر قبل الرأي: أي معلومة، قول ليا المصدر. إلا كانت تخمين، قول تخمين.
3 - خطوة بخطوة: ما تعطينيش كلشي دقة وحدة. خطوة، نتأكد، عاد دوز.
4 - التحذير قبل الخطر: إلا طلبت شي حاجة فيها خطر قانوني أو مالي أو صحي عليا، حبسني وشرح ليا الخطر قبل ما تكمل.
5 - البديل قبل الرفض: إلا ما قدرتيش، عطيني بديل قانوني.
6 - التبسيط بلا تسطيح: شرح بالدارجة، ولكن ما تحيدش المعلومة المهمة.
7 - السؤال قبل التنفيذ: إلا كان طلبي غامض، سولني، ما تخمنش.
8 - الفعل قبل الكلام: ما تتيقش في شنو كيقول الكود، تيق في شنو كيدير بالصح. قبل ما تقول تم الحفظ ولا تم الإرسال، تأكد واش الفعل وقع بالصح. سول: شنو قال؟ شنو دار؟ واش الكلام كيساوي الفعل؟ إلا قال تم الحفظ وما كاين والو تحفظ، راه كيكذب عليا. حيد ديك الرسالة.

كيفاش تجاوبني:
- جاوبني بالدارجة المغربية، بسيطة.
- بدا بالخلاصة، عاد التفاصيل.
- إلا كان جوابك فيه كود، عطيني الكود كامل، واجد للنسخ.
- إلا كان فيه خطر، قول ليا الخطر في الأول، قبل الحل.

الأثر اللي بغيتو منك: ماشي كلام، ماشي كود كيبان زوين. بغيت أثر حقيقي: كود خدام، كيجيب قيمة، وكيحميني من الغلط.

واش قبلتي الميثاق؟ إلا قبلتيه، قول ليا: قبلت الميثاق، ونبداو.
"""
    st.text_area("نص الميثاق - كوبيه كامل", mithaq, height=520)

else:
    st.markdown('<h2>ميزان التحقق</h2>', unsafe_allow_html=True)
    st.markdown('<p>ملي الأداة تجاوبك، ما تلصقش غير الجملة. لصق الكود، ولصق الجملة اللي قالها ليك، باش الميزان يعرف القصة كاملة.</p>', unsafe_allow_html=True)

    # ===== الجزء الجديد - 1: الكود =====
    st.markdown('<h3>1 - لصق الكود اللي بغيتي تتحقق منو</h3>', unsafe_allow_html=True)
    st.markdown('<p>لصق هنا الكود كامل، اللي كتقول باللي كيدير شي حاجة - بحال كود الواتساب، ولا كود الحفظ.</p>', unsafe_allow_html=True)
    code_a_verifier = st.text_area("الكود - لصقو هنا", height=200, placeholder="مثال:\nif st.button('صيفط الواتساب'):\n    st.success('تم إرسال الواتساب بنجاح')")

    # ===== الجزء الجديد - 2: الجملة =====
    st.markdown('<h3>2 - لصق الجملة اللي قالها ليك الكود</h3>', unsafe_allow_html=True)
    st.markdown('<p>لصق هنا النتيجة اللي بانات ليك في الشاشة - بحال: تم إرسال الواتساب لأحمد بنجاح</p>', unsafe_allow_html=True)
    reponse = st.text_area("جملة التحقق - لصقها هنا", height=100, placeholder="مثال: تم إرسال الواتساب لأحمد بنجاح")

    if st.button("وزن ليا هاد الجواب"):
        # إلا ما كاينش الكود ولا الجملة، نحبسوه
        if not code_a_verifier and not reponse:
            st.warning("لصق الكود والجملة الأول")
        elif not code_a_verifier:
            st.warning("نسيتي الكود. لصق الكود اللي بغيتي تتحقق منو في الخانة الأولى.")
        elif not reponse:
            st.warning("نسيتي الجملة. لصق الجملة اللي قالها ليك الكود في الخانة الثانية.")
        else:
            # القاعدة 8 - نجمعو الكود + الجملة، باش الفحص يكون على القصة كاملة
            # هكا الميزان كيعرف شنو هو التطبيق، وشنو قال
            texte_complet = code_a_verifier + "\n" + reponse
            reponse_nqi = texte_complet.replace("'", "").replace('"', "").replace("’", "").strip()

            score = 100
            alertes = []
            if "متأكد 100" in reponse_nqi and "مصدر" not in reponse_nqi:
                score -= 20
                alertes.append("كيقول أكيد بلا مصدر - هادي علامة ديال التخمين")
            if "بالتأكيد" in reponse_nqi:
                score -= 10
                alertes.append("كلمة بالتأكيد بلا دليل - طلب منو المصدر")
            if len(reponse_nqi) > 2000 and "خطوة" not in reponse_nqi:
                score -= 15
                alertes.append("جواب طويل بلا خطوات - ممكن يكون فيه غلط مخبي")
            if "http" not in reponse_nqi and "مصدر" not in reponse_nqi and len(reponse_nqi) > 500:
                score -= 20
                alertes.append("ما كاينش مصدر - سولو: منين جبتي هاد المعلومة؟")
            if "ما عرفتش" in reponse_nqi or "ممكن" in reponse_nqi:
                score += 10
                alertes.append("قال ما عرفتش ولا ممكن - هادي علامة ديال الصدق، مزيان")

            # ===== القاعدة 8 - الفعل قبل الكلام =====
            kalam_kadab = ["تم حفظ", "تم الحفظ", "تم ارسال", "تم الإرسال", "تم الدفع", "تم بنجاح", "تم حفظ الزبون", "تم ارسال الرسالة", "تم ارسال الواتساب"]
            lqa_kadab = any(k in reponse_nqi for k in kalam_kadab)

            # الدليل: واش الكود فيه فعل حقيقي؟ ولا غير كلام؟
            dalil_fi3l = ["session_state", "append", "open(", "write", "save", "insert", "ملف", "قاعدة بيانات", "تحقق", "نتأكد", "تجربة", "جرب", "wa.me", "whatsapp", "api", "requests.post", "send"]
            kayn_dalil = any(d in reponse_nqi for d in dalil_fi3l)

            if lqa_kadab and not kayn_dalil:
                score -= 30
                alertes.append("القاعدة 8 - خطر: كيقول تم الحفظ ولا تم الإرسال، ولكن الكود اللي لصقتي ما فيه حتى فعل حقيقي. غير كلام. سولو: فين هو الكود ديال الحفظ ولا الإرسال؟")
            elif lqa_kadab and kayn_dalil:
                alertes.append("القاعدة 8 - مزيان: قال تم الحفظ، وكاين دليل على الفعل في الكود. تأكد بالتجربة قبل ما تتيق 100%.")

            score = max(0, min(100, score))
            st.progress(score/100)
            st.write(f"نقطة الثقة: {score} من 100")
            if score >= 80:
                st.success("الجواب باين مزيان. جربو بتجربة صغيرة قبل ما تتيق فيه 100%.")
            elif score >= 60:
                st.warning("الجواب فيه شك. سول الأداة: منين جبتي هاد المعلومة؟ واش متأكد؟")
            else:
                st.error("الجواب فيه خطر. ما تتيقش فيه.")
            for a in alertes:
                st.write(a)
st.caption("الميثاق - IMPACT v1.1 | عهدك مع أي أداة ذكاء اصطناعي | 8 ديال القواعد")
