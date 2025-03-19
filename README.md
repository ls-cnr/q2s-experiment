# Progetto Q2S (Quality to Satisfaction)

Questo progetto implementa un framework sperimentale per valutare l'efficacia della matrice Quality to Satisfaction (Q2S) nella selezione di piani in presenza di perturbazioni.

## Descrizione

La matrice Q2S è uno strumento progettato per valutare e confrontare diversi piani in base alla loro capacità di soddisfare obiettivi di qualità. Il progetto confronta diverse strategie di selezione dei piani:

1. **Q2S**: Combina AvgSat e MinSat secondo il parametro α
2. **AvgSat**: Seleziona il piano con la migliore media delle distanze
3. **MinSat**: Seleziona il piano con la migliore distanza minima
4. **Random**: Seleziona casualmente un piano valido (baseline)

## Struttura del progetto

- `data/`: Contiene i file CSV di input e output
- `scripts/`: Contiene gli script Python per l'esperimento
  - `scenario_generator.py`: Genera scenari sperimentali
  - `scenario_processor.py`: Elabora gli scenari e applica le strategie
  - `results_analyzer.py`: Analizza i risultati e genera report

## Utilizzo

1. Generare gli scenari:
   ```
   python scripts/scenario_generator.py
   ```

2. Elaborare gli scenari:
   ```
   python scripts/scenario_processor.py
   ```

3. Analizzare i risultati:
   ```
   python scripts/results_analyzer.py
   ```
