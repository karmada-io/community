#!/usr/bin/env python3
"""Find the first unsupported propagation stage from supplied evidence."""

import argparse

from lib.scenario import emit, load_scenario

STAGES = ("policyClaim", "binding", "scheduling", "work", "execution", "status")


def evaluate(data: dict) -> dict:
    evidence = data.get("evidence", {})
    for stage in STAGES:
        state = evidence.get(stage, "missing")
        if state != "ok":
            return {
                "id": data["id"],
                "firstProblemStage": stage,
                "state": state,
                "checkedStages": list(STAGES[: STAGES.index(stage) + 1]),
            }
    return {
        "id": data["id"],
        "firstProblemStage": None,
        "state": "ok",
        "checkedStages": list(STAGES),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("scenario")
    args = parser.parse_args()
    emit(evaluate(load_scenario(args.scenario)))


if __name__ == "__main__":
    main()
