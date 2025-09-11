#!/usr/bin/env python3
"""
Canlı Sinyal Tarayıcısı
Şu anda tavan öncesi sinyalleri veren tüm BİST hisselerini bulur.
"""

import pandas as pd
import numpy as np
import logging
from typing import List, Dict, Any
from bist_data_fetcher import BISTDataFetcher
from datetime import datetime

logger = logging.getLogger(__name__)

class LiveSignalScanner:
    def __init__(self):
        """Canlı sinyal tarama sistemi"""
        self.data_fetcher = BISTDataFetcher()
        
        # İdeal tavan öncesi teknik profil (bulgularımızdan)
        self.ideal_profile = {
            'RSI': {'min': 64, 'max': 72, 'ideal': 68},
            'Volume_Ratio': {'min': 1.5, 'ideal': 1.6},
            'BB_Position': {'min': 80, 'ideal': 87},
            'Stochastic_K': {'min': 65, 'ideal': 72},
            'Price_vs_SMA20': {'min': 8, 'ideal': 13},
            'Daily_Change': {'min': 2, 'ideal': 4},
            'Momentum_5D': {'min': 5, 'ideal': 10}
        }
        
    def calculate_current_technical_indicators(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Güncel teknik göstergeleri hesapla"""
        if len(data) < 25:
            return {}
            
        try:
            close = data['Close']
            high = data['High']
            low = data['Low']
            volume = data['Volume']
            
            # Son değerler (bugünkü)
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
                
            # Bollinger Band pozisyonu
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
            
            # Stochastic
            if len(high) >= 14:
                lowest_low = low.rolling(14).min().iloc[-1]
                highest_high = high.rolling(14).max().iloc[-1]
                if highest_high != lowest_low:
                    stoch_k = ((current_close - lowest_low) / (highest_high - lowest_low)) * 100
                else:
                    stoch_k = 50
            else:
                stoch_k = 50
            
            # Son 3 günün günlük değişimleri
            recent_changes = []
            for i in range(1, min(4, len(close))):
                if close.iloc[-i-1] > 0:
                    change = ((close.iloc[-i] - close.iloc[-i-1]) / close.iloc[-i-1]) * 100
                    recent_changes.append(change)
            
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
                'Current_Price': current_close,
                'Current_Volume': current_volume,
                'Recent_Changes': recent_changes,
                'Last_Update': data.index[-1]
            }
            
        except Exception as e:
            logger.debug(f"Teknik gösterge hesaplama hatası: {e}")
            return {}
    
    def calculate_signal_score(self, indicators: Dict[str, Any]) -> Dict[str, Any]:
        """Sinyal puanını hesapla"""
        if not indicators:
            return {'total_score': 0, 'signals': {}}
            
        signals = {}
        total_score = 0
        max_possible = 0
        
        # Her gösterge için puan hesapla
        for indicator, thresholds in self.ideal_profile.items():
            if indicator not in indicators:
                continue
                
            value = indicators[indicator]
            
            # Puan hesaplama
            if indicator == 'RSI':
                if thresholds['min'] <= value <= thresholds['max']:
                    score = 100 - abs(value - thresholds['ideal']) * 3
                    signal_type = "MÜKEMMEL" if abs(value - thresholds['ideal']) < 2 else "İYİ"
                elif 60 <= value < thresholds['min']:
                    score = 60
                    signal_type = "NORMAL"
                elif value > thresholds['max']:
                    score = 85  # Overbought ama tavan öncesi normal
                    signal_type = "TAVAN YAKINI"
                else:
                    score = 20
                    signal_type = "ZAYIF"
                    
            elif indicator == 'Volume_Ratio':
                if value >= thresholds['ideal']:
                    score = min(100, 70 + (value - thresholds['ideal']) * 15)
                    signal_type = "GÜÇLÜ" if value < 2.5 else "ÇOK GÜÇLÜ"
                elif value >= thresholds['min']:
                    score = 50 + (value - thresholds['min']) * 20
                    signal_type = "İYİ"
                elif value >= 1.0:
                    score = 30 + (value - 1.0) * 40
                    signal_type = "ZAYIF"
                else:
                    score = 10
                    signal_type = "ÇOK ZAYIF"
                    
            elif indicator == 'BB_Position':
                if value >= thresholds['ideal']:
                    score = 90 + min(10, (value - thresholds['ideal']) * 2)
                    signal_type = "MÜKEMMEL"
                elif value >= thresholds['min']:
                    score = 60 + (value - thresholds['min']) * 4
                    signal_type = "İYİ"
                elif value >= 50:
                    score = 30 + (value - 50) * 1
                    signal_type = "NORMAL"
                else:
                    score = 20
                    signal_type = "ZAYIF"
                    
            elif indicator == 'Stochastic_K':
                if value >= thresholds['ideal']:
                    score = 85 + min(15, (value - thresholds['ideal']) * 1.5)
                    signal_type = "GÜÇLÜ"
                elif value >= thresholds['min']:
                    score = 60 + (value - thresholds['min']) * 3.5
                    signal_type = "İYİ"
                elif value >= 50:
                    score = 40 + (value - 50) * 1.3
                    signal_type = "NORMAL"
                else:
                    score = 20
                    signal_type = "ZAYIF"
                    
            elif indicator == 'Price_vs_SMA20':
                if value >= thresholds['ideal']:
                    score = 85 + min(15, (value - thresholds['ideal']) * 2)
                    signal_type = "MÜKEMMEL"
                elif value >= thresholds['min']:
                    score = 60 + (value - thresholds['min']) * 5
                    signal_type = "İYİ"
                elif value >= 2:
                    score = 40 + (value - 2) * 3.3
                    signal_type = "NORMAL"
                else:
                    score = 20
                    signal_type = "ZAYIF"
                    
            elif 'Change' in indicator or 'Momentum' in indicator:
                if value >= thresholds['ideal']:
                    score = 80 + min(20, (value - thresholds['ideal']) * 2)
                    signal_type = "GÜÇLÜ"
                elif value >= thresholds['min']:
                    score = 50 + (value - thresholds['min']) * 6
                    signal_type = "İYİ"
                elif value >= 0:
                    score = 30 + value * 4
                    signal_type = "NORMAL"
                else:
                    score = 10
                    signal_type = "ZAYIF"
            else:
                score = 50
                signal_type = "NORMAL"
            
            signals[indicator] = {
                'value': value,
                'score': max(0, min(100, score)),
                'signal_type': signal_type
            }
            
            total_score += signals[indicator]['score']
            max_possible += 100
        
        # Bonus puanlar
        bonus_score = 0
        bonus_reasons = []
        
        # Son 3 gün pozitif momentum bonusu
        if 'Recent_Changes' in indicators and len(indicators['Recent_Changes']) >= 2:
            positive_days = sum(1 for change in indicators['Recent_Changes'] if change > 1)
            if positive_days >= 2:
                bonus_score += 10
                bonus_reasons.append(f"Son 3 günde {positive_days} pozitif gün")
        
        # Çok güçlü hacim bonusu
        if indicators.get('Volume_Ratio', 0) > 3:
            bonus_score += 15
            bonus_reasons.append("Çok yüksek hacim")
            
        # Mükemmel RSI bonusu
        if 66 <= indicators.get('RSI', 0) <= 70:
            bonus_score += 10
            bonus_reasons.append("İdeal RSI seviyesi")
        
        final_score = (total_score / max_possible * 100) if max_possible > 0 else 0
        final_score = min(100, final_score + bonus_score)
        
        return {
            'total_score': final_score,
            'signals': signals,
            'bonus_score': bonus_score,
            'bonus_reasons': bonus_reasons,
            'max_possible': max_possible
        }
    
    def scan_all_stocks(self) -> List[Dict[str, Any]]:
        """Tüm BİST hisselerini tara"""
        logger.info("Tüm BİST hisseleri tavan öncesi sinyaller için taranıyor...")
        
        # Son 30 günlük veri al
        all_data = self.data_fetcher.get_all_bist_data(period="30d")
        
        signal_results = []
        
        for symbol, data in all_data.items():
            if data.empty or len(data) < 25:
                continue
                
            try:
                # Güncel teknik göstergeleri hesapla
                indicators = self.calculate_current_technical_indicators(data)
                
                if not indicators:
                    continue
                
                # Sinyal puanını hesapla
                signal_analysis = self.calculate_signal_score(indicators)
                
                # Sadece belirli bir eşiğin üstündeki hisseleri al
                if signal_analysis['total_score'] >= 35:  # En az 35 puan
                    result = {
                        'symbol': symbol.replace('.IS', ''),
                        'current_price': indicators['Current_Price'],
                        'last_update': indicators['Last_Update'],
                        'signal_score': signal_analysis['total_score'],
                        'indicators': indicators,
                        'signal_analysis': signal_analysis
                    }
                    signal_results.append(result)
                    
            except Exception as e:
                logger.debug(f"{symbol} tarama hatası: {e}")
                continue
        
        # Skor bazında sırala
        signal_results.sort(key=lambda x: x['signal_score'], reverse=True)
        
        logger.info(f"Toplam {len(signal_results)} hisse sinyal veriyor")
        return signal_results

def main():
    logging.basicConfig(level=logging.INFO)
    scanner = LiveSignalScanner()
    
    print("\n🔍 CANLI TAVAN ÖNCESİ SİNYAL TARAMASI")
    print("=" * 70)
    print("Bulgular: RSI 64-72, Hacim 1.5x+, BB %80+, Stochastic 65+...")
    print("=" * 70)
    
    # Tüm hisseleri tara
    signal_stocks = scanner.scan_all_stocks()
    
    if not signal_stocks:
        print("❌ Şu anda sinyal veren hisse bulunamadı!")
        return
    
    print(f"\n🎯 SİNYAL VEREN HİSSELER: {len(signal_stocks)} ADET")
    print("=" * 70)
    
    # En iyi 20 hisseyi göster
    top_stocks = signal_stocks[:20]
    
    for i, stock in enumerate(top_stocks, 1):
        symbol = stock['symbol']
        score = stock['signal_score']
        price = stock['current_price']
        indicators = stock['indicators']
        analysis = stock['signal_analysis']
        
        # Skor seviyesi emoji
        if score >= 80:
            score_emoji = "🔥"
            score_level = "MÜKEMMEL"
        elif score >= 70:
            score_emoji = "⚡"
            score_level = "ÇOK İYİ"
        elif score >= 60:
            score_emoji = "✨"
            score_level = "İYİ"
        elif score >= 50:
            score_emoji = "📊"
            score_level = "NORMAL"
        else:
            score_emoji = "💡"
            score_level = "ZAYIF"
        
        print(f"\n{score_emoji} {i}. {symbol} - {score:.1f} PUAN ({score_level})")
        print(f"   💰 Fiyat: {price:.2f} TL")
        
        # Ana sinyaller
        signals = analysis['signals']
        print(f"   📊 Ana Sinyaller:")
        
        if 'RSI' in signals:
            rsi_data = signals['RSI']
            print(f"      • RSI: {rsi_data['value']:.1f} - {rsi_data['signal_type']} ({rsi_data['score']:.0f} puan)")
            
        if 'Volume_Ratio' in signals:
            vol_data = signals['Volume_Ratio']
            print(f"      • Hacim: {vol_data['value']:.2f}x - {vol_data['signal_type']} ({vol_data['score']:.0f} puan)")
            
        if 'BB_Position' in signals:
            bb_data = signals['BB_Position']
            print(f"      • BB Pozisyon: %{bb_data['value']:.1f} - {bb_data['signal_type']} ({bb_data['score']:.0f} puan)")
            
        if 'Stochastic_K' in signals:
            stoch_data = signals['Stochastic_K']
            print(f"      • Stochastic: {stoch_data['value']:.1f} - {stoch_data['signal_type']} ({stoch_data['score']:.0f} puan)")
            
        if 'Price_vs_SMA20' in signals:
            sma_data = signals['Price_vs_SMA20']
            print(f"      • SMA20 üstü: %{sma_data['value']:.1f} - {sma_data['signal_type']} ({sma_data['score']:.0f} puan)")
        
        # Momentum bilgileri
        daily = indicators.get('Daily_Change', 0)
        momentum = indicators.get('Momentum_5D', 0)
        print(f"   🚀 Momentum: Günlük %{daily:.1f}, 5 gün %{momentum:.1f}")
        
        # Bonus puanlar
        if analysis['bonus_score'] > 0:
            print(f"   🎁 Bonus: +{analysis['bonus_score']:.0f} puan ({', '.join(analysis['bonus_reasons'])})")
    
    # Özet istatistikler
    print(f"\n📈 ÖZET İSTATİSTİKLER:")
    print(f"   🎯 Toplam sinyal veren: {len(signal_stocks)} hisse")
    
    # Skor dağılımı
    excellent = len([s for s in signal_stocks if s['signal_score'] >= 80])
    very_good = len([s for s in signal_stocks if 70 <= s['signal_score'] < 80])
    good = len([s for s in signal_stocks if 60 <= s['signal_score'] < 70])
    normal = len([s for s in signal_stocks if 50 <= s['signal_score'] < 60])
    weak = len([s for s in signal_stocks if s['signal_score'] < 50])
    
    print(f"   🔥 Mükemmel (80+): {excellent} hisse")
    print(f"   ⚡ Çok iyi (70-79): {very_good} hisse")
    print(f"   ✨ İyi (60-69): {good} hisse")
    print(f"   📊 Normal (50-59): {normal} hisse")
    print(f"   💡 Zayıf (35-49): {weak} hisse")
    
    # En çok sinyal veren göstergeler
    all_signals = {}
    for stock in signal_stocks:
        for indicator, signal_data in stock['signal_analysis']['signals'].items():
            if signal_data['score'] >= 70:
                all_signals[indicator] = all_signals.get(indicator, 0) + 1
    
    if all_signals:
        print(f"\n🏆 EN GÜÇLÜ SİNYAL VEREN GÖSTERGELER:")
        sorted_signals = sorted(all_signals.items(), key=lambda x: x[1], reverse=True)
        for indicator, count in sorted_signals[:5]:
            print(f"   • {indicator}: {count} hisse")
    
    # Tavan kralları var mı kontrol et
    crown_stocks = ['PINSU', 'ISGSY', 'IZINV', 'GRNYO', 'TRHOL']
    found_crowns = [s for s in signal_stocks if s['symbol'] in crown_stocks]
    
    if found_crowns:
        print(f"\n👑 TAVAN KRALLARI DURUMU:")
        for crown in found_crowns:
            print(f"   🏆 {crown['symbol']}: {crown['signal_score']:.1f} puan")
    
    print(f"\n⚠️ UYARI: Bu analiz sadece teknik göstergelere dayanır.")
    print(f"💡 Yatırım kararları için ek analizler gereklidir.")
    print(f"📅 Son güncelleme: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()