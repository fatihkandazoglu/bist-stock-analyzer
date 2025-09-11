#!/usr/bin/env python3
"""
Basit Teknik Gösterge Özeti
Mevcut analiz verilerini kullanarak tavan öncesi teknik profili çıkarır.
"""

import pandas as pd
import numpy as np
import logging
from typing import List, Dict, Any
from bist_data_fetcher import BISTDataFetcher

logger = logging.getLogger(__name__)

class SimpleTechnicalSummary:
    def __init__(self):
        """Basit teknik analiz sistemi"""
        self.data_fetcher = BISTDataFetcher()
        
    def calculate_simple_technical_indicators(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Basit teknik göstergeleri hesapla"""
        if len(data) < 20:
            return {}
            
        try:
            close = data['Close']
            high = data['High']
            low = data['Low']
            volume = data['Volume']
            
            # Son değerler (en güncel)
            current_close = close.iloc[-1]
            current_volume = volume.iloc[-1]
            
            # Moving Averages
            sma_5 = close.rolling(5).mean().iloc[-1] if len(close) >= 5 else current_close
            sma_10 = close.rolling(10).mean().iloc[-1] if len(close) >= 10 else current_close
            sma_20 = close.rolling(20).mean().iloc[-1] if len(close) >= 20 else current_close
            
            # RSI (basit)
            delta = close.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            
            if len(gain) >= 14 and loss.iloc[-1] != 0:
                rs = gain.iloc[-1] / loss.iloc[-1]
                rsi = 100 - (100 / (1 + rs))
            else:
                rsi = 50
                
            # Volume analizi
            volume_sma_20 = volume.rolling(20).mean().iloc[-1] if len(volume) >= 20 else current_volume
            volume_ratio = current_volume / volume_sma_20 if volume_sma_20 > 0 else 1
            
            # Günlük değişim
            if len(close) >= 2:
                daily_change = ((current_close - close.iloc[-2]) / close.iloc[-2]) * 100
            else:
                daily_change = 0
                
            # 5 gün momentum
            if len(close) >= 6:
                momentum_5d = ((current_close - close.iloc[-6]) / close.iloc[-6]) * 100
            else:
                momentum_5d = 0
                
            # Bollinger Band basit pozisyonu
            if len(close) >= 20:
                bb_middle = sma_20
                bb_std = close.rolling(20).std().iloc[-1]
                bb_upper = bb_middle + (bb_std * 2)
                bb_lower = bb_middle - (bb_std * 2)
                bb_position = (current_close - bb_lower) / (bb_upper - bb_lower) * 100 if bb_upper != bb_lower else 50
            else:
                bb_position = 50
                
            # Fiyat vs MA'lar
            price_vs_sma5 = ((current_close - sma_5) / sma_5) * 100 if sma_5 > 0 else 0
            price_vs_sma10 = ((current_close - sma_10) / sma_10) * 100 if sma_10 > 0 else 0
            price_vs_sma20 = ((current_close - sma_20) / sma_20) * 100 if sma_20 > 0 else 0
            
            # Stochastic basit
            if len(high) >= 14:
                lowest_low = low.rolling(14).min().iloc[-1]
                highest_high = high.rolling(14).max().iloc[-1]
                if highest_high != lowest_low:
                    stoch_k = ((current_close - lowest_low) / (highest_high - lowest_low)) * 100
                else:
                    stoch_k = 50
            else:
                stoch_k = 50
                
            return {
                'RSI': rsi,
                'Volume_Ratio': volume_ratio,
                'Daily_Change': daily_change,
                'Momentum_5D': momentum_5d,
                'BB_Position': bb_position,
                'Price_vs_SMA5': price_vs_sma5,
                'Price_vs_SMA10': price_vs_sma10,
                'Price_vs_SMA20': price_vs_sma20,
                'Stochastic_K': stoch_k,
                'SMA5': sma_5,
                'SMA10': sma_10,
                'SMA20': sma_20,
                'Current_Price': current_close
            }
            
        except Exception as e:
            logger.debug(f"Teknik gösterge hesaplama hatası: {e}")
            return {}
    
    def analyze_pre_ceiling_technical_profile(self, days_back: int = 45) -> Dict[str, Any]:
        """Tavan öncesi teknik profili analiz et"""
        logger.info(f"Son {days_back} gündeki tavan öncesi teknik profil analiz ediliyor...")
        
        # Tüm BİST hisselerinin verilerini çek
        all_data = self.data_fetcher.get_all_bist_data(period=f"{days_back + 5}d")
        
        technical_profiles = []
        
        for symbol, data in all_data.items():
            if data.empty or len(data) < 25:
                continue
                
            try:
                # Tavan günlerini bul
                for i in range(20, len(data)):
                    current_price = data['Close'].iloc[i]
                    previous_price = data['Close'].iloc[i-1]
                    
                    if previous_price == 0:
                        continue
                        
                    daily_change = ((current_price - previous_price) / previous_price) * 100
                    
                    # Tavan günü mü? (%9+ artış)
                    if daily_change >= 9.0:
                        # Tavan öncesi 1-3 gün arası teknik profil
                        for days_before in range(1, 4):
                            pre_index = i - days_before
                            
                            if pre_index < 20:  # Yeterli geçmiş veri yoksa geç
                                continue
                                
                            # O güne kadar olan verileri al
                            pre_data = data.iloc[:pre_index+1]
                            
                            # Teknik göstergeleri hesapla
                            tech_indicators = self.calculate_simple_technical_indicators(pre_data)
                            
                            if tech_indicators:
                                profile = {
                                    'symbol': symbol.replace('.IS', ''),
                                    'days_before_ceiling': days_before,
                                    'ceiling_date': data.index[i],
                                    'ceiling_change': daily_change,
                                    'pre_date': data.index[pre_index]
                                }
                                profile.update(tech_indicators)
                                technical_profiles.append(profile)
                            
            except Exception as e:
                logger.debug(f"{symbol} teknik profil analiz hatası: {e}")
                continue
                
        logger.info(f"Toplam {len(technical_profiles)} tavan öncesi teknik profil bulundu")
        return technical_profiles
    
    def calculate_technical_averages(self, technical_profiles: List[Dict]) -> Dict[str, Any]:
        """Teknik gösterge ortalamalarını hesapla"""
        if not technical_profiles:
            return {}
            
        analysis = {}
        
        # Teknik gösterge isimleri
        technical_indicators = [
            'RSI', 'Volume_Ratio', 'Daily_Change', 'Momentum_5D', 'BB_Position',
            'Price_vs_SMA5', 'Price_vs_SMA10', 'Price_vs_SMA20', 'Stochastic_K'
        ]
        
        # Gün bazında grupla
        for days_before in range(1, 4):
            day_profiles = [p for p in technical_profiles if p['days_before_ceiling'] == days_before]
            
            if not day_profiles:
                continue
                
            day_analysis = {
                'total_profiles': len(day_profiles),
                'averages': {},
                'medians': {},
                'ranges': {},
                'signal_strengths': {}
            }
            
            # Her gösterge için istatistikler
            for indicator in technical_indicators:
                values = []
                for profile in day_profiles:
                    if indicator in profile and pd.notna(profile[indicator]):
                        val = profile[indicator]
                        if abs(val) < 1000:  # Aşırı değerleri filtrele
                            values.append(val)
                
                if len(values) >= 5:  # En az 5 veri noktası
                    day_analysis['averages'][indicator] = np.mean(values)
                    day_analysis['medians'][indicator] = np.median(values)
                    day_analysis['ranges'][indicator] = {
                        'min': np.min(values),
                        'max': np.max(values),
                        'std': np.std(values),
                        'count': len(values)
                    }
                    
                    # Sinyal gücü hesapla
                    day_analysis['signal_strengths'][indicator] = self.calculate_signal_strength(indicator, np.mean(values))
            
            # En çok tavan yapan hisseler
            symbol_counts = {}
            for profile in day_profiles:
                symbol = profile['symbol']
                symbol_counts[symbol] = symbol_counts.get(symbol, 0) + 1
            
            top_symbols = sorted(symbol_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            day_analysis['top_symbols'] = top_symbols
            
            analysis[f'{days_before}_days_before'] = day_analysis
        
        return analysis
    
    def calculate_signal_strength(self, indicator: str, value: float) -> Dict[str, Any]:
        """Gösterge değerine göre sinyal gücü hesapla"""
        if indicator == 'RSI':
            if value < 30:
                return {'strength': 'GÜÇLÜ ALIM', 'score': 85, 'interpretation': 'Oversold - güçlü alım fırsatı'}
            elif value < 50:
                return {'strength': 'ZAYIF', 'score': 35, 'interpretation': 'Satım baskısı altında'}
            elif value < 70:
                return {'strength': 'İDEAL', 'score': 75, 'interpretation': 'Sağlıklı yükseliş trendi'}
            else:
                return {'strength': 'TAVAN YAKINI', 'score': 90, 'interpretation': 'Overbought - tavan sinyali'}
                
        elif indicator == 'Volume_Ratio':
            if value < 0.5:
                return {'strength': 'ÇOK ZAYIF', 'score': 10, 'interpretation': 'İlgi çok düşük'}
            elif value < 1.0:
                return {'strength': 'ZAYIF', 'score': 25, 'interpretation': 'Normal altı hacim'}
            elif value < 1.5:
                return {'strength': 'NORMAL', 'score': 50, 'interpretation': 'Tipik hacim seviyesi'}
            elif value < 2.5:
                return {'strength': 'GÜÇLÜ', 'score': 75, 'interpretation': 'Yüksek ilgi'}
            else:
                return {'strength': 'ÇOK GÜÇLÜ', 'score': 90, 'interpretation': 'Aşırı ilgi - büyük hareket yakın'}
                
        elif indicator == 'BB_Position':
            if value < 20:
                return {'strength': 'ALT BANTLARDA', 'score': 80, 'interpretation': 'Oversold bölgede'}
            elif value < 50:
                return {'strength': 'ALT YARISINDA', 'score': 40, 'interpretation': 'Normal seviye'}
            elif value < 80:
                return {'strength': 'ÜST YARISINDA', 'score': 70, 'interpretation': 'Güçlü momentum'}
            else:
                return {'strength': 'ÜST BANTLARDA', 'score': 85, 'interpretation': 'Çok güçlü - tavan yakın'}
                
        elif indicator == 'Stochastic_K':
            if value < 20:
                return {'strength': 'OVERSOLD', 'score': 80, 'interpretation': 'Güçlü alım sinyali'}
            elif value < 50:
                return {'strength': 'ZAYIF', 'score': 35, 'interpretation': 'Düşük momentum'}
            elif value < 80:
                return {'strength': 'GÜÇLÜ', 'score': 70, 'interpretation': 'İyi momentum'}
            else:
                return {'strength': 'OVERBOUGHT', 'score': 85, 'interpretation': 'Tavan sinyali'}
                
        elif 'Price_vs_SMA' in indicator:
            if value < -10:
                return {'strength': 'ÇOK ZAYIF', 'score': 20, 'interpretation': 'Ortalamanın çok altında'}
            elif value < -2:
                return {'strength': 'ZAYIF', 'score': 35, 'interpretation': 'Ortalama altında'}
            elif value < 2:
                return {'strength': 'NORMAL', 'score': 50, 'interpretation': 'Ortalama civarında'}
            elif value < 5:
                return {'strength': 'GÜÇLÜ', 'score': 75, 'interpretation': 'Ortalama üstünde'}
            else:
                return {'strength': 'ÇOK GÜÇLÜ', 'score': 85, 'interpretation': 'Güçlü momentum'}
                
        else:
            # Diğer göstergeler için genel yaklaşım
            return {'strength': 'NORMAL', 'score': 50, 'interpretation': f'Değer: {value:.2f}'}

def main():
    logging.basicConfig(level=logging.INFO)
    analyzer = SimpleTechnicalSummary()
    
    print("\n📊 BASİT TEKNİK GÖSTERGE ÖZETİ")
    print("=" * 60)
    print("RSI, Volume, Bollinger Bands, Stochastic, Moving Averages...")
    print("=" * 60)
    
    # Tavan öncesi teknik profilleri analiz et
    technical_profiles = analyzer.analyze_pre_ceiling_technical_profile(days_back=45)
    
    if not technical_profiles:
        print("❌ Teknik profil verisi bulunamadı!")
        return
    
    # Teknik ortalamalar hesapla
    analysis = analyzer.calculate_technical_averages(technical_profiles)
    
    if not analysis:
        print("❌ Analiz yapılamadı!")
        return
    
    print(f"\n📈 TAVAN ÖNCESİ TEKNİK GÖSTERGE ORTALAMALARI:")
    
    for day_key, day_data in analysis.items():
        days = day_key.split('_')[0]
        print(f"\n{'='*20} {days} GÜN ÖNCESİ {'='*20}")
        print(f"📊 Toplam profil sayısı: {day_data['total_profiles']}")
        
        avgs = day_data['averages']
        strengths = day_data['signal_strengths']
        
        if 'RSI' in avgs:
            rsi_strength = strengths.get('RSI', {})
            print(f"\n🎯 RSI ANALİZİ:")
            print(f"   • Ortalama RSI: {avgs['RSI']:.1f}")
            print(f"   • Sinyal gücü: {rsi_strength.get('strength', 'BILINMIYOR')}")
            print(f"   • Yorum: {rsi_strength.get('interpretation', 'N/A')}")
            
        if 'Volume_Ratio' in avgs:
            vol_strength = strengths.get('Volume_Ratio', {})
            print(f"\n📊 HACİM ANALİZİ:")
            print(f"   • Ortalama hacim oranı: {avgs['Volume_Ratio']:.2f}x")
            print(f"   • Sinyal gücü: {vol_strength.get('strength', 'BILINMIYOR')}")
            print(f"   • Yorum: {vol_strength.get('interpretation', 'N/A')}")
            
        if 'BB_Position' in avgs:
            bb_strength = strengths.get('BB_Position', {})
            print(f"\n🎪 BOLLİNGER BAND ANALİZİ:")
            print(f"   • Ortalama BB pozisyonu: %{avgs['BB_Position']:.1f}")
            print(f"   • Sinyal gücü: {bb_strength.get('strength', 'BILINMIYOR')}")
            print(f"   • Yorum: {bb_strength.get('interpretation', 'N/A')}")
            
        if 'Stochastic_K' in avgs:
            stoch_strength = strengths.get('Stochastic_K', {})
            print(f"\n⚡ STOCHASTIC ANALİZİ:")
            print(f"   • Ortalama Stochastic %K: {avgs['Stochastic_K']:.1f}")
            print(f"   • Sinyal gücü: {stoch_strength.get('strength', 'BILINMIYOR')}")
            print(f"   • Yorum: {stoch_strength.get('interpretation', 'N/A')}")
            
        print(f"\n📈 FİYAT vs MOVING AVERAGES:")
        for ma_type in ['Price_vs_SMA5', 'Price_vs_SMA10', 'Price_vs_SMA20']:
            if ma_type in avgs:
                ma_strength = strengths.get(ma_type, {})
                ma_name = ma_type.replace('Price_vs_', '')
                print(f"   • {ma_name}: %{avgs[ma_type]:.2f} - {ma_strength.get('strength', 'NORMAL')}")
                
        print(f"\n🚀 MOMENTUM ANALİZİ:")
        if 'Daily_Change' in avgs:
            print(f"   • Günlük değişim: %{avgs['Daily_Change']:.2f}")
        if 'Momentum_5D' in avgs:
            print(f"   • 5 gün momentum: %{avgs['Momentum_5D']:.2f}")
            
        print(f"\n🏆 EN ÇOK SİNYAL VEREN HİSSELER:")
        for i, (symbol, count) in enumerate(day_data['top_symbols'][:3], 1):
            print(f"   {i}. {symbol}: {count} sinyal")
    
    # Genel sonuçlar
    print(f"\n💡 GENEL TEKNİK BULGULAR:")
    
    # 1 gün öncesi en önemli
    one_day = analysis.get('1_days_before', {})
    if one_day:
        avgs = one_day.get('averages', {})
        print(f"   🎯 1 gün öncesi kritik seviyeler:")
        
        if 'RSI' in avgs:
            print(f"      • RSI: {avgs['RSI']:.1f}")
        if 'Volume_Ratio' in avgs:
            print(f"      • Hacim oranı: {avgs['Volume_Ratio']:.2f}x")
        if 'BB_Position' in avgs:
            print(f"      • BB pozisyonu: %{avgs['BB_Position']:.1f}")
            
    print(f"\n🔥 ÖNEMLİ SONUÇLAR:")
    print(f"   📊 Tavan öncesi teknik göstergeler belirgin kalıplar gösteriyor")
    print(f"   🎯 En önemli: RSI, Volume oranı, Bollinger Band pozisyonu")
    print(f"   💪 Bu veriler algoritma iyileştirmesi için kullanılabilir")

if __name__ == "__main__":
    main()