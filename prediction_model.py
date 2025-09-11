#!/usr/bin/env python3
"""
Tahmin Modeli Modülü
Bu modül makine öğrenmesi ile tavan yapabilecek hisseleri tahmin eder.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import logging
from typing import List, Dict, Any, Optional
import pickle
import os

logger = logging.getLogger(__name__)

class StockPredictionModel:
    def __init__(self):
        """Tahmin modeli sınıfını başlat"""
        self.model = None
        self.scaler = StandardScaler()
        self.feature_columns = []
        self.model_trained = False
        self.model_file = "stock_prediction_model.pkl"
        
        # YENİ! Genişletilmiş özellik isimleri
        self.base_features = [
            'rsi', 'macd', 'macd_signal', 'price_change_1d', 'price_change_5d',
            'volume_ratio_20', 'volume_ratio_5', 'volume_momentum', 'technical_score', 
            'ceiling_score', 'momentum_score', 'pattern_score', 'sentiment_score', 
            'xu100_change', 'volatility', 'momentum_continuation'
        ]
        
        self._load_model()
    
    def create_features(self, analysis_data: Dict[str, Any], 
                       market_info: Dict[str, Any] = None,
                       sentiment_score: float = 0.5) -> List[float]:
        """YENİ! Genişletilmiş özellik vektörü oluştur"""
        features = []
        
        # Temel teknik analiz özellikleri
        features.append(analysis_data.get('rsi', 50.0))
        features.append(analysis_data.get('macd', 0.0))
        features.append(analysis_data.get('macd_signal', 0.0))
        features.append(analysis_data.get('price_change_1d', 0.0))
        features.append(analysis_data.get('price_change_5d', 0.0))
        
        # YENİ! Gelişmiş hacim analizi
        volume_analysis = analysis_data.get('volume_analysis', {})
        features.append(volume_analysis.get('volume_ratio_20', 1.0))
        features.append(volume_analysis.get('volume_ratio_5', 1.0))
        features.append(volume_analysis.get('recent_volume_momentum', 1.0))
        
        # Temel teknik skor
        features.append(analysis_data.get('technical_score', 50.0))
        
        # YENİ! Tavan potansiyeli skoru
        ceiling_potential = analysis_data.get('ceiling_potential', {})
        features.append(ceiling_potential.get('ceiling_score', 0.0))
        
        # YENİ! Momentum skoru
        momentum_signals = analysis_data.get('momentum_signals', {})
        features.append(momentum_signals.get('momentum_score', 0.0))
        
        # YENİ! Pattern skoru
        pattern_signals = analysis_data.get('pattern_signals', {})
        pattern_score = 0.0
        if pattern_signals.get('breakout') == 'upward':
            pattern_score += 30
        if pattern_signals.get('gap') == 'gap_up':
            pattern_score += 20
        if pattern_signals.get('support_resistance') == 'resistance_break':
            pattern_score += 25
        features.append(pattern_score)
        
        # Sentiment skoru
        features.append(sentiment_score)
        
        # Piyasa durumu
        xu100_change = 0.0
        if market_info:
            xu100_change = market_info.get('xu100_change', 0.0)
        features.append(xu100_change)
        
        # YENİ! Volatilite ve piyasa karakteristikleri
        characteristics = analysis_data.get('market_characteristics', {})
        features.append(characteristics.get('volatility', 5.0))
        
        # YENİ! Momentum devamı (binary)
        features.append(1.0 if momentum_signals.get('momentum_continuation', False) else 0.0)
        
        return features
    
    def prepare_training_data(self, historical_data: List[Dict[str, Any]]) -> tuple:
        """Eğitim verisi hazırla"""
        features_list = []
        labels = []
        
        for data_point in historical_data:
            features = self.create_features(
                data_point.get('analysis', {}),
                data_point.get('market_info', {}),
                data_point.get('sentiment_score', 0.5)
            )
            
            # Etiket: Sonraki gün tavan yapma durumu (1: tavan, 0: değil)
            label = data_point.get('next_day_ceiling', 0)
            
            features_list.append(features)
            labels.append(label)
        
        return np.array(features_list), np.array(labels)
    
    def train_model(self, historical_data: List[Dict[str, Any]]) -> bool:
        """Modeli eğit"""
        try:
            logger.info("Model eğitimi başlatılıyor...")
            
            # Veri hazırlama
            X, y = self.prepare_training_data(historical_data)
            
            if len(X) < 50:  # Minimum veri kontrolü
                logger.warning("Eğitim için yeterli veri yok")
                return False
            
            # Veriyi ölçekle
            X_scaled = self.scaler.fit_transform(X)
            
            # Eğitim/test ayırma
            X_train, X_test, y_train, y_test = train_test_split(
                X_scaled, y, test_size=0.2, random_state=42
            )
            
            # Model oluştur (Random Forest + Gradient Boosting ensemble)
            rf_model = RandomForestClassifier(
                n_estimators=100, 
                max_depth=10, 
                random_state=42
            )
            gb_model = GradientBoostingClassifier(
                n_estimators=100, 
                max_depth=6, 
                random_state=42
            )
            
            # Modelleri eğit
            rf_model.fit(X_train, y_train)
            gb_model.fit(X_train, y_train)
            
            # Ensemble model oluştur (basit ortalama)
            self.model = {
                'rf': rf_model,
                'gb': gb_model,
                'scaler': self.scaler
            }
            
            # Test skorları
            rf_score = rf_model.score(X_test, y_test)
            gb_score = gb_model.score(X_test, y_test)
            
            logger.info(f"Random Forest doğruluk: {rf_score:.3f}")
            logger.info(f"Gradient Boosting doğruluk: {gb_score:.3f}")
            
            self.model_trained = True
            self._save_model()
            
            return True
            
        except Exception as e:
            logger.error(f"Model eğitim hatası: {e}")
            return False
    
    def predict_ceiling_probability(self, analysis_data: Dict[str, Any],
                                  market_info: Dict[str, Any] = None,
                                  sentiment_score: float = 0.5) -> float:
        """Tavan yapma olasılığını tahmin et"""
        if not self.model_trained or not self.model:
            # Model eğitilmemişse basit heuristik kullan
            return self._simple_heuristic_prediction(analysis_data, sentiment_score)
        
        try:
            # Özellik vektörü oluştur
            features = self.create_features(analysis_data, market_info, sentiment_score)
            features_array = np.array([features])
            
            # Özellikleri ölçekle
            features_scaled = self.scaler.transform(features_array)
            
            # Her iki modelden tahmin al
            rf_prob = self.model['rf'].predict_proba(features_scaled)[0][1]
            gb_prob = self.model['gb'].predict_proba(features_scaled)[0][1]
            
            # Ensemble tahmini (ağırlıklı ortalama)
            ensemble_prob = (rf_prob * 0.6 + gb_prob * 0.4)
            
            return float(ensemble_prob)
            
        except Exception as e:
            logger.error(f"Tahmin hatası: {e}")
            return self._simple_heuristic_prediction(analysis_data, sentiment_score)
    
    def _simple_heuristic_prediction(self, analysis_data: Dict[str, Any], 
                                   sentiment_score: float) -> float:
        """YENİ GELİŞMİŞ TAHMİN - Volume momentum + Pattern recognition"""
        score = 0.0
        symbol = analysis_data.get('symbol', '').replace('.IS', '')
        
        # ÖNEMLİ: Günlük fiyat değişimini kontrol et
        price_change_1d = analysis_data.get('price_change_1d', 0.0)
        price_change_5d = analysis_data.get('price_change_5d', 0.0)
        
        # 1. MOMENTUM DEVAMİ BONUSU (EN ÖNEMLİ!)
        if price_change_1d >= 8.0:  # Bugün tavan yaptı
            score += 0.6  # SÜPER BONUS - yarın da devam edebilir
        elif price_change_1d >= 5.0:  # Güçlü artış
            score += 0.4
        elif price_change_1d >= 2.0:  # Orta momentum
            score += 0.2
        elif price_change_1d < -2.0:  # Düşüş
            score -= 0.4
        
        # 2. KÜÇÜK/ORTA CAP BONUSU
        if self._is_small_mid_cap(symbol):
            score += 0.3  # Küçük hisseler daha hareketli
        
        # 3. SPEKÜLATİF BONUS
        if self._is_speculative_stock(symbol):
            score += 0.25
            
        # 4. YENİ RSI YAKLAŞIMI - MOMENTUM ODAKLI
        rsi = analysis_data.get('rsi', 50.0)
        if 60 <= rsi <= 75:  # Güçlü momentum bölgesi
            score += 0.25
        elif 50 <= rsi <= 60:  # Orta momentum
            score += 0.15
        elif 25 <= rsi <= 35 and price_change_1d > 0:  # Oversold çıkış (eski yaklaşım)
            score += 0.1
        elif rsi > 80:  # Aşırı momentum
            score -= 0.1
        
        # MACD - sadece pozitif crossover durumunda
        macd = analysis_data.get('macd', 0.0)
        macd_signal = analysis_data.get('macd_signal', 0.0)
        macd_histogram = analysis_data.get('macd_histogram', 0.0)
        
        if macd > macd_signal and macd_histogram > 0:  # Güçlü bullish sinyal
            score += 0.15
        elif macd < macd_signal:  # Bearish
            score -= 0.15
        
        # 5. YENİ! GELİŞMİŞ HACİM ANALİZİ
        volume_analysis = analysis_data.get('volume_analysis', {})
        volume_ratio_20 = volume_analysis.get('volume_ratio_20', 1.0)
        volume_alerts = volume_analysis.get('volume_alerts', [])
        volume_momentum = volume_analysis.get('recent_volume_momentum', 1.0)
        
        # Volume ratio bonusu
        if volume_ratio_20 > 3.0:
            score += 0.4  # Daha yüksek!
        elif volume_ratio_20 > 2.5:
            score += 0.35
        elif volume_ratio_20 > 2.0:
            score += 0.25
        elif volume_ratio_20 > 1.5:
            score += 0.15
        elif volume_ratio_20 > 1.2:
            score += 0.1
        elif volume_ratio_20 < 0.7:
            score -= 0.25
            
        # Volume alert bonusları
        if 'EXPLOSIVE_VOLUME' in volume_alerts:
            score += 0.3
        if 'VOLUME_SPIKE' in volume_alerts:
            score += 0.2
        if 'MOMENTUM_ACCELERATION' in volume_alerts:
            score += 0.15
            
        # Volume momentum bonusu
        if volume_momentum > 1.8:
            score += 0.2
        elif volume_momentum > 1.5:
            score += 0.1
        
        # Teknik skor - daha katı değerlendirme
        technical_score = analysis_data.get('technical_score', 50.0)
        if technical_score > 70:
            score += 0.1
        elif technical_score < 40:
            score -= 0.2
        
        # Sentiment etkisi - sadece çok güçlü pozitif sentimentte bonus
        if sentiment_score > 0.7:
            score += 0.1
        elif sentiment_score < 0.3:
            score -= 0.1
        
        # 6. BOLLINGER BANDS - YENİ YAKLAŞIM
        bb_position = analysis_data.get('bollinger_position', 0)
        if bb_position > 0.5:  # Üst banda yakın - momentum!
            score += 0.15
        elif bb_position > 0:  # Orta üstü
            score += 0.1
        
        # 7. SENTIMENT BONUS
        if sentiment_score > 0.7:
            score += 0.15
        elif sentiment_score < 0.3:
            score -= 0.1
            
        # 8. 5 GÜN MOMENTUM BONUSU
        if price_change_5d > 15:  # Güçlü 5 gün momentum
            score += 0.2
        elif price_change_5d > 8:
            score += 0.1
        elif price_change_5d < -10:
            score -= 0.2
        
        # YENİ! Pattern ve momentum bonusları
        patterns = analysis_data.get('pattern_signals', {})
        momentum_signals = analysis_data.get('momentum_signals', {})
        ceiling_potential = analysis_data.get('ceiling_potential', {})
        
        # Pattern bonusları
        if patterns.get('breakout') == 'upward':
            score += 0.25
        if patterns.get('gap') == 'gap_up':
            score += 0.15
        if patterns.get('support_resistance') == 'resistance_break':
            score += 0.2
            
        # Momentum continuation bonusu
        if momentum_signals.get('momentum_continuation'):
            score += 0.3  # ÇOK ÖNEMLİ!
            
        # Ceiling potential entegrasyonu
        ceiling_score = ceiling_potential.get('ceiling_score', 0)
        if ceiling_score > 80:
            score += 0.25
        elif ceiling_score > 60:
            score += 0.15
        elif ceiling_score > 40:
            score += 0.1
            
        # 0-1 arasına normalize et - daha agresif yaklaşım
        probability = max(0.0, min(1.0, score + 0.3))  # Base score artırıldı
        
        volume_ratio_20 = volume_analysis.get('volume_ratio_20', 1.0)
        logger.debug(f"{symbol} YENİ SKOR: {probability:.3f} (momentum: {price_change_1d:+.1f}%, hacim: {volume_ratio_20:.1f}x, ceiling: {ceiling_score})")
        return probability
    
    def _is_small_mid_cap(self, symbol: str) -> bool:
        """Küçük/orta cap hisse mi kontrol et"""
        large_caps = ['THYAO', 'AKBNK', 'GARAN', 'ISCTR', 'YKBNK', 'SISE', 'ARCLK', 
                     'MGROS', 'PETKM', 'SAHOL', 'FROTO', 'TUPRS', 'EREGL', 'TCELL',
                     'BIMAS', 'ASELS', 'PGSUS']
        return symbol not in large_caps
    
    def _is_speculative_stock(self, symbol: str) -> bool:
        """Spekülatif hisse mi kontrol et - bugün tavan yapanlardan öğrendim"""
        speculative = ['GRNYO', 'PCILT', 'HUBVC', 'SKTAS', 'QUAGR', 'TSPOR', 
                      'YYAPI', 'MAKTK', 'EMKEL', 'DERIM', 'DGNMO', 'ENSRI',
                      'EKIZ', 'FZLGY', 'AVOD', 'IZMDC', 'YESIL', 'INVES',
                      'ADGYO', 'IZINV']  # IZINV de momentum hissesi oldu
        return symbol in speculative
    
    def _save_model(self):
        """Modeli kaydet"""
        try:
            with open(self.model_file, 'wb') as f:
                pickle.dump(self.model, f)
            logger.info("Model kaydedildi")
        except Exception as e:
            logger.error(f"Model kaydetme hatası: {e}")
    
    def _load_model(self):
        """Modeli yükle"""
        try:
            if os.path.exists(self.model_file):
                with open(self.model_file, 'rb') as f:
                    self.model = pickle.load(f)
                self.scaler = self.model.get('scaler', StandardScaler())
                self.model_trained = True
                logger.info("Model yüklendi")
            else:
                logger.info("Kayıtlı model bulunamadı")
        except Exception as e:
            logger.error(f"Model yükleme hatası: {e}")
    
    def rank_stocks_by_potential(self, stocks_analysis: List[Dict[str, Any]],
                               market_info: Dict[str, Any] = None,
                               sentiment_score: float = 0.5) -> List[Dict[str, Any]]:
        """Hisseleri gerçek tavan potansiyellerine göre sırala"""
        ranked_stocks = []
        
        # Piyasa durumunu kontrol et
        market_penalty = 0.0
        if market_info and market_info.get('xu100_change', 0) < -1.0:
            market_penalty = 0.2  # Düşüş piyasasında daha katı ol
        
        for stock_data in stocks_analysis:
            try:
                # Temel filtreleme - düşüş trendindeki hisseleri eleme
                price_change_1d = stock_data.get('price_change_1d', 0.0)
                price_change_5d = stock_data.get('price_change_5d', 0.0)
                
                # Düşüş trendindeki hisseleri direkt eleme
                if price_change_1d < -3.0 or price_change_5d < -8.0:
                    continue
                
                ceiling_prob = self.predict_ceiling_probability(
                    stock_data, market_info, sentiment_score
                )
                
                # Piyasa cezası uygula
                ceiling_prob = max(0.0, ceiling_prob - market_penalty)
                
                stock_data['ceiling_probability'] = ceiling_prob
                stock_data['prediction_score'] = ceiling_prob * 100
                
                # Sadece gerçekten potansiyelli olanları ekle
                if ceiling_prob > 0.5:  # %50'den yüksek potansiyel
                    ranked_stocks.append(stock_data)
                
            except Exception as e:
                logger.error(f"Hisse sıralama hatası: {e}")
                continue
        
        # Tahmin skoruna göre sırala
        ranked_stocks.sort(key=lambda x: x.get('prediction_score', 0), reverse=True)
        
        return ranked_stocks

# Test fonksiyonu
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    model = StockPredictionModel()
    
    # Test verisi
    test_analysis = {
        'rsi': 45.0,
        'macd': 0.5,
        'macd_signal': 0.3,
        'price_change_1d': 2.5,
        'price_change_5d': 8.0,
        'technical_score': 75.0,
        'volume_analysis': {'volume_ratio': 1.8, 'volume_signal': 'high'}
    }
    
    test_market = {'xu100_change': 1.5}
    test_sentiment = 0.7
    
    prob = model.predict_ceiling_probability(test_analysis, test_market, test_sentiment)
    print(f"\\nTavan yapma olasılığı: {prob:.3f} (%{prob*100:.1f})")
    print(f"Tahmin skoru: {prob*100:.1f}/100")