#!/usr/bin/env python3
"""
BİST Hisse Senedi Analiz ve Tahmin Sistemi
Bu sistem günlük olarak BİST hisselerini analiz eder ve potansiyel tavan yapabilecek
hisseleri Telegram üzerinden bildirir.
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any
import os
from dotenv import load_dotenv

# Kendi modüllerimizi import et
from bist_data_fetcher import BISTDataFetcher
from technical_analyzer import TechnicalAnalyzer
from news_analyzer import NewsAnalyzer
from telegram_bot import TelegramNotifier
from prediction_model import StockPredictionModel

# Çevre değişkenlerini yükle
load_dotenv()

# Logging ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bist_analyzer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BISTAnalyzer:
    def __init__(self):
        """BİST analiz sistemini başlat"""
        logger.info("BİST Analiz Sistemi başlatılıyor...")
        
        # Modülleri başlat
        self.data_fetcher = BISTDataFetcher()
        self.technical_analyzer = TechnicalAnalyzer()
        self.news_analyzer = NewsAnalyzer()
        self.telegram_notifier = TelegramNotifier()
        self.prediction_model = StockPredictionModel()
        
        logger.info("Tüm modüller başlatıldı")
        
    async def run_daily_analysis(self):
        """Günlük analizi çalıştır"""
        try:
            logger.info("Günlük analiz başlatılıyor...")
            
            # 1. Bugün tavan yapan hisseleri bul
            todays_ceiling_stocks = self.get_todays_ceiling_stocks()
            
            # 2. Önceki gün tavan yapan hisseleri analiz et
            previous_day_data = self.get_previous_day_ceiling_stocks()
            
            # 3. Tüm hisseler için teknik analiz yap
            technical_analysis = await self.perform_technical_analysis()
            
            # 4. Piyasa haberlerini analiz et
            news_analysis = self.analyze_market_news()
            
            # 5. Piyasa bilgilerini al
            market_info = self.data_fetcher.get_market_info()
            
            # 6. Potansiyel tavan hisselerini tahmin et
            predictions = self.predict_potential_ceiling_stocks(
                technical_analysis, news_analysis, market_info
            )
            
            # 7. Telegram'a gönder (bugün tavan yapanlar + yarın potansiyeli olanlar)
            await self.send_telegram_message(predictions, market_info, news_analysis, todays_ceiling_stocks)
            
            logger.info("Günlük analiz tamamlandı")
            
        except Exception as e:
            logger.error(f"Analiz sırasında hata: {e}")
            # Hata durumunda Telegram'a bildir
            try:
                await self.telegram_notifier.send_error_notification(str(e))
            except:
                pass
    
    def get_todays_ceiling_stocks(self) -> List[Dict]:
        """Bugün tavan yapan hisseleri getir"""
        logger.info("Bugün tavan yapan hisseler analiz ediliyor...")
        try:
            ceiling_stocks = self.data_fetcher.get_todays_ceiling_stocks()
            logger.info(f"{len(ceiling_stocks)} bugün tavan yapan hisse bulundu")
            return ceiling_stocks
        except Exception as e:
            logger.error(f"Bugün tavan hisse analizi hatası: {e}")
            return []
    
    def get_previous_day_ceiling_stocks(self) -> List[Dict]:
        """Önceki gün tavan yapan hisseleri getir"""
        logger.info("Önceki gün tavan yapan hisseler analiz ediliyor...")
        try:
            ceiling_stocks = self.data_fetcher.get_previous_day_ceiling_stocks()
            logger.info(f"{len(ceiling_stocks)} tavan yapan hisse bulundu")
            return ceiling_stocks
        except Exception as e:
            logger.error(f"Tavan hisse analizi hatası: {e}")
            return []
    
    async def perform_technical_analysis(self) -> List[Dict]:
        """Teknik analiz yap"""
        logger.info("Teknik analiz yapılıyor...")
        try:
            # Tüm BİST hisselerinin verilerini çek
            all_data = self.data_fetcher.get_all_bist_data(period="1mo")
            
            technical_results = []
            
            for symbol, data in all_data.items():
                try:
                    analysis = self.technical_analyzer.analyze_stock(symbol, data)
                    if analysis:
                        technical_results.append(analysis)
                        
                except Exception as e:
                    logger.debug(f"{symbol} teknik analiz hatası: {e}")
                    continue
            
            logger.info(f"{len(technical_results)} hisse için teknik analiz tamamlandı")
            return technical_results
            
        except Exception as e:
            logger.error(f"Teknik analiz hatası: {e}")
            return []
    
    def analyze_market_news(self) -> Dict:
        """Piyasa haberlerini analiz et"""
        logger.info("Piyasa haberleri analiz ediliyor...")
        try:
            # Güncel haberleri çek
            news = self.news_analyzer.fetch_financial_news(days_back=1)
            
            # Sentiment analizi
            sentiment_analysis = self.news_analyzer.analyze_news_sentiment(news)
            
            # Hisse bahislerini bul
            stock_mentions = self.news_analyzer.find_stock_mentions(news)
            
            return {
                'sentiment': sentiment_analysis,
                'stock_mentions': stock_mentions,
                'news_count': len(news)
            }
            
        except Exception as e:
            logger.error(f"Haber analizi hatası: {e}")
            return {'sentiment': {'sentiment': 'neutral', 'score': 0.5}, 'stock_mentions': {}}
    
    def predict_potential_ceiling_stocks(self, technical_analysis: List[Dict], 
                                       news_analysis: Dict, market_info: Dict) -> List[Dict]:
        """Potansiyel tavan yapabilecek hisseleri tahmin et"""
        logger.info("Tavan tahminleri yapılıyor...")
        try:
            sentiment_score = news_analysis.get('sentiment', {}).get('score', 0.5)
            
            # Hisseleri tahmin modeli ile değerlendir
            ranked_stocks = self.prediction_model.rank_stocks_by_potential(
                technical_analysis, market_info, sentiment_score
            )
            
            # En yüksek potansiyeli olanları seç (skor > 70) - daha katı filtre
            potential_stocks = [
                stock for stock in ranked_stocks 
                if stock.get('prediction_score', 0) > 70
            ]
            
            logger.info(f"{len(potential_stocks)} potansiyel tavan hissesi bulundu")
            return potential_stocks[:10]  # En fazla 10 hisse
            
        except Exception as e:
            logger.error(f"Tahmin hatası: {e}")
            return []
    
    async def send_telegram_message(self, predictions: List[Dict], 
                                   market_info: Dict, news_analysis: Dict,
                                   todays_ceiling_stocks: List[Dict] = None):
        """Telegram'a mesaj gönder"""
        logger.info("Telegram mesajı gönderiliyor...")
        try:
            sentiment_info = news_analysis.get('sentiment', {})
            
            success = await self.telegram_notifier.send_daily_analysis(
                predictions, market_info, sentiment_info, todays_ceiling_stocks
            )
            
            if success:
                logger.info("Telegram mesajı başarıyla gönderildi")
            else:
                logger.error("Telegram mesajı gönderilemedi")
                
        except Exception as e:
            logger.error(f"Telegram mesaj hatası: {e}")

    async def run_test_analysis(self):
        """Test analizi çalıştır"""
        logger.info("Test analizi başlatılıyor...")
        
        try:
            # Telegram test mesajı
            await self.telegram_notifier.send_test_message()
            
            # Mini analiz
            await self.run_daily_analysis()
            
        except Exception as e:
            logger.error(f"Test analizi hatası: {e}")

async def scheduled_analysis():
    """Zamanlanmış analiz fonksiyonu"""
    analyzer = BISTAnalyzer()
    await analyzer.run_daily_analysis()

async def main():
    """Ana fonksiyon"""
    analyzer = BISTAnalyzer()
    
    # Test çalıştırması
    logger.info("Test analizi başlatılıyor...")
    await analyzer.run_test_analysis()
    
    logger.info("Sistem başlatıldı. Manuel test tamamlandı.")
    
    # Burada gerçek zamanlı çalışma için cron job veya scheduler eklenir
    # Şu an sadece test çalıştırıyoruz

if __name__ == "__main__":
    asyncio.run(main())