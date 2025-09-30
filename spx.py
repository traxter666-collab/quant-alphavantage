#!/usr/bin/env python3
"""
SPX Trading System - Interactive Menu Interface
Consolidates all trading functionality into one seamless interface
"""

import os
import sys
import subprocess
import json
from datetime import datetime

class SPXTradingSystem:
    def __init__(self):
        self.session_file = ".spx/session.json"
        self.ensure_session_directory()

    def ensure_session_directory(self):
        """Ensure .spx directory exists"""
        if not os.path.exists(".spx"):
            os.makedirs(".spx")

    def clear_screen(self):
        """Clear the console screen"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def display_header(self):
        """Display system header"""
        print("=" * 60)
        print("      SPX 0DTE TRADING SYSTEM - INTERACTIVE MENU")
        print("=" * 60)
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Show current market data if available
        try:
            result = subprocess.run([sys.executable, "simple_api_test.py"],
                                  capture_output=True, text=True, cwd=".")
            if result.returncode == 0 and "SPY Price:" in result.stdout:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if "SPY Price:" in line or "SPX Estimate:" in line:
                        print(line)
        except:
            print("Market data unavailable")

        print("=" * 60)

    def display_menu(self):
        """Display main menu options"""
        print("\nMAIN MENU:")
        print("1. SPX Live Analysis (Full Market Report)")
        print("2. SPX Quick Analysis (Core Engine)")
        print("3. Fast SPY Price (Real-time)")
        print("4. Strike Recommendations")
        print("5. GEX Analysis (Gamma Exposure)")
        print("6. Monte Carlo Analysis")
        print("7. Market Validation")
        print("8. Send to Discord")
        print("9. System Tools")
        print("10. Session Management")
        print("0. Exit")
        print("-" * 40)

    def run_script(self, script_name, description="Running analysis"):
        """Execute a Python script and display results"""
        print(f"\n{description}...")
        print("-" * 40)

        try:
            result = subprocess.run([sys.executable, script_name],
                                  cwd=".", text=True, capture_output=True)

            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(f"Warnings: {result.stderr}")

            if result.returncode != 0:
                print(f"Script completed with warnings (code: {result.returncode})")

            return result.returncode == 0

        except FileNotFoundError:
            print(f"Error: {script_name} not found")
            return False
        except Exception as e:
            print(f"Error running {script_name}: {e}")
            return False

    def system_tools_menu(self):
        """System tools submenu"""
        while True:
            self.clear_screen()
            self.display_header()
            print("\nSYSTEM TOOLS:")
            print("1. Validate API Key")
            print("2. Debug API")
            print("3. Enhanced SPX Data Test")
            print("4. Simple API Test")
            print("5. Clean System Cache")
            print("0. Back to Main Menu")
            print("-" * 40)

            choice = input("Select option: ").strip()

            if choice == "1":
                self.run_script("validate_api_key.py", "Validating API Key")
            elif choice == "2":
                self.run_script("debug_api.py", "Running API Debug")
            elif choice == "3":
                self.run_script("enhanced_spx_data.py", "Testing Enhanced SPX Data")
            elif choice == "4":
                self.run_script("simple_api_test.py", "Running Simple API Test")
            elif choice == "5":
                self.clean_cache()
            elif choice == "0":
                break
            else:
                print("Invalid option. Please try again.")

            if choice != "0":
                input("\nPress Enter to continue...")

    def session_menu(self):
        """Session management submenu"""
        while True:
            self.clear_screen()
            self.display_header()
            print("\nSESSION MANAGEMENT:")
            print("1. Save Current Session")
            print("2. Load Session")
            print("3. View Session Notes")
            print("4. Clear Session Data")
            print("5. Session Statistics")
            print("0. Back to Main Menu")
            print("-" * 40)

            choice = input("Select option: ").strip()

            if choice == "1":
                self.save_session()
            elif choice == "2":
                self.load_session()
            elif choice == "3":
                self.view_session_notes()
            elif choice == "4":
                self.clear_session()
            elif choice == "5":
                self.session_stats()
            elif choice == "0":
                break
            else:
                print("Invalid option. Please try again.")

            if choice != "0":
                input("\nPress Enter to continue...")

    def save_session(self):
        """Save current session state"""
        session_data = {
            "timestamp": datetime.now().isoformat(),
            "last_activity": "Session saved via menu",
            "market_status": "Unknown"
        }

        try:
            with open(self.session_file, 'w') as f:
                json.dump(session_data, f, indent=2)
            print("SUCCESS: Session saved successfully")
        except Exception as e:
            print(f"ERROR: Error saving session: {e}")

    def load_session(self):
        """Load existing session"""
        try:
            if os.path.exists(self.session_file):
                with open(self.session_file, 'r') as f:
                    session_data = json.load(f)
                print("SUCCESS: Session loaded:")
                print(f"   Last saved: {session_data.get('timestamp', 'Unknown')}")
                print(f"   Activity: {session_data.get('last_activity', 'Unknown')}")
            else:
                print("INFO: No saved session found")
        except Exception as e:
            print(f"ERROR: Error loading session: {e}")

    def view_session_notes(self):
        """View session notes"""
        notes_file = ".spx/notes.txt"
        try:
            if os.path.exists(notes_file):
                with open(notes_file, 'r') as f:
                    notes = f.read()
                if notes.strip():
                    print("Session Notes:")
                    print("-" * 20)
                    print(notes)
                else:
                    print("INFO: No session notes found")
            else:
                print("INFO: No session notes file found")
        except Exception as e:
            print(f"ERROR: Error reading notes: {e}")

    def clear_session(self):
        """Clear session data"""
        confirm = input("WARNING: Clear all session data? (y/N): ").strip().lower()
        if confirm == 'y':
            try:
                for file in [".spx/session.json", ".spx/notes.txt", ".spx/levels.json"]:
                    if os.path.exists(file):
                        os.remove(file)
                print("SUCCESS: Session data cleared")
            except Exception as e:
                print(f"ERROR: Error clearing session: {e}")
        else:
            print("INFO: Session clear cancelled")

    def session_stats(self):
        """Show session statistics"""
        spx_dir = ".spx"
        if os.path.exists(spx_dir):
            files = os.listdir(spx_dir)
            print(f"Session Statistics:")
            print(f"   Files in .spx/: {len(files)}")
            for file in files:
                file_path = os.path.join(spx_dir, file)
                if os.path.isfile(file_path):
                    size = os.path.getsize(file_path)
                    mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                    print(f"   {file}: {size} bytes, modified {mtime.strftime('%Y-%m-%d %H:%M')}")
        else:
            print("INFO: No session directory found")

    def clean_cache(self):
        """Clean system cache"""
        cache_dirs = ["__pycache__", ".mypy_cache"]
        cleaned = 0

        for cache_dir in cache_dirs:
            if os.path.exists(cache_dir):
                try:
                    import shutil
                    shutil.rmtree(cache_dir)
                    cleaned += 1
                    print(f"SUCCESS: Cleaned {cache_dir}")
                except Exception as e:
                    print(f"ERROR: Error cleaning {cache_dir}: {e}")

        if cleaned == 0:
            print("INFO: No cache directories to clean")
        else:
            print(f"SUCCESS: Cleaned {cleaned} cache directories")

    def get_fast_spy_price(self):
        """Get fast SPY price using core engine"""
        print("\nGetting fast SPY price...")
        print("-" * 40)

        try:
            from core_functions import CoreTradingEngine
            engine = CoreTradingEngine()

            price_data = engine.get_price_data(force_refresh=True)

            if price_data:
                spy_price = price_data['spy_price']
                spx_price = price_data['spx_price']
                change = price_data['spy_change']
                change_pct = price_data['spy_change_percent']
                source = price_data['source']

                print(f"Source: {source.upper()}")
                print(f"SPY: ${spy_price:.2f} ({change:+.2f}, {change_pct:+.2f}%)")

                if price_data.get('after_hours'):
                    ah_price = price_data['after_hours']
                    ah_change = ah_price - spy_price
                    print(f"After Hours: ${ah_price:.2f} ({ah_change:+.2f})")

                print(f"SPX Equivalent: ${spx_price:.0f}")

                # Update session
                try:
                    session_data = {
                        "timestamp": datetime.now().isoformat(),
                        "spy_price": spy_price,
                        "spx_equivalent": spx_price,
                        "last_activity": "Fast price check",
                        "data_source": source
                    }
                    with open(self.session_file, 'w') as f:
                        import json
                        json.dump(session_data, f, indent=2)
                except:
                    pass
            else:
                print("ERROR: No price data available from any source")

        except Exception as e:
            print(f"ERROR: Core engine failed: {e}")
            print("Falling back to simple API test...")
            self.run_script("simple_api_test.py", "Getting fallback data")

    def run_core_analysis(self):
        """Run core trading analysis"""
        print("\nRunning Core Trading Analysis...")
        print("-" * 40)

        try:
            from core_functions import CoreTradingEngine
            engine = CoreTradingEngine()

            analysis = engine.quick_analysis()
            print(analysis)

            # Save analysis to session
            try:
                session_data = {
                    "timestamp": datetime.now().isoformat(),
                    "last_activity": "Core analysis completed",
                    "analysis_type": "quick_core"
                }
                with open(self.session_file, 'w') as f:
                    import json
                    json.dump(session_data, f, indent=2)
            except:
                pass

        except Exception as e:
            print(f"ERROR: Core analysis failed: {e}")
            print("Falling back to simple API test...")
            self.run_script("simple_api_test.py", "Getting fallback analysis")

    def get_strike_recommendations(self):
        """Get strike recommendations using core engine"""
        print("\nGenerating Strike Recommendations...")
        print("-" * 40)

        try:
            from core_functions import CoreTradingEngine
            engine = CoreTradingEngine()

            recommendations = engine.get_strike_recommendations()

            current_spx = recommendations['current_spx']

            print(f"CURRENT SPX: ${current_spx:.0f}")
            print()

            print("SCALP TRADES (High Probability):")
            print(f"  Calls: {recommendations['scalp_calls']}")
            print(f"  Puts:  {recommendations['scalp_puts']}")
            print()

            print("LOTTERY TRADES (High Risk/Reward):")
            print(f"  Calls: {recommendations['lottery_calls']}")
            print(f"  Puts:  {recommendations['lottery_puts']}")
            print()

            print("SAFE TRADES (Conservative):")
            print(f"  Calls: {recommendations['safe_calls']}")
            print(f"  Puts:  {recommendations['safe_puts']}")

        except Exception as e:
            print(f"ERROR: Strike recommendations failed: {e}")
            print("Using fallback analysis...")
            self.run_script("spx_strike_analysis.py", "Getting fallback strikes")

    def send_to_discord(self):
        """Send last analysis to Discord"""
        message = input("Enter message to send to Discord (or press Enter for test): ").strip()
        if not message:
            message = f"SPX Trading System Test - {datetime.now().strftime('%H:%M:%S')}"

        try:
            result = subprocess.run([sys.executable, "send_discord.py", "SPX Update", message],
                                  capture_output=True, text=True, cwd=".")

            if result.returncode == 0:
                print("SUCCESS: Message sent to Discord successfully")
            else:
                print(f"ERROR: Discord send failed: {result.stderr}")
        except Exception as e:
            print(f"ERROR: Error sending to Discord: {e}")

    def run(self):
        """Main application loop"""
        while True:
            try:
                self.clear_screen()
                self.display_header()
                self.display_menu()

                choice = input("Select option: ").strip()

                if choice == "1":
                    self.run_script("spx_live.py", "Running Full SPX Analysis")
                elif choice == "2":
                    self.run_core_analysis()
                elif choice == "3":
                    self.get_fast_spy_price()
                elif choice == "4":
                    self.get_strike_recommendations()
                elif choice == "5":
                    self.run_script("gex_analyzer.py", "Running GEX Analysis")
                elif choice == "6":
                    self.run_script("monte_carlo_analysis.py", "Running Monte Carlo Analysis")
                elif choice == "7":
                    self.run_script("validate_api_key.py", "Validating Market Data")
                elif choice == "8":
                    self.send_to_discord()
                elif choice == "9":
                    self.system_tools_menu()
                elif choice == "10":
                    self.session_menu()
                elif choice == "0":
                    print("\nExiting SPX Trading System...")
                    break
                else:
                    print("Invalid option. Please try again.")

                if choice not in ["0", "9", "10"]:
                    input("\nPress Enter to continue...")

            except KeyboardInterrupt:
                print("\n\nExiting...")
                break
            except Exception as e:
                print(f"\nError: {e}")
                input("Press Enter to continue...")

def main():
    """Entry point"""
    # Set encoding for Windows
    if os.name == 'nt':
        os.environ['PYTHONIOENCODING'] = 'utf-8'

    # Initialize and run the trading system
    system = SPXTradingSystem()
    system.run()

if __name__ == "__main__":
    main()