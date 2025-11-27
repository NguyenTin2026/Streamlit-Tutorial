import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, confusion_matrix
import joblib

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="ML Pro++ Dashboard", layout="wide")
st.title("🚀 ML Pro++ Ultimate Dashboard - Streamlit")

# ---------- SIDEBAR ----------
st.sidebar.header("Options")
model_choice = st.sidebar.selectbox("Select Model", ["RandomForest", "LogisticRegression", "SVM", "XGBoost", "KNN"])
target_column = st.sidebar.text_input("Target Column Name")
test_size = st.sidebar.slider("Test Size Fraction", 0.1, 0.5, 0.2)
upload_file = st.sidebar.file_uploader("Upload CSV Dataset", type=["csv"])

# ---------- DATA INPUT ----------
df = None
if upload_file:
    df = pd.read_csv(upload_file)
    st.subheader("Dataset Preview")
    st.dataframe(df.head())
elif st.checkbox("Use Sample Dataset"):
    df = pd.DataFrame({
        'Feature1': [1,2,3,4,5,6,7,8,9,10],
        'Feature2': [10,9,8,7,6,5,4,3,2,1],
        'Target': [0,1,0,1,0,1,0,1,0,1]
    })
    st.write("Sample Dataset:", df)

# ---------- EDA ----------
if df is not None:
    st.subheader("Interactive EDA")
    st.write(df.describe())

    # Feature distribution plot
    feature = st.selectbox("Select feature to visualize", [c for c in df.columns if c != target_column])
    fig = px.histogram(df, x=feature, color=target_column)
    st.plotly_chart(fig)

    # Correlation heatmap
    plt.figure(figsize=(6,4))
    sns.heatmap(df.corr(), annot=True, cmap="coolwarm")
    st.pyplot(plt.gcf())

    # Boxplot
    plt.figure(figsize=(6,4))
    sns.boxplot(x=target_column, y=feature, data=df)
    st.pyplot(plt.gcf())

# ---------- TRAIN MODEL ----------
if df is not None and target_column in df.columns:
    X = df.drop(columns=[target_column])
    y = df[target_column]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)

    # Select model
    if model_choice == "RandomForest":
        model = RandomForestClassifier(n_estimators=100, random_state=42)
    elif model_choice == "LogisticRegression":
        model = LogisticRegression(max_iter=500)
    elif model_choice == "SVM":
        model = SVC(probability=True)
    elif model_choice == "XGBoost":
        model = XGBClassifier(use_label_encoder=False, eval_metric='logloss')
    elif model_choice == "KNN":
        model = KNeighborsClassifier(n_neighbors=3)

    # Train
    model.fit(X_train, y_train)
    st.success(f"{model_choice} trained successfully!")

    # Predict
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    st.write(f"Accuracy on Test Set: {acc:.2f}")

    # Confusion matrix
    st.subheader("Confusion Matrix")
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(5,4))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues")
    st.pyplot(plt.gcf())

    # Feature importance (if supported)
    if hasattr(model, "feature_importances_"):
        st.subheader("Feature Importance")
        fi = pd.DataFrame({'Feature': X.columns, 'Importance': model.feature_importances_}).sort_values(by="Importance", ascending=False)
        st.bar_chart(fi.set_index('Feature'))

    # ---------- MANUAL PREDICTION ----------
    st.subheader("Manual Prediction")
    input_data = {}
    for col in X.columns:
        input_data[col] = st.number_input(f"{col}", value=float(X[col].mean()))

    if st.button("Predict"):
        input_df = pd.DataFrame([input_data])
        prediction = model.predict(input_df)[0]
        st.write(f"Predicted Target: {prediction}")

        if hasattr(model, "predict_proba"):
            st.write(f"Prediction Probabilities: {model.predict_proba(input_df)}")

    # ---------- EXPORT MODEL ----------
    if st.button("Export Trained Model"):
        joblib.dump(model, f"{model_choice}_pro_plus.pkl")
        st.success(f"Model saved as {model_choice}_pro_plus.pkl")

    # ---------- EXPORT PREDICTIONS ----------
    if st.button("Export Predictions on Test Set"):
        pred_df = X_test.copy()
        pred_df['Actual'] = y_test
        pred_df['Predicted'] = y_pred
        pred_df.to_excel("predictions_pro_plus.xlsx", index=False)
        st.success("Predictions exported to predictions_pro_plus.xlsx")
