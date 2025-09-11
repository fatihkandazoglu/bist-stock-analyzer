#!/usr/bin/env python3
"""
Tavan Kralı Tahmin Analizi
Sürekli tavan yapan hisselerin önceki sinyallerini analiz eder.
"""

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import logging
from typing import List, Dict, Any
from bist_data_fetcher import BISTDataFetcher
from technical_analyzer import TechnicalAnalyzer

logger = logging.getLogger(__name__)

class CrownStockPredictor:
    def __init__(self):
        """Tavan kralı tahmin sistemi"""
        self.data_fetcher = BISTDataFetcher()
        self.technical_analyzer = TechnicalAnalyzer()
        
        # En çok tavan yapan hisseler (analiz sonucundan)
        self.crown_stocks = ['PINSU', 'IZINV', 'ISGSY', 'GRNYO', 'YYAPI']
        
    def analyze_crown_stock_patterns(self, symbol: str, days_back: int = 60) -> Dict[str, Any]:
        """Bir tavan kralının geçmiş pattern'lerini analiz et"""
        logger.info(f"{symbol} tavan pattern'leri analiz ediliyor...")
        
        # 60 günlük veri çek
        symbol_with_suffix = f"{symbol}.IS"
        data = self.data_fetcher.get_stock_data(symbol_with_suffix, period=f"{days_back}d")
        
        if data.empty or len(data) < 10:
            return {'error': 'Yetersiz veri'}
            
        # Tavan günlerini bul
        ceiling_days = []
        for i in range(1, len(data)):
            current_price = data['Close'].iloc[i]
            previous_price = data['Close'].iloc[i-1]
            
            if previous_price == 0:
                continue
                
            daily_change = ((current_price - previous_price) / previous_price) * 100
            
            if daily_change >= 9.0:  # Tavan günü
                ceiling_days.append({
                    'date': data.index[i],
                    'change': daily_change,
                    'price': current_price,
                    'volume': data['Volume'].iloc[i],
                    'index': i
                })
        
        if not ceiling_days:
            return {'error': 'Tavan günü bulunamadı'}
            
        # Her tavan öncesi sinyalleri analiz et
        pre_ceiling_signals = []
        
        for ceiling in ceiling_days:
            ceiling_index = ceiling['index']
            
            # Tavan öncesi 1-5 gün arası sinyalleri bul
            for days_before in range(1, 6):  # 1-5 gün öncesi
                signal_index = ceiling_index - days_before
                
                if signal_index < 20:  # Yeterli veri yoksa geç
                    continue
                    
                # O günün analizi
                signal_data = data.iloc[max(0, signal_index-19):signal_index+1]  # 20 günlük window
                
                if len(signal_data) < 20:
                    continue
                    
                try:
                    # Teknik analiz yap
                    analysis = self.technical_analyzer.analyze_stock(symbol, signal_data)
                    
                    if analysis:
                        # Sinyal gününden tavan gününe kadar geçen gün sayısı
                        signal_strength = self.calculate_signal_strength(analysis)
                        
                        pre_ceiling_signals.append({
                            'ceiling_date': ceiling['date'],
                            'ceiling_change': ceiling['change'],
                            'signal_date': signal_data.index[-1],
                            'days_before_ceiling': days_before,
                            'signal_strength': signal_strength,
                            'analysis': analysis
                        })
                        
                except Exception as e:
                    logger.debug(f"{symbol} sinyal analiz hatası: {e}")
                    continue
        
        return {
            'symbol': symbol,
            'total_ceilings': len(ceiling_days),
            'pre_signals': pre_ceiling_signals,
            'ceiling_days': ceiling_days
        }
    
    def calculate_signal_strength(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Sinyal gücünü hesapla"""
        strength = {
            'total_score': 0,
            'volume_strength': 0,
            'momentum_strength': 0,
            'technical_strength': 0,
            'pattern_strength': 0
        }
        
        # Volume analizi
        volume_analysis = analysis.get('volume_analysis', {})
        volume_ratio = volume_analysis.get('volume_ratio_20', 1.0)
        
        if volume_ratio > 2.5:
            strength['volume_strength'] = 100
        elif volume_ratio > 2.0:
            strength['volume_strength'] = 80
        elif volume_ratio > 1.5:
            strength['volume_strength'] = 60
        elif volume_ratio > 1.2:
            strength['volume_strength'] = 40
        else:
            strength['volume_strength'] = 20
        
        # Momentum analizi
        momentum_signals = analysis.get('momentum_signals', {})
        momentum_score = momentum_signals.get('momentum_score', 0)
        
        if momentum_score > 40:
            strength['momentum_strength'] = 100
        elif momentum_score > 25:
            strength['momentum_strength'] = 80
        elif momentum_score > 15:
            strength['momentum_strength'] = 60
        else:
            strength['momentum_strength'] = 40
        
        # Technical strength
        technical_score = analysis.get('technical_score', 50)
        if technical_score > 75:
            strength['technical_strength'] = 100
        elif technical_score > 65:
            strength['technical_strength'] = 80
        elif technical_score > 55:
            strength['technical_strength'] = 60
        else:
            strength['technical_strength'] = 40
        
        # Pattern strength
        ceiling_potential = analysis.get('ceiling_potential', {})
        ceiling_score = ceiling_potential.get('ceiling_score', 0)
        
        if ceiling_score > 80:
            strength['pattern_strength'] = 100
        elif ceiling_score > 60:
            strength['pattern_strength'] = 80
        elif ceiling_score > 40:
            strength['pattern_strength'] = 60
        else:
            strength['pattern_strength'] = 40
        
        # Toplam skor
        strength['total_score'] = (
            strength['volume_strength'] * 0.3 +
            strength['momentum_strength'] * 0.25 + 
            strength['technical_strength'] * 0.25 +
            strength['pattern_strength'] * 0.2
        )
        
        return strength
    
    def find_best_prediction_signals(self, crown_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """En iyi tahmin sinyallerini bul"""
        all_signals = []
        
        for stock_symbol, stock_data in crown_analysis.items():
            if 'error' in stock_data:
                continue
                
            pre_signals = stock_data.get('pre_signals', [])
            
            for signal in pre_signals:
                signal['stock'] = stock_symbol
                all_signals.append(signal)
        
        if not all_signals:
            return {'error': 'Sinyal bulunamadı'}
        
        # Sinyalleri güç sırasına göre sırala
        all_signals.sort(key=lambda x: x['signal_strength']['total_score'], reverse=True)
        
        # En güçlü sinyalleri analiz et
        top_signals = all_signals[:20]  # En iyi 20 sinyal
        
        # Gün bazında analiz
        day_analysis = {}
        for i in range(1, 6):
            day_signals = [s for s in all_signals if s['days_before_ceiling'] == i]
            if day_signals:
                avg_strength = np.mean([s['signal_strength']['total_score'] for s in day_signals])
                success_count = len([s for s in day_signals if s['signal_strength']['total_score'] > 70])
                
                day_analysis[f'{i}_days_before'] = {
                    'signal_count': len(day_signals),
                    'average_strength': avg_strength,
                    'strong_signals': success_count,
                    'success_rate': success_count / len(day_signals) * 100 if day_signals else 0
                }
        
        # En çok sinyal veren günü bul
        best_day = max(day_analysis.items(), key=lambda x: x[1]['success_rate']) if day_analysis else None
        
        return {
            'total_signals': len(all_signals),
            'top_signals': top_signals[:10],
            'day_analysis': day_analysis,
            'best_prediction_day': best_day,
            'average_signal_strength': np.mean([s['signal_strength']['total_score'] for s in all_signals]),
            'strong_signals_count': len([s for s in all_signals if s['signal_strength']['total_score'] > 70])
        }

def main():
    logging.basicConfig(level=logging.INFO)
    predictor = CrownStockPredictor()
    
    print("\n👑 TAVAN KRALI SİNYAL ANALİZİ")
    print("=" * 50)
    
    crown_analysis = {}
    
    # Her tavan kralını analiz et
    for stock in predictor.crown_stocks:
        print(f"\n🔍 {stock} analiz ediliyor...")
        analysis = predictor.analyze_crown_stock_patterns(stock, days_back=90)  # 3 ay
        crown_analysis[stock] = analysis
        
        if 'error' not in analysis:
            print(f"   • {analysis['total_ceilings']} tavan günü bulundu")
            print(f"   • {len(analysis['pre_signals'])} öncü sinyal tespit edildi")
        else:
            print(f"   • Hata: {analysis['error']}")
    
    # En iyi sinyalleri bul
    best_signals = predictor.find_best_prediction_signals(crown_analysis)
    
    if 'error' in best_signals:
        print(f"\n❌ Hata: {best_signals['error']}")
        return
    
    print(f"\n📊 GENEL SINYAL ANALİZİ:")
    print(f"   • Toplam sinyal sayısı: {best_signals['total_signals']}")
    print(f"   • Ortalama sinyal gücü: {best_signals['average_signal_strength']:.1f}/100")
    print(f"   • Güçlü sinyaller (70+): {best_signals['strong_signals_count']}")
    
    print(f"\n📅 GÜN BAZINDA ANALİZ:")
    day_analysis = best_signals.get('day_analysis', {})
    for day_key, day_data in day_analysis.items():
        day_num = day_key.split('_')[0]
        print(f"   • {day_num} gün öncesi: {day_data['signal_count']} sinyal, "
              f"%{day_data['success_rate']:.1f} başarı, {day_data['average_strength']:.1f} güç")
    
    # En iyi tahmin gününü göster
    best_day = best_signals.get('best_prediction_day')
    if best_day:
        day_name, day_data = best_day
        print(f"\n🎯 EN İYİ TAHMİN GÜNÜ: {day_name.split('_')[0]} gün öncesi")
        print(f"   • Başarı oranı: %{day_data['success_rate']:.1f}")
        print(f"   • Sinyal sayısı: {day_data['signal_count']}")
        print(f"   • Ortalama güç: {day_data['average_strength']:.1f}")
    
    print(f"\n🏆 EN GÜÇLÜ 5 SİNYAL:")
    top_signals = best_signals.get('top_signals', [])[:5]
    for i, signal in enumerate(top_signals, 1):
        date_str = signal['signal_date'].strftime('%Y-%m-%d') if hasattr(signal['signal_date'], 'strftime') else str(signal['signal_date'])
        ceiling_date_str = signal['ceiling_date'].strftime('%Y-%m-%d') if hasattr(signal['ceiling_date'], 'strftime') else str(signal['ceiling_date'])
        
        print(f"   {i}. {signal['stock']} - {date_str}")
        print(f"      → {signal['days_before_ceiling']} gün sonra tavan (% {signal['ceiling_change']:.2f})")
        print(f"      → Sinyal gücü: {signal['signal_strength']['total_score']:.1f}/100")
        print(f"      → Volume: {signal['signal_strength']['volume_strength']}, "
              f"Momentum: {signal['signal_strength']['momentum_strength']}, "
              f"Teknik: {signal['signal_strength']['technical_strength']}")

if __name__ == "__main__":
    main()