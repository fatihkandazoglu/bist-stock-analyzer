# GitHub Codespaces'e Dosya Yükleme

## Yöntem 1: Direkt Dosya Oluştur
Her bir Python dosyasını Codespaces'de oluştur:

```bash
# Ana tarayıcı sistemi
cat > volume_revolution_scanner.py << 'EOF'
#!/usr/bin/env python3
"""
🎯 VOLUME DEVRİMİ TARAMA SİSTEMİ V3.0
=====================================
YENİ VOLUME TEORİSİ:
- Düşük volume = Az satıcı = Kolay yükselir
- Volume percentile analizi
- 3 tip tavan modeli
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
            'SAMAT', 'EKIZ', 'KAPLM', 'MRSHL', 'EUKYO', 'ICBCT', 'SAFKR', 'BARMA'
        ]
    
    def analyze_revolutionary_volume(self, volume_data: np.array) -> Dict:
        """🎯 DEVRİMCİ VOLUME ANALİZİ"""
        if len(volume_data) < 10:
            return {'score': 0, 'signals': ['Yetersiz volume verisi'], 'type': 'UNKNOWN'}
        
        current_volume = volume_data[-1]
        volume_percentile = (np.sum(volume_data <= current_volume) / len(volume_data)) * 100
        avg_volume = np.mean(volume_data[:-1])
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 0
        
        score = 0
        signals = []
        volume_type = ""
        
        # YENİ VOLUME TEORİSİ - 3 TİP TAVAN MODELİ
        if volume_percentile <= 20:  # DÜŞÜK VOLUME = AZ SATICI
            score += 4
            volume_type = "LOW_VOLUME_BREAKOUT"
            signals.append(f'Az satıcı avantajı (percentile %{volume_percentile:.0f})')
            
        elif volume_percentile >= 80:  # YÜKSEK VOLUME = ÇOK ALICI
            score += 5
            volume_type = "HIGH_VOLUME_SURGE"
            signals.append(f'Çok alıcı patlaması (percentile %{volume_percentile:.0f})')
            
        else:
            score += 1
            volume_type = "NORMAL_VOLUME"
            signals.append(f'Normal volume seviyesi (percentile %{volume_percentile:.0f})')
        
        return {
            'score': score,
            'signals': signals,
            'type': volume_type,
            'percentile': volume_percentile,
            'ratio': volume_ratio
        }
    
    def revolutionary_scan(self, symbol: str) -> Dict:
        """🎯 DEVRİMCİ TARAMA SİSTEMİ"""
        try:
            ticker = yf.Ticker(f"{symbol}.IS")
            data = ticker.history(period='20d')
            
            if len(data) < 15:
                return {'score': 0, 'signals': ['Yetersiz veri'], 'error': 'Insufficient data'}
            
            close = np.array(data['Close'].values, dtype=np.float64)
            volume = np.array(data['Volume'].values, dtype=np.float64)
            
            # Devrimci volume analizi
            volume_analysis = self.analyze_revolutionary_volume(volume)
            
            # Momentum analizi
            big_moves = sum(1 for i in range(-7, 0) 
                           if len(close) > abs(i) and len(close) > abs(i-1) 
                           and abs((close[i] - close[i-1]) / close[i-1]) * 100 >= 5)
            
            momentum_score = 4 if big_moves >= 4 else 2 if big_moves >= 2 else 0
            
            # RSI
            rsi = talib.RSI(close, timeperiod=14)
            rsi_score = 1 if len(rsi) > 0 and 30 <= rsi[-1] <= 70 else 0
            
            # TOPLAM SKOR
            total_score = (
                volume_analysis['score'] * 0.40 +      # %40 - Volume devrim!
                momentum_score * 0.30 +               # %30 - Momentum
                rsi_score * 0.30                      # %30 - Technical
            )
            
            return {
                'symbol': symbol,
                'total_score': total_score,
                'volume_analysis': volume_analysis,
                'current_price': close[-1],
                'volume_type': volume_analysis['type']
            }
            
        except Exception as e:
            return {'score': 0, 'signals': [], 'error': str(e)}

# Test çalıştır
if __name__ == "__main__":
    scanner = VolumeRevolutionScanner()
    test_stocks = ['SAMAT', 'EKIZ', 'KAPLM']
    
    for symbol in test_stocks:
        result = scanner.revolutionary_scan(symbol)
        if 'error' not in result:
            print(f"{symbol}: {result.get('total_score', 0):.1f} puan")
EOF

# Requirements dosyası
cat > requirements.txt << 'EOF'
yfinance>=0.2.0
pandas>=1.5.0
numpy>=1.24.0
ta>=0.10.0
TA-Lib>=0.4.0
python-telegram-bot>=20.0
schedule>=1.2.0
requests>=2.28.0
python-dotenv>=1.0.0
EOF

# Git'e ekle ve commit et
git add .
git commit -m "Add BIST Stock Analysis System - Volume Revolution Scanner"
git push
```

## Yöntem 2: Dosya Yükleme
Codespaces'de sol panelde dosya yükleyebilirsin.