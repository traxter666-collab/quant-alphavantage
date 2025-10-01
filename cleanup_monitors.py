#!/usr/bin/env python3
"""
MONITOR CLEANUP UTILITY
Clean up duplicate/stuck background processes

Usage: python cleanup_monitors.py [--kill-all] [--list]
"""
import sys
import subprocess
import re

def list_python_processes():
    """List all Python processes"""
    try:
        if sys.platform == 'win32':
            result = subprocess.run(
                ['tasklist', '/FI', 'IMAGENAME eq python.exe', '/FO', 'CSV'],
                capture_output=True,
                text=True
            )
        else:
            result = subprocess.run(
                ['ps', 'aux'],
                capture_output=True,
                text=True
            )

        return result.stdout
    except Exception as e:
        print(f"Error listing processes: {e}")
        return ""

def find_monitor_processes():
    """Find monitoring processes"""
    output = list_python_processes()
    monitors = []

    patterns = [
        'seamless_market_system',
        'spx_trade_setup',
        'spx_auto_trade_monitor',
        'multi_asset_trade_monitor',
        'flow_live_monitor',
        'flow_master_system'
    ]

    for line in output.split('\n'):
        for pattern in patterns:
            if pattern in line:
                monitors.append(line)
                break

    return monitors

def kill_process(pid):
    """Kill process by PID"""
    try:
        if sys.platform == 'win32':
            subprocess.run(['taskkill', '/PID', str(pid), '/F'], check=True)
        else:
            subprocess.run(['kill', '-9', str(pid)], check=True)
        return True
    except:
        return False

def main():
    if '--list' in sys.argv:
        print("\n📊 ACTIVE PYTHON MONITORS:\n")
        monitors = find_monitor_processes()

        if monitors:
            for i, mon in enumerate(monitors, 1):
                print(f"{i}. {mon}")
            print(f"\nTotal: {len(monitors)} monitor processes")
        else:
            print("No monitor processes found")

    elif '--kill-all' in sys.argv:
        print("\n🛑 KILLING ALL MONITOR PROCESSES...\n")
        monitors = find_monitor_processes()

        if not monitors:
            print("No monitor processes found")
            return

        # Extract PIDs and kill
        killed = 0
        for mon in monitors:
            # Extract PID (platform-specific)
            if sys.platform == 'win32':
                # CSV format on Windows
                parts = mon.split(',')
                if len(parts) >= 2:
                    pid = parts[1].strip('"')
                    if kill_process(pid):
                        print(f"✅ Killed PID {pid}")
                        killed += 1
            else:
                # Linux/Mac ps aux format
                match = re.search(r'\s+(\d+)\s+', mon)
                if match:
                    pid = match.group(1)
                    if kill_process(pid):
                        print(f"✅ Killed PID {pid}")
                        killed += 1

        print(f"\n✅ Killed {killed} monitor processes")

    else:
        print("MONITOR CLEANUP UTILITY")
        print("="*60)
        print("\nUsage:")
        print("  python cleanup_monitors.py --list      # List all monitors")
        print("  python cleanup_monitors.py --kill-all  # Kill all monitors")
        print("\nCurrent monitors:")
        print("  • seamless_market_system.py")
        print("  • spx_trade_setup.py")
        print("  • spx_auto_trade_monitor.py")
        print("  • multi_asset_trade_monitor.py")
        print("  • flow_live_monitor.py")
        print("  • flow_master_system.py (watch mode)")

if __name__ == "__main__":
    main()
