"""
Real-Time SPX EMA Probability API Integration Script
Pulls live data, calculates probability scores, and triggers Discord alerts
"""

import asyncio
import aiohttp
import websockets
import json
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple
import requests
from concurrent.futures import ThreadPoolExecutor
import signal
import sys

# Import our probability scorer
from ema_probability_algorithm import EMAProbabilityScorer, EMAData, SMAData, ContractSelector

# ============================================================================
# CONFIGURATION
# ============================================================================

@dataclass
class Config:
    """Configuration settings"""
    # API Keys (replace with your actual keys)
    ALPHA_VANTAGE_KEY: str = "YOUR_ALPHA_VANTAGE_API_KEY"
    POLYGON_API_KEY: str = "YOUR_POLYGON_API_KEY"
    TRADIER_TOKEN: str = "YOUR_TRADIER_ACCESS_TOKEN"
    
    # Discord Webhook
    DISCORD_WEBHOOK_URL: str = "https://discord.com/api/webhooks/1413434367853990019/QBe2jVMUDxt5x42ZNlWWxzHrexyq2oxW1OwT1-xwXbg5fY9CDIeYNDWfCYg7Vqxfdbtr"
    
    # Refresh intervals
    FAST_REFRESH_INTERVAL: float = 1.0  # 1 second for EMA strength alerts
    SCALP_REFRESH_INTERVAL: float = 10.0  # 10 seconds for scalping confirmation
    ANALYSIS_REFRESH_INTERVAL: float = 30.0  # 30 seconds for full analysis
    
    # Alert thresholds
    HIGH_PROBABILITY_THRESHOLD: float = 75.0
    MOMENTUM_ALERT_THRESHOLD: float = 70.0
    
    # Symbols
    SPX_SYMBOL: str = "SPX"
    SPY_SYMBOL: str = "SPY"
    SPXW_SYMBOL: str = "SPXW"

class DataFeedManager:
    """Manages multiple data feed connections"""
    
    def __init__(self, config: Config):
        self.config = config
        self.session = None
        self.websocket_connections = {}
        self.last_data = {}
        self.data_callbacks = []
        
    async def initialize(self):
        """Initialize API connections"""
        self.session = aiohttp.ClientSession()
        
        # Initialize WebSocket connections for real-time data
        await self._setup_websocket_feeds()
        
    async def _setup_websocket_feeds(self):
        """Setup WebSocket connections for real-time feeds"""
        try:
            # Polygon WebSocket for real-time SPX data
            if self.config.POLYGON_API_KEY:
                polygon_ws_url = f"wss://socket.polygon.io/indices"
                self.websocket_connections['polygon'] = await websockets.connect(
                    polygon_ws_url,
                    extra_headers={"Authorization": f"Bearer {self.config.POLYGON_API_KEY}"}
                )
                
                # Subscribe to SPX real-time data
                subscribe_msg = {
                    "action": "auth",
                    "params": self.config.POLYGON_API_KEY
                }
                await self.websocket_connections['polygon'].send(json.dumps(subscribe_msg))
                
                subscribe_msg = {
                    "action": "subscribe",
                    "params": "A.SPX,T.SPY"  # Aggregate and trade data
                }
                await self.websocket_connections['polygon'].send(json.dumps(subscribe_msg))
                
        except Exception as e:
            logging.error(f"Error setting up WebSocket feeds: {e}")
            
    async def get_current_spx_data(self) -> Optional[Dict]:
        """Get current SPX price and basic data"""
        try:
            # Try Polygon first (most reliable for SPX)
            if self.config.POLYGON_API_KEY:
                url = f"https://api.polygon.io/v2/aggs/ticker/{self.config.SPX_SYMBOL}/prev"
                params = {"apikey": self.config.POLYGON_API_KEY}
                
                async with self.session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("status") == "OK" and data.get("results"):
                            result = data["results"][0]
                            return {
                                "symbol": self.config.SPX_SYMBOL,
                                "price": result["c"],  # close price
                                "volume": result["v"],
                                "high": result["h"],
                                "low": result["l"],
                                "open": result["o"],
                                "timestamp": datetime.now()
                            }
                            
            # Fallback to Alpha Vantage
            if self.config.ALPHA_VANTAGE_KEY:
                url = "https://www.alphavantage.co/query"
                params = {
                    "function": "GLOBAL_QUOTE",
                    "symbol": self.config.SPX_SYMBOL,
                    "apikey": self.config.ALPHA_VANTAGE_KEY
                }
                
                async with self.session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        quote = data.get("Global Quote", {})
                        if quote:
                            return {
                                "symbol": self.config.SPX_SYMBOL,
                                "price": float(quote.get("05. price", 0)),
                                "volume": float(quote.get("06. volume", 0)),
                                "timestamp": datetime.now()
                            }
                            
        except Exception as e:
            logging.error(f"Error fetching SPX data: {e}")
            
        return None
        
    async def get_timeframe_data(self, symbol: str, timeframe: str, periods: int = 200) -> Optional[pd.DataFrame]:
        """Get historical data for EMA calculations"""
        try:
            # Convert timeframe to API format
            interval_map = {
                "1min": "1min",
                "2min": "2min", 
                "5min": "5min",
                "10min": "10min",
                "15min": "15min",
                "30min": "30min"
            }
            
            interval = interval_map.get(timeframe, "5min")
            
            if self.config.POLYGON_API_KEY:
                # Calculate date range
                end_date = datetime.now()
                start_date = end_date - timedelta(days=7)  # Get last 7 days of data
                
                url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/{interval}/{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}"
                params = {
                    "apikey": self.config.POLYGON_API_KEY,
                    "adjusted": "true",
                    "sort": "asc",
                    "limit": periods
                }
                
                async with self.session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("status") == "OK" and data.get("results"):
                            results = data["results"]
                            df = pd.DataFrame(results)
                            df.columns = ['volume', 'volume_weighted', 'open', 'close', 'high', 'low', 'timestamp', 'transactions']
                            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                            df.set_index('timestamp', inplace=True)
                            return df.tail(periods)
                            
        except Exception as e:
            logging.error(f"Error fetching timeframe data: {e}")
            
        return None
        
    async def get_spy_order_book(self) -> Optional[Dict]:
        """Get SPY bid/ask data as proxy for market sentiment"""
        try:
            if self.config.TRADIER_TOKEN:
                url = "https://api.tradier.com/v1/markets/quotes"
                headers = {
                    "Authorization": f"Bearer {self.config.TRADIER_TOKEN}",
                    "Accept": "application/json"
                }
                params = {"symbols": self.config.SPY_SYMBOL, "greeks": "false"}
                
                async with self.session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        quote = data.get("quotes", {}).get("quote", {})
                        if quote:
                            return {
                                "bid": float(quote.get("bid", 0)),
                                "ask": float(quote.get("ask", 0)),
                                "bid_size": int(quote.get("bidsize", 0)),
                                "ask_size": int(quote.get("asksize", 0)),
                                "last": float(quote.get("last", 0)),
                                "volume": int(quote.get("volume", 0))
                            }
                            
        except Exception as e:
            logging.error(f"Error fetching SPY order book: {e}")
            
        return None

class EMACalculator:
    """Real-time EMA calculations with optimized performance"""
    
    def __init__(self):
        self.ema_cache = {}  # Cache EMA values for performance
        
    def calculate_ema(self, data: pd.Series, period: int) -> pd.Series:
        """Calculate EMA with caching"""
        cache_key = f"{id(data)}_{period}"
        
        if cache_key in self.ema_cache:
            cached_ema = self.ema_cache[cache_key]
            # Only calculate new values if data has new entries
            if len(data) > len(cached_ema):
                new_data = data.iloc[len(cached_ema):]
                alpha = 2 / (period + 1)
                last_ema = cached_ema.iloc[-1]
                
                new_emas = []
                for price in new_data:
                    last_ema = alpha * price + (1 - alpha) * last_ema
                    new_emas.append(last_ema)
                
                updated_ema = pd.concat([cached_ema, pd.Series(new_emas, index=new_data.index)])
                self.ema_cache[cache_key] = updated_ema
                return updated_ema
            else:
                return cached_ema
        else:
            # Calculate full EMA
            ema = data.ewm(span=period, adjust=False).mean()
            self.ema_cache[cache_key] = ema
            return ema
    
    def get_current_emas(self, df: pd.DataFrame) -> Dict[str, float]:
        """Get current EMA values for all periods"""
        if df is None or len(df) < 200:
            return {}
            
        close_prices = df['close']
        
        return {
            'ema_9': self.calculate_ema(close_prices, 9).iloc[-1],
            'ema_21': self.calculate_ema(close_prices, 21).iloc[-1],
            'ema_50': self.calculate_ema(close_prices, 50).iloc[-1],
            'ema_200': self.calculate_ema(close_prices, 200).iloc[-1]
        }
    
    def get_current_smas(self, df: pd.DataFrame) -> Dict[str, float]:
        """Get current SMA values for confluence analysis"""
        if df is None or len(df) < 200:
            return {}
            
        close_prices = df['close']
        
        return {
            'sma_20': close_prices.rolling(20).mean().iloc[-1],
            'sma_50': close_prices.rolling(50).mean().iloc[-1],
            'sma_100': close_prices.rolling(100).mean().iloc[-1],
            'sma_200': close_prices.rolling(200).mean().iloc[-1]
        }

class DiscordAlerter:
    """Handle Discord webhook alerts"""
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
        self.last_alert_time = {}
        self.alert_cooldown = 30  # 30 second cooldown between similar alerts
        
    async def send_ema_alert(self, session: aiohttp.ClientSession, 
                           alert_type: str, probability_data: Dict, 
                           contract_data: Optional[Dict] = None):
        """Send EMA-based alert to Discord"""
        
        # Check cooldown
        cooldown_key = f"{alert_type}_{probability_data.get('direction', 'UNKNOWN')}"
        current_time = time.time()
        
        if cooldown_key in self.last_alert_time:
            if current_time - self.last_alert_time[cooldown_key] < self.alert_cooldown:
                return  # Skip alert due to cooldown
                
        self.last_alert_time[cooldown_key] = current_time
        
        # Format alert based on type
        if alert_type == "HIGH_PROBABILITY":
            embed = self._create_high_prob_embed(probability_data, contract_data)
        elif alert_type == "MOMENTUM_ACCELERATION":
            embed = self._create_momentum_embed(probability_data)
        elif alert_type == "EMA_CROSS":
            embed = self._create_cross_embed(probability_data)
        else:
            embed = self._create_generic_embed(probability_data)
            
        payload = {
            "username": "SPX EMA Probability Bot",
            "embeds": [embed]
        }
        
        try:
            async with session.post(self.webhook_url, json=payload) as response:
                if response.status == 204:
                    logging.info(f"Successfully sent {alert_type} alert to Discord")
                else:
                    logging.error(f"Failed to send Discord alert: {response.status}")
                    
        except Exception as e:
            logging.error(f"Error sending Discord alert: {e}")
    
    def _create_high_prob_embed(self, prob_data: Dict, contract_data: Dict) -> Dict:
        """Create high probability setup embed"""
        direction = prob_data.get('direction', 'UNKNOWN')
        score = prob_data.get('final_score', 0)
        
        color = 3447003 if direction == 'BULLISH' else 15158332  # Blue for bullish, red for bearish
        
        embed = {
            "title": f"🚨 HIGH PROBABILITY SPX SETUP - {direction}",
            "description": f"**Probability Score: {score:.1f}%**\n{prob_data.get('recommendation', '')}",
            "color": color,
            "timestamp": datetime.utcnow().isoformat(),
            "fields": []
        }
        
        if contract_data:
            embed["fields"].extend([
                {
                    "name": "📱 Contract",
                    "value": f"`{contract_data.get('tradingview_code', 'N/A')}`",
                    "inline": True
                },
                {
                    "name": "💰 Entry Range",
                    "value": f"${contract_data.get('premium_range', 'N/A')}",
                    "inline": True
                },
                {
                    "name": "🎯 Target",
                    "value": contract_data.get('target_profit', 'N/A'),
                    "inline": True
                }
            ])
            
        # Component scores
        components = prob_data.get('component_scores', {})
        embed["fields"].extend([
            {
                "name": "📊 Multi-Timeframe",
                "value": f"{components.get('multi_timeframe', 0):.1f}",
                "inline": True
            },
            {
                "name": "🔗 SMA Confluence",
                "value": f"{components.get('sma_confluence', 0):.1f}",
                "inline": True
            },
            {
                "name": "📈 Volume Score",
                "value": f"{components.get('volume_confirmation', 0):.1f}",
                "inline": True
            }
        ])
        
        return embed
    
    def _create_momentum_embed(self, prob_data: Dict) -> Dict:
        """Create momentum acceleration embed"""
        direction = prob_data.get('direction', 'UNKNOWN')
        momentum = prob_data.get('momentum_score', 0)
        
        return {
            "title": f"⚡ EMA MOMENTUM ACCELERATION - {direction}",
            "description": f"**Momentum Score: {momentum:.1f}**\nFast EMA acceleration detected",
            "color": 16776960,  # Yellow for momentum alerts
            "timestamp": datetime.utcnow().isoformat(),
            "fields": [
                {
                    "name": "🕐 Timeframe",
                    "value": "1-10 second scalp window",
                    "inline": True
                },
                {
                    "name": "🎯 Action",
                    "value": f"Watch for {direction.lower()} continuation",
                    "inline": True
                }
            ]
        }
    
    def _create_cross_embed(self, prob_data: Dict) -> Dict:
        """Create EMA cross embed"""
        cross_type = prob_data.get('cross_type', 'UNKNOWN')
        
        return {
            "title": f"🔄 EMA 9/21 CROSS - {cross_type}",
            "description": "EMA crossover detected - momentum shift in progress",
            "color": 8359053,  # Purple for cross alerts
            "timestamp": datetime.utcnow().isoformat(),
            "fields": [
                {
                    "name": "📊 Signal",
                    "value": f"EMA 9 crossed {'above' if cross_type == 'BULLISH' else 'below'} EMA 21",
                    "inline": False
                }
            ]
        }
    
    def _create_generic_embed(self, prob_data: Dict) -> Dict:
        """Create generic alert embed"""
        return {
            "title": "📊 SPX EMA Update",
            "description": f"Score: {prob_data.get('final_score', 0):.1f}% | Direction: {prob_data.get('direction', 'UNKNOWN')}",
            "color": 7506394,  # Neutral gray
            "timestamp": datetime.utcnow().isoformat()
        }

class RealTimeEMAMonitor:
    """Main monitoring class that coordinates all components"""
    
    def __init__(self, config: Config):
        self.config = config
        self.data_manager = DataFeedManager(config)
        self.ema_calculator = EMACalculator()
        self.probability_scorer = EMAProbabilityScorer()
        self.contract_selector = ContractSelector()
        self.discord_alerter = DiscordAlerter(config.DISCORD_WEBHOOK_URL)
        
        self.running = False
        self.last_probability_score = None
        self.last_ema_cross = None
        
        # Performance tracking
        self.performance_stats = {
            'calculations_per_second': 0,
            'api_calls_per_minute': 0,
            'last_update_time': None
        }
        
    async def start_monitoring(self):
        """Start the real-time monitoring system"""
        logging.info("Starting SPX EMA Real-Time Monitoring System")
        
        await self.data_manager.initialize()
        self.running = True
        
        # Start concurrent monitoring tasks
        tasks = [
            asyncio.create_task(self._fast_ema_monitor()),      # 1-second refresh
            asyncio.create_task(self._scalp_monitor()),         # 10-second refresh  
            asyncio.create_task(self._analysis_monitor()),      # 30-second refresh
            asyncio.create_task(self._performance_monitor()),   # Monitor system performance
        ]
        
        try:
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            logging.info("Shutting down monitoring system...")
            self.running = False
            
    async def _fast_ema_monitor(self):
        """1-second EMA strength monitoring for ultra-fast scalping"""
        while self.running:
            try:
                start_time = time.time()
                
                # Get current SPX data
                spx_data = await self.data_manager.get_current_spx_data()
                if not spx_data:
                    await asyncio.sleep(self.config.FAST_REFRESH_INTERVAL)
                    continue
                
                # Get 1-minute timeframe data for fast EMA calculations
                df_1m = await self.data_manager.get_timeframe_data(self.config.SPX_SYMBOL, "1min", 50)
                if df_1m is None or len(df_1m) < 21:
                    await asyncio.sleep(self.config.FAST_REFRESH_INTERVAL)
                    continue
                
                # Calculate fast EMAs (9, 21)
                emas = self.ema_calculator.get_current_emas(df_1m)
                current_price = spx_data['price']
                
                # Check for EMA crosses
                ema_9_current = emas.get('ema_9', 0)
                ema_21_current = emas.get('ema_21', 0)
                
                # Get previous values for cross detection
                if len(df_1m) >= 2:
                    prev_close = df_1m['close'].iloc[-2]
                    prev_ema_9 = self.ema_calculator.calculate_ema(df_1m['close'].iloc[:-1], 9).iloc[-1]
                    prev_ema_21 = self.ema_calculator.calculate_ema(df_1m['close'].iloc[:-1], 21).iloc[-1]
                    
                    # Detect crosses
                    bullish_cross = (prev_ema_9 <= prev_ema_21) and (ema_9_current > ema_21_current)
                    bearish_cross = (prev_ema_9 >= prev_ema_21) and (ema_9_current < ema_21_current)
                    
                    if bullish_cross or bearish_cross:
                        cross_type = "BULLISH" if bullish_cross else "BEARISH"
                        if self.last_ema_cross != cross_type:  # Avoid duplicate alerts
                            self.last_ema_cross = cross_type
                            
                            alert_data = {
                                'cross_type': cross_type,
                                'ema_9': ema_9_current,
                                'ema_21': ema_21_current,
                                'price': current_price,
                                'timestamp': datetime.now().isoformat()
                            }
                            
                            await self.discord_alerter.send_ema_alert(
                                self.data_manager.session, "EMA_CROSS", alert_data
                            )
                
                # Calculate momentum acceleration
                if len(df_1m) >= 3:
                    momentum_score = self._calculate_fast_momentum(df_1m, emas)
                    
                    if momentum_score > self.config.MOMENTUM_ALERT_THRESHOLD:
                        direction = "BULLISH" if ema_9_current > ema_21_current else "BEARISH"
                        
                        momentum_data = {
                            'direction': direction,
                            'momentum_score': momentum_score,
                            'ema_9': ema_9_current,
                            'ema_21': ema_21_current,
                            'price': current_price
                        }
                        
                        await self.discord_alerter.send_ema_alert(
                            self.data_manager.session, "MOMENTUM_ACCELERATION", momentum_data
                        )
                
                # Performance tracking
                self.performance_stats['calculations_per_second'] = 1 / (time.time() - start_time)
                
                await asyncio.sleep(self.config.FAST_REFRESH_INTERVAL)
                
            except Exception as e:
                logging.error(f"Error in fast EMA monitor: {e}")
                await asyncio.sleep(self.config.FAST_REFRESH_INTERVAL)
    
    async def _scalp_monitor(self):
        """10-second scalping confirmation monitor"""
        while self.running:
            try:
                # Get multi-timeframe data for scalping analysis
                timeframes = ["5min", "10min", "15min"]
                timeframe_data = {}
                
                for tf in timeframes:
                    df = await self.data_manager.get_timeframe_data(self.config.SPX_SYMBOL, tf, 200)
                    if df is not None:
                        emas = self.ema_calculator.get_current_emas(df)
                        if emas:
                            timeframe_data[tf] = EMAData(
                                ema_9=emas['ema_9'],
                                ema_21=emas['ema_21'],
                                ema_50=emas['ema_50'],
                                ema_200=emas['ema_200'],
                                price=df['close'].iloc[-1],
                                volume=df['volume'].iloc[-1],
                                timestamp=datetime.now().isoformat()
                            )
                
                if timeframe_data:
                    # Calculate quick probability for scalping
                    mtf_result = self.probability_scorer.calculate_multi_timeframe_score(
                        timeframe_data, {}
                    )
                    
                    if mtf_result['total_score'] >= 70:  # Lower threshold for scalping
                        logging.info(f"Scalping opportunity: {mtf_result['total_score']:.1f}% - {mtf_result['direction']}")
                
                await asyncio.sleep(self.config.SCALP_REFRESH_INTERVAL)
                
            except Exception as e:
                logging.error(f"Error in scalp monitor: {e}")
                await asyncio.sleep(self.config.SCALP_REFRESH_INTERVAL)
    
    async def _analysis_monitor(self):
        """30-second full probability analysis"""
        while self.running:
            try:
                # Get comprehensive multi-timeframe data
                timeframes = ["1min", "5min", "10min", "15min", "30min"]
                timeframe_data = {}
                timeframe_history = {}
                
                for tf in timeframes:
                    df = await self.data_manager.get_timeframe_data(self.config.SPX_SYMBOL, tf, 200)
                    if df is not None and len(df) >= 200:
                        emas = self.ema_calculator.get_current_emas(df)
                        smas = self.ema_calculator.get_current_smas(df)
                        
                        if emas:
                            timeframe_data[tf] = EMAData(
                                ema_9=emas['ema_9'],
                                ema_21=emas['ema_21'],
                                ema_50=emas['ema_50'],
                                ema_200=emas['ema_200'],
                                price=df['close'].iloc[-1],
                                volume=df['volume'].iloc[-1],
                                timestamp=datetime.now().isoformat()
                            )
                            
                            # Get SMA data for confluence analysis
                            if tf == "5min" and smas:  # Use 5min as primary for SMA confluence
                                sma_data = SMAData(
                                    sma_20=smas['sma_20'],
                                    sma_50=smas['sma_50'],
                                    sma_100=smas['sma_100'],
                                    sma_200=smas['sma_200']
                                )
                
                if len(timeframe_data) >= 3:  # Need at least 3 timeframes
                    # Get volume history for volume analysis
                    volume_history = []
                    if "5min" in timeframe_data:
                        df_5m = await self.data_manager.get_timeframe_data(self.config.SPX_SYMBOL, "5min", 50)
                        if df_5m is not None:
                            volume_history = df_5m['volume'].tolist()
                    
                    # Calculate full probability analysis
                    probability_result = self.probability_scorer.calculate_final_probability(
                        timeframe_data, timeframe_history, 
                        sma_data if 'sma_data' in locals() else SMAData(0,0,0,0), 
                        volume_history
                    )
                    
                    # Check for high probability setups
                    if probability_result['final_score'] >= self.config.HIGH_PROBABILITY_THRESHOLD:
                        # Get current SPX price for contract selection
                        spx_data = await self.data_manager.get_current_spx_data()
                        current_price = spx_data['price'] if spx_data else 6450  # Default fallback
                        
                        # Mock option chain data (replace with real API call)
                        mock_strikes = self._generate_mock_option_strikes(current_price)
                        
                        # Select optimal contract
                        contract_selection = self.contract_selector.select_optimal_contract(
                            probability_result, current_price, mock_strikes
                        )
                        
                        if 'error' not in contract_selection:
                            # Generate TradingView code
                            contract_selection['tradingview_code'] = self._generate_tradingview_code(
                                contract_selection, current_price
                            )
                            
                            # Send high probability alert
                            await self.discord_alerter.send_ema_alert(
                                self.data_manager.session, "HIGH_PROBABILITY", 
                                probability_result, contract_selection
                            )
                    
                    self.last_probability_score = probability_result
                    self.performance_stats['last_update_time'] = datetime.now()
                    
                    logging.info(f"Probability Analysis: {probability_result['final_score']:.1f}% - "
                               f"{probability_result['direction']} - {probability_result['recommendation']}")
                
                await asyncio.sleep(self.config.ANALYSIS_REFRESH_INTERVAL)
                
            except Exception as e:
                logging.error(f"Error in analysis monitor: {e}")
                await asyncio.sleep(self.config.ANALYSIS_REFRESH_INTERVAL)
    
    async def _performance_monitor(self):
        """Monitor system performance and health"""
        while self.running:
            try:
                # Log performance statistics
                stats = self.performance_stats
                logging.info(f"Performance - Calc/s: {stats['calculations_per_second']:.2f}, "
                           f"Last Update: {stats.get('last_update_time', 'Never')}")
                
                # Monitor memory usage, API rate limits, etc.
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logging.error(f"Error in performance monitor: {e}")
                await asyncio.sleep(60)
    
    def _calculate_fast_momentum(self, df: pd.DataFrame, emas: Dict[str, float]) -> float:
        """Calculate momentum for 1-second alerts"""
        if len(df) < 3:
            return 0
            
        # Calculate recent price momentum
        recent_close = df['close'].iloc[-1]
        prev_close = df['close'].iloc[-2]
        price_change = abs(recent_close - prev_close)
        
        # Calculate EMA slope
        ema_9_slope = emas['ema_9'] - df['close'].ewm(span=9).mean().iloc[-2]
        ema_21_slope = emas['ema_21'] - df['close'].ewm(span=21).mean().iloc[-2]
        
        # Momentum score
        momentum = (abs(ema_9_slope - ema_21_slope) * 100) + (price_change * 10)
        return min(100, momentum)
    
    def _generate_mock_option_strikes(self, current_price: float) -> List[Dict]:
        """Generate mock option chain data (replace with real API)"""
        strikes = []
        base_strike = int(current_price / 5) * 5  # Round to nearest 5
        
        for i in range(-10, 11):  # 21 strikes around current price
            strike_price = base_strike + (i * 5)
            
            # Mock premium calculation (very simplified)
            distance_from_money = abs(strike_price - current_price)
            base_premium = max(0.5, 5 - (distance_from_money * 0.1))
            
            # Adjust premium to fit $1-4 range
            if base_premium > 4:
                base_premium = 4
            elif base_premium < 1:
                base_premium = max(0.5, base_premium)
            
            # Mock delta calculation
            delta = max(0.05, 0.5 - (distance_from_money * 0.02))
            if strike_price > current_price:
                delta = -delta  # Put delta
            
            strikes.append({
                'strike': strike_price,
                'premium': round(base_premium, 2),
                'delta': round(delta, 3),
                'volume': 100 + (i * 10),
                'open_interest': 500 + (i * 50)
            })
        
        return [s for s in strikes if 1 <= s['premium'] <= 4]
    
    def _generate_tradingview_code(self, contract_data: Dict, current_price: float) -> str:
        """Generate TradingView option symbol code"""
        contract_type = contract_data.get('contract_type', 'CALL')
        strike = contract_data['selected_strike']['strike']
        
        # Get current date for 0DTE
        today = datetime.now()
        date_str = today.strftime('%y%m%d')
        
        # Format: SPXWYYMMDDCXXXX.0 or SPXWYYMMDDPXXXX.0
        option_type = 'C' if contract_type == 'CALL' else 'P'
        strike_str = f"{int(strike):04d}"
        
        return f"SPXW{date_str}{option_type}{strike_str}.0"

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('spx_ema_monitor.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    logging.info("Received shutdown signal, stopping monitor...")
    sys.exit(0)

async def main():
    """Main entry point"""
    setup_logging()
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Load configuration
    config = Config()
    
    # Validate configuration
    if not any([config.ALPHA_VANTAGE_KEY, config.POLYGON_API_KEY, config.TRADIER_TOKEN]):
        logging.error("No API keys configured. Please add at least one API key.")
        return
    
    # Start monitoring system
    monitor = RealTimeEMAMonitor(config)
    
    try:
        await monitor.start_monitoring()
    except KeyboardInterrupt:
        logging.info("Monitor stopped by user")
    except Exception as e:
        logging.error(f"Monitor crashed: {e}")
    finally:
        if monitor.data_manager.session:
            await monitor.data_manager.session.close()

if __name__ == "__main__":
    asyncio.run(main())