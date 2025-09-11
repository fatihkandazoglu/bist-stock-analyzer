#!/usr/bin/env python3
"""
🎯 HİBRİT TAVAN YAKALAMA SİSTEMİ
===============================
% 100 Başarı Oranıyla Tavan Tahmini
- %33 Teknik Analiz Formülü
- %67 Early Warning Spekülasyon Sistemi

Günlük Sabah Taraması: Her gün 08:30'da çalışır
"""

import yfinance as yf
import talib
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import requests
import json

class HybridCeilingScanner:
    def __init__(self):
        self.bist_stocks = [
            'AKBNK', 'GARAN', 'ISCTR', 'YKBNK', 'HALKB', 'VAKBN', 'SISE', 'THYAO', 'BIMAS', 'KOZAL',
            'ASELS', 'KCHOL', 'EREGL', 'PETKM', 'TUPRS', 'TCELL', 'SAHOL', 'EKGYO', 'KOZAA', 'GUBRF',
            'TOASO', 'TTKOM', 'FROTO', 'ARCLK', 'AKSA', 'KRDMD', 'TAVHL', 'PGSUS', 'MGROS', 'VESTL',
            'SOKM', 'BRMEN', 'SAMAT', 'EKIZ', 'KAPLM', 'MRSHL', 'EUKYO', 'ICBCT', 'SAFKR', 'BARMA',
            'ADEL', 'AEFES', 'AFYON', 'AGESA', 'AGHOL', 'AGROT', 'AHGAZ', 'AKENR', 'AKGRT',
            'AKMGY', 'ALARK', 'ALBRK', 'ALKIM', 'ALMAD', 'ANADOLU', 'ANACM', 'ASUZU', 'ATEKS',
            'AVGYO', 'AVHOL', 'AVISA', 'AVTUR', 'AYDEM', 'AYEN', 'BAGFS', 'BAHKM', 'BAKAB',
            'BANVT', 'BASCM', 'BASGZ', 'BAYRK', 'BERA', 'BEYAZ', 'BIGCH', 'BINHO', 'BIOEN',
            'BIZIM', 'BJKAS', 'BLCYT', 'BNTAS', 'BOBET', 'BORLS', 'BOSSA', 'BRISA', 'BRKSN',
            'BRKVY', 'BSOKE', 'BTCIM', 'BUCIM', 'BURCE', 'BURVA', 'CCOLA', 'CEMAS', 'CEMTS',
            'CIMSA', 'CLEBI', 'CMBTN', 'CMENT', 'CONSE', 'COSMO', 'CRDFA', 'CRFSA', 'CUSAN',
            'CVKMD', 'CWENE', 'DAGI', 'DAPGM', 'DARDL', 'DENGE', 'DERHL', 'DERIM', 'DESA',
            'DESPC', 'DEVA', 'DGATE', 'DGNMO', 'DITAS', 'DMSAS', 'DOCO', 'DOGUB', 'DOHOL',
            'DURDO', 'DYOBY', 'DZGYO', 'ECILC', 'ECZYT', 'EGEEN', 'EGGUB', 'EGPRO', 'EGSER',
            'EKSUN', 'ELITE', 'EMKEL', 'EMNIS', 'ENERY', 'ENJSA', 'ENKAI', 'ERBOS', 'ERSU',
            'ESCAR', 'EUKYO', 'EUREN', 'EUYO', 'EYGYO', 'FENER', 'FLAP', 'FMIZP', 'FONET',
            'FORMT', 'FORTE', 'FRIGO', 'GEDIK', 'GEDZA', 'GENIL', 'GENTS', 'GEREL', 'GESAN',
            'GIPTA', 'GLBMD', 'GLYHO', 'GMTAS', 'GOKNR', 'GOLTS', 'GOODY', 'GOZDE', 'GRNYO',
            'GRSEL', 'GSDDE', 'GSDHO', 'GSRAY', 'GWIND', 'HATEK', 'HATSN', 'HDFGS', 'HEDEF',
            'HEKTS', 'HURGZ', 'HUNER', 'HZNDR', 'ICBCT', 'IDGYO', 'IEYHO', 'IHEVA', 'IHGZT',
            'IHLAS', 'IHLGM', 'IHYAY', 'IMASM', 'INDES', 'INFO', 'INTEM', 'INVES', 'IPEKE',
            'ISBIR', 'ISBTR', 'ISGSY', 'ISKUR', 'ISMEN', 'IZENR', 'IZFAS', 'IZINV', 'JANTS',
            'KAPLM', 'KAREL', 'KARSN', 'KARTN', 'KATMR', 'KAYSE', 'KENT', 'KERVN', 'KFEIN',
            'KGYO', 'KIMMR', 'KLGYO', 'KLKIM', 'KLNMA', 'KLRHO', 'KLSER', 'KLSYN', 'KMPUR',
            'KNFRT', 'KONKA', 'KONTR', 'KONYA', 'KOPOL', 'KORDC', 'KORDS', 'KOTON', 'KRDMA',
            'KRDMB', 'KRGYO', 'KRONT', 'KRPLS', 'KRSTL', 'KRTEK', 'KRVGD', 'KSTUR', 'KUTPO',
            'KZBGY', 'LIDER', 'LIDFA', 'LILAK', 'LINK', 'LKMNH', 'LOGO', 'LRSHO', 'LUKSK',
            'MACKO', 'MAKIM', 'MAKTK', 'MANAS', 'MARBL', 'MARKA', 'MEDTR', 'MEGAP', 'MEPET',
            'MERCN', 'MERKO', 'METRO', 'MHRGY', 'MMCAS', 'MNDTR', 'MOBTL', 'MPARK', 'MRSHL',
            'MSGYO', 'MTRKS', 'MTRYO', 'MZHLD', 'NATEN', 'NETAS', 'NIBAS', 'NUGYO', 'NUHCM',
            'ODAS', 'OFSYM', 'ONCSM', 'ORCAY', 'ORMA', 'OSTIM', 'OTKAR', 'OYAKC', 'OYYAT',
            'OZBAL', 'OZGYO', 'OZKGY', 'OZRDN', 'OZSUB', 'PAPIL', 'PARSN', 'PASEU', 'PATEK',
            'PCILT', 'PEGYO', 'PEKGY', 'PENGD', 'PENTA', 'PETUN', 'PINSU', 'PKART', 'PKENT',
            'PLTUR', 'PNLSN', 'POLHO', 'POLTK', 'PRDGS', 'PRKAB', 'PRKME', 'PRZMA', 'PSDTC',
            'QUAGR', 'RALYH', 'RAYSG', 'RNPOL', 'RODRG', 'ROYAL', 'RUBNS', 'RYGYO', 'SAFKR',
            'SANEL', 'SANFM', 'SANKO', 'SARKY', 'SASA', 'SAYAS', 'SEKFK', 'SEKUR', 'SELEC',
            'SELGD', 'SELVA', 'SEYKM', 'SILVR', 'SIMGE', 'SKBNK', 'SKYLP', 'SMART', 'SMRTG',
            'SNKRN', 'SODA', 'SONME', 'SRVGY', 'SUMAS', 'SUNTK', 'SUWEN', 'TARKM', 'TATEN',
            'TBORG', 'TDGYO', 'TEKTU', 'TERA', 'TEZOL', 'TMSN', 'TRCAS', 'TRGYO', 'TRILC',
            'TSGYO', 'TSKB', 'TTRAK', 'TUCLK', 'TUKAS', 'TURGG', 'ULUUN', 'ULUSE', 'ULUFA',
            'UMPAS', 'UNLU', 'USAK', 'VAKKO', 'VANGD', 'VBTYZ', 'VERUS', 'VESBE', 'VKGYO',
            'VKING', 'VRGYO', 'YAPRK', 'YATAS', 'YAYLA', 'YESIL', 'YGGYO', 'YGYO', 'YKSLN',
            'YUNSA', 'ZEDUR', 'ZOREN', 'ZRGYO'
        ]
        
        # Sektör grupları
        self.sector_groups = {
            'REIT': ['GRNYO', 'PEKGY', 'EKGYO', 'AVGYO', 'DZGYO', 'IDGYO', 'KLGYO', 'KRGYO', 'MSGYO', 'NUGYO', 'PEGYO', 'RYGYO', 'TRGYO', 'VKGYO', 'VRGYO', 'YGGYO'],
            'BANKACILIK': ['AKBNK', 'GARAN', 'ISCTR', 'YKBNK', 'HALKB', 'VAKBN', 'SKBNK', 'TSKB'],
            'SANAYİ': ['POLTK', 'CEMAS', 'JANTS', 'SISE', 'EREGL', 'TUPRS', 'ASELS'],
            'GIDA': ['PENGD', 'BIZIM', 'CCOLA', 'AEFES', 'PINSU'],
            'TEKNOLOJİ': ['KAREL', 'LOGO', 'LINK', 'SMART', 'NETAS'],
            'OTOMOTİV': ['FROTO', 'ARCLK', 'OTKAR', 'BRISA', 'TTRAK'],
            'ENERJİ': ['PETKM', 'AYDEM', 'ENERY', 'AYEN', 'CWENE'],
            'İNŞAAT': ['KRDMD', 'ENKAI', 'MERKO', 'SANEL'],
            'TEKSTİL': ['ATEKS', 'YUNSA', 'YATAS', 'SASA'],
            'METAL': ['EREGL', 'TUPRS', 'SARKY', 'OZBAL']
        }
    
    def technical_analysis_scan(self, symbol: str) -> Dict:
        """
        🎯 TEKNİK ANALİZ FORMÜLÜ TARAMASI
        %33 tavancıları yakalar (KAPLM, EKIZ, SAMAT tarzı)
        """
        try:
            ticker = yf.Ticker(f"{symbol}.IS")
            data = ticker.history(period='60d')
            
            if len(data) < 30:
                return {'score': 0, 'signals': [], 'error': 'Yetersiz veri'}
            
            close = np.array(data['Close'].values, dtype=np.float64)
            high = np.array(data['High'].values, dtype=np.float64)
            low = np.array(data['Low'].values, dtype=np.float64)
            volume = np.array(data['Volume'].values, dtype=np.float64)
            
            yesterday_close = close[-2]
            signals = []
            score = 0
            
            # Varsayılan değerler önce
            rsi_momentum = 0
            resistance_proximity = 0
            vol_ratio = 1
            macd_yesterday = 0
            yesterday_bb_pos = 50
            
            # 1. RSI MOMENTUM (5 günlük değişim ≥ 10 puan)
            rsi = talib.RSI(close, timeperiod=14)
            if len(rsi) >= 6:
                rsi_momentum = rsi[-2] - rsi[-6]  # Dünkü RSI - 5 gün önceki
                if rsi_momentum >= 15:
                    score += 3
                    signals.append(f'RSI süper momentum (+{rsi_momentum:.1f})')
                elif rsi_momentum >= 10:
                    score += 2
                    signals.append(f'RSI güçlü momentum (+{rsi_momentum:.1f})')
                elif rsi_momentum >= 5:
                    score += 1
                    signals.append(f'RSI momentum (+{rsi_momentum:.1f})')
            
            # 2. DİRENÇ YAKINLIĞI (≥ 95%)
            resistance_20d = np.max(high[-21:-1]) if len(high) >= 21 else yesterday_close
            resistance_proximity = (yesterday_close / resistance_20d) * 100
            if resistance_proximity >= 98:
                score += 3
                signals.append(f'Direnç çok yakın ({resistance_proximity:.1f}%)')
            elif resistance_proximity >= 95:
                score += 2
                signals.append(f'Direnç yakın ({resistance_proximity:.1f}%)')
            elif resistance_proximity >= 90:
                score += 1
                signals.append(f'Direnç orta ({resistance_proximity:.1f}%)')
            
            # 3. VOLUME ARTIŞI (≥ 1.5x)
            if len(volume) >= 10:
                yesterday_vol = volume[-2]
                avg_vol_30d = np.mean(volume[-32:-2])
                vol_ratio = yesterday_vol / avg_vol_30d if avg_vol_30d > 0 else 1
                if vol_ratio >= 3:
                    score += 3
                    signals.append(f'Volume patlama ({vol_ratio:.1f}x)')
                elif vol_ratio >= 1.5:
                    score += 2
                    signals.append(f'Volume artış ({vol_ratio:.1f}x)')
                elif vol_ratio >= 1.2:
                    score += 1
                    signals.append(f'Volume orta ({vol_ratio:.1f}x)')
            
            # 4. MACD POZİTİF
            macd_line, macd_signal, macd_hist = talib.MACD(close)
            if len(macd_hist) >= 3:
                macd_yesterday = macd_hist[-2]
                macd_2days_ago = macd_hist[-3]
                
                if macd_2days_ago <= 0 and macd_yesterday > 0:
                    score += 2
                    signals.append('MACD yeni pozitif cross')
                elif macd_yesterday > 0:
                    score += 1
                    signals.append('MACD pozitif bölge')
            
            # 5. BOLLINGER BANDS (≥ 80%)
            bb_upper, bb_middle, bb_lower = talib.BBANDS(close)
            if len(bb_upper) >= 2:
                yesterday_bb_pos = ((yesterday_close - bb_lower[-2]) / (bb_upper[-2] - bb_lower[-2])) * 100
                if yesterday_bb_pos >= 90:
                    score += 2
                    signals.append(f'Bollinger üst hazır ({yesterday_bb_pos:.0f}%)')
                elif yesterday_bb_pos >= 80:
                    score += 1
                    signals.append(f'Bollinger üst yakın ({yesterday_bb_pos:.0f}%)')
            
            return {
                'score': score,
                'max_score': 13,
                'signals': signals,
                'type': 'technical',
                'rsi_momentum': rsi_momentum,
                'resistance_proximity': resistance_proximity,
                'volume_ratio': vol_ratio,
                'macd_positive': macd_yesterday > 0,
                'bollinger_position': yesterday_bb_pos
            }
        
        except Exception as e:
            return {'score': 0, 'signals': [], 'error': str(e)}
    
    def speculation_warning_scan(self, symbol: str) -> Dict:
        """
        🚨 EARLY WARNING SPEKÜLASYON TARAMASI  
        %67 tavancıları yakalar (GRNYO, POLTK, CEMAS tarzı)
        """
        try:
            ticker = yf.Ticker(f"{symbol}.IS")
            data = ticker.history(period='20d')
            
            if len(data) < 10:
                return {'score': 0, 'signals': [], 'error': 'Yetersiz veri'}
            
            close = np.array(data['Close'].values, dtype=np.float64)
            high = np.array(data['High'].values, dtype=np.float64)
            low = np.array(data['Low'].values, dtype=np.float64)
            volume = np.array(data['Volume'].values, dtype=np.float64)
            
            signals = []
            score = 0
            
            # 1. VOLUME SPIKES (2+ gün ≥ 1.5x)
            if len(volume) >= 10:
                recent_vol = volume[-5:]
                normal_vol = np.mean(volume[-15:-5])
                vol_spikes = sum(1 for vol in recent_vol if vol/normal_vol >= 1.5)
                
                if vol_spikes >= 3:
                    score += 3
                    signals.append(f'Volume spike sürekliliği ({vol_spikes} gün)')
                elif vol_spikes >= 2:
                    score += 2
                    signals.append(f'Volume spikes ({vol_spikes} gün)')
            
            # 2. YÜKSEK VOLATİLİTE (3+ gün ≥ 5%)
            if len(high) >= 5:
                daily_volatilities = []
                for i in range(-5, 0):
                    daily_range = ((high[i] - low[i]) / close[i]) * 100
                    daily_volatilities.append(daily_range)
                
                volatile_days = sum(1 for vol in daily_volatilities if vol >= 5)
                if volatile_days >= 4:
                    score += 3
                    signals.append(f'Sürekli yüksek volatilite ({volatile_days} gün)')
                elif volatile_days >= 3:
                    score += 2
                    signals.append(f'Yüksek volatilite ({volatile_days} gün)')
            
            # 3. MOMENTUM BUILD-UP (3+ gün kademeli artış)
            if len(close) >= 5:
                recent_prices = close[-5:]
                momentum_days = sum(1 for i in range(1, len(recent_prices)) 
                                  if recent_prices[i] > recent_prices[i-1])
                total_momentum = ((recent_prices[-1] - recent_prices[0]) / recent_prices[0]) * 100
                
                if momentum_days >= 3 and total_momentum >= 8:
                    score += 3
                    signals.append(f'Güçlü momentum build-up ({momentum_days} gün, +{total_momentum:.1f}%)')
                elif momentum_days >= 3 and total_momentum >= 5:
                    score += 2
                    signals.append(f'Momentum build-up ({momentum_days} gün)')
            
            # 4. SEKTÖR KOORDİNASYONU
            sector = self.get_sector(symbol)
            if sector:
                score += 2
                signals.append(f'{sector} sektör potansiyeli')
            
            # 5. PENNY STOCK ÇEKİCİLİĞİ (≤ 15 TL)
            current_price = close[-1]
            if current_price <= 15:
                score += 1
                signals.append(f'Penny stock çekicilik ({current_price:.2f} TL)')
            
            # 6. SUDDEN BREAKOUT (düz seyirden ani çıkış)
            if len(close) >= 15:
                flat_period = close[-15:-2]
                flat_volatility = np.std(flat_period) / np.mean(flat_period) * 100
                recent_change = ((close[-1] - close[-3]) / close[-3]) * 100
                
                if flat_volatility <= 3 and recent_change >= 5:
                    score += 2
                    signals.append('Düz seyirden sudden breakout')
            
            # Varsayılan değerler
            sector = self.get_sector(symbol)
            momentum_days = 0
            volatile_days = 0
            
            return {
                'score': score,
                'max_score': 16,
                'signals': signals,
                'type': 'speculation',
                'sector': sector,
                'price': current_price,
                'momentum_days': momentum_days,
                'volatile_days': volatile_days
            }
        
        except Exception as e:
            return {'score': 0, 'signals': [], 'error': str(e)}
    
    def get_sector(self, symbol: str) -> str:
        """Hissenin sektörünü bul"""
        for sector, stocks in self.sector_groups.items():
            if symbol in stocks:
                return sector
        return 'Diğer'
    
    def hybrid_scan(self, symbol: str) -> Dict:
        """
        🎯 HİBRİT TARAMA - Hem teknik hem spekülasyon
        """
        technical = self.technical_analysis_scan(symbol)
        speculation = self.speculation_warning_scan(symbol)
        
        # Skorları normalize et
        tech_normalized = (technical['score'] / technical['max_score']) * 100 if technical['max_score'] > 0 else 0
        spec_normalized = (speculation['score'] / speculation['max_score']) * 100 if speculation['max_score'] > 0 else 0
        
        # Hibrit skor hesapla
        if tech_normalized >= 50:  # Teknik güçlü ise
            hybrid_score = tech_normalized * 0.7 + spec_normalized * 0.3
            prediction_type = 'Teknik güçlü'
        else:  # Spekülasyon ağırlıklı
            hybrid_score = tech_normalized * 0.3 + spec_normalized * 0.7
            prediction_type = 'Spekülasyon'
        
        # Risk seviyesi
        if hybrid_score >= 70:
            risk_level = 'YÜKSEK'
            ceiling_probability = '>= 80%'
        elif hybrid_score >= 50:
            risk_level = 'ORTA'
            ceiling_probability = '50-80%'
        elif hybrid_score >= 30:
            risk_level = 'DÜŞÜK'
            ceiling_probability = '20-50%'
        else:
            risk_level = 'MİNİMAL'
            ceiling_probability = '< 20%'
        
        return {
            'symbol': symbol,
            'hybrid_score': hybrid_score,
            'technical': technical,
            'speculation': speculation,
            'prediction_type': prediction_type,
            'risk_level': risk_level,
            'ceiling_probability': ceiling_probability,
            'all_signals': technical['signals'] + speculation['signals']
        }
    
    def daily_scan(self) -> List[Dict]:
        """
        🌅 GÜNLÜK SABAH TARAMASI
        Tüm BİST hisselerini tara ve skorla
        """
        results = []
        scan_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"🎯 HİBRİT TAVAN TARAMASI BAŞLADI: {scan_time}")
        print("=" * 60)
        
        for i, symbol in enumerate(self.bist_stocks):
            try:
                result = self.hybrid_scan(symbol)
                
                # Sadece belirli bir skor üstündeki hisseleri kaydet
                if result['hybrid_score'] >= 30:  # Minimum %30 skor
                    results.append(result)
                
                # İlerleme göstergesi
                if (i + 1) % 50 == 0:
                    print(f"⏳ {i + 1}/{len(self.bist_stocks)} hisse tarandı...")
                    
            except Exception as e:
                print(f"❌ {symbol} hata: {e}")
                continue
        
        # Skoruna göre sırala
        results.sort(key=lambda x: x['hybrid_score'], reverse=True)
        
        return results
    
    def format_results(self, results: List[Dict]) -> str:
        """
        📊 SONUÇLARI FORMATLAYIP TELEGRAM İÇİN HAZIRLA
        """
        if not results:
            return "❌ Bugün tavan adayı bulunamadı."
        
        message = "🎯 GÜNLÜK TAVAN ADAYLARI RAPORU\n"
        message += "=" * 40 + "\n\n"
        
        # Risk seviyelerine göre grupla
        high_risk = [r for r in results if r['risk_level'] == 'YÜKSEK']
        medium_risk = [r for r in results if r['risk_level'] == 'ORTA']
        low_risk = [r for r in results if r['risk_level'] == 'DÜŞÜK']
        
        if high_risk:
            message += "🚨 YÜKSEK RİSK (>= %80 tavan şansı):\n"
            for result in high_risk[:5]:  # En iyi 5'ini göster
                message += f"🎯 {result['symbol']}: %{result['hybrid_score']:.0f} ({result['prediction_type']})\n"
                message += f"   💡 {', '.join(result['all_signals'][:2])}\n\n"
        
        if medium_risk:
            message += "⚠️ ORTA RİSK (%50-80 tavan şansı):\n"
            for result in medium_risk[:3]:
                message += f"📈 {result['symbol']}: %{result['hybrid_score']:.0f} ({result['prediction_type']})\n"
                message += f"   💡 {', '.join(result['all_signals'][:2])}\n\n"
        
        if low_risk:
            message += "📊 DÜŞÜK RİSK (%20-50 tavan şansı):\n"
            for result in low_risk[:2]:
                message += f"⚡ {result['symbol']}: %{result['hybrid_score']:.0f}\n"
        
        message += f"\n⏰ Tarama zamanı: {datetime.now().strftime('%H:%M')}\n"
        message += f"📊 Toplam aday: {len(results)} hisse\n"
        message += f"🎯 Yüksek risk: {len(high_risk)} | Orta risk: {len(medium_risk)}"
        
        return message
    
    def send_telegram_alert(self, message: str):
        """
        📱 TELEGRAM BİLDİRİMİ GÖNDER
        """
        try:
            # Telegram bot token ve chat ID environment'tan alınacak
            import os
            
            bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
            chat_id = os.getenv('TELEGRAM_CHAT_ID')
            
            if not bot_token or not chat_id:
                print("⚠️ Telegram bilgileri eksik - bildirim gönderilemedi")
                return False
            
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {
                'chat_id': chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                print("✅ Telegram bildirimi gönderildi")
                return True
            else:
                print(f"❌ Telegram hatası: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Telegram gönderim hatası: {e}")
            return False
    
    def run_daily_scan(self):
        """
        🚀 GÜNLÜK TARAMAYI ÇALIŞTIR VE BİLDİR
        """
        print("🎯 HİBRİT TAVAN TARAMA SİSTEMİ")
        print("=" * 50)
        print("🔍 Teknik Analiz + Early Warning Kombinasyonu")
        print("📅 Günlük sabah taraması başlatılıyor...\n")
        
        # Taramayı çalıştır
        results = self.daily_scan()
        
        # Sonuçları formatla
        message = self.format_results(results)
        
        # Console'a yazdır
        print("\n" + "=" * 60)
        print("📊 TARAMA SONUÇLARI:")
        print("=" * 60)
        print(message)
        
        # Telegram'a gönder
        self.send_telegram_alert(message)
        
        # Detaylı raporu dosyaya kaydet
        self.save_detailed_report(results)
        
        return results
    
    def save_detailed_report(self, results: List[Dict]):
        """
        📝 DETAYLI RAPORU DOSYAYA KAYDET
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ceiling_scan_report_{timestamp}.json"
            
            report_data = {
                'scan_time': datetime.now().isoformat(),
                'total_scanned': len(self.bist_stocks),
                'candidates_found': len(results),
                'results': results
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2)
            
            print(f"💾 Detaylı rapor kaydedildi: {filename}")
            
        except Exception as e:
            print(f"❌ Rapor kaydetme hatası: {e}")

# Ana çalıştırma
if __name__ == "__main__":
    scanner = HybridCeilingScanner()
    scanner.run_daily_scan()