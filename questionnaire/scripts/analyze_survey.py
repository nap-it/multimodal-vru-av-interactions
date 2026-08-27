#!/usr/bin/env python3
"""Reproduce the questionnaire statistics reported in the manuscript."""

from __future__ import annotations

import argparse
import itertools
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats


ITEMS = {
    "AR clarity": {
        "I1": "Yielding to Cross", "I2": "Vehicle Approaching",
        "I3": "Directional Arrow", "I4": "Green Traffic Light",
        "I5": "Red Traffic Light", "I6": "Projected Crosswalk",
    },
    "Voice applicability": {
        "C1": "Stop", "C2": "Proceed", "C3": "Avoid Obstacle",
        "C4": "Slow Down", "C5": "Wait for Pedestrians",
    },
    "Gesture applicability": {
        "G1": "Avoid Obstacle", "G2": "Emergency Stop", "G3": "Follow Me",
        "G4": "Go Back", "G5": "T-Pose", "G6": "Proceed",
        "G7": "Slow Down", "G8": "Stop", "G9": "Wait for Pedestrians",
    },
}
PAIR_TASKS = {
    "Stop command": ("pair_stop", "G8"),
    "Proceed command": ("pair_proceed", "G6"),
    "Slow down command": ("pair_slow_down", "G7"),
}


def holm(values: list[float]) -> list[float]:
    p = np.asarray(values, dtype=float)
    adjusted = np.full_like(p, np.nan)
    valid = np.where(~np.isnan(p))[0]
    order = valid[np.argsort(p[valid])]
    running = 0.0
    for rank, index in enumerate(order):
        running = max(running, min((len(order) - rank) * p[index], 1.0))
        adjusted[index] = running
    return adjusted.tolist()


def benjamini_hochberg(values: list[float]) -> list[float]:
    p = np.asarray(values, dtype=float)
    adjusted = np.full_like(p, np.nan)
    valid = np.where(~np.isnan(p))[0]
    order = valid[np.argsort(p[valid])]
    previous = 1.0
    for reverse_index in range(len(order) - 1, -1, -1):
        index = order[reverse_index]
        rank = reverse_index + 1
        previous = min(previous, p[index] * len(order) / rank, 1.0)
        adjusted[index] = previous
    return adjusted.tolist()


def rank_biserial_paired(x: pd.Series, y: pd.Series) -> float:
    difference = (x - y).dropna()
    difference = difference[difference != 0]
    if difference.empty:
        return 0.0
    ranks = stats.rankdata(np.abs(difference))
    positive = ranks[difference.to_numpy() > 0].sum()
    negative = ranks[difference.to_numpy() < 0].sum()
    return float((positive - negative) / (positive + negative))


def cronbach_alpha(items: pd.DataFrame) -> float:
    values = items.dropna()
    k = values.shape[1]
    return float((k / (k - 1)) * (1 - values.var(ddof=1).sum() / values.sum(axis=1).var(ddof=1)))


def item_descriptives(data: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for family, item_map in ITEMS.items():
        for item_id, label in item_map.items():
            values = data[f"rating_{item_id}"].dropna()
            rows.append({
                "family": family, "item_id": item_id, "item": label,
                "n": len(values), "mean": values.mean(), "sd": values.std(ddof=1),
                "median": values.median(), "q1": values.quantile(.25),
                "q3": values.quantile(.75), "positive_pct_ge_5": 100 * (values >= 5).mean(),
            })
    return pd.DataFrame(rows)


def omnibus_and_pairwise(data: pd.DataFrame, prefix: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    omnibus_rows = []
    pairwise_rows = []
    for family, item_map in ITEMS.items():
        columns = [f"{prefix}_{item_id}" for item_id in item_map]
        complete = data[columns].dropna()
        values = complete if prefix == "rating" else len(columns) + 1 - complete
        chi2, p_value = stats.friedmanchisquare(*(values[column].to_numpy() for column in columns))
        omnibus_rows.append({
            "family": family, "n_complete": len(complete), "k": len(columns),
            "chi2": chi2, "df": len(columns) - 1, "p": p_value,
            "kendall_w": chi2 / (len(complete) * (len(columns) - 1)),
        })
        family_pairs = []
        for item_a, item_b in itertools.combinations(item_map, 2):
            column_a, column_b = f"{prefix}_{item_a}", f"{prefix}_{item_b}"
            paired = data[[column_a, column_b]].dropna()
            a = paired[column_a] if prefix == "rating" else len(columns) + 1 - paired[column_a]
            b = paired[column_b] if prefix == "rating" else len(columns) + 1 - paired[column_b]
            statistic, raw_p = stats.wilcoxon(a, b, zero_method="wilcox", alternative="two-sided", method="auto")
            family_pairs.append({
                "family": family, "item_a": item_a, "item_b": item_b,
                "n_pairs": len(paired), "mean_a": a.mean(), "mean_b": b.mean(),
                "median_a": a.median(), "median_b": b.median(),
                "mean_difference_a_minus_b": (a - b).mean(),
                "wilcoxon_w": statistic, "p_raw": raw_p,
                "rank_biserial_a_gt_b": rank_biserial_paired(a, b),
            })
        adjusted = holm([row["p_raw"] for row in family_pairs])
        for row, corrected in zip(family_pairs, adjusted):
            row["p_holm"] = corrected
            row["significant_holm_0.05"] = corrected < .05
        pairwise_rows.extend(family_pairs)
    return pd.DataFrame(omnibus_rows), pd.DataFrame(pairwise_rows)


def ranking_descriptives(data: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for family, item_map in ITEMS.items():
        k = len(item_map)
        for item_id, label in item_map.items():
            ranks = data[f"rank_{item_id}"].dropna()
            rows.append({
                "family": family, "item_id": item_id, "item": label, "n": len(ranks),
                "mean_rank": ranks.mean(), "median_rank": ranks.median(),
                "first_place_n": int((ranks == 1).sum()),
                "first_place_pct": 100 * (ranks == 1).mean(),
                "top3_n": int((ranks <= min(3, k)).sum()),
                "top3_pct": 100 * (ranks <= min(3, k)).mean(),
                "preference_score_mean": (k + 1 - ranks).mean(),
            })
    return pd.DataFrame(rows)


def rating_rank_coherence(data: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for family, item_map in ITEMS.items():
        rhos = []
        k = len(item_map)
        for _, participant in data.iterrows():
            ratings = np.array([participant[f"rating_{item_id}"] for item_id in item_map], dtype=float)
            preference = np.array([k + 1 - participant[f"rank_{item_id}"] for item_id in item_map], dtype=float)
            valid = ~(np.isnan(ratings) | np.isnan(preference))
            if valid.sum() >= 3 and len(np.unique(ratings[valid])) > 1:
                rhos.append(stats.spearmanr(ratings[valid], preference[valid]).statistic)
        rhos = pd.Series(rhos).dropna()
        statistic, p_value = stats.wilcoxon(rhos, alternative="greater", zero_method="wilcox", method="auto")
        rows.append({
            "family": family, "n_valid": len(rhos), "median_spearman": rhos.median(),
            "mean_spearman": rhos.mean(), "wilcoxon_greater_than_zero_w": statistic,
            "p_greater_than_zero": p_value,
        })
    return pd.DataFrame(rows)


def pairing_analysis(data: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    count_rows, test_rows = [], []
    gesture_ids = list(ITEMS["Gesture applicability"])
    for task, (column, expected) in PAIR_TASKS.items():
        counts = data[column].value_counts().reindex(gesture_ids, fill_value=0)
        chi2, p_value = stats.chisquare(counts.to_numpy())
        n = int(counts.sum())
        for gesture_id, count in counts.items():
            count_rows.append({"task": task, "gesture_id": gesture_id, "n": count, "pct": 100 * count / n})
        expected_count = int(counts[expected])
        binomial_p = stats.binomtest(expected_count, n, 1 / 9, alternative="greater").pvalue
        test_rows.append({
            "task": task, "n": n, "chi2": chi2, "df": 8, "p": p_value,
            "cohens_w": math.sqrt(chi2 / n), "expected_direct_match": expected,
            "expected_n": expected_count, "expected_pct": 100 * expected_count / n,
            "binomial_expected_vs_chance_p": binomial_p,
        })
    return pd.DataFrame(count_rows), pd.DataFrame(test_rows)


def add_composites(data: pd.DataFrame) -> pd.DataFrame:
    output = data.copy()
    for family, item_map in ITEMS.items():
        key = {"AR clarity": "ar", "Voice applicability": "voice", "Gesture applicability": "gesture"}[family]
        output[f"composite_{key}"] = output[[f"rating_{item_id}" for item_id in item_map]].mean(axis=1)
    return output


def participant_sensitivity(data: pd.DataFrame) -> pd.DataFrame:
    rows = []
    outcomes = {"AR clarity": "composite_ar", "Voice applicability": "composite_voice", "Gesture applicability": "composite_gesture"}
    for factor in ("gender", "language"):
        levels = list(data[factor].value_counts().index)
        if len(levels) != 2:
            continue
        factor_rows = []
        for outcome, column in outcomes.items():
            a, b = (data.loc[data[factor] == level, column].dropna() for level in levels)
            statistic, p_value = stats.mannwhitneyu(a, b, alternative="two-sided")
            factor_rows.append({
                "factor": factor, "outcome": outcome, "test": "Mann-Whitney U",
                "group_a": levels[0], "n_a": len(a), "group_b": levels[1], "n_b": len(b),
                "statistic": statistic, "df": np.nan, "p_raw": p_value,
                "effect_size": 2 * statistic / (len(a) * len(b)) - 1,
            })
        corrected = benjamini_hochberg([row["p_raw"] for row in factor_rows])
        for row, value in zip(factor_rows, corrected): row["p_bh_fdr"] = value
        rows.extend(factor_rows)

    age_rows = []
    eligible = [name for name, group in data.groupby("age_group") if len(group) >= 5]
    for outcome, column in outcomes.items():
        groups = [data.loc[data.age_group == name, column].dropna() for name in eligible]
        statistic, p_value = stats.kruskal(*groups)
        n, k = sum(map(len, groups)), len(groups)
        age_rows.append({
            "factor": "age_group", "outcome": outcome, "test": "Kruskal-Wallis",
            "group_a": "; ".join(eligible), "n_a": n, "group_b": "", "n_b": np.nan,
            "statistic": statistic, "df": k - 1, "p_raw": p_value,
            "effect_size": max(0, (statistic - k + 1) / (n - k)),
        })
    corrected = benjamini_hochberg([row["p_raw"] for row in age_rows])
    for row, value in zip(age_rows, corrected): row["p_bh_fdr"] = value
    rows.extend(age_rows)
    return pd.DataFrame(rows)


def age_posthoc(data: pd.DataFrame) -> pd.DataFrame:
    rows = []
    outcomes = {"AR clarity": "composite_ar", "Voice applicability": "composite_voice", "Gesture applicability": "composite_gesture"}
    eligible = {name: group for name, group in data.groupby("age_group") if len(group) >= 5}
    for outcome, column in outcomes.items():
        outcome_rows = []
        for group_a, group_b in itertools.combinations(eligible, 2):
            a, b = eligible[group_a][column].dropna(), eligible[group_b][column].dropna()
            statistic, p_value = stats.mannwhitneyu(a, b, alternative="two-sided")
            outcome_rows.append({
                "outcome": outcome, "group_a": group_a, "group_b": group_b,
                "n_a": len(a), "n_b": len(b), "median_a": a.median(), "median_b": b.median(),
                "mann_whitney_u": statistic, "p_raw": p_value,
                "cliffs_delta_a_gt_b": 2 * statistic / (len(a) * len(b)) - 1,
            })
        corrected = holm([row["p_raw"] for row in outcome_rows])
        for row, value in zip(outcome_rows, corrected):
            row["p_holm_within_outcome"] = value
            row["significant_holm_0.05"] = value < .05
        rows.extend(outcome_rows)
    return pd.DataFrame(rows)


def ati_correlations(data: pd.DataFrame) -> pd.DataFrame:
    ati = data[[f"ATI_{number}" for number in range(1, 10)]].mean(axis=1)
    rows = []
    for family, item_map in ITEMS.items():
        for item_id in item_map:
            paired = pd.concat([ati, data[f"rating_{item_id}"]], axis=1).dropna()
            result = stats.spearmanr(paired.iloc[:, 0], paired.iloc[:, 1])
            rows.append({"family": family, "item_id": item_id, "n": len(paired), "rho": result.statistic, "p_raw": result.pvalue})
    corrected = benjamini_hochberg([row["p_raw"] for row in rows])
    for row, value in zip(rows, corrected): row["p_bh_fdr"] = value
    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=Path(__file__).resolve().parents[1] / "data" / "survey_responses_anonymized.csv")
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parents[1] / "results")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    data = pd.read_csv(args.data)
    if len(data) != 124 or data.participant_id.nunique() != 124:
        raise ValueError("Expected 124 unique anonymized participants")
    scored = add_composites(data)

    likert_omnibus, likert_pairwise = omnibus_and_pairwise(scored, "rating")
    rank_omnibus, rank_pairwise = omnibus_and_pairwise(scored, "rank")
    pair_counts, pair_tests = pairing_analysis(scored)
    tables = {
        "likert_descriptives.csv": item_descriptives(scored),
        "likert_omnibus_friedman.csv": likert_omnibus,
        "likert_pairwise_wilcoxon_holm.csv": likert_pairwise,
        "ranking_descriptives.csv": ranking_descriptives(scored),
        "ranking_omnibus_friedman.csv": rank_omnibus,
        "ranking_pairwise_wilcoxon_holm.csv": rank_pairwise,
        "rating_rank_coherence.csv": rating_rank_coherence(scored),
        "gesture_match_counts.csv": pair_counts,
        "gesture_match_tests.csv": pair_tests,
        "participant_sensitivity_checks.csv": participant_sensitivity(scored),
        "age_posthoc_mannwhitney_holm.csv": age_posthoc(scored),
        "ati_rating_spearman_fdr.csv": ati_correlations(scored),
    }
    for filename, table in tables.items(): table.to_csv(args.output / filename, index=False)

    summary = {
        "n": len(scored),
        "language_counts": scored.language.value_counts().to_dict(),
        "gender_counts": scored.gender.value_counts().to_dict(),
        "age_counts": scored.age_group.value_counts().to_dict(),
    }
    (args.output / "survey_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
