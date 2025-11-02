import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# -------------------------------
# Technical Indicators
# -------------------------------
def sma(series, period=14):
    return series.rolling(window=period, min_periods=period).mean()

def ema(series, period=14):
    return series.ewm(span=period, adjust=False).mean()

def rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.ewm(com=period-1, min_periods=period).mean()
    avg_loss = loss.ewm(com=period-1, min_periods=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def macd(series, short=12, long=26, signal=9):
    ema_short = ema(series, short)
    ema_long = ema(series, long)
    macd_line = ema_short - ema_long
    signal_line = ema(macd_line, signal)
    hist = macd_line - signal_line
    return macd_line, signal_line, hist

def stochastic_oscillator(df, period=14):
    low_min = df['Close'].rolling(window=period).min()
    high_max = df['Close'].rolling(window=period).max()
    return 100 * (df['Close'] - low_min) / (high_max - low_min)

def roc(series, period=12):
    return (series.diff(period) / series.shift(period)) * 100

def volatility(series, period=14):
    return series.pct_change().rolling(window=period).std() * np.sqrt(period)

# -------------------------------
# Confusion Matrix
# -------------------------------
def confusion_matrix(y_true, y_pred):
    TP = np.sum((y_true == 1) & (y_pred == 1))
    TN = np.sum((y_true == 0) & (y_pred == 0))
    FP = np.sum((y_true == 0) & (y_pred == 1))
    FN = np.sum((y_true == 1) & (y_pred == 0))
    return {"TP": TP, "TN": TN, "FP": FP, "FN": FN}

# -------------------------------
# Logistic Regression from scratch
# -------------------------------
class LogisticRegression:
    def __init__(self, lr=0.01, epochs=1000):
        self.lr = lr
        self.epochs = epochs
        self.W = None
        self.b = 0

    def sigmoid(self, z):
        return 1 / (1 + np.exp(-z))

    def fit(self, X, y):
        m, n = X.shape
        self.W = np.zeros(n)
        self.b = 0
        for _ in range(self.epochs):
            linear = np.dot(X, self.W) + self.b
            y_pred = self.sigmoid(linear)
            dw = (1/m) * np.dot(X.T, (y_pred - y))
            db = (1/m) * np.sum(y_pred - y)
            self.W -= self.lr * dw
            self.b -= self.lr * db

    def predict(self, X, threshold=0.5):
        linear = np.dot(X, self.W) + self.b
        probs = self.sigmoid(linear)
        return (probs >= threshold).astype(int), probs

    def evaluate(self, y_true, y_pred):
        TP = np.sum((y_true == 1) & (y_pred == 1))
        TN = np.sum((y_true == 0) & (y_pred == 0))
        FP = np.sum((y_true == 0) & (y_pred == 1))
        FN = np.sum((y_true == 1) & (y_pred == 0))
        accuracy = (TP + TN) / (TP + TN + FP + FN)
        recall = TP / (TP + FN) if (TP + FN) > 0 else 0
        precision = TP / (TP + FP) if (TP + FP) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        return accuracy, recall, precision, f1

# -------------------------------
# Load and clean CSV
# -------------------------------
def load_and_clean_csv(path):
    df = pd.read_csv(path)
    numeric_cols = ["numTrans", "tradedShares", "amount", "Close", "Change", "Percentage change"]
    for col in numeric_cols:
        df[col] = df[col].astype(str).str.replace(",", "", regex=True)
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df.dropna(subset=numeric_cols, inplace=True)
    return df

# -------------------------------
# Streamlit App
# -------------------------------
st.title("📈 NEPSE Indicators + Logistic Regression (Balanced Train/Test)")

file_path = "C:\\CSIT\\Abhi Semester 7\\project\\0 Program\\3_analysis\\classification_2\\final_clean_data.csv"
df = load_and_clean_csv(file_path)

# Sidebar for indicator params
st.sidebar.header("⚙️ Indicator Settings")
ma_period = st.sidebar.number_input("MA Period", 5, 200, 14)
ema_period = st.sidebar.number_input("EMA Period", 5, 200, 14)
rsi_period = st.sidebar.number_input("RSI Period", 5, 200, 14)
macd_short = st.sidebar.number_input("MACD Short EMA", 5, 50, 12)
macd_long = st.sidebar.number_input("MACD Long EMA", 10, 100, 26)
macd_signal = st.sidebar.number_input("MACD Signal", 5, 50, 9)
so_period = st.sidebar.number_input("Stochastic Oscillator Period", 5, 50, 14)
roc_period = st.sidebar.number_input("ROC Period", 5, 50, 12)
vt_period = st.sidebar.number_input("Volatility Period", 5, 50, 14)

# Threshold slider
threshold = st.sidebar.slider("Prediction Threshold", 0.1, 0.9, 0.5)

# Calculate indicators
df["MA"] = sma(df["Close"], ma_period)
df["EMA"] = ema(df["Close"], ema_period)
df["RSI"] = rsi(df["Close"], rsi_period)
df["MACD"], df["Signal"], df["Hist"] = macd(df["Close"], macd_short, macd_long, macd_signal)
# df["SO"] = stochastic_oscillator(df, so_period)
df["ROC"] = roc(df["Close"], roc_period)
df["VT"] = volatility(df["Close"], vt_period)

st.subheader("Processed Data (last 20 rows)")
st.dataframe(df.tail(20))

# -------------------------------
# Prepare logistic regression data
# -------------------------------
train_df = df.dropna(subset=["MA","EMA","RSI","MACD","ROC","VT","outcome"])
X_all = train_df[["MA","EMA","RSI","MACD","ROC","VT"]].values
y_all = train_df["outcome"].astype(str).str.contains("1").astype(int).values

# Manual min-max normalization
X_min = X_all.min(axis=0)
X_max = X_all.max(axis=0)
X_all = (X_all - X_min) / (X_max - X_min + 1e-8)

# Balance dataset
ones_idx = np.where(y_all==1)[0]
zeros_idx = np.where(y_all==0)[0]
min_len = min(len(ones_idx), len(zeros_idx))
balanced_idx = np.concatenate([ones_idx[:min_len], zeros_idx[:min_len]])
X_all = X_all[balanced_idx]
y_all = y_all[balanced_idx]

# Shuffle
shuffle_idx = np.random.permutation(len(X_all))
X_all, y_all = X_all[shuffle_idx], y_all[shuffle_idx]

# Train/test split
split_idx = int(0.7 * len(X_all))
X_train, X_test = X_all[:split_idx], X_all[split_idx:]
y_train, y_test = y_all[:split_idx], y_all[split_idx:]

# Train logistic regression
model = LogisticRegression(lr=0.01, epochs=5000)
model.fit(X_train, y_train)

# Predictions
y_train_pred, _ = model.predict(X_train, threshold)
y_test_pred, _ = model.predict(X_test, threshold)

# Evaluate
train_acc, train_rec, train_prec, train_f1 = model.evaluate(y_train, y_train_pred)
test_acc, test_rec, test_prec, test_f1 = model.evaluate(y_test, y_test_pred)

st.subheader("Logistic Regression Metrics")
st.write("### Training Set")
st.write(f"Accuracy: {train_acc*100:.2f}% | Recall: {train_rec:.4f} | Precision: {train_prec:.4f} | F1: {train_f1:.4f}")
st.write("### Testing Set")
st.write(f"Accuracy: {test_acc*100:.2f}% | Recall: {test_rec:.4f} | Precision: {test_prec:.4f} | F1: {test_f1:.4f}")

# Confusion matrices
cm_train = confusion_matrix(y_train, y_train_pred)
cm_test = confusion_matrix(y_test, y_test_pred)

# st.subheader("Confusion Matrix - Training Set")
# st.write(f"TP: {cm_train['TP']} | FP: {cm_train['FP']}")
# st.write(f"FN: {cm_train['FN']} | TN: {cm_train['TN']}")

st.subheader("Confusion Matrix - Testing Set")
st.write(f"TP: {cm_test['TP']} | FP: {cm_test['FP']}")
st.write(f"FN: {cm_test['FN']} | TN: {cm_test['TN']}")

# Predicted vs actual tables
results_train = pd.DataFrame({"Actual": y_train, "Predicted": y_train_pred})
results_test = pd.DataFrame({"Actual": y_test, "Predicted": y_test_pred})

# st.subheader("Predicted vs Actual")
# st.write("### Training Set (last 20 rows)")
st.dataframe(results_train.tail(20))
st.write("### Testing Set (last 20 rows)")
st.dataframe(results_test.tail(20))

# -------------------------------
# Plots
# -------------------------------
st.subheader("Price with MA & EMA")
fig, ax = plt.subplots(figsize=(10,5))
ax.plot(df["Date"], df["Close"], label="Close", color="black")
ax.plot(df["Date"], df["MA"], label=f"MA({ma_period})", color="blue")
ax.plot(df["Date"], df["EMA"], label=f"EMA({ema_period})", color="red")
ax.legend()
st.pyplot(fig)

st.subheader("📉 MACD")
fig, ax = plt.subplots(figsize=(10,5))
ax.plot(df["Date"], df["MACD"], label="MACD", color="green")
ax.plot(df["Date"], df["Signal"], label="Signal", color="red")
ax.bar(df["Date"], df["Hist"], label="Histogram", color="grey")
ax.legend()
st.pyplot(fig)

st.subheader("📉 RSI")
fig, ax = plt.subplots(figsize=(10,5))
ax.plot(df["Date"], df["RSI"], label="RSI", color="purple")
ax.axhline(70, linestyle="--", color="red")
ax.axhline(30, linestyle="--", color="green")
ax.legend()
st.pyplot(fig)

st.success("✅ Indicators + Balanced Logistic Regression completed with normalization and threshold control.")
