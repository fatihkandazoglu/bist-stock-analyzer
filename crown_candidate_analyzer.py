#!/usr/bin/env python3
"""
Yeni Tavan Kralları Adayları Analizi
Hangi hisselerin gelecekte tavan kralı olma potansiyeli var?
"""

import pandas as pd
import numpy as np
import logging
from typing import List, Dict, Any
from bist_data_fetcher import BISTDataFetcher
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class CrownCandidateAnalyzer:
    def __init__(self):
        """Tavan kralı aday analiz sistemi"""
        self.data_fetcher = BISTDataFetcher()
        
        # Bilinen tavan kralları
        self.known_crown_stocks = ['PINSU', 'IZINV', 'ISGSY', 'GRNYO', 'TRHOL']
        
        # Tavan kralı olma kriterleri
        self.crown_criteria = {
            'consistency': 0.3,      # Tutarlılık ağırlığı
            'frequency': 0.2,        # Sıklık ağırlığı  
            'signal_strength': 0.25, # Sinyal gücü ağırlığı
            'momentum_power': 0.15,  # Momentum gücü ağırlığı
            'volume_pattern': 0.1    # Hacim pattern ağırlığı
        }
        
    def analyze_historical_ceiling_potential(self, symbol: str, data: pd.DataFrame, days_back: int = 90) -> Dict[str, Any]:
        """Geçmiş tavan potansiyelini analiz et"""
        if len(data) < 30:
            return {}
            
        try:
            ceiling_events = []
            strong_moves = []
            
            # Tavan ve güçlü hareketleri bul
            for i in range(20, len(data)):
                current_price = data['Close'].iloc[i]
                previous_price = data['Close'].iloc[i-1]
                
                if previous_price == 0:
                    continue
                    
                daily_change = ((current_price - previous_price) / previous_price) * 100
                
                # Tavan veya güçlü hareket
                if daily_change >= 9.0:
                    ceiling_events.append({
                        'date': data.index[i],
                        'change': daily_change,
                        'type': 'ceiling'
                    })
                elif daily_change >= 5.0:
                    strong_moves.append({
                        'date': data.index[i],
                        'change': daily_change,
                        'type': 'strong'
                    })
            
            # Tutarlılık analizi (son X günde kaç kez güçlü hareket)
            recent_days = 60
            if len(data) >= recent_days:
                recent_data = data.iloc[-recent_days:]
                recent_strong = 0
                
                for i in range(1, len(recent_data)):
                    prev_price = recent_data['Close'].iloc[i-1]
                    curr_price = recent_data['Close'].iloc[i]
                    if prev_price > 0:
                        change = ((curr_price - prev_price) / prev_price) * 100
                        if change >= 4.0:  # 4%+ güçlü hareket
                            recent_strong += 1
                            
                consistency_score = min(100, recent_strong * 10)  # Max 100 puan
            else:
                consistency_score = 0
            
            # Sıklık analizi
            total_events = len(ceiling_events) + len(strong_moves)
            frequency_score = min(100, total_events * 15)  # Her güçlü hareket 15 puan
            
            return {
                'ceiling_count': len(ceiling_events),
                'strong_move_count': len(strong_moves),
                'total_events': total_events,
                'consistency_score': consistency_score,
                'frequency_score': frequency_score,
                'recent_strong_moves': recent_strong,
                'ceiling_events': ceiling_events[-5:],  # Son 5 tavan
                'strong_moves': strong_moves[-10:]       # Son 10 güçlü hareket
            }
            
        except Exception as e:
            logger.debug(f"{symbol} geçmiş analiz hatası: {e}")
            return {}
    
    def calculate_current_technical_strength(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Güncel teknik güç analizi"""
        if len(data) < 25:
            return {}
            
        try:
            close = data['Close']
            high = data['High']
            low = data['Low']
            volume = data['Volume']
            
            # Son değerler
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
            volume_sma_20 = volume.rolling(20).mean().iloc[-1] if len(volume) >= 20 else current_volume
            volume_ratio = current_volume / volume_sma_20 if volume_sma_20 > 0 else 1
            
            # Bollinger Band pozisyonu
            sma_20 = close.rolling(20).mean().iloc[-1] if len(close) >= 20 else current_close
            if len(close) >= 20:
                bb_std = close.rolling(20).std().iloc[-1]
                bb_upper = sma_20 + (bb_std * 2)
                bb_lower = sma_20 - (bb_std * 2)
                bb_position = (current_close - bb_lower) / (bb_upper - bb_lower) * 100 if bb_upper != bb_lower else 50
            else:
                bb_position = 50
                
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
            
            # Momentum hesapla
            if len(close) >= 6:
                momentum_5d = ((current_close - close.iloc[-6]) / close.iloc[-6]) * 100
            else:
                momentum_5d = 0
                
            # Günlük değişim
            if len(close) >= 2:
                daily_change = ((current_close - close.iloc[-2]) / close.iloc[-2]) * 100
            else:
                daily_change = 0
            
            # Teknik güç puanı hesapla
            signal_strength = 0
            
            # RSI puanı (60-75 arası ideal)
            if 60 <= rsi <= 75:
                signal_strength += 25
            elif 50 <= rsi < 60 or 75 < rsi <= 85:
                signal_strength += 15
            elif rsi > 85:
                signal_strength += 20  # Tavan yakını
            
            # Volume puanı
            if volume_ratio >= 2.0:
                signal_strength += 25
            elif volume_ratio >= 1.5:
                signal_strength += 15
            elif volume_ratio >= 1.0:
                signal_strength += 10
                
            # BB pozisyon puanı
            if bb_position >= 80:
                signal_strength += 25
            elif bb_position >= 60:
                signal_strength += 15
            elif bb_position >= 40:
                signal_strength += 10
                
            # Momentum puanı
            if momentum_5d >= 10:
                signal_strength += 15
            elif momentum_5d >= 5:
                signal_strength += 10
            elif momentum_5d >= 0:
                signal_strength += 5
                
            # Stochastic puanı
            if stoch_k >= 70:
                signal_strength += 10
            elif stoch_k >= 50:
                signal_strength += 5
            
            return {
                'RSI': rsi,
                'Volume_Ratio': volume_ratio,
                'BB_Position': bb_position,
                'Stochastic_K': stoch_k,
                'Momentum_5D': momentum_5d,
                'Daily_Change': daily_change,
                'Signal_Strength': signal_strength,
                'Current_Price': current_close
            }
            
        except Exception as e:
            logger.debug(f"Teknik güç analiz hatası: {e}")
            return {}
    
    def analyze_volume_pattern(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Hacim pattern analizi"""
        if len(data) < 30:
            return {}
            
        try:
            volume = data['Volume']
            close = data['Close']
            
            # Son 30 gün hacim analizi
            recent_volume = volume.iloc[-30:]
            avg_volume = recent_volume.mean()
            
            # Hacim artış günleri
            volume_spike_days = 0
            big_volume_days = 0
            
            for i in range(len(recent_volume)-1, max(len(recent_volume)-15, 0), -1):
                vol_ratio = recent_volume.iloc[i] / avg_volume if avg_volume > 0 else 1
                
                if vol_ratio >= 2.0:
                    volume_spike_days += 1
                if vol_ratio >= 1.5:
                    big_volume_days += 1
            
            # Hacim-fiyat korelasyonu
            price_changes = close.pct_change().iloc[-30:]
            volume_changes = recent_volume.pct_change()
            
            # Pozitif günlerde hacim artışı
            positive_days = price_changes > 0.02  # %2+ artış günleri
            volume_on_positive = volume_changes[positive_days].mean() if len(volume_changes[positive_days]) > 0 else 0
            
            volume_pattern_score = 0
            
            # Spike günleri puanı
            volume_pattern_score += min(50, volume_spike_days * 10)
            
            # Büyük hacim günleri puanı
            volume_pattern_score += min(30, big_volume_days * 3)
            
            # Pozitif korelasyon puanı
            if volume_on_positive > 0.1:  # %10+ hacim artışı pozitif günlerde
                volume_pattern_score += 20
            
            return {
                'volume_spike_days': volume_spike_days,
                'big_volume_days': big_volume_days,
                'volume_on_positive': volume_on_positive,
                'volume_pattern_score': volume_pattern_score,
                'avg_volume': avg_volume
            }
            
        except Exception as e:
            logger.debug(f"Hacim pattern analiz hatası: {e}")
            return {}
    
    def calculate_crown_potential_score(self, symbol: str, all_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Tavan kralı potansiyel puanını hesapla"""
        if not all_analysis:
            return {'total_score': 0, 'breakdown': {}}
            
        scores = {}
        weights = self.crown_criteria
        
        # 1. Tutarlılık puanı
        historical = all_analysis.get('historical', {})
        consistency = historical.get('consistency_score', 0)
        scores['consistency'] = consistency * weights['consistency']
        
        # 2. Sıklık puanı
        frequency = historical.get('frequency_score', 0)
        scores['frequency'] = frequency * weights['frequency']
        
        # 3. Sinyal gücü puanı
        technical = all_analysis.get('technical', {})
        signal_strength = technical.get('Signal_Strength', 0)
        scores['signal_strength'] = signal_strength * weights['signal_strength']
        
        # 4. Momentum gücü puanı
        momentum_5d = technical.get('Momentum_5D', 0)
        momentum_power = min(100, abs(momentum_5d) * 5)  # Her %1 momentum = 5 puan
        scores['momentum_power'] = momentum_power * weights['momentum_power']
        
        # 5. Hacim pattern puanı
        volume_pattern = all_analysis.get('volume_pattern', {})
        volume_score = volume_pattern.get('volume_pattern_score', 0)
        scores['volume_pattern'] = volume_score * weights['volume_pattern']
        
        # Toplam puan
        total_score = sum(scores.values())
        
        # Bonus puanlar
        bonus = 0
        bonus_reasons = []
        
        # Son zamanlarda çok aktif
        if historical.get('recent_strong_moves', 0) >= 3:
            bonus += 5
            bonus_reasons.append("Son 60 günde 3+ güçlü hareket")
            
        # Teknik göstergeler çok güçlü
        if signal_strength >= 80:
            bonus += 10
            bonus_reasons.append("Çok güçlü teknik sinyaller")
            
        # Hacim patlamaları var
        if volume_pattern.get('volume_spike_days', 0) >= 3:
            bonus += 5
            bonus_reasons.append("Son dönemde 3+ hacim patlaması")
        
        # RSI ideal seviyede
        rsi = technical.get('RSI', 50)
        if 60 <= rsi <= 70:
            bonus += 5
            bonus_reasons.append("İdeal RSI seviyesi")
        
        final_score = min(100, total_score + bonus)
        
        return {
            'total_score': final_score,
            'breakdown': scores,
            'bonus': bonus,
            'bonus_reasons': bonus_reasons,
            'category': self.get_potential_category(final_score),
            'ceiling_count': historical.get('ceiling_count', 0),
            'strong_moves': historical.get('strong_move_count', 0),
            'current_signal': signal_strength
        }
    
    def get_potential_category(self, score: float) -> str:
        """Potansiyel kategorisini belirle"""
        if score >= 80:
            return "SÜPER ADAY"
        elif score >= 70:
            return "GÜÇLÜ ADAY"
        elif score >= 60:
            return "UMUT VADEDİYOR"
        elif score >= 50:
            return "TAKİP EDİLMELİ"
        else:
            return "ZAYIF POTANSIYEL"
    
    def analyze_crown_candidates(self, candidate_stocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Tavan kralı adaylarını analiz et"""
        logger.info("Tavan kralı adayları analiz ediliyor...")
        
        # 90 günlük veri al (daha uzun geçmiş için)
        all_data = self.data_fetcher.get_all_bist_data(period="90d")
        
        crown_candidates = []
        
        for stock in candidate_stocks:
            symbol = stock['symbol']
            
            # Zaten bilinen tavan kralı mı?
            if symbol in self.known_crown_stocks:
                continue
                
            stock_symbol_with_suffix = symbol + '.IS'
            if stock_symbol_with_suffix not in all_data:
                continue
                
            data = all_data[stock_symbol_with_suffix]
            if data.empty or len(data) < 60:
                continue
                
            try:
                # Kapsamlı analiz yap
                historical_analysis = self.analyze_historical_ceiling_potential(symbol, data, 90)
                technical_analysis = self.calculate_current_technical_strength(data)
                volume_analysis = self.analyze_volume_pattern(data)
                
                all_analysis = {
                    'historical': historical_analysis,
                    'technical': technical_analysis,
                    'volume_pattern': volume_analysis
                }
                
                # Potansiyel puanını hesapla
                potential_score = self.calculate_crown_potential_score(symbol, all_analysis)
                
                # Sadece potansiyeli yüksek olanları al
                if potential_score['total_score'] >= 45:  # Minimum 45 puan
                    candidate = {
                        'symbol': symbol,
                        'current_price': technical_analysis.get('Current_Price', 0),
                        'current_signal_score': stock['signal_score'],
                        'crown_potential': potential_score,
                        'analysis': all_analysis
                    }
                    crown_candidates.append(candidate)
                    
            except Exception as e:
                logger.debug(f"{symbol} aday analiz hatası: {e}")
                continue
        
        # Potansiyel puanına göre sırala
        crown_candidates.sort(key=lambda x: x['crown_potential']['total_score'], reverse=True)
        
        logger.info(f"Toplam {len(crown_candidates)} tavan kralı adayı bulundu")
        return crown_candidates

def main():
    logging.basicConfig(level=logging.INFO)
    
    # Önce güncel sinyal veren hisseleri al (önceki taramadan)
    from live_signal_scanner import LiveSignalScanner
    
    scanner = LiveSignalScanner()
    signal_stocks = scanner.scan_all_stocks()
    
    # Yeni tavan kralı adaylarını analiz et
    analyzer = CrownCandidateAnalyzer()
    crown_candidates = analyzer.analyze_crown_candidates(signal_stocks)
    
    print("\n👑 YENİ TAVAN KRALLARI ADAYLARI ANALİZİ")
    print("=" * 80)
    print("Mevcut tavan kralları: PINSU, IZINV, ISGSY, GRNYO, TRHOL")
    print("=" * 80)
    
    if not crown_candidates:
        print("❌ Yeni tavan kralı adayı bulunamadı!")
        return
    
    print(f"\n🔍 ADAY ANALİZİ: {len(crown_candidates)} HİSSE DEĞERLENDİRİLDİ")
    
    # En iyi 15 adayı göster
    top_candidates = crown_candidates[:15]
    
    for i, candidate in enumerate(top_candidates, 1):
        symbol = candidate['symbol']
        potential = candidate['crown_potential']
        analysis = candidate['analysis']
        current_price = candidate['current_price']
        current_signal = candidate['current_signal_score']
        
        # Kategori emoji
        category_emojis = {
            "SÜPER ADAY": "🔥",
            "GÜÇLÜ ADAY": "⚡",
            "UMUT VADEDİYOR": "✨",
            "TAKİP EDİLMELİ": "📊",
            "ZAYIF POTANSIYEL": "💡"
        }
        
        emoji = category_emojis.get(potential['category'], "📊")
        
        print(f"\n{emoji} {i}. {symbol} - {potential['total_score']:.1f} PUAN")
        print(f"   📊 Kategori: {potential['category']}")
        print(f"   💰 Fiyat: {current_price:.2f} TL")
        print(f"   🎯 Güncel sinyal: {current_signal:.1f} puan")
        
        # Geçmiş performans
        historical = analysis['historical']
        print(f"   📈 Geçmiş: {potential['ceiling_count']} tavan, {potential['strong_moves']} güçlü hareket")
        
        # Teknik durum
        technical = analysis['technical']
        print(f"   🔧 Teknik: RSI {technical.get('RSI', 0):.1f}, Hacim {technical.get('Volume_Ratio', 0):.1f}x, BB %{technical.get('BB_Position', 0):.1f}")
        
        # Puan detayları
        breakdown = potential['breakdown']
        print(f"   📊 Puan detayı:")
        print(f"      • Tutarlılık: {breakdown.get('consistency', 0):.1f}")
        print(f"      • Sıklık: {breakdown.get('frequency', 0):.1f}")
        print(f"      • Sinyal gücü: {breakdown.get('signal_strength', 0):.1f}")
        print(f"      • Momentum: {breakdown.get('momentum_power', 0):.1f}")
        print(f"      • Hacim pattern: {breakdown.get('volume_pattern', 0):.1f}")
        
        # Bonus puanlar
        if potential['bonus'] > 0:
            print(f"   🎁 Bonus: +{potential['bonus']:.1f} ({', '.join(potential['bonus_reasons'])})")
    
    # Kategoriye göre özet
    print(f"\n📊 KATEGORİ ÖZETİ:")
    category_counts = {}
    for candidate in crown_candidates:
        category = candidate['crown_potential']['category']
        category_counts[category] = category_counts.get(category, 0) + 1
    
    for category, count in category_counts.items():
        emoji = category_emojis.get(category, "📊")
        print(f"   {emoji} {category}: {count} hisse")
    
    # En umut vadeden 5 hisse
    print(f"\n🌟 EN UMUT VADEDENLER (İlk 5):")
    for i, candidate in enumerate(top_candidates[:5], 1):
        symbol = candidate['symbol']
        score = candidate['crown_potential']['total_score']
        category = candidate['crown_potential']['category']
        ceiling_count = candidate['crown_potential']['ceiling_count']
        
        print(f"   {i}. {symbol}: {score:.1f} puan - {category}")
        print(f"      → Geçmişte {ceiling_count} tavan yapmış")
    
    print(f"\n💡 DEĞERLENDİRME:")
    print(f"   🎯 Analiz {len(signal_stocks)} sinyal veren hisseden {len(crown_candidates)} aday buldu")
    print(f"   👑 Tavan kralı olmak için: tutarlılık + sıklık + güçlü sinyaller gerekli")
    print(f"   📈 Bu adaylar yakından takip edilmeli - gelecekteki tavan potansiyeli yüksek")

if __name__ == "__main__":
    main()