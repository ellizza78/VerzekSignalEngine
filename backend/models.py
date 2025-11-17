"""
Database models for Verzek AutoTrader
All models are designed to work with both SQLite and PostgreSQL
"""
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from db import Base


class User(Base):
    """User account model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255))
    is_verified = Column(Boolean, default=False)
    auto_trade_enabled = Column(Boolean, default=False)
    subscription_type = Column(String(20), default="TRIAL")  # TRIAL, VIP, PREMIUM
    referral_code = Column(String(20), unique=True, index=True)  # VZK + 6 chars
    referred_by = Column(Integer, ForeignKey("users.id"), nullable=True)  # Referrer user ID
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    notifications_enabled = Column(Boolean, default=True)
    
    # Relationships
    settings = relationship("UserSettings", uselist=False, back_populates="user", cascade="all, delete-orphan")
    exchanges = relationship("ExchangeAccount", back_populates="user", cascade="all, delete-orphan")
    positions = relationship("Position", back_populates="user", cascade="all, delete-orphan")
    device_tokens = relationship("DeviceToken", back_populates="user", cascade="all, delete-orphan")


class UserSettings(Base):
    """User trading settings and preferences"""
    __tablename__ = "user_settings"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    # Capital & Risk
    capital_usdt = Column(Float, default=0)
    per_trade_usdt = Column(Float, default=5.0)
    leverage = Column(Integer, default=1)  # 1-25x
    max_concurrent_trades = Column(Integer, default=5)  # Max 50 per user
    
    # Strategy
    strategy = Column(JSON, default=dict)  # RSI, MA, custom indicators
    
    # DCA Settings
    dca_enabled = Column(Boolean, default=False)
    dca_steps = Column(Integer, default=3)
    dca_step_percent = Column(Float, default=2.0)
    
    # Preferences
    preferences = Column(JSON, default=dict)  # UI settings, notifications, etc.
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="settings")


class ExchangeAccount(Base):
    """User exchange API credentials (encrypted)"""
    __tablename__ = "exchange_accounts"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    exchange = Column(String(50), nullable=False)  # binance, bybit, phemex, kraken
    api_key = Column(String(255))  # Encrypted
    api_secret = Column(String(255))  # Encrypted
    testnet = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="exchanges")


class Signal(Base):
    """Trading signals from Telegram or manual creation"""
    __tablename__ = "signals"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(50), index=True, nullable=False)
    side = Column(String(10), nullable=False)  # BUY/SELL or LONG/SHORT
    entry = Column(Float, nullable=False)
    tp = Column(JSON, nullable=False)  # [price1, price2, price3]
    sl = Column(Float, nullable=False)
    leverage = Column(Integer, default=1)
    confidence = Column(Integer, default=0)  # 0-100
    trade_type = Column(String(20), default="FUTURES")  # SPOT/FUTURES
    duration = Column(String(20), default="SHORT")  # SHORT/LONG (time horizon)
    status = Column(String(20), default="NEW", index=True)  # NEW|OPENED|PARTIAL|CLOSED|CANCELLED|STOPPED
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    meta = Column(JSON, default=dict)  # Source, provider, raw text
    
    # Relationships
    positions = relationship("Position", back_populates="signal")


class Position(Base):
    """User positions tracking"""
    __tablename__ = "positions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    signal_id = Column(Integer, ForeignKey("signals.id"), index=True)
    
    symbol = Column(String(50), nullable=False)
    side = Column(String(10), nullable=False)  # LONG/SHORT
    leverage = Column(Integer, default=1)
    qty = Column(Float, default=0)
    entry_price = Column(Float, default=0)
    remaining_qty = Column(Float, default=0)
    
    status = Column(String(20), default="OPEN", index=True)  # OPEN|PARTIAL|CLOSED|STOPPED|CANCELLED
    pnl_usdt = Column(Float, default=0)
    pnl_pct = Column(Float, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    closed_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="positions")
    signal = relationship("Signal", back_populates="positions")
    targets = relationship("PositionTarget", back_populates="position", cascade="all, delete-orphan")


class PositionTarget(Base):
    """Take-profit targets for positions"""
    __tablename__ = "position_targets"
    
    id = Column(Integer, primary_key=True)
    position_id = Column(Integer, ForeignKey("positions.id"), nullable=False)
    
    target_index = Column(Integer, nullable=False)  # 1, 2, 3, ...
    price = Column(Float, nullable=False)
    qty = Column(Float, nullable=False)  # Quantity to close at this target
    hit = Column(Boolean, default=False, index=True)
    hit_at = Column(DateTime)
    
    position = relationship("Position", back_populates="targets")


class TradeLog(Base):
    """Comprehensive trade event logging"""
    __tablename__ = "trade_logs"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, index=True)
    position_id = Column(Integer, index=True)
    signal_id = Column(Integer, index=True)
    
    type = Column(String(50), nullable=False)  # OPEN|TP_HIT|SL_HIT|CANCELLED|CLOSE|ERROR
    message = Column(Text)
    meta = Column(JSON, default=dict)  # Exchange response, prices, quantities
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class VerificationToken(Base):
    """Email verification and password reset tokens"""
    __tablename__ = "verification_tokens"
    
    id = Column(Integer, primary_key=True)
    token = Column(String(255), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token_type = Column(String(50), nullable=False)  # email_verification, password_reset
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class HouseSignal(Base):
    """Verzek House Trading Signals from VerzekSignalEngine"""
    __tablename__ = "house_signals"
    
    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(50), nullable=False, index=True)  # SCALPER, TREND, QFL, AI_ML
    symbol = Column(String(50), nullable=False, index=True)
    side = Column(String(10), nullable=False)  # LONG/SHORT
    entry = Column(Float, nullable=False)
    stop_loss = Column(Float, nullable=False)
    take_profits = Column(JSON, nullable=False)  # [tp1, tp2, ...]
    timeframe = Column(String(10), nullable=False)  # M5, M15, H1, H4
    confidence = Column(Integer, nullable=False)  # 0-100
    version = Column(String(20), default="SE.v1.0")
    meta_data = Column('metadata', JSON, default=dict)  # Python attr: meta_data, DB column: metadata (avoiding reserved word)
    
    status = Column(String(20), default="ACTIVE", index=True)  # ACTIVE, CLOSED, CANCELLED, EXPIRED
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    closed_at = Column(DateTime)
    
    positions = relationship("HouseSignalPosition", back_populates="signal", cascade="all, delete-orphan")


class HouseSignalPosition(Base):
    """Position tracking for house signals (paper trading)"""
    __tablename__ = "house_signal_positions"
    
    id = Column(Integer, primary_key=True, index=True)
    signal_id = Column(Integer, ForeignKey("house_signals.id"), nullable=False, index=True)
    
    status = Column(String(20), default="OPEN", index=True)  # OPEN, TP_HIT, SL_HIT, CANCELLED, EXPIRED
    entry_price = Column(Float)
    exit_price = Column(Float)
    tps_hit = Column(JSON, default=list)  # [1, 2] - which TPs were hit
    
    mfe = Column(Float, default=0)  # Maximum Favorable Excursion (%)
    mae = Column(Float, default=0)  # Maximum Adverse Excursion (%)
    pnl_pct = Column(Float, default=0)  # Final P&L percentage
    
    opened_at = Column(DateTime)
    closed_at = Column(DateTime)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    signal = relationship("HouseSignal", back_populates="positions")


class Payment(Base):
    """Payment tracking for subscription upgrades"""
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    
    payment_id = Column(String(255), unique=True, index=True)
    amount_usdt = Column(Float, nullable=False)
    plan_type = Column(String(20), nullable=False)  # VIP, PREMIUM
    
    status = Column(String(20), default="PENDING")  # PENDING|VERIFIED|FAILED
    tx_hash = Column(String(255))  # Blockchain transaction hash
    admin_wallet = Column(String(255))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    verified_at = Column(DateTime)


class DeviceToken(Base):
    """Push notification device tokens (multi-device support)"""
    __tablename__ = "device_tokens"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    push_token = Column(String(255), unique=True, nullable=False, index=True)
    device_name = Column(String(100))  # e.g., "iPhone 13", "Samsung Galaxy S21"
    device_platform = Column(String(20))  # ios, android
    
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True, index=True)
    
    # Relationship
    user = relationship("User", back_populates="device_tokens")
