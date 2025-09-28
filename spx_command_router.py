#!/usr/bin/env python3
"""
SPX Command Router - Seamless Command Integration Layer
Maps user commands to appropriate analysis engines for true seamless operation

This is the CRITICAL missing piece that makes commands actually work.
"""

import os
import sys
import subprocess
import json
from datetime import datetime
from typing import Dict, List, Optional, Any

class SPXCommandRouter:
    """Central command router for seamless SPX trading system operation"""

    def __init__(self):
        self.command_map = {
            # Core Trading Commands
            'spx now': 'spx_auto.py',
            'spx analysis': 'spx_auto.py',
            'spx quick': 'spx_auto.py',
            'spx full market report': 'spx_auto.py',
            'spx sbirs': 'spx_auto.py',
            'spx scalp plan': 'spx_auto.py',

            # Dealer Positioning Commands
            'spx dealer positioning': 'dealer_positioning_engine.py',
            'spx king nodes': 'dealer_positioning_engine.py',
            'spx put call walls': 'dealer_positioning_engine.py',
            'spx multi strike analysis': 'dealer_positioning_integration.py',
            'spx enhanced consensus': 'dealer_positioning_integration.py',
            'spx integrated analysis': 'dealer_positioning_integration.py',
            'spx touch probability': 'dealer_positioning_engine.py',
            'spx node confluence': 'dealer_positioning_integration.py',
            'spx map reshuffle check': 'dealer_positioning_engine.py',
            'spx dealer signals': 'dealer_positioning_engine.py',

            # Specialized Analysis
            'spx gex dex': 'gex_analyzer.py',
            'spx consensus score': 'consensus_optimization.py',
            'spx chop zone': 'spx_auto.py',
            'spx kelly sizing': 'risk_management_enhancement.py',
            'spx demand zones': 'spx_auto.py',
            'spx strike forecast': 'spx_strike_analysis.py',
            'spx mag 7 analysis': 'spx_auto.py',

            # Pattern Commands
            'spx pattern scan': 'ml_pattern_engine.py',
            'spx high win rate': 'ml_pattern_engine.py',
            'spx volume breakout': 'spx_auto.py',
            'spx resistance rejection': 'spx_auto.py',
            'spx opening range': 'spx_open_range.py',
            'spx time filter check': 'spx_auto.py',
            'spx eod acceleration': 'spx_auto.py',
            'spx pattern validation': 'ml_pattern_engine.py',

            # System Management
            'spx session start': 'system_validation.py',
            'spx session save': 'system_validation.py',
            'spx key levels save': 'spx_auto.py',
            'spx performance tracking': 'performance_analytics.py',
            'spx emergency protocol': 'system_validation.py',
            'portfolio heat check': 'risk_management_enhancement.py',
            'spx systems check': 'system_validation.py',

            # Testing & Validation
            'spx market open protocol': 'market_open_protocol.py',
            'spx api status': 'validate_api_key.py',
            'spx alert status': 'smart_alerts.py',

            # Advanced Analysis
            'spx momentum': 'spx_auto.py',
            'spx structure': 'spx_auto.py',
            'spx play by play': 'spx_auto.py',
            'last hour of trading': 'spx_auto.py',
            'spx market intel': 'spx_auto.py',
            'spx earnings check': 'spx_auto.py',
            'spx sentiment scan': 'news_sentiment_engine.py',
            'spx event risk': 'spx_auto.py',
            'spx mag7 intel': 'spx_auto.py',
            'spx insider flow': 'spx_auto.py',

            # Risk Management
            'kelly sizing': 'risk_management_enhancement.py',
            'portfolio heat': 'risk_management_enhancement.py',
            'emergency protocol': 'system_validation.py',
            'smart exits': 'trading_dashboard.py',
            'spx risk controls': 'risk_management_enhancement.py',
            'spx vix adaptive size': 'volatility_intelligence.py',

            # NDX Integration
            'ndx analysis': 'ndx_integration.py',
            'ndx options': 'ndx_integration.py',
            'ndx consensus': 'ndx_integration.py',
            'nasdaq 100 analysis': 'ndx_integration.py',
            'ndx now': 'ndx_integration.py',

            # Five-Asset Integration
            'five asset analysis': 'five_asset_integration.py',
            'complete multi asset': 'five_asset_integration.py',
            'spx qqq spy iwm ndx': 'five_asset_integration.py',
            'full portfolio analysis': 'five_asset_integration.py',

            # Technical Analysis
            'chop zone': 'spx_auto.py',
            'gex analysis': 'gex_analyzer.py',
            'forecasts': 'spx_strike_analysis.py',
            'sbirs signals': 'sbirs_integrated_system.py',
            'consensus score': 'consensus_optimization.py',
            'spx false signal filter': 'ml_pattern_engine.py',
            'spx cost analysis full': 'spx_auto.py',
            'spx regime detect': 'volatility_intelligence.py',
            'spx pattern recognition': 'ml_pattern_engine.py',
            'spx institutional': 'spx_auto.py',
            'spx confidence score': 'consensus_optimization.py'
        }

        self.discord_commands = [
            'spx now discord',
            'spx analysis discord',
            'spx dealer positioning discord',
            'spx enhanced consensus discord',
            'spx full market report discord',
            'spx sbirs discord',
            'send to discord',
            'discord it'
        ]

        self.session_file = '.spx/command_history.json'
        self.ensure_session_dir()

    def ensure_session_dir(self):
        """Ensure .spx directory exists"""
        os.makedirs('.spx', exist_ok=True)

    def execute_command(self, command: str, args: List[str] = None) -> Dict[str, Any]:
        """Execute a user command by routing to appropriate script"""
        command = command.lower().strip()
        args = args or []

        # Log command
        self.log_command(command, args)

        # Handle Discord commands
        if any(discord_cmd in command for discord_cmd in self.discord_commands):
            return self.handle_discord_command(command, args)

        # Route to appropriate script
        if command in self.command_map:
            script = self.command_map[command]
            return self.run_script(script, args)
        else:
            return self.handle_unknown_command(command)

    def run_script(self, script: str, args: List[str] = None) -> Dict[str, Any]:
        """Run a Python script with arguments"""
        args = args or []

        if not os.path.exists(script):
            return {
                'success': False,
                'error': f'Script not found: {script}',
                'command': script,
                'timestamp': datetime.now().isoformat()
            }

        try:
            # Run the script
            cmd = ['python', script] + args
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                cwd='.'
            )

            return {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode,
                'command': ' '.join(cmd),
                'timestamp': datetime.now().isoformat()
            }

        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Command timed out after 5 minutes',
                'command': script,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'command': script,
                'timestamp': datetime.now().isoformat()
            }

    def handle_discord_command(self, command: str, args: List[str]) -> Dict[str, Any]:
        """Handle Discord integration commands"""
        # Extract base command
        base_command = command.replace(' discord', '').strip()

        if base_command in self.command_map:
            # Run the base analysis first
            analysis_result = self.run_script(self.command_map[base_command], args)

            if analysis_result['success']:
                # Send to Discord
                discord_result = self.send_to_discord(analysis_result['stdout'], base_command)

                return {
                    'success': True,
                    'analysis_output': analysis_result['stdout'],
                    'discord_sent': discord_result['success'],
                    'discord_response': discord_result.get('response', ''),
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return analysis_result
        else:
            return {
                'success': False,
                'error': f'Unknown base command: {base_command}',
                'timestamp': datetime.now().isoformat()
            }

    def send_to_discord(self, content: str, title: str = 'SPX Analysis') -> Dict[str, Any]:
        """Send content to Discord via send_discord.py"""
        try:
            result = subprocess.run(
                ['python', 'send_discord.py', title, content],
                capture_output=True,
                text=True,
                timeout=30
            )

            return {
                'success': result.returncode == 0,
                'response': result.stdout,
                'error': result.stderr if result.returncode != 0 else None
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def handle_unknown_command(self, command: str) -> Dict[str, Any]:
        """Handle unknown commands with suggestions"""
        # Find similar commands
        suggestions = []
        for known_command in self.command_map.keys():
            if any(word in known_command for word in command.split()):
                suggestions.append(known_command)

        return {
            'success': False,
            'error': f'Unknown command: {command}',
            'suggestions': suggestions[:5],  # Top 5 suggestions
            'timestamp': datetime.now().isoformat()
        }

    def log_command(self, command: str, args: List[str]):
        """Log command execution for debugging"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'command': command,
            'args': args
        }

        try:
            # Load existing history
            if os.path.exists(self.session_file):
                with open(self.session_file, 'r') as f:
                    history = json.load(f)
            else:
                history = []

            # Add new entry
            history.append(log_entry)

            # Keep only last 100 commands
            history = history[-100:]

            # Save history
            with open(self.session_file, 'w') as f:
                json.dump(history, f, indent=2)

        except Exception:
            pass  # Don't fail command execution due to logging issues

    def list_commands(self) -> List[str]:
        """List all available commands"""
        return sorted(list(self.command_map.keys()) + self.discord_commands)

    def get_command_info(self, command: str) -> Dict[str, Any]:
        """Get information about a specific command"""
        command = command.lower().strip()

        if command in self.command_map:
            return {
                'command': command,
                'script': self.command_map[command],
                'available': os.path.exists(self.command_map[command]),
                'type': 'analysis'
            }
        elif command in self.discord_commands:
            return {
                'command': command,
                'type': 'discord',
                'available': True
            }
        else:
            return {
                'command': command,
                'available': False,
                'error': 'Unknown command'
            }

def main():
    """Command line interface for the router"""
    if len(sys.argv) < 2:
        print("SPX Command Router")
        print("Usage: python spx_command_router.py <command> [args...]")
        print("")
        print("Examples:")
        print("  python spx_command_router.py 'spx now'")
        print("  python spx_command_router.py 'spx dealer positioning'")
        print("  python spx_command_router.py 'spx analysis discord'")
        print("")

        router = SPXCommandRouter()
        commands = router.list_commands()
        print(f"Available commands ({len(commands)}):")
        for cmd in commands[:20]:  # Show first 20
            print(f"  {cmd}")
        if len(commands) > 20:
            print(f"  ... and {len(commands) - 20} more")
        return

    # Get command and arguments
    command = sys.argv[1]
    args = sys.argv[2:] if len(sys.argv) > 2 else []

    # Execute command
    router = SPXCommandRouter()
    result = router.execute_command(command, args)

    # Output result
    if result['success']:
        print(result.get('stdout', ''))
        if result.get('discord_sent'):
            print("\nSent to Discord successfully!")
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")
        if 'suggestions' in result:
            print("\nDid you mean:")
            for suggestion in result['suggestions']:
                print(f"  {suggestion}")

if __name__ == "__main__":
    main()