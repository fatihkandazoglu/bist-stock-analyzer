#!/usr/bin/env python3
"""
Haftalık Yatırım Stratejisi
Önümüzdeki hafta içi 5 gün boyunca yatırım yapılması gereken hisseleri belirler
"""

import pandas as pd
import numpy as np
import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta
from bist_data_fetcher import BISTDataFetcher

logger = logging.getLogger(__name__)

class WeeklyInvestmentStrategy:
    def __init__(self):
        """Haftalık yatırım stratejisi sistemi"""
        self.data_fetcher = BISTDataFetcher()
        
        # Bugünkü en güçlü sinyaller (100 puan alanlar)
        self.today_top_signals = {
            'KAPLM': 100.0, 'PENTA': 100.0, 'PCILT': 100.0, 
            'BARMA': 98.2, 'GRNYO': 97.1, 'FLAP': 95.5
        }
        
        # Gelecek hafta tahminleri (yüksek olasılık)
        self.next_week_predictions = {
            'PCILT': 83.5, 'KAPLM': 81.0, 'GRNYO': 80.2, 'PENTA': 75.8,
            'MRGYO': 65.2, 'MAKTK': 62.0, 'PATEK': 61.0
        }
        
        # Fresh adaylar (sürpriz potansiyeli)
        self.fresh_candidates = {
            'AKSA': 100.0, 'ADGYO': 100.0, 'KARSN': 100.0, 
            'GLYHO': 100.0, 'PENTA': 100.0
        }
        
        # Tavan kralları (devam eden güç)
        self.ceiling_kings = {
            'PINSU': 36.5, 'IZINV': 91.8, 'ISGSY': 60.0, 
            'GRNYO': 97.1, 'TRHOL': 75.9
        }
        
        # Güçlü adaylar (8+ tavan yapmış)
        self.strong_candidates_8ceiling = {
            'MRGYO': 88.0, 'YESIL': 86.9, 'MAKTK': 85.8
        }
        
        # Günlük yatırım kriterleri
        self.daily_criteria = {
            'pazartesi': {'risk_appetite': 'yüksek', 'focus': 'fresh_momentum'},
            'sali': {'risk_appetite': 'orta', 'focus': 'technical_signals'},
            'carsamba': {'risk_appetite': 'orta', 'focus': 'pattern_continuation'},
            'persembe': {'risk_appetite': 'yüksek', 'focus': 'ceiling_breakouts'},
            'cuma': {'risk_appetite': 'düşük', 'focus': 'profit_taking'}
        }
    
    def calculate_investment_score(self, symbol: str, day: str) -> Dict[str, Any]:
        """Günlük yatırım skorunu hesapla"""
        score = 0
        reasons = []
        category = ""
        
        # Temel skor hesaplama
        if symbol in self.today_top_signals:
            base_score = self.today_top_signals[symbol]
            score += base_score * 0.4  # %40 ağırlık
            reasons.append(f"Bugün {base_score:.1f} sinyal gücü")
            category = "Güncel Güçlü"
        
        if symbol in self.next_week_predictions:
            prediction_score = self.next_week_predictions[symbol]
            score += prediction_score * 0.3  # %30 ağırlık
            reasons.append(f"Gelecek hafta %{prediction_score:.1f} olasılık")
            if not category:
                category = "Gelecek Vadeden"
        
        if symbol in self.fresh_candidates:
            fresh_score = self.fresh_candidates[symbol]
            score += fresh_score * 0.2  # %20 ağırlık
            reasons.append(f"Fresh aday {fresh_score:.1f} puan")
            if not category:
                category = "Fresh Aday"
        
        if symbol in self.ceiling_kings:
            king_score = self.ceiling_kings[symbol]
            score += king_score * 0.15  # %15 ağırlık
            reasons.append(f"Tavan kralı {king_score:.1f} puan")
            if not category:
                category = "Tavan Kralı"
        
        if symbol in self.strong_candidates_8ceiling:
            candidate_score = self.strong_candidates_8ceiling[symbol]
            score += candidate_score * 0.25  # %25 ağırlık
            reasons.append(f"8+ tavan adayı {candidate_score:.1f} puan")
            if not category:
                category = "Güçlü Aday"
        
        # Günlük bonus hesaplama
        day_bonus = self.calculate_daily_bonus(symbol, day)
        score += day_bonus['bonus']
        if day_bonus['reasons']:
            reasons.extend(day_bonus['reasons'])
        
        return {
            'symbol': symbol,
            'daily_score': min(100, score),
            'category': category,
            'reasons': reasons,
            'day_bonus': day_bonus
        }
    
    def calculate_daily_bonus(self, symbol: str, day: str) -> Dict[str, Any]:
        """Günlük bonus puanları"""
        criteria = self.daily_criteria.get(day.lower(), {})
        bonus = 0
        reasons = []
        
        risk_appetite = criteria.get('risk_appetite', 'orta')
        focus = criteria.get('focus', 'technical_signals')
        
        # Risk iştahına göre bonus
        if risk_appetite == 'yüksek':
            if symbol in self.fresh_candidates or symbol in ['PENTA', 'AKSA']:
                bonus += 15
                reasons.append(f"{day.title()} fresh risk bonusu")
            if symbol in self.today_top_signals and self.today_top_signals[symbol] >= 95:
                bonus += 10
                reasons.append(f"{day.title()} güçlü sinyal bonusu")
        
        elif risk_appetite == 'orta':
            if symbol in self.next_week_predictions and self.next_week_predictions[symbol] >= 70:
                bonus += 12
                reasons.append(f"{day.title()} güvenli tahmin bonusu")
            if symbol in ['GRNYO', 'PCILT', 'KAPLM']:
                bonus += 8
                reasons.append(f"{day.title()} istikrarlı aday bonusu")
        
        elif risk_appetite == 'düşük':
            if symbol in self.ceiling_kings and self.ceiling_kings[symbol] >= 80:
                bonus += 10
                reasons.append(f"{day.title()} güvenli kral bonusu")
            if symbol in ['GRNYO', 'IZINV']:
                bonus += 8
                reasons.append(f"{day.title()} etabli kral bonusu")
        
        # Odak alanına göre bonus
        if focus == 'fresh_momentum' and symbol in self.fresh_candidates:
            bonus += 12
            reasons.append("Fresh momentum odağı")
        elif focus == 'technical_signals' and symbol in self.today_top_signals:
            bonus += 10
            reasons.append("Teknik sinyal odağı")
        elif focus == 'pattern_continuation' and symbol in self.next_week_predictions:
            bonus += 8
            reasons.append("Pattern devam odağı")
        elif focus == 'ceiling_breakouts' and symbol in self.strong_candidates_8ceiling:
            bonus += 15
            reasons.append("Tavan breakout odağı")
        elif focus == 'profit_taking' and symbol in self.ceiling_kings:
            bonus += 10
            reasons.append("Kar realization odağı")
        
        # Özel günlük bonuslar
        special_bonuses = self.get_special_daily_bonuses(symbol, day)
        bonus += special_bonuses['bonus']
        reasons.extend(special_bonuses['reasons'])
        
        return {
            'bonus': bonus,
            'reasons': reasons
        }
    
    def get_special_daily_bonuses(self, symbol: str, day: str) -> Dict[str, Any]:
        """Özel günlük bonuslar"""
        bonus = 0
        reasons = []
        
        # Pazartesi - Fresh start bonusu
        if day.lower() == 'pazartesi':
            if symbol in ['AKSA', 'GLYHO']:  # Virgin adaylar
                bonus += 10
                reasons.append("Pazartesi virgin aday bonusu")
            if symbol == 'PENTA':  # Çifte aday
                bonus += 8
                reasons.append("Pazartesi çifte aday bonusu")
        
        # Salı - Teknik güç bonusu
        elif day.lower() == 'sali':
            if symbol in ['PCILT', 'KAPLM']:  # Bugün 100 puan
                bonus += 12
                reasons.append("Salı teknik güç bonusu")
        
        # Çarşamba - Tavan pattern bonusu
        elif day.lower() == 'carsamba':
            if symbol in ['MRGYO', 'YESIL', 'MAKTK']:  # 8+ tavan
                bonus += 10
                reasons.append("Çarşamba tavan pattern bonusu")
        
        # Perşembe - Breakout bonusu
        elif day.lower() == 'persembe':
            if symbol in ['PCILT', 'KAPLM', 'GRNYO']:  # En yüksek tahminler
                bonus += 15
                reasons.append("Perşembe breakout bonusu")
        
        # Cuma - Güvenli kar bonusu
        elif day.lower() == 'cuma':
            if symbol in ['GRNYO', 'IZINV']:  # Etabli krallar
                bonus += 8
                reasons.append("Cuma güvenli kar bonusu")
        
        return {
            'bonus': bonus,
            'reasons': reasons
        }
    
    def generate_weekly_strategy(self) -> Dict[str, List[Dict[str, Any]]]:
        """5 günlük yatırım stratejisi oluştur"""
        logger.info("Haftalık yatırım stratejisi oluşturuluyor...")
        
        days = ['pazartesi', 'sali', 'carsamba', 'persembe', 'cuma']
        weekly_strategy = {}
        
        # Tüm hisse listesi
        all_symbols = set()
        all_symbols.update(self.today_top_signals.keys())
        all_symbols.update(self.next_week_predictions.keys())
        all_symbols.update(self.fresh_candidates.keys())
        all_symbols.update(self.ceiling_kings.keys())
        all_symbols.update(self.strong_candidates_8ceiling.keys())
        
        for day in days:
            day_recommendations = []
            
            for symbol in all_symbols:
                score_data = self.calculate_investment_score(symbol, day)
                
                # Minimum 40 puan gerekli
                if score_data['daily_score'] >= 40:
                    day_recommendations.append(score_data)
            
            # Günlük skora göre sırala
            day_recommendations.sort(key=lambda x: x['daily_score'], reverse=True)
            
            # En iyi 8 hisse al
            weekly_strategy[day] = day_recommendations[:8]
        
        return weekly_strategy

def main():
    logging.basicConfig(level=logging.INFO)
    
    strategy = WeeklyInvestmentStrategy()
    
    print("\n📅 HAFTALIK YATIRIM STRATEJİSİ")
    print("=" * 80)
    print("🎯 Önümüzdeki hafta içi 5 gün boyunca yatırım yapılması gerekenler")
    print("📊 Tüm analizler birleştirilerek günlük optimum portföy")
    print("=" * 80)
    
    weekly_plan = strategy.generate_weekly_strategy()
    
    days_tr = {
        'pazartesi': '📈 PAZARTESİ',
        'sali': '⚡ SALI', 
        'carsamba': '🎯 ÇARŞAMBA',
        'persembe': '🚀 PERŞEMBE',
        'cuma': '💰 CUMA'
    }
    
    day_descriptions = {
        'pazartesi': 'Fresh Start - Yeni fırsatlar, yüksek risk iştahı',
        'sali': 'Teknik Güç - Güçlü sinyaller, orta risk',
        'carsamba': 'Pattern Devam - Trend takibi, istikrarlı yatırım',
        'persembe': 'Breakout - Tavan kırma potansiyeli, yüksek risk',
        'cuma': 'Kar Alma - Güvenli pozisyonlar, düşük risk'
    }
    
    for day, recommendations in weekly_plan.items():
        print(f"\n{days_tr[day]} - {day_descriptions[day]}")
        print("=" * 50)
        
        if not recommendations:
            print("❌ Bu gün için uygun yatırım bulunamadı")
            continue
        
        print(f"🎯 Önerilen {len(recommendations)} hisse:")
        
        for i, rec in enumerate(recommendations, 1):
            symbol = rec['symbol']
            score = rec['daily_score']
            category = rec['category']
            reasons = rec['reasons']
            
            # Skor emoji
            if score >= 80:
                emoji = "🔥"
                level = "SÜPER"
            elif score >= 70:
                emoji = "⚡"
                level = "GÜÇLÜ"
            elif score >= 60:
                emoji = "✨"
                level = "İYİ"
            else:
                emoji = "📊"
                level = "NORMAL"
            
            print(f"\n{emoji} {i}. {symbol} - {score:.1f} PUAN ({level})")
            print(f"   📊 Kategori: {category}")
            print(f"   💡 Nedenler:")
            for reason in reasons[:3]:  # En önemli 3 neden
                print(f"      • {reason}")
    
    # Haftalık özet
    print(f"\n📊 HAFTALIK ÖZET:")
    print("=" * 50)
    
    # En çok önerilen hisseler
    all_recommendations = {}
    for day, recs in weekly_plan.items():
        for rec in recs:
            symbol = rec['symbol']
            score = rec['daily_score']
            all_recommendations[symbol] = all_recommendations.get(symbol, [])
            all_recommendations[symbol].append((day, score))
    
    # Haftalık sıklık
    weekly_frequency = {symbol: len(days) for symbol, days in all_recommendations.items()}
    top_weekly = sorted(weekly_frequency.items(), key=lambda x: x[1], reverse=True)[:5]
    
    print(f"🏆 EN ÇOK ÖNERİLEN HİSSELER:")
    for symbol, freq in top_weekly:
        print(f"   • {symbol}: {freq}/5 gün önerildi")
    
    # Günlük dağılım
    daily_counts = {day: len(recs) for day, recs in weekly_plan.items()}
    
    print(f"\n📈 GÜNLÜK DAĞILIM:")
    for day, count in daily_counts.items():
        day_name = days_tr[day].split(' ')[1]
        print(f"   • {day_name}: {count} hisse önerildi")
    
    # En yüksek skorlar
    all_scores = []
    for day, recs in weekly_plan.items():
        for rec in recs:
            all_scores.append((rec['symbol'], day, rec['daily_score']))
    
    top_scores = sorted(all_scores, key=lambda x: x[2], reverse=True)[:5]
    
    print(f"\n🎯 EN YÜKSEK SKORLAR:")
    for symbol, day, score in top_scores:
        day_name = days_tr[day].split(' ')[1]
        print(f"   • {symbol}: {score:.1f} puan ({day_name})")
    
    # Strateji önerileri
    print(f"\n💡 STRATEJİ ÖNERİLERİ:")
    print(f"   🎯 Her gün 2-3 hisse seçerek portföy oluştur")
    print(f"   💰 Günlük risk iştahına göre pozisyon büyüklüğü ayarla")
    print(f"   ⚡ En yüksek skorlu hisselere odaklan")
    print(f"   📊 Günlük piyasa koşullarını da değerlendir")
    
    print(f"\n⚠️ UYARI:")
    print(f"   • Bu strateji teknik analize dayalıdır")
    print(f"   • Piyasa haberleri ve dış faktörleri de değerlendir")
    print(f"   • Risk yönetimi kurallarını uygula")
    print(f"   • Stop-loss seviyelerini belirle")

if __name__ == "__main__":
    main()