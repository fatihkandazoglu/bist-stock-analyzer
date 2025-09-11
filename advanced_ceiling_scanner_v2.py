#!/usr/bin/env python3
"""
🎯 GELİŞTİRİLMİŞ TAVAN YAKALAMA SİSTEMİ V2.0
=============================================
EUKYO hatasından öğrenilenlerle yeni kriterler:
- Şirket büyüklüğü (market cap) kontrolü
- Volume süreklilik analizi
- Momentum makine tipi tanıma
- Çalışan sayısı kontrolü
- Likidite taban analizi
"""

import yfinance as yf
import talib
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import requests
import json

class AdvancedCeilingScanner:
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
    
    def get_company_fundamentals(self, symbol: str) -> Dict:
        """
        🏢 ŞİRKET TEMEL BİLGİLERİNİ ALIR
        """
        try:
            ticker = yf.Ticker(f"{symbol}.IS")
            info = ticker.info
            
            return {
                'market_cap': info.get('marketCap', 0),
                'enterprise_value': info.get('enterpriseValue', 0),
                'employees': info.get('fullTimeEmployees', 0),
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown'),
                'shares_outstanding': info.get('sharesOutstanding', 0),
                'float_shares': info.get('floatShares', 0)
            }
        except:
            return {
                'market_cap': 0, 'enterprise_value': 0, 'employees': 0,
                'sector': 'Unknown', 'industry': 'Unknown',
                'shares_outstanding': 0, 'float_shares': 0
            }
    
    def analyze_volume_continuity(self, volume_data: np.array) -> Dict:
        """
        📊 VOLUME SÜREKLİLİK ANALİZİ
        """
        if len(volume_data) < 7:
            return {'score': 0, 'signals': ['Yetersiz volume verisi']}
        
        # Son 7 günlük ortalama volume
        avg_volume = np.mean(volume_data[:-7]) if len(volume_data) > 14 else np.mean(volume_data[:-1])
        
        # Volume spike günlerini say
        volume_spike_days = 0
        recent_volume_avg = 0
        
        for i in range(-7, 0):
            if len(volume_data) > abs(i):
                daily_volume = volume_data[i]
                recent_volume_avg += daily_volume
                
                if daily_volume / avg_volume >= 1.5:
                    volume_spike_days += 1
        
        recent_volume_avg = recent_volume_avg / 7
        current_volume_ratio = volume_data[-1] / avg_volume if avg_volume > 0 else 0
        
        # Skorlama
        score = 0
        signals = []
        
        # 1. Güncel volume çok yüksek
        if current_volume_ratio >= 3.0:
            score += 4
            signals.append(f'Süper volume ({current_volume_ratio:.1f}x)')
        elif current_volume_ratio >= 2.0:
            score += 3
            signals.append(f'Yüksek volume ({current_volume_ratio:.1f}x)')
        elif current_volume_ratio >= 1.5:
            score += 2
            signals.append(f'Orta volume ({current_volume_ratio:.1f}x)')
        elif current_volume_ratio < 0.5:
            score -= 3  # EUKYO hatası
            signals.append(f'Volume çöktü ({current_volume_ratio:.1f}x)')
        
        # 2. Volume spike süreklilik (KRITIK!)
        if volume_spike_days >= 5:
            score += 4
            signals.append(f'Volume süreklilik mükemmel ({volume_spike_days}/7)')
        elif volume_spike_days >= 3:
            score += 3
            signals.append(f'Volume süreklilik güçlü ({volume_spike_days}/7)')
        elif volume_spike_days >= 2:
            score += 1
            signals.append(f'Volume süreklilik zayıf ({volume_spike_days}/7)')
        else:
            score -= 1
            signals.append(f'Volume süreklilik yok ({volume_spike_days}/7)')
        
        return {
            'score': score,
            'signals': signals,
            'current_ratio': current_volume_ratio,
            'spike_days': volume_spike_days,
            'avg_volume': avg_volume
        }
    
    def analyze_momentum_machine(self, close_data: np.array) -> Dict:
        """
        🚀 MOMENTUM MAKİNESİ ANALİZİ
        3 tip momentum: Sürekli büyük, Volume destekli, Temiz artış
        """
        if len(close_data) < 7:
            return {'score': 0, 'signals': ['Yetersiz fiyat verisi']}
        
        # Son 7 günde büyük hareket günlerini say
        big_move_days = 0
        consecutive_days = 0
        max_consecutive = 0
        daily_changes = []
        
        for i in range(-7, 0):
            if len(close_data) > abs(i) and len(close_data) > abs(i-1):
                daily_change = ((close_data[i] - close_data[i-1]) / close_data[i-1]) * 100
                daily_changes.append(abs(daily_change))
                
                if abs(daily_change) >= 5:  # %5+ hareket
                    big_move_days += 1
                    consecutive_days += 1
                    max_consecutive = max(max_consecutive, consecutive_days)
                else:
                    consecutive_days = 0
        
        # Momentum tipi belirleme
        score = 0
        signals = []
        momentum_type = ""
        
        # TİP 1: MOMENTUM MAKİNESİ (KAPLM, EKIZ tarzı)
        if big_move_days >= 5:
            score += 5
            momentum_type = "MOMENTUM_MACHINE"
            signals.append(f'Momentum makinesi ({big_move_days}/7 büyük gün)')
            
            if max_consecutive >= 3:
                score += 2
                signals.append(f'Sürekli momentum ({max_consecutive} gün peş peşe)')
        
        # TİP 2: GÜÇLÜ MOMENTUM
        elif big_move_days >= 3:
            score += 3
            momentum_type = "STRONG_MOMENTUM"
            signals.append(f'Güçlü momentum ({big_move_days}/7 büyük gün)')
        
        # TİP 3: ORTA MOMENTUM
        elif big_move_days >= 2:
            score += 2
            momentum_type = "MEDIUM_MOMENTUM"
            signals.append(f'Orta momentum ({big_move_days}/7 büyük gün)')
        
        # TİP 4: TEMİZ ARTIŞLAR (PKENT tarzı)
        elif big_move_days <= 1:
            avg_change = np.mean(daily_changes) if daily_changes else 0
            if avg_change <= 3 and avg_change > 1:  # Düşük volatiliteli artış
                score += 2
                momentum_type = "CLEAN_UPTREND"
                signals.append(f'Temiz artış trendi (düşük volatilite)')
        
        # CEZA: Son günde büyük düşüş
        if len(close_data) >= 2:
            last_change = ((close_data[-1] - close_data[-2]) / close_data[-2]) * 100
            if last_change <= -5:
                score -= 2
                signals.append(f'Son günde büyük düşüş ({last_change:.1f}%)')
        
        return {
            'score': score,
            'signals': signals,
            'type': momentum_type,
            'big_move_days': big_move_days,
            'max_consecutive': max_consecutive
        }
    
    def company_size_analysis(self, fundamentals: Dict) -> Dict:
        """
        🏢 ŞİRKET BÜYÜKLÜĞÜ ANALİZİ (EUKYO hatasından öğrendik)
        """
        market_cap = fundamentals.get('market_cap', 0)
        employees = fundamentals.get('employees', 0)
        
        score = 0
        signals = []
        size_category = ""
        
        # Market cap analizi
        if market_cap >= 50_000_000_000:  # 50B TL+
            score += 4
            size_category = "MEGA"
            signals.append(f'Mega şirket ({market_cap/1e9:.1f}B TL)')
        elif market_cap >= 5_000_000_000:  # 5B TL+
            score += 3
            size_category = "LARGE"
            signals.append(f'Büyük şirket ({market_cap/1e9:.1f}B TL)')
        elif market_cap >= 1_000_000_000:  # 1B TL+
            score += 2
            size_category = "MEDIUM"
            signals.append(f'Orta şirket ({market_cap/1e9:.1f}B TL)')
        elif market_cap >= 500_000_000:  # 500M TL+
            score += 0
            size_category = "SMALL_OK"
            signals.append(f'Küçük ama kabul edilebilir ({market_cap/1e6:.0f}M TL)')
        else:  # 500M TL altı
            score -= 3  # EUKYO cezası!
            size_category = "TOO_SMALL"
            signals.append(f'Çok küçük şirket riski ({market_cap/1e6:.0f}M TL)')
        
        # Çalışan sayısı analizi
        if employees >= 1000:
            score += 2
            signals.append(f'Büyük organizasyon ({employees} kişi)')
        elif employees >= 100:
            score += 1
            signals.append(f'Orta organizasyon ({employees} kişi)')
        elif employees > 0 and employees < 50:
            score -= 2  # EUKYO'nun 6 kişi cezası
            signals.append(f'Küçük organizasyon riski ({employees} kişi)')
        
        return {
            'score': score,
            'signals': signals,
            'category': size_category,
            'market_cap_billion': market_cap / 1e9 if market_cap > 0 else 0
        }
    
    def advanced_ceiling_scan(self, symbol: str) -> Dict:
        """
        🎯 GELİŞTİRİLMİŞ TAVAN TARAMASI V2.0
        """
        try:
            # Veri çekme
            ticker = yf.Ticker(f"{symbol}.IS")
            data = ticker.history(period='30d')
            fundamentals = self.get_company_fundamentals(symbol)
            
            if len(data) < 14:
                return {'score': 0, 'signals': ['Yetersiz veri'], 'error': 'Insufficient data'}
            
            close = np.array(data['Close'].values, dtype=np.float64)
            high = np.array(data['High'].values, dtype=np.float64)
            low = np.array(data['Low'].values, dtype=np.float64)
            volume = np.array(data['Volume'].values, dtype=np.float64)
            
            # Analizler
            volume_analysis = self.analyze_volume_continuity(volume)
            momentum_analysis = self.analyze_momentum_machine(close)
            size_analysis = self.company_size_analysis(fundamentals)
            
            # Temel teknik analiz (RSI, MACD vb.)
            rsi = talib.RSI(close, timeperiod=14)
            macd, macd_signal, macd_hist = talib.MACD(close)
            bb_upper, bb_middle, bb_lower = talib.BBANDS(close)
            
            # RSI momentum (5 günlük)
            rsi_momentum = 0
            if len(rsi) >= 6:
                rsi_momentum = rsi[-2] - rsi[-6]
            
            rsi_score = 0
            if rsi_momentum >= 15:
                rsi_score = 3
            elif rsi_momentum >= 10:
                rsi_score = 2
            elif rsi_momentum >= 5:
                rsi_score = 1
            
            # Direnç yakınlığı
            recent_high = np.max(high[-20:])
            yesterday_close = close[-2]
            resistance_proximity = (yesterday_close / recent_high) * 100
            
            resistance_score = 0
            if resistance_proximity >= 98:
                resistance_score = 3
            elif resistance_proximity >= 95:
                resistance_score = 2
            elif resistance_proximity >= 90:
                resistance_score = 1
            
            # TOPLAM SKOR HESAPLAMA
            total_score = (
                volume_analysis['score'] * 0.35 +      # %35 - Volume en önemli
                momentum_analysis['score'] * 0.30 +    # %30 - Momentum çok önemli  
                size_analysis['score'] * 0.20 +        # %20 - Şirket büyüklüğü kritik
                rsi_score * 0.10 +                     # %10 - RSI
                resistance_score * 0.05                # %5 - Direnç
            )
            
            # Risk seviyesi
            if total_score >= 8:
                risk_level = 'SÜPER YÜKSEK'
                ceiling_probability = '>= 90%'
            elif total_score >= 6:
                risk_level = 'YÜKSEK'
                ceiling_probability = '>= 80%'
            elif total_score >= 4:
                risk_level = 'ORTA'
                ceiling_probability = '50-80%'
            elif total_score >= 2:
                risk_level = 'DÜŞÜK'
                ceiling_probability = '20-50%'
            else:
                risk_level = 'MİNİMAL'
                ceiling_probability = '< 20%'
            
            # Tüm sinyalleri topla
            all_signals = (
                volume_analysis['signals'] + 
                momentum_analysis['signals'] + 
                size_analysis['signals']
            )
            
            if rsi_momentum >= 5:
                all_signals.append(f'RSI momentum +{rsi_momentum:.1f}')
            if resistance_proximity >= 90:
                all_signals.append(f'Direnç yakın %{resistance_proximity:.1f}')
            
            return {
                'symbol': symbol,
                'total_score': total_score,
                'risk_level': risk_level,
                'ceiling_probability': ceiling_probability,
                'fundamentals': fundamentals,
                'volume_analysis': volume_analysis,
                'momentum_analysis': momentum_analysis,
                'size_analysis': size_analysis,
                'rsi_momentum': rsi_momentum,
                'resistance_proximity': resistance_proximity,
                'all_signals': all_signals,
                'current_price': close[-1]
            }
            
        except Exception as e:
            return {'score': 0, 'signals': [], 'error': str(e)}
    
    def daily_advanced_scan(self) -> List[Dict]:
        """
        🌅 GELİŞTİRİLMİŞ GÜNLÜK TARAMA
        """
        results = []
        scan_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"🎯 GELİŞTİRİLMİŞ TAVAN TARAMASI V2.0 BAŞLADI: {scan_time}")
        print("=" * 70)
        
        for i, symbol in enumerate(self.bist_stocks):
            try:
                result = self.advanced_ceiling_scan(symbol)
                
                # Minimum skor 2.0
                if result.get('total_score', 0) >= 2.0:
                    results.append(result)
                
                # İlerleme
                if (i + 1) % 50 == 0:
                    print(f"⏳ {i + 1}/{len(self.bist_stocks)} hisse tarandı...")
                    
            except Exception as e:
                print(f"❌ {symbol} hata: {e}")
                continue
        
        # Skoruna göre sırala
        results.sort(key=lambda x: x.get('total_score', 0), reverse=True)
        
        return results
    
    def format_results(self, results: List[Dict]) -> str:
        """
        📊 SONUÇLARI FORMATLA
        """
        if not results:
            return "❌ Kriterlerimize uygun hisse bulunamadı."
        
        message = "🎯 GELİŞTİRİLMİŞ TAVAN ADAYLARI V2.0\n"
        message += "="*50 + "\n\n"
        
        # Yüksek risk adayları
        high_risk = [r for r in results if r.get('total_score', 0) >= 6]
        if high_risk:
            message += "🚨 SÜPER & YÜKSEK RİSK (≥80% şans):\n"
            for result in high_risk[:5]:
                symbol = result['symbol']
                score = result.get('total_score', 0)
                risk = result.get('risk_level', 'UNKNOWN')
                price = result.get('current_price', 0)
                size_cat = result.get('size_analysis', {}).get('category', 'UNKNOWN')
                momentum_type = result.get('momentum_analysis', {}).get('type', 'UNKNOWN')
                
                message += f"🎯 {symbol}: {score:.1f} puan ({risk})\n"
                message += f"   💰 Fiyat: {price:.2f} TL\n"
                message += f"   🏢 Boyut: {size_cat}\n"
                message += f"   🚀 Momentum: {momentum_type}\n"
                
                # En önemli sinyaller
                top_signals = result.get('all_signals', [])[:3]
                for signal in top_signals:
                    message += f"   💡 {signal}\n"
                message += "\n"
        
        # Orta risk adayları
        medium_risk = [r for r in results if 4 <= r.get('total_score', 0) < 6]
        if medium_risk:
            message += "⚠️ ORTA RİSK (%50-80 şans):\n"
            for result in medium_risk[:3]:
                symbol = result['symbol']
                score = result.get('total_score', 0)
                message += f"📈 {symbol}: {score:.1f} puan\n"
        
        # Özet bilgiler
        message += f"\n⏰ Tarama zamanı: {datetime.now().strftime('%H:%M')}\n"
        message += f"📊 Toplam aday: {len(results)} hisse\n"
        message += f"🎯 Yüksek risk: {len(high_risk)} | Orta risk: {len(medium_risk)}\n"
        message += "✅ Geliştirilmiş algoritma ile taranmıştır"
        
        return message

# Test için
if __name__ == "__main__":
    scanner = AdvancedCeilingScanner()
    
    # Birkaç test hissesi
    test_stocks = ['EKIZ', 'KAPLM', 'MRSHL', 'EUKYO', 'PKENT']
    
    print("🧪 TEST TARAMASI")
    print("=" * 40)
    
    for symbol in test_stocks:
        result = scanner.advanced_ceiling_scan(symbol)
        if 'error' not in result:
            print(f"{symbol}: {result.get('total_score', 0):.1f} puan - {result.get('risk_level', 'UNKNOWN')}")
        else:
            print(f"{symbol}: HATA - {result.get('error', 'Unknown')}")