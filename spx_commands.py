#!/usr/bin/env python3
"""
SPX Command Integration
Seamless command interface for all SPX analysis tools
"""

import sys
import os
import json
from datetime import datetime
from spx_gex_integration import SPXGEXIntegration

def handle_command(command: str):
    """
    Handle SPX command routing
    """
    integration = SPXGEXIntegration()
    
    if command in ['gex analysis', 'spx gex precision', 'spx gamma levels']:
        print("PRECISION GEX ANALYSIS")
        print("=" * 30)
        analysis = integration.generate_enhanced_analysis(include_gex=True)
        print(analysis)
        
    elif command in ['spx analysis gex', 'spx precision trades']:
        print("SPX ANALYSIS WITH GEX INTEGRATION")
        print("=" * 40)
        analysis = integration.generate_enhanced_analysis(include_gex=True)
        print(analysis)
        
        # Add any additional SPX analysis here
        print("\nCOMBINED ANALYSIS COMPLETE")
        print("All data saved to .spx/ directory")
        
    elif command in ['doctor', 'spx doctor', 'system check', 'health check']:
        print("SPX TRADING SYSTEM DOCTOR")
        print("=" * 50)
        run_system_diagnosis()
        
    else:
        print(f"Unknown command: {command}")
        print("Available commands:")
        print("- gex analysis")
        print("- spx gex precision") 
        print("- spx gamma levels")
        print("- spx analysis gex")
        print("- spx precision trades")
        print("- doctor")
        print("- system check")

def run_system_diagnosis():
    """
    Run comprehensive system health check without external scripts
    """
    print("\nAPI HEALTH CHECK")
    print("-" * 30)
    
    # Check session file
    session_file = ".spx/session.json"
    if os.path.exists(session_file):
        print("✅ Session file: EXISTS")
        try:
            with open(session_file, 'r') as f:
                session_data = json.load(f)
            print("✅ Session data: VALID JSON")
            
            # Check GEX data
            if 'gex_data' in session_data:
                gex_data = session_data['gex_data']
                print("✅ GEX data: PRESENT")
                print(f"   Current SPX: ${gex_data.get('current_spx', 'N/A')}")
                print(f"   Gamma Flip: ${gex_data.get('gamma_flip', 'N/A')}")
                print(f"   Call Wall: ${gex_data.get('call_wall', 'N/A')}")
                print(f"   Put Wall: ${gex_data.get('put_wall', 'N/A')}")
                print(f"   Market Regime: {gex_data.get('market_regime', 'N/A')}")
            else:
                print("⚠️ GEX data: MISSING")
            
            # Check positions
            positions = session_data.get('filled_positions', [])
            if len(positions) == 0:
                print("✅ Positions: CLEAR")
            else:
                print(f"⚠️ Positions: {len(positions)} ACTIVE")
                
        except Exception as e:
            print(f"❌ Session data: INVALID - {e}")
    else:
        print("❌ Session file: MISSING")
    
    print("\nGEX SYSTEM CHECK")
    print("-" * 30)
    
    # Check GEX components
    if os.path.exists('gex_analyzer.py'):
        print("✅ GEX Analyzer: EXISTS")
    else:
        print("❌ GEX Analyzer: MISSING")
    
    if os.path.exists('spx_gex_integration.py'):
        print("✅ GEX Integration: EXISTS")
    else:
        print("❌ GEX Integration: MISSING")
    
    print("\nFILE SYSTEM CHECK")
    print("-" * 30)
    
    # Check .spx directory
    if os.path.exists('.spx'):
        print("✅ .spx directory: EXISTS")
    else:
        print("❌ .spx directory: MISSING")
    
    # Check write permissions
    try:
        test_file = ".spx/test_write.tmp"
        with open(test_file, 'w') as f:
            f.write("test")
        os.remove(test_file)
        print("✅ Write permissions: OK")
    except:
        print("❌ Write permissions: DENIED")
    
    print("\nSYSTEM SUMMARY")
    print("-" * 30)
    print("💊 RECOMMENDATIONS:")
    print("   - Run 'gex analysis' for fresh GEX data")
    print("   - Use 'spx analysis gex' for integrated analysis")
    print("   - Check API connectivity if data seems stale")
    
    print(f"\n📋 Diagnosis completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    """
    Main command handler
    """
    if len(sys.argv) < 2:
        print("Usage: python spx_commands.py '<command>'")
        print("Example: python spx_commands.py 'gex analysis'")
        return
    
    command = ' '.join(sys.argv[1:])
    handle_command(command)

if __name__ == "__main__":
    main()