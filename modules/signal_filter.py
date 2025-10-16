"""
signal_filter.py
----------------
Signal quality filtering system to auto-trade only the best signals.
"""

import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional


class SignalFilter:
    """
    Filters trading signals based on quality score.
    Auto-trades only signals that pass the quality threshold.
    """
    
    def __init__(self):
        self.signal_history = []
        self.provider_stats = {}
        
    def calculate_signal_quality_score(self, signal_data: dict) -> float:
        """
        Calculate quality score for a signal (0-100).
        Higher score = better signal quality.
        
        Scoring factors:
        - Risk/Reward ratio (30 points)
        - Stop loss presence (20 points)
        - Multiple targets (20 points)
        - Entry price clarity (15 points)
        - Provider reputation (15 points)
        """
        score = 0
        
        symbol = signal_data.get('symbol', '')
        entry_price = signal_data.get('entry_price', 0)
        stop_loss = signal_data.get('stop_loss', 0)
        targets = signal_data.get('targets', [])
        signal_type = signal_data.get('signal_type', '')
        
        if entry_price <= 0:
            return 0
        
        if stop_loss <= 0:
            score += 5
        else:
            score += 20
            
            if targets:
                first_target = targets[0].get('price', 0)
                
                if signal_type == 'long':
                    risk = abs(entry_price - stop_loss)
                    reward = abs(first_target - entry_price)
                elif signal_type == 'short':
                    risk = abs(stop_loss - entry_price)
                    reward = abs(entry_price - first_target)
                else:
                    risk = 1
                    reward = 1
                
                if risk > 0:
                    rr_ratio = reward / risk
                    
                    if rr_ratio >= 3:
                        score += 30
                    elif rr_ratio >= 2:
                        score += 25
                    elif rr_ratio >= 1.5:
                        score += 20
                    elif rr_ratio >= 1:
                        score += 15
                    else:
                        score += 5
        
        if len(targets) >= 4:
            score += 20
        elif len(targets) >= 3:
            score += 15
        elif len(targets) >= 2:
            score += 10
        elif len(targets) >= 1:
            score += 5
        
        if entry_price > 0:
            score += 15
        
        provider = signal_data.get('provider', 'unknown')
        provider_quality = self._get_provider_quality(provider)
        score += provider_quality * 15
        
        return min(score, 100)
    
    def _get_provider_quality(self, provider: str) -> float:
        """
        Get provider quality rating (0.0 - 1.0).
        Based on historical performance if available.
        """
        if provider not in self.provider_stats:
            return 0.5
        
        stats = self.provider_stats[provider]
        total_signals = stats.get('total', 0)
        successful = stats.get('successful', 0)
        
        if total_signals == 0:
            return 0.5
        
        win_rate = successful / total_signals
        return win_rate
    
    def update_provider_stats(self, provider: str, success: bool):
        """Update provider performance statistics."""
        if provider not in self.provider_stats:
            self.provider_stats[provider] = {
                'total': 0,
                'successful': 0
            }
        
        self.provider_stats[provider]['total'] += 1
        if success:
            self.provider_stats[provider]['successful'] += 1
    
    def should_auto_trade(self, signal_data: dict, user_quality_threshold: float = 60.0) -> tuple:
        """
        Determine if signal should be auto-traded based on quality score.
        
        Returns:
            (should_trade: bool, quality_score: float, reason: str)
        """
        quality_score = self.calculate_signal_quality_score(signal_data)
        
        if quality_score >= user_quality_threshold:
            return (True, quality_score, f"High quality signal (score: {quality_score:.1f})")
        else:
            return (False, quality_score, f"Signal quality below threshold ({quality_score:.1f} < {user_quality_threshold})")
    
    def get_signal_quality_breakdown(self, signal_data: dict) -> dict:
        """Get detailed breakdown of signal quality factors."""
        entry_price = signal_data.get('entry_price', 0)
        stop_loss = signal_data.get('stop_loss', 0)
        targets = signal_data.get('targets', [])
        signal_type = signal_data.get('signal_type', '')
        
        breakdown = {
            'has_stop_loss': stop_loss > 0,
            'has_entry_price': entry_price > 0,
            'target_count': len(targets),
            'risk_reward_ratio': 0,
            'provider_quality': self._get_provider_quality(signal_data.get('provider', 'unknown'))
        }
        
        if entry_price > 0 and stop_loss > 0 and targets:
            first_target = targets[0].get('price', 0)
            
            if signal_type == 'long':
                risk = abs(entry_price - stop_loss)
                reward = abs(first_target - entry_price)
            elif signal_type == 'short':
                risk = abs(stop_loss - entry_price)
                reward = abs(entry_price - first_target)
            else:
                risk = 1
                reward = 1
            
            if risk > 0:
                breakdown['risk_reward_ratio'] = reward / risk
        
        return breakdown


signal_filter = SignalFilter()
