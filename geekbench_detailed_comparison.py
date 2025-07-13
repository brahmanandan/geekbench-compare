#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Author: K. Brahmanandan

import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_geekbench_data(geekbench_id):
    """Fetches and parses detailed Geekbench data for a given ID."""
    url = f"https://browser.geekbench.com/v6/cpu/{geekbench_id}"
    print(f"Fetching data for ID: {geekbench_id} from {url}")
    response = requests.get(url)
    if not response.ok:
        print(f"Failed to fetch URL: {url}")
        return None

    soup = BeautifulSoup(response.text, 'lxml')
    data = {"ID": geekbench_id}

    # --- Extract Summary Scores ---
    scores = {}
    single_core_div = soup.find('div', class_='note', string='Single-Core Score')
    if single_core_div and single_core_div.find_previous_sibling('div', class_='score'):
        scores["Single-Core Score"] = single_core_div.find_previous_sibling('div', class_='score').text.strip()
    multi_core_div = soup.find('div', class_='note', string='Multi-Core Score')
    if multi_core_div and multi_core_div.find_previous_sibling('div', class_='score'):
        scores["Multi-Core Score"] = multi_core_div.find_previous_sibling('div', class_='score').text.strip()
    data['Scores'] = scores

    # --- Extract Detailed Information Tables ---
    for heading_text in ["System Information", "CPU Information", "Memory Information"]:
        info_dict = {}
        heading = soup.find('th', string=heading_text)
        if heading:
            table = heading.find_parent('table')
            if table:
                for row in table.find_all('tr'):
                    cells = row.find_all('td')
                    if len(cells) == 2:
                        key = cells[0].text.strip()
                        value = cells[1].text.strip()
                        info_dict[key] = value
        data[heading_text] = info_dict

    # --- Extract Performance Benchmarks ---
    for heading_text in ["Single-Core Performance", "Multi-Core Performance"]:
        perf_dict = {}
        heading = soup.find('h3', string=heading_text)
        if heading and heading.parent:
            table_wrapper = heading.parent.find_next_sibling('div', class_='table-wrapper')
            if table_wrapper:
                table = table_wrapper.find('table')
                if table and table.find('tbody'):
                    for row in table.find('tbody').find_all('tr'):
                        cells = row.find_all('td')
                        if len(cells) == 3:
                            name = cells[0].contents[0].strip()
                            score = cells[1].contents[0].strip()
                            perf_dict[name] = int(score)
        data[heading_text] = perf_dict
        
    return data

def compare_benchmarks(ids):
    """Compares detailed benchmarks for a list of Geekbench IDs."""
    all_data = [get_geekbench_data(gid) for gid in ids]
    all_data = [d for d in all_data if d is not None]

    if not all_data:
        print("No data collected. Exiting.")
        return

    # --- General Scores and Info ---
    for section in ["Scores", "System Information", "CPU Information", "Memory Information"]:
        print("\n" + "="*80)
        print(f"{section} Comparison")
        print("="*80)
        df = pd.DataFrame([d.get(section, {}) for d in all_data], index=[d['ID'] for d in all_data])
        print(df.T.to_string())
        print("="*80)

    # --- Detailed Performance ---
    for section in ["Single-Core Performance", "Multi-Core Performance"]:
        print("\n" + "="*80)
        print(f"{section} Comparison")
        print("="*80)
        df = pd.DataFrame([d.get(section, {}) for d in all_data], index=[d['ID'] for d in all_data])
        print(df.T.to_string())
        print("="*80)


if __name__ == "__main__":
    geekbench_ids = [12842736, 12843900, 12842099]
    compare_benchmarks(geekbench_ids)
