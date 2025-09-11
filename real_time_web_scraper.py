#!/usr/bin/env python3
"""
Web Scraping ile Gerçek Zamanlı BİST Veri Çekme
investing.com ve bigpara.com'dan gerçek zamanlı hisse fiyatları çeker.
"""

import requests
import time
import logging
import json
import re
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Any, Optional
import concurrent.futures
from urllib.parse import quote

logger = logging.getLogger(__name__)

class RealTimeWebScraper:
    def __init__(self):
        """Web scraping ile gerçek zamanlı veri çekici"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'tr-TR,tr;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 1  # 1 saniye minimum
        
        logger.info("🌐 Web Scraping Real-Time Fetcher başlatıldı")
    
    def _rate_limit(self):
        """Request rate limiting"""
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        if elapsed < self.min_request_interval:
            sleep_time = self.min_request_interval - elapsed
            time.sleep(sleep_time)
        self.last_request_time = time.time()
    
    def get_investing_com_data(self, symbol: str) -> Optional[Dict]:
        """
        investing.com'dan hisse verisi çek
        """
        self._rate_limit()
        
        try:
            # investing.com BİST URL formatı
            url = f"https://tr.investing.com/equities/{symbol.lower()}"
            
            logger.debug(f"Investing.com request: {url}")
            response = self.session.get(url, timeout=10)
            
            if response.status_code != 200:
                logger.warning(f"Investing.com {symbol}: HTTP {response.status_code}")
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Fiyat bilgilerini bul
            price_element = soup.find('span', class_=re.compile(r'text-5xl|text-2xl'))
            if not price_element:
                price_element = soup.find('span', {'data-test': 'instrument-price-last'})
            
            if not price_element:
                logger.warning(f"Fiyat bulunamadı: {symbol}")
                return None
            
            price_text = price_element.get_text(strip=True)
            current_price = float(re.sub(r'[^0-9,.]', '', price_text).replace(',', '.'))
            
            # Değişim bilgisi
            change_element = soup.find('span', class_=re.compile(r'change'))
            change_percent = 0
            
            if change_element:
                change_text = change_element.get_text(strip=True)
                change_match = re.search(r'([+-]?\d+[,.]?\d*)', change_text)
                if change_match:
                    change_percent = float(change_match.group(1).replace(',', '.'))
            
            result = {
                'symbol': symbol,
                'current_price': current_price,
                'change_percent': change_percent,
                'timestamp': datetime.now().strftime('%H:%M:%S'),
                'source': 'investing.com'
            }
            
            logger.debug(f"{symbol} investing.com: {current_price} TL (%{change_percent:+.2f})")
            return result
            
        except Exception as e:
            logger.error(f"Investing.com hatası ({symbol}): {e}")
            return None
    
    def get_bigpara_data(self, symbol: str) -> Optional[Dict]:
        """
        bigpara.com'dan hisse verisi çek
        """
        self._rate_limit()
        
        try:
            # BigPara URL formatı
            url = f"https://bigpara.hurriyet.com.tr/borsa/hisseler/{symbol.lower()}/"
            
            logger.debug(f"BigPara request: {url}")
            response = self.session.get(url, timeout=10)
            
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Fiyat elementi
            price_element = soup.find('div', class_='price')
            if not price_element:
                price_element = soup.find('span', class_='last-price')
            
            if not price_element:
                return None
            
            price_text = price_element.get_text(strip=True)
            current_price = float(re.sub(r'[^0-9,.]', '', price_text).replace(',', '.'))
            
            # Değişim oranı
            change_element = soup.find('div', class_='change') or soup.find('span', class_='change-percent')
            change_percent = 0
            
            if change_element:
                change_text = change_element.get_text(strip=True)
                percent_match = re.search(r'([+-]?\d+[,.]?\d*)%?', change_text)
                if percent_match:
                    change_percent = float(percent_match.group(1).replace(',', '.'))
            
            result = {
                'symbol': symbol,
                'current_price': current_price,
                'change_percent': change_percent,
                'timestamp': datetime.now().strftime('%H:%M:%S'),
                'source': 'bigpara.com'
            }
            
            return result
            
        except Exception as e:
            logger.error(f"BigPara hatası ({symbol}): {e}")
            return None
    
    def get_stock_data_multi_source(self, symbol: str) -> Optional[Dict]:
        """
        Birden fazla kaynaktan veri çek ve en güvenilir olanı döndür
        """
        sources = [
            self.get_investing_com_data,
            self.get_bigpara_data
        ]
        
        results = []
        
        for source_func in sources:
            try:
                data = source_func(symbol)
                if data and data['current_price'] > 0:
                    results.append(data)
            except Exception as e:
                logger.debug(f"Kaynak hatası ({symbol}): {e}")
                continue
        
        if not results:
            logger.warning(f"Hiçbir kaynaktan veri alınamadı: {symbol}")
            return None
        
        # En güncel/güvenilir veriyi seç (investing.com öncelikli)
        for result in results:
            if result['source'] == 'investing.com':
                return result
        
        # Yoksa ilk bulunanı döndür
        return results[0]
    
    def get_real_time_ceiling_stocks(self, symbols: List[str], threshold: float = 9.0) -> List[Dict]:
        """
        Gerçek zamanlı web scraping ile tavan yapan hisseleri bul
        """
        logger.info(f"🌐 Web scraping tavan tarama başlatılıyor - {len(symbols)} hisse")
        
        ceiling_stocks = []
        
        # Concurrent requests for faster processing
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            # Submit all requests
            future_to_symbol = {
                executor.submit(self.get_stock_data_multi_source, symbol): symbol 
                for symbol in symbols
            }
            
            # Collect results
            for future in concurrent.futures.as_completed(future_to_symbol):
                symbol = future_to_symbol[future]
                try:
                    data = future.result(timeout=30)
                    
                    if data and data['change_percent'] >= threshold:
                        ceiling_info = {
                            'symbol': symbol,
                            'current_price': data['current_price'],
                            'change_percent': data['change_percent'],
                            'timestamp': data['timestamp'],
                            'source': data['source'],
                            'last_updated': datetime.now().strftime('%H:%M:%S')
                        }
                        ceiling_stocks.append(ceiling_info)
                        logger.info(f"🚀 WEB SCRAPING TAVAN: {symbol} %{data['change_percent']:.2f}")
                
                except Exception as e:
                    logger.error(f"Future error ({symbol}): {e}")
                    continue
        
        # Değişim oranına göre sırala
        ceiling_stocks.sort(key=lambda x: x['change_percent'], reverse=True)
        
        logger.info(f"🎯 Web scraping tamamlandı: {len(ceiling_stocks)} tavan bulundu")
        return ceiling_stocks
    
    def get_market_pulse(self, symbols: List[str]) -> Dict[str, Any]:
        """
        Pazar nabzı - hızlı genel bakış
        """
        logger.info("💓 Pazar nabzı alınıyor...")
        
        pulse = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'sample_stocks': [],
            'quick_stats': {
                'processed': 0,
                'positive': 0,
                'negative': 0,
                'neutral': 0,
                'avg_change': 0
            }
        }
        
        sample_size = min(10, len(symbols))  # İlk 10 hisse hızlı test
        total_change = 0
        
        for symbol in symbols[:sample_size]:
            try:
                data = self.get_stock_data_multi_source(symbol)
                if data:
                    change = data['change_percent']
                    
                    pulse['sample_stocks'].append({
                        'symbol': symbol,
                        'price': data['current_price'],
                        'change': change,
                        'source': data['source']
                    })
                    
                    pulse['quick_stats']['processed'] += 1
                    total_change += change
                    
                    if change > 1:
                        pulse['quick_stats']['positive'] += 1
                    elif change < -1:
                        pulse['quick_stats']['negative'] += 1
                    else:
                        pulse['quick_stats']['neutral'] += 1
                
            except Exception as e:
                logger.debug(f"Pulse error ({symbol}): {e}")
                continue
        
        # Ortalama hesapla
        if pulse['quick_stats']['processed'] > 0:
            pulse['quick_stats']['avg_change'] = total_change / pulse['quick_stats']['processed']
        
        return pulse

# Test fonksiyonu
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    try:
        scraper = RealTimeWebScraper()
        
        print("🌐 Web Scraping gerçek zamanlı test başlatılıyor...")
        
        # Test sembolleri
        test_symbols = ['THYAO', 'AKBNK', 'GARAN', 'SISE']
        
        # Test 1: Tek hisse
        print("\n📊 Test 1: THYAO hissesi")
        thyao_data = scraper.get_stock_data_multi_source('THYAO')
        if thyao_data:
            print(f"✅ THYAO: {thyao_data['current_price']} TL (%{thyao_data['change_percent']:+.2f})")
            print(f"   Kaynak: {thyao_data['source']} | Zaman: {thyao_data['timestamp']}")
        else:
            print("❌ THYAO verisi alınamadı")
        
        # Test 2: Pazar nabzı
        print("\n💓 Test 2: Pazar nabzı")
        pulse = scraper.get_market_pulse(test_symbols)
        stats = pulse['quick_stats']
        print(f"✅ İşlenen: {stats['processed']}")
        print(f"   📈 Pozitif: {stats['positive']}")
        print(f"   📉 Negatif: {stats['negative']}")
        print(f"   📊 Ortalama: %{stats['avg_change']:.2f}")
        
        # Test 3: Tavan tarama (düşük eşik)
        print(f"\n🚀 Test 3: Tavan tarama ({len(test_symbols)} hisse)")
        ceiling_stocks = scraper.get_real_time_ceiling_stocks(test_symbols, threshold=3.0)
        
        if ceiling_stocks:
            print(f"✅ {len(ceiling_stocks)} yüksek artış bulundu:")
            for stock in ceiling_stocks:
                print(f"   🎯 {stock['symbol']}: %{stock['change_percent']:+.2f} ({stock['source']})")
        else:
            print("ℹ️ Yüksek artış bulunamadı")
        
        print(f"\n✅ Web scraping test tamamlandı!")
        
    except Exception as e:
        print(f"❌ Test hatası: {e}")