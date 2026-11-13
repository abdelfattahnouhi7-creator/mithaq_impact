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
    st.markdown('<h2>القواعد الـ 7</h2>', unsafe_allow_html=True)
    st.markdown('<p>هادو هما القواعد اللي خاصك تعطيهم لأي أداة ذكاء اصطناعي.</p>', unsafe_allow_html=True)

    regles = [
        ("1 - الصدق قبل السرعة", "إلا ما عرفتيش، قول ما عرفتش. ما تخترعش جواب باش تبان عارف.", "الذكاء الاصطناعي كيكذب ملي كيبغي يرضيك. هاد القاعدة كتحبسو.", "معلومات خاطئة كتخسر ليك فلوس ووقت"),
        ("2 - المصدر قبل الرأي", "أي معلومة تعطيها ليا، قول ليا المصدر ديالها. إلا كانت تخمين، قول ليا تخمين.", "باش نعرف واش نتيق فيك ولا لا.", "كتاخد تخمين على أساس حقيقة"),
        ("3 - خطوة بخطوة", "ما تعطينيش الحل الكامل دقة وحدة. عطيني خطوة، نتأكد منها، عاد دوز للي من بعدها.", "إلا غلطتي في الأول، كلشي اللي من بعد غادي يكون غلط.", "كود طويل فيه غلط، وما كتعرفش فين هو"),
        ("4 - التحذير قبل الخطر", "إلا طلبت منك شي حاجة فيها خطر قانوني أو مالي أو صحي عليا، حبسني وقول ليا شنو هو الخطر قبل ما تكمل.", "انت هو الحارس ديالي، ماشي غير المنفذ.", "كتدخل في طرق ملتوية بلا ما تعرف"),
        ("5 - البديل قبل الرفض", "إلا ما قدرتيش تدير شي حاجة، ما تقولش غير لا. عطيني بديل قانوني وصحيح.", "الرفض بلا بديل كيوقف الخدمة.", "كتحبس وما كتكملش"),
        ("6 - التبسيط بلا تسطيح", "شرح ليا بالدارجة، بسيطة، ولكن ما تنقصش المعلومة المهمة.", "التبسيط الزايد كيحيد المعلومة اللي كتحميني.", "كتفهم نص الحقيقة"),
        ("7 - السؤال قبل التنفيذ", "إلا كان الطلب ديالي غامض، سولني سؤال واحد، ما تخمنش شنو بغيت.", "تخمينك غادي يضيع ليا ساعة.", "كود غالط، خاصك تعاودو من الأول"),
    ]

    for titre, regle, pourquoi, danger in regles:
        st.markdown(f"""
        <div class="card">
            <div class="card-title">{titre}</div>
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

كيفاش تجاوبني:
- جاوبني بالدارجة المغربية، بسيطة.
- بدا بالخلاصة، عاد التفاصيل.
- إلا كان جوابك فيه كود، عطيني الكود كامل، واجد للنسخ.
- إلا كان فيه خطر، قول ليا الخطر في الأول، قبل الحل.

الأثر اللي بغيتو منك: ماشي كلام، ماشي كود كيبان زوين. بغيت أثر حقيقي: كود خدام، كيجيب قيمة، وكيحميني من الغلط.

واش قبلتي الميثاق؟ إلا قبلتيه، قول ليا: قبلت الميثاق، ونبداو.
"""
    st.text_area("نص الميثاق - كوبيه كامل", mithaq, height=450)

else:
    st.markdown('<h2>ميزان التحقق</h2>', unsafe_allow_html=True)
    st.markdown('<p>ملي الأداة تجاوبك، كوبي الجواب ديالها، ولصقو هنا.</p>', unsafe_allow_html=True)
    reponse = st.text_area("لصق جواب الأداة هنا", height=200, placeholder="لصق هنا الجواب...")
    if st.button("وزن ليا هاد الجواب"):
        if not reponse:
            st.warning("لصق الجواب الأول")
        else:
            score = 100
            alertes = []
            if "متأكد 100" in reponse and "مصدر" not in reponse:
                score -= 20
                alertes.append("كيقول أكيد بلا مصدر - هادي علامة ديال التخمين")
            if "بالتأكيد" in reponse:
                score -= 10
                alertes.append("كلمة بالتأكيد بلا دليل - طلب منو المصدر")
            if len(reponse) > 2000 and "خطوة" not in reponse:
                score -= 15
                alertes.append("جواب طويل بلا خطوات - ممكن يكون فيه غلط مخبي")
            if "http" not in reponse and "مصدر" not in reponse and len(reponse) > 500:
                score -= 20
                alertes.append("ما كاينش مصدر - سولو: منين جبتي هاد المعلومة؟")
            if "ما عرفتش" in reponse or "ممكن" in reponse:
                score += 10
                alertes.append("قال ما عرفتش ولا ممكن - هادي علامة ديال الصدق، مزيان")
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

st.caption("الميثاق - IMPACT v1.0 | عهدك مع أي أداة ذكاء اصطناعي")
