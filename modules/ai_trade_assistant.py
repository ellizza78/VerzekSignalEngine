import os
import json
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from openai import OpenAI

class AITradeAssistant:
    def __init__(self):
        base_url = os.getenv("AI_INTEGRATIONS_OPENAI_BASE_URL")
        api_key = os.getenv("AI_INTEGRATIONS_OPENAI_API_KEY")
        
        if not base_url or not api_key:
            print("[AI_ASSISTANT] Warning: OpenAI AI Integrations not configured. AI features will be disabled.")
            self.client = None
            self.model = None
        else:
            self.client = OpenAI(
                base_url=base_url,
                api_key=api_key
            )
            self.model = "gpt-4o-mini"
    
    def analyze_signal(self, signal_data: Dict) -> Dict:
        if not self.client:
            return {
                "success": False,
                "error": "AI features are not available. OpenAI integration not configured.",
                "analysis": None
            }
        
        try:
            symbol = signal_data.get('symbol', 'Unknown')
            direction = signal_data.get('direction', 'Unknown')
            entry = signal_data.get('entry', 'Unknown')
            stop_loss = signal_data.get('stop_loss', 'Unknown')
            targets = signal_data.get('targets', [])
            leverage = signal_data.get('leverage', 1)
            
            prompt = f"""
You are an expert cryptocurrency trading analyst. Analyze this trading signal and provide insights:

Signal Details:
- Symbol: {symbol}
- Direction: {direction}
- Entry Price: {entry}
- Stop Loss: {stop_loss}
- Targets: {', '.join(map(str, targets))}
- Leverage: {leverage}x

Provide a comprehensive analysis including:
1. Risk/Reward Ratio Assessment
2. Market Context & Trends
3. Key Support/Resistance Levels
4. Recommended Position Size
5. Risk Management Advice
6. Overall Confidence Score (0-100)

Format your response as JSON with keys: risk_reward, market_context, support_resistance, position_size, risk_advice, confidence_score, summary
"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert cryptocurrency trading analyst providing actionable insights."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            analysis_text = response.choices[0].message.content or "{}"
            
            try:
                analysis = json.loads(analysis_text)
            except json.JSONDecodeError:
                analysis = {
                    "summary": analysis_text,
                    "confidence_score": 70,
                    "risk_reward": "Analysis in summary",
                    "market_context": "See summary",
                    "support_resistance": "See summary",
                    "position_size": "Conservative sizing recommended",
                    "risk_advice": "Always use stop loss"
                }
            
            analysis['timestamp'] = datetime.now().isoformat()
            analysis['signal_symbol'] = symbol
            
            return {
                "success": True,
                "analysis": analysis
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "analysis": None
            }
    
    def generate_trade_recommendation(self, market_data: Dict, user_profile: Dict) -> Dict:
        if not self.client:
            return {"success": False, "error": "AI features not available", "recommendation": None}
        
        try:
            symbol = market_data.get('symbol', 'BTC/USDT')
            current_price = market_data.get('price', 0)
            volume_24h = market_data.get('volume_24h', 0)
            price_change_24h = market_data.get('price_change_24h', 0)
            
            risk_level = user_profile.get('risk_level', 'medium')
            capital = user_profile.get('capital', 1000)
            
            prompt = f"""
You are an AI trading advisor. Generate a trade recommendation based on:

Market Data:
- Symbol: {symbol}
- Current Price: ${current_price}
- 24h Volume: ${volume_24h}
- 24h Change: {price_change_24h}%

User Profile:
- Risk Tolerance: {risk_level}
- Available Capital: ${capital}

Provide a trade recommendation including:
1. Action (BUY/SELL/HOLD)
2. Entry Price Range
3. Stop Loss Level
4. Take Profit Targets (3 levels)
5. Position Size in USD
6. Reasoning
7. Confidence Level (0-100)

Format as JSON with keys: action, entry_range, stop_loss, targets, position_size, reasoning, confidence
"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional trading advisor providing data-driven recommendations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=800
            )
            
            recommendation_text = response.choices[0].message.content or "{}"
            
            try:
                recommendation = json.loads(recommendation_text)
            except json.JSONDecodeError:
                recommendation = {
                    "action": "HOLD",
                    "reasoning": recommendation_text,
                    "confidence": 50
                }
            
            recommendation['timestamp'] = datetime.now().isoformat()
            recommendation['symbol'] = symbol
            
            return {
                "success": True,
                "recommendation": recommendation
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "recommendation": None
            }
    
    def analyze_portfolio(self, positions: List[Dict], market_conditions: Dict) -> Dict:
        if not self.client:
            return {"success": False, "error": "AI features not available", "analysis": None}
        
        try:
            total_value = sum(p.get('current_value', 0) for p in positions)
            total_pnl = sum(p.get('pnl', 0) for p in positions)
            
            positions_summary = []
            for pos in positions[:5]:
                positions_summary.append({
                    'symbol': pos.get('symbol', 'Unknown'),
                    'direction': pos.get('direction', 'Unknown'),
                    'pnl': pos.get('pnl', 0),
                    'size': pos.get('size', 0)
                })
            
            prompt = f"""
You are a portfolio management AI. Analyze this trading portfolio:

Portfolio Overview:
- Total Value: ${total_value:.2f}
- Total PnL: ${total_pnl:.2f}
- Number of Positions: {len(positions)}
- Active Positions: {json.dumps(positions_summary, indent=2)}

Market Conditions:
- Trend: {market_conditions.get('trend', 'Neutral')}
- Volatility: {market_conditions.get('volatility', 'Medium')}

Provide portfolio analysis including:
1. Overall Health Score (0-100)
2. Diversification Assessment
3. Risk Exposure Analysis
4. Rebalancing Recommendations
5. Positions to Close
6. Positions to Increase
7. Action Items

Format as JSON with keys: health_score, diversification, risk_exposure, rebalancing, close_positions, increase_positions, action_items
"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert portfolio manager specializing in cryptocurrency trading."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=1200
            )
            
            analysis_text = response.choices[0].message.content or "{}"
            
            try:
                analysis = json.loads(analysis_text)
            except json.JSONDecodeError:
                analysis = {
                    "health_score": 70,
                    "diversification": "Analysis in progress",
                    "action_items": [analysis_text]
                }
            
            analysis['timestamp'] = datetime.now().isoformat()
            analysis['portfolio_value'] = total_value
            analysis['portfolio_pnl'] = total_pnl
            
            return {
                "success": True,
                "analysis": analysis
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "analysis": None
            }
    
    def predict_market_movement(self, symbol: str, timeframe: str, historical_data: List[Dict]) -> Dict:
        if not self.client:
            return {"success": False, "error": "AI features not available", "prediction": None}
        
        try:
            recent_prices = [d.get('close', 0) for d in historical_data[-10:]]
            price_trend = "bullish" if recent_prices[-1] > recent_prices[0] else "bearish"
            
            prompt = f"""
You are a market prediction AI. Analyze and predict price movement:

Symbol: {symbol}
Timeframe: {timeframe}
Recent Prices: {recent_prices}
Current Trend: {price_trend}

Provide prediction including:
1. Direction (UP/DOWN/SIDEWAYS)
2. Probability (0-100%)
3. Price Target Range
4. Time Horizon
5. Key Indicators
6. Confidence Level
7. Risk Factors

Format as JSON with keys: direction, probability, price_target_low, price_target_high, time_horizon, key_indicators, confidence, risk_factors
"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a quantitative analyst specializing in price prediction."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=800
            )
            
            prediction_text = response.choices[0].message.content or "{}"
            
            try:
                prediction = json.loads(prediction_text)
            except json.JSONDecodeError:
                prediction = {
                    "direction": "SIDEWAYS",
                    "probability": 50,
                    "confidence": 50,
                    "reasoning": prediction_text
                }
            
            prediction['timestamp'] = datetime.now().isoformat()
            prediction['symbol'] = symbol
            prediction['timeframe'] = timeframe
            
            return {
                "success": True,
                "prediction": prediction
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "prediction": None
            }
    
    def sentiment_analysis(self, news_data: List[str], social_media_data: List[str]) -> Dict:
        if not self.client:
            return {"success": False, "error": "AI features not available", "analysis": None}
        
        try:
            combined_text = "\n".join(news_data[:5] + social_media_data[:5])
            
            prompt = f"""
Analyze market sentiment from news and social media:

Content:
{combined_text}

Provide sentiment analysis including:
1. Overall Sentiment (Bullish/Bearish/Neutral)
2. Sentiment Score (-100 to +100)
3. Key Themes
4. Market Impact Prediction
5. Trading Implications
6. Confidence Level

Format as JSON with keys: sentiment, score, themes, market_impact, trading_implications, confidence
"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a sentiment analysis expert for financial markets."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=600
            )
            
            analysis_text = response.choices[0].message.content or "{}"
            
            try:
                analysis = json.loads(analysis_text)
            except json.JSONDecodeError:
                analysis = {
                    "sentiment": "Neutral",
                    "score": 0,
                    "confidence": 50,
                    "summary": analysis_text
                }
            
            analysis['timestamp'] = datetime.now().isoformat()
            
            return {
                "success": True,
                "analysis": analysis
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "analysis": None
            }
    
    def chat_assistant(self, user_message: str, conversation_history: Optional[List[Dict]] = None) -> Dict:
        if not self.client:
            return {"success": False, "error": "AI features not available", "response": "I apologize, but AI features are currently unavailable."}
        
        try:
            messages: List[Dict[str, Any]] = [
                {"role": "system", "content": "You are VerzekBot, an expert cryptocurrency trading assistant. Help users with trading strategies, market analysis, risk management, and technical questions. Be concise, accurate, and actionable."}
            ]
            
            if conversation_history:
                messages.extend(conversation_history[-5:])
            
            messages.append({"role": "user", "content": user_message})
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            
            assistant_message = response.choices[0].message.content or "I apologize, but I couldn't generate a response."
            
            return {
                "success": True,
                "response": assistant_message,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response": "I apologize, but I'm having trouble processing your request. Please try again."
            }


if __name__ == "__main__":
    assistant = AITradeAssistant()
    
    test_signal = {
        "symbol": "BTC/USDT",
        "direction": "LONG",
        "entry": 45000,
        "stop_loss": 44000,
        "targets": [46000, 47000, 48000],
        "leverage": 10
    }
    
    print("Testing AI Trade Assistant...")
    result = assistant.analyze_signal(test_signal)
    print(json.dumps(result, indent=2))
