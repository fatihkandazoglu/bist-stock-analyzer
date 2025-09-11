#!/usr/bin/env python3
"""
Teknik Analiz Modülü
Bu modül hisse senetleri için teknik analiz göstergelerini hesaplar.
"""

import pandas as pd
import numpy as np
import ta
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class TechnicalAnalyzer:
    def __init__(self):
        """Teknik analiz sınıfını başlat"""
        self.indicators = {}
    
    def calculate_rsi(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """RSI (Relative Strength Index) hesapla"""
        return ta.momentum.RSIIndicator(close=data['Close'], window=period).rsi()
    
    def calculate_macd(self, data: pd.DataFrame) -> Dict[str, pd.Series]:
        """MACD hesapla"""
        macd_indicator = ta.trend.MACD(close=data['Close'])
        return {
            'macd': macd_indicator.macd(),
            'signal': macd_indicator.macd_signal(),
            'histogram': macd_indicator.macd_diff()
        }
    
    def calculate_bollinger_bands(self, data: pd.DataFrame, period: int = 20) -> Dict[str, pd.Series]:
        """Bollinger Bands hesapla"""
        bb_indicator = ta.volatility.BollingerBands(close=data['Close'], window=period)
        return {
            'upper': bb_indicator.bollinger_hband(),
            'middle': bb_indicator.bollinger_mavg(),
            'lower': bb_indicator.bollinger_lband()
        }
    
    def calculate_moving_averages(self, data: pd.DataFrame) -> Dict[str, pd.Series]:
        """Hareketli ortalamalar hesapla"""
        return {
            'sma_5': ta.trend.SMAIndicator(close=data['Close'], window=5).sma_indicator(),
            'sma_10': ta.trend.SMAIndicator(close=data['Close'], window=10).sma_indicator(),
            'sma_20': ta.trend.SMAIndicator(close=data['Close'], window=20).sma_indicator(),
            'ema_12': ta.trend.EMAIndicator(close=data['Close'], window=12).ema_indicator(),
            'ema_26': ta.trend.EMAIndicator(close=data['Close'], window=26).ema_indicator()
        }
    
    def calculate_volume_indicators(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Hacim göstergelerini hesapla"""
        # Basit hacim ortalaması
        volume_sma = data['Volume'].rolling(window=20).mean()
        volume_sma_5 = data['Volume'].rolling(window=5).mean()
        
        # On Balance Volume
        obv = ta.volume.OnBalanceVolumeIndicator(close=data['Close'], volume=data['Volume']).on_balance_volume()
        
        # Volume Price Trend  
        vpt = ta.volume.VolumePriceTrendIndicator(close=data['Close'], volume=data['Volume']).volume_price_trend()
        
        # Money Flow Index
        mfi = ta.volume.MFIIndicator(high=data['High'], low=data['Low'], close=data['Close'], volume=data['Volume']).money_flow_index()
        
        # Volume momentum - YENİ!
        current_vol = data['Volume'].iloc[-1] if len(data) > 0 else 0
        avg_vol_20 = data['Volume'].rolling(window=20).mean().iloc[-1] if len(data) >= 20 else 1
        avg_vol_5 = data['Volume'].rolling(window=5).mean().iloc[-1] if len(data) >= 5 else 1
        
        # Volume spike detection - YENİ!
        volume_ratio_20 = current_vol / avg_vol_20 if avg_vol_20 > 0 else 1
        volume_ratio_5 = current_vol / avg_vol_5 if avg_vol_5 > 0 else 1
        
        # 2-3 günlük volume momentum - YENİ!
        if len(data) >= 3:
            yesterday_vol = data['Volume'].iloc[-2]
            day_before_vol = data['Volume'].iloc[-3]
            avg_recent = (yesterday_vol + day_before_vol) / 2
            recent_volume_momentum = yesterday_vol / avg_recent if avg_recent > 0 else 1
        else:
            recent_volume_momentum = 1
        
        return {
            'volume_sma': volume_sma,
            'volume_sma_5': volume_sma_5,
            'obv': obv,
            'vpt': vpt,
            'mfi': mfi,
            'current_volume': current_vol,
            'avg_volume_20': avg_vol_20,
            'avg_volume_5': avg_vol_5,
            'volume_ratio_20': volume_ratio_20,
            'volume_ratio_5': volume_ratio_5,
            'recent_volume_momentum': recent_volume_momentum,
            'volume_spike_alert': volume_ratio_20 > 2.0 or volume_ratio_5 > 1.8
        }
    
    def calculate_momentum_indicators(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Momentum göstergelerini hesapla"""
        # Stochastic Oscillator
        stoch = ta.momentum.StochasticOscillator(high=data['High'], low=data['Low'], close=data['Close'])
        
        # Williams %R
        williams_r = ta.momentum.WilliamsRIndicator(high=data['High'], low=data['Low'], close=data['Close']).williams_r()
        
        # Rate of Change
        roc = ta.momentum.ROCIndicator(close=data['Close']).roc()
        
        # Stochastic RSI - YENİ!
        stoch_rsi = ta.momentum.StochRSIIndicator(close=data['Close']).stochrsi()
        
        # Price momentum - YENİ!
        if len(data) >= 3:
            current_price = data['Close'].iloc[-1]
            yesterday_price = data['Close'].iloc[-2]
            day_before_price = data['Close'].iloc[-3]
            
            # 1 günlük değişim
            daily_change = ((current_price - yesterday_price) / yesterday_price * 100) if yesterday_price > 0 else 0
            # 2 günlük değişim  
            two_day_change = ((current_price - day_before_price) / day_before_price * 100) if day_before_price > 0 else 0
            # Momentum devamı sinyali
            momentum_continuation = (yesterday_price > day_before_price) and (current_price > yesterday_price)
        else:
            daily_change = 0
            two_day_change = 0
            momentum_continuation = False
        
        # 5-10-20 günlük momentum - YENİ!
        momentum_5d = ((data['Close'].iloc[-1] - data['Close'].iloc[-6]) / data['Close'].iloc[-6] * 100) if len(data) > 5 else 0
        momentum_10d = ((data['Close'].iloc[-1] - data['Close'].iloc[-11]) / data['Close'].iloc[-11] * 100) if len(data) > 10 else 0
        momentum_20d = ((data['Close'].iloc[-1] - data['Close'].iloc[-21]) / data['Close'].iloc[-21] * 100) if len(data) > 20 else 0
        
        return {
            'stoch_k': stoch.stoch(),
            'stoch_d': stoch.stoch_signal(),
            'stoch_rsi': stoch_rsi,
            'williams_r': williams_r,
            'roc': roc,
            'daily_change': daily_change,
            'two_day_change': two_day_change,
            'momentum_5d': momentum_5d,
            'momentum_10d': momentum_10d,
            'momentum_20d': momentum_20d,
            'momentum_continuation': momentum_continuation
        }
    
    def analyze_stock(self, symbol: str, data: pd.DataFrame) -> Dict[str, Any]:
        """Hisse senedi için kapsamlı teknik analiz"""
        if data.empty or len(data) < 20:
            logger.warning(f"{symbol} için yeterli veri yok")
            return {}
        
        try:
            analysis = {
                'symbol': symbol,
                'last_price': data['Close'].iloc[-1],
                'price_change_1d': ((data['Close'].iloc[-1] - data['Close'].iloc[-2]) / data['Close'].iloc[-2] * 100) if len(data) > 1 else 0,
                'price_change_5d': ((data['Close'].iloc[-1] - data['Close'].iloc[-6]) / data['Close'].iloc[-6] * 100) if len(data) > 5 else 0,
            }
            
            # RSI analizi
            rsi = self.calculate_rsi(data)
            analysis['rsi'] = rsi.iloc[-1] if not rsi.empty else None
            analysis['rsi_signal'] = self._interpret_rsi(rsi.iloc[-1]) if not rsi.empty else 'neutral'
            
            # MACD analizi
            macd_data = self.calculate_macd(data)
            if not macd_data['macd'].empty:
                analysis['macd'] = macd_data['macd'].iloc[-1]
                analysis['macd_signal'] = macd_data['signal'].iloc[-1]
                analysis['macd_histogram'] = macd_data['histogram'].iloc[-1]
                analysis['macd_trend'] = self._interpret_macd(macd_data['macd'].iloc[-1], macd_data['signal'].iloc[-1])
            
            # Bollinger Bands
            bb = self.calculate_bollinger_bands(data)
            if not bb['upper'].empty:
                current_price = data['Close'].iloc[-1]
                analysis['bb_position'] = self._interpret_bollinger_position(current_price, bb)
            
            # Hareketli ortalamalar
            ma = self.calculate_moving_averages(data)
            analysis['ma_signals'] = self._interpret_moving_averages(data['Close'].iloc[-1], ma)
            
            # Hacim analizi
            volume_data = self.calculate_volume_indicators(data)
            analysis['volume_analysis'] = self._interpret_volume(volume_data)
            
            # Momentum göstergeleri
            momentum = self.calculate_momentum_indicators(data)
            analysis['momentum_signals'] = self._interpret_momentum(momentum)
            
            # YENİ! Pattern recognition analizi
            analysis['pattern_signals'] = self._detect_patterns(data, analysis)
            
            # YENİ! Market cap ve volatilite analizi
            analysis['market_characteristics'] = self._analyze_market_characteristics(data, symbol)
            
            # Genel skor hesaplama
            analysis['technical_score'] = self._calculate_technical_score(analysis)
            
            # YENİ! Ceiling potential skorlaması
            analysis['ceiling_potential'] = self._calculate_ceiling_potential(analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"{symbol} teknik analiz hatası: {e}")
            return {}
    
    def _interpret_rsi(self, rsi_value: float) -> str:
        """RSI değerini yorumla"""
        if rsi_value is None:
            return 'neutral'
        if rsi_value > 70:
            return 'overbought'
        elif rsi_value < 30:
            return 'oversold'
        elif rsi_value > 50:
            return 'bullish'
        else:
            return 'bearish'
    
    def _interpret_macd(self, macd: float, signal: float) -> str:
        """MACD sinyalini yorumla"""
        if macd > signal:
            return 'bullish'
        else:
            return 'bearish'
    
    def _interpret_bollinger_position(self, price: float, bb: Dict) -> str:
        """Bollinger Bands pozisyonunu yorumla"""
        upper = bb['upper'].iloc[-1]
        lower = bb['lower'].iloc[-1]
        middle = bb['middle'].iloc[-1]
        
        if price > upper:
            return 'above_upper'
        elif price < lower:
            return 'below_lower'
        elif price > middle:
            return 'above_middle'
        else:
            return 'below_middle'
    
    def _interpret_moving_averages(self, current_price: float, ma: Dict) -> Dict[str, str]:
        """Hareketli ortalama sinyallerini yorumla"""
        signals = {}
        
        for ma_name, ma_series in ma.items():
            if not ma_series.empty:
                ma_value = ma_series.iloc[-1]
                if current_price > ma_value:
                    signals[ma_name] = 'above'
                else:
                    signals[ma_name] = 'below'
        
        return signals
    
    def _interpret_volume(self, volume_data: Dict) -> Dict[str, Any]:
        """Hacim analizini yorumla - YENİ VE GELİŞMİŞ!"""
        current_vol = volume_data['current_volume']
        avg_vol_20 = volume_data['avg_volume_20']
        avg_vol_5 = volume_data['avg_volume_5']
        
        volume_ratio_20 = volume_data['volume_ratio_20']
        volume_ratio_5 = volume_data['volume_ratio_5']
        recent_momentum = volume_data['recent_volume_momentum']
        
        # Gelişmiş hacim sinyalleri
        volume_signal = 'explosive' if volume_ratio_20 > 3.0 else \
                       'very_high' if volume_ratio_20 > 2.0 else \
                       'high' if volume_ratio_20 > 1.5 else \
                       'above_average' if volume_ratio_20 > 1.2 else \
                       'normal' if volume_ratio_20 > 0.8 else 'low'
        
        # Volume momentum analizi
        volume_momentum = 'accelerating' if recent_momentum > 1.5 else \
                         'building' if recent_momentum > 1.2 else \
                         'stable' if recent_momentum > 0.8 else 'declining'
        
        # Kritik hacim alarmları
        volume_alerts = []
        if volume_data['volume_spike_alert']:
            volume_alerts.append('VOLUME_SPIKE')
        if volume_ratio_20 > 2.5:
            volume_alerts.append('EXPLOSIVE_VOLUME')
        if recent_momentum > 1.8:
            volume_alerts.append('MOMENTUM_ACCELERATION')
        
        return {
            'volume_ratio_20': volume_ratio_20,
            'volume_ratio_5': volume_ratio_5,
            'volume_signal': volume_signal,
            'volume_momentum': volume_momentum,
            'recent_volume_momentum': recent_momentum,
            'volume_alerts': volume_alerts,
            'obv_trend': 'up' if volume_data['obv'].iloc[-1] > volume_data['obv'].iloc[-5] else 'down' if len(volume_data['obv']) > 5 else 'neutral',
            'volume_score': min(100, max(0, (volume_ratio_20 - 0.5) * 50 + (recent_momentum - 0.5) * 30))
        }
    
    def _interpret_momentum(self, momentum: Dict) -> Dict[str, Any]:
        """Momentum göstergelerini yorumla - YENİ VE GELİŞMİŞ!"""
        signals = {}
        
        # Stochastic
        if not momentum['stoch_k'].empty:
            stoch_k = momentum['stoch_k'].iloc[-1]
            if stoch_k > 80:
                signals['stochastic'] = 'overbought'
            elif stoch_k < 20:
                signals['stochastic'] = 'oversold'
            else:
                signals['stochastic'] = 'neutral'
        
        # Williams %R
        if not momentum['williams_r'].empty:
            williams = momentum['williams_r'].iloc[-1]
            if williams > -20:
                signals['williams_r'] = 'overbought'
            elif williams < -80:
                signals['williams_r'] = 'oversold'
            else:
                signals['williams_r'] = 'neutral'
        
        # YENİ! Momentum sinyalleri
        signals['daily_change'] = momentum.get('daily_change', 0)
        signals['two_day_change'] = momentum.get('two_day_change', 0)
        signals['momentum_5d'] = momentum.get('momentum_5d', 0)
        signals['momentum_10d'] = momentum.get('momentum_10d', 0)
        signals['momentum_20d'] = momentum.get('momentum_20d', 0)
        signals['momentum_continuation'] = momentum.get('momentum_continuation', False)
        
        # Momentum skorlaması
        momentum_score = 0
        if signals['momentum_continuation']:
            momentum_score += 20
        if signals['momentum_5d'] > 5:
            momentum_score += 15
        if signals['momentum_10d'] > 10:
            momentum_score += 10
        if signals['daily_change'] > 3:
            momentum_score += 10
            
        signals['momentum_score'] = momentum_score
        signals['momentum_strength'] = 'very_strong' if momentum_score > 40 else \
                                     'strong' if momentum_score > 25 else \
                                     'moderate' if momentum_score > 15 else \
                                     'weak' if momentum_score > 5 else 'very_weak'
        
        return signals
    
    def _detect_patterns(self, data: pd.DataFrame, analysis: Dict) -> Dict[str, Any]:
        """Pattern recognition - YENİ!"""
        patterns = {}
        
        if len(data) < 5:
            return patterns
            
        # Breakout pattern tespiti
        current_price = data['Close'].iloc[-1]
        recent_high = data['High'].iloc[-5:].max()
        recent_low = data['Low'].iloc[-5:].min()
        
        # Yeni zirve kırımı
        if current_price > recent_high * 1.02:  # %2+ breakout
            patterns['breakout'] = 'upward'
        elif current_price < recent_low * 0.98:  # %2+ breakdown
            patterns['breakout'] = 'downward'
        else:
            patterns['breakout'] = 'none'
            
        # Gap analizi
        if len(data) >= 2:
            today_open = data['Open'].iloc[-1]
            yesterday_close = data['Close'].iloc[-2]
            gap_percentage = ((today_open - yesterday_close) / yesterday_close * 100)
            
            if gap_percentage > 2:
                patterns['gap'] = 'gap_up'
            elif gap_percentage < -2:
                patterns['gap'] = 'gap_down'
            else:
                patterns['gap'] = 'none'
        
        # Momentum devamı patternı
        momentum_signals = analysis.get('momentum_signals', {})
        if momentum_signals.get('momentum_continuation'):
            patterns['momentum_pattern'] = 'continuation'
        else:
            patterns['momentum_pattern'] = 'neutral'
            
        # Support/Resistance analizi
        if len(data) >= 10:
            support_level = data['Low'].iloc[-10:].min()
            resistance_level = data['High'].iloc[-10:].max()
            
            # Direncin kırılması
            if current_price > resistance_level * 0.99:
                patterns['support_resistance'] = 'resistance_break'
            elif current_price < support_level * 1.01:
                patterns['support_resistance'] = 'support_test'
            else:
                patterns['support_resistance'] = 'neutral'
        
        return patterns
    
    def _analyze_market_characteristics(self, data: pd.DataFrame, symbol: str) -> Dict[str, Any]:
        """Market cap ve volatilite analizi - YENİ!"""
        characteristics = {}
        
        if len(data) < 10:
            return characteristics
            
        # Volatilite hesaplama
        daily_returns = data['Close'].pct_change().dropna()
        volatility = daily_returns.std() * 100  # Yüzdelik volatilite
        
        # Fiyat aralığı analizi
        current_price = data['Close'].iloc[-1]
        
        # Küçük/orta kap tahmini (fiyat bazlı)
        if current_price < 5:
            size_category = 'micro_cap'
        elif current_price < 20:
            size_category = 'small_cap'
        elif current_price < 100:
            size_category = 'mid_cap'
        else:
            size_category = 'large_cap'
            
        # Liquidity proxy (hacim/fiyat oranı)
        avg_volume = data['Volume'].mean()
        liquidity_score = avg_volume / current_price if current_price > 0 else 0
        
        characteristics = {
            'volatility': volatility,
            'size_category': size_category,
            'price_range': current_price,
            'liquidity_score': liquidity_score,
            'volatility_signal': 'high' if volatility > 8 else 'medium' if volatility > 4 else 'low'
        }
        
        return characteristics
    
    def _calculate_ceiling_potential(self, analysis: Dict) -> Dict[str, Any]:
        """Tavan potansiyeli hesaplama - YENİ!"""
        ceiling_score = 0
        signals = []
        
        # Volume analizi ağırlığı (%40)
        volume_analysis = analysis.get('volume_analysis', {})
        volume_signal = volume_analysis.get('volume_signal')
        volume_alerts = volume_analysis.get('volume_alerts', [])
        
        if volume_signal == 'explosive':
            ceiling_score += 40
            signals.append('EXPLOSIVE_VOLUME')
        elif volume_signal == 'very_high':
            ceiling_score += 30
            signals.append('HIGH_VOLUME')
        elif volume_signal == 'high':
            ceiling_score += 20
            
        # Volume alert bonusları
        if 'VOLUME_SPIKE' in volume_alerts:
            ceiling_score += 15
        if 'EXPLOSIVE_VOLUME' in volume_alerts:
            ceiling_score += 10
            
        # Momentum analizi ağırlığı (%25)
        momentum_signals = analysis.get('momentum_signals', {})
        if momentum_signals.get('momentum_continuation'):
            ceiling_score += 15
            signals.append('MOMENTUM_CONTINUATION')
            
        momentum_5d = momentum_signals.get('momentum_5d', 0)
        if momentum_5d > 5:
            ceiling_score += 10
            
        # Pattern analizi ağırlığı (%20)
        patterns = analysis.get('pattern_signals', {})
        if patterns.get('breakout') == 'upward':
            ceiling_score += 15
            signals.append('BREAKOUT')
        if patterns.get('gap') == 'gap_up':
            ceiling_score += 10
            signals.append('GAP_UP')
        if patterns.get('support_resistance') == 'resistance_break':
            ceiling_score += 10
            signals.append('RESISTANCE_BREAK')
            
        # Market characteristics ağırlığı (%15)
        characteristics = analysis.get('market_characteristics', {})
        size_category = characteristics.get('size_category')
        volatility_signal = characteristics.get('volatility_signal')
        
        if size_category in ['small_cap', 'micro_cap']:
            ceiling_score += 10
            signals.append('SMALL_CAP_ADVANTAGE')
        if volatility_signal == 'high':
            ceiling_score += 5
            
        # Ceiling potential kategorisi
        if ceiling_score >= 80:
            potential = 'VERY_HIGH'
        elif ceiling_score >= 60:
            potential = 'HIGH'
        elif ceiling_score >= 40:
            potential = 'MEDIUM'
        elif ceiling_score >= 20:
            potential = 'LOW'
        else:
            potential = 'VERY_LOW'
            
        return {
            'ceiling_score': min(100, ceiling_score),
            'potential_level': potential,
            'key_signals': signals,
            'recommendation': 'STRONG_BUY' if ceiling_score >= 70 else 
                           'BUY' if ceiling_score >= 50 else 
                           'HOLD' if ceiling_score >= 30 else 'PASS'
        }
    
    def _calculate_technical_score(self, analysis: Dict) -> float:
        """Teknik analiz skorunu hesapla (0-100) - YENİ VE GELİŞMİŞ!"""
        score = 40.0  # Biraz daha düşük başlangıç
        
        # RSI skoru
        if analysis.get('rsi_signal') == 'oversold':
            score += 20  # Daha yüksek ağırlık
        elif analysis.get('rsi_signal') == 'bullish':
            score += 12
        elif analysis.get('rsi_signal') == 'overbought':
            score -= 15
        elif analysis.get('rsi_signal') == 'bearish':
            score -= 8
        
        # MACD skoru
        if analysis.get('macd_trend') == 'bullish':
            score += 12
        elif analysis.get('macd_trend') == 'bearish':
            score -= 12
        
        # GELİŞMİŞ Hacim skoru - ÇOK ÖNEMLİ!
        volume_analysis = analysis.get('volume_analysis', {})
        volume_signal = volume_analysis.get('volume_signal')
        volume_alerts = volume_analysis.get('volume_alerts', [])
        
        if volume_signal == 'explosive':
            score += 25  # En yüksek puan!
        elif volume_signal == 'very_high':
            score += 18
        elif volume_signal == 'high':
            score += 12
        elif volume_signal == 'above_average':
            score += 6
        elif volume_signal == 'low':
            score -= 10
            
        # Volume alert bonusları
        if 'VOLUME_SPIKE' in volume_alerts:
            score += 15
        if 'EXPLOSIVE_VOLUME' in volume_alerts:
            score += 20
        if 'MOMENTUM_ACCELERATION' in volume_alerts:
            score += 12
        
        # GELİŞMİŞ Momentum skoru
        momentum_signals = analysis.get('momentum_signals', {})
        if momentum_signals.get('momentum_continuation'):
            score += 15  # Momentum devamı çok önemli!
        if momentum_signals.get('stochastic') == 'oversold':
            score += 12
        elif momentum_signals.get('stochastic') == 'overbought':
            score -= 12
            
        # 5-20 günlük momentum bonusları
        momentum_5d = momentum_signals.get('momentum_5d', 0)
        momentum_20d = momentum_signals.get('momentum_20d', 0)
        
        if momentum_5d > 10:  # 5 günde %10+ artış
            score += 10
        elif momentum_5d > 5:
            score += 5
            
        if momentum_20d > 20:  # 20 günde %20+ artış
            score += 8
        elif momentum_20d > 10:
            score += 4
        
        return max(0, min(100, score))

# Test fonksiyonu
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    from bist_data_fetcher import BISTDataFetcher
    
    # Test için veri çek
    fetcher = BISTDataFetcher()
    analyzer = TechnicalAnalyzer()
    
    # Bir hisse için test
    test_symbol = "AKBNK.IS"
    data = fetcher.get_stock_data(test_symbol)
    
    if data is not None:
        analysis = analyzer.analyze_stock(test_symbol, data)
        print(f"\\n{test_symbol} Teknik Analiz:")
        print(f"Son Fiyat: {analysis.get('last_price', 'N/A')}")
        print(f"RSI: {analysis.get('rsi', 'N/A')} ({analysis.get('rsi_signal', 'N/A')})")
        print(f"Teknik Skor: {analysis.get('technical_score', 'N/A')}/100")
    else:
        print("Test verisi alınamadı")