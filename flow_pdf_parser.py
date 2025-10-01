#!/usr/bin/env python3
"""
Options Flow PDF Parser
Automatically extracts options flow data from PDF files
Usage: python flow_pdf_parser.py "path/to/flow.pdf"
"""
import sys
import re
import pdfplumber
from datetime import datetime
from pathlib import Path

class FlowPDFParser:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.data = {
            'calls_bought': [],
            'puts_sold': [],
            'puts_bought': [],
            'calls_sold': []
        }

    def parse(self):
        """Extract all options flow data from PDF"""
        print(f"📄 Parsing: {self.pdf_path}")

        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    print(f"📖 Processing page {page_num}/{len(pdf.pages)}")

                    # Extract text
                    text = page.extract_text()

                    # Parse each section
                    self._parse_calls_bought(text)
                    self._parse_puts_sold(text)
                    self._parse_puts_bought(text)
                    self._parse_calls_sold(text)

            print(f"✅ Parsed successfully!")
            print(f"   Calls Bought: {len(self.data['calls_bought'])}")
            print(f"   Puts Sold: {len(self.data['puts_sold'])}")
            print(f"   Puts Bought: {len(self.data['puts_bought'])}")
            print(f"   Calls Sold: {len(self.data['calls_sold'])}")

            return self.data

        except Exception as e:
            print(f"❌ Error parsing PDF: {e}")
            return None

    def _parse_calls_bought(self, text):
        """Parse 'Calls Bought' section"""
        # Pattern: TICKER STRIKE (X %) MM/DD/YY PREMIUM
        # Example: BABA 220.00 (23 %) 11/21/25 5.1M

        pattern = r'([A-Z]{1,5})\s+(\d+\.?\d*)\s+\(([+-]?\d+)\s*%\)\s+(\d{1,2}/\d{1,2}/\d{2,4})\s+([\d.]+[KM])'

        matches = re.finditer(pattern, text)
        for match in matches:
            ticker, strike, pct, exp, premium = match.groups()

            # Only add if in Calls Bought section
            if self._in_section(text, match.start(), "Calls Bought"):
                self.data['calls_bought'].append({
                    'ticker': ticker,
                    'strike': strike,
                    'percent_otm': pct,
                    'expiration': exp,
                    'premium': premium,
                    'premium_value': self._parse_premium(premium)
                })

    def _parse_puts_sold(self, text):
        """Parse 'Puts Sold' section"""
        pattern = r'([A-Z]{1,5})\s+(\d+\.?\d*)\s+\(([+-]?\d+)\s*%\)\s+(\d{1,2}/\d{1,2}/\d{2,4})\s+([\d.]+[KM])'

        matches = re.finditer(pattern, text)
        for match in matches:
            ticker, strike, pct, exp, premium = match.groups()

            if self._in_section(text, match.start(), "Puts Sold"):
                self.data['puts_sold'].append({
                    'ticker': ticker,
                    'strike': strike,
                    'percent_otm': pct,
                    'expiration': exp,
                    'premium': premium,
                    'premium_value': self._parse_premium(premium)
                })

    def _parse_puts_bought(self, text):
        """Parse 'Puts Bought' section"""
        pattern = r'([A-Z]{1,5})\s+(\d+\.?\d*)\s+\(([+-]?\d+)\s*%\)\s+(\d{1,2}/\d{1,2}/\d{2,4})\s+([\d.]+[KM])'

        matches = re.finditer(pattern, text)
        for match in matches:
            ticker, strike, pct, exp, premium = match.groups()

            if self._in_section(text, match.start(), "Puts Bought"):
                self.data['puts_bought'].append({
                    'ticker': ticker,
                    'strike': strike,
                    'percent_otm': pct,
                    'expiration': exp,
                    'premium': premium,
                    'premium_value': self._parse_premium(premium)
                })

    def _parse_calls_sold(self, text):
        """Parse 'Calls Sold' section"""
        pattern = r'([A-Z]{1,5})\s+(\d+\.?\d*)\s+\(([+-]?\d+)\s*%\)\s+(\d{1,2}/\d{1,2}/\d{2,4})\s+([\d.]+[KM])'

        matches = re.finditer(pattern, text)
        for match in matches:
            ticker, strike, pct, exp, premium = match.groups()

            if self._in_section(text, match.start(), "Calls Sold"):
                self.data['calls_sold'].append({
                    'ticker': ticker,
                    'strike': strike,
                    'percent_otm': pct,
                    'expiration': exp,
                    'premium': premium,
                    'premium_value': self._parse_premium(premium)
                })

    def _in_section(self, text, position, section_name):
        """Check if position is within specified section"""
        # Find section headers before and after position
        section_pattern = r'(Calls Bought|Puts Sold|Puts Bought|Calls Sold)'

        sections = list(re.finditer(section_pattern, text))

        for i, section in enumerate(sections):
            if section.group() == section_name:
                start = section.end()
                end = sections[i + 1].start() if i + 1 < len(sections) else len(text)

                if start <= position < end:
                    return True

        return False

    def _parse_premium(self, premium_str):
        """Convert premium string to numeric value (in dollars)"""
        value = float(re.sub(r'[KM]', '', premium_str))

        if 'M' in premium_str:
            return value * 1_000_000
        elif 'K' in premium_str:
            return value * 1_000
        return value

    def sort_by_premium(self):
        """Sort all sections by premium (highest first)"""
        for section in ['calls_bought', 'puts_sold', 'puts_bought', 'calls_sold']:
            self.data[section] = sorted(
                self.data[section],
                key=lambda x: x['premium_value'],
                reverse=True
            )

    def get_top_plays(self, n=5):
        """Get top N plays from each section"""
        self.sort_by_premium()

        return {
            'calls_bought': self.data['calls_bought'][:n],
            'puts_sold': self.data['puts_sold'][:n],
            'puts_bought': self.data['puts_bought'][:n],
            'calls_sold': self.data['calls_sold'][:n]
        }

def main():
    if len(sys.argv) < 2:
        print("Usage: python flow_pdf_parser.py 'path/to/flow.pdf'")
        print("\nExample:")
        print('  python flow_pdf_parser.py "Downloads/Flow-9-30-25.pdf.pdf"')
        sys.exit(1)

    pdf_path = sys.argv[1]

    if not Path(pdf_path).exists():
        print(f"❌ File not found: {pdf_path}")
        sys.exit(1)

    # Parse PDF
    parser = FlowPDFParser(pdf_path)
    data = parser.parse()

    if data:
        # Get top plays
        top_plays = parser.get_top_plays(5)

        print("\n" + "="*60)
        print("TOP 5 CALLS BOUGHT (by premium):")
        print("="*60)
        for i, trade in enumerate(top_plays['calls_bought'], 1):
            print(f"{i}. {trade['ticker']:6} ${trade['strike']:>7} ({trade['percent_otm']:>3}%) "
                  f"{trade['expiration']:>10} ${trade['premium']:>6}")

        print("\n" + "="*60)
        print("TOP 5 PUTS SOLD (by premium):")
        print("="*60)
        for i, trade in enumerate(top_plays['puts_sold'], 1):
            print(f"{i}. {trade['ticker']:6} ${trade['strike']:>7} ({trade['percent_otm']:>3}%) "
                  f"{trade['expiration']:>10} ${trade['premium']:>6}")

        print("\n" + "="*60)
        print("TOP 5 PUTS BOUGHT (by premium):")
        print("="*60)
        for i, trade in enumerate(top_plays['puts_bought'], 1):
            print(f"{i}. {trade['ticker']:6} ${trade['strike']:>7} ({trade['percent_otm']:>3}%) "
                  f"{trade['expiration']:>10} ${trade['premium']:>6}")

        print("\n✅ Parsing complete!")
        print(f"💡 Next: Run automated Discord formatter")
        print(f"   python flow.py \"{pdf_path}\"")

if __name__ == "__main__":
    main()
