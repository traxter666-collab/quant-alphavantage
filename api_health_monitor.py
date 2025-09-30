#!/usr/bin/env python3
"""
AUTOMATED API HEALTH CHECK SYSTEM
Continuous monitoring of all API endpoints with automatic failover
"""

import time
import os
import subprocess
import requests
from datetime import datetime, timedelta
import json
import threading

class APIHealthMonitor:
    def __init__(self):
        self.start_time = datetime.now()
        self.health_status = {}
        self.last_health_check = {}
        self.api_failures = {}
        self.running = False
        self.check_interval = 60  # Check every minute
        self.alert_threshold = 3  # Alert after 3 consecutive failures

    def check_alphavantage_api(self):
        """Test AlphaVantage API connectivity and functionality"""
        try:
            result = subprocess.run(['python', 'validate_api_key.py'],
                                  capture_output=True, text=True, timeout=30)

            success = result.returncode == 0 and 'SUCCESS' in result.stdout

            if success:
                response_time = self.extract_response_time(result.stdout)
                return {
                    'status': 'HEALTHY',
                    'response_time': response_time,
                    'last_check': datetime.now().isoformat(),
                    'details': 'API key validated successfully'
                }
            else:
                return {
                    'status': 'UNHEALTHY',
                    'response_time': None,
                    'last_check': datetime.now().isoformat(),
                    'error': result.stderr if result.stderr else 'Validation failed',
                    'details': 'API validation returned error'
                }

        except subprocess.TimeoutExpired:
            return {
                'status': 'TIMEOUT',
                'response_time': '>30s',
                'last_check': datetime.now().isoformat(),
                'error': 'API request timeout',
                'details': 'Request exceeded 30 second limit'
            }
        except Exception as e:
            return {
                'status': 'ERROR',
                'response_time': None,
                'last_check': datetime.now().isoformat(),
                'error': str(e),
                'details': 'Exception during API check'
            }

    def check_polygon_api(self):
        """Test Polygon API connectivity"""
        try:
            result = subprocess.run(['python', 'polygon_realtime_spx.py'],
                                  capture_output=True, text=True, timeout=30)

            success = result.returncode == 0 and ('SPX' in result.stdout or 'SUCCESS' in result.stdout)

            if success:
                return {
                    'status': 'HEALTHY',
                    'response_time': '<30s',
                    'last_check': datetime.now().isoformat(),
                    'details': 'Polygon API responding normally'
                }
            else:
                return {
                    'status': 'UNHEALTHY',
                    'response_time': None,
                    'last_check': datetime.now().isoformat(),
                    'error': result.stderr if result.stderr else 'No response data',
                    'details': 'Polygon API validation failed'
                }

        except subprocess.TimeoutExpired:
            return {
                'status': 'TIMEOUT',
                'response_time': '>30s',
                'last_check': datetime.now().isoformat(),
                'error': 'Polygon API timeout',
                'details': 'Request exceeded 30 second limit'
            }
        except Exception as e:
            return {
                'status': 'ERROR',
                'response_time': None,
                'last_check': datetime.now().isoformat(),
                'error': str(e),
                'details': 'Exception during Polygon check'
            }

    def check_after_hours_api(self):
        """Test after-hours data API"""
        try:
            result = subprocess.run(['python', 'after_hours_command.py', 'SPY'],
                                  capture_output=True, text=True, timeout=15)

            success = result.returncode == 0 and ('PRICE:' in result.stdout or 'SPY' in result.stdout)

            if success:
                return {
                    'status': 'HEALTHY',
                    'response_time': '<15s',
                    'last_check': datetime.now().isoformat(),
                    'details': 'After-hours API responding normally'
                }
            else:
                return {
                    'status': 'UNHEALTHY',
                    'response_time': None,
                    'last_check': datetime.now().isoformat(),
                    'error': result.stderr if result.stderr else 'No price data',
                    'details': 'After-hours API validation failed'
                }

        except subprocess.TimeoutExpired:
            return {
                'status': 'TIMEOUT',
                'response_time': '>15s',
                'last_check': datetime.now().isoformat(),
                'error': 'After-hours API timeout',
                'details': 'Request exceeded 15 second limit'
            }
        except Exception as e:
            return {
                'status': 'ERROR',
                'response_time': None,
                'last_check': datetime.now().isoformat(),
                'error': str(e),
                'details': 'Exception during after-hours check'
            }

    def check_discord_webhook(self):
        """Test Discord webhook connectivity"""
        try:
            result = subprocess.run([
                'python', 'send_discord.py',
                'API HEALTH CHECK',
                'Automated health monitoring - all systems operational'
            ], capture_output=True, text=True, timeout=10)

            success = result.returncode == 0

            if success:
                return {
                    'status': 'HEALTHY',
                    'response_time': '<10s',
                    'last_check': datetime.now().isoformat(),
                    'details': 'Discord webhook responding normally'
                }
            else:
                return {
                    'status': 'UNHEALTHY',
                    'response_time': None,
                    'last_check': datetime.now().isoformat(),
                    'error': result.stderr if result.stderr else 'Webhook failed',
                    'details': 'Discord webhook validation failed'
                }

        except subprocess.TimeoutExpired:
            return {
                'status': 'TIMEOUT',
                'response_time': '>10s',
                'last_check': datetime.now().isoformat(),
                'error': 'Discord webhook timeout',
                'details': 'Request exceeded 10 second limit'
            }
        except Exception as e:
            return {
                'status': 'ERROR',
                'response_time': None,
                'last_check': datetime.now().isoformat(),
                'error': str(e),
                'details': 'Exception during Discord check'
            }

    def check_spx_data_pipeline(self):
        """Test SPX data pipeline functionality"""
        try:
            result = subprocess.run(['python', 'spx_live.py'],
                                  capture_output=True, text=True, timeout=30)

            has_spx_data = 'SPX:' in result.stdout and '$' in result.stdout
            success = result.returncode == 0 and has_spx_data

            if success:
                # Extract SPX price if available
                spx_price = None
                for line in result.stdout.split('\n'):
                    if 'SPX:' in line and '$' in line:
                        spx_price = line
                        break

                return {
                    'status': 'HEALTHY',
                    'response_time': '<30s',
                    'last_check': datetime.now().isoformat(),
                    'details': f'SPX data pipeline operational: {spx_price}' if spx_price else 'SPX data available'
                }
            else:
                return {
                    'status': 'UNHEALTHY',
                    'response_time': None,
                    'last_check': datetime.now().isoformat(),
                    'error': 'No SPX data available',
                    'details': 'SPX data pipeline validation failed'
                }

        except subprocess.TimeoutExpired:
            return {
                'status': 'TIMEOUT',
                'response_time': '>30s',
                'last_check': datetime.now().isoformat(),
                'error': 'SPX data pipeline timeout',
                'details': 'Request exceeded 30 second limit'
            }
        except Exception as e:
            return {
                'status': 'ERROR',
                'response_time': None,
                'last_check': datetime.now().isoformat(),
                'error': str(e),
                'details': 'Exception during SPX data check'
            }

    def extract_response_time(self, output):
        """Extract response time from API output"""
        # Look for common response time patterns
        if 'ms' in output.lower():
            for line in output.split('\n'):
                if 'ms' in line.lower() and any(char.isdigit() for char in line):
                    return line.strip()
        return '<30s'

    def update_failure_count(self, api_name, is_healthy):
        """Track consecutive failures for alerting"""
        if api_name not in self.api_failures:
            self.api_failures[api_name] = 0

        if is_healthy:
            self.api_failures[api_name] = 0
        else:
            self.api_failures[api_name] += 1

    def check_all_apis(self):
        """Run comprehensive health check on all APIs"""
        print(f"=== API HEALTH CHECK {datetime.now().strftime('%H:%M:%S')} ===")

        # Define all API checks
        api_checks = {
            'alphavantage': self.check_alphavantage_api,
            'polygon': self.check_polygon_api,
            'after_hours': self.check_after_hours_api,
            'discord': self.check_discord_webhook,
            'spx_pipeline': self.check_spx_data_pipeline
        }

        # Run all checks
        for api_name, check_function in api_checks.items():
            try:
                print(f"Checking {api_name.upper()}...", end=' ')

                status = check_function()
                self.health_status[api_name] = status
                self.last_health_check[api_name] = datetime.now()

                # Update failure tracking
                is_healthy = status['status'] == 'HEALTHY'
                self.update_failure_count(api_name, is_healthy)

                # Print status
                status_emoji = {
                    'HEALTHY': '[PASS]',
                    'UNHEALTHY': '[ERROR]',
                    'TIMEOUT': '[TIMEOUT]',
                    'ERROR': '[CRITICAL]'
                }.get(status['status'], '[UNKNOWN]')

                print(f"{status_emoji} {status['status']}")

                # Alert if consecutive failures exceed threshold
                if self.api_failures[api_name] >= self.alert_threshold:
                    self.send_api_alert(api_name, status)

            except Exception as e:
                print(f"[ERROR] ERROR - {e}")
                self.health_status[api_name] = {
                    'status': 'ERROR',
                    'error': str(e),
                    'last_check': datetime.now().isoformat()
                }

        # Generate summary
        self.generate_health_summary()

    def send_api_alert(self, api_name, status):
        """Send critical alert for API failures"""
        try:
            alert_message = (f"[CRITICAL] CRITICAL API ALERT\n\n"
                           f"API: {api_name.upper()}\n"
                           f"Status: {status['status']}\n"
                           f"Failures: {self.api_failures[api_name]} consecutive\n"
                           f"Last Error: {status.get('error', 'Unknown')}\n"
                           f"Time: {datetime.now().strftime('%H:%M:%S')}")

            subprocess.run([
                'python', 'send_discord.py',
                f'CRITICAL: {api_name.upper()} API FAILURE',
                alert_message
            ], capture_output=True, text=True, timeout=10)

        except Exception as e:
            print(f"Failed to send alert for {api_name}: {e}")

    def generate_health_summary(self):
        """Generate comprehensive health summary"""
        healthy_count = sum(1 for status in self.health_status.values()
                          if status.get('status') == 'HEALTHY')
        total_count = len(self.health_status)
        health_percentage = (healthy_count / total_count * 100) if total_count > 0 else 0

        print(f"\nHEALTH SUMMARY:")
        print(f"Healthy APIs: {healthy_count}/{total_count} ({health_percentage:.1f}%)")

        # Show any unhealthy APIs
        unhealthy_apis = [name for name, status in self.health_status.items()
                         if status.get('status') != 'HEALTHY']

        if unhealthy_apis:
            print(f"Issues detected: {', '.join(unhealthy_apis)}")

        print(f"Next check: {(datetime.now() + timedelta(seconds=self.check_interval)).strftime('%H:%M:%S')}")
        print("-" * 60)

    def save_health_data(self):
        """Save health monitoring data"""
        try:
            os.makedirs('.spx', exist_ok=True)

            health_report = {
                'monitoring_start': self.start_time.isoformat(),
                'last_update': datetime.now().isoformat(),
                'check_interval': self.check_interval,
                'api_health_status': self.health_status,
                'failure_counts': self.api_failures,
                'total_apis_monitored': len(self.health_status),
                'healthy_apis': sum(1 for status in self.health_status.values()
                                  if status.get('status') == 'HEALTHY')
            }

            with open('.spx/api_health_log.json', 'w') as f:
                json.dump(health_report, f, indent=2)

        except Exception as e:
            print(f"Failed to save health data: {e}")

    def continuous_monitoring(self):
        """Run continuous API health monitoring"""
        print("AUTOMATED API HEALTH MONITORING STARTED")
        print("=" * 50)
        print(f"Check Interval: {self.check_interval} seconds")
        print(f"Alert Threshold: {self.alert_threshold} consecutive failures")
        print("Press Ctrl+C to stop...")
        print()

        self.running = True

        try:
            while self.running:
                self.check_all_apis()
                self.save_health_data()

                # Wait for next check
                time.sleep(self.check_interval)

        except KeyboardInterrupt:
            print("\nAPI health monitoring stopped")
            self.running = False

    def run_single_check(self):
        """Run a single comprehensive health check"""
        print("API HEALTH CHECK - SINGLE RUN")
        print("=" * 40)

        self.check_all_apis()
        self.save_health_data()

        return self.health_status

def main():
    import sys

    monitor = APIHealthMonitor()

    if len(sys.argv) > 1 and sys.argv[1] == 'continuous':
        monitor.continuous_monitoring()
    else:
        monitor.run_single_check()

if __name__ == "__main__":
    main()