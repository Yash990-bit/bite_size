"""
Unit and Integration Tests for BiteSize Agent
"""
import unittest
from bitesize.agent import BiteSizeAgent
from bitesize.schemas import DecomposedPlan, AtomicStep
from bitesize.tools import TaskDecomposerTool, DopamineTrackerTool, PlanExporterTool


class TestBiteSizeAgent(unittest.TestCase):

    def setUp(self):
        self.agent = BiteSizeAgent(user_name="Mayank")

    def test_deoverwhelm_generates_atomic_steps(self):
        dump = "my room is a disaster clothes on floor need to study for exam code is broken"
        plan = self.agent.deoverwhelm(dump, paralysis_level="extreme")
        
        self.assertIsInstance(plan, DecomposedPlan)
        self.assertGreater(len(plan.atomic_steps), 0)
        self.assertTrue(all(isinstance(s, AtomicStep) for s in plan.atomic_steps))
        # Ensure all steps are <= 120 seconds for ADHD executive relief
        self.assertTrue(all(s.estimated_seconds <= 120 for s in plan.atomic_steps))

    def test_focus_mode_advancement_and_dopamine(self):
        dump = "clean room wash dishes"
        self.agent.deoverwhelm(dump)
        
        # Step 1
        step1 = self.agent.get_current_focus_step()
        self.assertIsNotNone(step1)
        
        # Complete step 1
        res = self.agent.complete_current_step()
        self.assertEqual(res["status"], "success")
        self.assertEqual(self.agent.user_state.streak, 1)
        self.assertGreater(self.agent.user_state.dopamine_score, 0)
        
        # Next step should be different
        step2 = self.agent.get_current_focus_step()
        if step2:
            self.assertNotEqual(step1.id, step2.id)

    def test_export_plan_markdown(self):
        dump = "study for exam"
        self.agent.deoverwhelm(dump)
        md = self.agent.export_plan_markdown()
        self.assertIn("# 🎯 BiteSize Action Plan", md)
        self.assertIn("Atomic 2-Minute Steps", md)

    def test_arbitrary_unseen_tasks(self):
        dump = "file tax returns, take dog to the vet, fix the leaking faucet, and pack suitcase for trip"
        plan = self.agent.deoverwhelm(dump)
        self.assertEqual(len(plan.atomic_steps), 4)
        domains = [s.domain for s in plan.atomic_steps]
        self.assertIn("Administrative", domains)
        self.assertIn("Logistics & Errands", domains)
        self.assertIn("Physical Space", domains)

    def test_persistence_and_user_stats(self):
        dump = "drink water, clean desk"
        self.agent.deoverwhelm(dump)
        self.agent.complete_current_step()
        stats = self.agent.storage.get_user_stats("Mayank")
        self.assertGreater(stats["all_time_dopamine"], 0)
        self.assertGreater(stats["total_conquered_tasks"], 0)


if __name__ == "__main__":
    unittest.main()
