#!/usr/bin/env python3
"""
🕰️ GÜNLÜK TAVAN TARAMA OTOMASYONU
================================
Her gün sabah 08:30'da otomatik tarama yapar
Telegram bildirimi gönderir
"""

import schedule
import time
import os
from datetime import datetime
from hybrid_ceiling_scanner import HybridCeilingScanner

class DailyCeilingAutomation:
    def __init__(self):
        self.scanner = HybridCeilingScanner()
        
    def morning_scan_job(self):
        """
        🌅 SABAH TARAMA GÖREVI (08:30)
        """
        try:
            print(f"\n🎯 GÜNLÜK TAVAN TARAMASI BAŞLIYOR: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("=" * 70)
            
            # Ana taramayı çalıştır
            results = self.scanner.run_daily_scan()
            
            # Başarı bilgisi
            high_risk_count = len([r for r in results if r['risk_level'] == 'YÜKSEK'])
            medium_risk_count = len([r for r in results if r['risk_level'] == 'ORTA'])
            
            print(f"\n✅ TARAMA TAMAMLANDI!")
            print(f"🎯 Yüksek risk adayları: {high_risk_count}")
            print(f"⚠️ Orta risk adayları: {medium_risk_count}")
            print(f"📊 Toplam aday: {len(results)}")
            print("=" * 70)
            
        except Exception as e:
            error_message = f"❌ SABAH TARAMA HATASI: {e}"
            print(error_message)
            
            # Hata durumunda da bildirim gönder
            try:
                self.scanner.send_telegram_alert(f"🚨 Sistem Hatası\n\n{error_message}\n\nZaman: {datetime.now().strftime('%H:%M')}")
            except:
                pass
    
    def evening_summary_job(self):
        """
        🌅 AKŞAM ÖZET RAPORU (18:00)
        Günün sonunda başarı oranını kontrol et
        """
        try:
            print(f"\n📊 AKŞAM DEĞERLENDİRME: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Bugünün tarama sonuçlarını oku (en son rapor)
            import glob
            import json
            
            today = datetime.now().strftime("%Y%m%d")
            report_files = glob.glob(f"ceiling_scan_report_{today}_*.json")
            
            if report_files:
                latest_report = max(report_files)
                
                with open(latest_report, 'r', encoding='utf-8') as f:
                    report_data = json.load(f)
                
                candidates = report_data['results']
                high_risk = [r for r in candidates if r['risk_level'] == 'YÜKSEK']
                
                summary_message = f"📊 GÜNLÜK ÖZET RAPORU\n\n"
                summary_message += f"🎯 Sabah tahmin sayısı: {len(candidates)}\n"
                summary_message += f"🚨 Yüksek risk adayları: {len(high_risk)}\n"
                
                if high_risk:
                    summary_message += f"\n🏆 YÜKSEk RİSK ADAYLARI:\n"
                    for candidate in high_risk[:3]:
                        summary_message += f"• {candidate['symbol']}: %{candidate['hybrid_score']:.0f}\n"
                
                summary_message += f"\n📅 Tarih: {datetime.now().strftime('%d.%m.%Y')}"
                summary_message += f"\n⏰ Özet saati: {datetime.now().strftime('%H:%M')}"
                
                print(summary_message)
                
                # Akşam özetini Telegram'a da gönder
                self.scanner.send_telegram_alert(summary_message)
                
            else:
                print("❌ Bugünlük rapor bulunamadı")
                
        except Exception as e:
            print(f"❌ AKŞAM ÖZET HATASI: {e}")
    
    def setup_schedule(self):
        """
        ⏰ ZAMANLAMA KURULUMU
        """
        # Sabah taraması: Her gün 08:30
        schedule.every().day.at("08:30").do(self.morning_scan_job)
        
        # Akşam özeti: Her gün 18:00
        schedule.every().day.at("18:00").do(self.evening_summary_job)
        
        # Test için: Her dakika çalışma (geliştirme amaçlı)
        # schedule.every(1).minutes.do(self.morning_scan_job)
        
        print("⏰ ZAMANLAMA KURULDU:")
        print("🌅 Sabah tarama: Her gün 08:30")
        print("🌆 Akşam özet: Her gün 18:00")
        print("=" * 50)
    
    def run_continuous(self):
        """
        🔄 SÜREKLİ ÇALIŞMA MODU
        Sistem sürekli çalışır ve zamanlanmış görevleri bekler
        """
        print("🚀 GÜNLÜK TAVAN TARAMA OTOMASYONU BAŞLATILDI")
        print("=" * 60)
        print("💡 Sistem sürekli çalışacak ve zamanlanmış görevleri bekleyecek...")
        print("🛑 Durdurmak için CTRL+C")
        print("=" * 60)
        
        self.setup_schedule()
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Her dakika kontrol et
                
        except KeyboardInterrupt:
            print("\n🛑 OTOMASYON DURDURULDU")
            print("👋 Görüşürüz!")
    
    def run_once_now(self):
        """
        ⚡ TEK SEFERLIK ŞİMDİ ÇALIŞTIR
        Test amaçlı hemen tarama yapar
        """
        print("⚡ TEK SEFERLIK TARAMA ÇALIŞTIRILIYOR...")
        self.morning_scan_job()

# Ana çalıştırma
if __name__ == "__main__":
    automation = DailyCeilingAutomation()
    
    # Komut satırı argümanlarını kontrol et
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "now":
        # Hemen çalıştır
        automation.run_once_now()
    else:
        # Sürekli otomasyon modunda çalış
        automation.run_continuous()