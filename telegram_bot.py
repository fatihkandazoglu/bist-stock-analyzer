#!/usr/bin/env python3
"""
Telegram Bot Modülü
Bu modül analiz sonuçlarını Telegram üzerinden gönderir.
"""

import asyncio
import os
try:
    from telegram import Bot
    from telegram.error import TelegramError
    print("✅ Telegram library başarıyla yüklendi!")
except ImportError as e:
    # Fallback for import issues
    print(f"⚠️ Telegram import problemi: {e}")
    Bot = None
    TelegramError = Exception
import logging
from typing import List, Dict, Any
from datetime import datetime
# import emoji  # Şimdilik emoji kullanmayacağız

logger = logging.getLogger(__name__)

class TelegramNotifier:
    def __init__(self):
        """Telegram bildirim sınıfını başlat"""
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.bot = None
        
        if self.bot_token and self.chat_id and Bot is not None:
            self.bot = Bot(token=self.bot_token)
            logger.info("Telegram bot başlatıldı")
        else:
            logger.warning("Telegram bot token veya chat ID bulunamadı - Test modunda çalışıyor")
    
    async def send_daily_analysis(self, predictions: List[Dict[str, Any]], 
                                market_info: Dict[str, Any] = None,
                                sentiment_info: Dict[str, Any] = None,
                                todays_ceiling_stocks: List[Dict[str, Any]] = None) -> bool:
        """Günlük analiz raporunu gönder"""
        if not self.bot:
            logger.warning("Telegram bot test modunda - konsol çıktısı")
        
        # Telegram yoksa sadece konsola yazdır
        if self.bot is None:
            logger.warning("Telegram bot mevcut değil - sadece konsol çıktısı")
            message = self._format_daily_message(predictions, market_info, sentiment_info, todays_ceiling_stocks)
            print("=" * 60)
            print("📱 TELEGRAM MESAJI (Test modu):")
            print("=" * 60)
            print(message)
            print("=" * 60)
            return True
            
        try:
            message = self._format_daily_message(predictions, market_info, sentiment_info, todays_ceiling_stocks)
            
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='HTML'
            )
            
            logger.info("Günlük analiz raporu Telegram'a gönderildi")
            return True
            
        except TelegramError as e:
            logger.error(f"Telegram mesaj gönderme hatası: {e}")
            return False
        except Exception as e:
            logger.error(f"Beklenmeyen hata: {e}")
            return False
    
    def _format_daily_message(self, predictions: List[Dict[str, Any]], 
                            market_info: Dict[str, Any] = None,
                            sentiment_info: Dict[str, Any] = None,
                            todays_ceiling_stocks: List[Dict[str, Any]] = None) -> str:
        """Günlük mesajı formatla"""
        
        # Mesaj başlığı
        today = datetime.now().strftime("%d.%m.%Y")
        message = f"📊 <b>BİST Tavan Tahminleri - {today}</b>\\n\\n"
        
        # Piyasa durumu
        if market_info:
            xu100_value = market_info.get('xu100_value', 'N/A')
            xu100_change = market_info.get('xu100_change', 0)
            change_emoji = "📈" if xu100_change > 0 else "📉" if xu100_change < 0 else "➡️"
            
            message += f"🏛️ <b>XU100:</b> {xu100_value:.2f} {change_emoji} %{xu100_change:.2f}\\n"
        
        # Piyasa sentimenti
        if sentiment_info:
            sentiment = sentiment_info.get('sentiment', 'neutral')
            sentiment_emoji = self._get_sentiment_emoji(sentiment)
            message += f"💭 <b>Piyasa Sentimenti:</b> {sentiment_emoji} {sentiment.title()}\\n"
        
        message += "\\n" + "="*30 + "\\n\\n"
        
        # Bugün tavan yapan hisseler
        if todays_ceiling_stocks:
            message += f"🚀 <b>BUGÜN TAVAN YAPAN HİSSELER ({len(todays_ceiling_stocks)} adet):</b>\\n\\n"
            
            for i, stock in enumerate(todays_ceiling_stocks[:10], 1):
                symbol = stock.get('symbol', 'N/A')
                change = stock.get('price_change', 0)
                price = stock.get('close_price', 0)
                high_change = stock.get('daily_high_change', 0)
                
                message += f"{i}. <b>{symbol}</b> 🔥\\n"
                message += f"   📈 Artış: %{change:.2f}\\n"
                message += f"   💰 Kapanış: {price:.2f} TL\\n"
                message += f"   🎯 En Yüksek: %{high_change:.2f}\\n\\n"
                
            message += "\\n" + "="*30 + "\\n\\n"
        
        # Yarın için tavan tahminleri
        if predictions:
            message += f"🎯 <b>YARIN POTANSİYEL TAVAN HİSSELERİ ({len(predictions)} adet):</b>\\n\\n"
            
            for i, stock in enumerate(predictions[:10], 1):  # En fazla 10 hisse göster
                symbol = stock.get('symbol', 'N/A')
                score = stock.get('technical_score', 0)
                rsi = stock.get('rsi', 'N/A')
                price = stock.get('last_price', 'N/A')
                
                # Skor bazlı emoji
                score_emoji = self._get_score_emoji(score)
                
                message += f"{i}. <b>{symbol}</b> {score_emoji}\\n"
                message += f"   💰 Fiyat: {price:.2f} TL\\n"
                message += f"   📊 Teknik Skor: {score:.1f}/100\\n"
                if rsi != 'N/A':
                    message += f"   📈 RSI: {rsi:.1f}\\n"
                message += "\\n"
        else:
            message += "❌ <b>Yarın için potansiyel tavan hissesi bulunamadı.</b>\\n\\n"
            
        if not todays_ceiling_stocks:
            message += "📝 <b>Not:</b> Bugün tavan yapan hisse bulunamadı.\\n\\n"
        
        # Uyarı ve bilgilendirme
        message += "\\n" + "="*30 + "\\n"
        message += "⚠️ <b>UYARI:</b>\\n"
        message += "• Bu tahminler sadece teknik analiz ve haberler üzerine kuruludur\\n"
        message += "• Yatırım tavsiyesi değildir\\n"
        message += "• Risk yönetimini unutmayın\\n"
        message += "• Kendi araştırmanızı yapın\\n\\n"
        
        message += f"🤖 <i>Otomatik analiz - {datetime.now().strftime('%H:%M')} itibariyle</i>"
        
        return message
    
    def _get_sentiment_emoji(self, sentiment: str) -> str:
        """Sentiment için emoji döndür"""
        sentiment_emojis = {
            'very_positive': '🚀',
            'positive': '😊',
            'neutral': '😐',
            'negative': '😟',
            'very_negative': '😱'
        }
        return sentiment_emojis.get(sentiment, '😐')
    
    def _get_score_emoji(self, score: float) -> str:
        """Skor için emoji döndür"""
        if score >= 80:
            return '🔥'
        elif score >= 70:
            return '⭐'
        elif score >= 60:
            return '👍'
        elif score >= 40:
            return '👌'
        else:
            return '🤔'
    
    async def send_test_message(self) -> bool:
        """Test mesajı gönder"""
        if not self.bot:
            return False
        
        try:
            test_message = "🧪 <b>BİST Analiz Sistemi Test</b>\\n\\nSistem çalışıyor! ✅"
            
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=test_message,
                parse_mode='HTML'
            )
            
            logger.info("Test mesajı gönderildi")
            return True
            
        except Exception as e:
            logger.error(f"Test mesajı gönderme hatası: {e}")
            return False
    
    async def send_error_notification(self, error_message: str) -> bool:
        """Hata bildirimi gönder"""
        if not self.bot:
            return False
        
        try:
            message = f"❌ <b>BİST Analiz Sistemi Hatası</b>\\n\\n{error_message}"
            
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='HTML'
            )
            
            logger.info("Hata bildirimi gönderildi")
            return True
            
        except Exception as e:
            logger.error(f"Hata bildirimi gönderme hatası: {e}")
            return False

# Test fonksiyonu
async def test_telegram_bot():
    """Telegram bot test fonksiyonu"""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    notifier = TelegramNotifier()
    
    if notifier.bot:
        # Test mesajı gönder
        success = await notifier.send_test_message()
        print(f"Test mesajı gönderildi: {success}")
        
        # Örnek analiz raporu gönder
        sample_predictions = [
            {
                'symbol': 'AKBNK',
                'technical_score': 75.5,
                'rsi': 45.2,
                'last_price': 15.67
            },
            {
                'symbol': 'GARAN',
                'technical_score': 68.3,
                'rsi': 52.1,
                'last_price': 23.45
            }
        ]
        
        sample_market_info = {
            'xu100_value': 8756.43,
            'xu100_change': 1.25
        }
        
        sample_sentiment = {
            'sentiment': 'positive'
        }
        
        success = await notifier.send_daily_analysis(
            sample_predictions, 
            sample_market_info, 
            sample_sentiment
        )
        print(f"Örnek rapor gönderildi: {success}")
    else:
        print("Telegram bot yapılandırması bulunamadı")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_telegram_bot())