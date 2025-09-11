#!/usr/bin/env python3
"""
SKBNK 18:00 Toparlanma Monitörü
Bu script SKBNK hissesini sürekli takip eder ve kritik fiyat seviyelerinde uyarı verir.
"""

import yfinance as yf
import time
from datetime import datetime, timedelta
import sys

class SKBNKMonitor:
    def __init__(self):
        self.symbol = 'SKBNK.IS'
        self.entry_price = 7.51
        self.target_1 = 7.70  # %2.5 kar
        self.target_2 = 7.85  # %4.5 kar  
        self.stop_loss = 7.36  # %-2 zarar
        self.market_close = datetime.now().replace(hour=18, minute=0, second=0, microsecond=0)
        
        print("🚀 SKBNK TOPARLANMA MONİTÖRÜ BAŞLATILDI")
        print("=" * 50)
        print(f"📊 Giriş fiyatı: {self.entry_price:.2f} TL")
        print(f"🎯 Hedef 1: {self.target_1:.2f} TL (%2.5)")
        print(f"🎯 Hedef 2: {self.target_2:.2f} TL (%4.5)")
        print(f"❌ Stop Loss: {self.stop_loss:.2f} TL (%-2)")
        print(f"⏰ Kapanış: {self.market_close.strftime('%H:%M')}")
        print("=" * 50)
        
    def get_current_price(self):
        """Güncel fiyatı al"""
        try:
            ticker = yf.Ticker(self.symbol)
            data = ticker.history(period='1d', interval='1m')
            if len(data) > 0:
                return data['Close'].iloc[-1]
            return None
        except Exception as e:
            print(f"❌ Fiyat alınamadı: {e}")
            return None
    
    def calculate_performance(self, current_price):
        """Performans hesapla"""
        if current_price and self.entry_price:
            return ((current_price - self.entry_price) / self.entry_price) * 100
        return 0
    
    def check_signals(self, current_price, performance):
        """Kritik seviyeleri kontrol et"""
        signals = []
        
        if current_price >= self.target_2:
            signals.append("🚀 HEDEF 2 ULAŞILDI - TAMAMEN SAT!")
        elif current_price >= self.target_1:
            signals.append("🎯 HEDEF 1 ULAŞILDI - %50 SAT!")
        elif current_price <= self.stop_loss:
            signals.append("❌ STOP LOSS ULAŞILDI - HEMEN SAT!")
        elif performance >= 1.5:
            signals.append("⚡ İyi gidiyor - takip et")
        elif performance <= -1:
            signals.append("⚠️ Düşüş var - dikkat!")
            
        return signals
    
    def time_check(self):
        """Kapanış zamanı kontrolü"""
        now = datetime.now()
        time_to_close = self.market_close - now
        
        if time_to_close <= timedelta(minutes=15):
            return "🚨 KAPANIŞ 15 DK KALDI - PİYASADAN ÇIK!"
        elif time_to_close <= timedelta(hours=1):
            return "⏰ Kapanışa 1 saat kaldı - hazırlan"
        elif time_to_close <= timedelta(hours=2):
            return "⏳ Kapanışa 2 saat kaldı"
        else:
            return f"🕒 Kapanışa {time_to_close.seconds//3600}h {(time_to_close.seconds//60)%60}m"
    
    def monitor(self):
        """Ana monitoring döngüsü"""
        print("📡 Monitoring başladı - Her 2 dakikada kontrol...")
        print("Ctrl+C ile durdurabilirsiniz\n")
        
        try:
            while datetime.now() < self.market_close:
                current_price = self.get_current_price()
                
                if current_price:
                    performance = self.calculate_performance(current_price)
                    signals = self.check_signals(current_price, performance)
                    time_status = self.time_check()
                    
                    # Status display
                    now_str = datetime.now().strftime("%H:%M:%S")
                    print(f"\n[{now_str}] SKBNK: {current_price:.2f} TL | %{performance:+.2f} | {time_status}")
                    
                    # Kritik uyarılar
                    for signal in signals:
                        print(f"🔔 {signal}")
                    
                    # Güncellenen hedefler
                    if performance > 0:
                        print(f"📈 Kar: +{(current_price - self.entry_price) * 1000:.0f} TL (1000 hisse için)")
                    elif performance < 0:
                        print(f"📉 Zarar: {(current_price - self.entry_price) * 1000:.0f} TL (1000 hisse için)")
                    
                else:
                    print(f"❌ [{datetime.now().strftime('%H:%M:%S')}] Fiyat alınamadı")
                
                # 2 dakika bekle
                time.sleep(120)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Monitoring durduruldu.")
        
        print("\n🔚 Market kapandı - Monitoring sona erdi.")

if __name__ == "__main__":
    monitor = SKBNKMonitor()
    monitor.monitor()