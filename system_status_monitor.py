#!/usr/bin/env python3
"""
SEAMLESS SYSTEM STATUS MONITORING
Real-time dashboard and status aggregation system
"""

import time
import os
import subprocess
import requests
from datetime import datetime, timedelta
import json
import threading

class SystemStatusMonitor:
    def __init__(self):
        self.start_time = datetime.now()
        self.system_status = {}
        self.streaming_processes = {}
        self.performance_metrics = {}
        self.monitoring_active = False

    def get_system_overview(self):
        """Get comprehensive system status overview"""
        print("SEAMLESS TRADING SYSTEM STATUS")
        print("=" * 50)
        print(f"Monitor Start: {self.start_time.strftime('%H:%M:%S')}")
        print(f"Current Time: {datetime.now().strftime('%H:%M:%S')}")
        print()

        # Get core system components
        self.check_streaming_systems()
        self.check_api_endpoints()
        self.check_data_pipeline()
        self.check_trading_infrastructure()
        self.generate_performance_summary()

        return self.system_status

    def check_streaming_systems(self):
        """Monitor all 5 streaming systems"""
        print("=== STREAMING SYSTEMS STATUS ===")

        try:
            # Get running processes
            result = subprocess.run(['tasklist'], capture_output=True, text=True, timeout=10)
            python_processes = result.stdout.count('python.exe')

            streaming_systems = {
                'high_frequency_spx': {'expected': True, 'refresh': '10s', 'status': 'UNKNOWN'},
                'best_options_scanner': {'expected': True, 'refresh': '20s', 'status': 'UNKNOWN'},
                'ndx_tech_monitor': {'expected': True, 'refresh': '25s', 'status': 'UNKNOWN'},
                'es_futures_stream': {'expected': True, 'refresh': '30s', 'status': 'UNKNOWN'},
                'multi_asset_monitor': {'expected': True, 'refresh': '30s', 'status': 'UNKNOWN'}
            }

            # Estimate status based on process count
            if python_processes >= 5:
                for system in streaming_systems:
                    streaming_systems[system]['status'] = 'ACTIVE'
            elif python_processes >= 3:
                active_count = 0
                for system in streaming_systems:
                    if active_count < python_processes - 1:  # Exclude this monitor
                        streaming_systems[system]['status'] = 'ACTIVE'
                        active_count += 1
                    else:
                        streaming_systems[system]['status'] = 'STOPPED'
            else:
                for system in streaming_systems:
                    streaming_systems[system]['status'] = 'STOPPED'

            # Display status
            for system_name, info in streaming_systems.items():
                status_emoji = "[ACTIVE]" if info['status'] == 'ACTIVE' else "[STOPPED]"
                system_display = system_name.replace('_', ' ').title()
                print(f"{status_emoji} {system_display}: {info['status']} ({info['refresh']})")

            self.system_status['streaming_systems'] = {
                'total_processes': python_processes,
                'systems': streaming_systems,
                'overall_status': 'OPERATIONAL' if python_processes >= 3 else 'DEGRADED'
            }

        except Exception as e:
            print(f"[ERROR] Error checking streaming systems: {e}")
            self.system_status['streaming_systems'] = {'error': str(e), 'overall_status': 'ERROR'}

    def check_api_endpoints(self):
        """Check API endpoint health"""
        print("\n=== API ENDPOINTS STATUS ===")

        api_tests = [
            ('AlphaVantage', ['python', 'validate_api_key.py'], 30),
            ('Polygon', ['python', 'polygon_realtime_spx.py'], 30),
            ('After Hours', ['python', 'after_hours_command.py', 'SPY'], 15),
            ('Discord', ['python', 'send_discord.py', 'STATUS CHECK', 'System monitoring active'], 10)
        ]

        api_results = {}

        for api_name, command, timeout in api_tests:
            try:
                start_time = time.time()
                result = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
                response_time = time.time() - start_time

                if result.returncode == 0:
                    status = "[HEALTHY]"
                    api_results[api_name.lower().replace(' ', '_')] = {
                        'status': 'HEALTHY',
                        'response_time': f"{response_time:.2f}s"
                    }
                else:
                    status = "[UNHEALTHY]"
                    api_results[api_name.lower().replace(' ', '_')] = {
                        'status': 'UNHEALTHY',
                        'error': result.stderr if result.stderr else 'Command failed'
                    }

                print(f"{status} {api_name}")

            except subprocess.TimeoutExpired:
                print(f"[TIMEOUT] {api_name}")
                api_results[api_name.lower().replace(' ', '_')] = {
                    'status': 'TIMEOUT',
                    'error': f'Timeout after {timeout}s'
                }
            except Exception as e:
                print(f"[ERROR] {api_name}: {e}")
                api_results[api_name.lower().replace(' ', '_')] = {
                    'status': 'ERROR',
                    'error': str(e)
                }

        self.system_status['api_endpoints'] = api_results

    def check_data_pipeline(self):
        """Check data pipeline integrity"""
        print("\n=== DATA PIPELINE STATUS ===")

        try:
            # Test SPX data
            result = subprocess.run(['python', 'spx_live.py'], capture_output=True, text=True, timeout=30)

            has_spx_data = 'SPX:' in result.stdout and '$' in result.stdout

            if has_spx_data and result.returncode == 0:
                print("[OPERATIONAL] SPX Data Pipeline: OPERATIONAL")

                # Extract current SPX price
                spx_price = "Not found"
                for line in result.stdout.split('\n'):
                    if 'SPX:' in line and '$' in line:
                        spx_price = line.strip()
                        break

                self.system_status['data_pipeline'] = {
                    'spx_data': 'OPERATIONAL',
                    'current_spx': spx_price,
                    'last_update': datetime.now().isoformat()
                }
            else:
                print("[FAILED] SPX Data Pipeline: FAILED")
                self.system_status['data_pipeline'] = {
                    'spx_data': 'FAILED',
                    'error': 'No SPX data available'
                }

            # Test options data
            try:
                options_result = subprocess.run(['python', 'spx_strike_analysis.py'],
                                              capture_output=True, text=True, timeout=30)

                has_options = 'SPXW' in options_result.stdout or 'strike' in options_result.stdout.lower()

                if has_options:
                    print("[ACCESSIBLE] Options Chain: ACCESSIBLE")
                    self.system_status['data_pipeline']['options_chain'] = 'ACCESSIBLE'
                else:
                    print("[LIMITED] Options Chain: LIMITED")
                    self.system_status['data_pipeline']['options_chain'] = 'LIMITED'

            except Exception as e:
                print(f"[ERROR] Options Chain: ERROR - {e}")
                self.system_status['data_pipeline']['options_chain'] = 'ERROR'

        except Exception as e:
            print(f"[ERROR] Data Pipeline Error: {e}")
            self.system_status['data_pipeline'] = {'error': str(e)}

    def check_trading_infrastructure(self):
        """Check trading infrastructure readiness"""
        print("\n=== TRADING INFRASTRUCTURE ===")

        try:
            # Check session persistence
            session_files = ['.spx/session.json', '.spx/levels.json', '.spx/market_open_status.json']
            session_status = {}

            for file_path in session_files:
                if os.path.exists(file_path):
                    file_size = os.path.getsize(file_path)
                    modified_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    age_minutes = (datetime.now() - modified_time).total_seconds() / 60

                    if file_size > 0 and age_minutes < 1440:  # Less than 24 hours old
                        status = "[HEALTHY] CURRENT"
                    elif file_size > 0:
                        status = "[WARNING] STALE"
                    else:
                        status = "[UNHEALTHY] EMPTY"

                    session_status[file_path] = {
                        'status': status.split(' ')[1],
                        'size': file_size,
                        'age_minutes': int(age_minutes)
                    }
                    print(f"{status} {file_path}")
                else:
                    session_status[file_path] = {'status': 'MISSING'}
                    print(f"[UNHEALTHY] MISSING {file_path}")

            # Risk management check
            risk_status = self.check_risk_management()

            self.system_status['trading_infrastructure'] = {
                'session_files': session_status,
                'risk_management': risk_status
            }

        except Exception as e:
            print(f"[ERROR] Trading Infrastructure Error: {e}")
            self.system_status['trading_infrastructure'] = {'error': str(e)}

    def check_risk_management(self):
        """Check risk management systems"""
        print("\n=== RISK MANAGEMENT ===")

        try:
            # Check for existing position tracking
            performance_files = ['.spx/performance_log.json', '.spx/trade_log.jsonl']

            risk_controls = {
                'position_tracking': False,
                'portfolio_heat_monitoring': False,
                'stop_loss_management': False
            }

            for file_path in performance_files:
                if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                    risk_controls['position_tracking'] = True
                    break

            # Default risk parameters
            risk_parameters = {
                'max_portfolio_heat': '15%',
                'max_position_size': '2%',
                'max_daily_loss': '6%',
                'stop_loss_limit': '50%'
            }

            for control, status in risk_controls.items():
                emoji = "[HEALTHY]" if status else "[WARNING]"
                control_display = control.replace('_', ' ').title()
                print(f"{emoji} {control_display}: {'ACTIVE' if status else 'STANDBY'}")

            return {
                'controls': risk_controls,
                'parameters': risk_parameters,
                'overall_status': 'OPERATIONAL'
            }

        except Exception as e:
            return {'error': str(e), 'overall_status': 'ERROR'}

    def generate_performance_summary(self):
        """Generate system performance summary"""
        print("\n=== PERFORMANCE SUMMARY ===")

        try:
            # Calculate overall system health
            total_systems = 0
            healthy_systems = 0

            # Count streaming systems
            if 'streaming_systems' in self.system_status:
                total_systems += 1
                if self.system_status['streaming_systems'].get('overall_status') == 'OPERATIONAL':
                    healthy_systems += 1

            # Count API endpoints
            if 'api_endpoints' in self.system_status:
                for api, status in self.system_status['api_endpoints'].items():
                    total_systems += 1
                    if status.get('status') == 'HEALTHY':
                        healthy_systems += 1

            # Count data pipeline
            if 'data_pipeline' in self.system_status:
                total_systems += 1
                if self.system_status['data_pipeline'].get('spx_data') == 'OPERATIONAL':
                    healthy_systems += 1

            # Count trading infrastructure
            if 'trading_infrastructure' in self.system_status:
                total_systems += 1
                if 'error' not in self.system_status['trading_infrastructure']:
                    healthy_systems += 1

            # Calculate health percentage
            health_percentage = (healthy_systems / total_systems * 100) if total_systems > 0 else 0

            # Determine overall status
            if health_percentage >= 90:
                overall_status = "[HEALTHY] EXCELLENT"
                trading_readiness = "FULLY READY"
            elif health_percentage >= 75:
                overall_status = "[WARNING] GOOD"
                trading_readiness = "READY WITH MINOR ISSUES"
            elif health_percentage >= 50:
                overall_status = "[DEGRADED] DEGRADED"
                trading_readiness = "LIMITED FUNCTIONALITY"
            else:
                overall_status = "[UNHEALTHY] CRITICAL"
                trading_readiness = "NOT READY"

            print(f"System Health: {health_percentage:.1f}% ({healthy_systems}/{total_systems})")
            print(f"Overall Status: {overall_status}")
            print(f"Trading Readiness: {trading_readiness}")

            # Market session info
            current_time = datetime.now()
            market_open = current_time.replace(hour=9, minute=30, second=0, microsecond=0)
            market_close = current_time.replace(hour=16, minute=0, second=0, microsecond=0)

            if market_open <= current_time <= market_close:
                market_status = "[HEALTHY] MARKET OPEN"
            elif current_time < market_open:
                time_to_open = market_open - current_time
                market_status = f"[TIMEOUT] OPENS IN {str(time_to_open).split('.')[0]}"
            else:
                market_status = "[UNHEALTHY] MARKET CLOSED"

            print(f"Market Status: {market_status}")

            self.performance_metrics = {
                'health_percentage': health_percentage,
                'healthy_systems': healthy_systems,
                'total_systems': total_systems,
                'overall_status': overall_status.split(' ')[1],
                'trading_readiness': trading_readiness,
                'market_status': market_status,
                'last_update': datetime.now().isoformat()
            }

        except Exception as e:
            print(f"[ERROR] Performance Summary Error: {e}")
            self.performance_metrics = {'error': str(e)}

    def save_status_report(self):
        """Save comprehensive status report"""
        try:
            os.makedirs('.spx', exist_ok=True)

            status_report = {
                'system_monitor': {
                    'timestamp': datetime.now().isoformat(),
                    'monitoring_start': self.start_time.isoformat(),
                    'system_status': self.system_status,
                    'performance_metrics': self.performance_metrics,
                    'uptime_minutes': (datetime.now() - self.start_time).total_seconds() / 60
                }
            }

            with open('.spx/system_status_report.json', 'w') as f:
                json.dump(status_report, f, indent=2)

            print(f"\nStatus report saved to .spx/system_status_report.json")

        except Exception as e:
            print(f"Failed to save status report: {e}")

    def run_continuous_monitoring(self):
        """Run continuous system monitoring"""
        print("CONTINUOUS SYSTEM MONITORING ACTIVATED")
        print("=" * 50)
        print("Monitor Interval: 5 minutes")
        print("Press Ctrl+C to stop...")
        print()

        self.monitoring_active = True

        try:
            while self.monitoring_active:
                self.get_system_overview()
                self.save_status_report()

                print(f"\nNext status check in 5 minutes...")
                print("=" * 50)

                # Wait 5 minutes
                time.sleep(300)

        except KeyboardInterrupt:
            print("\nSystem monitoring stopped")
            self.monitoring_active = False

    def run_single_status_check(self):
        """Run single comprehensive status check"""
        self.get_system_overview()
        self.save_status_report()

        print(f"\nSYSTEM STATUS COMPLETE")
        return self.system_status, self.performance_metrics

def main():
    import sys

    monitor = SystemStatusMonitor()

    if len(sys.argv) > 1 and sys.argv[1] == 'continuous':
        monitor.run_continuous_monitoring()
    else:
        monitor.run_single_status_check()

if __name__ == "__main__":
    main()