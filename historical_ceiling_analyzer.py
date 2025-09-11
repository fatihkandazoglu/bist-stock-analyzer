#!/usr/bin/env python3
"""
Geçmiş Tavan Analizi Modülü
Son 1 aydaki tavan yapan hisseleri analiz eder ve ortak paternleri bulur.
"""

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import logging
from typing import List, Dict, Any
from bist_data_fetcher import BISTDataFetcher
from technical_analyzer import TechnicalAnalyzer
from prediction_model import StockPredictionModel

logger = logging.getLogger(__name__)

class HistoricalCeilingAnalyzer:
    def __init__(self):
        """Geçmiş tavan analiz sistemi"""
        self.data_fetcher = BISTDataFetcher()
        self.technical_analyzer = TechnicalAnalyzer()
        self.prediction_model = StockPredictionModel()
        self.ceiling_threshold = 9.0  # %9+ artış = tavan kabul edelim
        
    def find_ceiling_days_in_period(self, days_back: int = 30) -> List[Dict[str, Any]]:
        """Son X gündeki tüm tavan yapan günleri bul"""
        logger.info(f"Son {days_back} gündeki tavan günleri aranıyor...")
        
        # Tüm BİST hisselerinin verilerini çek
        all_data = self.data_fetcher.get_all_bist_data(period=f"{days_back + 5}d")
        
        ceiling_events = []
        
        for symbol, data in all_data.items():
            if data.empty or len(data) < 5:
                continue
                
            try:
                # Her günü kontrol et
                for i in range(1, len(data)):
                    current_price = data['Close'].iloc[i]
                    previous_price = data['Close'].iloc[i-1]
                    
                    if previous_price == 0:
                        continue
                        
                    daily_change = ((current_price - previous_price) / previous_price) * 100
                    
                    # Tavan kontrolü (9%+ artış)
                    if daily_change >= self.ceiling_threshold:
                        ceiling_date = data.index[i]
                        
                        # O günkü hacim ve teknik veriler
                        volume = data['Volume'].iloc[i]
                        high = data['High'].iloc[i]
                        low = data['Low'].iloc[i]
                        open_price = data['Open'].iloc[i]
                        
                        # Önceki günün verileri
                        prev_volume = data['Volume'].iloc[i-1]
                        prev_close = data['Close'].iloc[i-1]
                        
                        # Volume ratio
                        if i >= 20:  # 20 gün ortalama için
                            avg_volume_20 = data['Volume'].iloc[i-20:i].mean()
                            volume_ratio = volume / avg_volume_20 if avg_volume_20 > 0 else 1
                        else:
                            volume_ratio = 1
                            
                        # Momentum kontrolü (önceki günler)
                        momentum_days = []
                        for j in range(max(0, i-5), i):
                            if j > 0:
                                prev_change = ((data['Close'].iloc[j] - data['Close'].iloc[j-1]) / data['Close'].iloc[j-1]) * 100
                                momentum_days.append(prev_change)
                        
                        ceiling_events.append({
                            'symbol': symbol.replace('.IS', ''),
                            'date': ceiling_date,
                            'daily_change': daily_change,
                            'price': current_price,
                            'volume': volume,
                            'prev_volume': prev_volume,
                            'volume_ratio': volume_ratio,
                            'high': high,
                            'low': low,
                            'open': open_price,
                            'prev_close': prev_close,
                            'momentum_5d': momentum_days,
                            'avg_momentum_5d': np.mean(momentum_days) if momentum_days else 0
                        })
                        
            except Exception as e:
                logger.debug(f"{symbol} tavan analiz hatası: {e}")
                continue
                
        logger.info(f"Toplam {len(ceiling_events)} tavan olayı bulundu")
        return ceiling_events
    
    def analyze_ceiling_patterns(self, ceiling_events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Tavan olaylarının ortak paternlerini analiz et"""
        if not ceiling_events:
            return {}
            
        logger.info(f"{len(ceiling_events)} tavan olayı analiz ediliyor...")
        
        # İstatistikler
        daily_changes = [event['daily_change'] for event in ceiling_events]
        volume_ratios = [event['volume_ratio'] for event in ceiling_events if event['volume_ratio'] > 0]
        momentum_5d = [event['avg_momentum_5d'] for event in ceiling_events]
        
        # Volume kategorileri
        explosive_volume = len([v for v in volume_ratios if v > 3.0])
        high_volume = len([v for v in volume_ratios if 2.0 <= v <= 3.0])
        medium_volume = len([v for v in volume_ratios if 1.5 <= v < 2.0])
        normal_volume = len([v for v in volume_ratios if v < 1.5])
        
        # Momentum kategorileri
        positive_momentum = len([m for m in momentum_5d if m > 2.0])
        neutral_momentum = len([m for m in momentum_5d if -1.0 <= m <= 2.0])
        negative_momentum = len([m for m in momentum_5d if m < -1.0])
        
        # En çok tavan yapan hisseler
        symbol_counts = {}
        for event in ceiling_events:
            symbol = event['symbol']
            symbol_counts[symbol] = symbol_counts.get(symbol, 0) + 1
            
        top_ceiling_stocks = sorted(symbol_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Son hafta oranı
        one_week_ago = datetime.now() - timedelta(days=7)
        recent_ceilings = [e for e in ceiling_events if pd.to_datetime(e['date']).tz_localize(None) > one_week_ago]
        
        analysis = {
            'total_ceiling_events': len(ceiling_events),
            'recent_week_events': len(recent_ceilings),
            'average_daily_change': np.mean(daily_changes),
            'median_daily_change': np.median(daily_changes),
            'max_daily_change': np.max(daily_changes),
            'average_volume_ratio': np.mean(volume_ratios) if volume_ratios else 0,
            'median_volume_ratio': np.median(volume_ratios) if volume_ratios else 0,
            'average_momentum_5d': np.mean(momentum_5d) if momentum_5d else 0,
            'volume_distribution': {
                'explosive_volume_3x+': explosive_volume,
                'high_volume_2-3x': high_volume,
                'medium_volume_1.5-2x': medium_volume,
                'normal_volume_<1.5x': normal_volume
            },
            'momentum_distribution': {
                'positive_momentum_>2%': positive_momentum,
                'neutral_momentum': neutral_momentum,
                'negative_momentum': negative_momentum
            },
            'top_ceiling_stocks': top_ceiling_stocks,
            'volume_success_rate': {
                'explosive_volume_rate': explosive_volume / len(volume_ratios) * 100 if volume_ratios else 0,
                'high_volume_rate': high_volume / len(volume_ratios) * 100 if volume_ratios else 0,
                'medium_volume_rate': medium_volume / len(volume_ratios) * 100 if volume_ratios else 0
            }
        }
        
        return analysis
    
    def test_our_algorithm_performance(self, ceiling_events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Mevcut algoritmamızın bu geçmiş olayları yakalayabilirlik oranını test et"""
        logger.info("Algoritmamızın geçmiş performansı test ediliyor...")
        
        if not ceiling_events:
            return {}
            
        caught_events = 0
        total_events = len(ceiling_events)
        high_confidence_catches = 0
        
        for event in ceiling_events:
            try:
                symbol = event['symbol']
                
                # Bu event için mock analiz verisi oluştur
                mock_analysis = {
                    'symbol': symbol,
                    'price_change_1d': 2.0,  # Önceki günün değişimi (tavan günü değil)
                    'price_change_5d': event['avg_momentum_5d'],
                    'rsi': 65.0,  # Orta değer
                    'macd': 0.5,
                    'macd_signal': 0.3,
                    'technical_score': 70.0,
                    'volume_analysis': {
                        'volume_ratio_20': event['volume_ratio'],
                        'volume_ratio_5': event['volume_ratio'] * 0.9,
                        'recent_volume_momentum': min(2.0, event['volume_ratio'] * 0.8),
                        'volume_alerts': ['VOLUME_SPIKE'] if event['volume_ratio'] > 2.0 else []
                    },
                    'momentum_signals': {
                        'momentum_continuation': event['avg_momentum_5d'] > 1.0,
                        'momentum_5d': event['avg_momentum_5d'],
                        'momentum_score': min(50, event['avg_momentum_5d'] * 5)
                    },
                    'pattern_signals': {
                        'breakout': 'upward' if event['volume_ratio'] > 1.8 else 'none',
                        'gap': 'none',
                        'support_resistance': 'neutral'
                    },
                    'market_characteristics': {
                        'volatility': 6.0,
                        'size_category': 'small_cap' if event['price'] < 20 else 'mid_cap'
                    },
                    'ceiling_potential': {
                        'ceiling_score': min(100, event['volume_ratio'] * 30 + (event['avg_momentum_5d'] * 10))
                    }
                }
                
                # Tahmin skoru hesapla
                prediction_score = self.prediction_model.predict_ceiling_probability(
                    mock_analysis, {'xu100_change': 0.0}, 0.5
                )
                
                # %50+ tahmin = yakaladı kabul et
                if prediction_score >= 0.5:
                    caught_events += 1
                    if prediction_score >= 0.7:  # %70+ = yüksek güven
                        high_confidence_catches += 1
                        
            except Exception as e:
                logger.debug(f"Test hatası {event['symbol']}: {e}")
                continue
        
        success_rate = (caught_events / total_events * 100) if total_events > 0 else 0
        high_confidence_rate = (high_confidence_catches / total_events * 100) if total_events > 0 else 0
        
        return {
            'total_events_tested': total_events,
            'caught_events': caught_events,
            'high_confidence_catches': high_confidence_catches,
            'success_rate': success_rate,
            'high_confidence_rate': high_confidence_rate,
            'missed_events': total_events - caught_events
        }
    
    def generate_insights(self, pattern_analysis: Dict, performance_test: Dict) -> List[str]:
        """Analizlerden çıkarımlar oluştur"""
        insights = []
        
        if pattern_analysis:
            # Volume insights
            vol_dist = pattern_analysis.get('volume_distribution', {})
            explosive_rate = pattern_analysis.get('volume_success_rate', {}).get('explosive_volume_rate', 0)
            
            if explosive_rate > 40:
                insights.append(f"🔥 %{explosive_rate:.1f} tavan olayında 3x+ hacim patlaması var - Volume çok kritik!")
            
            avg_volume = pattern_analysis.get('average_volume_ratio', 0)
            if avg_volume > 2.0:
                insights.append(f"📊 Ortalama hacim oranı {avg_volume:.1f}x - 2x+ hacim şart görünüyor")
            
            # Momentum insights  
            momentum_dist = pattern_analysis.get('momentum_distribution', {})
            positive_momentum_count = momentum_dist.get('positive_momentum_>2%', 0)
            total_events = pattern_analysis.get('total_ceiling_events', 1)
            
            if positive_momentum_count / total_events > 0.6:
                insights.append(f"⚡ %{positive_momentum_count/total_events*100:.1f} tavan olayında önceki momentum pozitif")
            
            # Top stocks
            top_stocks = pattern_analysis.get('top_ceiling_stocks', [])[:3]
            if top_stocks:
                top_names = [stock[0] for stock in top_stocks]
                insights.append(f"🏆 En çok tavan yapanlar: {', '.join(top_names)}")
        
        if performance_test:
            success_rate = performance_test.get('success_rate', 0)
            if success_rate >= 60:
                insights.append(f"✅ Algoritmamız %{success_rate:.1f} yakalama oranına sahip - Güçlü!")
            elif success_rate >= 40:
                insights.append(f"⚠️ Algoritmamız %{success_rate:.1f} yakalama oranında - İyileştirilebilir")
            else:
                insights.append(f"❌ Algoritmamız sadece %{success_rate:.1f} yakalıyor - Revizyon gerekli!")
        
        return insights

def main():
    logging.basicConfig(level=logging.INFO)
    analyzer = HistoricalCeilingAnalyzer()
    
    print("\n🔍 SON 30 GÜN TAVAN ANALİZİ BAŞLIYOR...")
    print("=" * 50)
    
    # Son 30 gündeki tavan olaylarını bul
    ceiling_events = analyzer.find_ceiling_days_in_period(days_back=30)
    
    if not ceiling_events:
        print("❌ Tavan olayı bulunamadı!")
        return
    
    # Pattern analizi
    patterns = analyzer.analyze_ceiling_patterns(ceiling_events)
    
    # Algoritma performans testi  
    performance = analyzer.test_our_algorithm_performance(ceiling_events)
    
    # Sonuçları yazdır
    print(f"\n📊 TAVAN OLAYLARI ANALİZİ:")
    print(f"   • Toplam tavan olayı: {patterns.get('total_ceiling_events', 0)}")
    print(f"   • Son hafta: {patterns.get('recent_week_events', 0)}")
    print(f"   • Ortalama artış: %{patterns.get('average_daily_change', 0):.2f}")
    print(f"   • Maksimum artış: %{patterns.get('max_daily_change', 0):.2f}")
    
    print(f"\n📈 HACİM ANALİZİ:")
    print(f"   • Ortalama hacim oranı: {patterns.get('average_volume_ratio', 0):.1f}x")
    vol_dist = patterns.get('volume_distribution', {})
    print(f"   • 3x+ hacim: {vol_dist.get('explosive_volume_3x+', 0)} olay")
    print(f"   • 2-3x hacim: {vol_dist.get('high_volume_2-3x', 0)} olay")
    print(f"   • 1.5-2x hacim: {vol_dist.get('medium_volume_1.5-2x', 0)} olay")
    
    print(f"\n⚡ MOMENTUM ANALİZİ:")
    print(f"   • Ortalama 5 gün momentum: %{patterns.get('average_momentum_5d', 0):.2f}")
    mom_dist = patterns.get('momentum_distribution', {})
    print(f"   • Pozitif momentum: {mom_dist.get('positive_momentum_>2%', 0)} olay")
    print(f"   • Nötr momentum: {mom_dist.get('neutral_momentum', 0)} olay")
    
    print(f"\n🎯 ALGORİTMA PERFORMANSI:")
    print(f"   • Yakalanan olaylar: {performance.get('caught_events', 0)}/{performance.get('total_events_tested', 0)}")
    print(f"   • Başarı oranı: %{performance.get('success_rate', 0):.1f}")
    print(f"   • Yüksek güven: %{performance.get('high_confidence_rate', 0):.1f}")
    
    print(f"\n🏆 EN ÇOK TAVAN YAPAN HİSSELER:")
    top_stocks = patterns.get('top_ceiling_stocks', [])[:5]
    for i, (stock, count) in enumerate(top_stocks, 1):
        print(f"   {i}. {stock}: {count} kez")
    
    # Insights
    insights = analyzer.generate_insights(patterns, performance)
    if insights:
        print(f"\n💡 ÖNEMLİ ÇIKARILAR:")
        for insight in insights:
            print(f"   {insight}")

if __name__ == "__main__":
    main()