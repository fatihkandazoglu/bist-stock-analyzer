#!/usr/bin/env python3
"""
Önümüzdeki Hafta Tavan Kralları Tahmincisi
Tüm analizleri birleştirerek gelecek haftanın potansiyel tavan krallarını tahmin eder
"""

import pandas as pd
import numpy as np
import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta
from bist_data_fetcher import BISTDataFetcher

logger = logging.getLogger(__name__)

class NextWeekKingsPredictor:
    def __init__(self):
        """Gelecek hafta kralları tahmin sistemi"""
        self.data_fetcher = BISTDataFetcher()
        
        # Mevcut tavan kralları
        self.current_kings = ['PINSU', 'IZINV', 'ISGSY', 'GRNYO', 'TRHOL']
        
        # Güçlü adaylar (8+ tavan yapmış)
        self.strong_candidates = ['MRGYO', 'YESIL', 'MAKTK', 'PATEK', 'HUBVC', 'KAPLM', 'PCILT']
        
        # Fresh adaylar (yeni keşfedilenler)
        self.fresh_candidates = ['AKSA', 'ADGYO', 'KARSN', 'GLYHO', 'PENTA']
        
        # Bugün güçlü sinyal verenler (100 puan alanlar)
        self.today_strong_signals = ['KAPLM', 'PENTA', 'PCILT', 'BARMA', 'GRNYO', 'FLAP']
        
        # Tahmin ağırlıkları
        self.prediction_weights = {
            'current_signal_strength': 0.25,    # Güncel sinyal gücü
            'historical_performance': 0.20,     # Geçmiş performans
            'recent_momentum': 0.20,            # Son dönem momentum
            'technical_readiness': 0.15,        # Teknik hazırlık
            'pattern_alignment': 0.10,          # Pattern uyumu
            'market_timing': 0.10              # Piyasa zamanlaması
        }
    
    def calculate_next_week_probability(self, symbol: str, data: pd.DataFrame, category: str) -> Dict[str, Any]:
        """Gelecek hafta tavan yapma olasılığını hesapla"""
        if len(data) < 20:
            return {}
            
        try:
            close = data['Close']
            volume = data['Volume']
            
            current_price = close.iloc[-1]
            current_volume = volume.iloc[-1]
            
            # 1. Güncel sinyal gücü
            signal_strength = self.calculate_current_signal_strength(data)
            
            # 2. Geçmiş performans skoru
            historical_score = self.calculate_historical_performance(symbol, data, category)
            
            # 3. Son dönem momentum
            momentum_score = self.calculate_recent_momentum(data)
            
            # 4. Teknik hazırlık seviyesi
            technical_readiness = self.calculate_technical_readiness(data)
            
            # 5. Pattern uyumu
            pattern_score = self.calculate_pattern_alignment(data)
            
            # 6. Piyasa zamanlaması
            timing_score = self.calculate_market_timing(symbol, data)
            
            # Ağırlıklı toplam
            weights = self.prediction_weights
            total_probability = (
                signal_strength * weights['current_signal_strength'] +
                historical_score * weights['historical_performance'] +
                momentum_score * weights['recent_momentum'] +
                technical_readiness * weights['technical_readiness'] +
                pattern_score * weights['pattern_alignment'] +
                timing_score * weights['market_timing']
            )
            
            # Kategori bonusları
            category_bonus = self.get_category_bonus(symbol, category)
            final_probability = min(100, total_probability + category_bonus)
            
            return {
                'probability': final_probability,
                'signal_strength': signal_strength,
                'historical_score': historical_score,
                'momentum_score': momentum_score,
                'technical_readiness': technical_readiness,
                'pattern_score': pattern_score,
                'timing_score': timing_score,
                'category_bonus': category_bonus,
                'category': category,
                'current_price': current_price
            }
            
        except Exception as e:
            logger.debug(f"{symbol} gelecek hafta analiz hatası: {e}")
            return {}
    
    def calculate_current_signal_strength(self, data: pd.DataFrame) -> float:
        """Güncel sinyal gücü (bugünkü analiz sonuçlarından)"""
        close = data['Close']
        volume = data['Volume']
        high = data['High']
        low = data['Low']
        
        current_close = close.iloc[-1]
        current_volume = volume.iloc[-1]
        
        score = 0
        
        # RSI
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        
        if len(gain) >= 14 and loss.iloc[-1] != 0:
            rs = gain.iloc[-1] / loss.iloc[-1]
            rsi = 100 - (100 / (1 + rs))
            
            if 65 <= rsi <= 75:
                score += 25
            elif 60 <= rsi <= 80:
                score += 20
            elif rsi > 80:
                score += 15  # Overbought ama tavan yakını
        
        # Volume
        volume_sma = volume.rolling(20).mean().iloc[-1] if len(volume) >= 20 else current_volume
        volume_ratio = current_volume / volume_sma if volume_sma > 0 else 1
        
        if volume_ratio >= 2.0:
            score += 25
        elif volume_ratio >= 1.5:
            score += 20
        elif volume_ratio >= 1.0:
            score += 10
        
        # Bollinger Band pozisyonu
        if len(close) >= 20:
            sma_20 = close.rolling(20).mean().iloc[-1]
            bb_std = close.rolling(20).std().iloc[-1]
            bb_upper = sma_20 + (bb_std * 2)
            bb_lower = sma_20 - (bb_std * 2)
            bb_position = (current_close - bb_lower) / (bb_upper - bb_lower) * 100 if bb_upper != bb_lower else 50
            
            if bb_position >= 80:
                score += 25
            elif bb_position >= 60:
                score += 15
        
        # Günlük momentum
        if len(close) >= 2:
            daily_change = ((current_close - close.iloc[-2]) / close.iloc[-2]) * 100
            if daily_change >= 5:
                score += 15
            elif daily_change >= 2:
                score += 10
            elif daily_change >= 0:
                score += 5
        
        return min(100, score)
    
    def calculate_historical_performance(self, symbol: str, data: pd.DataFrame, category: str) -> float:
        """Geçmiş performans skoru"""
        score = 0
        
        # Kategori bazlı skor
        if category == "current_king":
            score += 50  # Mevcut krallar yüksek skor
        elif category == "strong_candidate":
            score += 40  # Güçlü adaylar
        elif category == "fresh_candidate":
            score += 20  # Fresh adaylar düşük ama umutlu
        
        # Geçmiş tavan sayısını hesapla
        ceiling_count = 0
        for i in range(1, len(data)):
            if data['Close'].iloc[i-1] > 0:
                daily_change = ((data['Close'].iloc[i] - data['Close'].iloc[i-1]) / data['Close'].iloc[i-1]) * 100
                if daily_change >= 9.0:
                    ceiling_count += 1
        
        # Tavan sayısı bonusu
        if ceiling_count >= 10:
            score += 30
        elif ceiling_count >= 5:
            score += 20
        elif ceiling_count >= 2:
            score += 10
        
        return min(100, score)
    
    def calculate_recent_momentum(self, data: pd.DataFrame) -> float:
        """Son dönem momentum"""
        close = data['Close']
        
        if len(close) < 10:
            return 0
        
        score = 0
        
        # Son 5 gün momentum
        momentum_5d = ((close.iloc[-1] - close.iloc[-6]) / close.iloc[-6]) * 100
        if momentum_5d >= 15:
            score += 30
        elif momentum_5d >= 10:
            score += 25
        elif momentum_5d >= 5:
            score += 20
        elif momentum_5d >= 0:
            score += 10
        
        # Son 10 gün momentum
        momentum_10d = ((close.iloc[-1] - close.iloc[-11]) / close.iloc[-11]) * 100
        if momentum_10d >= 25:
            score += 25
        elif momentum_10d >= 15:
            score += 20
        elif momentum_10d >= 5:
            score += 15
        elif momentum_10d >= 0:
            score += 5
        
        # Pozitif günler sayısı (son 10 gün)
        positive_days = 0
        for i in range(len(close)-10, len(close)):
            if i > 0 and close.iloc[i-1] > 0:
                change = ((close.iloc[i] - close.iloc[i-1]) / close.iloc[i-1]) * 100
                if change > 0:
                    positive_days += 1
        
        if positive_days >= 7:
            score += 20
        elif positive_days >= 5:
            score += 15
        elif positive_days >= 3:
            score += 10
        
        return min(100, score)
    
    def calculate_technical_readiness(self, data: pd.DataFrame) -> float:
        """Teknik hazırlık seviyesi"""
        close = data['Close']
        high = data['High']
        low = data['Low']
        
        if len(close) < 20:
            return 0
        
        score = 0
        current_close = close.iloc[-1]
        
        # Moving average pozisyonu
        sma_5 = close.rolling(5).mean().iloc[-1]
        sma_10 = close.rolling(10).mean().iloc[-1] 
        sma_20 = close.rolling(20).mean().iloc[-1]
        
        # Fiyat MA'ların üstünde mi?
        if current_close > sma_5 > sma_10 > sma_20:
            score += 30
        elif current_close > sma_5 > sma_10:
            score += 20
        elif current_close > sma_5:
            score += 10
        
        # Stochastic
        if len(high) >= 14:
            lowest_low = low.rolling(14).min().iloc[-1]
            highest_high = high.rolling(14).max().iloc[-1]
            if highest_high != lowest_low:
                stoch_k = ((current_close - lowest_low) / (highest_high - lowest_low)) * 100
                
                if 70 <= stoch_k <= 90:
                    score += 25
                elif 60 <= stoch_k <= 95:
                    score += 20
                elif stoch_k > 95:
                    score += 15
        
        # Resistance yakınlığı
        recent_high = high.iloc[-20:].max()
        resistance_proximity = (current_close / recent_high) * 100
        
        if resistance_proximity >= 95:
            score += 25
        elif resistance_proximity >= 90:
            score += 20
        elif resistance_proximity >= 85:
            score += 15
        
        return min(100, score)
    
    def calculate_pattern_alignment(self, data: pd.DataFrame) -> float:
        """Pattern uyumu (tavan öncesi sinyaller)"""
        close = data['Close']
        volume = data['Volume']
        
        if len(close) < 10:
            return 0
        
        score = 0
        
        # Son 3 günün pattern'i
        recent_changes = []
        for i in range(len(close)-3, len(close)):
            if i > 0 and close.iloc[i-1] > 0:
                change = ((close.iloc[i] - close.iloc[i-1]) / close.iloc[i-1]) * 100
                recent_changes.append(change)
        
        # Pozitif seri var mı?
        positive_streak = 0
        for change in reversed(recent_changes):
            if change > 0:
                positive_streak += 1
            else:
                break
        
        if positive_streak >= 2:
            score += 30
        elif positive_streak >= 1:
            score += 20
        
        # Volume pattern (artış trendi)
        if len(volume) >= 5:
            recent_volumes = volume.iloc[-5:].tolist()
            volume_trend = 0
            for i in range(1, len(recent_volumes)):
                if recent_volumes[i] > recent_volumes[i-1]:
                    volume_trend += 1
            
            if volume_trend >= 3:
                score += 25
            elif volume_trend >= 2:
                score += 15
        
        # Volatilite uygunluğu
        if len(close) >= 10:
            volatility = close.iloc[-10:].pct_change().std() * 100
            if 3 <= volatility <= 7:  # Optimal volatilite
                score += 25
            elif 2 <= volatility <= 10:
                score += 15
        
        return min(100, score)
    
    def calculate_market_timing(self, symbol: str, data: pd.DataFrame) -> float:
        """Piyasa zamanlaması"""
        score = 0
        
        # Hafta içi pozisyonu (Pazartesi-Perşembe tavan sıklığı yüksek)
        current_day = datetime.now().weekday()  # 0=Pazartesi, 6=Pazar
        
        if current_day <= 3:  # Pazartesi-Perşembe
            score += 25
        elif current_day == 4:  # Cuma
            score += 15
        
        # Son tavan üzerinden geçen süre
        last_ceiling_days = self.days_since_last_ceiling(data)
        
        if 10 <= last_ceiling_days <= 30:  # Optimal aralık
            score += 30
        elif 5 <= last_ceiling_days <= 45:
            score += 20
        elif last_ceiling_days >= 60:
            score += 10  # Çok uzun süre geçmiş, sürpriz olabilir
        
        # Bugünkü sinyaller (bugün güçlü sinyal veriyorsa)
        if symbol in self.today_strong_signals:
            score += 25
        
        return min(100, score)
    
    def days_since_last_ceiling(self, data: pd.DataFrame) -> int:
        """Son tavandan beri geçen gün sayısı"""
        for i in range(len(data)-1, 0, -1):
            if data['Close'].iloc[i-1] > 0:
                daily_change = ((data['Close'].iloc[i] - data['Close'].iloc[i-1]) / data['Close'].iloc[i-1]) * 100
                if daily_change >= 9.0:
                    return len(data) - i
        return 999  # Hiç tavan yapmamış
    
    def get_category_bonus(self, symbol: str, category: str) -> float:
        """Kategori bonus puanları"""
        bonus = 0
        
        # Bugün güçlü sinyal verme bonusu
        if symbol in self.today_strong_signals:
            bonus += 10
        
        # Kategori özel bonusları
        if category == "current_king" and symbol in ['GRNYO', 'TRHOL']:
            bonus += 5  # Son zamanlarda aktif krallar
        elif category == "strong_candidate":
            bonus += 8  # Güçlü adaylar yüksek potansiyel
        elif category == "fresh_candidate":
            bonus += 12  # Fresh adaylar sürpriz potansiyeli
        
        return bonus
    
    def predict_next_week_kings(self) -> List[Dict[str, Any]]:
        """Gelecek haftanın krallarını tahmin et"""
        logger.info("Gelecek haftanın potansiyel tavan kralları tahmin ediliyor...")
        
        # 30 günlük veri al
        all_data = self.data_fetcher.get_all_bist_data(period="30d")
        
        predictions = []
        
        # Tüm adayları analiz et
        all_candidates = {
            **{symbol: "current_king" for symbol in self.current_kings},
            **{symbol: "strong_candidate" for symbol in self.strong_candidates},
            **{symbol: "fresh_candidate" for symbol in self.fresh_candidates}
        }
        
        for symbol, category in all_candidates.items():
            symbol_with_suffix = symbol + '.IS'
            
            if symbol_with_suffix not in all_data:
                continue
                
            data = all_data[symbol_with_suffix]
            if data.empty or len(data) < 20:
                continue
            
            try:
                prediction = self.calculate_next_week_probability(symbol, data, category)
                
                if prediction and prediction['probability'] >= 30:  # Minimum %30 olasılık
                    prediction['symbol'] = symbol
                    predictions.append(prediction)
                    
            except Exception as e:
                logger.debug(f"{symbol} tahmin hatası: {e}")
                continue
        
        # Olasılığa göre sırala
        predictions.sort(key=lambda x: x['probability'], reverse=True)
        
        logger.info(f"Toplam {len(predictions)} aday için tahmin yapıldı")
        return predictions

def main():
    logging.basicConfig(level=logging.INFO)
    
    predictor = NextWeekKingsPredictor()
    
    print("\n🔮 ÖNÜMÜZDEKİ HAFTA TAVAN KRALLARI TAHMİNİ")
    print("=" * 80)
    print("📊 Tüm analizleri birleştiren kapsamlı tahmin sistemi")
    print("🎯 Mevcut krallar + Güçlü adaylar + Fresh adaylar + Güncel sinyaller")
    print("=" * 80)
    
    # Tahminleri yap
    predictions = predictor.predict_next_week_kings()
    
    if not predictions:
        print("❌ Tahmin yapılabilecek aday bulunamadı!")
        return
    
    print(f"\n👑 GELECEKHAFTANıN POTANSİYEL KRALLARI:")
    print(f"Toplam {len(predictions)} aday analiz edildi")
    
    # En yüksek olasılıklı 15 adayı göster
    top_predictions = predictions[:15]
    
    for i, pred in enumerate(top_predictions, 1):
        symbol = pred['symbol']
        probability = pred['probability']
        category = pred['category']
        price = pred['current_price']
        
        # Olasılık emoji
        if probability >= 80:
            emoji = "🔥"
            level = "ÇOK YÜKSEK"
        elif probability >= 70:
            emoji = "⚡"
            level = "YÜKSEK"
        elif probability >= 60:
            emoji = "✨"
            level = "İYİ"
        elif probability >= 50:
            emoji = "📊"
            level = "ORTA"
        else:
            emoji = "💡"
            level = "DÜŞÜK"
        
        # Kategori çevirisi
        category_tr = {
            "current_king": "Mevcut Kral",
            "strong_candidate": "Güçlü Aday", 
            "fresh_candidate": "Fresh Aday"
        }.get(category, category)
        
        print(f"\n{emoji} {i}. {symbol} - %{probability:.1f} OLASILIK ({level})")
        print(f"   📊 Kategori: {category_tr}")
        print(f"   💰 Fiyat: {price:.2f} TL")
        
        # Skor detayları
        print(f"   🔧 Analiz Detayı:")
        print(f"      • Güncel sinyal: {pred['signal_strength']:.1f}/100")
        print(f"      • Geçmiş performans: {pred['historical_score']:.1f}/100")
        print(f"      • Son momentum: {pred['momentum_score']:.1f}/100")
        print(f"      • Teknik hazırlık: {pred['technical_readiness']:.1f}/100")
        print(f"      • Pattern uyumu: {pred['pattern_score']:.1f}/100")
        print(f"      • Piyasa zamanlaması: {pred['timing_score']:.1f}/100")
        
        if pred['category_bonus'] > 0:
            print(f"      • Kategori bonusu: +{pred['category_bonus']:.1f}")
    
    # Kategori özeti
    print(f"\n📈 KATEGORİ ÖZETİ:")
    category_stats = {}
    for pred in predictions:
        cat = pred['category']
        category_stats[cat] = category_stats.get(cat, 0) + 1
    
    category_names = {
        "current_king": "Mevcut Krallar",
        "strong_candidate": "Güçlü Adaylar",
        "fresh_candidate": "Fresh Adaylar"
    }
    
    for cat, count in category_stats.items():
        cat_name = category_names.get(cat, cat)
        print(f"   • {cat_name}: {count} aday")
    
    # En yüksek olasılıklı 5
    print(f"\n🏆 EN YÜKSEK OLASILIKLI 5 ADAY:")
    for i, pred in enumerate(top_predictions[:5], 1):
        symbol = pred['symbol']
        prob = pred['probability']
        cat = category_names.get(pred['category'], pred['category'])
        
        print(f"   {i}. {symbol}: %{prob:.1f} ({cat})")
    
    # Haftalık tahmin
    print(f"\n📅 HAFTALIK TAHMİN:")
    
    very_high = len([p for p in predictions if p['probability'] >= 80])
    high = len([p for p in predictions if 70 <= p['probability'] < 80])
    good = len([p for p in predictions if 60 <= p['probability'] < 70])
    
    print(f"   🔥 Çok yüksek olasılık (80%+): {very_high} hisse")
    print(f"   ⚡ Yüksek olasılık (70-79%): {high} hisse")
    print(f"   ✨ İyi olasılık (60-69%): {good} hisse")
    
    if very_high > 0:
        print(f"\n🎯 ÖNERİ: {very_high} hisse çok yüksek olasılıkla gelecek hafta tavan yapabilir!")
    elif high > 0:
        print(f"\n🎯 ÖNERİ: {high} hisse yüksek olasılıkla gelecek hafta tavan yapabilir!")
    else:
        print(f"\n💡 ÖNERİ: Gelecek hafta orta seviyeli fırsatlar olabilir.")
    
    print(f"\n⚠️ UYARI: Bu tahminler teknik analize dayalıdır.")
    print(f"💡 Piyasa koşulları ve haberler sonuçları etkileyebilir.")

if __name__ == "__main__":
    main()