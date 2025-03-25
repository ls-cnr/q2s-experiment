import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime

def load_results(file_path="data/exp1_results.csv"):
    """
    Carica i risultati da un file CSV.
    """
    try:
        df = pd.read_csv(file_path)
        print(f"Loaded {len(df)} experiment results from {file_path}")
        return df
    except Exception as e:
        print(f"Error loading results: {e}")
        return None

def print_dataset_statistics(df):
    """
    Stampa statistiche generali sul dataset.
    """
    print("\n===== DATASET STATISTICS =====")
    print(f"Total scenarios: {len(df)}")

    # Statistiche sulle dimensioni degli eventi
    event_sizes = df['event_size'].value_counts()
    print("\nEvent sizes distribution:")
    for size, count in event_sizes.items():
        print(f"  {size}: {count} scenarios ({count/len(df)*100:.1f}%)")

    # Statistiche sui vincoli
    print("\nConstraints statistics:")
    print(f"  Cost constraint: min={df['cost_constraint'].min()}, max={df['cost_constraint'].max()}, avg={df['cost_constraint'].mean():.1f}")
    print(f"  Effort constraint: min={df['effort_constraint'].min()}, max={df['effort_constraint'].max()}, avg={df['effort_constraint'].mean():.1f}")
    print(f"  Time constraint: min={df['time_constraint'].min()}, max={df['time_constraint'].max()}, avg={df['time_constraint'].mean():.1f}")

    # Statistiche sulle perturbazioni
    print("\nPerturbation levels distribution:")
    for pert_type in ['perturbation_level_cost', 'perturbation_level_effort', 'perturbation_level_time']:
        pert_counts = df[pert_type].value_counts()
        print(f"  {pert_type}:")
        for level, count in pert_counts.items():
            print(f"    {level}: {count} scenarios ({count/len(df)*100:.1f}%)")

    # Statistiche sui piani validi
    print(f"\nValid plans: min={df['num_valid_plans'].min()}, max={df['num_valid_plans'].max()}, avg={df['num_valid_plans'].mean():.1f}")
    no_valid_plans = len(df[df['num_valid_plans'] == 0])
    print(f"Scenarios with no valid plans: {no_valid_plans} ({no_valid_plans/len(df)*100:.1f}%)")

def compare_strategies(df):
    """
    Confronta le performance delle quattro strategie.
    """
    print("\n===== STRATEGY COMPARISON =====")

    # Filtra scenari con almeno un piano valido
    valid_df = df[df['num_valid_plans'] > 0].copy()
    print(f"Analyzing {len(valid_df)} scenarios with at least one valid plan")

    # Calcola la media dei tassi di successo e margini per ogni strategia
    strategies = ['Q2S', 'Avg', 'Min', 'Random']
    success_rates = {}
    margins = {}

    for strategy in strategies:
        success_rates[strategy] = valid_df[f'{strategy}_success'].mean() * 100  # In percentuale
        margins[strategy] = valid_df[f'{strategy}_margins'].mean()

    # Stampa i risultati in ordine di tasso di successo
    print("\nSuccess rates (percentage of plans that remain valid after perturbation):")
    for strategy, rate in sorted(success_rates.items(), key=lambda x: x[1], reverse=True):
        print(f"  {strategy}: {rate:.2f}%")

    print("\nAverage margins (distance from constraints after perturbation):")
    for strategy, margin in sorted(margins.items(), key=lambda x: x[1], reverse=True):
        print(f"  {strategy}: {margin:.4f}")

    # Crea un dataframe con i risultati per un'analisi più dettagliata
    result_df = pd.DataFrame({
        'Strategy': strategies,
        'Success Rate (%)': [success_rates[s] for s in strategies],
        'Average Margin': [margins[s] for s in strategies]
    })

    return result_df

def analyze_by_perturbation_level(df):
    """
    Analizza come le diverse strategie si comportano con diversi livelli di perturbazione.
    """
    print("\n===== ANALYSIS BY PERTURBATION LEVEL =====")

    # Filtra scenari con almeno un piano valido
    valid_df = df[df['num_valid_plans'] > 0].copy()

    # Crea un dizionario per memorizzare i risultati
    results = {}

    # Per ogni tipo di perturbazione
    for pert_type in ['perturbation_level_cost', 'perturbation_level_effort', 'perturbation_level_time']:
        print(f"\n{pert_type}:")
        results[pert_type] = {}

        # Per ogni livello di perturbazione
        for level in valid_df[pert_type].unique():
            level_df = valid_df[valid_df[pert_type] == level]

            if len(level_df) == 0:
                continue

            results[pert_type][level] = {}
            print(f"  {level} ({len(level_df)} scenarios):")

            # Calcola tassi di successo per ogni strategia
            strategies = ['Q2S', 'Avg', 'Min', 'Random']
            for strategy in strategies:
                success_rate = level_df[f'{strategy}_success'].mean() * 100  # In percentuale
                margin = level_df[f'{strategy}_margins'].mean()
                results[pert_type][level][strategy] = (success_rate, margin)

                print(f"    {strategy}: Success = {success_rate:.2f}%, Margin = {margin:.4f}")

    return results

def analyze_by_alpha(df):
    """
    Analizza come il parametro alpha influisce sulle prestazioni di Q2S.
    """
    print("\n===== ANALYSIS BY ALPHA VALUE =====")

    # Filtra scenari con almeno un piano valido
    valid_df = df[df['num_valid_plans'] > 0].copy()

    # Raggruppa per alpha e calcola statistiche
    alpha_groups = valid_df.groupby('alpha')

    for alpha, group in alpha_groups:
        print(f"\nAlpha = {alpha} ({len(group)} scenarios):")

        # Calcola tassi di successo di Q2S
        q2s_success = group['Q2S_success'].mean() * 100
        q2s_margin = group['Q2S_margins'].mean()

        # Confronta con le altre strategie
        avg_success = group['Avg_success'].mean() * 100
        min_success = group['Min_success'].mean() * 100
        random_success = group['Random_success'].mean() * 100

        print(f"  Q2S Success Rate: {q2s_success:.2f}%")
        print(f"  Q2S Average Margin: {q2s_margin:.4f}")
        print(f"  Comparison:")
        print(f"    Q2S vs AvgSat: {q2s_success - avg_success:+.2f}%")
        print(f"    Q2S vs MinSat: {q2s_success - min_success:+.2f}%")
        print(f"    Q2S vs Random: {q2s_success - random_success:+.2f}%")

def create_visualizations(df, output_dir="results/visualizations"):
    """
    Crea visualizzazioni per analizzare i dati.
    """
    print("\n===== CREATING VISUALIZATIONS =====")

    # Crea directory di output se non esiste
    os.makedirs(output_dir, exist_ok=True)

    # Filtra scenari con almeno un piano valido
    valid_df = df[df['num_valid_plans'] > 0].copy()

    # 1. Confronto generale delle strategie (tasso di successo e margine medio)
    plt.figure(figsize=(12, 5))

    # Tasso di successo
    plt.subplot(1, 2, 1)
    strategies = ['Q2S', 'Avg', 'Min', 'Random']
    success_rates = [valid_df[f'{s}_success'].mean() * 100 for s in strategies]

    bars = plt.bar(strategies, success_rates, color=['#3498db', '#2ecc71', '#e74c3c', '#f39c12'])
    plt.title('Success Rate by Strategy')
    plt.ylabel('Success Rate (%)')
    plt.ylim(0, 100)

    # Aggiungi etichette ai bar
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 1,
                 f'{height:.1f}%', ha='center', va='bottom')

    # Margine medio
    plt.subplot(1, 2, 2)
    margins = [valid_df[f'{s}_margins'].mean() for s in strategies]

    bars = plt.bar(strategies, margins, color=['#3498db', '#2ecc71', '#e74c3c', '#f39c12'])
    plt.title('Average Margin by Strategy')
    plt.ylabel('Average Margin')

    # Aggiungi etichette ai bar
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.001,
                 f'{height:.3f}', ha='center', va='bottom')

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'strategy_comparison.png'), dpi=300)
    print(f"Saved strategy_comparison.png")

    # 2. Analisi per livello di perturbazione (tasso di successo)
    for pert_type in ['perturbation_level_cost', 'perturbation_level_effort', 'perturbation_level_time']:
        plt.figure(figsize=(12, 6))

        # Ordina i livelli di perturbazione in un modo più logico
        level_order = ['pos', 'no', 'low_neg', 'high_neg']

        # Crea una matrice di dati per il grafico
        pert_levels = []
        strategy_data = {s: [] for s in strategies}

        for level in level_order:
            if level not in valid_df[pert_type].values:
                continue

            level_df = valid_df[valid_df[pert_type] == level]
            if len(level_df) == 0:
                continue

            pert_levels.append(level)
            for s in strategies:
                strategy_data[s].append(level_df[f'{s}_success'].mean() * 100)

        # Crea il grafico a barre
        bar_width = 0.2
        index = np.arange(len(pert_levels))

        colors = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12']
        for i, (strategy, color) in enumerate(zip(strategies, colors)):
            bars = plt.bar(index + i*bar_width, strategy_data[strategy], bar_width,
                    label=strategy, color=color)

            # Aggiungi etichette ai bar
            for bar in bars:
                height = bar.get_height()
                if height > 5:  # Solo per valori significativi
                    plt.text(bar.get_x() + bar.get_width()/2., height + 1,
                            f'{height:.0f}%', ha='center', va='bottom', fontsize=8)

        plt.xlabel('Perturbation Level')
        plt.ylabel('Success Rate (%)')
        plt.title(f'Success Rate by {pert_type} Level')
        plt.xticks(index + bar_width * 1.5, pert_levels)
        plt.legend()
        plt.ylim(0, 105)  # Un po' di spazio extra per le etichette

        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f'success_by_{pert_type}.png'), dpi=300)
        print(f"Saved success_by_{pert_type}.png")

    # 3. Analisi per alpha (solo per Q2S)
    plt.figure(figsize=(10, 6))

    alpha_values = sorted(valid_df['alpha'].unique())
    q2s_success_by_alpha = [valid_df[valid_df['alpha'] == a]['Q2S_success'].mean() * 100 for a in alpha_values]

    plt.plot(alpha_values, q2s_success_by_alpha, 'o-', linewidth=2, markersize=8, color='#3498db')

    # Aggiungi etichette ai punti
    for i, alpha in enumerate(alpha_values):
        plt.text(alpha, q2s_success_by_alpha[i] + 1, f'{q2s_success_by_alpha[i]:.1f}%',
                 ha='center', va='bottom')

    plt.xlabel('Alpha Value')
    plt.ylabel('Q2S Success Rate (%)')
    plt.title('Impact of Alpha on Q2S Performance')
    plt.grid(True, linestyle='--', alpha=0.7)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'q2s_by_alpha.png'), dpi=300)
    print(f"Saved q2s_by_alpha.png")

    # 4. Correlazione tra numero di piani validi e tasso di successo
    plt.figure(figsize=(10, 6))

    plt.scatter(valid_df['num_valid_plans'], valid_df['Q2S_success'] * 100,
                alpha=0.6, color='#3498db', label='Q2S')
    plt.scatter(valid_df['num_valid_plans'], valid_df['Random_success'] * 100,
                alpha=0.6, color='#f39c12', label='Random')

    # Aggiungi linee di tendenza
    z1 = np.polyfit(valid_df['num_valid_plans'], valid_df['Q2S_success'] * 100, 1)
    p1 = np.poly1d(z1)
    plt.plot(sorted(valid_df['num_valid_plans'].unique()),
             p1(sorted(valid_df['num_valid_plans'].unique())),
             '--', color='#3498db')

    z2 = np.polyfit(valid_df['num_valid_plans'], valid_df['Random_success'] * 100, 1)
    p2 = np.poly1d(z2)
    plt.plot(sorted(valid_df['num_valid_plans'].unique()),
             p2(sorted(valid_df['num_valid_plans'].unique())),
             '--', color='#f39c12')

    plt.xlabel('Number of Valid Plans')
    plt.ylabel('Success Rate (%)')
    plt.title('Success Rate vs Number of Valid Plans')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'success_vs_valid_plans.png'), dpi=300)
    print(f"Saved success_vs_valid_plans.png")

    plt.close('all')
    print(f"All visualizations saved to {output_dir}")

def generate_summary_report(df, output_file="results/experiment_summary.md"):
    """
    Genera un report di riepilogo in formato Markdown.
    """
    print("\n===== GENERATING SUMMARY REPORT =====")

    # Crea directory di output se non esiste
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # Filtra scenari con almeno un piano valido
    valid_df = df[df['num_valid_plans'] > 0].copy()

    # Calcola statistiche essenziali
    strategies = ['Q2S', 'Avg', 'Min', 'Random']
    success_rates = {s: valid_df[f'{s}_success'].mean() * 100 for s in strategies}
    margins = {s: valid_df[f'{s}_margins'].mean() for s in strategies}

    # Ordina le strategie dal migliore al peggiore
    sorted_by_success = sorted(success_rates.items(), key=lambda x: x[1], reverse=True)
    best_strategy = sorted_by_success[0][0]

    # Genera il contenuto del report
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    report = f"""# Q2S Experiment Summary Report
Generated on: {timestamp}

## Overview
- Total scenarios analyzed: {len(df)}
- Scenarios with valid plans: {len(valid_df)} ({len(valid_df)/len(df)*100:.1f}%)
- Average number of valid plans per scenario: {valid_df['num_valid_plans'].mean():.1f}

## Strategy Performance Comparison

### Success Rates (percentage of plans that remain valid after perturbation)
| Strategy | Success Rate (%) |
|----------|-----------------|
"""

    for strategy, rate in sorted_by_success:
        report += f"| {strategy} | {rate:.2f}% |\n"

    report += f"""
### Average Margins (distance from constraints after perturbation)
| Strategy | Average Margin |
|----------|---------------|
"""

    for strategy, margin in sorted(margins.items(), key=lambda x: x[1], reverse=True):
        report += f"| {strategy} | {margin:.4f} |\n"

    report += f"""
## Key Findings
- The best performing strategy is **{best_strategy}** with a success rate of {sorted_by_success[0][1]:.2f}%
- Compared to Random strategy baseline, {best_strategy} performs {success_rates[best_strategy] - success_rates['Random']:.2f}% better
"""

    # Aggiungi analisi per alpha se Q2S è la migliore
    if best_strategy == 'Q2S':
        alpha_groups = valid_df.groupby('alpha')
        best_alpha = 0
        best_alpha_success = 0

        report += "\n### Performance of Q2S by Alpha Value\n"
        report += "| Alpha | Success Rate (%) | Margin |\n"
        report += "|-------|-----------------|--------|\n"

        for alpha, group in alpha_groups:
            q2s_success = group['Q2S_success'].mean() * 100
            q2s_margin = group['Q2S_margins'].mean()

            if q2s_success > best_alpha_success:
                best_alpha = alpha
                best_alpha_success = q2s_success

            report += f"| {alpha} | {q2s_success:.2f}% | {q2s_margin:.4f} |\n"

        report += f"\nThe optimal alpha value appears to be **{best_alpha}** with a success rate of {best_alpha_success:.2f}%\n"

    # Aggiungi analisi per perturbazioni negative
    report += "\n## Performance Under Negative Perturbations\n"

    for pert_type in ['perturbation_level_cost', 'perturbation_level_effort', 'perturbation_level_time']:
        neg_perts = ['low_neg', 'high_neg']
        neg_df = valid_df[valid_df[pert_type].isin(neg_perts)]

        if len(neg_df) > 0:
            report += f"\n### {pert_type}\n"
            report += "| Strategy | Success Rate (%) | Margin |\n"
            report += "|----------|-----------------|--------|\n"

            for strategy in strategies:
                success_rate = neg_df[f'{strategy}_success'].mean() * 100
                margin = neg_df[f'{strategy}_margins'].mean()
                report += f"| {strategy} | {success_rate:.2f}% | {margin:.4f} |\n"

    # Conclusioni
    report += f"""
## Conclusion
Based on the experiment results, the {best_strategy} strategy demonstrates the highest resilience to perturbations,
with a success rate of {sorted_by_success[0][1]:.2f}%. This indicates that {best_strategy}'s approach to plan selection
provides better robustness against uncertainties in the execution environment.
"""

    # Scrivi il report nel file
    with open(output_file, 'w') as f:
        f.write(report)

    print(f"Summary report generated and saved to {output_file}")

    # Genera anche una versione CSV delle statistiche principali
    csv_file = output_file.replace('.md', '.csv')

    result_df = pd.DataFrame({
        'Strategy': strategies,
        'Success Rate (%)': [success_rates[s] for s in strategies],
        'Average Margin': [margins[s] for s in strategies]
    })

    result_df.to_csv(csv_file, index=False)
    print(f"Summary statistics saved to {csv_file}")

    return result_df

def analyze_results(input_file="data/exp1_results.csv", output_dir="results"):
    """
    Funzione principale per analizzare i risultati dell'esperimento.
    """
    print(f"Starting analysis of {input_file}")

    # Carica i dati
    df = load_results(input_file)
    if df is None or len(df) == 0:
        print("No data to analyze. Exiting.")
        return

    # Crea directory di output se non esiste
    os.makedirs(output_dir, exist_ok=True)

    # Esegui le analisi
    print_dataset_statistics(df)
    result_df = compare_strategies(df)

    # Analisi più dettagliate
    analyze_by_perturbation_level(df)
    analyze_by_alpha(df)

    # Crea visualizzazioni
    viz_dir = os.path.join(output_dir, "visualizations")
    create_visualizations(df, viz_dir)

    # Genera report di riepilogo
    summary_file = os.path.join(output_dir, "experiment_summary.md")
    generate_summary_report(df, summary_file)

    print(f"\nAnalysis complete. Results saved to {output_dir}")

    return result_df

if __name__ == "__main__":
    start_time = datetime.now()

    analyze_results()

    end_time = datetime.now()
    elapsed_time = end_time - start_time
    print(f"Analysis completed in {elapsed_time}")
