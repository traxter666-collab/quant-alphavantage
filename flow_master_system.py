#!/usr/bin/env python3
"""
MASTER OPTIONS FLOW SYSTEM
Complete automation: Auto-detect PDFs → TA Analysis → Agent Integration → Discord → Tracking

Usage:
    python flow_master_system.py                    # Auto-detect latest PDF
    python flow_master_system.py "path/to/flow.pdf" # Specific PDF
    python flow_master_system.py --watch            # Watch Downloads folder
"""
import os
import sys
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from flow_pdf_parser import FlowPDFParser
from flow_ta_engine import FlowTechnicalAnalyzer

class FlowMasterSystem:
    def __init__(self):
        self.downloads_dir = Path.home() / "Downloads"
        self.db_file = Path("flow_database.json")
        self.config_file = Path("flow_config.json")
        self.load_config()

    def load_config(self):
        """Load or create configuration"""
        default_config = {
            'min_ta_score': 70,
            'discord_channel': 'alerts',
            'auto_send': True,
            'watch_interval': 300,  # 5 minutes
            'account_size': 50000,
            'max_risk_per_trade': 0.02,  # 2%
            'downloads_folder': str(self.downloads_dir)
        }

        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                self.config = {**default_config, **json.load(f)}
        else:
            self.config = default_config
            self.save_config()

    def save_config(self):
        """Save configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)

    def find_latest_flow_pdf(self):
        """Find most recent flow PDF in Downloads"""
        pdf_patterns = ['*flow*.pdf', '*Flow*.pdf', '*FLOW*.pdf']
        all_pdfs = []

        for pattern in pdf_patterns:
            all_pdfs.extend(self.downloads_dir.glob(pattern))

        if not all_pdfs:
            return None

        # Sort by modification time, most recent first
        latest = max(all_pdfs, key=lambda p: p.stat().st_mtime)
        return latest

    def load_database(self):
        """Load historical flow database"""
        if self.db_file.exists():
            with open(self.db_file, 'r') as f:
                return json.load(f)
        return {'flows': [], 'trades': [], 'stats': {}}

    def save_to_database(self, flow_data, ta_results, analysis_timestamp):
        """Save flow analysis to database"""
        db = self.load_database()

        entry = {
            'timestamp': analysis_timestamp,
            'pdf_name': flow_data.get('pdf_name', 'unknown'),
            'total_plays': len(flow_data.get('calls_bought', [])),
            'ta_results': ta_results,
            'high_quality_count': sum(1 for ta in ta_results.values() if ta['ta_score'] >= 70)
        }

        db['flows'].append(entry)

        # Update stats
        db['stats']['total_analyses'] = len(db['flows'])
        db['stats']['last_analysis'] = analysis_timestamp

        with open(self.db_file, 'w') as f:
            json.dump(db, f, indent=2)

        print(f"💾 Saved to database: {len(db['flows'])} total analyses")

    def analyze_flow(self, pdf_path):
        """Complete flow analysis pipeline"""
        print("\n" + "="*70)
        print("🚀 MASTER FLOW ANALYSIS SYSTEM")
        print("="*70)
        print(f"📄 PDF: {pdf_path}")
        print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📊 Min TA Score: {self.config['min_ta_score']}")
        print(f"📱 Discord: {self.config['discord_channel']}")
        print()

        # Step 1: Parse PDF
        print("━" * 70)
        print("STEP 1: PARSING PDF")
        print("━" * 70)
        parser = FlowPDFParser(str(pdf_path))
        data = parser.parse()

        if not data:
            print("❌ Failed to parse PDF")
            return None

        data['pdf_name'] = pdf_path.name

        # Step 2: Technical Analysis
        print("\n" + "━" * 70)
        print("STEP 2: TECHNICAL ANALYSIS")
        print("━" * 70)

        analyzer = FlowTechnicalAnalyzer()
        ta_results = {}

        # Get all unique tickers
        all_trades = (
            data['calls_bought'][:15] +
            data['puts_sold'][:10] +
            data['puts_bought'][:10]
        )

        unique_tickers = list(set(trade['ticker'] for trade in all_trades))
        print(f"Analyzing {len(unique_tickers)} unique tickers...")

        for ticker in unique_tickers:
            ticker_trades = [t for t in all_trades if t['ticker'] == ticker]
            if ticker_trades:
                best_trade = max(ticker_trades, key=lambda x: x['premium_value'])

                if best_trade in data['calls_bought']:
                    option_type = 'calls_bought'
                elif best_trade in data['puts_sold']:
                    option_type = 'puts_sold'
                else:
                    option_type = 'puts_bought'

                ta_result = analyzer.analyze_ticker(
                    ticker,
                    option_type,
                    best_trade['strike'],
                    best_trade['premium_value']
                )
                ta_results[ticker] = ta_result

        # Step 3: Filter by TA score
        print("\n" + "━" * 70)
        print("STEP 3: FILTERING HIGH-QUALITY SETUPS")
        print("━" * 70)

        high_quality = {
            ticker: ta
            for ticker, ta in ta_results.items()
            if ta['ta_score'] >= self.config['min_ta_score']
        }

        excellent = sum(1 for ta in ta_results.values() if ta['ta_score'] >= 75)
        good = sum(1 for ta in ta_results.values() if 60 <= ta['ta_score'] < 75)
        fair = sum(1 for ta in ta_results.values() if 45 <= ta['ta_score'] < 60)
        poor = sum(1 for ta in ta_results.values() if ta['ta_score'] < 45)

        print(f"\n📊 TA SCORE DISTRIBUTION:")
        print(f"   Excellent (≥75): {excellent}")
        print(f"   Good (60-74): {good}")
        print(f"   Fair (45-59): {fair}")
        print(f"   Poor (<45): {poor}")
        print(f"\n✅ High-Quality Plays (≥{self.config['min_ta_score']}): {len(high_quality)}")

        # Step 4: Generate agent prompts
        print("\n" + "━" * 70)
        print("STEP 4: GENERATING AGENT ANALYSIS PROMPTS")
        print("━" * 70)

        agent_prompts = self.generate_agent_prompts(data, high_quality)

        # Step 5: Send to Discord
        if self.config['auto_send'] and high_quality:
            print("\n" + "━" * 70)
            print("STEP 5: SENDING TO DISCORD")
            print("━" * 70)

            self.send_to_discord(data, high_quality)

        # Step 6: Save to database
        print("\n" + "━" * 70)
        print("STEP 6: SAVING TO DATABASE")
        print("━" * 70)

        timestamp = datetime.now().isoformat()
        self.save_to_database(data, {k: {'ta_score': v['ta_score'], 'recommendation': v['recommendation']}
                                     for k, v in ta_results.items()}, timestamp)

        # Step 7: Display summary
        print("\n" + "="*70)
        print("✅ ANALYSIS COMPLETE")
        print("="*70)

        result = {
            'pdf_path': str(pdf_path),
            'timestamp': timestamp,
            'total_tickers': len(unique_tickers),
            'high_quality_count': len(high_quality),
            'ta_results': ta_results,
            'agent_prompts': agent_prompts
        }

        return result

    def generate_agent_prompts(self, data, high_quality_ta):
        """Generate prompts for specialized agents"""
        prompts = {
            'chart_reader': None,
            'entry_analyzer': [],
            'risk_manager': []
        }

        # Chart reader prompt (for reference)
        prompts['chart_reader'] = f"""
Flow data extracted from PDF:

Total Plays:
- Calls Bought: {len(data['calls_bought'])}
- Puts Sold: {len(data['puts_sold'])}
- Puts Bought: {len(data['puts_bought'])}
- Calls Sold: {len(data['calls_sold'])}

High-Quality Setups: {len(high_quality_ta)}
"""

        # Entry analyzer prompts
        print("\n📋 AGENT PROMPTS GENERATED:\n")
        print("🎯 FOR @flow-entry-analyzer:")
        print("-" * 70)

        for ticker, ta_data in list(high_quality_ta.items())[:5]:
            # Find the trade
            trade = None
            for t in data['calls_bought']:
                if t['ticker'] == ticker:
                    trade = t
                    break

            if trade:
                prompt = f"""
{ticker} ${trade['strike']} calls bought
Premium: ${trade['premium']} ({trade['premium_value']:,.0f})
Expiration: {trade['expiration']}
Distance: {trade['percent_otm']}% OTM
TA Score: {ta_data['ta_score']:.0f}/100 ({ta_data['setup_quality']})

Please provide:
1. Current price and ATR
2. Optimal entry zone
3. ATR-based targets (T1, T2, T3)
4. Stop loss level
5. Key support/resistance levels
"""
                prompts['entry_analyzer'].append(prompt)
                print(prompt)
                print("-" * 70)

        # Risk manager prompt
        print("\n💰 FOR @flow-risk-manager:")
        print("-" * 70)

        risk_prompt = f"""
Account Size: ${self.config['account_size']:,.0f}
Max Risk Per Trade: {self.config['max_risk_per_trade']*100}%

Calculate position sizing for these high-quality setups:
"""

        for ticker in list(high_quality_ta.keys())[:3]:
            risk_prompt += f"\n- {ticker} (TA Score: {high_quality_ta[ticker]['ta_score']:.0f})"

        risk_prompt += "\n\nFor each position, provide:\n1. Max contracts\n2. Dollar risk\n3. Greeks exposure\n4. Portfolio heat impact"

        prompts['risk_manager'].append(risk_prompt)
        print(risk_prompt)
        print("-" * 70)

        return prompts

    def send_to_discord(self, data, high_quality_ta):
        """Send analysis to Discord"""
        # Build message
        message = f"""📊 AUTOMATED FLOW ANALYSIS

**{len(data['calls_bought'])} CALLS BOUGHT | {len(data['puts_sold'])} PUTS SOLD | {len(data['puts_bought'])} PUTS BOUGHT | {len(data['calls_sold'])} CALLS SOLD**

**{len(high_quality_ta)} HIGH-QUALITY SETUPS** (TA Score ≥{self.config['min_ta_score']})

━━━━━━━━━━━━━━━━━━━━━━━━━━━
🟢 **TOP PLAYS (TA FILTERED)**
━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""

        # Add top plays
        sorted_plays = sorted(high_quality_ta.items(), key=lambda x: x[1]['ta_score'], reverse=True)

        for i, (ticker, ta_data) in enumerate(sorted_plays[:5], 1):
            # Find trade details
            trade = None
            for t in data['calls_bought']:
                if t['ticker'] == ticker:
                    trade = t
                    break

            if trade:
                signals = "\n".join([f"  • {s}" for s in ta_data.get('signals', [])[:3]])

                message += f"""**#{i} {ticker} - {ta_data['setup_quality']}**
Calls Bought: ${trade['strike']} strike | Exp: {trade['expiration']}
Premium: ${trade['premium']} | Distance: {trade['percent_otm']}% OTM

📊 TA Score: {ta_data['ta_score']:.0f}/100 | Rec: {ta_data['recommendation']}
{signals}

"""

        message += """━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 NEXT STEPS
━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Use @flow-entry-analyzer for entry prices + ATR targets
2. Use @flow-risk-manager for position sizing
3. Set alerts at entry zones

🤖 Automated by TraxterAI Flow Master System"""

        try:
            result = subprocess.run(
                ['python', 'send_discord_multi.py',
                 '🤖 Automated Flow Analysis',
                 message,
                 self.config['discord_channel']],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                print(f"✅ Sent to Discord channel '{self.config['discord_channel']}'")
                return True
            else:
                print(f"⚠️ Discord send failed: {result.stderr}")
                return False
        except Exception as e:
            print(f"⚠️ Error sending to Discord: {e}")
            return False

    def watch_mode(self):
        """Watch Downloads folder for new PDFs"""
        print("\n" + "="*70)
        print("👁️ WATCH MODE ACTIVATED")
        print("="*70)
        print(f"📁 Monitoring: {self.downloads_dir}")
        print(f"⏱️ Interval: {self.config['watch_interval']} seconds")
        print(f"📊 Min TA Score: {self.config['min_ta_score']}")
        print(f"📱 Auto-send: {self.config['auto_send']}")
        print("\nPress Ctrl+C to stop...\n")

        processed_pdfs = set()

        try:
            while True:
                latest_pdf = self.find_latest_flow_pdf()

                if latest_pdf and latest_pdf not in processed_pdfs:
                    # Check if PDF is recent (within last hour)
                    mtime = latest_pdf.stat().st_mtime
                    age = time.time() - mtime

                    if age < 3600:  # Less than 1 hour old
                        print(f"\n🔔 NEW FLOW PDF DETECTED: {latest_pdf.name}")
                        print(f"⏰ Modified: {datetime.fromtimestamp(mtime).strftime('%H:%M:%S')}")

                        self.analyze_flow(latest_pdf)
                        processed_pdfs.add(latest_pdf)

                time.sleep(self.config['watch_interval'])

        except KeyboardInterrupt:
            print("\n\n👋 Watch mode stopped")

def main():
    system = FlowMasterSystem()

    if '--watch' in sys.argv:
        system.watch_mode()
    elif len(sys.argv) > 1 and sys.argv[1] != '--watch':
        pdf_path = Path(sys.argv[1])
        if not pdf_path.exists():
            print(f"❌ File not found: {pdf_path}")
            sys.exit(1)
        system.analyze_flow(pdf_path)
    else:
        # Auto-detect latest
        latest = system.find_latest_flow_pdf()
        if latest:
            print(f"📄 Auto-detected: {latest.name}")
            system.analyze_flow(latest)
        else:
            print("❌ No flow PDFs found in Downloads")
            print("\nUsage:")
            print('  python flow_master_system.py                    # Auto-detect latest')
            print('  python flow_master_system.py "path/to/flow.pdf" # Specific PDF')
            print('  python flow_master_system.py --watch            # Watch mode')

if __name__ == "__main__":
    main()
