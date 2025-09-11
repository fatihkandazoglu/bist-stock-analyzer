#!/usr/bin/env python3
"""
6 Eylül Borsa Açılışı - Bugünkü Tavan Adayları Analizi
Kapsamlı teknik analiz ile bugün tavan yapabilecek hisselerin tespiti
"""

import yfinance as yf
import talib
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class TodayCeilingPredictor:
    def __init__(self):
        """Bugünkü tavan tahmin sistemi"""
        self.top_candidates = [
            'RTALB.IS', 'BEYAZ.IS', 'BARMA.IS', 'VERUS.IS', 'BORLS.IS',
            'GRNYO.IS', 'PCILT.IS', 'KAPLM.IS', 'PENTA.IS'
        ]
        
        # Ek potansiyel adaylar
        self.additional_candidates = [
            'BTCIM.IS', 'YATAS.IS', 'BLCYT.IS', 'KLNMA.IS', 'BFREN.IS',
            'THYAO.IS', 'AKBNK.IS', 'TUPRS.IS', 'ASELS.IS', 'VESTL.IS'
        ]
    
    def analyze_pre_market_momentum(self, symbol: str) -> dict:
        """Piyasa öncesi momentum analizi"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period='90d')
            
            if len(data) < 30:
                return {'error': 'Yetersiz veri'}
            
            close = data['Close'].values
            high = data['High'].values
            low = data['Low'].values
            volume = data['Volume'].values
            
            # Son fiyat bilgileri
            current_price = close[-1]
            prev_close = close[-2] if len(close) >= 2 else close[-1]
            
            # Temel momentum hesaplamaları
            daily_change = ((current_price - prev_close) / prev_close) * 100
            
            # Volume analizi
            volume_avg_20 = np.mean(volume[-20:]) if len(volume) >= 20 else volume[-1]
            volume_ratio = volume[-1] / volume_avg_20 if volume_avg_20 > 0 else 1.0
            
            # Teknik göstergeler
            rsi = talib.RSI(close, timeperiod=14)[-1] if len(close) >= 14 else 50.0
            adx = talib.ADX(high, low, close, timeperiod=14)[-1] if len(close) >= 14 else 25.0
            
            # MACD
            macd_line, macd_signal, macd_hist = talib.MACD(close)
            macd_momentum = macd_hist[-1] if len(macd_hist) > 0 else 0.0
            macd_bullish = macd_line[-1] > macd_signal[-1] if len(macd_line) > 0 and len(macd_signal) > 0 else False
            
            # Bollinger Bands
            bb_upper, bb_middle, bb_lower = talib.BBANDS(close)
            bb_position = ((current_price - bb_lower[-1]) / (bb_upper[-1] - bb_lower[-1]) * 100) if len(bb_upper) > 0 and bb_upper[-1] != bb_lower[-1] else 50.0
            
            # Williams %R
            williams_r = talib.WILLR(high, low, close)[-1] if len(close) >= 14 else -50.0
            
            # CCI
            cci = talib.CCI(high, low, close)[-1] if len(close) >= 20 else 0.0
            
            # Stochastic
            stoch_k, stoch_d = talib.STOCH(high, low, close)
            stoch_k_val = stoch_k[-1] if len(stoch_k) > 0 else 50.0
            
            # ATR (Average True Range)
            atr = talib.ATR(high, low, close)[-1] if len(close) >= 14 else 0.0
            atr_percent = (atr / current_price * 100) if current_price > 0 else 0.0
            
            # Momentum analizi
            momentum_3d = ((close[-1] - close[-4]) / close[-4]) * 100 if len(close) >= 4 else 0.0
            momentum_5d = ((close[-1] - close[-6]) / close[-6]) * 100 if len(close) >= 6 else 0.0
            momentum_10d = ((close[-1] - close[-11]) / close[-11]) * 100 if len(close) >= 11 else 0.0
            
            # Son 30 gün tavan analizi
            ceiling_days = []
            big_move_days = []
            
            for i in range(1, min(30, len(data))):
                prev_price = data['Close'].iloc[i-1]
                day_price = data['Close'].iloc[i]
                day_change = ((day_price - prev_price) / prev_price) * 100
                
                if day_change >= 9.0:
                    ceiling_days.append({
                        'date': data.index[i].strftime('%d.%m'),
                        'change': day_change,
                        'price': day_price
                    })
                elif day_change >= 5.0:
                    big_move_days.append({
                        'date': data.index[i].strftime('%d.%m'),
                        'change': day_change,
                        'price': day_price
                    })
            
            # Gap analizi (önceki kapanış vs bugünkü açılış beklentisi)
            gap_potential = 0
            if len(data) >= 5:
                # Son 5 günün ortalama volatilitesi
                recent_volatility = np.std([(data['Close'].iloc[i] - data['Close'].iloc[i-1]) / data['Close'].iloc[i-1] * 100 
                                          for i in range(-5, 0)]) if len(data) >= 5 else 0
                gap_potential = recent_volatility
            
            # Destek/Direnç seviyeleri
            recent_high_20 = np.max(high[-20:]) if len(high) >= 20 else current_price
            recent_low_20 = np.min(low[-20:]) if len(low) >= 20 else current_price
            
            resistance_distance = ((recent_high_20 - current_price) / current_price * 100) if current_price > 0 else 0
            support_distance = ((current_price - recent_low_20) / current_price * 100) if current_price > 0 else 0
            
            return {
                'symbol': symbol.replace('.IS', ''),
                'current_price': current_price,
                'prev_close': prev_close,
                'daily_change': daily_change,
                'volume_ratio': volume_ratio,
                'rsi': rsi,
                'adx': adx,
                'macd_momentum': macd_momentum,
                'macd_bullish': macd_bullish,
                'bb_position': bb_position,
                'williams_r': williams_r,
                'cci': cci,
                'stoch_k': stoch_k_val,
                'atr_percent': atr_percent,
                'momentum_3d': momentum_3d,
                'momentum_5d': momentum_5d,
                'momentum_10d': momentum_10d,
                'ceiling_count': len(ceiling_days),
                'big_move_count': len(big_move_days),
                'ceiling_days': ceiling_days,
                'gap_potential': gap_potential,
                'resistance_distance': resistance_distance,
                'support_distance': support_distance,
                'recent_high_20': recent_high_20,
                'recent_low_20': recent_low_20
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def calculate_ceiling_probability(self, analysis: dict) -> float:
        """Tavan yapma olasılığı hesaplama (0-100)"""
        if 'error' in analysis:
            return 0
        
        score = 0
        max_score = 0
        
        # RSI değerlendirmesi (30 puan)
        rsi = analysis['rsi']
        if 50 <= rsi <= 70:
            score += 30
        elif 45 <= rsi <= 75:
            score += 25
        elif 40 <= rsi <= 80:
            score += 20
        elif rsi < 40:
            score += 10  # Oversold bounce potential
        max_score += 30
        
        # ADX trend gücü (25 puan)
        adx = analysis['adx']
        if adx >= 50:
            score += 25
        elif adx >= 40:
            score += 22
        elif adx >= 30:
            score += 18
        elif adx >= 25:
            score += 15
        elif adx >= 20:
            score += 10
        max_score += 25
        
        # Volume momentum (20 puan)
        vol_ratio = analysis['volume_ratio']
        if vol_ratio >= 3.0:
            score += 20
        elif vol_ratio >= 2.5:
            score += 18
        elif vol_ratio >= 2.0:
            score += 15
        elif vol_ratio >= 1.5:
            score += 12
        elif vol_ratio >= 1.2:
            score += 8
        max_score += 20
        
        # MACD momentum (15 puan)
        if analysis['macd_bullish']:
            if analysis['macd_momentum'] > 0:
                score += 15
            else:
                score += 10
        max_score += 15
        
        # BB pozisyonu (15 puan)
        bb_pos = analysis['bb_position']
        if 60 <= bb_pos <= 85:
            score += 15
        elif 50 <= bb_pos <= 90:
            score += 12
        elif bb_pos >= 40:
            score += 8
        max_score += 15
        
        # Son günlerin momentum (20 puan)
        mom_3d = analysis['momentum_3d']
        mom_5d = analysis['momentum_5d']
        
        if mom_3d >= 8:
            score += 12
        elif mom_3d >= 5:
            score += 10
        elif mom_3d >= 2:
            score += 6
        elif mom_3d >= 0:
            score += 3
        
        if mom_5d >= 15:
            score += 8
        elif mom_5d >= 10:
            score += 6
        elif mom_5d >= 5:
            score += 4
        max_score += 20
        
        # Tavan geçmişi (10 puan)
        ceiling_count = analysis['ceiling_count']
        if ceiling_count >= 3:
            score += 10
        elif ceiling_count >= 2:
            score += 8
        elif ceiling_count >= 1:
            score += 6
        elif analysis['big_move_count'] >= 3:
            score += 4
        max_score += 10
        
        # Williams %R (10 puan)
        williams = analysis['williams_r']
        if williams >= -30:
            score += 10
        elif williams >= -40:
            score += 8
        elif williams >= -50:
            score += 6
        max_score += 10
        
        # CCI momentum (10 puan)
        cci = analysis['cci']
        if cci >= 150:
            score += 10
        elif cci >= 100:
            score += 8
        elif cci >= 50:
            score += 6
        elif cci >= 0:
            score += 4
        max_score += 10
        
        # Direnç mesafesi (10 puan)
        resistance_dist = analysis['resistance_distance']
        if resistance_dist <= 5:
            score += 10
        elif resistance_dist <= 10:
            score += 8
        elif resistance_dist <= 15:
            score += 6
        max_score += 10
        
        # ATR volatilite (5 puan)
        atr_pct = analysis['atr_percent']
        if 3 <= atr_pct <= 8:
            score += 5
        elif 2 <= atr_pct <= 10:
            score += 3
        max_score += 5
        
        return (score / max_score * 100) if max_score > 0 else 0
    
    def get_ceiling_signals(self, analysis: dict) -> list:
        """Tavan sinyallerini tespit et"""
        signals = []
        
        if 'error' in analysis:
            return signals
        
        # Güçlü sinyaller
        if analysis['adx'] >= 50:
            signals.append('🔥 Çok güçlü trend (ADX 50+)')
        elif analysis['adx'] >= 40:
            signals.append('⚡ Güçlü trend (ADX 40+)')
        
        if analysis['volume_ratio'] >= 2.5:
            signals.append('📊 Çok yüksek hacim (2.5x+)')
        elif analysis['volume_ratio'] >= 1.8:
            signals.append('📈 Yüksek hacim (1.8x+)')
        
        if analysis['momentum_3d'] >= 8:
            signals.append('🚀 3 gün güçlü momentum (%8+)')
        elif analysis['momentum_3d'] >= 5:
            signals.append('📈 3 gün iyi momentum (%5+)')
        
        if analysis['bb_position'] >= 80:
            signals.append('🎯 BB üst bölgede (%80+)')
        elif analysis['bb_position'] >= 70:
            signals.append('📊 BB üst-ortada (%70+)')
        
        if analysis['williams_r'] >= -25:
            signals.append('⚡ Williams R güçlü (-25+)')
        
        if analysis['cci'] >= 150:
            signals.append('💪 CCI çok güçlü (150+)')
        elif analysis['cci'] >= 100:
            signals.append('📈 CCI güçlü (100+)')
        
        if analysis['macd_bullish'] and analysis['macd_momentum'] > 0:
            signals.append('✅ MACD bullish momentum')
        
        if 50 <= analysis['rsi'] <= 70:
            signals.append('🎯 RSI ideal seviyede')
        elif analysis['rsi'] < 40:
            signals.append('💎 RSI oversold (bounce potential)')
        
        if analysis['ceiling_count'] >= 2:
            signals.append(f'👑 Son 30 günde {analysis["ceiling_count"]} tavan')
        
        if analysis['resistance_distance'] <= 5:
            signals.append('🎪 Dirençe çok yakın (%5 altı)')
        
        return signals
    
    def run_today_analysis(self):
        """Bugünkü kapsamlı analiz"""
        print("🚀 6 EYLÜL CUMA - BUGÜNKÜ TAVAN ADAY ANALİZİ")
        print("=" * 80)
        print("📅 Analiz Zamanı:", datetime.now().strftime("%d.%m.%Y %H:%M"))
        print("=" * 80)
        
        all_candidates = []
        
        # Ana adayları analiz et
        print("\n🔥 ANA SÜPER ADAYLAR ANALİZİ:")
        print("-" * 50)
        
        for symbol in self.top_candidates:
            analysis = self.analyze_pre_market_momentum(symbol)
            if 'error' not in analysis:
                probability = self.calculate_ceiling_probability(analysis)
                signals = self.get_ceiling_signals(analysis)
                
                analysis['ceiling_probability'] = probability
                analysis['signals'] = signals
                all_candidates.append(analysis)
        
        # Ek adayları analiz et
        print("\n📊 EK POTANSIYEL ADAYLAR:")
        print("-" * 50)
        
        for symbol in self.additional_candidates:
            analysis = self.analyze_pre_market_momentum(symbol)
            if 'error' not in analysis:
                probability = self.calculate_ceiling_probability(analysis)
                if probability >= 60:  # Sadece yüksek potansiyelli olanlar
                    signals = self.get_ceiling_signals(analysis)
                    analysis['ceiling_probability'] = probability
                    analysis['signals'] = signals
                    all_candidates.append(analysis)
        
        # Sırala
        all_candidates.sort(key=lambda x: x['ceiling_probability'], reverse=True)
        
        print(f"\n🎯 TOPLAM {len(all_candidates)} GÜÇLÜ ADAY BULUNDU!")
        print("\n👑 BUGÜNKÜ TAVAN ADAY LİSTESİ:")
        print("=" * 100)
        
        for i, candidate in enumerate(all_candidates[:15]):
            prob = candidate['ceiling_probability']
            symbol = candidate['symbol']
            price = candidate['current_price']
            change = candidate['daily_change']
            
            # Emoji seçimi
            if prob >= 85:
                emoji = "👑"
                risk = "ÇOK YÜKSEK"
            elif prob >= 75:
                emoji = "🔥"
                risk = "YÜKSEK"
            elif prob >= 65:
                emoji = "⚡"
                risk = "ORTA-YÜKSEK"
            else:
                emoji = "✨"
                risk = "ORTA"
            
            print(f"{emoji} {i+1:2d}. {symbol:8s} | Olasılık: %{prob:5.1f} | Risk: {risk:10s}")
            print(f"      Fiyat: {price:8.2f} TL | Dün: %{change:+5.1f} | ADX: {candidate['adx']:5.1f}")
            print(f"      Hacim: {candidate['volume_ratio']:4.1f}x | RSI: {candidate['rsi']:5.1f} | 3G Mom: %{candidate['momentum_3d']:+5.1f}")
            
            # En önemli sinyaller
            top_signals = candidate['signals'][:3]
            if top_signals:
                print(f"      🎯 {' | '.join(top_signals)}")
            
            print()
        
        # Özel kategoriler
        self._print_special_categories(all_candidates)
        
        # Risk uyarıları
        self._print_risk_warnings(all_candidates)
        
        # Piyasa değerlendirmesi
        self._print_market_assessment(all_candidates)
        
        return all_candidates
    
    def _print_special_categories(self, candidates):
        """Özel kategorilerde sınıflandırma"""
        print("\n🏆 ÖZEL KATEGORİLER:")
        print("=" * 60)
        
        # Kesin tavan adayları (85%+)
        sure_bets = [c for c in candidates if c['ceiling_probability'] >= 85]
        if sure_bets:
            print(f"\n👑 KEŞİN TAVAN ADAYLARI (%85+ olasılık):")
            for c in sure_bets[:5]:
                print(f"   {c['symbol']:8s} - %{c['ceiling_probability']:5.1f} olasılık")
        
        # Güçlü momentum (75%+)
        strong_momentum = [c for c in candidates if 75 <= c['ceiling_probability'] < 85]
        if strong_momentum:
            print(f"\n🔥 GÜÇLÜ MOMENTUM ADAYLARI (%75-84 olasılık):")
            for c in strong_momentum[:5]:
                print(f"   {c['symbol']:8s} - %{c['ceiling_probability']:5.1f} olasılık")
        
        # Sürpriz adaylar (65-74%)
        surprise_candidates = [c for c in candidates if 65 <= c['ceiling_probability'] < 75]
        if surprise_candidates:
            print(f"\n⚡ SÜRPRİZ ADAY POTANSİYELİ (%65-74 olasılık):")
            for c in surprise_candidates[:5]:
                print(f"   {c['symbol']:8s} - %{c['ceiling_probability']:5.1f} olasılık")
        
        # Yüksek hacim adayları
        high_volume = [c for c in candidates if c['volume_ratio'] >= 2.0]
        high_volume.sort(key=lambda x: x['volume_ratio'], reverse=True)
        if high_volume:
            print(f"\n📊 YÜKSEK HACİM ADAYLARI:")
            for c in high_volume[:5]:
                print(f"   {c['symbol']:8s} - {c['volume_ratio']:4.1f}x hacim")
        
        # Güçlü trend adayları
        strong_trend = [c for c in candidates if c['adx'] >= 40]
        strong_trend.sort(key=lambda x: x['adx'], reverse=True)
        if strong_trend:
            print(f"\n📈 GÜÇLÜ TREND ADAYLARI:")
            for c in strong_trend[:5]:
                print(f"   {c['symbol']:8s} - ADX {c['adx']:5.1f}")
    
    def _print_risk_warnings(self, candidates):
        """Risk uyarıları"""
        print(f"\n⚠️ RİSK UYARILARI VE DİKKAT EDİLECEKLER:")
        print("=" * 60)
        
        # Aşırı alım uyarıları
        overbought = [c for c in candidates if c['rsi'] > 80]
        if overbought:
            print(f"\n🚨 AŞIRI ALIM UYARISI (RSI 80+):")
            for c in overbought:
                print(f"   {c['symbol']:8s} - RSI {c['rsi']:5.1f} (dikkatli olun!)")
        
        # Düşük hacim uyarıları
        low_volume = [c for c in candidates if c['volume_ratio'] < 1.2]
        if low_volume:
            print(f"\n📉 DÜŞÜK HACİM UYARISI:")
            for c in low_volume:
                print(f"   {c['symbol']:8s} - Sadece {c['volume_ratio']:4.1f}x hacim")
        
        # Genel uyarılar
        print(f"\n💡 GENEL UYARILAR:")
        print(f"   • Tavan limitine yakın alım yapmayın")
        print(f"   • Stop-loss seviyelerinizi belirleyin")
        print(f"   • Portföyünüzü çeşitlendirin")
        print(f"   • Hacimsiz hareketlere dikkat!")
        print(f"   • %9+ artış = tavan (alım satım durur)")
    
    def _print_market_assessment(self, candidates):
        """Genel piyasa değerlendirmesi"""
        print(f"\n📊 GENEL PİYASA DEĞERLENDİRMESİ:")
        print("=" * 60)
        
        # İstatistikler
        high_prob_count = len([c for c in candidates if c['ceiling_probability'] >= 75])
        medium_prob_count = len([c for c in candidates if 60 <= c['ceiling_probability'] < 75])
        
        avg_prob = np.mean([c['ceiling_probability'] for c in candidates])
        avg_volume = np.mean([c['volume_ratio'] for c in candidates])
        avg_adx = np.mean([c['adx'] for c in candidates])
        
        print(f"\n📈 BUGÜNKÜ PİYASA DURUMU:")
        print(f"   • Yüksek potansiyel adaylar: {high_prob_count}")
        print(f"   • Orta potansiyel adaylar: {medium_prob_count}")
        print(f"   • Ortalama tavan olasılığı: %{avg_prob:.1f}")
        print(f"   • Ortalama hacim oranı: {avg_volume:.1f}x")
        print(f"   • Ortalama trend gücü (ADX): {avg_adx:.1f}")
        
        # Piyasa görünümü
        if avg_prob >= 70:
            market_mood = "🔥 ÇOK YÜKSEK POTANSİYEL"
        elif avg_prob >= 60:
            market_mood = "⚡ YÜKSEK POTANSİYEL"
        elif avg_prob >= 50:
            market_mood = "📊 ORTA POTANSİYEL"
        else:
            market_mood = "😐 DÜŞÜK POTANSİYEL"
        
        print(f"\n🎯 BUGÜNKÜ PİYASA RUHYATI: {market_mood}")
        
        if high_prob_count >= 3:
            print(f"   ✅ Çok sayıda güçlü aday var - aktif bir gün olabilir!")
        elif high_prob_count >= 1:
            print(f"   ✅ İyi adaylar mevcut - seçici davranın")
        else:
            print(f"   ⚠️ Güçlü aday sayısı az - temkinli olun")
        
        print(f"\n🕘 ÖNERİLEN STRATEJİ:")
        print(f"   • 09:30 açılışta ilk 15 dakika bekleyin")
        print(f"   • Hacimli hareketleri takip edin")
        print(f"   • İlk %5 artışta pozisyon alın")
        print(f"   • %7-8 civarında kısmi kar alın")
        print(f"   • Tavan yakını alım yapmayın!")

def main():
    predictor = TodayCeilingPredictor()
    results = predictor.run_today_analysis()
    
    print(f"\n🎯 ÖZET:")
    print(f"=" * 40)
    print(f"📅 Analiz: 6 Eylül 2025 Cuma")
    print(f"🔍 Toplam aday: {len(results)}")
    print(f"👑 En yüksek olasılık: %{max([r['ceiling_probability'] for r in results]):.1f}")
    print(f"💰 En umutlu aday: {results[0]['symbol'] if results else 'YOK'}")
    print(f"\n🚀 İYİ GÜNLER DİLEYİM! BAŞARILAR! 🍀")

if __name__ == "__main__":
    main()