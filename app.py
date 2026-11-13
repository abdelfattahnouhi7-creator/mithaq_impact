import streamlit as st

st.set_page_config(page_title="الميثاق", page_icon="📜", layout="wide")

# ===== إصلاح العربية - RTL قوي =====
st.markdown("""
<style>
    .stApp, .main, .block-container {
        direction: rtl !important;
        text-align: right !important;
    }
    h1, h2, h3, p, div, span, label, li {
        direction: rtl !important;
        text-align: right !important;
        unicode-bidi: embed !important;
        line-height: 1.9 !important;
        font-family: 'Segoe UI', Tahoma, Arial, sans-serif !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        direction: rtl !important;
        flex-direction: row-reverse !important;
    }
    .stTabs [data-baseweb="tab"] {
        direction: rtl !important;
    }
    .stTextArea textarea, .stTextInput input {
        direction: rtl !important;
        text-align: right !important;
        font-size: 16px !important;
        line-height: 1.9 !important;
    }
    .stButton > button {
        direction: rtl !important;
        width: 100% !important;
    }
    .stExpander {
        direction: rtl !important;
        text-align: right !important;
    }
    /* الكلمات الإنجليزية بوحدها - باش ما تقلبش الجملة */
    .en {
        direction: ltr !important;
        display: inline-block !important;
        unicode-bidi: isolate !important;
        text-align: left !important;
    }
</style>
""", unsafe_allow_html=True)

# ===== العنوان - سطر عربي + سطر إنجليزي، ماشي مخلطين =====
st.markdown('<h1 style="text-align:right;">📜 الميثاق</h1>', unsafe_allow_html=True)
st.markdown('<p style="direction:ltr; text-align:right; font-size:18px; color:#888;">IMPACT</p>', unsafe_allow_html=True)
st.markdown('<p style="text-align:right;">ماشي قواعد. ماشي نصائح. هو عهد بيني وبين الذكاء الاصطناعي.</p>', unsafe_allow_html=True)
st.markdown('<p style="text-align:right;">باش يكون عندو أثر حقيقي، بلا ضرر.</p>', unsafe_allow_html=True)

st.markdown('<h3 style="text-align:right;">شنو هو الميثاق؟</h3>', unsafe_allow_html=True)
st.markdown('<p style="text-align:right;">هو العهد اللي كتعطيه لأي أداة ذكاء اصطناعي قبل ما تبدا تخدم معاه. ملي كيقبلو، كيولي خدام معاك بهاد القواعد، وما يقدرش يخرج عليهم.</p>', unsafe_allow_html=True)

REGLES = [
    {"titre": "1 - الصدق قبل السرعة", "regle": "إلا ما عرفتيش، قول ما عرفتش. ما تخترعش جواب باش تبان عارف.", "pourquoi": "الذكاء الاصطناعي كيكذب ملي كيبغي يرضيك. هاد القاعدة كتحبسو.", "danger": "معلومات خاطئة كتخسر ليك فلوس ووقت"},
    {"titre": "2 - المصدر قبل الرأي", "regle": "أي معلومة تعطيها ليا، قول ليا المصدر ديالها. إلا كانت تخمين، قول ليا تخمين.", "pourquoi": "باش نعرف واش نتيق فيك ولا لا.", "danger": "كتاخد تخمين على أساس حقيقة"},
    {"titre": "3 - خطوة بخطوة", "regle": "ما تعطينيش الحل الكامل دقة وحدة. عطيني خطوة، نتأكد منها، عاد دوز للي من بعدها.", "pourquoi": "إلا غلطتي في الأول، كلشي اللي من بعد غادي يكون غلط.", "danger": "كود طويل فيه غلط، وما كتعرفش فين هو"},
    {"titre": "4 - التحذير قبل الخطر", "regle": "إلا طلبت منك شي حاجة فيها خطر قانوني أو مالي أو صحي عليا، حبسني وقول ليا شنو هو الخطر قبل ما تكمل.", "pourquoi": "انت هو الحارس ديالي، ماشي غير المنفذ.", "danger": "كتدخل في طرق ملتوية بلا ما تعرف"},
    {"titre": "5 - البديل قبل الرفض", "regle": "إلا ما قدرتيش تدير شي حاجة، ما تقولش غير لا. عطيني بديل قانوني وصحيح.", "pourquoi": "الرفض بلا بديل كيوقف الخدمة.", "danger": "كتحبس وما كتكملش"},
    {"titre": "6 - التبسيط بلا تسطيح", "regle": "شرح ليا بالدارجة، بسيطة، ولكن ما تنقصش المعلومة المهمة.", "pourquoi": "التبسيط الزايد كيحيد المعلومة اللي كتحميني.", "danger": "كتفهم نص الحقيقة"},
    {"titre": "7 - السؤال قبل التنفيذ", "regle": "إلا كان الطلب ديالي غامض، سولني سؤال واحد، ما تخمنش شنو بغيت.", "pourquoi": "تخمينك غادي يضيع ليا ساعة.", "danger": "كود غالط، خاصك تعاودو من الأول"},
]

tab1, tab2, tab3 = st.tabs(["القواعد", "نص الميثاق", "ميزان التحقق"])

with tab1:
    st.markdown('<h3 style="text-align:right;">القواعد الـ 7</h3>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:right;">هادو هما القواعد اللي خاصك تعطيهم لأي أداة ذكاء اصطناعي.</p>', unsafe_allow_html=True)
    for r in REGLES:
        with st.expander(r["titre"]):
            st.write(f"القاعدة - {r['regle']}")
            st.write(f"علاش - {r['pourquoi']}")
            st.error(f"إلا ما طبقتهاش، شنو غادي يوقع - {r['danger']}")

with tab2:
    st.markdown('<h3 style="text-align:right;">نص الميثاق - كوبيه ولصقو في أي أداة جديدة</h3>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:right;">1 - كوبي النص اللي تحت</p>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:right;">2 - حلو أي أداة ذكاء اصطناعي</p>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:right;">3 - لصقو في أول رسالة</p>', unsafe_allow_html=True)

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
    st.success("من دابا، أي أداة غادي تخدم معاك بهاد القواعد.")

with tab3:
    st.markdown('<h3 style="text-align:right;">ميزان التحقق</h3>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:right;">ملي الأداة تجاوبك، كوبي الجواب ديالها، ولصقو هنا.</p>', unsafe_allow_html=True)
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
            st.divider()
            st.write("الأسئلة اللي خاصك تسولها ملي تشك:")
            st.code("1 - منين جبتي هاد المعلومة؟\n2 - واش هادا تخمين ولا حقيقة؟\n3 - شنو هو الخطر إلا طبقت هادشي؟\n4 - عطيني بديل إلا كان هادشي غالط.")

st.caption("الميثاق - IMPACT v1.0 | عهدك مع أي أداة ذكاء اصطناعي")
