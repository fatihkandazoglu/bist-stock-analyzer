#!/usr/bin/env python3
"""
Tavan Öncesi Sinyal Analizi
Tavan yapan hisselerin tavan yapmadan önceki günlerdeki ortak özelliklerini bulur.
"""

import pandas as pd
import numpy as np
import logging
from typing import List, Dict, Any
from bist_data_fetcher import BISTDataFetcher
from technical_analyzer import TechnicalAnalyzer

logger = logging.getLogger(__name__)

class PreCeilingSignalAnalyzer:
    def __init__(self):
        """Tavan öncesi sinyal analiz sistemi"""
        self.data_fetcher = BISTDataFetcher()
        self.technical_analyzer = TechnicalAnalyzer()
        
    def analyze_pre_ceiling_signals(self, days_back: int = 45) -> Dict[str, Any]:
        """Tavan öncesi sinyalleri analiz et"""
        logger.info(f"Son {days_back} gündeki tavan öncesi sinyaller analiz ediliyor...")
        
        # Tüm BİST hisselerinin verilerini çek
        all_data = self.data_fetcher.get_all_bist_data(period=f"{days_back + 5}d")
        
        pre_ceiling_data = []
        
        for symbol, data in all_data.items():
            if data.empty or len(data) < 10:
                continue
                
            try:
                # Tavan günlerini bul
                for i in range(5, len(data)):  # En az 5 gün önceki veri olsun
                    current_price = data['Close'].iloc[i]
                    previous_price = data['Close'].iloc[i-1]
                    
                    if previous_price == 0:
                        continue
                        
                    daily_change = ((current_price - previous_price) / previous_price) * 100
                    
                    # Tavan günü mü? (%9+ artış)
                    if daily_change >= 9.0:
                        # Tavan öncesi 1-4 gün arası verileri analiz et
                        for days_before in range(1, 5):
                            pre_index = i - days_before
                            
                            if pre_index < 20:  # Yeterli geçmiş veri yoksa geç
                                continue
                                
                            # Tavan öncesi günün verileri
                            pre_data = data.iloc[pre_index-19:pre_index+1]  # 20 günlük window
                            
                            if len(pre_data) < 20:
                                continue
                                
                            # O günün fiyat bilgileri
                            pre_close = data['Close'].iloc[pre_index]
                            pre_volume = data['Volume'].iloc[pre_index]
                            pre_high = data['High'].iloc[pre_index]
                            pre_low = data['Low'].iloc[pre_index]
                            
                            # Önceki günle karşılaştırma
                            if pre_index > 0:
                                prev_close = data['Close'].iloc[pre_index-1] 
                                prev_volume = data['Volume'].iloc[pre_index-1]
                                pre_daily_change = ((pre_close - prev_close) / prev_close * 100) if prev_close > 0 else 0
                            else:
                                prev_close = pre_close
                                prev_volume = pre_volume
                                pre_daily_change = 0
                            
                            # Volume analizi
                            if pre_index >= 20:
                                avg_volume_20 = data['Volume'].iloc[pre_index-20:pre_index].mean()
                                volume_ratio = pre_volume / avg_volume_20 if avg_volume_20 > 0 else 1
                            else:
                                volume_ratio = 1
                                
                            # Son 5 gün momentum
                            momentum_5d = []
                            for j in range(max(0, pre_index-5), pre_index):
                                if j > 0:
                                    momentum_change = ((data['Close'].iloc[j] - data['Close'].iloc[j-1]) / data['Close'].iloc[j-1] * 100)
                                    momentum_5d.append(momentum_change)
                            
                            avg_momentum_5d = np.mean(momentum_5d) if momentum_5d else 0
                            
                            # RSI hesapla (basit)
                            rsi_window = min(14, pre_index)
                            if pre_index >= rsi_window:
                                closes = data['Close'].iloc[pre_index-rsi_window:pre_index+1]
                                gains = closes.diff().clip(lower=0)
                                losses = (-closes.diff()).clip(lower=0)
                                avg_gain = gains.mean()
                                avg_loss = losses.mean()
                                
                                if avg_loss == 0:
                                    rsi = 100
                                else:
                                    rs = avg_gain / avg_loss
                                    rsi = 100 - (100 / (1 + rs))
                            else:
                                rsi = 50
                                
                            pre_ceiling_data.append({
                                'symbol': symbol.replace('.IS', ''),
                                'days_before_ceiling': days_before,
                                'ceiling_date': data.index[i],
                                'ceiling_change': daily_change,
                                'pre_date': data.index[pre_index],
                                'pre_price': pre_close,
                                'pre_volume': pre_volume,
                                'volume_ratio': volume_ratio,
                                'pre_daily_change': pre_daily_change,
                                'avg_momentum_5d': avg_momentum_5d,
                                'rsi': rsi,
                                'price_range': pre_close,
                                'volume_momentum': pre_volume / prev_volume if prev_volume > 0 else 1
                            })
                            
            except Exception as e:
                logger.debug(f"{symbol} pre-ceiling analiz hatası: {e}")
                continue
                
        logger.info(f"Toplam {len(pre_ceiling_data)} tavan öncesi veri noktası bulundu")
        return pre_ceiling_data
    
    def calculate_average_signals(self, pre_ceiling_data: List[Dict]) -> Dict[str, Any]:
        """Tavan öncesi sinyallerin ortalamalarını hesapla"""
        if not pre_ceiling_data:
            return {}
            
        # Gün bazında grupla
        day_groups = {}
        for i in range(1, 5):
            day_groups[i] = [d for d in pre_ceiling_data if d['days_before_ceiling'] == i]
        
        analysis = {}
        
        for days_before, data_points in day_groups.items():
            if not data_points:
                continue
                
            # Ortalamalar
            avg_volume_ratio = np.mean([d['volume_ratio'] for d in data_points if d['volume_ratio'] > 0])
            avg_daily_change = np.mean([d['pre_daily_change'] for d in data_points])
            avg_momentum_5d = np.mean([d['avg_momentum_5d'] for d in data_points])
            avg_rsi = np.mean([d['rsi'] for d in data_points if 0 < d['rsi'] < 100])
            avg_volume_momentum = np.mean([d['volume_momentum'] for d in data_points if d['volume_momentum'] > 0])
            
            # Medyanlar
            median_volume_ratio = np.median([d['volume_ratio'] for d in data_points if d['volume_ratio'] > 0])
            median_daily_change = np.median([d['pre_daily_change'] for d in data_points])
            median_rsi = np.median([d['rsi'] for d in data_points if 0 < d['rsi'] < 100])
            
            # Kategorik analizler
            high_volume_count = len([d for d in data_points if d['volume_ratio'] > 2.0])
            positive_change_count = len([d for d in data_points if d['pre_daily_change'] > 2.0])
            strong_momentum_count = len([d for d in data_points if d['avg_momentum_5d'] > 2.0])
            oversold_count = len([d for d in data_points if d['rsi'] < 30])
            bullish_rsi_count = len([d for d in data_points if 50 <= d['rsi'] <= 70])
            
            total_count = len(data_points)
            
            # En çok hangi hisseler tavan öncesi sinyal veriyor
            symbol_counts = {}
            for d in data_points:
                symbol = d['symbol']
                symbol_counts[symbol] = symbol_counts.get(symbol, 0) + 1
            top_symbols = sorted(symbol_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            
            analysis[f'{days_before}_days_before'] = {
                'total_signals': total_count,
                'averages': {
                    'volume_ratio': avg_volume_ratio,
                    'daily_change': avg_daily_change,
                    'momentum_5d': avg_momentum_5d,
                    'rsi': avg_rsi,
                    'volume_momentum': avg_volume_momentum
                },
                'medians': {
                    'volume_ratio': median_volume_ratio,
                    'daily_change': median_daily_change,
                    'rsi': median_rsi
                },
                'signal_percentages': {
                    'high_volume_2x+': (high_volume_count / total_count * 100) if total_count > 0 else 0,
                    'positive_change_2%+': (positive_change_count / total_count * 100) if total_count > 0 else 0,
                    'strong_momentum_2%+': (strong_momentum_count / total_count * 100) if total_count > 0 else 0,
                    'oversold_rsi_<30': (oversold_count / total_count * 100) if total_count > 0 else 0,
                    'bullish_rsi_50-70': (bullish_rsi_count / total_count * 100) if total_count > 0 else 0
                },
                'top_signaling_stocks': top_symbols
            }
        
        return analysis
    
    def find_common_patterns(self, analysis: Dict) -> List[str]:
        """Ortak paternleri bul"""
        patterns = []
        
        # Tüm günlerde ortak olan özellikler
        all_days = [key for key in analysis.keys() if 'days_before' in key]
        
        if not all_days:
            return patterns
            
        # Volume pattern kontrolü
        high_volume_days = []
        for day_key in all_days:
            day_data = analysis[day_key]
            if day_data['averages']['volume_ratio'] > 1.5:
                high_volume_days.append(day_key)
                
        if len(high_volume_days) >= len(all_days) * 0.7:  # %70+ günlerde
            patterns.append(f"🔥 Tavan öncesi {len(high_volume_days)}/{len(all_days)} günde yüksek hacim (1.5x+)")
            
        # RSI pattern kontrolü
        optimal_rsi_days = []
        for day_key in all_days:
            day_data = analysis[day_key]
            avg_rsi = day_data['averages']['rsi']
            if 45 <= avg_rsi <= 65:  # Optimal RSI aralığı
                optimal_rsi_days.append(day_key)
                
        if optimal_rsi_days:
            patterns.append(f"📊 Tavan öncesi {len(optimal_rsi_days)}/{len(all_days)} günde optimal RSI (45-65)")
            
        # Momentum pattern kontrolü
        positive_momentum_days = []
        for day_key in all_days:
            day_data = analysis[day_key]
            if day_data['averages']['momentum_5d'] > 0:
                positive_momentum_days.append(day_key)
                
        if positive_momentum_days:
            patterns.append(f"⚡ Tavan öncesi {len(positive_momentum_days)}/{len(all_days)} günde pozitif momentum")
        
        # En güçlü sinyal günü
        best_day = None
        best_score = 0
        
        for day_key in all_days:
            day_data = analysis[day_key]
            # Basit skor hesapla
            score = (
                day_data['averages']['volume_ratio'] * 30 +
                max(0, day_data['averages']['daily_change']) * 10 +
                max(0, day_data['averages']['momentum_5d']) * 20 +
                (65 - abs(day_data['averages']['rsi'] - 55)) * 2  # 55'e yakınlık
            )
            
            if score > best_score:
                best_score = score
                best_day = day_key
        
        if best_day:
            patterns.append(f"🎯 En güçlü sinyal günü: {best_day} (Skor: {best_score:.1f})")
        
        return patterns

def main():
    logging.basicConfig(level=logging.INFO)
    analyzer = PreCeilingSignalAnalyzer()
    
    print("\n🔍 TAVAN ÖNCESİ SİNYAL ANALİZİ")
    print("=" * 50)
    
    # Tavan öncesi verileri topla
    pre_ceiling_data = analyzer.analyze_pre_ceiling_signals(days_back=60)
    
    if not pre_ceiling_data:
        print("❌ Tavan öncesi veri bulunamadı!")
        return
    
    # Ortalama sinyalleri hesapla
    analysis = analyzer.calculate_average_signals(pre_ceiling_data)
    
    if not analysis:
        print("❌ Analiz yapılamadı!")
        return
    
    print(f"\n📊 TAVAN ÖNCESİ ORTALAMA SİNYALLER:")
    
    for day_key, day_data in analysis.items():
        days = day_key.split('_')[0]
        print(f"\n{'='*20} {days} GÜN ÖNCESİ {'='*20}")
        print(f"📈 Toplam sinyal sayısı: {day_data['total_signals']}")
        
        print(f"\n📊 ORTALAMALAR:")
        avgs = day_data['averages']
        print(f"   • Hacim oranı: {avgs['volume_ratio']:.2f}x")
        print(f"   • Günlük değişim: %{avgs['daily_change']:.2f}")
        print(f"   • 5 gün momentum: %{avgs['momentum_5d']:.2f}")
        print(f"   • RSI: {avgs['rsi']:.1f}")
        print(f"   • Hacim momentum: {avgs['volume_momentum']:.2f}x")
        
        print(f"\n📊 MEDYANLAR:")
        meds = day_data['medians']
        print(f"   • Hacim oranı: {meds['volume_ratio']:.2f}x")
        print(f"   • Günlük değişim: %{meds['daily_change']:.2f}")
        print(f"   • RSI: {meds['rsi']:.1f}")
        
        print(f"\n🎯 SİNYAL YÜZDE ORANLARI:")
        percs = day_data['signal_percentages']
        print(f"   • Yüksek hacim (2x+): %{percs['high_volume_2x+']:.1f}")
        print(f"   • Pozitif değişim (2%+): %{percs['positive_change_2%+']:.1f}")
        print(f"   • Güçlü momentum (2%+): %{percs['strong_momentum_2%+']:.1f}")
        print(f"   • Oversold RSI (<30): %{percs['oversold_rsi_<30']:.1f}")
        print(f"   • İdeal RSI (50-70): %{percs['bullish_rsi_50-70']:.1f}")
        
        print(f"\n🏆 EN ÇOK SİNYAL VEREN HİSSELER:")
        for i, (stock, count) in enumerate(day_data['top_signaling_stocks'][:3], 1):
            print(f"   {i}. {stock}: {count} sinyal")
    
    # Ortak paternleri bul
    patterns = analyzer.find_common_patterns(analysis)
    
    if patterns:
        print(f"\n💡 ORTAK PATERNLER:")
        for pattern in patterns:
            print(f"   {pattern}")
    
    print(f"\n🎯 ÖNEMLİ SONUÇLAR:")
    if analysis:
        # 1 gün öncesi en kritik
        one_day = analysis.get('1_days_before', {})
        if one_day:
            avgs = one_day.get('averages', {})
            print(f"   • 1 gün öncesi ortalama hacim: {avgs.get('volume_ratio', 0):.2f}x")
            print(f"   • 1 gün öncesi ortalama RSI: {avgs.get('rsi', 0):.1f}")
            print(f"   • 1 gün öncesi ortalama değişim: %{avgs.get('daily_change', 0):.2f}")

if __name__ == "__main__":
    main()