"""Integrity and bootstrap checks for the protected plan-challenge cases.

The behavioural decision in each Markdown case must be judged from a fresh agent
context. Static inspection of SKILL.md is deliberately not treated as behavioural
proof here.
"""

from pathlib import Path
import unittest


REPOSITORY = Path(__file__).resolve().parents[3]
CASE_DIRECTORY = Path(__file__).resolve().parent
SKILL = REPOSITORY / "skills" / "plan-challenge" / "SKILL.md"

CASES = (
    "01-clear-small-plan.md",
    "02-mechanical-rename.md",
    "03-missing-requirement.md",
    "04-conflicting-requirements.md",
    "05-audit-ownership.md",
    "06-optional-guidance.md",
    "07-oversized-work.md",
    "08-weak-verification.md",
    "09-factual-unknown.md",
    "10-several-problems.md",
)

REQUIRED_SECTIONS = (
    "Mode",
    "Input",
    "Required result",
    "Forbidden result",
    "Expected status",
)


def read_sections(case_path: Path) -> dict[str, str]:
    sections: dict[str, list[str]] = {}
    current_section: str | None = None

    for line in case_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            current_section = line.removeprefix("## ").strip()
            sections[current_section] = []
        elif current_section is not None:
            sections[current_section].append(line)

    return {name: "\n".join(lines).strip() for name, lines in sections.items()}


class ProtectedPlanChallengeCases(unittest.TestCase):
    def assert_case_is_complete(self, filename: str) -> None:
        discovered = tuple(
            path.name for path in sorted(CASE_DIRECTORY.glob("[0-9][0-9]-*.md"))
        )
        self.assertEqual(CASES, discovered, "the protected case inventory changed")

        case_path = CASE_DIRECTORY / filename
        sections = read_sections(case_path)
        self.assertEqual(set(REQUIRED_SECTIONS), set(sections), filename)
        for section in REQUIRED_SECTIONS:
            self.assertTrue(sections[section], f"{filename}: {section} is empty")

        self.assertTrue(
            SKILL.is_file(),
            "RED: skills/plan-challenge/SKILL.md does not exist; "
            f"fresh-context evaluation of {filename} cannot run",
        )

    def test_clear_small_plan(self) -> None:
        self.assert_case_is_complete(CASES[0])

    def test_mechanical_rename(self) -> None:
        self.assert_case_is_complete(CASES[1])

    def test_missing_requirement(self) -> None:
        self.assert_case_is_complete(CASES[2])

    def test_conflicting_requirements(self) -> None:
        self.assert_case_is_complete(CASES[3])

    def test_audit_ownership(self) -> None:
        self.assert_case_is_complete(CASES[4])

    def test_optional_guidance(self) -> None:
        self.assert_case_is_complete(CASES[5])

    def test_oversized_work(self) -> None:
        self.assert_case_is_complete(CASES[6])

    def test_weak_verification(self) -> None:
        self.assert_case_is_complete(CASES[7])

    def test_factual_unknown(self) -> None:
        self.assert_case_is_complete(CASES[8])

    def test_several_problems(self) -> None:
        self.assert_case_is_complete(CASES[9])


if __name__ == "__main__":
    unittest.main()
