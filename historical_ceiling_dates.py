#!/usr/bin/env python3
"""
8 Tavan Yapan Hisselerin Tarihlerini Bul
MRGYO, YESIL, MAKTK'nin tavan yaptığı tarihleri detaylı olarak göster
"""

import pandas as pd
import numpy as np
import logging
from typing import List, Dict, Any
from bist_data_fetcher import BISTDataFetcher
from datetime import datetime

logger = logging.getLogger(__name__)

class HistoricalCeilingDatesFinder:
    def __init__(self):
        """Tarihi tavan tarihlerini bulan sistem"""
        self.data_fetcher = BISTDataFetcher()
        
    def find_ceiling_dates(self, symbol: str, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Belirli bir hisse için tavan yapılan tarihleri bul"""
        if len(data) < 20:
            return []
            
        ceiling_events = []
        
        try:
            for i in range(1, len(data)):
                current_price = data['Close'].iloc[i]
                previous_price = data['Close'].iloc[i-1]
                current_volume = data['Volume'].iloc[i]
                
                if previous_price == 0:
                    continue
                    
                daily_change = ((current_price - previous_price) / previous_price) * 100
                
                # Tavan kriteri: %9.0+ artış
                if daily_change >= 9.0:
                    # Volume bilgisi varsa ekle
                    volume_info = ""
                    if len(data) >= i + 1:
                        avg_volume = data['Volume'].iloc[max(0, i-20):i].mean()
                        if avg_volume > 0:
                            volume_ratio = current_volume / avg_volume
                            volume_info = f" (Hacim: {volume_ratio:.1f}x)"
                    
                    ceiling_event = {
                        'date': data.index[i].strftime('%Y-%m-%d'),
                        'date_formatted': data.index[i].strftime('%d.%m.%Y'),
                        'day_name': data.index[i].strftime('%A'),
                        'change_percent': daily_change,
                        'close_price': current_price,
                        'previous_price': previous_price,
                        'volume': current_volume,
                        'volume_info': volume_info
                    }
                    ceiling_events.append(ceiling_event)
                    
        except Exception as e:
            logger.debug(f"{symbol} tavan tarihleri bulma hatası: {e}")
            
        return ceiling_events
    
    def analyze_ceiling_patterns(self, ceiling_events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Tavan paternlerini analiz et"""
        if not ceiling_events:
            return {}
            
        # Ay dağılımı
        month_distribution = {}
        day_distribution = {}
        
        for event in ceiling_events:
            # Ay analizi
            event_date = datetime.strptime(event['date'], '%Y-%m-%d')
            month = event_date.strftime('%B')
            month_tr = self.get_turkish_month(month)
            month_distribution[month_tr] = month_distribution.get(month_tr, 0) + 1
            
            # Gün analizi  
            day = event['day_name']
            day_tr = self.get_turkish_day(day)
            day_distribution[day_tr] = day_distribution.get(day_tr, 0) + 1
        
        # Ortalamalar
        avg_change = sum(e['change_percent'] for e in ceiling_events) / len(ceiling_events)
        max_change = max(e['change_percent'] for e in ceiling_events)
        
        # Son tavan
        latest_ceiling = max(ceiling_events, key=lambda x: x['date'])
        
        # Tarihler arası farklar
        dates = [datetime.strptime(e['date'], '%Y-%m-%d') for e in ceiling_events]
        dates.sort()
        
        intervals = []
        if len(dates) > 1:
            for i in range(1, len(dates)):
                diff = (dates[i] - dates[i-1]).days
                intervals.append(diff)
        
        avg_interval = sum(intervals) / len(intervals) if intervals else 0
        
        return {
            'month_distribution': month_distribution,
            'day_distribution': day_distribution,
            'avg_change': avg_change,
            'max_change': max_change,
            'latest_ceiling': latest_ceiling,
            'avg_interval_days': avg_interval,
            'intervals': intervals
        }
    
    def get_turkish_month(self, english_month: str) -> str:
        """İngilizce ay ismini Türkçe'ye çevir"""
        months = {
            'January': 'Ocak', 'February': 'Şubat', 'March': 'Mart',
            'April': 'Nisan', 'May': 'Mayıs', 'June': 'Haziran',
            'July': 'Temmuz', 'August': 'Ağustos', 'September': 'Eylül',
            'October': 'Ekim', 'November': 'Kasım', 'December': 'Aralık'
        }
        return months.get(english_month, english_month)
    
    def get_turkish_day(self, english_day: str) -> str:
        """İngilizce gün ismini Türkçe'ye çevir"""
        days = {
            'Monday': 'Pazartesi', 'Tuesday': 'Salı', 'Wednesday': 'Çarşamba',
            'Thursday': 'Perşembe', 'Friday': 'Cuma', 'Saturday': 'Cumartesi',
            'Sunday': 'Pazar'
        }
        return days.get(english_day, english_day)
    
    def analyze_multiple_stocks(self, symbols: List[str]) -> Dict[str, Any]:
        """Birden fazla hisse için tavan analizi"""
        logger.info(f"{len(symbols)} hisse için tarihi tavan analizi yapılıyor...")
        
        # 1 yıllık veri al
        all_data = self.data_fetcher.get_all_bist_data(period="1y")
        
        results = {}
        
        for symbol in symbols:
            stock_symbol_with_suffix = symbol + '.IS'
            
            if stock_symbol_with_suffix not in all_data:
                logger.warning(f"{symbol} için veri bulunamadı")
                continue
                
            data = all_data[stock_symbol_with_suffix]
            if data.empty:
                continue
                
            # Tavan tarihlerini bul
            ceiling_events = self.find_ceiling_dates(symbol, data)
            
            if ceiling_events:
                # Pattern analizi
                patterns = self.analyze_ceiling_patterns(ceiling_events)
                
                results[symbol] = {
                    'ceiling_events': ceiling_events,
                    'patterns': patterns,
                    'total_ceilings': len(ceiling_events)
                }
                
                logger.info(f"{symbol}: {len(ceiling_events)} tavan bulundu")
            else:
                logger.info(f"{symbol}: Tavan bulunamadı")
        
        return results

def main():
    logging.basicConfig(level=logging.INFO)
    
    # 8 tavan yapmış olduğunu söylediğimiz hisseler
    target_stocks = ['MRGYO', 'YESIL', 'MAKTK']
    
    # Karşılaştırma için mevcut tavan kralları da ekleyelim
    comparison_stocks = ['PINSU', 'IZINV', 'ISGSY', 'GRNYO', 'TRHOL']
    
    all_stocks = target_stocks + comparison_stocks
    
    finder = HistoricalCeilingDatesFinder()
    
    print("\n📅 TARİHİ TAVAN ANALİZİ")
    print("=" * 80)
    print("8 tavan yapmış hisseler: MRGYO, YESIL, MAKTK")
    print("Karşılaştırma: Mevcut tavan kralları")
    print("=" * 80)
    
    results = finder.analyze_multiple_stocks(all_stocks)
    
    if not results:
        print("❌ Hiçbir hisse için tavan verisi bulunamadı!")
        return
    
    # Önce hedef hisseleri göster
    print(f"\n🎯 8 TAVAN YAPMIŞ ADAYLAR:")
    print("=" * 50)
    
    for symbol in target_stocks:
        if symbol not in results:
            print(f"\n❌ {symbol}: Veri bulunamadı")
            continue
            
        data = results[symbol]
        ceiling_events = data['ceiling_events']
        patterns = data['patterns']
        
        print(f"\n🔥 {symbol} - {len(ceiling_events)} TAVAN")
        print(f"   📊 Son 1 yılda bulunan tavan sayısı")
        
        if ceiling_events:
            print(f"   📅 Tavan Tarihleri:")
            for i, event in enumerate(ceiling_events, 1):
                date_str = event['date_formatted']
                day_tr = finder.get_turkish_day(event['day_name'])
                change = event['change_percent']
                price = event['close_price']
                volume_info = event['volume_info']
                
                print(f"      {i}. {date_str} ({day_tr}) - %{change:.1f} artış - {price:.2f} TL{volume_info}")
            
            # Pattern bilgileri
            if patterns:
                print(f"   📈 Pattern Analizi:")
                print(f"      • Ortalama artış: %{patterns['avg_change']:.1f}")
                print(f"      • En yüksek artış: %{patterns['max_change']:.1f}")
                print(f"      • Son tavan: {patterns['latest_ceiling']['date_formatted']}")
                
                if patterns['avg_interval_days'] > 0:
                    print(f"      • Ortalama aralık: {patterns['avg_interval_days']:.0f} gün")
                
                # Ay dağılımı
                if patterns['month_distribution']:
                    popular_months = sorted(patterns['month_distribution'].items(), 
                                         key=lambda x: x[1], reverse=True)[:3]
                    months_str = ", ".join([f"{month} ({count})" for month, count in popular_months])
                    print(f"      • Popüler aylar: {months_str}")
                
                # Gün dağılımı
                if patterns['day_distribution']:
                    popular_days = sorted(patterns['day_distribution'].items(), 
                                       key=lambda x: x[1], reverse=True)[:3]
                    days_str = ", ".join([f"{day} ({count})" for day, count in popular_days])
                    print(f"      • Popüler günler: {days_str}")
        else:
            print(f"   ❌ Son 1 yılda tavan bulunamadı")
    
    # Karşılaştırma için mevcut tavan kralları
    print(f"\n\n👑 MEVCUT TAVAN KRALLARI (Karşılaştırma):")
    print("=" * 50)
    
    for symbol in comparison_stocks:
        if symbol not in results:
            print(f"\n❌ {symbol}: Veri bulunamadı")
            continue
            
        data = results[symbol]
        ceiling_events = data['ceiling_events']
        
        print(f"\n👑 {symbol} - {len(ceiling_events)} TAVAN (Son 1 yıl)")
        
        if ceiling_events and len(ceiling_events) > 0:
            # Sadece son 3 tavanı göster
            recent_ceilings = ceiling_events[-3:]
            print(f"   📅 Son Tavanlar:")
            for i, event in enumerate(recent_ceilings, 1):
                date_str = event['date_formatted']
                change = event['change_percent']
                print(f"      {i}. {date_str} - %{change:.1f}")
        else:
            print(f"   ❌ Son 1 yılda tavan bulunamadı")
    
    # Genel karşılaştırma
    print(f"\n📊 GENEL KARŞILAŞTIRMA:")
    print("=" * 50)
    
    target_total = sum(len(results[s]['ceiling_events']) for s in target_stocks if s in results)
    comparison_total = sum(len(results[s]['ceiling_events']) for s in comparison_stocks if s in results)
    
    print(f"🎯 8-Tavan Adayları toplam: {target_total} tavan (son 1 yıl)")
    print(f"👑 Mevcut Krallar toplam: {comparison_total} tavan (son 1 yıl)")
    
    # En aktif hisse
    all_stocks_with_data = [(s, len(results[s]['ceiling_events'])) for s in results.keys()]
    all_stocks_with_data.sort(key=lambda x: x[1], reverse=True)
    
    if all_stocks_with_data:
        most_active = all_stocks_with_data[0]
        print(f"🏆 En aktif: {most_active[0]} ({most_active[1]} tavan)")
    
    print(f"\n💡 NOT: Bu analiz son 1 yıllık veriyi kapsar.")
    print(f"📅 Daha eski tavanlar için daha uzun süreli veri gerekir.")

if __name__ == "__main__":
    main()