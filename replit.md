# Overview

This is a Turkish stock market (BİST) analysis and prediction system that automatically analyzes BİST 100 stocks, predicts potential ceiling-breaking stocks, and sends daily reports via Telegram. The system combines technical analysis, news sentiment analysis, and machine learning predictions to identify promising investment opportunities.

The application runs on a scheduled basis (daily at 9:00 AM) and provides automated stock analysis with real-time notifications to users through Telegram integration.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Core Architecture Pattern
The system follows a modular architecture with specialized components for different aspects of stock analysis:

**Data Collection Layer**: Uses yfinance API to fetch real-time stock data from Yahoo Finance for BİST stocks with .IS suffix notation.

**Analysis Engine**: Implements multiple analysis strategies:
- Technical analysis using RSI, MACD, Bollinger Bands, and moving averages
- News sentiment analysis through web scraping of Turkish financial news sources
- Machine learning predictions using Random Forest and Gradient Boosting models

**Scheduling System**: Uses Python's schedule library for automated daily execution at 9:00 AM, with cron-like functionality for production deployment.

**Notification Layer**: Telegram bot integration for delivering analysis results to users in real-time.

## Data Flow Design
1. **Data Fetching**: BISTDataFetcher pulls stock data for predefined BİST 100 symbols
2. **Technical Analysis**: TechnicalAnalyzer calculates various technical indicators
3. **News Analysis**: NewsAnalyzer scrapes and analyzes financial news sentiment
4. **Prediction**: StockPredictionModel combines all inputs to predict stock performance
5. **Notification**: TelegramNotifier formats and sends results to users

## Machine Learning Architecture
The prediction model uses sklearn with feature engineering that combines:
- Technical indicators (RSI, MACD, price changes)
- Volume analysis ratios
- Market sentiment scores
- News sentiment analysis

Models are persistently stored using pickle for training continuity across runs.

## Error Handling Strategy
Comprehensive logging system with both file and console output, graceful fallbacks for missing data, and retry mechanisms for external API calls.

# External Dependencies

## Financial Data APIs
- **Yahoo Finance (yfinance)**: Primary data source for BİST stock prices, volumes, and historical data
- **Turkish Financial News Sources**: Web scraping targets including Investing.com, Mynet Finans, and BigPara

## Machine Learning Stack
- **scikit-learn**: Random Forest and Gradient Boosting for stock prediction models
- **pandas/numpy**: Data manipulation and numerical computations
- **ta (Technical Analysis)**: Technical indicator calculations

## Communication Services
- **Telegram Bot API**: Real-time notification delivery system requiring bot token and chat ID configuration

## Web Technologies
- **requests**: HTTP client for API calls and web scraping
- **BeautifulSoup4**: HTML parsing for news content extraction
- **aiohttp**: Asynchronous HTTP operations

## Scheduling and Environment
- **schedule**: Cron-like job scheduling for daily analysis execution
- **python-dotenv**: Environment variable management for API keys and configuration
- **asyncio**: Asynchronous programming support for concurrent operations

## Visualization (Optional)
- **matplotlib/seaborn**: Chart generation capabilities for technical analysis visualization