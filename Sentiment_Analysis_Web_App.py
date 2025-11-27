import streamlit as st
from textblob import TextBlob
from googletrans import Translator
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="Sentiment Analysis Ultimate Pro+", layout="wide")
st.title("🚀 Sentiment Analysis Ultimate Pro+ - Word-Level & Multi-language")

# ---------- SIDEBAR ----------
st.sidebar.header("Options")
mode = st.sidebar.selectbox("Input Mode", ["Text Input", "Upload File (.txt)"])
show_plot = st.sidebar.checkbox("Show Sentiment Plot", value=True)
export_csv = st.sidebar.checkbox("Export results to Excel", value=True)
language = st.sidebar.selectbox("Language of Input", ["English", "Vietnamese", "Spanish", "Chinese", "German", "Dutch", "French", "Thai"])

# ---------- INPUT ----------
texts = []
if mode == "Text Input":
    text = st.text_area("Enter text here (multiple paragraphs supported):")
    if text:
        texts = [para.strip() for para in text.split("\n\n") if para.strip()]
else:
    uploaded_file = st.file_uploader("Upload a .txt file", type=["txt"])
    if uploaded_file:
        content = uploaded_file.read().decode("utf-8")
        texts = [para.strip() for para in content.split("\n\n") if para.strip()]

# ---------- TRANSLATE & ANALYSIS ----------
if texts:
    translator = Translator()
    df_rows = []
    overall_polarity_list = []

    st.subheader("Paragraph & Word-Level Sentiment Analysis")

    for para_idx, para in enumerate(texts):
        # Translate paragraph if needed
        if language != "English":
            try:
                translated = translator.translate(para, src=language.lower(), dest="en").text
            except:
                translated = para
        else:
            translated = para

        # Word-level analysis
        words = re.findall(r'\w+|\S', para)
        word_analysis = []
        para_polarity_list = []

        for word in words:
            # Translate each word if not English
            if language != "English":
                try:
                    word_en = translator.translate(word, src=language.lower(), dest="en").text
                except:
                    word_en = word
            else:
                word_en = word

            polarity = TextBlob(word_en).sentiment.polarity
            para_polarity_list.append(polarity)

            if polarity > 0.1:
                sentiment = "Positive"
                color = "#2ecc71"
            elif polarity < -0.1:
                sentiment = "Negative"
                color = "#e74c3c"
            else:
                sentiment = "Neutral"
                color = "#95a5a6"

            word_analysis.append((word, sentiment, color, polarity))
            df_rows.append({"Paragraph": para_idx+1, "Word": word, "Sentiment": sentiment, "Polarity": polarity, "Color": color})

        # Highlight paragraph
        highlighted_para = "".join([f"<span style='color:{c}'>{w}</span>" for w, s, c, p in word_analysis])
        st.markdown(f"**Paragraph {para_idx+1}:** {highlighted_para}", unsafe_allow_html=True)

        # Paragraph average polarity
        para_avg = sum(para_polarity_list)/len(para_polarity_list)
        overall_polarity_list.append(para_avg)
        st.markdown(f"*Average Polarity for Paragraph {para_idx+1}: {para_avg:.2f}*")

    # ---------- OVERALL FILE POLARITY ----------
    overall_avg = sum(overall_polarity_list)/len(overall_polarity_list)
    st.subheader(f"Overall File Average Polarity: {overall_avg:.2f}")
    if overall_avg > 0.1:
        overall_sentiment = "Positive 😊"
        overall_color = "#2ecc71"
    elif overall_avg < -0.1:
        overall_sentiment = "Negative 😞"
        overall_color = "#e74c3c"
    else:
        overall_sentiment = "Neutral 😐"
        overall_color = "#95a5a6"
    st.markdown(f"Overall Sentiment: <span style='color:{overall_color}; font-size:20px'>{overall_sentiment}</span>", unsafe_allow_html=True)

    # ---------- DATAFRAME ----------
    df = pd.DataFrame(df_rows)
    st.subheader("Word-Level DataFrame")
    st.dataframe(df.drop(columns=["Color"]), height=300)

    # ---------- PLOT ----------
    if show_plot:
        st.subheader("Sentiment Distribution by Paragraph")
        plt.figure(figsize=(10,5))
        sns.countplot(x="Sentiment", data=df, palette={"Positive":"#2ecc71","Negative":"#e74c3c","Neutral":"#95a5a6"})
        plt.title("Word-Level Sentiment Counts")
        st.pyplot(plt.gcf())

    # ---------- EXPORT EXCEL ----------
    if export_csv:
        export_file = "sentiment_pro_plus.xlsx"
        df.to_excel(export_file, index=False)
        st.success(f"Results exported to `{export_file}`")
