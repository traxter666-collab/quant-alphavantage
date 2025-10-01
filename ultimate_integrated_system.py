"""
Ultimate Integrated Trading System
Combines EMA + Demand Zones + SP500 + Strike Forecasting + GEX/DEX + Chop Filter
With dynamic position sizing, exit management, and comprehensive backtesting
"""

from gex_dex_advanced_system import (
    GEXDEXAnalyzer, DynamicExitManager, GEXDEXBacktester,
    OptimalEntry, ExitSignal, HoldTimeframe
)

class UltimateIntegratedTradingSystem(UltimateRealTimeMonitor):
    """Ultimate trading system integrating all analysis components"""
    
    def __init__(self, config: EnhancedConfig):
        super().__init__(config)
        
        # Initialize GEX/DEX system
        self.gex_dex_analyzer = GEXDEXAnalyzer()
        self.exit_manager = DynamicExitManager()
        self.backtester = GEXDEXBacktester()
        
        # Position and performance tracking
        self.active_positions = {}
        self.position_history = []
        self.daily_performance = {}
        
        # Enhanced performance metrics
        self.performance_stats.update({
            'gex_dex_entries': 0,
            'optimal_exits': 0,
            'total_positions': 0,
            'winning_positions': 0,
            'current_portfolio_heat': 0.0,
            'best_win_rate_timeframe': 'UNKNOWN',
            'total_pnl': 0.0,
            'largest_winner': 0.0,
            'largest_loser': 0.0
        })
    
    async def start_monitoring(self):
        """Ultimate integrated monitoring system"""
        logging.info("🎯 STARTING ULTIMATE INTEGRATED TRADING SYSTEM 🎯")
        logging.info("📊 Components: EMA + Demand + SP500 + Forecasting + GEX/DEX + Exits")
        logging.info("⚡ Timeframes: 30s, 1m, 3m, 5m, 30m, 1h with dynamic sizing")
        
        await self.data_manager.initialize()
        await self.sp500_monitor.initialize()
        self.running = True
        
        # Ultimate integrated monitoring tasks
        tasks = [
            asyncio.create_task(self._ultimate_entry_monitor()),           # 1s: Ultimate entry detection
            asyncio.create_task(self._gex_dex_analysis_monitor()),         # 5s: GEX/DEX analysis
            asyncio.create_task(self._position_management_monitor()),      # 2s: Position monitoring
            asyncio.create_task(self._dynamic_exit_monitor()),             # 1s: Dynamic exit management
            asyncio.create_task(self._comprehensive_analysis_monitor()),   # 10s: Full analysis
            asyncio.create_task(self._performance_optimization_monitor()), # 30s: Performance optimization
            asyncio.create_task(self._risk_management_monitor()),          # 5s: Risk management
            asyncio.create_task(self._backtesting_monitor()),             # 300s: Continuous backtesting
        ]
        
        try:
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            logging.info("🛑 Ultimate Integrated System Shutdown")
            await self._generate_daily_report()
            self.running = False
    
    async def _ultimate_entry_monitor(self):
        """Ultimate entry detection combining all systems"""
        while self.running:
            try:
                start_time = time.time()
                
                # Gather all market data
                market_data = await self._gather_ultimate_market_data()
                if not market_data:
                    await asyncio.sleep(1.0)
                    continue
                
                # Get all analysis components
                ema_analysis = await self._get_current_ema_analysis(market_data)
                forecasts = list(self.current_strike_forecasts.values())
                sp500_influence = await self.sp500_monitor.analyze_sp500_influence()
                option_chain = await self._get_live_option_chain()
                
                # Run GEX/DEX analysis for optimal entries
                optimal_entries = await self.gex_dex_analyzer.analyze_optimal_entry_points(
                    market_data, option_chain, forecasts, sp500_influence
                )
                
                # Filter entries by EMA and chop zone conditions
                validated_entries = await self._validate_entries_with_all_systems(
                    optimal_entries, ema_analysis, market_data
                )
                
                # Execute highest probability entries
                if validated_entries:
                    await self._execute_optimal_entries(validated_entries)
                
                # Performance tracking
                calculation_time = time.time() - start_time
                self.performance_stats['calculations_per_second'] = 1 / calculation_time
                
                await asyncio.sleep(1.0)
                
            except Exception as e:
                logging.error(f"Error in ultimate entry monitor: {e}")
                await asyncio.sleep(1.0)
    
    async def _gex_dex_analysis_monitor(self):
        """5-second GEX/DEX analysis monitor"""
        while self.running:
            try:
                # Get current option chain and market data
                option_chain = await self._get_live_option_chain()
                market_data = await self._gather_ultimate_market_data()
                
                if option_chain and market_data:
                    # Calculate GEX/DEX levels
                    gex_levels = await self.gex_dex_analyzer._calculate_gex_levels(option_chain, market_data)
                    dex_levels = await self.gex_dex_analyzer._calculate_dex_levels(option_chain, market_data)
                    
                    # Store for use by other monitors
                    self.current_gex_levels = gex_levels
                    self.current_dex_levels = dex_levels
                    
                    # Send GEX/DEX alerts for significant changes
                    await self._check_gex_dex_alerts(gex_levels, dex_levels, market_data)
                
                await asyncio.sleep(5.0)
                
            except Exception as e:
                logging.error(f"Error in GEX/DEX analysis monitor: {e}")
                await asyncio.sleep(5.0)
    
    async def _position_management_monitor(self):
        """2-second position management monitor"""
        while self.running:
            try:
                if not self.active_positions:
                    await asyncio.sleep(2.0)
                    continue
                
                # Update position P&L and metrics
                await self._update_position_metrics()
                
                # Check for position adjustments
                adjustments = await self._check_position_adjustments()
                
                if adjustments:
                    await self._apply_position_adjustments(adjustments)
                
                # Update portfolio heat
                await self._update_portfolio_heat()
                
                await asyncio.sleep(2.0)
                
            except Exception as e:
                logging.error(f"Error in position management monitor: {e}")
                await asyncio.sleep(2.0)
    
    async def _dynamic_exit_monitor(self):
        """1-second dynamic exit monitoring"""
        while self.running:
            try:
                if not self.active_positions:
                    await asyncio.sleep(1.0)
                    continue
                
                # Get current market conditions
                market_data = await self._gather_ultimate_market_data()
                gex_levels = getattr(self, 'current_gex_levels', [])
                dex_levels = getattr(self, 'current_dex_levels', [])
                
                # Check for exit signals
                exit_signals = await self.exit_manager.monitor_active_positions(
                    self.active_positions, gex_levels, dex_levels, market_data
                )
                
                # Execute exits
                if exit_signals:
                    await self._execute_dynamic_exits(exit_signals)
                
                await asyncio.sleep(1.0)
                
            except Exception as e:
                logging.error(f"Error in dynamic exit monitor: {e}")
                await asyncio.sleep(1.0)
    
    async def _performance_optimization_monitor(self):
        """30-second performance optimization monitor"""
        while self.running:
            try:
                # Analyze recent performance
                performance_analysis = await self._analyze_recent_performance()
                
                # Optimize model weights based on performance
                await self._optimize_system_weights(performance_analysis)
                
                # Adjust risk parameters if needed
                await self._adjust_risk_parameters(performance_analysis)
                
                # Log performance summary
                await self._log_performance_summary()
                
                await asyncio.sleep(30.0)
                
            except Exception as e:
                logging.error(f"Error in performance optimization monitor: {e}")
                await asyncio.sleep(30.0)
    
    async def _risk_management_monitor(self):
        """5-second risk management monitor"""
        while self.running:
            try:
                # Check portfolio-wide risk metrics
                risk_metrics = await self._calculate_portfolio_risk_metrics()
                
                # Check for risk limit breaches
                risk_breaches = self._check_risk_limit_breaches(risk_metrics)
                
                if risk_breaches:
                    await self._handle_risk_breaches(risk_breaches)
                
                # Update risk-adjusted position sizing
                await self._update_risk_adjusted_sizing()
                
                await asyncio.sleep(5.0)
                
            except Exception as e:
                logging.error(f"Error in risk management monitor: {e}")
                await asyncio.sleep(5.0)
    
    async def _backtesting_monitor(self):
        """5-minute continuous backtesting monitor"""
        while self.running:
            try:
                # Run continuous backtesting on recent strategies
                strategies = ['SUPPORT_BOUNCE', 'RESISTANCE_REJECTION', 'MOMENTUM_DEX', 
                             'CONFLUENCE', 'GAMMA_SQUEEZE']
                timeframes = ['30s', '1m', '3m', '5m', '30m', '1h']
                
                backtest_results = await self.backtester.run_comprehensive_backtest(
                    strategies, timeframes, {}
                )
                
                # Update strategy rankings based on backtest
                await self._update_strategy_rankings(backtest_results)
                
                # Log best performing combinations
                best_combos = backtest_results.get('best_combinations', [])[:3]
                if best_combos:
                    logging.info("🎯 Top Strategy Combinations:")
                    for i, combo in enumerate(best_combos, 1):
                        logging.info(f"  #{i}: {combo['strategy']} @ {combo['timeframe']} "
                                   f"(WR: {combo['win_rate']:.1%}, Ret: {combo['total_return']:.1f}%)")
                
                await asyncio.sleep(300.0)  # 5 minutes
                
            except Exception as e:
                logging.error(f"Error in backtesting monitor: {e}")
                await asyncio.sleep(300.0)
    
    # ============================================================================
    # CORE INTEGRATION METHODS
    # ============================================================================
    
    async def _validate_entries_with_all_systems(self, optimal_entries: List[OptimalEntry],
                                                ema_analysis: Dict, market_data: Dict) -> List[OptimalEntry]:
        """Validate entries against all analysis systems"""
        validated_entries = []
        
        # Get chop zone status
        chop_allowed = ema_analysis.get('trade_allowed', True)
        if not chop_allowed:
            logging.info("🌊 All entries blocked by Chop Zone filter")
            return validated_entries
        
        for entry in optimal_entries:
            validation_score = 0
            validation_reasons = []
            
            # EMA alignment validation (25 points)
            ema_direction = ema_analysis.get('direction', 'NEUTRAL')
            entry_bullish = entry.contract_type == 'CALL'
            
            if (entry_bullish and ema_direction == 'BULLISH') or (not entry_bullish and ema_direction == 'BEARISH'):
                validation_score += 25
                validation_reasons.append('EMA_ALIGNED')
            elif ema_direction == 'NEUTRAL':
                validation_score += 15
                validation_reasons.append('EMA_NEUTRAL')
            else:
                validation_score += 5
                validation_reasons.append('EMA_DIVERGENT')
            
            # Strike forecast alignment (20 points)
            forecast_alignment = self._check_forecast_alignment(entry)
            validation_score += forecast_alignment
            if forecast_alignment > 15:
                validation_reasons.append('FORECAST_ALIGNED')
            
            # SP500 alignment (15 points)
            sp500_alignment = await self._check_sp500_alignment(entry)
            validation_score += sp500_alignment
            if sp500_alignment > 10:
                validation_reasons.append('SP500_ALIGNED')
            
            # GEX/DEX strength (25 points)
            gex_dex_strength = self._calculate_gex_dex_strength(entry)
            validation_score += gex_dex_strength
            if gex_dex_strength > 20:
                validation_reasons.append('STRONG_GEX_DEX')
            
            # Win rate threshold (15 points)
            if entry.win_probability >= 80:
                validation_score += 15
                validation_reasons.append('HIGH_WIN_RATE')
            elif entry.win_probability >= 70:
                validation_score += 10
                validation_reasons.append('GOOD_WIN_RATE')
            elif entry.win_probability >= 65:
                validation_score += 5
                validation_reasons.append('ACCEPTABLE_WIN_RATE')
            
            # Overall validation threshold
            if validation_score >= 70:  # Minimum 70/100 validation score
                entry.validation_score = validation_score
                entry.validation_reasons = validation_reasons
                validated_entries.append(entry)
                
                logging.info(f"✅ Entry Validated: {entry.contract_type} {entry.target_strike} "
                           f"({entry.time_horizon}) - Score: {validation_score}/100 "
                           f"- Reasons: {', '.join(validation_reasons)}")
        
        return validated_entries
    
    async def _execute_optimal_entries(self, validated_entries: List[OptimalEntry]):
        """Execute validated optimal entries"""
        for entry in validated_entries:
            # Check if we can add this position (risk management)
            if not await self._can_add_position(entry):
                continue
            
            # Execute the entry
            position_id = await self._execute_entry(entry)
            
            if position_id:
                # Send entry alert
                await self._send_entry_execution_alert(entry, position_id)
                
                # Update performance tracking
                self.performance_stats['total_positions'] += 1
                self.performance_stats['gex_dex_entries'] += 1
    
    async def _execute_entry(self, entry: OptimalEntry) -> Optional[str]:
        """Execute individual entry and return position ID"""
        position_id = f"{entry.contract_type}_{entry.target_strike}_{datetime.now().strftime('%H%M%S')}"
        
        # Create position record
        position = {
            'id': position_id,
            'entry_price': entry.entry_price,
            'entry_time': entry.entry_time,
            'contract_type': entry.contract_type,
            'target_strike': entry.target_strike,
            'position_size': entry.position_size,
            'win_probability': entry.win_probability,
            'expected_return': entry.expected_return,
            'max_risk': entry.max_risk,
            'time_horizon': entry.time_horizon,
            'exit_triggers': entry.exit_triggers,
            'gex_support': entry.gex_support,
            'dex_support': entry.dex_support,
            'validation_score': getattr(entry, 'validation_score', 0),
            'validation_reasons': getattr(entry, 'validation_reasons', []),
            'current_pnl': 0.0,
            'max_pnl': 0.0,
            'min_pnl': 0.0,
            'status': 'ACTIVE'
        }
        
        # Add to active positions
        self.active_positions[position_id] = position
        
        # Update portfolio heat
        self.performance_stats['current_portfolio_heat'] += entry.position_size
        
        logging.info(f"🚀 POSITION OPENED: {position_id} - {entry.contract_type} {entry.target_strike} "
                   f"({entry.position_size:.1f}% position, {entry.win_probability:.1f}% prob)")
        
        return position_id
    
    async def _execute_dynamic_exits(self, exit_signals: List[ExitSignal]):
        """Execute dynamic exits based on signals"""
        for signal in exit_signals:
            # Find the position to exit
            position_to_exit = self._find_position_for_exit(signal)
            
            if position_to_exit:
                # Execute the exit
                await self._execute_exit(position_to_exit, signal)
                
                # Send exit alert
                await self._send_exit_execution_alert(position_to_exit, signal)
                
                # Update performance tracking
                self.performance_stats['optimal_exits'] += 1
                if signal.success:
                    self.performance_stats['winning_positions'] += 1
    
    async def _execute_exit(self, position: Dict, signal: ExitSignal):
        """Execute individual position exit"""
        position_id = position['id']
        
        # Calculate final P&L
        final_pnl = signal.profit_loss_pct
        position_size = position['position_size']
        dollar_pnl = (final_pnl / 100) * position_size
        
        # Update position record
        position['exit_price'] = signal.exit_price
        position['exit_time'] = datetime.now()
        position['exit_reason'] = signal.exit_reason
        position['final_pnl'] = final_pnl
        position['dollar_pnl'] = dollar_pnl
        position['hold_duration'] = signal.hold_duration
        position['status'] = 'CLOSED'
        
        # Move to position history
        self.position_history.append(position)
        
        # Remove from active positions
        del self.active_positions[position_id]
        
        # Update portfolio heat
        self.performance_stats['current_portfolio_heat'] -= position_size
        
        # Update P&L tracking
        self.performance_stats['total_pnl'] += dollar_pnl
        
        if dollar_pnl > 0:
            self.performance_stats['largest_winner'] = max(
                self.performance_stats['largest_winner'], dollar_pnl
            )
        else:
            self.performance_stats['largest_loser'] = min(
                self.performance_stats['largest_loser'], dollar_pnl
            )
        
        # Log exit
        success_emoji = "✅" if signal.success else "❌"
        logging.info(f"{success_emoji} POSITION CLOSED: {position_id} - "
                   f"P&L: {final_pnl:+.1f}% (${dollar_pnl:+.0f}) - "
                   f"Duration: {signal.hold_duration} - Reason: {signal.exit_reason}")
    
    # ============================================================================
    # HELPER METHODS
    # ============================================================================
    
    def _check_forecast_alignment(self, entry: OptimalEntry) -> float:
        """Check alignment with current strike forecasts"""
        alignment_score = 0
        target_strike = entry.target_strike
        
        # Check if any forecasts support this strike
        for forecast in self.current_strike_forecasts.values():
            distance = abs(forecast.strike_price - target_strike)
            if distance <= 5:  # Within $5
                alignment_score = max(alignment_score, forecast.probability / 5)  # Convert to 0-20 scale
        
        return min(20, alignment_score)
    
    async def _check_sp500_alignment(self, entry: OptimalEntry) -> float:
        """Check SP500 alignment for entry"""
        try:
            sp500_influence = await self.sp500_monitor.analyze_sp500_influence()
            sp500_direction = sp500_influence.get('weighted_direction', 'NEUTRAL')
            sp500_confidence = sp500_influence.get('confidence_score', 50)
            
            entry_bullish = entry.contract_type == 'CALL'
            
            if (entry_bullish and sp500_direction == 'BULLISH') or (not entry_bullish and sp500_direction == 'BEARISH'):
                return (sp500_confidence / 100) * 15  # 0-15 points
            elif sp500_direction == 'NEUTRAL':
                return 7  # Neutral gets middle score
            else:
                return 2  # Divergent gets minimal score
                
        except Exception:
            return 5  # Default score if SP500 data unavailable
    
    def _calculate_gex_dex_strength(self, entry: OptimalEntry) -> float:
        """Calculate GEX/DEX strength for entry"""
        strength_score = 0
        
        # GEX strength
        gex_support = entry.gex_support
        if gex_support:
            gex_strength = gex_support.get('strength', 0)
            strength_score += min(15, gex_strength / 5)  # 0-15 points from GEX
        
        # DEX strength  
        dex_support = entry.dex_support
        if dex_support:
            hedge_pressure = dex_support.get('hedge_pressure', 0)
            strength_score += min(10, hedge_pressure * 2)  # 0-10 points from DEX
        
        return min(25, strength_score)
    
    async def _can_add_position(self, entry: OptimalEntry) -> bool:
        """Check if we can add this position within risk limits"""
        # Check portfolio heat
        current_heat = self.performance_stats['current_portfolio_heat']
        if current_heat + entry.position_size > 15.0:  # 15% max portfolio heat
            logging.warning(f"⚠️ Position rejected: Portfolio heat limit ({current_heat:.1f}% + {entry.position_size:.1f}% > 15%)")
            return False
        
        # Check maximum concurrent positions
        if len(self.active_positions) >= 5:  # Max 5 concurrent positions
            logging.warning(f"⚠️ Position rejected: Too many concurrent positions ({len(self.active_positions)}/5)")
            return False
        
        # Check position concentration (no more than 40% in same direction)
        same_direction_heat = sum(
            pos['position_size'] for pos in self.active_positions.values()
            if pos['contract_type'] == entry.contract_type
        )
        
        if same_direction_heat + entry.position_size > 6.0:  # 6% max same direction
            logging.warning(f"⚠️ Position rejected: Too much {entry.contract_type} exposure "
                          f"({same_direction_heat:.1f}% + {entry.position_size:.1f}% > 6%)")
            return False
        
        return True
    
    def _find_position_for_exit(self, signal: ExitSignal) -> Optional[Dict]:
        """Find position corresponding to exit signal"""
        # Simple matching - in real implementation, would use more sophisticated matching
        for position in self.active_positions.values():
            # Match based on exit price proximity and timing
            price_distance = abs(position['entry_price'] - signal.exit_price)
            if price_distance < position['entry_price'] * 0.05:  # Within 5%
                return position
        
        return None
    
    async def _update_position_metrics(self):
        """Update metrics for all active positions"""
        current_price = 6450  # Get from real market data
        
        for position in self.active_positions.values():
            # Calculate current P&L
            current_pnl = self._calculate_position_pnl(position, current_price)
            position['current_pnl'] = current_pnl
            
            # Update max/min P&L
            position['max_pnl'] = max(position['max_pnl'], current_pnl)
            position['min_pnl'] = min(position['min_pnl'], current_pnl)
    
    def _calculate_position_pnl(self, position: Dict, current_price: float) -> float:
        """Calculate current P&L for position"""
        entry_price = position['entry_price']
        contract_type = position['contract_type']
        
        # Simplified P&L calculation
        if contract_type == 'CALL':
            price_move = current_price - entry_price
        else:  # PUT
            price_move = entry_price - current_price
        
        # Convert price move to percentage return (simplified)
        pnl_pct = (price_move / entry_price) * 100
        
        return max(-50, min(200, pnl_pct))  # Cap at -50% to +200%
    
    async def _send_entry_execution_alert(self, entry: OptimalEntry, position_id: str):
        """Send entry execution alert"""
        embed = {
            "title": "🚀 POSITION OPENED",
            "description": f"**{entry.contract_type} {entry.target_strike}** | **{entry.time_horizon}** | **{entry.win_probability:.1f}% Probability**",
            "color": 3447003 if entry.contract_type == 'CALL' else 15158332,
            "timestamp": datetime.utcnow().isoformat(),
            "fields": [
                {
                    "name": "💰 Position Size",
                    "value": f"{entry.position_size:.1f}%",
                    "inline": True
                },
                {
                    "name": "📊 Expected Return",
                    "value": f"{entry.expected_return:.0f}%",
                    "inline": True
                },
                {
                    "name": "⚠️ Max Risk",
                    "value": f"{entry.max_risk:.1f}%",
                    "inline": True
                },
                {
                    "name": "✅ Validation",
                    "value": f"{getattr(entry, 'validation_score', 0)}/100",
                    "inline": True
                },
                {
                    "name": "🎯 Strategy",
                    "value": entry.gex_support.get('type', 'GEX_DEX_STRATEGY'),
                    "inline": True
                },
                {
                    "name": "⏱️ Exits",
                    "value": "\n".join(entry.exit_triggers[:3]),
                    "inline": False
                }
            ]
        }
        
        payload = {
            "username": "🚀 Position Manager",
            "embeds": [embed]
        }
        
        await self._send_discord_alert(payload)
    
    async def _send_exit_execution_alert(self, position: Dict, signal: ExitSignal):
        """Send exit execution alert"""
        success_color = 3066993 if signal.success else 15158332
        success_emoji = "✅" if signal.success else "❌"
        
        embed = {
            "title": f"{success_emoji} POSITION CLOSED",
            "description": f"**{position['contract_type']} {position['target_strike']}** | **{signal.profit_loss_pct:+.1f}% P&L**",
            "color": success_color,
            "timestamp": datetime.utcnow().isoformat(),
            "fields": [
                {
                    "name": "💰 Dollar P&L",
                    "value": f"${position.get('dollar_pnl', 0):+.0f}",
                    "inline": True
                },
                {
                    "name": "⏱️ Hold Time",
                    "value": str(signal.hold_duration).split('.')[0],
                    "inline": True
                },
                {
                    "name": "📊 Exit Reason",
                    "value": signal.exit_reason[:50],
                    "inline": True
                },
                {
                    "name": "🎯 Strategy",
                    "value": position['gex_support'].get('type', 'GEX_DEX')[:20],
                    "inline": True
                },
                {
                    "name": "📈 Max P&L",
                    "value": f"{position.get('max_pnl', 0):+.1f}%",
                    "inline": True
                },
                {
                    "name": "📉 Min P&L",
                    "value": f"{position.get('min_pnl', 0):+.1f}%",
                    "inline": True
                }
            ]
        }
        
        payload = {
            "username": f"{success_emoji} Exit Manager",
            "embeds": [embed]
        }
        
        await self._send_discord_alert(payload)
    
    async def _generate_daily_report(self):
        """Generate comprehensive daily performance report"""
        total_positions = len(self.position_history)
        if total_positions == 0:
            return
        
        winning_positions = sum(1 for pos in self.position_history if pos.get('final_pnl', 0) > 0)
        win_rate = winning_positions / total_positions
        
        total_pnl = sum(pos.get('dollar_pnl', 0) for pos in self.position_history)
        avg_winner = np.mean([pos['final_pnl'] for pos in self.position_history if pos.get('final_pnl', 0) > 0])
        avg_loser = np.mean([pos['final_pnl'] for pos in self.position_history if pos.get('final_pnl', 0) < 0])
        
        # Generate report
        embed = {
            "title": "📈 DAILY PERFORMANCE REPORT",
            "description": f"**Total P&L: ${total_pnl:+.0f}** | **Win Rate: {win_rate:.1%}**",
            "color": 3066993 if total_pnl > 0 else 15158332,
            "timestamp": datetime.utcnow().isoformat(),
            "fields": [
                {
                    "name": "📊 Positions",
                    "value": f"Total: {total_positions}\nWins: {winning_positions}\nLosses: {total_positions - winning_positions}",
                    "inline": True
                },
                {
                    "name": "💰 P&L Metrics",
                    "value": f"Avg Win: {avg_winner:.1f}%\nAvg Loss: {avg_loser:.1f}%\nLargest Win: ${self.performance_stats['largest_winner']:+.0f}",
                    "inline": True
                },
                {
                    "name": "⚡ Performance",
                    "value": f"GEX/DEX Entries: {self.performance_stats['gex_dex_entries']}\nOptimal Exits: {self.performance_stats['optimal_exits']}\nSuccess Rate: {self.performance_stats['forecast_accuracy_rate']:.1%}",
                    "inline": True
                }
            ]
        }
        
        payload = {
            "username": "📈 Daily Report",
            "embeds": [embed]
        }
        
        await self._send_discord_alert(payload)
        
        logging.info("📈 DAILY REPORT GENERATED")
        logging.info(f"📊 Total Positions: {total_positions} | Win Rate: {win_rate:.1%} | P&L: ${total_pnl:+.0f}")
    
    async def _gather_ultimate_market_data(self) -> Dict:
        """Gather ultimate comprehensive market data"""
        try:
            spx_data = await self.data_manager.get_current_spx_data()
            if not spx_data:
                return {}
            
            return {
                'current_price': spx_data['price'],
                'volume': spx_data.get('volume', 0),
                'timestamp': datetime.now()
            }
        except Exception as e:
            logging.error(f"Error gathering market data: {e}")
            return {}

# Example usage with enhanced configuration
if __name__ == "__main__":
    async def main():
        # Enhanced configuration
        config = EnhancedConfig()
        config.DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1422928703972970516/59EBn9XvN6VautbSfjE8p_pFDNX4qIrU6ephGS--UvSiD7nSahftbhQDSW66fQwfXajp"
        
        # Initialize ultimate system
        ultimate_system = UltimateIntegratedTradingSystem(config)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('ultimate_trading_system.log'),
                logging.StreamHandler()
            ]
        )
        
        logging.info("🎯 ULTIMATE INTEGRATED TRADING SYSTEM")
        logging.info("🔥 ALL SYSTEMS INTEGRATED:")
        logging.info("   • EMA Probability Analysis")
        logging.info("   • Demand Zone Detection") 
        logging.info("   • SP500 Weighted Correlation")
        logging.info("   • Dynamic Strike Forecasting")
        logging.info("   • GEX/DEX Analysis & Optimal Entries")
        logging.info("   • Chop Zone Filtering")
        logging.info("   • Dynamic Exit Management")
        logging.info("   • Multi-Timeframe Backtesting")
        logging.info("   • Advanced Risk Management")
        logging.info("   • Real-Time Performance Optimization")
        
        try:
            await ultimate_system.start_monitoring()
        except KeyboardInterrupt:
            logging.info("🛑 Ultimate system stopped by user")
        except Exception as e:
            logging.error(f"💥 Ultimate system crashed: {e}")
        finally:
            await ultimate_system._generate_daily_report()
    
    asyncio.run(main())

                