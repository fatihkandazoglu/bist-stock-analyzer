#!/usr/bin/env python3
"""
Ağırlıklı Tavan Öncesi Analizi
Tavan öncesi sinyallerin ağırlıklı ortalamalarını hesaplar.
Yakın günlere daha fazla ağırlık verir.
"""

import pandas as pd
import numpy as np
import logging
from typing import List, Dict, Any
from bist_data_fetcher import BISTDataFetcher

logger = logging.getLogger(__name__)

class WeightedCeilingAnalyzer:
    def __init__(self):
        """Ağırlıklı tavan analiz sistemi"""
        self.data_fetcher = BISTDataFetcher()
        
        # Gün bazında ağırlıklar (yakın günler daha önemli)
        self.day_weights = {
            1: 4.0,  # 1 gün öncesi en önemli
            2: 3.0,  # 2 gün öncesi 
            3: 2.0,  # 3 gün öncesi
            4: 1.0   # 4 gün öncesi en az önemli
        }
        
    def collect_weighted_ceiling_data(self, days_back: int = 60) -> List[Dict[str, Any]]:
        """Tavan öncesi verileri topla ve ağırlıkla"""
        logger.info(f"Son {days_back} gündeki ağırlıklı tavan verileri toplanıyor...")
        
        # Tüm BİST hisselerinin verilerini çek
        all_data = self.data_fetcher.get_all_bist_data(period=f"{days_back + 5}d")
        
        weighted_data = []
        
        for symbol, data in all_data.items():
            if data.empty or len(data) < 25:
                continue
                
            try:
                # Tavan günlerini bul
                for i in range(20, len(data)):  # En az 20 gün geçmiş veri
                    current_price = data['Close'].iloc[i]
                    previous_price = data['Close'].iloc[i-1]
                    
                    if previous_price == 0:
                        continue
                        
                    daily_change = ((current_price - previous_price) / previous_price) * 100
                    
                    # Tavan günü mü? (%9+ artış)
                    if daily_change >= 9.0:
                        # Bu tavan için ağırlıklı öncesi verileri hesapla
                        ceiling_profile = self.calculate_weighted_profile(data, i)
                        
                        if ceiling_profile:
                            ceiling_profile.update({
                                'symbol': symbol.replace('.IS', ''),
                                'ceiling_date': data.index[i],
                                'ceiling_change': daily_change,
                                'ceiling_price': current_price
                            })
                            weighted_data.append(ceiling_profile)
                            
            except Exception as e:
                logger.debug(f"{symbol} ağırlıklı analiz hatası: {e}")
                continue
                
        logger.info(f"Toplam {len(weighted_data)} ağırlıklı tavan profili oluşturuldu")
        return weighted_data
    
    def calculate_weighted_profile(self, data: pd.DataFrame, ceiling_index: int) -> Dict[str, Any]:
        """Bir tavan için ağırlıklı profil hesapla"""
        profile = {
            'weighted_volume_ratio': 0,
            'weighted_daily_change': 0,
            'weighted_rsi': 0,
            'weighted_momentum_5d': 0,
            'weighted_price_momentum': 0,
            'total_weight': 0,
            'signal_strength_by_day': {}
        }
        
        # Her gün için ağırlıklı hesaplama
        for days_before in range(1, 5):  # 1-4 gün öncesi
            signal_index = ceiling_index - days_before
            
            if signal_index < 20:  # Yeterli geçmiş veri yoksa geç
                continue
                
            weight = self.day_weights[days_before]
            
            try:
                # O günün verileri
                signal_close = data['Close'].iloc[signal_index]
                signal_volume = data['Volume'].iloc[signal_index]
                
                # Günlük değişim
                if signal_index > 0:
                    prev_close = data['Close'].iloc[signal_index-1]
                    daily_change = ((signal_close - prev_close) / prev_close * 100) if prev_close > 0 else 0
                else:
                    daily_change = 0
                
                # Volume ratio (20 gün ortalama)
                if signal_index >= 20:
                    avg_volume_20 = data['Volume'].iloc[signal_index-20:signal_index].mean()
                    volume_ratio = signal_volume / avg_volume_20 if avg_volume_20 > 0 else 1
                else:
                    volume_ratio = 1
                    
                # 5 gün momentum
                momentum_5d = []
                for j in range(max(0, signal_index-5), signal_index):
                    if j > 0:
                        momentum_change = ((data['Close'].iloc[j] - data['Close'].iloc[j-1]) / data['Close'].iloc[j-1] * 100)
                        momentum_5d.append(momentum_change)
                avg_momentum_5d = np.mean(momentum_5d) if momentum_5d else 0
                
                # Basit RSI hesaplama
                rsi_window = min(14, signal_index)
                if signal_index >= rsi_window:
                    closes = data['Close'].iloc[signal_index-rsi_window:signal_index+1]
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
                
                # Fiyat momentum (son 3 günün ortalamasına göre)
                if signal_index >= 3:
                    avg_price_3d = data['Close'].iloc[signal_index-3:signal_index].mean()
                    price_momentum = ((signal_close - avg_price_3d) / avg_price_3d * 100) if avg_price_3d > 0 else 0
                else:
                    price_momentum = 0
                
                # Ağırlıklı toplama ekle
                profile['weighted_volume_ratio'] += volume_ratio * weight
                profile['weighted_daily_change'] += daily_change * weight
                profile['weighted_rsi'] += rsi * weight
                profile['weighted_momentum_5d'] += avg_momentum_5d * weight
                profile['weighted_price_momentum'] += price_momentum * weight
                profile['total_weight'] += weight
                
                # Gün bazında sinyal gücü
                signal_strength = (
                    min(100, volume_ratio * 25) +  # Volume component
                    min(100, max(0, daily_change) * 10) +  # Daily change component
                    min(100, abs(rsi - 60) * -1 + 70) +  # RSI component (60'a yakınlık)
                    min(100, max(0, avg_momentum_5d) * 15)  # Momentum component
                ) / 4
                
                profile['signal_strength_by_day'][days_before] = {
                    'strength': signal_strength,
                    'volume_ratio': volume_ratio,
                    'daily_change': daily_change,
                    'rsi': rsi,
                    'momentum_5d': avg_momentum_5d,
                    'weight': weight
                }
                
            except Exception as e:
                logger.debug(f"Gün hesaplama hatası: {e}")
                continue
        
        # Ağırlıklı ortalamaları hesapla
        if profile['total_weight'] > 0:
            profile['weighted_volume_ratio'] /= profile['total_weight']
            profile['weighted_daily_change'] /= profile['total_weight']
            profile['weighted_rsi'] /= profile['total_weight']
            profile['weighted_momentum_5d'] /= profile['total_weight']
            profile['weighted_price_momentum'] /= profile['total_weight']
        
        return profile
    
    def analyze_weighted_averages(self, weighted_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Ağırlıklı ortalamaları analiz et"""
        if not weighted_data:
            return {}
        
        analysis = {
            'total_ceilings': len(weighted_data),
            'weighted_averages': {},
            'day_by_day_analysis': {},
            'signal_strength_analysis': {},
            'top_performers': {}
        }
        
        # Genel ağırlıklı ortalamalar
        all_volume_ratios = [d['weighted_volume_ratio'] for d in weighted_data if d['weighted_volume_ratio'] > 0]
        all_daily_changes = [d['weighted_daily_change'] for d in weighted_data]
        all_rsi_values = [d['weighted_rsi'] for d in weighted_data if 0 < d['weighted_rsi'] < 100]
        all_momentum_5d = [d['weighted_momentum_5d'] for d in weighted_data]
        all_price_momentum = [d['weighted_price_momentum'] for d in weighted_data]
        
        analysis['weighted_averages'] = {
            'volume_ratio': np.mean(all_volume_ratios) if all_volume_ratios else 0,
            'daily_change': np.mean(all_daily_changes) if all_daily_changes else 0,
            'rsi': np.mean(all_rsi_values) if all_rsi_values else 0,
            'momentum_5d': np.mean(all_momentum_5d) if all_momentum_5d else 0,
            'price_momentum': np.mean(all_price_momentum) if all_price_momentum else 0
        }
        
        # Gün bazında detay analizi
        for day in range(1, 5):
            day_data = []
            for ceiling in weighted_data:
                if day in ceiling['signal_strength_by_day']:
                    day_data.append(ceiling['signal_strength_by_day'][day])
            
            if day_data:
                analysis['day_by_day_analysis'][f'{day}_days_before'] = {
                    'count': len(day_data),
                    'avg_strength': np.mean([d['strength'] for d in day_data]),
                    'avg_volume_ratio': np.mean([d['volume_ratio'] for d in day_data]),
                    'avg_daily_change': np.mean([d['daily_change'] for d in day_data]),
                    'avg_rsi': np.mean([d['rsi'] for d in day_data]),
                    'avg_momentum_5d': np.mean([d['momentum_5d'] for d in day_data]),
                    'weight': day_data[0]['weight'],
                    # Yüzde hesaplamaları
                    'high_volume_pct': len([d for d in day_data if d['volume_ratio'] > 2.0]) / len(day_data) * 100,
                    'positive_change_pct': len([d for d in day_data if d['daily_change'] > 2.0]) / len(day_data) * 100,
                    'strong_momentum_pct': len([d for d in day_data if d['momentum_5d'] > 2.0]) / len(day_data) * 100,
                    'ideal_rsi_pct': len([d for d in day_data if 50 <= d['rsi'] <= 70]) / len(day_data) * 100
                }
        
        # En güçlü sinyalleri bul
        all_strengths = []
        for ceiling in weighted_data:
            for day, day_info in ceiling['signal_strength_by_day'].items():
                all_strengths.append({
                    'symbol': ceiling['symbol'],
                    'days_before': day,
                    'strength': day_info['strength'],
                    'volume_ratio': day_info['volume_ratio'],
                    'daily_change': day_info['daily_change'],
                    'rsi': day_info['rsi'],
                    'ceiling_change': ceiling['ceiling_change']
                })
        
        # En güçlü 10 sinyal
        all_strengths.sort(key=lambda x: x['strength'], reverse=True)
        analysis['top_signals'] = all_strengths[:10]
        
        # Hisse bazında performans
        symbol_performance = {}
        for ceiling in weighted_data:
            symbol = ceiling['symbol']
            if symbol not in symbol_performance:
                symbol_performance[symbol] = {
                    'ceiling_count': 0,
                    'avg_weighted_volume': 0,
                    'avg_weighted_change': 0,
                    'avg_weighted_rsi': 0
                }
            
            symbol_performance[symbol]['ceiling_count'] += 1
            symbol_performance[symbol]['avg_weighted_volume'] += ceiling['weighted_volume_ratio']
            symbol_performance[symbol]['avg_weighted_change'] += ceiling['weighted_daily_change']
            symbol_performance[symbol]['avg_weighted_rsi'] += ceiling['weighted_rsi']
        
        # Ortalama hesapla
        for symbol, perf in symbol_performance.items():
            count = perf['ceiling_count']
            perf['avg_weighted_volume'] /= count
            perf['avg_weighted_change'] /= count
            perf['avg_weighted_rsi'] /= count
        
        # En iyi performans gösterenleri sırala
        top_performers = sorted(symbol_performance.items(), 
                              key=lambda x: x[1]['ceiling_count'], reverse=True)[:10]
        
        analysis['top_performers'] = top_performers
        
        return analysis

def main():
    logging.basicConfig(level=logging.INFO)
    analyzer = WeightedCeilingAnalyzer()
    
    print("\n⚖️ AĞIRLIKLI TAVAN ÖNCESİ ANALİZİ")
    print("=" * 60)
    print("Ağırlık sistemi: 1 gün öncesi=4x, 2 gün=3x, 3 gün=2x, 4 gün=1x")
    print("=" * 60)
    
    # Ağırlıklı verileri topla
    weighted_data = analyzer.collect_weighted_ceiling_data(days_back=75)
    
    if not weighted_data:
        print("❌ Ağırlıklı veri bulunamadı!")
        return
    
    # Ağırlıklı analizi hesapla
    analysis = analyzer.analyze_weighted_averages(weighted_data)
    
    if not analysis:
        print("❌ Analiz yapılamadı!")
        return
    
    print(f"\n📊 GENEL AĞIRLIKLI ORTALAMALAR:")
    print(f"   📈 Toplam tavan sayısı: {analysis['total_ceilings']}")
    
    weighted_avgs = analysis['weighted_averages']
    print(f"\n🎯 AĞIRLIKLI ORTALAMA SİNYALLER:")
    print(f"   • Hacim oranı: {weighted_avgs['volume_ratio']:.2f}x")
    print(f"   • Günlük değişim: %{weighted_avgs['daily_change']:.2f}")
    print(f"   • RSI: {weighted_avgs['rsi']:.1f}")
    print(f"   • 5 gün momentum: %{weighted_avgs['momentum_5d']:.2f}")
    print(f"   • Fiyat momentum: %{weighted_avgs['price_momentum']:.2f}")
    
    print(f"\n📅 GÜN BAZINDA DETAY ANALİZ:")
    day_analysis = analysis['day_by_day_analysis']
    
    for day_key in ['1_days_before', '2_days_before', '3_days_before', '4_days_before']:
        if day_key in day_analysis:
            day_data = day_analysis[day_key]
            day_num = day_key.split('_')[0]
            weight = day_data['weight']
            
            print(f"\n   🕐 {day_num} GÜN ÖNCESİ (Ağırlık: {weight}x):")
            print(f"      • Sinyal gücü: {day_data['avg_strength']:.1f}/100")
            print(f"      • Hacim oranı: {day_data['avg_volume_ratio']:.2f}x")
            print(f"      • Günlük değişim: %{day_data['avg_daily_change']:.2f}")
            print(f"      • RSI: {day_data['avg_rsi']:.1f}")
            print(f"      • Momentum: %{day_data['avg_momentum_5d']:.2f}")
            print(f"      • Yüksek hacim %: {day_data['high_volume_pct']:.1f}")
            print(f"      • Pozitif değişim %: {day_data['positive_change_pct']:.1f}")
    
    print(f"\n🏆 EN GÜÇLÜ 5 AĞIRLIKLI SİNYAL:")
    top_signals = analysis['top_signals'][:5]
    
    for i, signal in enumerate(top_signals, 1):
        print(f"   {i}. {signal['symbol']} - {signal['days_before']} gün öncesi")
        print(f"      → Sinyal gücü: {signal['strength']:.1f}/100")
        print(f"      → Hacim: {signal['volume_ratio']:.2f}x, Değişim: %{signal['daily_change']:.2f}, RSI: {signal['rsi']:.1f}")
        print(f"      → Sonuç: %{signal['ceiling_change']:.2f} tavan")
    
    print(f"\n👑 EN ÇOK TAVAN YAPAN HİSSELER (Ağırlıklı Profilleri):")
    top_performers = analysis['top_performers'][:5]
    
    for i, (symbol, perf) in enumerate(top_performers, 1):
        print(f"   {i}. {symbol}: {perf['ceiling_count']} tavan")
        print(f"      → Ağırlıklı hacim: {perf['avg_weighted_volume']:.2f}x")
        print(f"      → Ağırlıklı değişim: %{perf['avg_weighted_change']:.2f}")
        print(f"      → Ağırlıklı RSI: {perf['avg_weighted_rsi']:.1f}")
    
    print(f"\n💡 ÖNEMLİ ÇIKARILAR:")
    
    # En iyi sinyal gününü bul
    best_day = None
    best_strength = 0
    for day_key, day_data in day_analysis.items():
        if day_data['avg_strength'] > best_strength:
            best_strength = day_data['avg_strength']
            best_day = day_key.split('_')[0]
    
    if best_day:
        print(f"   🎯 En güçlü sinyal günü: {best_day} gün öncesi ({best_strength:.1f} güç)")
    
    # Kritik threshold'ları bul
    ideal_volume = weighted_avgs['volume_ratio']
    ideal_rsi = weighted_avgs['rsi']
    ideal_change = weighted_avgs['daily_change']
    
    print(f"   📊 İdeal ağırlıklı profil:")
    print(f"      • Hacim >= {ideal_volume:.2f}x")
    print(f"      • RSI yaklaşık {ideal_rsi:.0f}")
    print(f"      • Günlük değişim >= %{ideal_change:.1f}")

if __name__ == "__main__":
    main()