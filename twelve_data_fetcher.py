#!/usr/bin/env python3
"""
Twelve Data Gerçek Zamanlı BİST Veri Çekme Modülü
1 dakika gecikmeli gerçek zamanlı BİST hisse senedi verilerini Twelve Data API'dan çeker.
"""

import requests
import pandas as pd
import time
import logging
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class TwelveDataRealTimeFetcher:
    def __init__(self, api_key: str = None):
        """Twelve Data gerçek zamanlı veri çekici başlat"""
        import os
        # Gerçek API key'i environment'dan al
        self.api_key = api_key or os.getenv('TWELVE_DATA_API_KEY', 'demo')
        self.base_url = "https://api.twelvedata.com"
        self.call_count = 0
        self.last_call_time = 0
        
        logger.info("Twelve Data Real-Time Fetcher başlatıldı")
    
    def _rate_limit_check(self):
        """API rate limit kontrolü (Free tier: 8 calls/min)"""
        current_time = time.time()
        if current_time - self.last_call_time < 8:  # 8 saniye bekle
            wait_time = 8 - (current_time - self.last_call_time)
            logger.debug(f"Rate limit - {wait_time:.1f} saniye bekleniyor...")
            time.sleep(wait_time)
        
        self.last_call_time = time.time()
        self.call_count += 1
    
    def get_quote(self, bist_symbol: str) -> Optional[Dict]:
        """
        Gerçek zamanlı quote data çek
        
        Args:
            bist_symbol: BİST hisse kodu (örn: "THYAO")
        """
        self._rate_limit_check()
        
        # BIST formatına çevir
        symbol = f"{bist_symbol}:BIST"
        
        params = {
            'symbol': symbol,
            'apikey': self.api_key
        }
        
        try:
            logger.debug(f"Twelve Data Quote API: {symbol}")
            response = requests.get(f"{self.base_url}/quote", params=params, timeout=20)
            
            if response.status_code == 429:
                logger.warning("API rate limit exceeded")
                return None
                
            if response.status_code != 200:
                logger.error(f"API çağrısı başarısız: {response.status_code}")
                return None
            
            data = response.json()
            
            # Hata kontrolü
            if 'status' in data and data['status'] == 'error':
                logger.error(f"API Hatası: {data.get('message', 'Unknown error')}")
                return None
                
            # Veri kontrolü
            required_fields = ['open', 'high', 'low', 'close', 'volume']
            if not all(field in data for field in required_fields):
                logger.warning(f"Eksik veri alanları: {bist_symbol}")
                return None
            
            result = {
                'symbol': bist_symbol,
                'open': float(data['open']),
                'high': float(data['high']),
                'low': float(data['low']),
                'close': float(data['close']),
                'volume': int(data['volume']),
                'previous_close': float(data.get('previous_close', data['close'])),
                'change': float(data.get('change', 0)),
                'percent_change': float(data.get('percent_change', 0)),
                'datetime': data.get('datetime', ''),
                'timestamp': datetime.now().strftime('%H:%M:%S'),
                'source': 'Twelve Data'
            }
            
            logger.debug(f"{bist_symbol} başarılı - Fiyat: {result['close']}, Değişim: %{result['percent_change']:.2f}")
            return result
            
        except requests.exceptions.Timeout:
            logger.error(f"Timeout hatası: {symbol}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"İstek hatası: {e}")
            return None
        except (ValueError, KeyError) as e:
            logger.error(f"Veri parsing hatası ({bist_symbol}): {e}")
            return None
    
    def get_time_series(self, bist_symbol: str, interval: str = "1min", outputsize: int = 12) -> Optional[Dict]:
        """
        Time series data çek (intraday)
        
        Args:
            bist_symbol: BİST hisse kodu
            interval: Zaman aralığı ("1min", "5min", "15min", "30min", "1h")
            outputsize: Veri nokta sayısı
        """
        self._rate_limit_check()
        
        symbol = f"{bist_symbol}:BIST"
        
        params = {
            'symbol': symbol,
            'interval': interval,
            'outputsize': outputsize,
            'apikey': self.api_key
        }
        
        try:
            logger.debug(f"Time Series API: {symbol} ({interval})")
            response = requests.get(f"{self.base_url}/time_series", params=params, timeout=30)
            
            if response.status_code != 200:
                return None
                
            data = response.json()
            
            if 'status' in data and data['status'] == 'error':
                logger.error(f"Time Series API Hatası: {data.get('message', '')}")
                return None
            
            # Meta data ve values kontrol
            if 'values' not in data or not data['values']:
                logger.warning(f"Time series data bulunamadı: {bist_symbol}")
                return None
            
            # En son veri noktası
            latest_data = data['values'][0]  # En yeni veri ilk sırada
            
            result = {
                'symbol': bist_symbol,
                'datetime': latest_data['datetime'],
                'open': float(latest_data['open']),
                'high': float(latest_data['high']),
                'low': float(latest_data['low']),
                'close': float(latest_data['close']),
                'volume': int(latest_data['volume']),
                'interval': interval,
                'total_points': len(data['values']),
                'source': 'Twelve Data TS'
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Time series hatası ({bist_symbol}): {e}")
            return None
    
    def get_real_time_ceiling_stocks(self, symbols: List[str], threshold: float = 9.0) -> List[Dict]:
        """
        Gerçek zamanlı tavan yapan hisseleri bul
        
        Args:
            symbols: BİST hisse kodları listesi
            threshold: Tavan eşiği (%9.0 = %9+)
        """
        logger.info(f"🔍 Twelve Data gerçek zamanlı tavan tarama - {len(symbols)} hisse")
        
        ceiling_stocks = []
        processed = 0
        
        # Batch request için sembol listesini grupla (Twelve Data max 120 symbol)
        batch_size = 20  # Conservative batch size
        
        for i in range(0, len(symbols), batch_size):
            batch_symbols = symbols[i:i+batch_size]
            
            try:
                # Batch quote request
                symbol_string = ','.join([f"{s}:BIST" for s in batch_symbols])
                
                params = {
                    'symbol': symbol_string,
                    'apikey': self.api_key
                }
                
                self._rate_limit_check()
                response = requests.get(f"{self.base_url}/quote", params=params, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Batch response processing  
                    if isinstance(data, str):
                        logger.error(f"API returned string: {data}")
                        continue
                    
                    if isinstance(data, dict):
                        if 'status' in data and data['status'] == 'error':
                            logger.error(f"Batch API error: {data.get('message', '')}")
                            continue
                        # Single stock response
                        data = [data]
                    
                    for stock_data in data:
                        if 'status' in stock_data and stock_data['status'] == 'error':
                            continue
                            
                        try:
                            symbol = stock_data.get('symbol', '').replace(':BIST', '')
                            percent_change = float(stock_data.get('percent_change', 0))
                            
                            if percent_change >= threshold:
                                ceiling_info = {
                                    'symbol': symbol,
                                    'current_price': float(stock_data.get('close', 0)),
                                    'change_percent': percent_change,
                                    'volume': int(stock_data.get('volume', 0)),
                                    'high': float(stock_data.get('high', 0)),
                                    'low': float(stock_data.get('low', 0)),
                                    'change': float(stock_data.get('change', 0)),
                                    'last_updated': datetime.now().strftime('%H:%M:%S'),
                                    'source': 'Twelve Data'
                                }
                                ceiling_stocks.append(ceiling_info)
                                logger.info(f"🚀 TAVAN: {symbol} %{percent_change:.2f}")
                            
                        except (ValueError, KeyError) as e:
                            logger.debug(f"Veri parsing hatası: {e}")
                            continue
                
                processed += len(batch_symbols)
                logger.info(f"📊 İşlenen: {processed}/{len(symbols)}")
                
                # Batch arası kısa bekleme
                if i + batch_size < len(symbols):
                    time.sleep(2)
                
            except Exception as e:
                logger.error(f"Batch işleme hatası: {e}")
                continue
        
        # Değişim oranına göre sırala
        ceiling_stocks.sort(key=lambda x: x['change_percent'], reverse=True)
        
        logger.info(f"🎯 Twelve Data tarama tamamlandı: {len(ceiling_stocks)} tavan bulundu")
        return ceiling_stocks
    
    def get_market_overview(self, top_symbols: List[str] = None) -> Dict[str, Any]:
        """
        Pazar genel görünümü
        """
        if not top_symbols:
            top_symbols = ['THYAO', 'AKBNK', 'GARAN', 'SISE', 'FROTO']
        
        logger.info("📊 Pazar görünümü alınıyor...")
        
        overview = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'stocks': [],
            'summary': {
                'total_processed': 0,
                'positive_count': 0,
                'negative_count': 0,
                'ceiling_count': 0,
                'avg_change': 0
            }
        }
        
        total_change = 0
        
        for symbol in top_symbols[:15]:  # İlk 15 hisse
            try:
                data = self.get_quote(symbol)
                if data:
                    change_percent = data['percent_change']
                    
                    stock_info = {
                        'symbol': symbol,
                        'price': data['close'],
                        'change_percent': change_percent,
                        'volume': data['volume'],
                        'high': data['high'],
                        'low': data['low']
                    }
                    overview['stocks'].append(stock_info)
                    
                    # İstatistikler
                    overview['summary']['total_processed'] += 1
                    total_change += change_percent
                    
                    if change_percent > 0:
                        overview['summary']['positive_count'] += 1
                    elif change_percent < 0:
                        overview['summary']['negative_count'] += 1
                    if change_percent >= 9.0:
                        overview['summary']['ceiling_count'] += 1
                
            except Exception as e:
                logger.error(f"Overview hatası ({symbol}): {e}")
                continue
        
        # Ortalama hesapla
        if overview['summary']['total_processed'] > 0:
            overview['summary']['avg_change'] = total_change / overview['summary']['total_processed']
        
        return overview

# Test fonksiyonu
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    try:
        fetcher = TwelveDataRealTimeFetcher()
        
        print("🔍 Twelve Data gerçek zamanlı test başlatılıyor...")
        
        # Test 1: Tek hisse
        print("\n📊 Test 1: THYAO hissesi")
        thyao_data = fetcher.get_quote('THYAO')
        if thyao_data:
            print(f"✅ THYAO: {thyao_data['close']} TL (%{thyao_data['percent_change']:+.2f})")
            print(f"   Hacim: {thyao_data['volume']:,} | Kaynak: {thyao_data['source']}")
        else:
            print("❌ THYAO verisi alınamadı")
        
        # Test 2: Time series
        print("\n📈 Test 2: Time Series (5min)")
        ts_data = fetcher.get_time_series('THYAO', '5min', 5)
        if ts_data:
            print(f"✅ Time Series: {ts_data['close']} TL ({ts_data['datetime']})")
            print(f"   Toplam veri noktası: {ts_data['total_points']}")
        
        # Test 3: Tavan tarama (düşük eşik test için)
        test_symbols = ['THYAO', 'AKBNK', 'GARAN', 'SISE', 'FROTO']
        print(f"\n🚀 Test 3: Tavan tarama ({len(test_symbols)} hisse)")
        ceiling_stocks = fetcher.get_real_time_ceiling_stocks(test_symbols, threshold=3.0)
        
        if ceiling_stocks:
            print(f"✅ {len(ceiling_stocks)} yüksek artış bulundu:")
            for stock in ceiling_stocks:
                print(f"   🎯 {stock['symbol']}: %{stock['change_percent']:+.2f} ({stock['current_price']} TL)")
        else:
            print("ℹ️ Yüksek artış bulunamadı (normal)")
        
        # Test 4: Market overview
        print("\n📊 Test 4: Pazar görünümü")
        overview = fetcher.get_market_overview(test_symbols)
        summary = overview['summary']
        print(f"✅ İşlenen: {summary['total_processed']}")
        print(f"   📈 Pozitif: {summary['positive_count']}")
        print(f"   📉 Negatif: {summary['negative_count']}")
        print(f"   🚀 Tavan: {summary['ceiling_count']}")
        print(f"   📊 Ortalama: %{summary['avg_change']:.2f}")
        
        print(f"\n✅ Test tamamlandı - API çağrı sayısı: {fetcher.call_count}")
        
    except Exception as e:
        print(f"❌ Test hatası: {e}")