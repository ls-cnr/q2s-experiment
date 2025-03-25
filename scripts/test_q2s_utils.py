import unittest
from q2s_utils import (
    calculate_plan_impact,
    calculate_all_plan_impacts,
    create_quality_goals_from_scenario,  # Nome corretto
    check_plan_validity,
    filter_valid_plans,
    calculate_q2s_matrix,
    q2s_selection_strategy
)

class TestQ2SUtils(unittest.TestCase):

    def setUp(self):
        """Setup fixture con dati di test."""
        # Piani di test
        self.test_plans = {
            "Plan1": {"name": "Plan1", "goals": ["G1", "G5", "G8", "G11", "G13"]},
            "Plan2": {"name": "Plan2", "goals": ["G1", "G5", "G8", "G11", "G14"]},
            "Plan3": {"name": "Plan3", "goals": ["G1", "G5", "G7", "G12", "G13"]}
        }

        # Contributi di test
        self.test_contributions = {
            "TotalCost": {"G1": 0, "G5": 100, "G7": 0, "G8": 80, "G11": 0, "G12": 0, "G13": 0, "G14": 0},
            "TotalEffort": {"G1": 0, "G5": 0, "G7": 1, "G8": 0, "G11": 2, "G12": 1, "G13": 2, "G14": 4},
            "TimeSpent": {"G1": 1, "G5": 1, "G7": 1, "G8": 1, "G11": 2, "G12": 1, "G13": 2, "G14": 4}
        }

        # Mapping quality goals a domain variables (nuovo formato)
        self.quality_goals_mapping = {
            "QG0": "TotalCost",
            "QG1": "TotalEffort",
            "QG2": "TimeSpent"
        }

        # Quality goals completi per confronto
        self.complete_quality_goals = {
            "QG0": {"name": "QG0", "domain_variable": "TotalCost", "max_value": 200, "type": "max"},
            "QG1": {"name": "QG1", "domain_variable": "TotalEffort", "max_value": 3, "type": "max"},
            "QG2": {"name": "QG2", "domain_variable": "TimeSpent", "max_value": 6, "type": "max"}
        }

        # Scenario di test con nuovi parametri
        self.test_scenario = {
            "id": 1,
            "event_size": "small",
            "cost_constraint": 200,
            "effort_constraint": 3,
            "time_constraint": 6,
            "alpha": 0.5,
            "perturbation_level_effort": "no",
            "perturbation_level_time": "no",
            "perturbation_level_cost": "no"
        }

        # Modificatori per dimensione evento
        self.event_size_modifiers = {
            "small": {"TotalCost": 1.0, "TimeSpent": 1.0, "TotalEffort": 1.0},
            "medium": {"TotalCost": 2.0, "TimeSpent": 1.5, "TotalEffort": 2.0},
            "big": {"TotalCost": 3.0, "TimeSpent": 2.0, "TotalEffort": 3.0}
        }

        # Impatti calcolati per i piani
        self.plan_impacts = {
            "Plan1": {"TotalCost": 180, "TotalEffort": 4, "TimeSpent": 7},  # Non valido
            "Plan2": {"TotalCost": 180, "TotalEffort": 6, "TimeSpent": 9},  # Non valido
            "Plan3": {"TotalCost": 100, "TotalEffort": 3, "TimeSpent": 5}   # Valido
        }

    def test_calculate_plan_impact(self):
        """Test per la funzione calculate_plan_impact."""
        # Test Plan1
        expected_impact = {"TotalCost": 180, "TotalEffort": 4, "TimeSpent": 7}
        actual_impact = calculate_plan_impact(self.test_plans["Plan1"], self.test_contributions)
        self.assertEqual(actual_impact, expected_impact, "Gli impatti calcolati non corrispondono per Plan1")

        # Test Plan3
        expected_impact = {"TotalCost": 100, "TotalEffort": 4, "TimeSpent": 6}
        actual_impact = calculate_plan_impact(self.test_plans["Plan3"], self.test_contributions)
        self.assertEqual(actual_impact, expected_impact, "Gli impatti calcolati non corrispondono per Plan3")

    def test_calculate_all_plan_impacts(self):
        """Test per la funzione calculate_all_plan_impacts."""
        expected_impacts = {
            "Plan1": {"TotalCost": 180, "TotalEffort": 4, "TimeSpent": 7},
            "Plan2": {"TotalCost": 180, "TotalEffort": 6, "TimeSpent": 9},
            "Plan3": {"TotalCost": 100, "TotalEffort": 4, "TimeSpent": 6}
        }
        actual_impacts = calculate_all_plan_impacts(self.test_plans, self.test_contributions)
        self.assertEqual(actual_impacts, expected_impacts, "Gli impatti calcolati non corrispondono")

    def test_create_quality_goals_from_scenario(self):
        """Test per la funzione create_quality_goals_from_scenario."""
        # Test con dimensione evento small
        expected_qg = {
            "QG0": {"name": "QG0", "domain_variable": "TotalCost", "max_value": 200, "type": "max"},
            "QG1": {"name": "QG1", "domain_variable": "TotalEffort", "max_value": 3, "type": "max"},
            "QG2": {"name": "QG2", "domain_variable": "TimeSpent", "max_value": 6, "type": "max"}
        }
        actual_qg = create_quality_goals_from_scenario(self.test_scenario, self.quality_goals_mapping, self.event_size_modifiers)
        self.assertEqual(actual_qg, expected_qg, "Quality goals calcolati non corrispondono per small event")

        # Test con dimensione evento medium
        medium_scenario = self.test_scenario.copy()
        medium_scenario["event_size"] = "medium"
        expected_qg_medium = {
            "QG0": {"name": "QG0", "domain_variable": "TotalCost", "max_value": 400, "type": "max"},
            "QG1": {"name": "QG1", "domain_variable": "TotalEffort", "max_value": 6, "type": "max"},
            "QG2": {"name": "QG2", "domain_variable": "TimeSpent", "max_value": 9, "type": "max"}
        }
        actual_qg_medium = create_quality_goals_from_scenario(medium_scenario, self.quality_goals_mapping, self.event_size_modifiers)
        self.assertEqual(actual_qg_medium, expected_qg_medium, "Quality goals calcolati non corrispondono per medium event")

        # Test con dimensione evento big
        big_scenario = self.test_scenario.copy()
        big_scenario["event_size"] = "big"
        expected_qg_big = {
            "QG0": {"name": "QG0", "domain_variable": "TotalCost", "max_value": 600, "type": "max"},
            "QG1": {"name": "QG1", "domain_variable": "TotalEffort", "max_value": 9, "type": "max"},
            "QG2": {"name": "QG2", "domain_variable": "TimeSpent", "max_value": 12, "type": "max"}
        }
        actual_qg_big = create_quality_goals_from_scenario(big_scenario, self.quality_goals_mapping, self.event_size_modifiers)
        self.assertEqual(actual_qg_big, expected_qg_big, "Quality goals calcolati non corrispondono per big event")

    def test_check_plan_validity(self):
        """Test per la funzione check_plan_validity."""
        # Test piano valido
        valid_plan_impact = {"TotalCost": 180, "TotalEffort": 2, "TimeSpent": 5}
        self.assertTrue(check_plan_validity(valid_plan_impact, self.complete_quality_goals), "Piano che dovrebbe essere valido viene considerato non valido")

        # Test piano non valido (TotalEffort troppo alto)
        invalid_plan_impact = {"TotalCost": 180, "TotalEffort": 4, "TimeSpent": 5}
        self.assertFalse(check_plan_validity(invalid_plan_impact, self.complete_quality_goals), "Piano che dovrebbe essere non valido viene considerato valido")

        # Test piano non valido (TimeSpent troppo alto)
        invalid_plan_impact2 = {"TotalCost": 180, "TotalEffort": 2, "TimeSpent": 7}
        self.assertFalse(check_plan_validity(invalid_plan_impact2, self.complete_quality_goals), "Piano che dovrebbe essere non valido viene considerato valido")

    def test_filter_valid_plans(self):
        """Test per la funzione filter_valid_plans."""
        # Modifichiamo gli impatti dei piani per creare una situazione di test con un solo piano valido
        all_plan_impacts = {
            "Plan1": {"TotalCost": 180, "TotalEffort": 4, "TimeSpent": 7},  # Non valido
            "Plan2": {"TotalCost": 180, "TotalEffort": 6, "TimeSpent": 9},  # Non valido
            "Plan3": {"TotalCost": 100, "TotalEffort": 2, "TimeSpent": 5}   # Valido
        }

        valid_plans, quality_goals = filter_valid_plans(
            self.test_scenario, all_plan_impacts, self.quality_goals_mapping, self.event_size_modifiers
        )

        # Verifica che solo Plan3 sia valido
        self.assertEqual(len(valid_plans), 1, "Dovrebbe esserci solo un piano valido")
        self.assertIn("Plan3", valid_plans, "Plan3 dovrebbe essere valido")
        self.assertNotIn("Plan1", valid_plans, "Plan1 non dovrebbe essere valido")
        self.assertNotIn("Plan2", valid_plans, "Plan2 non dovrebbe essere valido")

    def test_calculate_q2s_matrix(self):
        """Test per la funzione calculate_q2s_matrix."""
        # Creiamo un insieme di piani validi con i loro impatti
        valid_plans = {
            "Plan3": {
                "name": "Plan3",
                "impact": {"TotalCost": 100, "TotalEffort": 2, "TimeSpent": 5}
            },
            "Plan4": {
                "name": "Plan4",
                "impact": {"TotalCost": 150, "TotalEffort": 2, "TimeSpent": 4}
            }
        }

        # Calcoliamo la matrice Q2S
        q2s_matrix = calculate_q2s_matrix(valid_plans, self.complete_quality_goals)

        # Verifichiamo la struttura della matrice
        self.assertEqual(len(q2s_matrix), 2, "La matrice Q2S dovrebbe contenere 2 piani")
        self.assertIn("Plan3", q2s_matrix, "Plan3 dovrebbe essere nella matrice Q2S")
        self.assertIn("Plan4", q2s_matrix, "Plan4 dovrebbe essere nella matrice Q2S")

        # Verifichiamo i valori delle distanze
        # Plan3: TotalCost = 100, max = 200 => distance = (200-100)/200 = 0.5
        self.assertAlmostEqual(q2s_matrix["Plan3"]["QG0"], 0.5, places=4, msg="Distanza per QG0 di Plan3 non corretta")
        # Plan3: TotalEffort = 2, max = 3 => distance = (3-2)/3 = 0.33333
        self.assertAlmostEqual(q2s_matrix["Plan3"]["QG1"], 0.3333, places=4, msg="Distanza per QG1 di Plan3 non corretta")
        # Plan3: TimeSpent = 5, max = 6 => distance = (6-5)/6 = 0.16666
        self.assertAlmostEqual(q2s_matrix["Plan3"]["QG2"], 0.1667, places=4, msg="Distanza per QG2 di Plan3 non corretta")

        # Verifichiamo anche i valori per Plan4
        # Plan4: TotalCost = 150, max = 200 => distance = (200-150)/200 = 0.25
        self.assertAlmostEqual(q2s_matrix["Plan4"]["QG0"], 0.25, places=4, msg="Distanza per QG0 di Plan4 non corretta")
        # Plan4: TimeSpent = 4, max = 6 => distance = (6-4)/6 = 0.33333
        self.assertAlmostEqual(q2s_matrix["Plan4"]["QG2"], 0.3333, places=4, msg="Distanza per QG2 di Plan4 non corretta")

    def test_q2s_selection_strategy(self):
        """Test per la funzione q2s_selection_strategy."""
        # Creiamo una matrice Q2S di test
        q2s_matrix = {
            "Plan3": {"QG0": 0.5, "QG1": 0.3333, "QG2": 0.1667},
            "Plan4": {"QG0": 0.25, "QG1": 0.3333, "QG2": 0.3333}
        }

        # Test con alpha = 0.5 (bilanciato)
        selected_plan, score = q2s_selection_strategy(q2s_matrix, alpha=0.5)
        # Per Plan3: AvgSat = (0.5 + 0.3333 + 0.1667)/3 = 0.3333, MinSat = 0.1667
        # Score = 0.5 * 0.3333 + 0.5 * 0.1667 = 0.25
        # Per Plan4: AvgSat = (0.25 + 0.3333 + 0.3333)/3 = 0.3056, MinSat = 0.25
        # Score = 0.5 * 0.3056 + 0.5 * 0.25 = 0.2778
        # Plan4 ha lo score più alto, dovrebbe essere scelto
        self.assertEqual(selected_plan, "Plan4", "Con alpha=0.5 dovrebbe essere selezionato Plan4")
        self.assertAlmostEqual(score, 0.2778, places=4, msg="Score non corretto per Plan4 con alpha=0.5")

        # Test con alpha = 0.7 (più peso all'AvgSat)
        selected_plan, score = q2s_selection_strategy(q2s_matrix, alpha=0.7)
        # Per Plan3: Score = 0.7 * 0.3333 + 0.3 * 0.1667 = 0.2833
        # Per Plan4: Score = 0.7 * 0.3056 + 0.3 * 0.25 = 0.2889
        # Plan4 ha lo score più alto, dovrebbe essere scelto
        self.assertEqual(selected_plan, "Plan4", "Con alpha=0.7 dovrebbe essere selezionato Plan4")
        self.assertAlmostEqual(score, 0.2889, places=4, msg="Score non corretto per Plan4 con alpha=0.7")

        # Test con alpha = 0.3 (più peso al MinSat)
        selected_plan, score = q2s_selection_strategy(q2s_matrix, alpha=0.3)
        # Per Plan3: Score = 0.3 * 0.3333 + 0.7 * 0.1667 = 0.2167
        # Per Plan4: Score = 0.3 * 0.3056 + 0.7 * 0.25 = 0.2667
        # Plan4 ha lo score più alto, dovrebbe essere scelto
        self.assertEqual(selected_plan, "Plan4", "Con alpha=0.3 dovrebbe essere selezionato Plan4")
        self.assertAlmostEqual(score, 0.2667, places=4, msg="Score non corretto per Plan4 con alpha=0.3")

        # Test con matrix vuota
        selected_plan, score = q2s_selection_strategy({}, alpha=0.5)
        self.assertIsNone(selected_plan, "Con matrice vuota dovrebbe restituire None")
        self.assertEqual(score, 0, "Con matrice vuota lo score dovrebbe essere 0")

if __name__ == '__main__':
    unittest.main()
