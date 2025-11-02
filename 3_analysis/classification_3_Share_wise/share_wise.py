import streamlit as st
import pandas as pd
import numpy as np

# ========== Load Data ==========
DATA_PATH = r"C:\CSIT\Abhi Semester 7\project\0 Program\3_analysis\classification_3_Share_wise\final_clean_data_share_wise.csv"
df = pd.read_csv(DATA_PATH)
df.dropna(inplace=True)

# ========== Filter by Company ==========
companies = df['Company'].unique()
selected_company = st.selectbox("Select a Stock/Company", companies)
data = df[df['Company'] == selected_company].copy()

st.write("Filtered Data Sample:", data.head())

# ========== Technical Indicators ==========

def compute_macd(close, short=12, long=26, signal=9):
    ema_short = close.ewm(span=short, adjust=False).mean()
    ema_long = close.ewm(span=long, adjust=False).mean()
    macd_line = ema_short - ema_long
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    return macd_line

def compute_rsi(close, period=14):
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def compute_stochastic_oscillator(high, low, close, k_period=14):
    lowest_low = low.rolling(window=k_period).min()
    highest_high = high.rolling(window=k_period).max()
    so_k = 100 * ((close - lowest_low) / (highest_high - lowest_low))
    return so_k

def compute_ma(close, window=14):
    return close.rolling(window=window).mean()

def compute_ema(close, span=14):
    return close.ewm(span=span, adjust=False).mean()

def compute_roc(close, period=12):
    return ((close - close.shift(period)) / close.shift(period)) * 100

def compute_volume_trading(amount):
    return amount  # Using amount directly

# ========== Feature Engineering ==========
data['MACD'] = compute_macd(data['Close'])
data['RSI'] = compute_rsi(data['Close'])
data['SO'] = compute_stochastic_oscillator(data['High'], data['Low'], data['Close'])
data['MA'] = compute_ma(data['Close'])
data['EMA'] = compute_ema(data['Close'])
data['ROC'] = compute_roc(data['Close'])
data['VT'] = compute_volume_trading(data['amount'])

# Drop NaN values from indicator calculations
data.dropna(inplace=True)

# ========== Create Labels ==========
data['Target'] = np.where(data['Close'].shift(-1) > data['Close'], 1, 0)

# ========== Feature Matrix ==========
features = ['MACD', 'RSI', 'SO', 'MA', 'EMA', 'ROC', 'VT']
X = data[features].values
y = data['Target'].values

# ========== MinMaxScaler from Scratch ==========
def minmax_scaler(X):
    min_vals = np.min(X, axis=0)
    max_vals = np.max(X, axis=0)
    scaled = (X - min_vals) / (max_vals - min_vals + 1e-10)
    return scaled

X_scaled = minmax_scaler(X)

# ========== Train/Test Split ==========
split = int(0.8 * len(X_scaled))
X_train, X_test = X_scaled[:split], X_scaled[split:]
y_train, y_test = y[:split], y[split:]

# ========== Logistic Regression from Scratch ==========
class LogisticRegressionScratch:
    def __init__(self, lr=0.01, n_iter=1000):
        self.lr = lr
        self.n_iter = n_iter

    def sigmoid(self, z):
        return 1 / (1 + np.exp(-z))

    def fit(self, X, y):
        self.theta = np.zeros(X.shape[1])
        self.bias = 0

        for _ in range(self.n_iter):
            linear = np.dot(X, self.theta) + self.bias
            y_pred = self.sigmoid(linear)

            error = y_pred - y
            dw = np.dot(X.T, error) / len(y)
            db = np.sum(error) / len(y)

            self.theta -= self.lr * dw
            self.bias -= self.lr * db

    def predict(self, X):
        linear = np.dot(X, self.theta) + self.bias
        y_pred = self.sigmoid(linear)
        return [1 if i > 0.5 else 0 for i in y_pred]

# ========== Train Model ==========
model = LogisticRegressionScratch(lr=0.01, n_iter=1000)
model.fit(X_train, y_train)
preds = model.predict(X_test)

# ========== Confusion Matrix  ==========
def confusion_matrix(y_true, y_pred):
    TP = FP = TN = FN = 0
    for yt, yp in zip(y_true, y_pred):
        if yt == 1 and yp == 1:
            TP += 1
        elif yt == 0 and yp == 0:
            TN += 1
        elif yt == 0 and yp == 1:
            FP += 1
        elif yt == 1 and yp == 0:
            FN += 1
    return np.array([[TP, FN], [FP, TN]])

cm = confusion_matrix(y_test, preds)

# ========== Show Results ==========
st.subheader("Model Evaluation")

st.write("Confusion Matrix:")
st.write(pd.DataFrame(cm,
                      index=["Actual 1 (Up)", "Actual 0 (Down)"],
                      columns=["Predicted 1 (Up)", "Predicted 0 (Down)"]))

accuracy = (cm[0][0] + cm[1][1]) / np.sum(cm)
st.write(f"Accuracy: {accuracy:.2f}")

