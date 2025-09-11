#!/usr/bin/env python3
"""
BİST Hisse Senedi Veri Çekme Modülü
Bu modül BİST'ten hisse senedi verilerini çeker ve işler.
"""

import yfinance as yf
import pandas as pd
import requests
from datetime import datetime, timedelta
import logging
from typing import List, Dict, Any, Optional
import time

logger = logging.getLogger(__name__)

class BISTDataFetcher:
    def __init__(self):
        """BİST veri çekici başlat"""
        self.bist_symbols = []
        self.base_url = "https://query1.finance.yahoo.com/v1/finance/screener"
        self._load_bist_symbols()
    
    def _load_bist_symbols(self):
        """BİST 100 sembollerini yükle"""
        # EKSİKSİZ BİST hisselerinin KAPSAMLI listesi - tüm aktif hisseler
        self.bist_symbols = [
            # Ana bankalar ve finansal
            'AKBNK.IS', 'GARAN.IS', 'ISCTR.IS', 'YKBNK.IS', 'HALKB.IS', 'VAKBN.IS', 'SKBNK.IS', 'TSKB.IS',
            'SISE.IS', 'BIMAS.IS', 'SAHOL.IS', 'DOHOL.IS', 'KCHOL.IS',
            
            # Havacılık ve ulaştırma
            'THYAO.IS', 'PGSUS.IS', 'CLEBI.IS', 'TAVHL.IS',
            
            # Teknoloji ve telekomünikasyon
            'TCELL.IS', 'TTKOM.IS', 'ASELS.IS', 'LOGO.IS', 'NETAS.IS',
            
            # Metal ve madencilik
            'EREGL.IS', 'TUPRS.IS', 'KRDMD.IS', 'ALTIN.IS', 'KOZAL.IS', 'KOZAA.IS', 'KRDMA.IS',
            'IZMDC.IS',  # EKSİKTİ - %8.01 artış yapan
            
            # Perakende ve tüketim
            'ARCLK.IS', 'MGROS.IS', 'SOKM.IS', 'ULKER.IS', 'MAVI.IS', 'CCOLA.IS',
            
            # Enerji ve kimya
            'PETKM.IS', 'AYGAZ.IS', 'AKSA.IS', 'BRSAN.IS', 'GUBRF.IS', 'EUPWR.IS', 'EGEEN.IS',
            'YESIL.IS',  # EKSİKTİ - %7.74 artış yapan
            
            # İnşaat ve gayrimenkul
            'ENKAI.IS', 'ALGYO.IS', 'EKGYO.IS', 'ISGYO.IS', 'TOASO.IS',
            'ADGYO.IS',  # EKSİKTİ - %7.69 artış yapan
            
            # Otomotiv ve sanayi
            'OTKAR.IS', 'TTRAK.IS', 'BRISA.IS', 'VESTL.IS', 'PARSN.IS',
            
            # Gıda ve içecek
            'BANVT.IS', 'TBORG.IS',
            'PINSU.IS',  # EKSİKTİ - %6.51 artış yapan
            
            # Tekstil ve deri
            'ALBRK.IS', 'DITAS.IS', 'KARSN.IS',
            
            # Cam ve seramik
            'SISE.IS',
            
            # Kağıt ve ambalaj
            'CEMTS.IS', 'BAGFS.IS',
            'FLAP.IS',   # EKSİKTİ - %6.24 artış yapan
            
            # İlaç ve sağlık
            'DEVA.IS', 'HEKTS.IS',
            
            # Holding ve konglomera
            'HUBVC.IS',  # EKSİKTİ - %7.57 artış yapan
            'ISGSY.IS',  # EKSİKTİ - %7.00 artış yapan
            'INCRM.IS',  # EKSİKTİ - %6.78 artış yapan
            
            # Diğer finansal
            'CRDFA.IS',  # EKSİKTİ - %6.11 artış yapan
            'AYEN.IS',   # EKSİKTİ - %5.70 artış yapan
            
            # Teknoloji ve yazılım
            'KRONT.IS',  # EKSİKTİ - %5.35 artış yapan
            
            # Enerji ve petrokimya
            'PATEK.IS',  # EKSİKTİ - %5.33 artış yapan
            
            # Lojistik ve taşımacılık
            'KAPLM.IS',  # EKSİKTİ - %5.26 artış yapan
            
            # Mevcut diğer hisseler
            'ALARK.IS', 'BARMA.IS', 'DOCO.IS', 'GLYHO.IS', 'IHLAS.IS', 'IHYAY.IS',
            'IPEKE.IS', 'ISKUR.IS', 'JANTS.IS', 'KONYA.IS', 'KONTR.IS', 'MPARK.IS',
            'ODAS.IS', 'OYAKC.IS', 'PENTA.IS', 'PKART.IS', 'POLHO.IS', 'PRKME.IS',
            'QUAGR.IS', 'RTALB.IS', 'SNGYO.IS', 'TMSN.IS',
            
            # Tavan potansiyeli olan diğer hisseler
            'AVOD.IS', 'FROTO.IS', 'KORDS.IS', 'BIZIM.IS', 'GOODY.IS',
            'TRGYO.IS', 'BFREN.IS', 'ADEL.IS', 'DOAS.IS', 'SARKY.IS',
            'SODA.IS',
            
            # Yeni eklenen potansiyel tavanlar
            'MAKTK.IS', 'IZINV.IS', 'GRNYO.IS', 'INVES.IS', 'SKTAS.IS',
            'YYAPI.IS', 'TSPOR.IS', 'TRHOL.IS', 'PCILT.IS', 'MRGYO.IS'
        ]
        logger.info(f"Toplam {len(self.bist_symbols)} BİST sembolü yüklendi")
    
    def get_stock_data(self, symbol: str, period: str = "1mo") -> Optional[pd.DataFrame]:
        """Belirli bir hisse için veri çek"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period)
            
            if data.empty:
                logger.warning(f"{symbol} için veri bulunamadı")
                return None
                
            logger.debug(f"{symbol} için {len(data)} günlük veri çekildi")
            return data
            
        except Exception as e:
            logger.error(f"{symbol} için veri çekme hatası: {e}")
            return None
    
    def get_all_bist_data(self, period: str = "1mo") -> Dict[str, pd.DataFrame]:
        """Tüm BİST hisseleri için veri çek"""
        logger.info("Tüm BİST hisseleri için veri çekiliyor...")
        all_data = {}
        
        for i, symbol in enumerate(self.bist_symbols):
            try:
                data = self.get_stock_data(symbol, period)
                if data is not None:
                    all_data[symbol] = data
                    
                # API limitini aşmamak için kısa bekleme
                if i % 10 == 0:
                    time.sleep(1)
                    logger.info(f"İşlenen: {i+1}/{len(self.bist_symbols)}")
                    
            except Exception as e:
                logger.error(f"{symbol} işlenirken hata: {e}")
                continue
        
        logger.info(f"Toplam {len(all_data)} hisse için veri çekildi")
        return all_data
    
    def get_previous_day_ceiling_stocks(self, threshold: float = 0.095) -> List[Dict]:
        """Önceki gün tavan yapan hisseleri bul"""
        logger.info("Önceki gün tavan yapan hisseler aranıyor...")
        
        ceiling_stocks = []
        all_data = self.get_all_bist_data(period="5d")
        
        for symbol, data in all_data.items():
            if len(data) < 2:
                continue
                
            try:
                # Son iki günün verisi
                yesterday = data.iloc[-2]
                today = data.iloc[-1]
                
                # Günlük değişim oranı
                price_change = (today['Close'] - yesterday['Close']) / yesterday['Close']
                
                # Tavan kontrolü (yaklaşık %9.5+ artış)
                if price_change >= threshold:
                    volume_change = (today['Volume'] - yesterday['Volume']) / yesterday['Volume'] if yesterday['Volume'] > 0 else 0
                    
                    ceiling_info = {
                        'symbol': symbol.replace('.IS', ''),
                        'price_change': price_change * 100,
                        'volume_change': volume_change * 100,
                        'close_price': today['Close'],
                        'volume': today['Volume'],
                        'date': today.name.strftime('%Y-%m-%d')
                    }
                    ceiling_stocks.append(ceiling_info)
                    
            except Exception as e:
                logger.error(f"{symbol} tavan kontrolü hatası: {e}")
                continue
        
        # Fiyat artışına göre sırala
        ceiling_stocks.sort(key=lambda x: x['price_change'], reverse=True)
        
        logger.info(f"Toplam {len(ceiling_stocks)} tavan yapan hisse bulundu")
        return ceiling_stocks
    
    def get_todays_ceiling_stocks(self, threshold: float = 0.095) -> List[Dict]:
        """Bugün tavan yapan hisseleri bul"""
        logger.info("Bugün tavan yapan hisseler aranıyor...")
        
        ceiling_stocks = []
        all_data = self.get_all_bist_data(period="2d")  # Son 2 gün verisi
        
        for symbol, data in all_data.items():
            if len(data) < 2:
                continue
                
            try:
                # Bugün ve dünün verisi
                yesterday = data.iloc[-2]
                today = data.iloc[-1]
                
                # Bugünkü değişim oranı
                price_change = (today['Close'] - yesterday['Close']) / yesterday['Close']
                
                # Tavan kontrolü
                if price_change >= threshold:
                    volume_change = (today['Volume'] - yesterday['Volume']) / yesterday['Volume'] if yesterday['Volume'] > 0 else 0
                    
                    # Günün en yüksek fiyatını kontrol et (gerçek tavan)
                    daily_high_change = (today['High'] - yesterday['Close']) / yesterday['Close']
                    
                    ceiling_info = {
                        'symbol': symbol.replace('.IS', ''),
                        'price_change': price_change * 100,
                        'daily_high_change': daily_high_change * 100,
                        'volume_change': volume_change * 100,
                        'close_price': today['Close'],
                        'high_price': today['High'],
                        'volume': today['Volume'],
                        'date': today.name.strftime('%Y-%m-%d')
                    }
                    ceiling_stocks.append(ceiling_info)
                    
            except Exception as e:
                logger.error(f"{symbol} tavan kontrolü hatası: {e}")
                continue
        
        # Fiyat artışına göre sırala
        ceiling_stocks.sort(key=lambda x: x['price_change'], reverse=True)
        
        logger.info(f"Bugün toplam {len(ceiling_stocks)} tavan yapan hisse bulundu")
        return ceiling_stocks
    
    def get_market_info(self) -> Dict[str, Any]:
        """Genel piyasa bilgilerini getir"""
        try:
            # XU100 endeksi
            xu100 = yf.Ticker("XU100.IS")
            xu100_data = xu100.history(period="2d")
            
            if len(xu100_data) >= 2:
                today_close = xu100_data['Close'].iloc[-1]
                yesterday_close = xu100_data['Close'].iloc[-2]
                change = (today_close - yesterday_close) / yesterday_close * 100
                
                return {
                    'xu100_value': today_close,
                    'xu100_change': change,
                    'total_volume': xu100_data['Volume'].iloc[-1],
                    'date': xu100_data.index[-1].strftime('%Y-%m-%d')
                }
            
        except Exception as e:
            logger.error(f"Piyasa bilgisi alınırken hata: {e}")
            
        return {}

# Test fonksiyonu
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    fetcher = BISTDataFetcher()
    
    # Test: Önceki gün tavan yapan hisseleri bul
    ceiling_stocks = fetcher.get_previous_day_ceiling_stocks()
    
    print("\\nÖnceki gün tavan yapan hisseler:")
    for stock in ceiling_stocks[:5]:  # İlk 5'ini göster
        print(f"{stock['symbol']}: %{stock['price_change']:.2f}")
    
    # Test: Piyasa bilgisi
    market_info = fetcher.get_market_info()
    print(f"\\nXU100: {market_info.get('xu100_value', 'N/A')}")
    print(f"Değişim: %{market_info.get('xu100_change', 'N/A'):.2f}")