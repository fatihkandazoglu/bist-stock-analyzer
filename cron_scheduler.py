#!/usr/bin/env python3
"""
Cron Zamanlayıcı - Her gün sabah 9:00'da analizi çalıştırır
"""

import asyncio
import schedule
import time
import logging
from main import scheduled_analysis

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_analysis():
    """Analizi async olarak çalıştır"""
    try:
        asyncio.run(scheduled_analysis())
    except Exception as e:
        logger.error(f"Zamanlanmış analiz hatası: {e}")

def main():
    """Ana zamanlayıcı fonksiyonu"""
    logger.info("BİST Analiz Zamanlayıcı başlatıldı")
    
    # Her gün sabah 9:00'da çalış
    schedule.every().day.at("09:00").do(run_analysis)
    
    # Test için şimdi de çalıştır
    logger.info("Test analizi çalıştırılıyor...")
    run_analysis()
    
    logger.info("Zamanlayıcı çalışıyor. Her gün 09:00'da analiz yapılacak.")
    
    # Sürekli çalışma döngüsü
    while True:
        schedule.run_pending()
        time.sleep(60)  # Her dakika kontrol et

if __name__ == "__main__":
    main()