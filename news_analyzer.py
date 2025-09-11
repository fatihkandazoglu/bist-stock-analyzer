#!/usr/bin/env python3
"""
Haber Analizi Modülü
Bu modül finansal haberleri toplar ve analiz eder.
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import logging
from typing import List, Dict, Any, Optional
import re

logger = logging.getLogger(__name__)

class NewsAnalyzer:
    def __init__(self):
        """Haber analiz sınıfını başlat"""
        self.news_sources = {
            'investing': 'https://tr.investing.com/news/stock-market-news',
            'mynet_finans': 'https://finans.mynet.com/borsa/',
            'bigpara': 'https://bigpara.hurriyet.com.tr/haberler/'
        }
        
        # Pozitif/negatif anahtar kelimeler
        self.positive_keywords = [
            'artış', 'yükseliş', 'rekor', 'başarı', 'kazanç', 'büyüme', 
            'gelişme', 'iyileşme', 'pozitif', 'güçlü', 'hedef', 'yatırım'
        ]
        
        self.negative_keywords = [
            'düşüş', 'azalış', 'kayıp', 'kriz', 'sorun', 'zarar', 'risk',
            'olumsuz', 'negatif', 'zayıf', 'endişe', 'belirsizlik'
        ]
        
        # Şirket sembolleri ve isimleri eşleştirmesi
        self.company_mapping = {
            'akbank': 'AKBNK',
            'garanti': 'GARAN',
            'yapı kredi': 'YKBNK',
            'türk hava yolları': 'THYAO',
            'arçelik': 'ARCLK',
            'turkcell': 'TCELL',
            'aselsan': 'ASELS',
            'ereğli demir': 'EREGL',
            'petkim': 'PETKM',
            'pegasus': 'PGSUS'
        }
    
    def fetch_financial_news(self, days_back: int = 1) -> List[Dict[str, Any]]:
        """Finansal haberleri topla"""
        logger.info(f"Son {days_back} günün finansal haberleri toplanıyor...")
        
        all_news = []
        
        # Investing.com haberlerini çek
        investing_news = self._fetch_investing_news()
        all_news.extend(investing_news)
        
        # Bigpara haberlerini çek
        bigpara_news = self._fetch_bigpara_news()
        all_news.extend(bigpara_news)
        
        # Haberleri tarihe göre filtrele
        cutoff_date = datetime.now() - timedelta(days=days_back)
        filtered_news = [news for news in all_news if news.get('date', datetime.min) >= cutoff_date]
        
        logger.info(f"Toplam {len(filtered_news)} haber toplandı")
        return filtered_news
    
    def _fetch_investing_news(self) -> List[Dict[str, Any]]:
        """Investing.com'dan haberleri çek"""
        news_list = []
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(self.news_sources['investing'], headers=headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Haber başlıklarını bul (site yapısına göre ayarlanabilir)
                news_items = soup.find_all('article', class_='js-article-item')
                
                for item in news_items[:10]:  # Son 10 haberi al
                    try:
                        title_elem = item.find('a')
                        title = title_elem.text.strip() if title_elem else ""
                        
                        if title:
                            news_list.append({
                                'title': title,
                                'source': 'investing',
                                'date': datetime.now(),
                                'content': title  # Başlık içeriği olarak kullan
                            })
                            
                    except Exception as e:
                        logger.debug(f"Investing haber parse hatası: {e}")
                        continue
            
        except Exception as e:
            logger.error(f"Investing.com haber çekme hatası: {e}")
        
        return news_list
    
    def _fetch_bigpara_news(self) -> List[Dict[str, Any]]:
        """Bigpara'dan haberleri çek"""
        news_list = []
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            # Bigpara API benzeri endpoint (gerçek bir endpoint olabilir)
            response = requests.get(self.news_sources['bigpara'], headers=headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Haber başlıklarını bul
                news_items = soup.find_all('h3')
                
                for item in news_items[:5]:
                    try:
                        title = item.text.strip()
                        if title and len(title) > 10:
                            news_list.append({
                                'title': title,
                                'source': 'bigpara',
                                'date': datetime.now(),
                                'content': title
                            })
                            
                    except Exception as e:
                        logger.debug(f"Bigpara haber parse hatası: {e}")
                        continue
        
        except Exception as e:
            logger.error(f"Bigpara haber çekme hatası: {e}")
        
        return news_list
    
    def analyze_news_sentiment(self, news_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Haberlerin genel sentiment analizini yap"""
        if not news_list:
            return {'sentiment': 'neutral', 'score': 0.5, 'positive_count': 0, 'negative_count': 0}
        
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        
        for news in news_list:
            content = news.get('content', '').lower()
            title = news.get('title', '').lower()
            text = content + ' ' + title
            
            positive_score = sum(1 for keyword in self.positive_keywords if keyword in text)
            negative_score = sum(1 for keyword in self.negative_keywords if keyword in text)
            
            if positive_score > negative_score:
                positive_count += 1
            elif negative_score > positive_score:
                negative_count += 1
            else:
                neutral_count += 1
        
        total_news = len(news_list)
        positive_ratio = positive_count / total_news if total_news > 0 else 0
        negative_ratio = negative_count / total_news if total_news > 0 else 0
        
        # Genel sentiment belirleme
        if positive_ratio > 0.6:
            sentiment = 'very_positive'
        elif positive_ratio > 0.4:
            sentiment = 'positive'
        elif negative_ratio > 0.6:
            sentiment = 'very_negative'
        elif negative_ratio > 0.4:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        return {
            'sentiment': sentiment,
            'score': positive_ratio - negative_ratio + 0.5,  # 0-1 arası skor
            'positive_count': positive_count,
            'negative_count': negative_count,
            'neutral_count': neutral_count,
            'total_news': total_news
        }
    
    def find_stock_mentions(self, news_list: List[Dict[str, Any]]) -> Dict[str, List[Dict]]:
        """Haberlerde geçen hisse senetlerini bul"""
        stock_mentions = {}
        
        for news in news_list:
            content = news.get('content', '').lower()
            title = news.get('title', '').lower()
            text = content + ' ' + title
            
            for company_name, symbol in self.company_mapping.items():
                if company_name in text:
                    if symbol not in stock_mentions:
                        stock_mentions[symbol] = []
                    
                    # Sentiment analizi
                    positive_score = sum(1 for keyword in self.positive_keywords if keyword in text)
                    negative_score = sum(1 for keyword in self.negative_keywords if keyword in text)
                    
                    sentiment = 'positive' if positive_score > negative_score else 'negative' if negative_score > positive_score else 'neutral'
                    
                    stock_mentions[symbol].append({
                        'title': news.get('title', ''),
                        'source': news.get('source', ''),
                        'date': news.get('date', datetime.now()),
                        'sentiment': sentiment,
                        'relevance_score': positive_score + negative_score + 1
                    })
        
        return stock_mentions
    
    def get_market_sentiment_score(self) -> float:
        """Piyasa sentiment skorunu hesapla (0-1 arası)"""
        try:
            news = self.fetch_financial_news(days_back=1)
            sentiment_analysis = self.analyze_news_sentiment(news)
            return sentiment_analysis.get('score', 0.5)
            
        except Exception as e:
            logger.error(f"Market sentiment hesaplama hatası: {e}")
            return 0.5  # Nötr skor

# Test fonksiyonu
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    analyzer = NewsAnalyzer()
    
    # Test: Haberleri çek
    news = analyzer.fetch_financial_news()
    print(f"\\nToplam {len(news)} haber toplandı")
    
    # Test: Sentiment analizi
    sentiment = analyzer.analyze_news_sentiment(news)
    print(f"\\nPiyasa Sentimenti: {sentiment['sentiment']}")
    print(f"Pozitif/Negatif: {sentiment['positive_count']}/{sentiment['negative_count']}")
    
    # Test: Hisse bahisleri
    mentions = analyzer.find_stock_mentions(news)
    print(f"\\nHaberlerde bahsedilen hisseler: {list(mentions.keys())}")