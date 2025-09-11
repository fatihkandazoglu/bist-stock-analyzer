#!/usr/bin/env python3
"""
Alpha Vantage Gerçek Zamanlı BİST Veri Çekme Modülü
Gerçek zamanlı (1-15 dakika gecikmeli) BİST hisse senedi verilerini Alpha Vantage API'dan çeker.
"""

import requests
import pandas as pd
import time
import logging
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
import json

logger = logging.getLogger(__name__)

class AlphaVantageRealTimeFetcher:
    def __init__(self):
        """Alpha Vantage gerçek zamanlı veri çekici başlat"""
        self.api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
        self.base_url = "https://www.alphavantage.co/query"
        self.call_count = 0
        self.max_calls_per_minute = 5  # Free tier limit
        self.last_call_time = 0
        
        if not self.api_key:
            logger.error("Alpha Vantage API key bulunamadı!")
            raise ValueError("ALPHA_VANTAGE_API_KEY environment variable gerekli")
        
        logger.info("Alpha Vantage Real-Time Fetcher başlatıldı")
    
    def _rate_limit_check(self):
        """API rate limit kontrolü"""
        current_time = time.time()
        if current_time - self.last_call_time < 12:  # 12 saniye bekle (5 calls/min için)
            wait_time = 12 - (current_time - self.last_call_time)
            logger.info(f"Rate limit - {wait_time:.1f} saniye bekleniyor...")
            time.sleep(wait_time)
        
        self.last_call_time = time.time()
        self.call_count += 1
    
    def get_intraday_data(self, bist_symbol: str, interval: str = "1min") -> Optional[Dict]:
        """
        Gerçek zamanlı intraday data çek
        
        Args:
            bist_symbol: BİST hisse kodu (örn: "THYAO")  
            interval: Zaman aralığı ("1min", "5min", "15min", "30min", "60min")
        """
        self._rate_limit_check()
        
        # BİST formatına çevir
        symbol = f"{bist_symbol}.IST"  # Alpha Vantage için IST suffix
        
        params = {
            'function': 'TIME_SERIES_INTRADAY',
            'symbol': symbol,
            'interval': interval,
            'apikey': self.api_key,
            'outputsize': 'compact'  # Son 100 data point
        }
        
        try:
            logger.debug(f"Alpha Vantage API çağrısı: {symbol} ({interval})")
            response = requests.get(self.base_url, params=params, timeout=30)
            
            if response.status_code != 200:
                logger.error(f"API çağrısı başarısız: {response.status_code}")
                return None
            
            data = response.json()
            
            # Hata kontrolü
            if 'Error Message' in data:
                logger.error(f"API Hatası: {data['Error Message']}")
                return None
                
            if 'Note' in data:
                logger.warning(f"API Uyarısı: {data['Note']}")
                return None
            
            # Time series verisini çek
            time_series_key = f"Time Series ({interval})"
            if time_series_key not in data:
                logger.error(f"Veri formatı hatası - beklenen key bulunamadı: {time_series_key}")
                return None
            
            time_series = data[time_series_key]
            
            # En son fiyat bilgisi
            latest_time = max(time_series.keys())
            latest_data = time_series[latest_time]
            
            result = {
                'symbol': bist_symbol,
                'timestamp': latest_time,
                'open': float(latest_data['1. open']),
                'high': float(latest_data['2. high']),
                'low': float(latest_data['3. low']),
                'close': float(latest_data['4. close']),
                'volume': int(latest_data['5. volume']),
                'last_refreshed': data.get('Meta Data', {}).get('3. Last Refreshed', ''),
                'time_zone': data.get('Meta Data', {}).get('6. Time Zone', ''),
                'interval': interval,
                'data_count': len(time_series)
            }
            
            logger.debug(f"{bist_symbol} başarılı - Son fiyat: {result['close']}")
            return result
            
        except requests.exceptions.Timeout:
            logger.error(f"Timeout hatası: {symbol}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"İstek hatası: {e}")
            return None
        except (ValueError, KeyError) as e:
            logger.error(f"Veri parsing hatası: {e}")
            return None
    
    def get_quote_endpoint(self, bist_symbol: str) -> Optional[Dict]:
        """
        Global Quote endpoint - daha hızlı güncel fiyat
        """
        self._rate_limit_check()
        
        symbol = f"{bist_symbol}.IST"
        
        params = {
            'function': 'GLOBAL_QUOTE',
            'symbol': symbol,
            'apikey': self.api_key
        }
        
        try:
            logger.debug(f"Global Quote API: {symbol}")
            response = requests.get(self.base_url, params=params, timeout=20)
            
            if response.status_code != 200:
                return None
                
            data = response.json()
            
            if 'Global Quote' not in data:
                logger.warning(f"Global Quote verisi bulunamadı: {bist_symbol}")
                return None
                
            quote = data['Global Quote']
            
            if not quote:
                return None
                
            result = {
                'symbol': bist_symbol,
                'open': float(quote.get('02. open', 0)),
                'high': float(quote.get('03. high', 0)),
                'low': float(quote.get('04. low', 0)),
                'price': float(quote.get('05. price', 0)),
                'volume': int(quote.get('06. volume', 0)),
                'latest_trading_day': quote.get('07. latest trading day', ''),
                'previous_close': float(quote.get('08. previous close', 0)),
                'change': float(quote.get('09. change', 0)),
                'change_percent': quote.get('10. change percent', '0%').replace('%', ''),
                'last_refreshed': data.get('Global Quote', {}).get('07. latest trading day', '')
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Global Quote hatası ({bist_symbol}): {e}")
            return None
    
    def get_real_time_ceiling_stocks(self, symbols: List[str], threshold: float = 9.0) -> List[Dict]:
        """
        Gerçek zamanlı tavan yapan hisseleri bul
        
        Args:
            symbols: BİST hisse kodları listesi
            threshold: Tavan eşiği (%9.0 = %9+)
        """
        logger.info(f"Gerçek zamanlı tavan tarama başlatılıyor - {len(symbols)} hisse")
        
        ceiling_stocks = []
        processed = 0
        
        for symbol in symbols:
            try:
                # Önce Global Quote dene (daha hızlı)
                data = self.get_quote_endpoint(symbol)
                
                if not data:
                    # Global Quote çalışmazsa intraday dene
                    intraday_data = self.get_intraday_data(symbol, "5min")
                    if intraday_data:
                        data = {
                            'symbol': symbol,
                            'price': intraday_data['close'],
                            'previous_close': 0,  # Hesaplanması gerekecek
                            'change_percent': '0',
                            'volume': intraday_data['volume'],
                            'high': intraday_data['high'],
                            'low': intraday_data['low']
                        }
                    else:
                        continue
                
                # Değişim yüzdesini hesapla
                try:
                    change_percent = float(data['change_percent'].replace('%', ''))
                except (ValueError, AttributeError):
                    change_percent = 0
                    if data['previous_close'] > 0:
                        change_percent = ((data['price'] - data['previous_close']) / data['previous_close']) * 100
                
                # Tavan kontrolü
                if change_percent >= threshold:
                    ceiling_info = {
                        'symbol': symbol,
                        'current_price': data['price'],
                        'change_percent': change_percent,
                        'volume': data.get('volume', 0),
                        'high': data.get('high', 0),
                        'low': data.get('low', 0),
                        'last_updated': datetime.now().strftime('%H:%M:%S'),
                        'source': 'Alpha Vantage'
                    }
                    ceiling_stocks.append(ceiling_info)
                    logger.info(f"🚀 TAVAN BULUNDU: {symbol} %{change_percent:.2f}")
                
                processed += 1
                if processed % 10 == 0:
                    logger.info(f"İşlenen: {processed}/{len(symbols)}")
                
                # Rate limit için kısa bekleme
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"{symbol} işleme hatası: {e}")
                continue
        
        # Değişim oranına göre sırala
        ceiling_stocks.sort(key=lambda x: x['change_percent'], reverse=True)
        
        logger.info(f"🎯 Gerçek zamanlı tarama tamamlandı: {len(ceiling_stocks)} tavan bulundu")
        return ceiling_stocks
    
    def get_live_market_snapshot(self, top_symbols: List[str]) -> Dict[str, Any]:
        """
        Canlı pazar anlık görüntüsü
        """
        logger.info("Canlı pazar görüntüsü alınıyor...")
        
        snapshot = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'stocks': [],
            'summary': {
                'total_processed': 0,
                'positive_count': 0,
                'negative_count': 0,
                'ceiling_count': 0
            }
        }
        
        for symbol in top_symbols[:20]:  # İlk 20 hisse
            try:
                data = self.get_quote_endpoint(symbol)
                if data:
                    change_percent = float(data['change_percent'].replace('%', ''))
                    
                    stock_info = {
                        'symbol': symbol,
                        'price': data['price'],
                        'change_percent': change_percent,
                        'volume': data['volume']
                    }
                    snapshot['stocks'].append(stock_info)
                    
                    # İstatistikler
                    snapshot['summary']['total_processed'] += 1
                    if change_percent > 0:
                        snapshot['summary']['positive_count'] += 1
                    elif change_percent < 0:
                        snapshot['summary']['negative_count'] += 1
                    if change_percent >= 9.0:
                        snapshot['summary']['ceiling_count'] += 1
                
            except Exception as e:
                logger.error(f"Snapshot hatası ({symbol}): {e}")
                continue
        
        return snapshot

# Test fonksiyonu
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test sembol listesi
    test_symbols = ['THYAO', 'AKBNK', 'GARAN', 'SISE', 'FROTO']
    
    try:
        fetcher = AlphaVantageRealTimeFetcher()
        
        print("🔍 Gerçek zamanlı test başlatılıyor...")
        
        # Test 1: Tek hisse
        print("\n📊 Test 1: THYAO hissesi")
        thyao_data = fetcher.get_quote_endpoint('THYAO')
        if thyao_data:
            print(f"THYAO: {thyao_data['price']} TL (%{thyao_data['change_percent']})")
        
        # Test 2: Tavan tarama
        print("\n🚀 Test 2: Tavan tarama")
        ceiling_stocks = fetcher.get_real_time_ceiling_stocks(test_symbols, threshold=5.0)  # %5+ test için
        for stock in ceiling_stocks:
            print(f"{stock['symbol']}: %{stock['change_percent']:.2f}")
        
        print(f"\n✅ Test tamamlandı - {len(ceiling_stocks)} yüksek artış bulundu")
        
    except Exception as e:
        print(f"❌ Test hatası: {e}")