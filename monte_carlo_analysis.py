#!/usr/bin/env python3
"""
Monte Carlo Analysis for SPX 0DTE Option Plays
Analyzing 6490P and 6510C setups from alphavantage data
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
import json

# Current market data from alphavantage MCP
SPX_CURRENT = 6503
SPY_PRICE = 650.33
TRADING_DAYS_TO_EXPIRY = 1  # 0DTE
HOURS_TO_EXPIRY = 16  # Market opens at 9:30 AM ET

# Historical volatility calculation from SPY range
SESSION_HIGH = 650.86
SESSION_LOW = 647.22
SESSION_RANGE = SESSION_HIGH - SESSION_LOW
DAILY_RANGE_PCT = SESSION_RANGE / SPY_PRICE

# Estimate annualized volatility from daily range (approximation)
HISTORICAL_VOL = DAILY_RANGE_PCT * np.sqrt(252) * 100  # ~31% annualized

# Option setups from analysis
PUT_STRIKE = 6490
PUT_ENTRY_LOW = 2.50
PUT_ENTRY_HIGH = 3.50
PUT_ENTRY_MID = (PUT_ENTRY_LOW + PUT_ENTRY_HIGH) / 2

CALL_STRIKE = 6510
CALL_ENTRY_LOW = 3.00
CALL_ENTRY_HIGH = 4.00
CALL_ENTRY_MID = (CALL_ENTRY_LOW + CALL_ENTRY_HIGH) / 2

# Monte Carlo parameters
NUM_SIMULATIONS = 50000
RISK_FREE_RATE = 0.045  # Current risk-free rate

def black_scholes_put(S, K, T, r, sigma):
    """Black-Scholes Put Option Price"""
    d1 = (np.log(S/K) + (r + sigma**2/2)*T) / (sigma*np.sqrt(T))
    d2 = d1 - sigma*np.sqrt(T)
    put_price = K*np.exp(-r*T)*stats.norm.cdf(-d2) - S*stats.norm.cdf(-d1)
    return put_price

def black_scholes_call(S, K, T, r, sigma):
    """Black-Scholes Call Option Price"""
    d1 = (np.log(S/K) + (r + sigma**2/2)*T) / (sigma*np.sqrt(T))
    d2 = d1 - sigma*np.sqrt(T)
    call_price = S*stats.norm.cdf(d1) - K*np.exp(-r*T)*stats.norm.cdf(d2)
    return call_price

def monte_carlo_simulation():
    """Run Monte Carlo simulation for both option plays"""
    
    # Time to expiration (0DTE - very short time frame)
    T = HOURS_TO_EXPIRY / (365 * 24)  # Convert hours to years
    
    # Volatility scenarios (account for vol expansion near close)
    vol_scenarios = [
        HISTORICAL_VOL * 0.8,  # Low vol scenario
        HISTORICAL_VOL,        # Base scenario  
        HISTORICAL_VOL * 1.3,  # High vol scenario (0DTE expansion)
        HISTORICAL_VOL * 1.8   # Extreme vol scenario
    ]
    
    results = {}
    
    for i, vol in enumerate(vol_scenarios):
        scenario_name = ['Low Vol', 'Base Vol', 'High Vol', 'Extreme Vol'][i]
        vol_decimal = vol / 100
        
        # Generate random price paths
        np.random.seed(42 + i)  # For reproducible results
        
        # Geometric Brownian Motion for price simulation
        dt = T
        drift = (RISK_FREE_RATE - 0.5 * vol_decimal**2) * dt
        diffusion = vol_decimal * np.sqrt(dt) * np.random.normal(0, 1, NUM_SIMULATIONS)
        
        # Simulate final SPX prices
        final_prices = SPX_CURRENT * np.exp(drift + diffusion)
        
        # Calculate option payoffs at expiration
        put_payoffs = np.maximum(PUT_STRIKE - final_prices, 0)
        call_payoffs = np.maximum(final_prices - CALL_STRIKE, 0)
        
        # Calculate P&L (payoff minus premium paid)
        put_pnl = put_payoffs - PUT_ENTRY_MID
        call_pnl = call_payoffs - CALL_ENTRY_MID
        
        # Calculate statistics
        results[scenario_name] = {
            'vol_used': vol,
            'put_analysis': {
                'prob_profit': np.mean(put_pnl > 0) * 100,
                'prob_50pct_profit': np.mean(put_pnl > PUT_ENTRY_MID * 0.5) * 100,
                'prob_100pct_profit': np.mean(put_pnl > PUT_ENTRY_MID) * 100,
                'avg_pnl': np.mean(put_pnl),
                'max_profit': np.max(put_pnl),
                'max_loss': -PUT_ENTRY_MID,
                'breakeven': PUT_STRIKE - PUT_ENTRY_MID,
                'prob_itm': np.mean(final_prices < PUT_STRIKE) * 100,
                'avg_profit_when_win': np.mean(put_pnl[put_pnl > 0]) if np.any(put_pnl > 0) else 0,
                'avg_loss_when_lose': np.mean(put_pnl[put_pnl < 0]) if np.any(put_pnl < 0) else 0
            },
            'call_analysis': {
                'prob_profit': np.mean(call_pnl > 0) * 100,
                'prob_50pct_profit': np.mean(call_pnl > CALL_ENTRY_MID * 0.5) * 100,
                'prob_100pct_profit': np.mean(call_pnl > CALL_ENTRY_MID) * 100,
                'avg_pnl': np.mean(call_pnl),
                'max_profit': np.max(call_pnl),
                'max_loss': -CALL_ENTRY_MID,
                'breakeven': CALL_STRIKE + CALL_ENTRY_MID,
                'prob_itm': np.mean(final_prices > CALL_STRIKE) * 100,
                'avg_profit_when_win': np.mean(call_pnl[call_pnl > 0]) if np.any(call_pnl > 0) else 0,
                'avg_loss_when_lose': np.mean(call_pnl[call_pnl < 0]) if np.any(call_pnl < 0) else 0
            },
            'price_stats': {
                'avg_final_price': np.mean(final_prices),
                'std_final_price': np.std(final_prices),
                'prob_above_6510': np.mean(final_prices > 6510) * 100,
                'prob_below_6490': np.mean(final_prices < 6490) * 100,
                'prob_in_range': np.mean((final_prices >= 6490) & (final_prices <= 6510)) * 100
            }
        }
    
    return results

def print_analysis_summary(results):
    """Print formatted analysis summary"""
    
    print("MONTE CARLO ANALYSIS - SPX 0DTE OPTIONS")
    print("=" * 60)
    print(f"Current SPX: {SPX_CURRENT}")
    print(f"Historical Vol: {HISTORICAL_VOL:.1f}%")
    print(f"Time to Expiry: {HOURS_TO_EXPIRY} hours")
    print()
    
    print("PUT SETUP: 6490P @ $3.00 (Break below 648 support)")
    print("-" * 50)
    for scenario, data in results.items():
        put_data = data['put_analysis']
        print(f"\n{scenario} ({data['vol_used']:.1f}%):")
        print(f"  Prob Profit: {put_data['prob_profit']:.1f}%")
        print(f"  Prob 50%+ Gain: {put_data['prob_50pct_profit']:.1f}%")
        print(f"  Prob 100%+ Gain: {put_data['prob_100pct_profit']:.1f}%")
        print(f"  Avg P&L: ${put_data['avg_pnl']:.2f}")
        print(f"  Breakeven: {put_data['breakeven']:.0f}")
        print(f"  Prob ITM: {put_data['prob_itm']:.1f}%")
    
    print("\nCALL SETUP: 6510C @ $3.50 (Break above 651 resistance)")
    print("-" * 50)
    for scenario, data in results.items():
        call_data = data['call_analysis']
        print(f"\n{scenario} ({data['vol_used']:.1f}%):")
        print(f"  Prob Profit: {call_data['prob_profit']:.1f}%")
        print(f"  Prob 50%+ Gain: {call_data['prob_50pct_profit']:.1f}%")
        print(f"  Prob 100%+ Gain: {call_data['prob_100pct_profit']:.1f}%")
        print(f"  Avg P&L: ${call_data['avg_pnl']:.2f}")
        print(f"  Breakeven: {call_data['breakeven']:.0f}")
        print(f"  Prob ITM: {call_data['prob_itm']:.1f}%")

if __name__ == "__main__":
    print("Running Monte Carlo Analysis for SPX 0DTE Options...")
    results = monte_carlo_simulation()
    print_analysis_summary(results)
    
    # Save results to JSON for further analysis
    with open('.spx/monte_carlo_results.json', 'w') as f:
        # Convert numpy types to native Python types for JSON serialization
        json_results = {}
        for scenario, data in results.items():
            json_results[scenario] = {}
            for key, value in data.items():
                if isinstance(value, dict):
                    json_results[scenario][key] = {k: float(v) if isinstance(v, np.number) else v 
                                                   for k, v in value.items()}
                else:
                    json_results[scenario][key] = float(value) if isinstance(value, np.number) else value
        
        json.dump(json_results, f, indent=2)
    
    print(f"\nResults saved to .spx/monte_carlo_results.json")