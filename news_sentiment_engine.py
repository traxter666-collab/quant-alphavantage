#!/usr/bin/env python3
"""
News Sentiment Analysis Engine
Real-time news analysis with market impact assessment and sentiment scoring
"""

import json
import os
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import statistics

@dataclass
class NewsItem:
    """Individual news item with analysis"""
    timestamp: str
    title: str
    summary: str
    source: str
    relevance_score: float
    sentiment_score: float
    market_impact: str
    keywords: List[str]
    confidence: float

@dataclass
class SentimentSignal:
    """Sentiment-based trading signal"""
    signal_type: str
    strength: float
    direction: str
    reasoning: str
    time_horizon: str
    confidence: float

class NewsSentimentEngine:
    """Advanced news sentiment analysis with market impact assessment"""

    def __init__(self):
        self.news_history_file = ".spx/news_history.json"
        self.sentiment_analysis_file = ".spx/sentiment_analysis.json"
        self.keyword_weights_file = ".spx/keyword_weights.json"
        self.load_configuration()

    def load_configuration(self):
        """Load news analysis configuration"""
        try:
            if os.path.exists(self.keyword_weights_file):
                with open(self.keyword_weights_file, 'r') as f:
                    self.keyword_weights = json.load(f)
            else:
                self.keyword_weights = self.initialize_keyword_weights()

            if os.path.exists(self.news_history_file):
                with open(self.news_history_file, 'r') as f:
                    self.news_history = json.load(f)
            else:
                self.news_history = []

        except Exception as e:
            print(f"Error loading news configuration: {e}")
            self.keyword_weights = self.initialize_keyword_weights()
            self.news_history = []

    def initialize_keyword_weights(self) -> Dict:
        """Initialize keyword weighting system"""
        return {
            "bullish_keywords": {
                "strong": ["breakout", "surge", "rally", "bullish", "optimistic", "growth", "expansion", "boom"],
                "medium": ["rise", "gain", "increase", "positive", "strong", "solid", "healthy"],
                "weak": ["stable", "steady", "maintains", "holds", "continues"]
            },
            "bearish_keywords": {
                "strong": ["crash", "plunge", "collapse", "bearish", "pessimistic", "recession", "crisis", "panic"],
                "medium": ["fall", "drop", "decline", "negative", "weak", "concern", "worry"],
                "weak": ["soft", "cautious", "uncertain", "mixed", "volatile"]
            },
            "volatility_keywords": {
                "high": ["volatile", "uncertainty", "crisis", "panic", "turmoil", "chaos"],
                "medium": ["fluctuation", "swing", "change", "shift", "movement"],
                "low": ["stable", "calm", "steady", "quiet", "range-bound"]
            },
            "market_moving_topics": {
                "federal_reserve": 2.0,
                "interest_rates": 2.0,
                "inflation": 1.8,
                "employment": 1.5,
                "gdp": 1.5,
                "earnings": 1.3,
                "geopolitical": 1.4,
                "oil": 1.2,
                "china": 1.3,
                "technology": 1.1
            },
            "source_credibility": {
                "reuters": 1.0,
                "bloomberg": 1.0,
                "wsj": 0.95,
                "cnbc": 0.9,
                "marketwatch": 0.85,
                "yahoo": 0.7,
                "social_media": 0.3
            }
        }

    def analyze_news_sentiment(self, news_data: List[Dict]) -> Dict:
        """Comprehensive news sentiment analysis"""
        try:
            if not news_data:
                return self.get_default_sentiment_analysis()

            # Process individual news items
            processed_news = []
            for item in news_data:
                processed_item = self.process_news_item(item)
                if processed_item:
                    processed_news.append(processed_item)

            if not processed_news:
                return self.get_default_sentiment_analysis()

            # Calculate aggregate sentiment
            aggregate_sentiment = self.calculate_aggregate_sentiment(processed_news)

            # Generate sentiment signals
            sentiment_signals = self.generate_sentiment_signals(processed_news, aggregate_sentiment)

            # Analyze news flow patterns
            flow_analysis = self.analyze_news_flow_patterns(processed_news)

            # Calculate market impact assessment
            market_impact = self.assess_market_impact(processed_news, aggregate_sentiment)

            # Generate trading recommendations
            trading_recommendations = self.generate_news_trading_recommendations(
                sentiment_signals, market_impact, flow_analysis
            )

            analysis = {
                "timestamp": datetime.now().isoformat(),
                "total_news_items": len(processed_news),
                "aggregate_sentiment": aggregate_sentiment,
                "sentiment_signals": [signal.__dict__ for signal in sentiment_signals],
                "news_flow_analysis": flow_analysis,
                "market_impact_assessment": market_impact,
                "trading_recommendations": trading_recommendations,
                "top_news_items": [item.__dict__ for item in processed_news[:5]],  # Top 5 by relevance
                "sentiment_distribution": self.calculate_sentiment_distribution(processed_news)
            }

            # Save analysis
            self.save_sentiment_analysis(analysis)

            return analysis

        except Exception as e:
            print(f"Error in news sentiment analysis: {e}")
            return self.get_default_sentiment_analysis()

    def process_news_item(self, news_item: Dict) -> Optional[NewsItem]:
        """Process individual news item"""
        try:
            title = news_item.get('title', '')
            summary = news_item.get('summary', '')
            source = news_item.get('source', 'unknown')
            timestamp = news_item.get('time_published', datetime.now().isoformat())

            if not title and not summary:
                return None

            # Calculate relevance score
            relevance_score = self.calculate_relevance_score(title, summary)

            # Skip low relevance items
            if relevance_score < 0.3:
                return None

            # Calculate sentiment score
            sentiment_score = self.calculate_sentiment_score(title, summary)

            # Determine market impact
            market_impact = self.determine_market_impact(title, summary, sentiment_score)

            # Extract keywords
            keywords = self.extract_keywords(title, summary)

            # Calculate confidence
            confidence = self.calculate_confidence(source, relevance_score, sentiment_score)

            return NewsItem(
                timestamp=timestamp,
                title=title,
                summary=summary,
                source=source,
                relevance_score=relevance_score,
                sentiment_score=sentiment_score,
                market_impact=market_impact,
                keywords=keywords,
                confidence=confidence
            )

        except Exception as e:
            print(f"Error processing news item: {e}")
            return None

    def calculate_relevance_score(self, title: str, summary: str) -> float:
        """Calculate how relevant news is to trading"""
        text = (title + " " + summary).lower()
        score = 0.0

        # Market-moving topics
        for topic, weight in self.keyword_weights["market_moving_topics"].items():
            if topic in text:
                score += weight * 0.3

        # Market-specific keywords
        market_keywords = [
            "market", "stock", "trading", "index", "dow", "s&p", "nasdaq",
            "federal reserve", "fed", "interest rate", "inflation", "economy"
        ]

        for keyword in market_keywords:
            if keyword in text:
                score += 0.2

        # SPX-specific keywords
        spx_keywords = ["s&p 500", "spx", "spy", "large cap", "blue chip"]
        for keyword in spx_keywords:
            if keyword in text:
                score += 0.4

        return min(score, 1.0)

    def calculate_sentiment_score(self, title: str, summary: str) -> float:
        """Calculate sentiment score (-1 to +1)"""
        text = (title + " " + summary).lower()
        sentiment_score = 0.0
        word_count = 0

        # Bullish keywords
        for strength, keywords in self.keyword_weights["bullish_keywords"].items():
            weight = {"strong": 0.8, "medium": 0.5, "weak": 0.2}[strength]
            for keyword in keywords:
                count = text.count(keyword)
                sentiment_score += count * weight
                word_count += count

        # Bearish keywords
        for strength, keywords in self.keyword_weights["bearish_keywords"].items():
            weight = {"strong": -0.8, "medium": -0.5, "weak": -0.2}[strength]
            for keyword in keywords:
                count = text.count(keyword)
                sentiment_score += count * weight
                word_count += count

        # Normalize by word count
        if word_count > 0:
            sentiment_score = sentiment_score / word_count

        return max(-1.0, min(1.0, sentiment_score))

    def determine_market_impact(self, title: str, summary: str, sentiment_score: float) -> str:
        """Determine expected market impact"""
        text = (title + " " + summary).lower()

        # High impact keywords
        high_impact_keywords = [
            "federal reserve", "interest rate", "inflation", "gdp", "employment",
            "crisis", "crash", "recession", "boom", "breakout"
        ]

        impact_score = 0
        for keyword in high_impact_keywords:
            if keyword in text:
                impact_score += 1

        # Adjust by sentiment strength
        sentiment_strength = abs(sentiment_score)

        if impact_score >= 2 and sentiment_strength > 0.6:
            return "HIGH"
        elif impact_score >= 1 or sentiment_strength > 0.4:
            return "MEDIUM"
        else:
            return "LOW"

    def extract_keywords(self, title: str, summary: str) -> List[str]:
        """Extract relevant keywords from news"""
        text = (title + " " + summary).lower()
        keywords = []

        # Extract market-moving topics
        for topic in self.keyword_weights["market_moving_topics"].keys():
            if topic in text:
                keywords.append(topic)

        # Extract sentiment keywords
        for strength_dict in self.keyword_weights["bullish_keywords"].values():
            for keyword in strength_dict:
                if keyword in text:
                    keywords.append(keyword)

        for strength_dict in self.keyword_weights["bearish_keywords"].values():
            for keyword in strength_dict:
                if keyword in text:
                    keywords.append(keyword)

        return list(set(keywords))  # Remove duplicates

    def calculate_confidence(self, source: str, relevance: float, sentiment: float) -> float:
        """Calculate confidence in news analysis"""
        source_weight = self.keyword_weights["source_credibility"].get(source.lower(), 0.5)
        confidence = source_weight * 0.4 + relevance * 0.4 + abs(sentiment) * 0.2
        return min(confidence, 1.0)

    def calculate_aggregate_sentiment(self, news_items: List[NewsItem]) -> Dict:
        """Calculate aggregate sentiment from all news items"""
        if not news_items:
            return {"overall_sentiment": 0.0, "confidence": 0.0, "bias": "NEUTRAL"}

        # Weight sentiment by relevance and confidence
        weighted_sentiments = []
        total_weight = 0

        for item in news_items:
            weight = item.relevance_score * item.confidence
            weighted_sentiments.append(item.sentiment_score * weight)
            total_weight += weight

        if total_weight == 0:
            overall_sentiment = 0.0
        else:
            overall_sentiment = sum(weighted_sentiments) / total_weight

        # Calculate confidence
        avg_confidence = statistics.mean([item.confidence for item in news_items])

        # Determine bias
        if overall_sentiment > 0.2:
            bias = "BULLISH"
        elif overall_sentiment < -0.2:
            bias = "BEARISH"
        else:
            bias = "NEUTRAL"

        return {
            "overall_sentiment": round(overall_sentiment, 3),
            "confidence": round(avg_confidence, 3),
            "bias": bias,
            "sentiment_strength": abs(overall_sentiment),
            "total_weighted_items": len(news_items)
        }

    def generate_sentiment_signals(self, news_items: List[NewsItem], aggregate: Dict) -> List[SentimentSignal]:
        """Generate trading signals based on sentiment"""
        signals = []

        overall_sentiment = aggregate["overall_sentiment"]
        confidence = aggregate["confidence"]
        sentiment_strength = aggregate["sentiment_strength"]

        try:
            # Strong sentiment signal
            if sentiment_strength > 0.6 and confidence > 0.7:
                direction = "BULLISH" if overall_sentiment > 0 else "BEARISH"
                signals.append(SentimentSignal(
                    signal_type="STRONG_SENTIMENT",
                    strength=sentiment_strength,
                    direction=direction,
                    reasoning=f"Strong {direction.lower()} sentiment ({overall_sentiment:.2f}) with high confidence",
                    time_horizon="SHORT_TERM",
                    confidence=confidence
                ))

            # News flow momentum signal
            momentum_signal = self.analyze_sentiment_momentum(news_items)
            if momentum_signal:
                signals.append(momentum_signal)

            # Contrarian signal (extreme sentiment)
            if sentiment_strength > 0.8:
                contrarian_direction = "BEARISH" if overall_sentiment > 0 else "BULLISH"
                signals.append(SentimentSignal(
                    signal_type="CONTRARIAN_SENTIMENT",
                    strength=sentiment_strength * 0.7,  # Reduce strength for contrarian
                    direction=contrarian_direction,
                    reasoning=f"Extreme sentiment ({overall_sentiment:.2f}) may indicate reversal",
                    time_horizon="MEDIUM_TERM",
                    confidence=confidence * 0.8
                ))

            # Event-driven signal
            event_signal = self.detect_event_driven_signals(news_items)
            if event_signal:
                signals.append(event_signal)

        except Exception as e:
            print(f"Error generating sentiment signals: {e}")

        return signals

    def analyze_sentiment_momentum(self, news_items: List[NewsItem]) -> Optional[SentimentSignal]:
        """Analyze sentiment momentum over time"""
        if len(news_items) < 3:
            return None

        try:
            # Sort by timestamp
            sorted_items = sorted(news_items, key=lambda x: x.timestamp)

            # Calculate recent vs older sentiment
            recent_items = sorted_items[-int(len(sorted_items)/2):]
            older_items = sorted_items[:int(len(sorted_items)/2)]

            recent_sentiment = statistics.mean([item.sentiment_score for item in recent_items])
            older_sentiment = statistics.mean([item.sentiment_score for item in older_items])

            momentum = recent_sentiment - older_sentiment

            if abs(momentum) > 0.3:
                direction = "BULLISH" if momentum > 0 else "BEARISH"
                return SentimentSignal(
                    signal_type="SENTIMENT_MOMENTUM",
                    strength=abs(momentum),
                    direction=direction,
                    reasoning=f"Sentiment momentum shift: {momentum:.2f}",
                    time_horizon="SHORT_TERM",
                    confidence=0.7
                )

        except Exception as e:
            print(f"Error analyzing sentiment momentum: {e}")

        return None

    def detect_event_driven_signals(self, news_items: List[NewsItem]) -> Optional[SentimentSignal]:
        """Detect event-driven trading signals"""
        try:
            # Look for high-impact events
            high_impact_items = [item for item in news_items if item.market_impact == "HIGH"]

            if not high_impact_items:
                return None

            # Calculate average sentiment of high-impact items
            avg_sentiment = statistics.mean([item.sentiment_score for item in high_impact_items])
            avg_confidence = statistics.mean([item.confidence for item in high_impact_items])

            if abs(avg_sentiment) > 0.4:
                direction = "BULLISH" if avg_sentiment > 0 else "BEARISH"
                return SentimentSignal(
                    signal_type="EVENT_DRIVEN",
                    strength=abs(avg_sentiment),
                    direction=direction,
                    reasoning=f"High-impact events with {direction.lower()} sentiment",
                    time_horizon="IMMEDIATE",
                    confidence=avg_confidence
                )

        except Exception as e:
            print(f"Error detecting event-driven signals: {e}")

        return None

    def analyze_news_flow_patterns(self, news_items: List[NewsItem]) -> Dict:
        """Analyze news flow patterns and timing"""
        if not news_items:
            return {"flow_intensity": "LOW", "timing_pattern": "NORMAL"}

        try:
            # Analyze flow intensity
            total_items = len(news_items)
            high_relevance_items = len([item for item in news_items if item.relevance_score > 0.7])

            if high_relevance_items > 10:
                flow_intensity = "VERY_HIGH"
            elif high_relevance_items > 5:
                flow_intensity = "HIGH"
            elif high_relevance_items > 2:
                flow_intensity = "MEDIUM"
            else:
                flow_intensity = "LOW"

            # Analyze timing patterns
            current_hour = datetime.now().hour
            if 9 <= current_hour <= 11:
                timing_pattern = "MARKET_OPEN"
            elif 15 <= current_hour <= 16:
                timing_pattern = "MARKET_CLOSE"
            elif 6 <= current_hour <= 9:
                timing_pattern = "PRE_MARKET"
            elif 16 <= current_hour <= 20:
                timing_pattern = "AFTER_HOURS"
            else:
                timing_pattern = "OFF_HOURS"

            # Calculate news velocity
            news_velocity = total_items / max(1, (datetime.now().hour + 1))  # News per hour

            return {
                "flow_intensity": flow_intensity,
                "timing_pattern": timing_pattern,
                "total_items": total_items,
                "high_relevance_items": high_relevance_items,
                "news_velocity": round(news_velocity, 2),
                "market_impact_distribution": {
                    "HIGH": len([item for item in news_items if item.market_impact == "HIGH"]),
                    "MEDIUM": len([item for item in news_items if item.market_impact == "MEDIUM"]),
                    "LOW": len([item for item in news_items if item.market_impact == "LOW"])
                }
            }

        except Exception as e:
            print(f"Error analyzing news flow patterns: {e}")
            return {"flow_intensity": "LOW", "timing_pattern": "NORMAL"}

    def assess_market_impact(self, news_items: List[NewsItem], aggregate: Dict) -> Dict:
        """Assess overall market impact"""
        high_impact_count = len([item for item in news_items if item.market_impact == "HIGH"])
        medium_impact_count = len([item for item in news_items if item.market_impact == "MEDIUM"])

        overall_sentiment = aggregate["overall_sentiment"]
        confidence = aggregate["confidence"]

        # Calculate expected volatility impact
        volatility_impact = "LOW"
        if high_impact_count >= 2:
            volatility_impact = "HIGH"
        elif high_impact_count >= 1 or medium_impact_count >= 3:
            volatility_impact = "MEDIUM"

        # Calculate directional impact
        direction_impact = "NEUTRAL"
        if abs(overall_sentiment) > 0.5 and confidence > 0.7:
            direction_impact = "BULLISH" if overall_sentiment > 0 else "BEARISH"

        # Time horizon assessment
        time_horizon = "SHORT_TERM"
        if any(item.market_impact == "HIGH" for item in news_items):
            time_horizon = "IMMEDIATE"

        return {
            "volatility_impact": volatility_impact,
            "directional_impact": direction_impact,
            "time_horizon": time_horizon,
            "confidence": confidence,
            "high_impact_events": high_impact_count,
            "expected_move": self.estimate_expected_move(overall_sentiment, volatility_impact)
        }

    def estimate_expected_move(self, sentiment: float, volatility_impact: str) -> str:
        """Estimate expected market move"""
        volatility_multipliers = {
            "LOW": 0.5,
            "MEDIUM": 1.0,
            "HIGH": 1.5
        }

        base_move = abs(sentiment) * 2.0  # 2% max sentiment-based move
        volatility_multiplier = volatility_multipliers.get(volatility_impact, 1.0)
        expected_move = base_move * volatility_multiplier

        if expected_move > 1.5:
            return "LARGE (>1.5%)"
        elif expected_move > 0.8:
            return "MEDIUM (0.8-1.5%)"
        elif expected_move > 0.3:
            return "SMALL (0.3-0.8%)"
        else:
            return "MINIMAL (<0.3%)"

    def generate_news_trading_recommendations(self, signals: List[SentimentSignal],
                                            market_impact: Dict, flow_analysis: Dict) -> List[Dict]:
        """Generate specific trading recommendations based on news analysis"""
        recommendations = []

        try:
            # Signal-based recommendations
            for signal in signals:
                if signal.strength > 0.6 and signal.confidence > 0.7:
                    strategy = self.get_strategy_for_signal(signal, market_impact)
                    if strategy:
                        recommendations.append(strategy)

            # Flow-based recommendations
            if flow_analysis.get("flow_intensity") == "VERY_HIGH":
                recommendations.append({
                    "strategy": "VOLATILITY_PLAY",
                    "reasoning": "Very high news flow intensity indicates volatility opportunity",
                    "specific_trades": ["Long straddles", "Short iron condors", "VIX calls"],
                    "confidence": 0.75,
                    "time_horizon": "SHORT_TERM"
                })

            # Impact-based recommendations
            if market_impact.get("volatility_impact") == "HIGH":
                recommendations.append({
                    "strategy": "DEFENSIVE_POSITIONING",
                    "reasoning": "High volatility impact expected from news events",
                    "specific_trades": ["Reduce position sizes", "Add protective puts", "Consider cash"],
                    "confidence": 0.80,
                    "time_horizon": "IMMEDIATE"
                })

        except Exception as e:
            print(f"Error generating trading recommendations: {e}")

        return recommendations

    def get_strategy_for_signal(self, signal: SentimentSignal, market_impact: Dict) -> Optional[Dict]:
        """Get specific strategy for a sentiment signal"""
        if signal.signal_type == "STRONG_SENTIMENT":
            if signal.direction == "BULLISH":
                return {
                    "strategy": "BULLISH_MOMENTUM",
                    "reasoning": signal.reasoning,
                    "specific_trades": ["Long calls", "Bull call spreads", "Covered calls"],
                    "confidence": signal.confidence,
                    "time_horizon": signal.time_horizon
                }
            else:
                return {
                    "strategy": "BEARISH_MOMENTUM",
                    "reasoning": signal.reasoning,
                    "specific_trades": ["Long puts", "Bear put spreads", "Protective puts"],
                    "confidence": signal.confidence,
                    "time_horizon": signal.time_horizon
                }

        elif signal.signal_type == "CONTRARIAN_SENTIMENT":
            return {
                "strategy": "CONTRARIAN_PLAY",
                "reasoning": signal.reasoning,
                "specific_trades": ["Counter-trend options", "Mean reversion plays", "Fade the move"],
                "confidence": signal.confidence,
                "time_horizon": signal.time_horizon
            }

        elif signal.signal_type == "EVENT_DRIVEN":
            return {
                "strategy": "EVENT_RESPONSE",
                "reasoning": signal.reasoning,
                "specific_trades": ["Quick directional plays", "Short-term options", "Scalp trades"],
                "confidence": signal.confidence,
                "time_horizon": "IMMEDIATE"
            }

        return None

    def calculate_sentiment_distribution(self, news_items: List[NewsItem]) -> Dict:
        """Calculate distribution of sentiment across news items"""
        if not news_items:
            return {"bullish": 0, "neutral": 0, "bearish": 0}

        bullish = len([item for item in news_items if item.sentiment_score > 0.2])
        bearish = len([item for item in news_items if item.sentiment_score < -0.2])
        neutral = len(news_items) - bullish - bearish

        return {
            "bullish": bullish,
            "neutral": neutral,
            "bearish": bearish,
            "bullish_pct": round(bullish / len(news_items) * 100, 1),
            "bearish_pct": round(bearish / len(news_items) * 100, 1),
            "neutral_pct": round(neutral / len(news_items) * 100, 1)
        }

    def get_default_sentiment_analysis(self) -> Dict:
        """Return default analysis when no news data available"""
        return {
            "timestamp": datetime.now().isoformat(),
            "total_news_items": 0,
            "aggregate_sentiment": {
                "overall_sentiment": 0.0,
                "confidence": 0.0,
                "bias": "NEUTRAL"
            },
            "sentiment_signals": [],
            "news_flow_analysis": {
                "flow_intensity": "LOW",
                "timing_pattern": "NORMAL"
            },
            "market_impact_assessment": {
                "volatility_impact": "LOW",
                "directional_impact": "NEUTRAL"
            },
            "trading_recommendations": [],
            "note": "No news data available for analysis"
        }

    def save_sentiment_analysis(self, analysis: Dict):
        """Save sentiment analysis to file"""
        try:
            os.makedirs(".spx", exist_ok=True)
            with open(self.sentiment_analysis_file, 'w') as f:
                json.dump(analysis, f, indent=2)

            # Update news history (keep last 50 items)
            if analysis.get("top_news_items"):
                self.news_history.extend(analysis["top_news_items"])
                self.news_history = self.news_history[-50:]

                with open(self.news_history_file, 'w') as f:
                    json.dump(self.news_history, f, indent=2)

        except Exception as e:
            print(f"Error saving sentiment analysis: {e}")

def main():
    """Test News Sentiment Engine"""
    sentiment_engine = NewsSentimentEngine()

    print(" News Sentiment Analysis Engine Test")
    print("=" * 50)

    # Sample news data
    sample_news = [
        {
            "title": "Federal Reserve Signals Potential Rate Cut Amid Economic Concerns",
            "summary": "The Federal Reserve indicated it may consider lowering interest rates if economic conditions continue to weaken, citing concerns about inflation and employment.",
            "source": "reuters",
            "time_published": datetime.now().isoformat()
        },
        {
            "title": "S&P 500 Hits New Record High on Strong Earnings Reports",
            "summary": "The S&P 500 index reached a new all-time high today as several major companies reported better-than-expected quarterly earnings, boosting investor confidence.",
            "source": "bloomberg",
            "time_published": (datetime.now() - timedelta(hours=1)).isoformat()
        },
        {
            "title": "Technology Stocks Surge on AI Breakthrough Announcement",
            "summary": "Technology stocks rallied after a major breakthrough in artificial intelligence was announced, with investors optimistic about future growth prospects.",
            "source": "cnbc",
            "time_published": (datetime.now() - timedelta(hours=2)).isoformat()
        }
    ]

    print(f"Testing with {len(sample_news)} news items")

    # Run sentiment analysis
    analysis = sentiment_engine.analyze_news_sentiment(sample_news)

    print(f"\nCHART Sentiment Analysis Results:")
    aggregate = analysis["aggregate_sentiment"]
    print(f"- Overall Sentiment: {aggregate['overall_sentiment']:.3f}")
    print(f"- Bias: {aggregate['bias']}")
    print(f"- Confidence: {aggregate['confidence']:.1%}")

    # Display signals
    signals = analysis.get('sentiment_signals', [])
    print(f"\nALERT Sentiment Signals ({len(signals)}):")
    for signal in signals:
        print(f"- {signal['signal_type']}: {signal['direction']} (Strength: {signal['strength']:.1%})")
        print(f"  Reasoning: {signal['reasoning']}")

    # Display market impact
    impact = analysis.get('market_impact_assessment', {})
    print(f"\n Market Impact Assessment:")
    print(f"- Volatility Impact: {impact.get('volatility_impact', 'N/A')}")
    print(f"- Directional Impact: {impact.get('directional_impact', 'N/A')}")
    print(f"- Expected Move: {impact.get('expected_move', 'N/A')}")

    # Display recommendations
    recommendations = analysis.get('trading_recommendations', [])
    print(f"\nIDEA Trading Recommendations ({len(recommendations)}):")
    for rec in recommendations:
        print(f"- {rec['strategy']} (Confidence: {rec['confidence']:.1%})")
        print(f"  {rec['reasoning']}")

    # News flow analysis
    flow = analysis.get('news_flow_analysis', {})
    print(f"\nCHART News Flow Analysis:")
    print(f"- Flow Intensity: {flow.get('flow_intensity', 'N/A')}")
    print(f"- High Relevance Items: {flow.get('high_relevance_items', 0)}")

    print("\nSUCCESS News Sentiment Engine test completed!")

if __name__ == "__main__":
    main()