import unittest
from exp1_scenario_processor import (
    avg_only_strategy,
    min_only_strategy,
    apply_perturbation,
    evaluate_plan_under_perturbation,
    PERTURBATION_VALUE
)

class TestExp1ScenarioProcessor(unittest.TestCase):

    def setUp(self):
        """Inizializza i dati di test."""
        # Matrice Q2S per i test delle strategie di selezione
        self.q2s_matrix = {
            "Plan1": {"QG0": 0.4, "QG1": 0.2, "QG2": 0.1},  # AvgSat = 0.2333, MinSat = 0.1
            "Plan2": {"QG0": 0.3, "QG1": 0.3, "QG2": 0.3},  # AvgSat = 0.3, MinSat = 0.3
            "Plan3": {"QG0": 0.5, "QG1": 0.1, "QG2": 0.05}  # AvgSat = 0.2167, MinSat = 0.05
        }

        # Piano con i suoi impatti per i test delle perturbazioni
        self.plan = {
            "name": "TestPlan",
            "impact": {
                "TotalCost": 150,
                "TotalEffort": 2.5,
                "TimeSpent": 4.0
            }
        }

        # Quality goals per i test
        self.quality_goals = {
            "QG0": {"name": "QG0", "domain_variable": "TotalCost", "max_value": 200, "type": "max"},
            "QG1": {"name": "QG1", "domain_variable": "TotalEffort", "max_value": 3, "type": "max"},
            "QG2": {"name": "QG2", "domain_variable": "TimeSpent", "max_value": 6, "type": "max"}
        }

        # Scenari per i test delle perturbazioni
        self.scenario_no_perturbation = {
            "id": 1,
            "event_size": "small",
            "organizers": 1,
            "time": 2,
            "budget": 100,
            "alpha": 0.5,
            "perturbation_level_org": "no",
            "perturbation_level_time": "no",
            "perturbation_level_cost": "no"
        }

        self.scenario_with_perturbation = {
            "id": 2,
            "event_size": "small",
            "organizers": 1,
            "time": 2,
            "budget": 100,
            "alpha": 0.5,
            "perturbation_level_org": "low_neg",  # +1 organizzatore (aumenta effort)
            "perturbation_level_time": "high_neg",  # +48 ore
            "perturbation_level_cost": "low_neg"   # +50 euro
        }

        self.scenario_with_positive_perturbation = {
            "id": 3,
            "event_size": "small",
            "organizers": 1,
            "time": 2,
            "budget": 100,
            "alpha": 0.5,
            "perturbation_level_org": "pos",  # -1 organizzatore (riduce effort)
            "perturbation_level_time": "pos",  # -24 ore
            "perturbation_level_cost": "pos"   # -50 euro
        }

    def test_avg_only_strategy(self):
        """Test per la funzione avg_only_strategy."""
        # Test caso normale
        selected_plan, score = avg_only_strategy(self.q2s_matrix)
        # Plan2 ha l'AvgSat più alto (0.3)
        self.assertEqual(selected_plan, "Plan2", "La strategia AvgSat dovrebbe selezionare Plan2")
        self.assertAlmostEqual(score, 0.3, places=4, msg="Score non corretto per Plan2")

        # Test con matrice vuota
        selected_plan, score = avg_only_strategy({})
        self.assertIsNone(selected_plan, "Con matrice vuota dovrebbe restituire None")
        self.assertEqual(score, 0, "Con matrice vuota lo score dovrebbe essere 0")

        # Test con valori mancanti
        incomplete_matrix = {
            "Plan1": {},  # Piano senza distanze
            "Plan2": {"QG0": 0.3, "QG1": 0.3, "QG2": 0.3}
        }
        selected_plan, score = avg_only_strategy(incomplete_matrix)
        self.assertEqual(selected_plan, "Plan2", "Dovrebbe ignorare i piani senza distanze")
        self.assertAlmostEqual(score, 0.3, places=4, msg="Score non corretto per Plan2")

    def test_min_only_strategy(self):
        """Test per la funzione min_only_strategy."""
        # Test caso normale
        selected_plan, score = min_only_strategy(self.q2s_matrix)
        # Plan2 ha il MinSat più alto (0.3)
        self.assertEqual(selected_plan, "Plan2", "La strategia MinSat dovrebbe selezionare Plan2")
        self.assertAlmostEqual(score, 0.3, places=4, msg="Score non corretto per Plan2")

        # Test con matrice vuota
        selected_plan, score = min_only_strategy({})
        self.assertIsNone(selected_plan, "Con matrice vuota dovrebbe restituire None")
        self.assertEqual(score, 0, "Con matrice vuota lo score dovrebbe essere 0")

        # Test con valori mancanti
        incomplete_matrix = {
            "Plan1": {},  # Piano senza distanze
            "Plan2": {"QG0": 0.3, "QG1": 0.3, "QG2": 0.3}
        }
        selected_plan, score = min_only_strategy(incomplete_matrix)
        self.assertEqual(selected_plan, "Plan2", "Dovrebbe ignorare i piani senza distanze")
        self.assertAlmostEqual(score, 0.3, places=4, msg="Score non corretto per Plan2")

    def test_apply_perturbation(self):
        """Test per la funzione apply_perturbation."""
        # Test senza perturbazioni
        perturbed_impacts = apply_perturbation(self.plan["impact"], self.scenario_no_perturbation)
        self.assertEqual(perturbed_impacts, self.plan["impact"],
                         "Senza perturbazioni gli impatti dovrebbero rimanere invariati")

        # Test con perturbazioni negative
        perturbed_impacts = apply_perturbation(self.plan["impact"], self.scenario_with_perturbation)

        # Verifica singole perturbazioni
        # TotalCost: 150 + 50 = 200 (perturbazione low_neg sul costo)
        self.assertEqual(perturbed_impacts["TotalCost"], 200,
                         "La perturbazione del costo non è stata applicata correttamente")

        # TimeSpent: 4.0 + 48 = 52.0 (perturbazione high_neg sul tempo)
        self.assertEqual(perturbed_impacts["TimeSpent"], 52.0,
                         "La perturbazione del tempo non è stata applicata correttamente")

        # TotalEffort: 2.5 * (1 + 0.15 * 1) = 2.5 * 1.15 = 2.875 (perturbazione low_neg sugli organizzatori)
        self.assertAlmostEqual(perturbed_impacts["TotalEffort"], 2.875, places=4,
                             msg="La perturbazione dell'effort non è stata applicata correttamente")

        # Test con perturbazioni positive
        perturbed_impacts = apply_perturbation(self.plan["impact"], self.scenario_with_positive_perturbation)

        # TotalCost: 150 - 50 = 100 (perturbazione pos sul costo)
        self.assertEqual(perturbed_impacts["TotalCost"], 100,
                         "La perturbazione positiva del costo non è stata applicata correttamente")

        # TimeSpent: 4.0 - 24 = -20.0 (perturbazione pos sul tempo)
        self.assertEqual(perturbed_impacts["TimeSpent"], -20.0,
                         "La perturbazione positiva del tempo non è stata applicata correttamente")

    def test_evaluate_plan_under_perturbation(self):
        """Test per la funzione evaluate_plan_under_perturbation."""
        # Test piano valido senza perturbazioni
        success_rate, avg_margin = evaluate_plan_under_perturbation(
            "TestPlan", self.plan, self.quality_goals, self.scenario_no_perturbation
        )
        self.assertEqual(success_rate, 1, "Il piano dovrebbe rimanere valido senza perturbazioni")

        # Calcolo margini attesi senza perturbazioni:
        # QG0: (200 - 150) / 200 = 0.25
        # QG1: (3 - 2.5) / 3 = 0.1667
        # QG2: (6 - 4) / 6 = 0.3333
        # Media = (0.25 + 0.1667 + 0.3333) / 3 = 0.25
        self.assertAlmostEqual(avg_margin, 0.25, places=2,
                             msg="Il margine medio non è corretto per il piano senza perturbazioni")

        # Test piano che diventa non valido con perturbazioni
        success_rate, avg_margin = evaluate_plan_under_perturbation(
            "TestPlan", self.plan, self.quality_goals, self.scenario_with_perturbation
        )
        self.assertEqual(success_rate, 0, "Il piano dovrebbe diventare non valido con perturbazioni negative")

        # Con perturbazioni negative i nuovi valori sono:
        # TotalCost: 200 (soglia 200) -> margine (200-200)/200 = 0
        # TotalEffort: 2.875 (soglia 3) -> margine (3-2.875)/3 = 0.0417
        # TimeSpent: 52 (soglia 6) -> margine (6-52)/6 = -7.6667 (ma il calcolo è su valori positivi)
        # Media = (0 + 0.0417 + (-7.6667)) / 3 = -2.5417
        # Non testiamo il valore esatto dell'avg_margin poiché dipende da come la funzione
        # gestisce i margini negativi nei vincoli violati

        # Test piano che rimane valido con perturbazioni positive
        # Prima modifichiamo il piano per essere vicino ai limiti
        plan_at_limit = {
            "name": "PlanAtLimit",
            "impact": {
                "TotalCost": 190,  # Vicino al limite di 200
                "TotalEffort": 2.9,  # Vicino al limite di 3
                "TimeSpent": 5.5    # Vicino al limite di 6
            }
        }

        success_rate, avg_margin = evaluate_plan_under_perturbation(
            "PlanAtLimit", plan_at_limit, self.quality_goals, self.scenario_with_positive_perturbation
        )
        self.assertEqual(success_rate, 1, "Il piano dovrebbe rimanere valido con perturbazioni positive")

        # Con perturbazioni positive:
        # TotalCost: 190 - 50 = 140 (soglia 200) -> margine (200-140)/200 = 0.3
        # TotalEffort: 2.9 (perturbazione 'pos' su organizzatori influisce sull'effort ma non testiamo)
        # TimeSpent: 5.5 - 24 = -18.5 (soglia 6) -> margine molto grande
        # La media sarà sicuramente positiva
        self.assertGreater(avg_margin, 0, "Il margine medio dovrebbe essere positivo con perturbazioni positive")

if __name__ == '__main__':
    unittest.main()
