"""
SBIRS Integrated Ultimate Trading System
Combines all systems: EMA + Demand Zones + SP500 + Forecasting + GEX/DEX + SBIRS + Chop Filter
The most comprehensive 0DTE SPX trading system with breakout/reversal detection
"""

from sbirs_system import SBIRSAnalyzer, SBIRSSignal, SignalType, ConfirmationType

class SBIRSIntegratedUltimateTradingSystem(UltimateIntegratedTradingSystem):
    """Ultimate trading system with SBIRS breakout/reversal detection"""
    
    def __init__(self, config: EnhancedConfig):
        super().__init__(config)
        
        # Initialize SBIRS system
        self.sbirs_analyzer = SBIRSAnalyzer()
        self.active_sbirs_signals = {}
        self.sbirs_performance = {}
        
        # Enhanced performance metrics for SBIRS
        self.performance_stats.update({
            'sbirs_signals_generated': 0,
            'sbirs_signals_triggered': 0,
            'sbirs_successful_signals': 0,
            'breakout_win_rate': 0.0,
            'reversal_win_rate': 0.0,
            'pattern_win_rate': 0.0,
            'momentum_win_rate': 0.0,
            'sbirs_total_pnl': 0.0
        })
    
    async def start_monitoring(self):
        """Ultimate integrated monitoring with SBIRS"""
        logging.info("🎯 STARTING SBIRS INTEGRATED ULTIMATE TRADING SYSTEM 🎯")
        logging.info("🔥 ALL SYSTEMS ACTIVE:")
        logging.info("   • EMA Probability Analysis")
        logging.info("   • Demand Zone Detection")
        logging.info("   • SP500 Weighted Correlation")
        logging.info("   • Dynamic Strike Forecasting")
        logging.info("   • GEX/DEX Analysis")
        logging.info("   • SBIRS Breakout/Reversal Detection")
        logging.info("   • Chop Zone Filtering")
        logging.info("   • Dynamic Exit Management")
        logging.info("   • Multi-Timeframe Backtesting")
        logging.info("   • Advanced Risk Management")
        
        await self.data_manager.initialize()
        await self.sp500_monitor.initialize()
        self.running = True
        
        # Ultimate integrated monitoring tasks with SBIRS
        tasks = [
            asyncio.create_task(self._sbirs_signal_detection_monitor()),    # 2s: SBIRS signal detection
            asyncio.create_task(self._ultimate_entry_monitor()),           # 1s: Ultimate entry detection
            asyncio.create_task(self._sbirs_signal_tracking_monitor()),    # 3s: Track SBIRS signals
            asyncio.create_task(self._position_management_monitor()),      # 2s: Position monitoring
            asyncio.create_task(self._dynamic_exit_monitor()),             # 1s: Dynamic exit management
            asyncio.create_task(self._comprehensive_analysis_monitor()),   # 10s: Full analysis
            asyncio.create_task(self._sbirs_performance_monitor()),        # 60s: SBIRS performance tracking
            asyncio.create_task(self._risk_management_monitor()),          # 5s: Risk management
            asyncio.create_task(self._backtesting_monitor()),             # 300s: Continuous backtesting
        ]
        
        try:
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            logging.info("🛑 SBIRS Integrated System Shutdown")
            await self._generate_sbirs_daily_report()
            self.running = False
    
    async def _sbirs_signal_detection_monitor(self):
        """2-second SBIRS signal detection monitor"""
        while self.running:
            try:
                start_time = time.time()
                
                # Gather market data for SBIRS analysis
                market_data = await self._gather_ultimate_market_data_for_sbirs()
                if not market_data:
                    await asyncio.sleep(2.0)
                    continue
                
                current_price = market_data.get('current_price', 6450)
                
                # Get supporting data
                option_chain = await self._get_live_option_chain()
                gex_dex_data = {
                    'gex_levels': getattr(self, 'current_gex_levels', []),
                    'dex_levels': getattr(self, 'current_dex_levels', [])
                }
                ema_analysis = await self._get_current_ema_analysis(market_data)
                forecasts = list(self.current_strike_forecasts.values())
                
                # Run SBIRS analysis
                sbirs_signals = await self.sbirs_analyzer.analyze_sbirs_signals(
                    market_data, current_price, option_chain, gex_dex_data, 
                    ema_analysis, forecasts
                )
                
                # Process new SBIRS signals
                if sbirs_signals:
                    await self._process_new_sbirs_signals(sbirs_signals)
                
                # Update performance tracking
                self.performance_stats['sbirs_signals_generated'] += len(sbirs_signals)
                
                # Performance tracking
                calculation_time = time.time() - start_time
                if hasattr(self, '_sbirs_calc_times'):
                    self._sbirs_calc_times.append(calculation_time)
                else:
                    self._sbirs_calc_times = [calculation_time]
                
                await asyncio.sleep(2.0)
                
            except Exception as e:
                logging.error(f"Error in SBIRS signal detection: {e}")
                await asyncio.sleep(2.0)
    
    async def _sbirs_signal_tracking_monitor(self):
        """3-second SBIRS signal tracking monitor"""
        while self.running:
            try:
                if not self.active_sbirs_signals:
                    await asyncio.sleep(3.0)
                    continue
                
                # Get current market price
                market_data = await self._gather_ultimate_market_data()
                current_price = market_data.get('current_price', 6450)
                
                # Track all active SBIRS signals
                triggered_signals = []
                failed_signals = []
                
                for signal_id, signal in self.active_sbirs_signals.items():
                    status = await self._check_sbirs_signal_status(signal, current_price)
                    
                    if status == 'TRIGGERED':
                        triggered_signals.append(signal)
                    elif status == 'FAILED':
                        failed_signals.append(signal)
                
                # Process triggered signals
                for signal in triggered_signals:
                    await self._handle_sbirs_signal_trigger(signal, current_price)
                
                # Process failed signals
                for signal in failed_signals:
                    await self._handle_sbirs_signal_failure(signal, current_price)
                
                await asyncio.sleep(3.0)
                
            except Exception as e:
                logging.error(f"Error in SBIRS signal tracking: {e}")
                await asyncio.sleep(3.0)
    
    async def _sbirs_performance_monitor(self):
        """60-second SBIRS performance monitoring"""
        while self.running:
            try:
                # Calculate SBIRS performance metrics
                await self._calculate_sbirs_performance_metrics()
                
                # Log SBIRS performance summary
                await self._log_sbirs_performance_summary()
                
                # Adjust SBIRS parameters based on performance
                await self._optimize_sbirs_parameters()
                
                await asyncio.sleep(60.0)
                
            except Exception as e:
                logging.error(f"Error in SBIRS performance monitor: {e}")
                await asyncio.sleep(60.0)
    
    # ============================================================================
    # SBIRS INTEGRATION METHODS
    # ============================================================================
    
    async def _process_new_sbirs_signals(self, signals: List[SBIRSSignal]):
        """Process new SBIRS signals"""
        for signal in signals:
            # Validate signal with all systems
            if await self._validate_sbirs_signal(signal):
                # Add to active signals
                self.active_sbirs_signals[signal.signal_id] = signal
                
                # Send SBIRS signal alert
                await self._send_sbirs_signal_alert(signal)
                
                # Check for immediate execution opportunity
                await self._check_immediate_sbirs_execution(signal)
                
                logging.info(f"🎯 SBIRS Signal Added: {signal.signal_type.value[0]} @ {signal.price_level:.2f} "
                           f"({signal.confidence_score:.1f}% confidence)")
    
    async def _validate_sbirs_signal(self, signal: SBIRSSignal) -> bool:
        """Validate SBIRS signal with all systems"""
        validation_score = 0
        validation_reasons = []
        
        # Base signal quality (30 points)
        if signal.confidence_score >= 80:
            validation_score += 30
            validation_reasons.append('HIGH_CONFIDENCE')
        elif signal.confidence_score >= 70:
            validation_score += 20
            validation_reasons.append('GOOD_CONFIDENCE')
        else:
            validation_score += 10
            validation_reasons.append('MINIMUM_CONFIDENCE')
        
        # EMA alignment (20 points)
        if signal.ema_alignment:
            validation_score += 20
            validation_reasons.append('EMA_ALIGNED')
        else:
            validation_score += 5
            validation_reasons.append('EMA_NEUTRAL')
        
        # GEX/DEX support (20 points)
        if signal.gex_dex_support:
            validation_score += 20
            validation_reasons.append('GEX_DEX_SUPPORT')
        else:
            validation_score += 5
        
        # Forecast alignment (15 points)
        if signal.forecast_alignment:
            validation_score += 15
            validation_reasons.append('FORECAST_ALIGNED')
        else:
            validation_score += 3
        
        # Risk/reward ratio (10 points)
        if signal.risk_reward_ratio >= 2.0:
            validation_score += 10
            validation_reasons.append('GOOD_RR')
        elif signal.risk_reward_ratio >= 1.5:
            validation_score += 5
            validation_reasons.append('ACCEPTABLE_RR')
        
        # Chop zone filter (5 points penalty if blocked)
        if signal.chop_zone_status == 'BLOCKED':
            validation_score -= 15
            validation_reasons.append('CHOP_BLOCKED')
        else:
            validation_score += 5
            validation_reasons.append('CHOP_ALLOWED')
        
        # Minimum validation threshold
        signal.validation_score = validation_score
        signal.validation_reasons = validation_reasons
        
        return validation_score >= 70  # Minimum 70/100 validation score
    
    async def _check_sbirs_signal_status(self, signal: SBIRSSignal, current_price: float) -> str:
        """Check status of SBIRS signal"""
        # Check if signal has been triggered
        if signal.signal_type in [SignalType.BULLISH_BREAKOUT, SignalType.BULLISH_REVERSAL, 
                                 SignalType.MOMENTUM_CONTINUATION]:
            # Bullish signals
            if current_price >= signal.breakout_target:
                return 'TRIGGERED'
            elif current_price <= signal.stop_loss_level:
                return 'FAILED'
        else:
            # Bearish signals
            if current_price <= signal.breakout_target:
                return 'TRIGGERED'
            elif current_price >= signal.stop_loss_level:
                return 'FAILED'
        
        # Check time expiration
        time_elapsed = (datetime.now() - signal.signal_time).total_seconds() / 60
        max_time = {'1min': 10, '5min': 30, '15min': 60, '30min': 120, '1h': 240}.get(signal.primary_timeframe, 60)
        
        if time_elapsed > max_time:
            return 'EXPIRED'
        
        return 'ACTIVE'
    
    async def _handle_sbirs_signal_trigger(self, signal: SBIRSSignal, current_price: float):
        """Handle SBIRS signal trigger"""
        # Update signal status
        signal.signal_status = 'TRIGGERED'
        signal.trigger_price = current_price
        signal.actual_move = abs(current_price - signal.price_level)
        signal.success = True
        
        # Calculate performance
        expected_move = signal.expected_move
        actual_vs_expected = signal.actual_move / expected_move if expected_move > 0 else 1
        
        # Update performance tracking
        self.performance_stats['sbirs_signals_triggered'] += 1
        self.performance_stats['sbirs_successful_signals'] += 1
        
        # Update signal type performance
        signal_type_name = signal.signal_type.name.lower()
        if 'breakout' in signal_type_name:
            self._update_breakout_performance(True, actual_vs_expected)
        elif 'reversal' in signal_type_name:
            self._update_reversal_performance(True, actual_vs_expected)
        elif 'momentum' in signal_type_name:
            self._update_momentum_performance(True, actual_vs_expected)
        
        # Send trigger alert
        await self._send_sbirs_trigger_alert(signal, current_price)
        
        # Remove from active signals
        if signal.signal_id in self.active_sbirs_signals:
            del self.active_sbirs_signals[signal.signal_id]
        
        logging.info(f"✅ SBIRS TRIGGERED: {signal.signal_type.value[0]} - "
                   f"Target: {signal.breakout_target:.2f} | Actual: {current_price:.2f} | "
                   f"Move: {signal.actual_move:.1f} pts")
    
    async def _handle_sbirs_signal_failure(self, signal: SBIRSSignal, current_price: float):
        """Handle SBIRS signal failure"""
        # Update signal status
        signal.signal_status = 'FAILED'
        signal.trigger_price = current_price
        signal.actual_move = abs(current_price - signal.price_level)
        signal.success = False
        
        # Update performance tracking
        self.performance_stats['sbirs_signals_triggered'] += 1  # Still counts as resolved
        
        # Update signal type performance
        signal_type_name = signal.signal_type.name.lower()
        if 'breakout' in signal_type_name:
            self._update_breakout_performance(False, 0)
        elif 'reversal' in signal_type_name:
            self._update_reversal_performance(False, 0)
        elif 'momentum' in signal_type_name:
            self._update_momentum_performance(False, 0)
        
        # Send failure alert
        await self._send_sbirs_failure_alert(signal, current_price)
        
        # Remove from active signals
        if signal.signal_id in self.active_sbirs_signals:
            del self.active_sbirs_signals[signal.signal_id]
        
        logging.info(f"❌ SBIRS FAILED: {signal.signal_type.value[0]} - "
                   f"Stop: {signal.stop_loss_level:.2f} | Actual: {current_price:.2f}")
    
    async def _check_immediate_sbirs_execution(self, signal: SBIRSSignal):
        """Check if SBIRS signal can be executed immediately"""
        # Only execute high-confidence signals immediately
        if (signal.confidence_score >= 85 and 
            signal.validation_score >= 80 and
            signal.chop_zone_status == 'ALLOWED'):
            
            # Create position based on SBIRS signal
            entry = await self._create_sbirs_entry(signal)
            
            if entry and await self._can_add_position(entry):
                position_id = await self._execute_entry(entry)
                
                if position_id:
                    # Link position to SBIRS signal
                    signal.linked_position_id = position_id
                    
                    logging.info(f"🚀 SBIRS IMMEDIATE EXECUTION: {signal.signal_type.value[0]} -> {position_id}")
    
    async def _create_sbirs_entry(self, signal: SBIRSSignal) -> Optional[OptimalEntry]:
        """Create optimal entry from SBIRS signal"""
        # Determine contract type
        if signal.signal_type in [SignalType.BULLISH_BREAKOUT, SignalType.BULLISH_REVERSAL, 
                                 SignalType.MOMENTUM_CONTINUATION]:
            contract_type = 'CALL'
        else:
            contract_type = 'PUT'
        
        # Calculate position size based on confidence
        base_size = 2.0  # Base 2%
        confidence_multiplier = signal.confidence_score / 70  # 70% = 1x
        validation_multiplier = signal.validation_score / 70  # 70% = 1x
        
        position_size = min(4.0, base_size * confidence_multiplier * validation_multiplier)
        
        # Determine timeframe for hold period
        timeframe_minutes = {
            '1min': 2, '5min': 10, '15min': 30, '30min': 60, '1h': 120
        }.get(signal.primary_timeframe, 15)
        
        # Create entry
        entry = OptimalEntry(
            entry_price=signal.price_level,
            entry_time=datetime.now(),
            contract_type=contract_type,
            target_strike=signal.breakout_target,
            position_size=position_size,
            win_probability=signal.confidence_score,
            expected_return=signal.expected_move / signal.price_level * 100,  # Convert to percentage
            max_risk=abs(signal.price_level - signal.stop_loss_level) / signal.price_level * 100,
            time_horizon=f"{timeframe_minutes}m",
            exit_triggers=[
                f'PROFIT_TARGET_{int(signal.risk_reward_ratio * 50)}%',
                f'STOP_LOSS_{int(50 / signal.risk_reward_ratio)}%',
                f'TIME_LIMIT_{timeframe_minutes}m',
                'SBIRS_INVALIDATION'
            ],
            gex_support={'sbirs_signal': signal.signal_id},
            dex_support={'signal_type': signal.signal_type.name},
            backtest_confidence=signal.pattern_reliability
        )
        
        return entry
    
    # ============================================================================
    # PERFORMANCE TRACKING METHODS
    # ============================================================================
    
    def _update_breakout_performance(self, success: bool, move_ratio: float):
        """Update breakout signal performance"""
        if 'breakout_signals' not in self.sbirs_performance:
            self.sbirs_performance['breakout_signals'] = {'total': 0, 'successful': 0, 'move_ratios': []}
        
        self.sbirs_performance['breakout_signals']['total'] += 1
        if success:
            self.sbirs_performance['breakout_signals']['successful'] += 1
            self.sbirs_performance['breakout_signals']['move_ratios'].append(move_ratio)
        
        # Update performance stats
        total = self.sbirs_performance['breakout_signals']['total']
        successful = self.sbirs_performance['breakout_signals']['successful']
        self.performance_stats['breakout_win_rate'] = successful / total if total > 0 else 0.0
    
    def _update_reversal_performance(self, success: bool, move_ratio: float):
        """Update reversal signal performance"""
        if 'reversal_signals' not in self.sbirs_performance:
            self.sbirs_performance['reversal_signals'] = {'total': 0, 'successful': 0, 'move_ratios': []}
        
        self.sbirs_performance['reversal_signals']['total'] += 1
        if success:
            self.sbirs_performance['reversal_signals']['successful'] += 1
            self.sbirs_performance['reversal_signals']['move_ratios'].append(move_ratio)
        
        # Update performance stats
        total = self.sbirs_performance['reversal_signals']['total']
        successful = self.sbirs_performance['reversal_signals']['successful']
        self.performance_stats['reversal_win_rate'] = successful / total if total > 0 else 0.0
    
    def _update_momentum_performance(self, success: bool, move_ratio: float):
        """Update momentum signal performance"""
        if 'momentum_signals' not in self.sbirs_performance:
            self.sbirs_performance['momentum_signals'] = {'total': 0, 'successful': 0, 'move_ratios': []}
        
        self.sbirs_performance['momentum_signals']['total'] += 1
        if success:
            self.sbirs_performance['momentum_signals']['successful'] += 1
            self.sbirs_performance['momentum_signals']['move_ratios'].append(move_ratio)
        
        # Update performance stats
        total = self.sbirs_performance['momentum_signals']['total']
        successful = self.sbirs_performance['momentum_signals']['successful']
        self.performance_stats['momentum_win_rate'] = successful / total if total > 0 else 0.0
    
    async def _calculate_sbirs_performance_metrics(self):
        """Calculate comprehensive SBIRS performance metrics"""
        total_signals = self.performance_stats['sbirs_signals_triggered']
        successful_signals = self.performance_stats['sbirs_successful_signals']
        
        if total_signals > 0:
            overall_win_rate = successful_signals / total_signals
            
            # Calculate average move accuracy
            all_move_ratios = []
            for signal_type in ['breakout_signals', 'reversal_signals', 'momentum_signals']:
                if signal_type in self.sbirs_performance:
                    all_move_ratios.extend(self.sbirs_performance[signal_type]['move_ratios'])
            
            avg_move_accuracy = np.mean(all_move_ratios) if all_move_ratios else 1.0
            
            # Update performance stats
            self.performance_stats['sbirs_overall_win_rate'] = overall_win_rate
            self.performance_stats['sbirs_move_accuracy'] = avg_move_accuracy
    
    async def _optimize_sbirs_parameters(self):
        """Optimize SBIRS parameters based on performance"""
        # Adjust confidence thresholds based on performance
        if self.performance_stats.get('breakout_win_rate', 0) < 0.6:
            # Increase breakout confidence threshold
            self.sbirs_analyzer.min_confidence = min(80, self.sbirs_analyzer.min_confidence + 2)
        elif self.performance_stats.get('breakout_win_rate', 0) > 0.8:
            # Decrease threshold to catch more signals
            self.sbirs_analyzer.min_confidence = max(65, self.sbirs_analyzer.min_confidence - 1)
        
        # Adjust volume threshold based on performance
        overall_win_rate = self.performance_stats.get('sbirs_overall_win_rate', 0)
        if overall_win_rate < 0.65:
            self.sbirs_analyzer.volume_threshold = min(2.0, self.sbirs_analyzer.volume_threshold + 0.1)
        elif overall_win_rate > 0.85:
            self.sbirs_analyzer.volume_threshold = max(1.2, self.sbirs_analyzer.volume_threshold - 0.05)
    
    # ============================================================================
    # ALERT METHODS
    # ============================================================================
    
    async def _send_sbirs_signal_alert(self, signal: SBIRSSignal):
        """Send SBIRS signal detection alert"""
        # Determine signal color
        if signal.signal_type in [SignalType.BULLISH_BREAKOUT, SignalType.BULLISH_REVERSAL]:
            color = 3066993  # Green
            direction_emoji = "🟢"
        else:
            color = 15158332  # Red
            direction_emoji = "🔴"
        
        # Confidence emoji
        if signal.confidence_score >= 85:
            confidence_emoji = "🔥"
        elif signal.confidence_score >= 75:
            confidence_emoji = "⚡"
        else:
            confidence_emoji = "📊"
        
        embed = {
            "title": f"{confidence_emoji} SBIRS SIGNAL DETECTED",
            "description": f"**{signal.signal_type.value[0]}** {direction_emoji}\n"
                          f"**{signal.confidence_score:.1f}% Confidence** | **{signal.strength_rating}**",
            "color": color,
            "timestamp": datetime.utcnow().isoformat(),
            "fields": [
                {
                    "name": "📍 Signal Level",
                    "value": f"${signal.price_level:.2f}",
                    "inline": True
                },
                {
                    "name": "🎯 Target",
                    "value": f"${signal.breakout_target:.2f}",
                    "inline": True
                },
                {
                    "name": "🛑 Stop Loss",
                    "value": f"${signal.stop_loss_level:.2f}",
                    "inline": True
                },
                {
                    "name": "📊 Risk/Reward",
                    "value": f"{signal.risk_reward_ratio:.1f}:1",
                    "inline": True
                },
                {
                    "name": "📈 Expected Move",
                    "value": f"{signal.expected_move:.1f} pts",
                    "inline": True
                },
                {
                    "name": "⏱️ Timeframe",
                    "value": signal.primary_timeframe,
                    "inline": True
                },
                {
                    "name": "🔊 Volume Ratio",
                    "value": f"{signal.volume_ratio:.1f}x",
                    "inline": True
                },
                {
                    "name": "💪 Momentum",
                    "value": f"{signal.momentum_score:.0f}",
                    "inline": True
                },
                {
                    "name": "✅ Validation",
                    "value": f"{getattr(signal, 'validation_score', 0)}/100",
                    "inline": True
                }
            ]
        }
        
        # Add confirmation info
        confirmation = signal.confirmation_type.value[0]
        embed["fields"].append({
            "name": "🔍 Confirmation",
            "value": confirmation,
            "inline": False
        })
        
        # Add system alignments
        alignments = []
        if signal.ema_alignment:
            alignments.append("EMA ✅")
        if signal.gex_dex_support:
            alignments.append("GEX/DEX ✅")
        if signal.forecast_alignment:
            alignments.append("Forecast ✅")
        
        if alignments:
            embed["fields"].append({
                "name": "🎯 System Alignment",
                "value": " | ".join(alignments),
                "inline": False
            })
        
        payload = {
            "username": "🎯 SBIRS Detection",
            "embeds": [embed]
        }
        
        await self._send_discord_alert(payload)
    
    async def _send_sbirs_trigger_alert(self, signal: SBIRSSignal, current_price: float):
        """Send SBIRS signal trigger alert"""
        move_points = signal.actual_move
        move_percentage = (move_points / signal.price_level) * 100
        
        embed = {
            "title": "✅ SBIRS SIGNAL TRIGGERED",
            "description": f"**{signal.signal_type.value[0]}** HIT TARGET!\n"
                          f"**{move_points:.1f} point move** ({move_percentage:.1f}%)",
            "color": 3066993,  # Green
            "timestamp": datetime.utcnow().isoformat(),
            "fields": [
                {
                    "name": "📍 Signal Price",
                    "value": f"${signal.price_level:.2f}",
                    "inline": True
                },
                {
                    "name": "🎯 Target Hit",
                    "value": f"${signal.breakout_target:.2f}",
                    "inline": True
                },
                {
                    "name": "📊 Actual Price",
                    "value": f"${current_price:.2f}",
                    "inline": True
                },
                {
                    "name": "⚡ Move Achieved",
                    "value": f"{move_points:.1f} pts",
                    "inline": True
                },
                {
                    "name": "⏱️ Time Elapsed",
                    "value": str(datetime.now() - signal.signal_time).split('.')[0],
                    "inline": True
                },
                {
                    "name": "📈 Expected vs Actual",
                    "value": f"{signal.expected_move:.1f} → {move_points:.1f}",
                    "inline": True
                }
            ]
        }
        
        # Add performance context
        if hasattr(signal, 'linked_position_id'):
            embed["fields"].append({
                "name": "🚀 Linked Position",
                "value": signal.linked_position_id,
                "inline": False
            })
        
        payload = {
            "username": "✅ SBIRS Success",
            "embeds": [embed]
        }
        
        await self._send_discord_alert(payload)
    
    async def _send_sbirs_failure_alert(self, signal: SBIRSSignal, current_price: float):
        """Send SBIRS signal failure alert"""
        embed = {
            "title": "❌ SBIRS SIGNAL FAILED",
            "description": f"**{signal.signal_type.value[0]}** hit stop loss",
            "color": 15158332,  # Red
            "timestamp": datetime.utcnow().isoformat(),
            "fields": [
                {
                    "name": "📍 Signal Price",
                    "value": f"${signal.price_level:.2f}",
                    "inline": True
                },
                {
                    "name": "🛑 Stop Hit",
                    "value": f"${signal.stop_loss_level:.2f}",
                    "inline": True
                },
                {
                    "name": "📊 Actual Price",
                    "value": f"${current_price:.2f}",
                    "inline": True
                },
                {
                    "name": "⏱️ Time Elapsed",
                    "value": str(datetime.now() - signal.signal_time).split('.')[0],
                    "inline": True
                },
                {
                    "name": "📉 Loss Amount",
                    "value": f"{abs(current_price - signal.price_level):.1f} pts",
                    "inline": True
                }
            ]
        }
        
        payload = {
            "username": "❌ SBIRS Failure",
            "embeds": [embed]
        }
        
        await self._send_discord_alert(payload)
    
    # ============================================================================
    # LOGGING AND REPORTING
    # ============================================================================
    
    async def _log_sbirs_performance_summary(self):
        """Log SBIRS performance summary"""
        total_signals = self.performance_stats['sbirs_signals_generated']
        triggered_signals = self.performance_stats['sbirs_signals_triggered']
        successful_signals = self.performance_stats['sbirs_successful_signals']
        
        if total_signals > 0:
            trigger_rate = triggered_signals / total_signals
            success_rate = successful_signals / triggered_signals if triggered_signals > 0 else 0
            
            logging.info("🎯 SBIRS PERFORMANCE SUMMARY:")
            logging.info(f"   📊 Signals Generated: {total_signals}")
            logging.info(f"   ⚡ Signals Triggered: {triggered_signals} ({trigger_rate:.1%})")
            logging.info(f"   ✅ Successful Signals: {successful_signals} ({success_rate:.1%})")
            logging.info(f"   🎯 Breakout Win Rate: {self.performance_stats.get('breakout_win_rate', 0):.1%}")
            logging.info(f"   🔄 Reversal Win Rate: {self.performance_stats.get('reversal_win_rate', 0):.1%}")
            logging.info(f"   📈 Momentum Win Rate: {self.performance_stats.get('momentum_win_rate', 0):.1%}")
            
            # Log active signals
            active_count = len(self.active_sbirs_signals)
            if active_count > 0:
                logging.info(f"   🔍 Active Signals: {active_count}")
                for signal_id, signal in list(self.active_sbirs_signals.items())[:3]:
                    logging.info(f"      • {signal.signal_type.value[0][:20]} @ {signal.price_level:.2f}")
    
    async def _generate_sbirs_daily_report(self):
        """Generate comprehensive SBIRS daily report"""
        total_signals = self.performance_stats['sbirs_signals_generated']
        if total_signals == 0:
            return
        
        triggered_signals = self.performance_stats['sbirs_signals_triggered']
        successful_signals = self.performance_stats['sbirs_successful_signals']
        
        # Calculate rates
        trigger_rate = triggered_signals / total_signals if total_signals > 0 else 0
        success_rate = successful_signals / triggered_signals if triggered_signals > 0 else 0
        overall_success = successful_signals / total_signals if total_signals > 0 else 0
        
        # Get individual signal type performance
        breakout_wr = self.performance_stats.get('breakout_win_rate', 0)
        reversal_wr = self.performance_stats.get('reversal_win_rate', 0)
        momentum_wr = self.performance_stats.get('momentum_win_rate', 0)
        
        embed = {
            "title": "🎯 SBIRS DAILY PERFORMANCE REPORT",
            "description": f"**Overall Success Rate: {overall_success:.1%}**\n"
                          f"Smart Breakout/Reversal Signal System Results",
            "color": 3066993 if overall_success > 0.6 else 15158332,
            "timestamp": datetime.utcnow().isoformat(),
            "fields": [
                {
                    "name": "📊 Signal Statistics",
                    "value": f"Generated: {total_signals}\n"
                            f"Triggered: {triggered_signals} ({trigger_rate:.1%})\n"
                            f"Successful: {successful_signals} ({success_rate:.1%})",
                    "inline": True
                },
                {
                    "name": "🎯 Signal Type Performance",
                    "value": f"Breakouts: {breakout_wr:.1%}\n"
                            f"Reversals: {reversal_wr:.1%}\n"
                            f"Momentum: {momentum_wr:.1%}",
                    "inline": True
                },
                {
                    "name": "⚙️ System Integration",
                    "value": f"EMA Aligned: {sum(1 for s in self.sbirs_analyzer.signal_history if hasattr(s, 'ema_alignment') and s.ema_alignment)}\n"
                            f"GEX/DEX Support: {sum(1 for s in self.sbirs_analyzer.signal_history if hasattr(s, 'gex_dex_support') and s.gex_dex_support)}\n"
                            f"Forecast Aligned: {sum(1 for s in self.sbirs_analyzer.signal_history if hasattr(s, 'forecast_alignment') and s.forecast_alignment)}",
                    "inline": True
                }
            ]
        }
        
        # Add performance analysis
        if hasattr(self, '_sbirs_calc_times') and self._sbirs_calc_times:
            avg_calc_time = np.mean(self._sbirs_calc_times[-100:])  # Last 100 calculations
            embed["fields"].append({
                "name": "⚡ Performance Metrics",
                "value": f"Avg Calculation Time: {avg_calc_time:.3f}s\n"
                        f"Active Signals: {len(self.active_sbirs_signals)}\n"
                        f"Signal Quality Score: {np.mean([s.confidence_score for s in self.sbirs_analyzer.signal_history[-10:]]) if len(self.sbirs_analyzer.signal_history) >= 10 else 0:.1f}",
                "inline": False
            })
        
        payload = {
            "username": "🎯 SBIRS Daily Report",
            "embeds": [embed]
        }
        
        await self._send_discord_alert(payload)
        
        logging.info("🎯 SBIRS DAILY REPORT GENERATED")
        logging.info(f"📊 Total Signals: {total_signals} | Success Rate: {overall_success:.1%}")
    
    # ============================================================================
    # ENHANCED DATA GATHERING
    # ============================================================================
    
    async def _gather_ultimate_market_data_for_sbirs(self) -> Dict[str, pd.DataFrame]:
        """Gather comprehensive market data for SBIRS analysis"""
        market_data = {}
        timeframes = ['1min', '5min', '15min', '30min', '1h']
        
        try:
            for tf in timeframes:
                # Get more data for pattern recognition
                periods = {'1min': 60, '5min': 100, '15min': 100, '30min': 100, '1h': 100}
                
                df = await self.data_manager.get_timeframe_data("SPX", tf, periods.get(tf, 100))
                if df is not None and len(df) >= 20:
                    market_data[tf] = df
            
            # Add current price to market data
            spx_data = await self.data_manager.get_current_spx_data()
            if spx_data:
                market_data['current_price'] = spx_data['price']
                market_data['current_volume'] = spx_data.get('volume', 0)
            
            return market_data
            
        except Exception as e:
            logging.error(f"Error gathering SBIRS market data: {e}")
            return {}

# Example usage with enhanced configuration
if __name__ == "__main__":
    async def main():
        # Enhanced configuration
        config = EnhancedConfig()
        config.DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/YOUR_WEBHOOK_HERE"
        
        # Initialize SBIRS integrated system
        sbirs_system = SBIRSIntegratedUltimateTradingSystem(config)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('sbirs_ultimate_trading_system.log'),
                logging.StreamHandler()
            ]
        )
        
        logging.info("🎯 SBIRS INTEGRATED ULTIMATE TRADING SYSTEM")
        logging.info("🔥 COMPLETE SYSTEM INTEGRATION:")
        logging.info("   • EMA Probability Analysis")
        logging.info("   • Demand Zone Detection")
        logging.info("   • SP500 Weighted Correlation")
        logging.info("   • Dynamic Strike Forecasting")
        logging.info("   • GEX/DEX Analysis & Optimal Entries")
        logging.info("   • SBIRS Breakout/Reversal Detection")
        logging.info("   • Chop Zone Filtering")
        logging.info("   • Dynamic Exit Management")
        logging.info("   • Multi-Timeframe Backtesting")
        logging.info("   • Advanced Risk Management")
        logging.info("   • Real-Time Performance Optimization")
        
        try:
            await sbirs_system.start_monitoring()
        except KeyboardInterrupt:
            logging.info("🛑 SBIRS system stopped by user")
        except Exception as e:
            logging.error(f"💥 SBIRS system crashed: {e}")
        finally:
            await sbirs_system._generate_sbirs_daily_report()
    
    asyncio.run(main())
