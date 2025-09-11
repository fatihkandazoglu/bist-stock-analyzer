#!/usr/bin/env python3
"""
🎯 VOLUME DEVRİMİ TARAMA SİSTEMİ V3.0
=====================================
YENİ VOLUME TEORİSİ:
- Düşük volume = Az satıcı = Kolay yükselir
- Volume percentile analizi
- 3 tip tavan modeli
- Fundamental surprise detection
"""

import yfinance as yf
import talib
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

class VolumeRevolutionScanner:
    def __init__(self):
        self.bist_stocks = [
            'AKBNK', 'GARAN', 'ISCTR', 'YKBNK', 'HALKB', 'VAKBN', 'SISE', 'THYAO', 'BIMAS', 'KOZAL',
            'ASELS', 'KCHOL', 'EREGL', 'PETKM', 'TUPRS', 'TCELL', 'SAHOL', 'EKGYO', 'KOZAA', 'GUBRF',
            'TOASO', 'TTKOM', 'FROTO', 'ARCLK', 'AKSA', 'KRDMD', 'TAVHL', 'PGSUS', 'MGROS', 'VESTL',
            'SOKM', 'BRMEN', 'SAMAT', 'EKIZ', 'KAPLM', 'MRSHL', 'EUKYO', 'ICBCT', 'SAFKR', 'BARMA',
            'TEKTU', 'YGYO', 'PKART', 'TURGG', 'YESIL', 'BURVA', 'ADEL', 'AEFES', 'AFYON', 'AGESA',
            'AGHOL', 'AGROT', 'AHGAZ', 'AKENR', 'AKGRT', 'AKMGY', 'ALARK', 'ALBRK', 'ALKIM',
            'ASUZU', 'ATEKS', 'AVGYO', 'AVHOL', 'AVTUR', 'AYDEM', 'AYEN', 'BAGFS', 'BAHKM',
            'BAKAB', 'BANVT', 'BASCM', 'BASGZ', 'BAYRK', 'BERA', 'BEYAZ', 'BIGCH', 'BINHO',
            'BIOEN', 'BIZIM', 'BJKAS', 'BLCYT', 'BNTAS', 'BOBET', 'BORLS', 'BOSSA', 'BRISA',
            'BRKSN', 'BRKVY', 'BSOKE', 'BTCIM', 'BUCIM', 'BURCE', 'CCOLA', 'CEMAS', 'CEMTS',
            'CIMSA', 'CLEBI', 'CMBTN', 'CMENT', 'CONSE', 'COSMO', 'CRDFA', 'CRFSA', 'CUSAN',
            'CVKMD', 'CWENE', 'DAGI', 'DAPGM', 'DARDL', 'DENGE', 'DERHL', 'DERIM', 'DESA',
            'DESPC', 'DEVA', 'DGATE', 'DGNMO', 'DITAS', 'DMSAS', 'DOCO', 'DOGUB', 'DOHOL',
            'DURDO', 'DYOBY', 'DZGYO', 'ECILC', 'ECZYT', 'EGEEN', 'EGGUB', 'EGPRO', 'EGSER',
            'EKSUN', 'ELITE', 'EMKEL', 'EMNIS', 'ENERY', 'ENJSA', 'ENKAI', 'ERBOS', 'ERSU',
            'ESCAR', 'EUREN', 'EUYO', 'EYGYO', 'FENER', 'FLAP', 'FMIZP', 'FONET', 'FORMT',
            'FORTE', 'FRIGO', 'GEDIK', 'GEDZA', 'GENIL', 'GENTS', 'GEREL', 'GESAN', 'GIPTA',
            'GLBMD', 'GLYHO', 'GMTAS', 'GOKNR', 'GOLTS', 'GOODY', 'GOZDE', 'GRNYO', 'GRSEL',
            'GSDDE', 'GSDHO', 'GSRAY', 'GWIND', 'HATEK', 'HATSN', 'HDFGS', 'HEDEF', 'HEKTS',
            'HURGZ', 'HUNER', 'IDGYO', 'IEYHO', 'IHEVA', 'IHGZT', 'IHLAS', 'IHLGM', 'IHYAY',
            'IMASM', 'INDES', 'INFO', 'INTEM', 'INVES', 'IPEKE', 'ISBIR', 'ISBTR', 'ISGSY',
            'ISKUR', 'ISMEN', 'IZENR', 'IZFAS', 'IZINV', 'JANTS', 'KAREL', 'KARSN', 'KARTN',
            'KATMR', 'KAYSE', 'KENT', 'KERVN', 'KFEIN', 'KGYO', 'KIMMR', 'KLGYO', 'KLKIM',
            'KLNMA', 'KLRHO', 'KLSER', 'KLSYN', 'KMPUR', 'KNFRT', 'KONKA', 'KONTR', 'KONYA',
            'KOPOL', 'KORDS', 'KOTON', 'KRDMA', 'KRDMB', 'KRGYO', 'KRONT', 'KRPLS', 'KRSTL',
            'KRTEK', 'KRVGD', 'KSTUR', 'KUTPO', 'KZBGY', 'LIDER', 'LIDFA', 'LILAK', 'LINK',
            'LKMNH', 'LOGO', 'LRSHO', 'LUKSK', 'MACKO', 'MAKIM', 'MAKTK', 'MANAS', 'MARBL',
            'MARKA', 'MEDTR', 'MEGAP', 'MEPET', 'MERCN', 'MERKO', 'METRO', 'MHRGY', 'MMCAS',
            'MNDTR', 'MOBTL', 'MPARK', 'MSGYO', 'MTRKS', 'MTRYO', 'MZHLD', 'NATEN', 'NETAS',
            'NIBAS', 'NUGYO', 'NUHCM', 'ODAS', 'OFSYM', 'ONCSM', 'ORCAY', 'ORMA', 'OSTIM',
            'OTKAR', 'OYAKC', 'OYYAT', 'OZGYO', 'OZKGY', 'OZRDN', 'OZSUB', 'PAPIL', 'PARSN',
            'PASEU', 'PATEK', 'PCILT', 'PEKGY', 'PENGD', 'PENTA', 'PETUN', 'PINSU', 'PKART',
            'PKENT', 'PLTUR', 'PNLSN', 'POLHO', 'POLTK', 'PRDGS', 'PRKAB', 'PRKME', 'PRZMA',
            'PSDTC', 'QUAGR', 'RALYH', 'RAYSG', 'RNPOL', 'RODRG', 'ROYAL', 'RUBNS', 'RYGYO',
            'SANEL', 'SANFM', 'SANKO', 'SARKY', 'SASA', 'SAYAS', 'SEKFK', 'SEKUR', 'SELEC',
            'SELGD', 'SELVA', 'SEYKM', 'SILVR', 'SKBNK', 'SKYLP', 'SMART', 'SMRTG', 'SNKRN',
            'SONME', 'SRVGY', 'SUMAS', 'SUNTK', 'SUWEN', 'TARKM', 'TATEN', 'TBORG', 'TDGYO',
            'TERA', 'TEZOL', 'TMSN', 'TRCAS', 'TRGYO', 'TRILC', 'TSGYO', 'TSKB', 'TTRAK',
            'TUCLK', 'TUKAS', 'TURGG', 'ULUUN', 'ULUSE', 'ULUFA', 'UMPAS', 'UNLU', 'USAK',
            'VAKKO', 'VANGD', 'VBTYZ', 'VERUS', 'VESBE', 'VKGYO', 'VKING', 'VRGYO', 'YAPRK',
            'YATAS', 'YAYLA', 'YGGYO', 'YKSLN', 'YUNSA', 'ZEDUR', 'ZOREN', 'ZRGYO'
        ]
    
    def analyze_revolutionary_volume(self, volume_data: np.array) -> Dict:
        """
        🎯 DEVRİMCİ VOLUME ANALİZİ
        Volume percentile + 3 tip tavan modeli
        """
        if len(volume_data) < 10:
            return {'score': 0, 'signals': ['Yetersiz volume verisi'], 'type': 'UNKNOWN'}
        
        # Volume percentile hesapla (son 15 gün içinde bugünün yeri)
        current_volume = volume_data[-1]
        volume_percentile = (np.sum(volume_data <= current_volume) / len(volume_data)) * 100
        
        # Ortalama volume
        avg_volume = np.mean(volume_data[:-1])
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 0
        
        score = 0
        signals = []
        volume_type = ""
        
        # YENİ VOLUME TEORİSİ - 3 TİP TAVAN MODELİ
        if volume_percentile <= 20:  # DÜŞÜK VOLUME = AZ SATICI
            score += 4  # Büyük bonus!
            volume_type = "LOW_VOLUME_BREAKOUT"
            signals.append(f'Az satıcı avantajı (percentile %{volume_percentile:.0f})')
            signals.append(f'Düşük volume patlaması ({volume_ratio:.1f}x)')
            
        elif volume_percentile >= 80:  # YÜKSEK VOLUME = ÇOK ALICI
            score += 5  # En büyük bonus!
            volume_type = "HIGH_VOLUME_SURGE"
            signals.append(f'Çok alıcı patlaması (percentile %{volume_percentile:.0f})')
            signals.append(f'Yüksek volume hücumu ({volume_ratio:.1f}x)')
            
        elif 40 <= volume_percentile <= 60:  # ORTA VOLUME = BELİRSİZLİK
            score -= 1  # Ceza
            volume_type = "UNCERTAIN_VOLUME"
            signals.append(f'Belirsiz volume bölgesi (percentile %{volume_percentile:.0f})')
            
        else:  # NORMAL VOLUME
            score += 1
            volume_type = "NORMAL_VOLUME"
            signals.append(f'Normal volume seviyesi (percentile %{volume_percentile:.0f})')
        
        # Volume süreklilik kontrolü (eski sistemden)
        spike_days = 0
        for i in range(-7, 0):
            if len(volume_data) > abs(i) and volume_data[i] / avg_volume >= 1.5:
                spike_days += 1
        
        if spike_days >= 3:
            score += 2
            signals.append(f'Volume süreklilik ({spike_days}/7 gün)')
        
        return {
            'score': score,
            'signals': signals,
            'type': volume_type,
            'percentile': volume_percentile,
            'ratio': volume_ratio,
            'spike_days': spike_days
        }
    
    def detect_fundamental_surprise(self, symbol: str) -> Dict:
        """
        💥 FUNDAMENTAL SURPRISE TESPİTİ
        TEKTU tarzı dramatik değişimler
        """
        try:
            ticker = yf.Ticker(f"{symbol}.IS")
            info = ticker.info
            
            score = 0
            signals = []
            
            # Sektör bonusları (TEKTU ve YGYO'dan öğrendim)
            sector = info.get('sector', 'Unknown')
            industry = info.get('industry', 'Unknown')
            
            if 'Real Estate' in sector:
                score += 2
                signals.append('REIT spekülasyon potansiyeli')
                
            if 'Consumer Cyclical' in sector:
                score += 1
                signals.append('Recovery sektörü avantajı')
                
            if 'Technology' in sector or 'Technology' in industry:
                score += 1
                signals.append('Tech momentum potansiyeli')
            
            # Küçük şirket spekülasyon bonusu (YGYO'dan öğrendim)
            market_cap = info.get('marketCap', 0)
            if 500_000_000 <= market_cap <= 5_000_000_000:  # 500M - 5B TL
                score += 1
                signals.append('Orta boy spekülasyon fırsatı')
            
            return {'score': score, 'signals': signals}
            
        except:
            return {'score': 0, 'signals': []}
    
    def revolutionary_scan(self, symbol: str) -> Dict:
        """
        🎯 DEVRİMCİ TARAMA SİSTEMİ
        """
        try:
            ticker = yf.Ticker(f"{symbol}.IS")
            data = ticker.history(period='20d')
            
            if len(data) < 15:
                return {'score': 0, 'signals': ['Yetersiz veri'], 'error': 'Insufficient data'}
            
            close = np.array(data['Close'].values, dtype=np.float64)
            volume = np.array(data['Volume'].values, dtype=np.float64)
            
            # Devrimci volume analizi
            volume_analysis = self.analyze_revolutionary_volume(volume)
            
            # Fundamental surprise
            surprise_analysis = self.detect_fundamental_surprise(symbol)
            
            # Momentum analizi (eski sistemden)
            momentum_score = 0
            momentum_signals = []
            
            # Son 7 günde büyük hareket sayısı
            big_moves = 0
            for i in range(-7, 0):
                if len(close) > abs(i) and len(close) > abs(i-1):
                    daily_change = abs((close[i] - close[i-1]) / close[i-1]) * 100
                    if daily_change >= 5:
                        big_moves += 1
            
            if big_moves >= 4:
                momentum_score = 4
                momentum_signals.append(f'Momentum makinesi ({big_moves}/7 gün)')
            elif big_moves >= 2:
                momentum_score = 2
                momentum_signals.append(f'Güçlü momentum ({big_moves}/7 gün)')
            else:
                momentum_score = 0
                momentum_signals.append(f'Zayıf momentum ({big_moves}/7 gün)')
            
            # Basit teknik skorlar
            rsi = talib.RSI(close, timeperiod=14)
            rsi_score = 1 if len(rsi) > 0 and 30 <= rsi[-1] <= 70 else 0
            
            # TOPLAM SKOR (yeni ağırlıklar)
            total_score = (
                volume_analysis['score'] * 0.40 +      # %40 - Volume devrim!
                momentum_score * 0.30 +               # %30 - Momentum
                surprise_analysis['score'] * 0.20 +   # %20 - Fundamental
                rsi_score * 0.10                      # %10 - Technical
            )
            
            # Risk kategorisi
            if total_score >= 7:
                risk_level = 'DEVRİMCİ'
                ceiling_chance = '>= 90%'
            elif total_score >= 5:
                risk_level = 'YÜKSEK'
                ceiling_chance = '>= 80%'
            elif total_score >= 3:
                risk_level = 'ORTA'
                ceiling_chance = '50-80%'
            elif total_score >= 1.5:
                risk_level = 'DÜŞÜK'
                ceiling_chance = '20-50%'
            else:
                risk_level = 'MİNİMAL'
                ceiling_chance = '< 20%'
            
            # Tüm sinyaller
            all_signals = volume_analysis['signals'] + momentum_signals + surprise_analysis['signals']
            
            return {
                'symbol': symbol,
                'total_score': total_score,
                'risk_level': risk_level,
                'ceiling_chance': ceiling_chance,
                'volume_analysis': volume_analysis,
                'momentum_score': momentum_score,
                'surprise_score': surprise_analysis['score'],
                'all_signals': all_signals,
                'current_price': close[-1],
                'volume_type': volume_analysis['type']
            }
            
        except Exception as e:
            return {'score': 0, 'signals': [], 'error': str(e)}

# Test çalıştır
if __name__ == "__main__":
    scanner = VolumeRevolutionScanner()
    
    # Bugün başarılı olan + test hisseleri
    test_stocks = ['TEKTU', 'YGYO', 'KAPLM', 'EKIZ', 'PKART', 'TURGG', 'AKBNK', 'GARAN', 'THYAO']
    
    print("🎯 DEVRİMCİ VOLUME TEORİSİ TEST")
    print("=" * 50)
    
    for symbol in test_stocks:
        result = scanner.revolutionary_scan(symbol)
        if 'error' not in result:
            volume_type = result.get('volume_type', 'UNKNOWN')
            score = result.get('total_score', 0)
            risk = result.get('risk_level', 'UNKNOWN')
            print(f"{symbol}: {score:.1f} puan - {risk} ({volume_type})")
        else:
            print(f"{symbol}: HATA")