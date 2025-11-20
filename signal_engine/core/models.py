"""
Central Signal Models
Standardized signal format for all bots
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List
import uuid


@dataclass
class SignalCandidate:
    """
    Standardized signal format from all trading bots
    All bots must return this format instead of sending signals directly
    """
    signal_id: str
    symbol: str
    side: str  # "LONG" or "SHORT"
    entry: float
    stop_loss: float
    take_profits: List[float]
    timeframe: str
    confidence: float  # 0-100
    bot_source: str  # "SCALPING", "TREND", "QFL", "AI_ML"
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """Validate signal data"""
        if self.side not in ["LONG", "SHORT"]:
            raise ValueError(f"Invalid side: {self.side}. Must be LONG or SHORT")
        
        if not 0 <= self.confidence <= 100:
            raise ValueError(f"Invalid confidence: {self.confidence}. Must be 0-100")
        
        if self.bot_source not in ["SCALPING", "TREND", "QFL", "AI_ML"]:
            raise ValueError(f"Invalid bot_source: {self.bot_source}")
    
    def to_dict(self) -> dict:
        """Convert to dictionary for API transmission"""
        return {
            'signal_id': self.signal_id,
            'symbol': self.symbol,
            'side': self.side,
            'entry': self.entry,
            'stop_loss': self.stop_loss,
            'take_profits': self.take_profits,
            'timeframe': self.timeframe,
            'confidence': self.confidence,
            'bot_source': self.bot_source,
            'created_at': self.created_at.isoformat(),
            'version': 'SE.v2.0'
        }
    
    def to_telegram_message(self) -> str:
        """Format signal for Telegram broadcast"""
        tp_text = ", ".join([f"${tp:.2f}" for tp in self.take_profits])
        
        message = f"""
🤖 **{self.bot_source} BOT SIGNAL**
━━━━━━━━━━━━━━━━━━━━━

📊 Symbol: {self.symbol}
{('🟢 LONG' if self.side == 'LONG' else '🔴 SHORT')}

💰 Entry: ${self.entry:.2f}
🎯 Take Profit: {tp_text}
🛑 Stop Loss: ${self.stop_loss:.2f}

⏱️ Timeframe: {self.timeframe}
⚡ Confidence: {self.confidence:.0f}%

🆔 Signal ID: {self.signal_id[:8]}
⏰ {self.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}
"""
        return message.strip()


@dataclass
class SignalOutcome:
    """
    Signal outcome after closure (TP, SL, or cancellation)
    Used for tracking performance and reporting
    Supports multi-TP tracking (5 levels)
    """
    signal_id: str
    symbol: str
    side: str
    entry: float
    exit_price: float
    close_reason: str  # "TP", "SL", "CANCEL", "REVERSAL", "TIMEOUT"
    profit_pct: float  # Calculated profit percentage
    opened_at: datetime
    closed_at: datetime
    bot_source: str = ""
    current_tp_index: int = 0  # Last TP hit (0-4 for TP1-TP5)
    total_tps: int = 5  # Always 5 TP levels
    partial_profits: List[float] = field(default_factory=list)  # Profit % per TP hit
    
    @property
    def duration_minutes(self) -> float:
        """Calculate signal duration in minutes"""
        delta = self.closed_at - self.opened_at
        return delta.total_seconds() / 60
    
    @property
    def is_profitable(self) -> bool:
        """Check if trade was profitable"""
        return self.profit_pct > 0
    
    @property
    def is_final(self) -> bool:
        """Check if this is the final TP (TP5) or a complete closure"""
        return self.close_reason != "TP" or self.current_tp_index >= self.total_tps - 1
    
    @property
    def duration_formatted(self) -> str:
        """Format duration as 'X Days Y Hours Z Minutes'"""
        delta = self.closed_at - self.opened_at
        total_seconds = int(delta.total_seconds())
        
        days = total_seconds // 86400
        hours = (total_seconds % 86400) // 3600
        minutes = (total_seconds % 3600) // 60
        
        parts = []
        if days > 0:
            parts.append(f"{days} Day{'s' if days != 1 else ''}")
        if hours > 0:
            parts.append(f"{hours} Hour{'s' if hours != 1 else ''}")
        if minutes > 0 or not parts:
            parts.append(f"{minutes} Minute{'s' if minutes != 1 else ''}")
        
        return " ".join(parts)
    
    def to_telegram_message(self) -> str:
        """Format outcome for Telegram notification"""
        emoji = "✅" if self.is_profitable else "❌"
        profit_text = f"+{self.profit_pct:.2f}%" if self.profit_pct > 0 else f"{self.profit_pct:.2f}%"
        
        reason_emojis = {
            "TP": "🎯 TAKE PROFIT",
            "SL": "🛑 STOP LOSS",
            "CANCEL": "❌ CANCELLED",
            "REVERSAL": "🔄 REVERSED"
        }
        reason_text = reason_emojis.get(self.close_reason, self.close_reason)
        
        message = f"""
{emoji} **SIGNAL CLOSED: {reason_text}**
━━━━━━━━━━━━━━━━━━━━━

📊 {self.symbol} {self.side}
💵 Entry: ${self.entry:.2f}
💵 Exit: ${self.exit_price:.2f}

💰 Profit: {profit_text}
⏱️ Duration: {self.duration_minutes:.1f} minutes

🆔 {self.signal_id[:8]}
⏰ Closed: {self.closed_at.strftime('%H:%M:%S UTC')}
"""
        return message.strip()
    
    def to_dict(self) -> dict:
        """Convert to dictionary for storage/API"""
        return {
            'signal_id': self.signal_id,
            'symbol': self.symbol,
            'side': self.side,
            'entry': self.entry,
            'exit_price': self.exit_price,
            'close_reason': self.close_reason,
            'profit_pct': self.profit_pct,
            'opened_at': self.opened_at.isoformat(),
            'closed_at': self.closed_at.isoformat(),
            'duration_minutes': self.duration_minutes,
            'bot_source': self.bot_source,
            'current_tp_index': self.current_tp_index,
            'total_tps': self.total_tps,
            'partial_profits': self.partial_profits,
            'is_final': self.is_final
        }


def generate_signal_id() -> str:
    """Generate unique signal ID"""
    return str(uuid.uuid4())
