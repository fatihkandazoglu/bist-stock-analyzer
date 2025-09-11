#!/usr/bin/env python3
"""
Fresh Tavan Kralı Adayı Bulucu
Henüz tavan kralı olmamış ama üst üste tavan yapma potansiyeli gösteren yeni adayları bulur
"""

import pandas as pd
import numpy as np
import logging
from typing import List, Dict, Any
from bist_data_fetcher import BISTDataFetcher
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class FreshCeilingCandidateFinder:
    def __init__(self):
        """Yeni tavan kralı adaylarını bulan sistem"""
        self.data_fetcher = BISTDataFetcher()
        
        # Bilinen tavan kralları ve mevcut güçlü adaylar (bunları dışla)
        self.exclude_stocks = [
            'PINSU', 'IZINV', 'ISGSY', 'GRNYO', 'TRHOL',  # Mevcut krallar
            'MRGYO', 'YESIL', 'MAKTK', 'PATEK', 'HUBVC'   # Güçlü adaylar
        ]
        
        # Fresh aday kriterleri
        self.fresh_criteria = {
            'max_historical_ceilings': 6,    # Max 6 tavan (henüz kral değil)
            'min_recent_activity': 2,        # Son 60 günde en az 2 güçlü hareket
            'min_current_signal': 60,        # Güncel sinyal gücü min 60
            'momentum_threshold': 5,         # %5+ momentum
            'volume_spike_threshold': 1.8,   # 1.8x hacim artışı
            'technical_strength': 70         # Teknik güç min 70
        }
    
    def analyze_fresh_potential(self, symbol: str, data: pd.DataFrame) -> Dict[str, Any]:
        """Fresh adaylık potansiyeli analiz et"""
        if len(data) < 30:
            return {}
            
        try:
            # Geçmiş tavan sayısı
            historical_ceilings = self.count_historical_ceilings(data)
            
            # Son dönem aktivitesi
            recent_activity = self.analyze_recent_activity(data, days=60)
            
            # Güncel teknik durum
            current_technical = self.calculate_current_technical(data)
            
            # Pattern analizi
            pattern_score = self.analyze_ceiling_pattern(data)
            
            # Fresh score hesapla
            fresh_score = self.calculate_fresh_score({
                'historical_ceilings': historical_ceilings,
                'recent_activity': recent_activity,
                'current_technical': current_technical,
                'pattern_score': pattern_score
            })
            
            return {
                'historical_ceilings': historical_ceilings,
                'recent_activity': recent_activity,
                'current_technical': current_technical,
                'pattern_score': pattern_score,
                'fresh_score': fresh_score,
                'symbol': symbol
            }
            
        except Exception as e:
            logger.debug(f"{symbol} fresh analiz hatası: {e}")
            return {}
    
    def count_historical_ceilings(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Tarihi tavan sayısını hesapla"""
        ceiling_count = 0
        strong_moves = 0
        ceiling_dates = []
        
        for i in range(1, len(data)):
            current_price = data['Close'].iloc[i]
            previous_price = data['Close'].iloc[i-1]
            
            if previous_price == 0:
                continue
                
            daily_change = ((current_price - previous_price) / previous_price) * 100
            
            if daily_change >= 9.0:  # Tavan
                ceiling_count += 1
                ceiling_dates.append({
                    'date': data.index[i],
                    'change': daily_change
                })
            elif daily_change >= 5.0:  # Güçlü hareket
                strong_moves += 1
        
        return {
            'ceiling_count': ceiling_count,
            'strong_moves': strong_moves,
            'total_events': ceiling_count + strong_moves,
            'recent_ceilings': ceiling_dates[-3:] if ceiling_dates else []
        }
    
    def analyze_recent_activity(self, data: pd.DataFrame, days: int = 60) -> Dict[str, Any]:
        """Son dönem aktivite analizi"""
        if len(data) < days:
            recent_data = data
        else:
            recent_data = data.iloc[-days:]
        
        strong_days = 0
        volume_spikes = 0
        positive_momentum_days = 0
        max_single_day = 0
        
        close = recent_data['Close']
        volume = recent_data['Volume']
        avg_volume = volume.mean()
        
        for i in range(1, len(recent_data)):
            current_price = close.iloc[i]
            previous_price = close.iloc[i-1]
            current_volume = volume.iloc[i]
            
            if previous_price == 0:
                continue
                
            daily_change = ((current_price - previous_price) / previous_price) * 100
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
            
            # Güçlü günler (4%+ artış)
            if daily_change >= 4.0:
                strong_days += 1
                max_single_day = max(max_single_day, daily_change)
            
            # Pozitif momentum günleri
            if daily_change >= 1.0:
                positive_momentum_days += 1
            
            # Hacim patlamaları
            if volume_ratio >= 1.8:
                volume_spikes += 1
        
        # Son 10 günün trendi
        if len(close) >= 10:
            recent_trend = ((close.iloc[-1] - close.iloc[-10]) / close.iloc[-10]) * 100
        else:
            recent_trend = 0
        
        return {
            'strong_days': strong_days,
            'volume_spikes': volume_spikes,
            'positive_momentum_days': positive_momentum_days,
            'max_single_day': max_single_day,
            'recent_trend': recent_trend,
            'activity_ratio': strong_days / (days / 10)  # Her 10 günde kaç güçlü gün
        }
    
    def calculate_current_technical(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Güncel teknik analiz"""
        if len(data) < 20:
            return {}
            
        close = data['Close']
        high = data['High']
        low = data['Low']
        volume = data['Volume']
        
        current_close = close.iloc[-1]
        current_volume = volume.iloc[-1]
        
        # RSI
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        
        if len(gain) >= 14 and loss.iloc[-1] != 0:
            rs = gain.iloc[-1] / loss.iloc[-1]
            rsi = 100 - (100 / (1 + rs))
        else:
            rsi = 50
        
        # Volume momentum
        volume_sma = volume.rolling(20).mean().iloc[-1]
        volume_ratio = current_volume / volume_sma if volume_sma > 0 else 1
        
        # Price momentum
        if len(close) >= 10:
            momentum_10d = ((current_close - close.iloc[-10]) / close.iloc[-10]) * 100
        else:
            momentum_10d = 0
        
        # Bollinger Bands
        sma_20 = close.rolling(20).mean().iloc[-1]
        bb_std = close.rolling(20).std().iloc[-1]
        bb_upper = sma_20 + (bb_std * 2)
        bb_lower = sma_20 - (bb_std * 2)
        bb_position = (current_close - bb_lower) / (bb_upper - bb_lower) * 100 if bb_upper != bb_lower else 50
        
        # Stochastic
        if len(high) >= 14:
            lowest_low = low.rolling(14).min().iloc[-1]
            highest_high = high.rolling(14).max().iloc[-1]
            stoch_k = ((current_close - lowest_low) / (highest_high - lowest_low)) * 100 if highest_high != lowest_low else 50
        else:
            stoch_k = 50
        
        # Teknik güç skoru
        technical_score = 0
        
        # RSI skoru (60-75 ideal)
        if 60 <= rsi <= 75:
            technical_score += 25
        elif 50 <= rsi <= 85:
            technical_score += 15
        
        # Volume skoru
        if volume_ratio >= 2.0:
            technical_score += 20
        elif volume_ratio >= 1.5:
            technical_score += 15
        
        # Momentum skoru
        if momentum_10d >= 10:
            technical_score += 20
        elif momentum_10d >= 5:
            technical_score += 15
        elif momentum_10d >= 0:
            technical_score += 10
        
        # BB pozisyon skoru
        if bb_position >= 80:
            technical_score += 20
        elif bb_position >= 60:
            technical_score += 15
        
        # Stochastic skoru
        if stoch_k >= 70:
            technical_score += 15
        elif stoch_k >= 50:
            technical_score += 10
        
        return {
            'RSI': rsi,
            'volume_ratio': volume_ratio,
            'momentum_10d': momentum_10d,
            'bb_position': bb_position,
            'stochastic_k': stoch_k,
            'technical_score': technical_score,
            'current_price': current_close
        }
    
    def analyze_ceiling_pattern(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Tavan pattern analizi"""
        close = data['Close']
        
        # Son 30 günde volatilite
        if len(close) >= 30:
            recent_volatility = close.iloc[-30:].pct_change().std() * 100
        else:
            recent_volatility = 0
        
        # Trend tutarlılığı
        if len(close) >= 20:
            sma_5 = close.rolling(5).mean().iloc[-1]
            sma_20 = close.rolling(20).mean().iloc[-1]
            trend_alignment = (sma_5 > sma_20)
        else:
            trend_alignment = False
        
        # Breakout potansiyeli
        if len(close) >= 20:
            recent_high = close.iloc[-20:].max()
            current_price = close.iloc[-1]
            breakout_proximity = (current_price / recent_high) * 100
        else:
            breakout_proximity = 0
        
        # Pattern skoru
        pattern_score = 0
        
        # Volatilite uygun mu? (çok düşük veya çok yüksek değil)
        if 3 <= recent_volatility <= 8:
            pattern_score += 20
        elif 2 <= recent_volatility <= 10:
            pattern_score += 10
        
        # Trend alignment
        if trend_alignment:
            pattern_score += 25
        
        # Breakout yakınlığı
        if breakout_proximity >= 95:
            pattern_score += 30
        elif breakout_proximity >= 90:
            pattern_score += 20
        elif breakout_proximity >= 85:
            pattern_score += 10
        
        return {
            'volatility': recent_volatility,
            'trend_alignment': trend_alignment,
            'breakout_proximity': breakout_proximity,
            'pattern_score': pattern_score
        }
    
    def calculate_fresh_score(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Fresh aday skorunu hesapla"""
        historical = analysis['historical_ceilings']
        recent = analysis['recent_activity']
        technical = analysis['current_technical']
        pattern = analysis['pattern_score']
        
        # Temel kriterler kontrolü
        if historical['ceiling_count'] > self.fresh_criteria['max_historical_ceilings']:
            return {'total_score': 0, 'reason': 'Çok fazla geçmiş tavan'}
        
        if recent['strong_days'] < self.fresh_criteria['min_recent_activity']:
            return {'total_score': 0, 'reason': 'Yetersiz son dönem aktivite'}
        
        if technical['technical_score'] < self.fresh_criteria['min_current_signal']:
            return {'total_score': 0, 'reason': 'Zayıf teknik sinyaller'}
        
        # Skor hesaplama
        scores = {}
        
        # 1. Tarihsel uygunluk (30%) - Az tavan = yüksek puan
        ceiling_appropriateness = max(0, 100 - (historical['ceiling_count'] * 15))
        scores['historical'] = ceiling_appropriateness * 0.3
        
        # 2. Son dönem aktivite (25%)
        activity_score = min(100, recent['strong_days'] * 20 + recent['volume_spikes'] * 15)
        scores['activity'] = activity_score * 0.25
        
        # 3. Teknik güç (25%)
        scores['technical'] = technical['technical_score'] * 0.25
        
        # 4. Pattern uygunluğu (20%)
        scores['pattern'] = pattern['pattern_score'] * 0.2
        
        total_score = sum(scores.values())
        
        # Bonus puanlar
        bonus = 0
        bonus_reasons = []
        
        # Çok az geçmiş tavan
        if historical['ceiling_count'] <= 3:
            bonus += 10
            bonus_reasons.append("Az geçmiş tavan (fresh)")
        
        # Son dönemde güçlü hareket
        if recent['max_single_day'] >= 7:
            bonus += 5
            bonus_reasons.append(f"Son dönemde %{recent['max_single_day']:.1f} güçlü hareket")
        
        # Yüksek hacim aktivitesi
        if recent['volume_spikes'] >= 3:
            bonus += 5
            bonus_reasons.append("Yüksek hacim aktivitesi")
        
        # Güçlü teknik pozisyon
        if technical['technical_score'] >= 80:
            bonus += 10
            bonus_reasons.append("Çok güçlü teknik pozisyon")
        
        final_score = min(100, total_score + bonus)
        
        return {
            'total_score': final_score,
            'scores': scores,
            'bonus': bonus,
            'bonus_reasons': bonus_reasons,
            'ceiling_count': historical['ceiling_count'],
            'strong_days': recent['strong_days'],
            'technical_strength': technical['technical_score']
        }
    
    def find_fresh_candidates(self) -> List[Dict[str, Any]]:
        """Fresh tavan kralı adaylarını bul"""
        logger.info("Fresh tavan kralı adayları aranıyor...")
        
        # 90 günlük veri al
        all_data = self.data_fetcher.get_all_bist_data(period="90d")
        
        fresh_candidates = []
        
        for symbol_with_suffix, data in all_data.items():
            symbol = symbol_with_suffix.replace('.IS', '')
            
            # Bilinen hisseleri dışla
            if symbol in self.exclude_stocks:
                continue
            
            if data.empty or len(data) < 60:
                continue
            
            try:
                analysis = self.analyze_fresh_potential(symbol, data)
                
                if not analysis or not analysis.get('fresh_score'):
                    continue
                
                fresh_score = analysis['fresh_score']
                
                # Minimum 50 puan fresh score
                if fresh_score['total_score'] >= 50:
                    candidate = {
                        'symbol': symbol,
                        'fresh_score': fresh_score['total_score'],
                        'analysis': analysis
                    }
                    fresh_candidates.append(candidate)
                    
            except Exception as e:
                logger.debug(f"{symbol} fresh analiz hatası: {e}")
                continue
        
        # Fresh score'a göre sırala
        fresh_candidates.sort(key=lambda x: x['fresh_score'], reverse=True)
        
        logger.info(f"Toplam {len(fresh_candidates)} fresh aday bulundu")
        return fresh_candidates

def main():
    logging.basicConfig(level=logging.INFO)
    
    finder = FreshCeilingCandidateFinder()
    
    print("\n🌟 FRESH TAVAN KRALI ADAYI ARAYIŞI")
    print("=" * 80)
    print("Aranıyor: Henüz tavan kralı olmamış ama üst üste tavan yapma potansiyeli olan yeni adaylar")
    print("Dışlananlar: PINSU, IZINV, ISGSY, GRNYO, TRHOL (mevcut krallar)")
    print("            MRGYO, YESIL, MAKTK, PATEK, HUBVC (güçlü adaylar)")
    print("=" * 80)
    
    fresh_candidates = finder.find_fresh_candidates()
    
    if not fresh_candidates:
        print("❌ Fresh tavan kralı adayı bulunamadı!")
        return
    
    print(f"\n🎯 FRESH ADAYLAR BULUNDU: {len(fresh_candidates)} HİSSE")
    
    # En iyi 10 fresh adayı göster
    top_fresh = fresh_candidates[:10]
    
    for i, candidate in enumerate(top_fresh, 1):
        symbol = candidate['symbol']
        fresh_score = candidate['fresh_score']
        analysis = candidate['analysis']
        
        historical = analysis['historical_ceilings']
        recent = analysis['recent_activity']
        technical = analysis['current_technical']
        fresh_data = analysis['fresh_score']
        
        # Fresh level emoji
        if fresh_score >= 80:
            emoji = "🔥"
            level = "SÜPERFresh"
        elif fresh_score >= 70:
            emoji = "⚡"
            level = "ÇOK Fresh"
        elif fresh_score >= 60:
            emoji = "✨"
            level = "Fresh"
        else:
            emoji = "💡"
            level = "Umutlu"
        
        print(f"\n{emoji} {i}. {symbol} - {fresh_score:.1f} PUAN ({level})")
        print(f"   💰 Fiyat: {technical['current_price']:.2f} TL")
        
        # Fresh özellikler
        print(f"   🌟 Fresh Özellikler:")
        print(f"      • Geçmiş tavan: {historical['ceiling_count']} (Az = İyi)")
        print(f"      • Son 60 gün güçlü hareket: {recent['strong_days']} gün")
        print(f"      • En güçlü gün: %{recent['max_single_day']:.1f}")
        print(f"      • Hacim patlaması: {recent['volume_spikes']} kez")
        
        # Teknik durum
        print(f"   🔧 Teknik Durum:")
        print(f"      • RSI: {technical['RSI']:.1f}")
        print(f"      • Hacim: {technical['volume_ratio']:.1f}x")
        print(f"      • 10 gün momentum: %{technical['momentum_10d']:.1f}")
        print(f"      • BB pozisyon: %{technical['bb_position']:.1f}")
        print(f"      • Teknik güç: {technical['technical_score']}/100")
        
        # Skor detayları
        scores = fresh_data['scores']
        print(f"   📊 Skor Detayı:")
        print(f"      • Tarihsel uygunluk: {scores['historical']:.1f}")
        print(f"      • Aktivite: {scores['activity']:.1f}")
        print(f"      • Teknik: {scores['technical']:.1f}")
        print(f"      • Pattern: {scores['pattern']:.1f}")
        
        # Bonus puanlar
        if fresh_data['bonus'] > 0:
            print(f"   🎁 Bonus: +{fresh_data['bonus']:.1f} ({', '.join(fresh_data['bonus_reasons'])})")
    
    # Fresh kategoriler
    print(f"\n📊 FRESH KATEGORİLERİ:")
    super_fresh = len([c for c in fresh_candidates if c['fresh_score'] >= 80])
    very_fresh = len([c for c in fresh_candidates if 70 <= c['fresh_score'] < 80])
    fresh = len([c for c in fresh_candidates if 60 <= c['fresh_score'] < 70])
    hopeful = len([c for c in fresh_candidates if c['fresh_score'] < 60])
    
    print(f"   🔥 SÜPERFresh (80+): {super_fresh} hisse")
    print(f"   ⚡ ÇOK Fresh (70-79): {very_fresh} hisse")  
    print(f"   ✨ Fresh (60-69): {fresh} hisse")
    print(f"   💡 Umutlu (50-59): {hopeful} hisse")
    
    # En umut veren fresh adaylar
    if fresh_candidates:
        print(f"\n🌟 EN UMUT VEREN FRESH ADAYLAR:")
        for i, candidate in enumerate(fresh_candidates[:5], 1):
            symbol = candidate['symbol']
            score = candidate['fresh_score']
            ceiling_count = candidate['analysis']['fresh_score']['ceiling_count']
            strong_days = candidate['analysis']['fresh_score']['strong_days']
            
            print(f"   {i}. {symbol}: {score:.1f} puan")
            print(f"      → {ceiling_count} geçmiş tavan, {strong_days} güçlü gün")
    
    print(f"\n💡 ÖNERİ:")
    print(f"   🎯 Bu fresh adaylar henüz 'tavan kralı' değil ama potansiyel çok yüksek")
    print(f"   📈 Üst üste tavan yapma ihtimali olan yeni nesil adaylar")
    print(f"   🚀 Yakından takip edilmeli - gelecekteki krallar bunlardan çıkabilir!")

if __name__ == "__main__":
    main()