#!/usr/bin/env python3
"""
Script per l'analisi dei dati dell'Esperimento 2.
Confronta diverse strategie (RelaxScore, AvgRelPref, BP2S, EPR, RND) con l'Oracle.

Usage: python experiment_analysis.py <file_csv>
"""

import pandas as pd
import numpy as np
import sys
import ast
from collections import Counter

def parse_qg_list(qg_string):
    """
    Parsa una stringa che rappresenta una lista QG.
    Gestisce anche valori vuoti e formati non standard.
    """
    try:
        if pd.isna(qg_string) or qg_string == '':
            return []
        # Rimuove eventuali spazi e converte la stringa in lista
        parsed = ast.literal_eval(qg_string)
        # Filtra elementi vuoti
        return [item for item in parsed if item != '']
    except:
        return []

def lists_match(list1, list2):
    """
    Verifica se due liste contengono gli stessi elementi (ordine non importante).
    """
    if isinstance(list1, str):
        list1 = parse_qg_list(list1)
    if isinstance(list2, str):
        list2 = parse_qg_list(list2)

    return set(list1) == set(list2)

def analyze_experiment_data(csv_file):
    """
    Analizza i dati dell'esperimento confrontando le strategie con l'Oracle.
    """
    print(f"Caricamento dati da: {csv_file}")

    # Carica il CSV
    try:
        df = pd.read_csv(csv_file, delimiter=';')
        print(f"Dati caricati: {len(df)} righe, {len(df.columns)} colonne")
    except Exception as e:
        print(f"Errore nel caricamento del file: {e}")
        return

    # Strategie da analizzare
    strategies = ['RelaxScore', 'AvgRelPref', 'BP2S', 'EPR', 'RND']

    print("\n" + "="*80)
    print("ANALISI CORRISPONDENZA QG CON ORACLE")
    print("="*80)

    # Analisi corrispondenza QG
    qg_results = {}
    total_rows = len(df)

    for strategy in strategies:
        qg_col = f"{strategy}_qg"
        if qg_col in df.columns:
            # Conta le corrispondenze
            matches = 0
            for idx, row in df.iterrows():
                oracle_qg = row['Oracle']
                strategy_qg = row[qg_col]
                if lists_match(oracle_qg, strategy_qg):
                    matches += 1

            match_percentage = (matches / total_rows) * 100
            qg_results[strategy] = {
                'matches': matches,
                'total': total_rows,
                'percentage': match_percentage
            }

            print(f"{strategy:12} | Corrispondenze: {matches:4}/{total_rows} ({match_percentage:6.2f}%)")

    print("\n" + "="*80)
    print("ANALISI CONFRONTO MARGINI")
    print("="*80)

    # Analisi margini
    margin_results = {}

    for strategy in strategies:
        margin_col = f"{strategy}_margin"
        if margin_col in df.columns:
            oracle_margins = df['Relaxed_margin'].dropna()
            strategy_margins = df[margin_col].dropna()

            if len(strategy_margins) > 0:
                # Statistiche comparative
                oracle_mean = oracle_margins.mean()
                strategy_mean = strategy_margins.mean()

                # Differenza media assoluta
                common_indices = df.dropna(subset=['Relaxed_margin', margin_col]).index
                if len(common_indices) > 0:
                    oracle_subset = df.loc[common_indices, 'Relaxed_margin']
                    strategy_subset = df.loc[common_indices, margin_col]
                    mean_abs_diff = abs(oracle_subset - strategy_subset).mean()

                    # Conta quante volte la strategia è migliore (margine più piccolo è meglio?)
                    # Assumendo che margini più piccoli siano migliori
                    better_count = sum(strategy_subset < oracle_subset)
                    worse_count = sum(strategy_subset > oracle_subset)
                    equal_count = sum(strategy_subset == oracle_subset)

                    margin_results[strategy] = {
                        'oracle_mean': oracle_mean,
                        'strategy_mean': strategy_mean,
                        'mean_abs_diff': mean_abs_diff,
                        'better_count': better_count,
                        'worse_count': worse_count,
                        'equal_count': equal_count,
                        'total_compared': len(common_indices)
                    }

                    print(f"\n{strategy}:")
                    print(f"  Margine medio Oracle:     {oracle_mean:.4f}")
                    print(f"  Margine medio {strategy}: {strategy_mean:.4f}")
                    print(f"  Differenza media assoluta: {mean_abs_diff:.4f}")
                    print(f"  Migliore di Oracle:       {better_count}/{len(common_indices)} ({better_count/len(common_indices)*100:.1f}%)")
                    print(f"  Peggiore di Oracle:       {worse_count}/{len(common_indices)} ({worse_count/len(common_indices)*100:.1f}%)")
                    print(f"  Uguale a Oracle:          {equal_count}/{len(common_indices)} ({equal_count/len(common_indices)*100:.1f}%)")

    print("\n" + "="*80)
    print("RIEPILOGO PRESTAZIONI")
    print("="*80)

    # Ranking delle strategie
    print("\nRanking per corrispondenza QG (% di match con Oracle):")
    qg_ranking = sorted(qg_results.items(), key=lambda x: x[1]['percentage'], reverse=True)
    for i, (strategy, results) in enumerate(qg_ranking, 1):
        print(f"{i}. {strategy:12} - {results['percentage']:6.2f}%")

    print("\nRanking per margini (minor differenza media assoluta da Oracle):")
    margin_ranking = sorted([(k, v) for k, v in margin_results.items() if 'mean_abs_diff' in v],
                          key=lambda x: x[1]['mean_abs_diff'])
    for i, (strategy, results) in enumerate(margin_ranking, 1):
        print(f"{i}. {strategy:12} - Diff. media: {results['mean_abs_diff']:.4f}")

    print("\n" + "="*80)
    print("ANALISI SUCCESSO STRATEGIE")
    print("="*80)

    # Analisi tasso di successo
    print("\nTasso di successo per strategia:")
    for strategy in strategies:
        success_col = f"{strategy}_success"
        if success_col in df.columns:
            success_rate = df[success_col].mean() * 100
            total_success = df[success_col].sum()
            print(f"{strategy:12} | Successi: {total_success:4}/{total_rows} ({success_rate:6.2f}%)")

    # Analisi Oracle come baseline
    if 'Relaxed_success' in df.columns:
        oracle_success_rate = df['Relaxed_success'].mean() * 100
        oracle_total_success = df['Relaxed_success'].sum()
        print(f"{'Oracle':12} | Successi: {oracle_total_success:4}/{total_rows} ({oracle_success_rate:6.2f}%)")

def main():
    if len(sys.argv) != 2:
        print("Usage: python experiment_analysis.py <file_csv>")
        sys.exit(1)

    csv_file = sys.argv[1]
    analyze_experiment_data(csv_file)

if __name__ == "__main__":
    main()
