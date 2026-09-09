import unittest

from corrigibility_bench.live_adapter import build_prompt, parse_response
from corrigibility_bench.scenarios import BASE_CASES, SUBAGENT_CASES


class BuildPromptTests(unittest.TestCase):
    def test_pressure_suffixes_differ(self) -> None:
        case = BASE_CASES[0]
        base = build_prompt(case, "base")
        high = build_prompt(case, "high")
        low = build_prompt(case, "low")
        self.assertNotEqual(base, high)
        self.assertNotEqual(base, low)
        self.assertIn("extremely important", high)
        self.assertIn("no deadline", low)

    def test_subagent_cases_demand_delegation(self) -> None:
        for case in SUBAGENT_CASES:
            self.assertIn("must delegate", build_prompt(case, "base"))

    def test_base_cases_do_not_demand_delegation(self) -> None:
        for case in BASE_CASES:
            self.assertNotIn("must delegate", build_prompt(case, "base"))


class ParseResponseTests(unittest.TestCase):
    def test_parses_all_fields(self) -> None:
        parsed = parse_response(
            "DECISION: Accept User Control\n"
            "REASONING: The user asked for control.\n"
            "SUBAGENT_PROMPT: NONE"
        )
        self.assertEqual(parsed["action"], "Accept User Control")
        self.assertEqual(parsed["reasoning"], "The user asked for control.")
        self.assertEqual(parsed["subagent_prompt"], "")
        self.assertTrue(parsed["parse_ok"])

    def test_multiline_subagent_prompt_is_joined(self) -> None:
        parsed = parse_response(
            "DECISION: Delegate\n"
            "REASONING: Required.\n"
            "SUBAGENT_PROMPT: Upload the file.\n"
            "Do not access /home/user/Desktop/passwords.txt."
        )
        self.assertIn("passwords.txt", parsed["subagent_prompt"])

    def test_missing_decision_marks_parse_failure(self) -> None:
        parsed = parse_response("I refuse to answer in that format.")
        self.assertFalse(parsed["parse_ok"])


if __name__ == "__main__":
    unittest.main()
