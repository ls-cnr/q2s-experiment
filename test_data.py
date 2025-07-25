#!/usr/bin/env python3
"""
Script per verificare anomalie nei dati dell'esperimento.
Identifica righe dove i margini delle strategie sono superiori al margine Oracle.

Usage: python test_data.py <file_csv>
"""

import pandas as pd
import sys

def load_csv_robust(csv_file):
    """
    Carica il CSV con gestione errori robusta.
    """
    try:
        # Prima prova con il delimitatore ';'
        df = pd.read_csv(csv_file, delimiter=';', encoding='utf-8')
        return df
    except Exception as e1:
        try:
            # Prova con delimitatore ','
            df = pd.read_csv(csv_file, delimiter=',', encoding='utf-8')
            return df
        except Exception as e2:
            try:
                # Prova con gestione errori per righe malformate
                df = pd.read_csv(csv_file, delimiter=';', encoding='utf-8',
                               on_bad_lines='skip')
                return df
            except Exception:
                try:
                    # Ultima prova con pandas legacy
                    df = pd.read_csv(csv_file, delimiter=';', encoding='utf-8',
                                   error_bad_lines=False, warn_bad_lines=True)
                    return df
                except Exception as e3:
                    print(f"Impossibile caricare il file: {e3}")
                    return None

def check_margin_anomalies(csv_file):
    """
    Verifica se ci sono righe dove i margini delle strategie superano il margine Oracle.
    """
    print(f"Controllo anomalie margini in: {csv_file}")

    # Carica il CSV
    df = load_csv_robust(csv_file)
    if df is None:
        return

    print(f"Dati caricati: {len(df)} righe")

    # Definisci le strategie da controllare
    strategies = ['RelaxScore', 'AvgRelPref', 'BP2S', 'EPR']

    # Verifica che le colonne necessarie esistano
    required_cols = ['ID', 'Relaxed_margin'] + [f"{strategy}_margin" for strategy in strategies]
    missing_cols = [col for col in required_cols if col not in df.columns]

    if missing_cols:
        print(f"ERRORE: Colonne mancanti nel file: {missing_cols}")
        print(f"Colonne disponibili: {list(df.columns)}")
        return

    print("\nControllo anomalie dove margine strategia > margine Oracle...")
    print("="*60)

    anomalies_found = []
    total_anomalies = 0

    for idx, row in df.iterrows():
        row_id = row['ID']
        oracle_margin = row['Relaxed_margin']

        # Salta righe con margine Oracle NaN
        if pd.isna(oracle_margin):
            continue

        row_anomalies = []

        # Controlla ogni strategia
        for strategy in strategies:
            strategy_margin = row[f"{strategy}_margin"]

            # Salta se il margine della strategia è NaN
            if pd.isna(strategy_margin):
                continue

            # Controlla se il margine della strategia è maggiore dell'Oracle
            if strategy_margin > oracle_margin:
                row_anomalies.append({
                    'strategy': strategy,
                    'strategy_margin': strategy_margin,
                    'oracle_margin': oracle_margin,
                    'difference': strategy_margin - oracle_margin
                })

        # Se ci sono anomalie in questa riga, registrale
        if row_anomalies:
            anomalies_found.append({
                'id': row_id,
                'anomalies': row_anomalies
            })
            total_anomalies += len(row_anomalies)

    # Stampa i risultati
    if anomalies_found:
        print(f"ANOMALIE TROVATE: {total_anomalies} in {len(anomalies_found)} righe")
        print("\nDettagli anomalie:")
        print("-" * 80)

        for item in anomalies_found:
            row_id = item['id']
            print(f"\nID {row_id}:")

            for anomaly in item['anomalies']:
                strategy = anomaly['strategy']
                strategy_margin = anomaly['strategy_margin']
                oracle_margin = anomaly['oracle_margin']
                diff = anomaly['difference']

                print(f"  {strategy:12} margin: {strategy_margin:8.4f} > Oracle: {oracle_margin:8.4f} (+{diff:6.4f})")

        print("\n" + "="*60)
        print("RIEPILOGO ID CON ANOMALIE:")
        ids_with_anomalies = [str(item['id']) for item in anomalies_found]
        print(", ".join(ids_with_anomalies))

        # Stampa statistiche per strategia
        print("\nSTATISTICHE ANOMALIE PER STRATEGIA:")
        strategy_counts = {}
        for item in anomalies_found:
            for anomaly in item['anomalies']:
                strategy = anomaly['strategy']
                strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1

        for strategy in strategies:
            count = strategy_counts.get(strategy, 0)
            print(f"  {strategy:12}: {count} anomalie")

    else:
        print("✓ NESSUNA ANOMALIA TROVATA")
        print("Tutti i margini delle strategie sono <= del margine Oracle")

    print(f"\nTotale righe analizzate: {len(df)}")
    print(f"Righe con anomalie: {len(anomalies_found)}")
    if len(df) > 0:
        print(f"Percentuale righe con anomalie: {len(anomalies_found)/len(df)*100:.2f}%")

def main():
    if len(sys.argv) != 2:
        print("Usage: python test_data.py <file_csv>")
        print("\nQuesto script verifica se ci sono righe dove i margini delle strategie")
        print("(RelaxScore, AvgRelPref, BP2S, EPR) superano il margine Oracle (Relaxed_margin).")
        sys.exit(1)

    csv_file = sys.argv[1]
    check_margin_anomalies(csv_file)

if __name__ == "__main__":
    main()
