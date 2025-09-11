#!/usr/bin/env python3
"""
Gelişmiş Teknik Analiz
Tüm teknik göstergeleri kullanan kapsamlı analiz sistemi
"""

import yfinance as yf
import pandas as pd
import numpy as np
import talib
from typing import Dict, Any, List

class AdvancedTechnicalAnalyzer:
    def __init__(self):
        """Gelişmiş teknik analiz sistemi"""
        pass
    
    def calculate_all_indicators(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Tüm teknik göstergeleri hesapla"""
        if len(data) < 50:
            return {}
        
        try:
            close = data['Close'].values
            high = data['High'].values
            low = data['Low'].values
            volume = data['Volume'].values
            
            indicators = {}
            
            # 1. MOMENTUM GÖSTERGELERI
            indicators.update(self._calculate_momentum_indicators(close, high, low, volume))
            
            # 2. TREND GÖSTERGELERI
            indicators.update(self._calculate_trend_indicators(close, high, low))
            
            # 3. VOLATİLİTE GÖSTERGELERİ
            indicators.update(self._calculate_volatility_indicators(close, high, low))
            
            # 4. HACİM GÖSTERGELERİ
            indicators.update(self._calculate_volume_indicators(close, volume))
            
            # 5. OSİLATÖRLER
            indicators.update(self._calculate_oscillators(close, high, low))
            
            # 6. DESTEK/DİRENÇ SEVİYELERİ
            indicators.update(self._calculate_support_resistance(close, high, low))
            
            # 7. FİBONACCI SEVİYELERİ
            indicators.update(self._calculate_fibonacci_levels(close, high, low))
            
            # 8. PATTERN TANIMLAMA
            indicators.update(self._identify_patterns(close, high, low))
            
            return indicators
            
        except Exception as e:
            print(f"Gösterge hesaplama hatası: {e}")
            return {}
    
    def _calculate_momentum_indicators(self, close, high, low, volume) -> Dict[str, float]:
        """Momentum göstergeleri"""
        try:
            return {
                'RSI_14': talib.RSI(close, timeperiod=14)[-1] if len(close) >= 14 else 50.0,
                'RSI_21': talib.RSI(close, timeperiod=21)[-1] if len(close) >= 21 else 50.0,
                'STOCH_K': talib.STOCH(high, low, close)[0][-1] if len(close) >= 14 else 50.0,
                'STOCH_D': talib.STOCH(high, low, close)[1][-1] if len(close) >= 14 else 50.0,
                'WILLIAMS_R': talib.WILLR(high, low, close)[-1] if len(close) >= 14 else -50.0,
                'CCI': talib.CCI(high, low, close)[-1] if len(close) >= 20 else 0.0,
                'ROC_10': talib.ROC(close, timeperiod=10)[-1] if len(close) >= 10 else 0.0,
                'ROC_20': talib.ROC(close, timeperiod=20)[-1] if len(close) >= 20 else 0.0,
                'MOMENTUM_10': talib.MOM(close, timeperiod=10)[-1] if len(close) >= 10 else 0.0,
                'CMO': talib.CMO(close)[-1] if len(close) >= 20 else 0.0
            }
        except:
            return {}
    
    def _calculate_trend_indicators(self, close, high, low) -> Dict[str, float]:
        """Trend göstergeleri"""
        try:
            indicators = {}
            
            # MACD
            macd_line, macd_signal, macd_hist = talib.MACD(close)
            indicators.update({
                'MACD_LINE': macd_line[-1] if len(macd_line) > 0 else 0.0,
                'MACD_SIGNAL': macd_signal[-1] if len(macd_signal) > 0 else 0.0,
                'MACD_HISTOGRAM': macd_hist[-1] if len(macd_hist) > 0 else 0.0
            })
            
            # ADX (Average Directional Index)
            indicators['ADX'] = talib.ADX(high, low, close)[-1] if len(close) >= 14 else 25.0
            indicators['PLUS_DI'] = talib.PLUS_DI(high, low, close)[-1] if len(close) >= 14 else 25.0
            indicators['MINUS_DI'] = talib.MINUS_DI(high, low, close)[-1] if len(close) >= 14 else 25.0
            
            # Aroon
            aroon_up, aroon_down = talib.AROON(high, low)
            indicators['AROON_UP'] = aroon_up[-1] if len(aroon_up) > 0 else 50.0
            indicators['AROON_DOWN'] = aroon_down[-1] if len(aroon_down) > 0 else 50.0
            
            # Moving Averages
            indicators.update({
                'SMA_5': talib.SMA(close, timeperiod=5)[-1] if len(close) >= 5 else close[-1],
                'SMA_10': talib.SMA(close, timeperiod=10)[-1] if len(close) >= 10 else close[-1],
                'SMA_20': talib.SMA(close, timeperiod=20)[-1] if len(close) >= 20 else close[-1],
                'SMA_50': talib.SMA(close, timeperiod=50)[-1] if len(close) >= 50 else close[-1],
                'EMA_12': talib.EMA(close, timeperiod=12)[-1] if len(close) >= 12 else close[-1],
                'EMA_26': talib.EMA(close, timeperiod=26)[-1] if len(close) >= 26 else close[-1],
                'WMA_20': talib.WMA(close, timeperiod=20)[-1] if len(close) >= 20 else close[-1]
            })
            
            return indicators
        except:
            return {}
    
    def _calculate_volatility_indicators(self, close, high, low) -> Dict[str, float]:
        """Volatilite göstergeleri"""
        try:
            # Bollinger Bands
            bb_upper, bb_middle, bb_lower = talib.BBANDS(close)
            
            # ATR (Average True Range)
            atr = talib.ATR(high, low, close)[-1] if len(close) >= 14 else 0.0
            
            return {
                'BB_UPPER': bb_upper[-1] if len(bb_upper) > 0 else close[-1],
                'BB_MIDDLE': bb_middle[-1] if len(bb_middle) > 0 else close[-1],
                'BB_LOWER': bb_lower[-1] if len(bb_lower) > 0 else close[-1],
                'BB_POSITION': ((close[-1] - bb_lower[-1]) / (bb_upper[-1] - bb_lower[-1]) * 100) if len(bb_upper) > 0 and bb_upper[-1] != bb_lower[-1] else 50.0,
                'ATR': atr,
                'ATR_PERCENT': (atr / close[-1] * 100) if close[-1] > 0 else 0.0,
                'VOLATILITY_10': np.std(close[-10:]) / np.mean(close[-10:]) * 100 if len(close) >= 10 else 0.0
            }
        except:
            return {}
    
    def _calculate_volume_indicators(self, close, volume) -> Dict[str, float]:
        """Hacim göstergeleri"""
        try:
            return {
                'OBV': talib.OBV(close, volume)[-1] if len(close) > 0 else 0.0,
                'AD_LINE': talib.AD(np.array([close[-1]]), np.array([close[-1]]), np.array([close[-1]]), np.array([volume[-1]]))[-1] if len(close) > 0 else 0.0,
                'VOLUME_SMA_20': talib.SMA(volume, timeperiod=20)[-1] if len(volume) >= 20 else volume[-1],
                'VOLUME_RATIO': volume[-1] / talib.SMA(volume, timeperiod=20)[-1] if len(volume) >= 20 and talib.SMA(volume, timeperiod=20)[-1] > 0 else 1.0,
                'VWAP': np.sum(close * volume) / np.sum(volume) if np.sum(volume) > 0 else close[-1]
            }
        except:
            return {}
    
    def _calculate_oscillators(self, close, high, low) -> Dict[str, float]:
        """Osilatör göstergeleri"""
        try:
            return {
                'ULTIMATE_OSC': talib.ULTOSC(high, low, close)[-1] if len(close) >= 28 else 50.0,
                'TRIX': talib.TRIX(close)[-1] if len(close) >= 30 else 0.0,
                'PPO': talib.PPO(close)[-1] if len(close) >= 26 else 0.0,
                'DEMA': talib.DEMA(close)[-1] if len(close) >= 20 else close[-1],
                'TEMA': talib.TEMA(close)[-1] if len(close) >= 30 else close[-1]
            }
        except:
            return {}
    
    def _calculate_support_resistance(self, close, high, low) -> Dict[str, float]:
        """Destek ve direnç seviyeleri"""
        try:
            # Son 20 günün pivot seviyeleri
            if len(close) >= 20:
                recent_high = np.max(high[-20:])
                recent_low = np.min(low[-20:])
                pivot = (recent_high + recent_low + close[-1]) / 3
                
                # Klasik pivot seviyeleri
                r1 = 2 * pivot - recent_low
                r2 = pivot + (recent_high - recent_low)
                s1 = 2 * pivot - recent_high
                s2 = pivot - (recent_high - recent_low)
                
                return {
                    'PIVOT_POINT': pivot,
                    'RESISTANCE_1': r1,
                    'RESISTANCE_2': r2,
                    'SUPPORT_1': s1,
                    'SUPPORT_2': s2,
                    'RANGE_HIGH_20': recent_high,
                    'RANGE_LOW_20': recent_low,
                    'PRICE_POSITION_20': ((close[-1] - recent_low) / (recent_high - recent_low) * 100) if recent_high != recent_low else 50.0
                }
            return {}
        except:
            return {}
    
    def _calculate_fibonacci_levels(self, close, high, low) -> Dict[str, float]:
        """Fibonacci seviyeleri"""
        try:
            if len(close) >= 20:
                swing_high = np.max(high[-20:])
                swing_low = np.min(low[-20:])
                diff = swing_high - swing_low
                
                # Fibonacci retracement seviyeleri
                fib_levels = {
                    'FIB_0': swing_high,
                    'FIB_23_6': swing_high - (diff * 0.236),
                    'FIB_38_2': swing_high - (diff * 0.382),
                    'FIB_50': swing_high - (diff * 0.5),
                    'FIB_61_8': swing_high - (diff * 0.618),
                    'FIB_78_6': swing_high - (diff * 0.786),
                    'FIB_100': swing_low
                }
                
                # Hangi seviyeye en yakın?
                current_price = close[-1]
                closest_fib = min(fib_levels.items(), key=lambda x: abs(x[1] - current_price))
                fib_levels['CLOSEST_FIB_LEVEL'] = closest_fib[1]
                fib_levels['CLOSEST_FIB_NAME'] = closest_fib[0]
                
                return fib_levels
            return {}
        except:
            return {}
    
    def _identify_patterns(self, close, high, low) -> Dict[str, Any]:
        """Pattern tanımlama"""
        try:
            patterns = {}
            
            if len(close) >= 10:
                # Candlestick patterns (talib ile)
                patterns.update({
                    'DOJI': talib.CDLDOJI(np.array([high[-1]]), np.array([low[-1]]), np.array([close[-2]]), np.array([close[-1]]))[-1] if len(close) >= 2 else 0,
                    'HAMMER': talib.CDLHAMMER(np.array([high[-1]]), np.array([low[-1]]), np.array([close[-2]]), np.array([close[-1]]))[-1] if len(close) >= 2 else 0,
                    'SHOOTING_STAR': talib.CDLSHOOTINGSTAR(np.array([high[-1]]), np.array([low[-1]]), np.array([close[-2]]), np.array([close[-1]]))[-1] if len(close) >= 2 else 0
                })
                
                # Trend patterns
                if len(close) >= 5:
                    # Son 5 günün trendi
                    recent_closes = close[-5:]
                    if all(recent_closes[i] > recent_closes[i-1] for i in range(1, len(recent_closes))):
                        patterns['UPTREND_5D'] = True
                    elif all(recent_closes[i] < recent_closes[i-1] for i in range(1, len(recent_closes))):
                        patterns['DOWNTREND_5D'] = True
                    else:
                        patterns['SIDEWAYS_5D'] = True
                
                # MA alignment
                if len(close) >= 20:
                    sma_5 = talib.SMA(close, timeperiod=5)[-1]
                    sma_10 = talib.SMA(close, timeperiod=10)[-1]
                    sma_20 = talib.SMA(close, timeperiod=20)[-1]
                    
                    if sma_5 > sma_10 > sma_20:
                        patterns['BULLISH_MA_ALIGNMENT'] = True
                    elif sma_5 < sma_10 < sma_20:
                        patterns['BEARISH_MA_ALIGNMENT'] = True
            
            return patterns
        except:
            return {}
    
    def analyze_comprehensive(self, symbol: str) -> Dict[str, Any]:
        """Kapsamlı analiz"""
        try:
            # Veri çek
            ticker = yf.Ticker(symbol)
            data = ticker.history(period='90d')
            
            if len(data) < 50:
                return {'error': 'Yetersiz veri'}
            
            # Tüm göstergeleri hesapla
            indicators = self.calculate_all_indicators(data)
            
            # Current price bilgilerini ekle
            indicators.update({
                'CURRENT_PRICE': data['Close'].iloc[-1],
                'DAILY_CHANGE': ((data['Close'].iloc[-1] - data['Close'].iloc[-2]) / data['Close'].iloc[-2] * 100) if len(data) >= 2 else 0.0,
                'VOLUME': data['Volume'].iloc[-1],
                'HIGH_52W': data['High'].max(),
                'LOW_52W': data['Low'].min()
            })
            
            # Genel değerlendirme skoru
            score = self.calculate_comprehensive_score(indicators)
            indicators['COMPREHENSIVE_SCORE'] = score
            
            return indicators
            
        except Exception as e:
            return {'error': str(e)}
    
    def calculate_comprehensive_score(self, indicators: Dict[str, Any]) -> float:
        """Kapsamlı skor hesaplama"""
        try:
            score = 0
            max_score = 0
            
            # Momentum skorları
            if 'RSI_14' in indicators:
                rsi = indicators['RSI_14']
                if 60 <= rsi <= 70:
                    score += 20
                elif 50 <= rsi <= 80:
                    score += 15
                elif rsi > 80:
                    score += 10
                max_score += 20
            
            # MACD skoru
            if all(k in indicators for k in ['MACD_LINE', 'MACD_SIGNAL']):
                if indicators['MACD_LINE'] > indicators['MACD_SIGNAL']:
                    score += 15
                max_score += 15
            
            # ADX trend gücü
            if 'ADX' in indicators:
                adx = indicators['ADX']
                if adx > 25:
                    score += 15
                elif adx > 20:
                    score += 10
                max_score += 15
            
            # Volume skoru
            if 'VOLUME_RATIO' in indicators:
                vol_ratio = indicators['VOLUME_RATIO']
                if vol_ratio >= 2.0:
                    score += 20
                elif vol_ratio >= 1.5:
                    score += 15
                elif vol_ratio >= 1.0:
                    score += 10
                max_score += 20
            
            # Bollinger Band pozisyonu
            if 'BB_POSITION' in indicators:
                bb_pos = indicators['BB_POSITION']
                if bb_pos >= 80:
                    score += 15
                elif bb_pos >= 60:
                    score += 10
                max_score += 15
            
            # Pattern bonusları
            if 'BULLISH_MA_ALIGNMENT' in indicators and indicators['BULLISH_MA_ALIGNMENT']:
                score += 10
            if 'UPTREND_5D' in indicators and indicators['UPTREND_5D']:
                score += 5
            max_score += 15
            
            return (score / max_score * 100) if max_score > 0 else 0
            
        except:
            return 0

def main():
    analyzer = AdvancedTechnicalAnalyzer()
    
    print("🔬 GELİŞMİŞ TEKNİK ANALİZ")
    print("=" * 80)
    print("Tüm teknik göstergeler kullanılarak kapsamlı analiz")
    print("=" * 80)
    
    # Analiz edilecek hisseler
    symbols = ['PENTA.IS', 'GRNYO.IS', 'PCILT.IS', 'KAPLM.IS']
    
    for symbol in symbols:
        symbol_name = symbol.replace('.IS', '')
        print(f"\n🔍 {symbol_name} KAPSAMLI ANALİZ:")
        print("=" * 50)
        
        result = analyzer.analyze_comprehensive(symbol)
        
        if 'error' in result:
            print(f"❌ Hata: {result['error']}")
            continue
        
        # Temel bilgiler
        print(f"💰 Son Fiyat: {result['CURRENT_PRICE']:.2f} TL")
        print(f"📈 Günlük Değişim: %{result['DAILY_CHANGE']:.1f}")
        print(f"📊 Kapsamlı Skor: {result['COMPREHENSIVE_SCORE']:.1f}/100")
        
        # Momentum göstergeleri
        print(f"\n📊 MOMENTUM GÖSTERGELERİ:")
        print(f"   RSI (14): {result.get('RSI_14', 0):.1f}")
        print(f"   RSI (21): {result.get('RSI_21', 0):.1f}")
        print(f"   Stochastic %K: {result.get('STOCH_K', 0):.1f}")
        print(f"   Williams %R: {result.get('WILLIAMS_R', 0):.1f}")
        print(f"   CCI: {result.get('CCI', 0):.1f}")
        
        # Trend göstergeleri
        print(f"\n📈 TREND GÖSTERGELERİ:")
        print(f"   MACD Line: {result.get('MACD_LINE', 0):.3f}")
        print(f"   MACD Signal: {result.get('MACD_SIGNAL', 0):.3f}")
        print(f"   MACD Histogram: {result.get('MACD_HISTOGRAM', 0):.3f}")
        print(f"   ADX: {result.get('ADX', 0):.1f}")
        print(f"   +DI: {result.get('PLUS_DI', 0):.1f}")
        print(f"   -DI: {result.get('MINUS_DI', 0):.1f}")
        
        # Bollinger Bands
        print(f"\n🎯 BOLLINGER BANDS:")
        print(f"   Üst Band: {result.get('BB_UPPER', 0):.2f}")
        print(f"   Orta Band: {result.get('BB_MIDDLE', 0):.2f}")
        print(f"   Alt Band: {result.get('BB_LOWER', 0):.2f}")
        print(f"   BB Pozisyon: %{result.get('BB_POSITION', 0):.1f}")
        
        # Destek/Direnç
        if 'PIVOT_POINT' in result:
            print(f"\n🎯 DESTEK/DİRENÇ:")
            print(f"   Pivot Point: {result.get('PIVOT_POINT', 0):.2f}")
            print(f"   Direnç 1: {result.get('RESISTANCE_1', 0):.2f}")
            print(f"   Direnç 2: {result.get('RESISTANCE_2', 0):.2f}")
            print(f"   Destek 1: {result.get('SUPPORT_1', 0):.2f}")
            print(f"   Destek 2: {result.get('SUPPORT_2', 0):.2f}")
        
        # Fibonacci
        if 'FIB_50' in result:
            print(f"\n🌀 FİBONACCI SEVİYELERİ:")
            print(f"   Fib 23.6%: {result.get('FIB_23_6', 0):.2f}")
            print(f"   Fib 38.2%: {result.get('FIB_38_2', 0):.2f}")
            print(f"   Fib 50%: {result.get('FIB_50', 0):.2f}")
            print(f"   Fib 61.8%: {result.get('FIB_61_8', 0):.2f}")
        
        # Hacim analizi
        print(f"\n📊 HACİM ANALİZİ:")
        print(f"   Güncel Hacim: {result.get('VOLUME', 0):,.0f}")
        print(f"   Hacim Oranı: {result.get('VOLUME_RATIO', 0):.1f}x")
        print(f"   OBV: {result.get('OBV', 0):,.0f}")
        
        # Volatilite
        print(f"\n⚡ VOLATİLİTE:")
        print(f"   ATR: {result.get('ATR', 0):.2f}")
        print(f"   ATR %: {result.get('ATR_PERCENT', 0):.1f}")
        print(f"   10 Gün Vol: %{result.get('VOLATILITY_10', 0):.1f}")
        
        # Pattern tanımlama
        print(f"\n🔍 PATTERN ANALİZİ:")
        patterns = []
        if result.get('BULLISH_MA_ALIGNMENT'):
            patterns.append("✅ Bullish MA Alignment")
        if result.get('BEARISH_MA_ALIGNMENT'):
            patterns.append("❌ Bearish MA Alignment")
        if result.get('UPTREND_5D'):
            patterns.append("📈 5 Gün Yükseliş Trendi")
        if result.get('DOWNTREND_5D'):
            patterns.append("📉 5 Gün Düşüş Trendi")
        if result.get('SIDEWAYS_5D'):
            patterns.append("📊 5 Gün Yatay Trend")
        
        for pattern in patterns:
            print(f"   {pattern}")
        
        if not patterns:
            print("   Belirgin pattern tespit edilmedi")

if __name__ == "__main__":
    main()