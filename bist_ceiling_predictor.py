import pandas as pd
import numpy as np
import yfinance as yf
from ta.momentum import RSIIndicator, StochasticOscillator, WilliamsRIndicator
from ta.trend import MACD, CCIIndicator, ADXIndicator, EMAIndicator, SMAIndicator
from ta.volatility import BollingerBands
from ta.volume import OnBalanceVolumeIndicator
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings("ignore")

def load_symbols(filename="bist_symbols.csv", min_count=5):
    """
    CSV'den sembol yükler. Örnek dosya:
    symbol
    AKBNK.IS
    THYAO.IS
    SISE.IS
    GARAN.IS
    ASELS.IS
    """
    try:
        df = pd.read_csv(filename)
        syms = df["symbol"].unique().tolist()
        if len(syms) < min_count:
            print(f"Uyarı: {filename} az sayıda sembol içeriyor.")
        return syms
    except Exception as e:
        print(f"{filename} bulunamadı, örnek birkaç sembol ile devam ediliyor.")
        return ["AKBNK.IS", "THYAO.IS", "SISE.IS", "GARAN.IS", "ASELS.IS", "EUHOL.IS", "KRGYO.IS"]

def get_data(symbol, start, end):
    try:
        data = yf.download(symbol, start=start, end=end, progress=False)
        data = data.dropna()
        return data
    except Exception as e:
        print(f"{symbol} için veri çekilemedi: {e}")
        return pd.DataFrame()

def add_technical_indicators(df):
    if df.empty: return df
    df['rsi'] = RSIIndicator(df['Close']).rsi()
    df['macd'] = MACD(df['Close']).macd()
    df['stoch'] = StochasticOscillator(df['High'], df['Low'], df['Close']).stoch()
    df['cci'] = CCIIndicator(df['High'], df['Low'], df['Close']).cci()
    df['adx'] = ADXIndicator(df['High'], df['Low'], df['Close']).adx()
    bb = BollingerBands(df['Close'])
    df['bb_high'] = bb.bollinger_hband()
    df['bb_low'] = bb.bollinger_lband()
    df['obv'] = OnBalanceVolumeIndicator(df['Close'], df['Volume']).on_balance_volume()
    df['ema_10'] = EMAIndicator(df['Close'], window=10).ema_indicator()
    df['sma_10'] = SMAIndicator(df['Close'], window=10).sma_indicator()
    df['sma_20'] = SMAIndicator(df['Close'], window=20).sma_indicator()
    df['sma_50'] = SMAIndicator(df['Close'], window=50).sma_indicator()
    df['sma_200'] = SMAIndicator(df['Close'], window=200).sma_indicator()
    df['williams_r'] = WilliamsRIndicator(df['High'], df['Low'], df['Close']).williams_r()
    # Golden Cross: 50 günlük SMA, 200 günlük SMA'nın üstüne çıktı mı
    df['golden_cross'] = (df['sma_50'] > df['sma_200']).astype(int)
    # Kesişim anı (bugün 50>200 ve dün <=200 ise yeni golden cross)
    df['golden_cross_signal'] = ((df['sma_50'] > df['sma_200']) & (df['sma_50'].shift(1) <= df['sma_200'].shift(1))).astype(int)
    return df

def mark_ceiling_days(df):
    df = df.copy()
    df['ceiling'] = False
    for i in range(1, len(df)):
        prev_close = df['Close'].iloc[i-1]
        tavan = round(prev_close * 1.10, 2)
        # BIST'te tavan fiyat küsuratı virgül sonrası 2 hane
        if abs(df['High'].iloc[i] - tavan) < 0.02:
            df.loc[df.index[i], 'ceiling'] = True
    return df

def mark_speculative(df):
    # Spekülatif tavan: Ani yüksek hacim + ani fiyat değişimi + düşük ortalama hacim
    df['volume_change'] = df['Volume'].pct_change().fillna(0)
    df['price_jump'] = df['Close'].pct_change().fillna(0)
    avg_volume = df['Volume'].rolling(window=20).mean()
    df['low_volume'] = (avg_volume < avg_volume.quantile(0.25)).astype(int)
    # Spekülatif: ani hacim patlaması, ani fiyat değişimi, düşük hacim tabanı
    df['speculative'] = ((df['volume_change'] > 1) & (df['price_jump'] > 0.09) & (df['low_volume'] == 1)).astype(int)
    return df

def create_feature_label_df(df):
    feat_cols = [
        'rsi', 'macd', 'stoch', 'cci', 'adx', 'bb_high', 'bb_low', 'obv', 'ema_10', 'sma_10', 'sma_20',
        'sma_50', 'sma_200', 'williams_r', 'golden_cross', 'golden_cross_signal',
        'volume_change', 'price_jump', 'low_volume', 'speculative'
    ]
    df = df.dropna(subset=feat_cols)
    feature_df = df[feat_cols]
    # Ertesi gün ceiling mi?
    df['target'] = df['ceiling'].shift(-1, fill_value=False)
    feature_df['target'] = df['target']
    return feature_df

def train_predict(symbols, start, end):
    all_feat = []
    for sym in symbols:
        df = get_data(sym, start, end)
        if len(df) < 60: continue
        df = add_technical_indicators(df)
        df = mark_ceiling_days(df)
        df = mark_speculative(df)
        feats = create_feature_label_df(df)
        feats['symbol'] = sym
        all_feat.append(feats)
    dataset = pd.concat(all_feat, axis=0).dropna()
    X = dataset.drop(columns=['target', 'symbol'])
    y = dataset['target'].astype(int)
    if y.sum() < 10:
        print("Tavan gün sayısı çok az, model zayıf olabilir!")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y)
    model = RandomForestClassifier(n_estimators=150, class_weight='balanced', random_state=42, max_depth=8)
    model.fit(X_train, y_train)
    print("Test seti doğruluk oranı:", model.score(X_test, y_test))
    return model, dataset

def predict_next_ceiling(model, symbols, lookback_days=30):
    today = datetime.now().date()
    start = (today - timedelta(days=lookback_days)).strftime('%Y-%m-%d')
    candidates = []
    for sym in symbols:
        df = get_data(sym, start, datetime.now().strftime('%Y-%m-%d'))
        if len(df) < 20: continue
        df = add_technical_indicators(df)
        df = mark_ceiling_days(df)
        df = mark_speculative(df)
        feats = create_feature_label_df(df)
        if len(feats) < 2: continue
        latest = feats.iloc[[-2]]
        X_latest = latest.drop(columns=['target', 'symbol'], errors='ignore')
        pred = model.predict(X_latest)
        proba = model.predict_proba(X_latest)[0][1]
        gcross = bool(latest['golden_cross_signal'].values[0])
        spec = bool(latest['speculative'].values[0])
        if pred[0] == 1 and proba > 0.45:
            candidates.append((sym, proba, gcross, spec))
    candidates = sorted(candidates, key=lambda x: -x[1])
    print("Tahmini tavan adayı hisseler (sembol, olasılık, yeni golden_cross, spekülatif):")
    for sym, proba, gc, spec in candidates:
        print(f"{sym}: {proba:.2f} | Golden Cross: {gc} | Spekülatif: {spec}")

if __name__ == "__main__":
    symbols = load_symbols("bist_symbols.csv")
    start = (datetime.now() - timedelta(days=240)).strftime('%Y-%m-%d')
    end = datetime.now().strftime('%Y-%m-%d')
    model, dataset = train_predict(symbols, start, end)
    predict_next_ceiling(model, symbols)