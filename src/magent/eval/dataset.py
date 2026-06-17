"""Golden dataset loading.

The dataset is versioned JSON (under ``datasets/``). In production this would be
tracked with DVC; here it is a small checked-in file so the gate is hermetic.
"""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel, Field


class Case(BaseModel):
    """One evaluation case: a goal and what a good artifact should contain."""

    id: str
    goal: str
    acceptance_criteria: list[str] = Field(default_factory=list)
    expected_keywords: list[str] = Field(default_factory=list)


def load_dataset(path: str | Path) -> list[Case]:
    """Load and validate a golden dataset from a JSON file."""
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    return [Case.model_validate(item) for item in raw]


def default_dataset_path() -> Path:
    """Path to the bundled golden dataset."""
    return Path(__file__).parent / "datasets" / "golden.json"
