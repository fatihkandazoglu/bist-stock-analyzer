#!/usr/bin/env python3
"""
Kapsamlı Teknik Gösterge Analizi
Tavan öncesi tüm teknik göstergelerin davranışını analiz eder.
"""

import pandas as pd
import numpy as np
import logging
from typing import List, Dict, Any
from bist_data_fetcher import BISTDataFetcher

# Simplified technical analysis without external dependencies
def simple_sma(data, period):
    """Simple Moving Average"""
    return data.rolling(window=period).mean()

def simple_ema(data, period):
    """Exponential Moving Average"""
    return data.ewm(span=period).mean()

def simple_rsi(data, period=14):
    """Simple RSI calculation"""
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def simple_bollinger_bands(data, period=20, std_dev=2):
    """Simple Bollinger Bands"""
    sma = simple_sma(data, period)
    std = data.rolling(window=period).std()
    upper = sma + (std * std_dev)
    lower = sma - (std * std_dev)
    return upper, sma, lower

def simple_stochastic(high, low, close, k_period=14):
    """Simple Stochastic %K"""
    lowest_low = low.rolling(window=k_period).min()
    highest_high = high.rolling(window=k_period).max()
    return 100 * (close - lowest_low) / (highest_high - lowest_low)

def simple_williams_r(high, low, close, period=14):
    """Simple Williams %R"""
    highest_high = high.rolling(window=period).max()
    lowest_low = low.rolling(window=period).min()
    return -100 * (highest_high - close) / (highest_high - lowest_low)

logger = logging.getLogger(__name__)

class ComprehensiveTechnicalAnalyzer:
    def __init__(self):
        """Kapsamlı teknik analiz sistemi"""
        self.data_fetcher = BISTDataFetcher()
        
    def calculate_all_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Tüm teknik göstergeleri hesapla"""
        if len(data) < 25:
            return pd.DataFrame()
            
        try:
            # Fiyat verileri
            high = data['High'].values
            low = data['Low'].values
            close = data['Close'].values
            volume = data['Volume'].values
            
            indicators = pd.DataFrame(index=data.index)
            
            # 1. TREND İNDİKATÖRLERİ
            # Moving Averages
            close_series = pd.Series(close)
            indicators['SMA_5'] = simple_sma(close_series, 5)
            indicators['SMA_10'] = simple_sma(close_series, 10)
            indicators['SMA_20'] = simple_sma(close_series, 20)
            indicators['SMA_50'] = simple_sma(close_series, 50) if len(close) >= 50 else np.nan
            
            indicators['EMA_5'] = simple_ema(close_series, 5)
            indicators['EMA_10'] = simple_ema(close_series, 10)
            indicators['EMA_20'] = simple_ema(close_series, 20)
            
            # 2. MOMENTUM İNDİKATÖRLERİ
            # RSI
            high_series = pd.Series(high)
            low_series = pd.Series(low)
            indicators['RSI_14'] = simple_rsi(close_series, 14)
            indicators['RSI_7'] = simple_rsi(close_series, 7)
            indicators['RSI_21'] = simple_rsi(close_series, 21)
            
            # MACD (simplified)
            ema_12 = simple_ema(close_series, 12)
            ema_26 = simple_ema(close_series, 26)
            macd = ema_12 - ema_26
            macd_signal = simple_ema(macd, 9)
            indicators['MACD'] = macd
            indicators['MACD_Signal'] = macd_signal
            indicators['MACD_Histogram'] = macd - macd_signal
            
            # Stochastic
            stoch_k = simple_stochastic(high_series, low_series, close_series, 14)
            indicators['Stoch_K'] = stoch_k
            indicators['Stoch_D'] = simple_sma(stoch_k, 3)
            
            # Williams %R
            indicators['Williams_R'] = simple_williams_r(high_series, low_series, close_series, 14)
            
            # Rate of Change
            indicators['ROC_10'] = (close_series / close_series.shift(10) - 1) * 100
            indicators['ROC_20'] = (close_series / close_series.shift(20) - 1) * 100
            
            # 3. VOLATİLİTE İNDİKATÖRLERİ
            # Bollinger Bands
            bb_upper, bb_middle, bb_lower = simple_bollinger_bands(close_series, 20, 2)
            indicators['BB_Upper'] = bb_upper
            indicators['BB_Middle'] = bb_middle
            indicators['BB_Lower'] = bb_lower
            indicators['BB_Position'] = (close_series - bb_lower) / (bb_upper - bb_lower) * 100
            
            # Average True Range (simplified)
            tr1 = high_series - low_series
            tr2 = abs(high_series - close_series.shift(1))
            tr3 = abs(low_series - close_series.shift(1))
            true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            indicators['ATR'] = simple_sma(true_range, 14)
            
            # 4. HACİM İNDİKATÖRLERİ
            # Volume SMA
            volume_series = pd.Series(volume)
            indicators['Volume_SMA_10'] = simple_sma(volume_series, 10)
            indicators['Volume_SMA_20'] = simple_sma(volume_series, 20)
            indicators['Volume_Ratio_10'] = volume_series / indicators['Volume_SMA_10']
            indicators['Volume_Ratio_20'] = volume_series / indicators['Volume_SMA_20']
            
            # On Balance Volume (simplified)
            price_change = close_series.diff()
            obv = (volume_series * np.where(price_change > 0, 1, np.where(price_change < 0, -1, 0))).cumsum()
            indicators['OBV'] = obv
            
            # 5. FİYAT PATTERN İNDİKATÖRLERİ
            # Price position relative to moving averages
            indicators['Price_vs_SMA5'] = (close_series / indicators['SMA_5'] - 1) * 100
            indicators['Price_vs_SMA10'] = (close_series / indicators['SMA_10'] - 1) * 100
            indicators['Price_vs_SMA20'] = (close_series / indicators['SMA_20'] - 1) * 100
            
            # 6. ÖZEL MOMENTUM İNDİKATÖRLERİ
            # Price momentum (son 3, 5, 10 gün)
            indicators['Price_Change_3D'] = (close_series / close_series.shift(3) - 1) * 100
            indicators['Price_Change_5D'] = (close_series / close_series.shift(5) - 1) * 100
            indicators['Price_Change_10D'] = (close_series / close_series.shift(10) - 1) * 100
            
            # Daily change
            indicators['Daily_Change'] = (close_series / close_series.shift(1) - 1) * 100
            
            # 7. TREND GÜCÜ İNDİKATÖRLERİ
            # ADX (simplified)
            plus_dm = (high_series.diff().where((high_series.diff() > low_series.diff().abs()) & (high_series.diff() > 0), 0)).rolling(14).mean()
            minus_dm = (low_series.diff().abs().where((low_series.diff().abs() > high_series.diff()) & (low_series.diff() < 0), 0)).rolling(14).mean()
            atr_14 = indicators['ATR']
            plus_di = 100 * plus_dm / atr_14
            minus_di = 100 * minus_dm / atr_14
            dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
            indicators['ADX'] = dx.rolling(14).mean()
            
            # SAR (simplified - basic trend indicator)
            indicators['SAR_Signal'] = np.where(close_series > indicators['SMA_20'], 1, -1)
            
            return indicators
            
        except Exception as e:
            logger.error(f"Teknik gösterge hesaplama hatası: {e}")
            return pd.DataFrame()
    
    def analyze_pre_ceiling_indicators(self, days_back: int = 60) -> Dict[str, Any]:
        """Tavan öncesi tüm teknik göstergeleri analiz et"""
        logger.info(f"Son {days_back} gündeki tavan öncesi teknik göstergeler analiz ediliyor...")
        
        # Tüm BİST hisselerinin verilerini çek
        all_data = self.data_fetcher.get_all_bist_data(period=f"{days_back + 10}d")
        
        pre_ceiling_indicators = []
        
        for symbol, data in all_data.items():
            if data.empty or len(data) < 30:
                continue
                
            try:
                # Teknik göstergeleri hesapla
                indicators = self.calculate_all_indicators(data)
                if indicators.empty:
                    continue
                
                # Tavan günlerini bul
                for i in range(25, len(data)):  # En az 25 gün geçmiş veri
                    current_price = data['Close'].iloc[i]
                    previous_price = data['Close'].iloc[i-1]
                    
                    if previous_price == 0:
                        continue
                        
                    daily_change = ((current_price - previous_price) / previous_price) * 100
                    
                    # Tavan günü mü? (%9+ artış)
                    if daily_change >= 9.0:
                        # Tavan öncesi 1-3 gün arası analiz et
                        for days_before in range(1, 4):
                            pre_index = i - days_before
                            
                            if pre_index < 0 or pre_index >= len(indicators):
                                continue
                                
                            # Tüm göstergeleri topla
                            indicator_data = {
                                'symbol': symbol.replace('.IS', ''),
                                'days_before_ceiling': days_before,
                                'ceiling_date': data.index[i],
                                'ceiling_change': daily_change,
                                'pre_date': data.index[pre_index]
                            }
                            
                            # Her göstergeyi ekle
                            for col in indicators.columns:
                                value = indicators[col].iloc[pre_index]
                                if pd.notna(value) and np.isfinite(value):
                                    indicator_data[col] = value
                                    
                            # Sadece yeterli veri varsa ekle
                            if len(indicator_data) > 10:  # En az 10 gösterge
                                pre_ceiling_indicators.append(indicator_data)
                            
            except Exception as e:
                logger.debug(f"{symbol} teknik gösterge analiz hatası: {e}")
                continue
                
        logger.info(f"Toplam {len(pre_ceiling_indicators)} tavan öncesi teknik veri noktası bulundu")
        return pre_ceiling_indicators
    
    def calculate_indicator_averages(self, pre_ceiling_data: List[Dict]) -> Dict[str, Any]:
        """Teknik gösterge ortalamalarını hesapla"""
        if not pre_ceiling_data:
            return {}
            
        # Tüm gösterge isimlerini topla
        all_indicators = set()
        for data_point in pre_ceiling_data:
            all_indicators.update([k for k in data_point.keys() 
                                 if k not in ['symbol', 'days_before_ceiling', 'ceiling_date', 'ceiling_change', 'pre_date']])
        
        analysis = {}
        
        # Gün bazında grupla
        for days_before in range(1, 4):
            day_data = [d for d in pre_ceiling_data if d['days_before_ceiling'] == days_before]
            
            if not day_data:
                continue
                
            day_analysis = {
                'total_signals': len(day_data),
                'indicator_averages': {},
                'indicator_medians': {},
                'indicator_ranges': {},
                'significant_patterns': []
            }
            
            # Her gösterge için istatistikleri hesapla
            for indicator in sorted(all_indicators):
                values = []
                for data_point in day_data:
                    if indicator in data_point and pd.notna(data_point[indicator]):
                        val = data_point[indicator]
                        if np.isfinite(val) and abs(val) < 1e10:  # Aşırı değerleri filtrele
                            values.append(val)
                
                if len(values) >= 10:  # En az 10 veri noktası
                    day_analysis['indicator_averages'][indicator] = np.mean(values)
                    day_analysis['indicator_medians'][indicator] = np.median(values)
                    day_analysis['indicator_ranges'][indicator] = {
                        'min': np.min(values),
                        'max': np.max(values),
                        'std': np.std(values),
                        'count': len(values)
                    }
            
            analysis[f'{days_before}_days_before'] = day_analysis
        
        return analysis
    
    def find_critical_indicators(self, analysis: Dict) -> List[Dict[str, Any]]:
        """En kritik göstergeleri bul"""
        critical_indicators = []
        
        # 1 gün öncesi verileri al (en önemli)
        one_day_data = analysis.get('1_days_before', {})
        if not one_day_data:
            return critical_indicators
            
        averages = one_day_data.get('indicator_averages', {})
        ranges = one_day_data.get('indicator_ranges', {})
        
        # RSI analizi
        if 'RSI_14' in averages:
            critical_indicators.append({
                'indicator': 'RSI_14',
                'category': 'Momentum',
                'avg_value': averages['RSI_14'],
                'interpretation': self.interpret_rsi(averages['RSI_14']),
                'importance': 'YÜKSEK',
                'range': f"{ranges['RSI_14']['min']:.1f} - {ranges['RSI_14']['max']:.1f}"
            })
        
        # MACD analizi
        if 'MACD' in averages and 'MACD_Signal' in averages:
            macd_diff = averages['MACD'] - averages['MACD_Signal']
            critical_indicators.append({
                'indicator': 'MACD Divergence',
                'category': 'Momentum',
                'avg_value': macd_diff,
                'interpretation': self.interpret_macd(macd_diff),
                'importance': 'YÜKSEK',
                'range': f"MACD: {averages['MACD']:.4f}, Signal: {averages['MACD_Signal']:.4f}"
            })
        
        # Bollinger Band pozisyonu
        if 'BB_Position' in averages:
            critical_indicators.append({
                'indicator': 'Bollinger Band Position',
                'category': 'Volatilite',
                'avg_value': averages['BB_Position'],
                'interpretation': self.interpret_bb_position(averages['BB_Position']),
                'importance': 'ORTA',
                'range': f"{ranges['BB_Position']['min']:.1f}% - {ranges['BB_Position']['max']:.1f}%"
            })
        
        # Volume momentum
        if 'Volume_Ratio_20' in averages:
            critical_indicators.append({
                'indicator': 'Volume Ratio (20D)',
                'category': 'Hacim',
                'avg_value': averages['Volume_Ratio_20'],
                'interpretation': self.interpret_volume_ratio(averages['Volume_Ratio_20']),
                'importance': 'YÜKSEK',
                'range': f"{ranges['Volume_Ratio_20']['min']:.2f}x - {ranges['Volume_Ratio_20']['max']:.2f}x"
            })
        
        # Stochastic
        if 'Stoch_K' in averages:
            critical_indicators.append({
                'indicator': 'Stochastic %K',
                'category': 'Momentum',
                'avg_value': averages['Stoch_K'],
                'interpretation': self.interpret_stochastic(averages['Stoch_K']),
                'importance': 'ORTA',
                'range': f"{ranges['Stoch_K']['min']:.1f} - {ranges['Stoch_K']['max']:.1f}"
            })
        
        # Williams %R
        if 'Williams_R' in averages:
            critical_indicators.append({
                'indicator': 'Williams %R',
                'category': 'Momentum',
                'avg_value': averages['Williams_R'],
                'interpretation': self.interpret_williams_r(averages['Williams_R']),
                'importance': 'DÜŞÜK',
                'range': f"{ranges['Williams_R']['min']:.1f} - {ranges['Williams_R']['max']:.1f}"
            })
        
        # Price vs Moving Averages
        if 'Price_vs_SMA20' in averages:
            critical_indicators.append({
                'indicator': 'Price vs SMA20',
                'category': 'Trend',
                'avg_value': averages['Price_vs_SMA20'],
                'interpretation': self.interpret_price_vs_ma(averages['Price_vs_SMA20']),
                'importance': 'YÜKSEK',
                'range': f"{ranges['Price_vs_SMA20']['min']:.2f}% - {ranges['Price_vs_SMA20']['max']:.2f}%"
            })
        
        return critical_indicators
    
    def interpret_rsi(self, rsi: float) -> str:
        """RSI yorumla"""
        if rsi < 30:
            return "OVERSOLD - Güçlü alım sinyali"
        elif rsi < 50:
            return "ZAYIF - Hafif satım baskısı"
        elif rsi < 70:
            return "GÜÇLÜ - İdeal momentum bölgesi"
        else:
            return "OVERBOUGHT - Tavan öncesi tipik"
    
    def interpret_macd(self, macd_diff: float) -> str:
        """MACD yorumla"""
        if macd_diff > 0:
            return "POZITIF - Yükseliş momentumu"
        else:
            return "NEGATIF - Düşüş momentumu"
    
    def interpret_bb_position(self, position: float) -> str:
        """Bollinger Band pozisyonu yorumla"""
        if position < 20:
            return "ALT BANTLARDA - Oversold"
        elif position < 50:
            return "ORTA ALTINDA - Normal"
        elif position < 80:
            return "ORTA ÜSTÜNDE - Güçlü"
        else:
            return "ÜST BANTLARDA - Çok güçlü"
    
    def interpret_volume_ratio(self, ratio: float) -> str:
        """Volume ratio yorumla"""
        if ratio < 1.0:
            return "DÜŞÜK HACİM - Zayıf ilgi"
        elif ratio < 1.5:
            return "NORMAL HACİM - Tipik"
        elif ratio < 2.0:
            return "YÜKSEK HACİM - Güçlü ilgi"
        else:
            return "ÇOK YÜKSEK HACİM - Aşırı ilgi"
    
    def interpret_stochastic(self, stoch: float) -> str:
        """Stochastic yorumla"""
        if stoch < 20:
            return "OVERSOLD - Güçlü alım fırsatı"
        elif stoch < 50:
            return "ZAYIF - Düşük momentum"
        elif stoch < 80:
            return "GÜÇLÜ - İyi momentum"
        else:
            return "OVERBOUGHT - Tavan sinyali"
    
    def interpret_williams_r(self, williams: float) -> str:
        """Williams %R yorumla"""
        if williams > -20:
            return "OVERBOUGHT - Satım sinyali"
        elif williams > -50:
            return "GÜÇLÜ - Yükseliş trendi"
        elif williams > -80:
            return "ZAYIF - Düşüş baskısı"
        else:
            return "OVERSOLD - Alım fırsatı"
    
    def interpret_price_vs_ma(self, percentage: float) -> str:
        """Fiyat vs Moving Average yorumla"""
        if percentage < -5:
            return "ORTALAMANIN ALTINDA - Zayıf"
        elif percentage < 0:
            return "ORTALAMAYA YAKIN - Normal"
        elif percentage < 5:
            return "ORTALAMANIN ÜSTÜNDE - Güçlü"
        else:
            return "ÇOK GÜÇLÜ - Güçlü momentum"

def main():
    logging.basicConfig(level=logging.INFO)
    
    analyzer = ComprehensiveTechnicalAnalyzer()
    
    print("\n📊 KAPSAMLI TEKNİK GÖSTERGE ANALİZİ")
    print("=" * 60)
    print("RSI, MACD, Bollinger Bands, Stochastic, Williams %R, Volume, Trend...")
    print("=" * 60)
    
    # Tavan öncesi teknik göstergeleri analiz et
    pre_ceiling_data = analyzer.analyze_pre_ceiling_indicators(days_back=45)
    
    if not pre_ceiling_data:
        print("❌ Teknik gösterge verisi bulunamadı!")
        return
    
    # Gösterge ortalamalarını hesapla
    analysis = analyzer.calculate_indicator_averages(pre_ceiling_data)
    
    if not analysis:
        print("❌ Analiz yapılamadı!")
        return
    
    print(f"\n📈 TAVAN ÖNCESİ TEKNİK GÖSTERGE ORTALAMALARI:")
    
    for day_key, day_data in analysis.items():
        days = day_key.split('_')[0]
        print(f"\n{'='*25} {days} GÜN ÖNCESİ {'='*25}")
        print(f"📊 Toplam sinyal sayısı: {day_data['total_signals']}")
        
        print(f"\n🎯 ÖNEMLİ MOMENTUM GÖSTERGELERİ:")
        avgs = day_data['indicator_averages']
        
        if 'RSI_14' in avgs:
            print(f"   • RSI (14): {avgs['RSI_14']:.1f}")
        if 'RSI_7' in avgs:
            print(f"   • RSI (7): {avgs['RSI_7']:.1f}")
        if 'Stoch_K' in avgs:
            print(f"   • Stochastic %K: {avgs['Stoch_K']:.1f}")
        if 'Williams_R' in avgs:
            print(f"   • Williams %R: {avgs['Williams_R']:.1f}")
            
        print(f"\n📈 TREND GÖSTERGELERİ:")
        if 'Price_vs_SMA5' in avgs:
            print(f"   • Fiyat vs SMA5: %{avgs['Price_vs_SMA5']:.2f}")
        if 'Price_vs_SMA10' in avgs:
            print(f"   • Fiyat vs SMA10: %{avgs['Price_vs_SMA10']:.2f}")
        if 'Price_vs_SMA20' in avgs:
            print(f"   • Fiyat vs SMA20: %{avgs['Price_vs_SMA20']:.2f}")
        if 'ADX' in avgs:
            print(f"   • ADX (Trend gücü): {avgs['ADX']:.1f}")
            
        print(f"\n📊 HACİM GÖSTERGELERİ:")
        if 'Volume_Ratio_10' in avgs:
            print(f"   • Hacim oranı (10D): {avgs['Volume_Ratio_10']:.2f}x")
        if 'Volume_Ratio_20' in avgs:
            print(f"   • Hacim oranı (20D): {avgs['Volume_Ratio_20']:.2f}x")
            
        print(f"\n⚡ MACD GÖSTERGELERİ:")
        if 'MACD' in avgs and 'MACD_Signal' in avgs:
            print(f"   • MACD: {avgs['MACD']:.4f}")
            print(f"   • MACD Signal: {avgs['MACD_Signal']:.4f}")
            print(f"   • MACD Fark: {(avgs['MACD'] - avgs['MACD_Signal']):.4f}")
            
        print(f"\n🎪 BOLLİNGER BANDS:")
        if 'BB_Position' in avgs:
            print(f"   • BB Pozisyonu: %{avgs['BB_Position']:.1f}")
            
        print(f"\n🚀 FİYAT MOMENTUM:")
        if 'Daily_Change' in avgs:
            print(f"   • Günlük değişim: %{avgs['Daily_Change']:.2f}")
        if 'Price_Change_3D' in avgs:
            print(f"   • 3 gün değişim: %{avgs['Price_Change_3D']:.2f}")
        if 'Price_Change_5D' in avgs:
            print(f"   • 5 gün değişim: %{avgs['Price_Change_5D']:.2f}")
    
    # Kritik göstergeleri bul
    critical_indicators = analyzer.find_critical_indicators(analysis)
    
    if critical_indicators:
        print(f"\n🔥 KRİTİK TAVAN ÖNCESİ GÖSTERGELERİ (1 gün öncesi):")
        
        for indicator in critical_indicators:
            importance_emoji = {"YÜKSEK": "🔥", "ORTA": "⚡", "DÜŞÜK": "💡"}
            emoji = importance_emoji.get(indicator['importance'], "📊")
            
            print(f"\n   {emoji} {indicator['indicator']} ({indicator['category']})")
            print(f"      → Ortalama: {indicator['avg_value']:.2f}")
            print(f"      → Yorum: {indicator['interpretation']}")
            print(f"      → Önem: {indicator['importance']}")
            print(f"      → Aralık: {indicator['range']}")
    
    print(f"\n💡 SONUÇ:")
    print(f"   🎯 Tavan öncesi teknik göstergeler belirli kalıplar gösteriyor")
    print(f"   📊 En önemli: RSI, Volume, MACD, Bollinger Band pozisyonu")
    print(f"   ⚖️ Bu göstergeler algoritma girdisi olarak kullanılabilir")

if __name__ == "__main__":
    main()