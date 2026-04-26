import itertools
import random
from typing import Dict, List, Tuple, Any


Matching = Dict[str, str]
Preferences = Dict[str, List[str]]


def generate_preferences(n: int, seed: int | None = None) -> Tuple[List[str], List[str], Preferences, Preferences]:
    """Generate random complete preference rankings for a balanced two-sided matching problem."""
    rng = random.Random(seed)

    men = [f"M{i+1}" for i in range(n)]
    women = [f"W{i+1}" for i in range(n)]

    men_prefs: Preferences = {}
    women_prefs: Preferences = {}

    for m in men:
        prefs = women[:]
        rng.shuffle(prefs)
        men_prefs[m] = prefs

    for w in women:
        prefs = men[:]
        rng.shuffle(prefs)
        women_prefs[w] = prefs

    return men, women, men_prefs, women_prefs


def make_rankings(prefs: Preferences) -> Dict[str, Dict[str, int]]:
    """Convert preference lists into rank maps. Lower rank is better."""
    return {
        person: {candidate: rank for rank, candidate in enumerate(pref_list)}
        for person, pref_list in prefs.items()
    }


def is_complete_one_to_one(matching: Matching, men: List[str], women: List[str]) -> Tuple[bool, str]:
    """Check whether every man is matched to a distinct woman."""
    if set(matching.keys()) != set(men):
        return False, "Every participant on the left side must be matched."

    selected = list(matching.values())
    if any(w not in women for w in selected):
        return False, "Some selected partners are invalid."

    if len(selected) != len(women):
        return False, "The matching is incomplete."

    if len(set(selected)) != len(selected):
        return False, "One participant on the right side is matched more than once."

    return True, "Complete one-to-one matching."


def invert_matching(matching: Matching) -> Dict[str, str]:
    return {w: m for m, w in matching.items()}


def find_blocking_pairs(
    matching: Matching,
    men_prefs: Preferences,
    women_prefs: Preferences,
) -> List[Dict[str, Any]]:
    """
    Return all blocking pairs.

    A pair (m, w) blocks the matching if:
    - m prefers w to his current partner, and
    - w prefers m to her current partner.
    """
    men_rank = make_rankings(men_prefs)
    women_rank = make_rankings(women_prefs)
    woman_to_man = invert_matching(matching)

    blocking_pairs: List[Dict[str, Any]] = []

    for m, current_w in matching.items():
        for w in men_prefs[m]:
            if w == current_w:
                break

            current_m = woman_to_man[w]

            man_prefers_w = men_rank[m][w] < men_rank[m][current_w]
            woman_prefers_m = women_rank[w][m] < women_rank[w][current_m]

            if man_prefers_w and woman_prefers_m:
                blocking_pairs.append(
                    {
                        "man": m,
                        "woman": w,
                        "man_current": current_w,
                        "woman_current": current_m,
                        "man_current_rank": men_rank[m][current_w] + 1,
                        "man_new_rank": men_rank[m][w] + 1,
                        "woman_current_rank": women_rank[w][current_m] + 1,
                        "woman_new_rank": women_rank[w][m] + 1,
                    }
                )

    return blocking_pairs


def is_stable(matching: Matching, men_prefs: Preferences, women_prefs: Preferences) -> bool:
    return len(find_blocking_pairs(matching, men_prefs, women_prefs)) == 0


def satisfaction_score(matching: Matching, men_prefs: Preferences, women_prefs: Preferences) -> int:
    """
    Higher is better.

    If there are n partners on each side:
    - 1st choice gives n points
    - 2nd choice gives n-1 points
    - ...
    - nth choice gives 1 point
    """
    n = len(matching)
    men_rank = make_rankings(men_prefs)
    women_rank = make_rankings(women_prefs)
    woman_to_man = invert_matching(matching)

    score = 0

    for m, w in matching.items():
        score += n - men_rank[m][w]

    for w, m in woman_to_man.items():
        score += n - women_rank[w][m]

    return score


def all_matchings(men: List[str], women: List[str]) -> List[Matching]:
    return [dict(zip(men, perm)) for perm in itertools.permutations(women)]


def stable_matchings(men: List[str], women: List[str], men_prefs: Preferences, women_prefs: Preferences) -> List[Matching]:
    return [
        matching
        for matching in all_matchings(men, women)
        if is_stable(matching, men_prefs, women_prefs)
    ]


def find_best_stable_matching(
    men: List[str],
    women: List[str],
    men_prefs: Preferences,
    women_prefs: Preferences,
) -> Tuple[Matching | None, int | None, List[Matching]]:
    """Find the stable matching with the highest total satisfaction score."""
    candidates = stable_matchings(men, women, men_prefs, women_prefs)

    if not candidates:
        return None, None, []

    scored = [(satisfaction_score(m, men_prefs, women_prefs), m) for m in candidates]
    best_score = max(score for score, _ in scored)
    best = [m for score, m in scored if score == best_score]

    return best[0], best_score, best


def gale_shapley_men_propose(
    men: List[str],
    women: List[str],
    men_prefs: Preferences,
    women_prefs: Preferences,
) -> Tuple[Matching, List[str]]:
    """Run the classic men-proposing Gale-Shapley algorithm."""
    women_rank = make_rankings(women_prefs)

    free_men = men[:]
    next_choice_index = {m: 0 for m in men}
    held_by_woman: Dict[str, str] = {}
    log: List[str] = []

    round_no = 1

    while free_men:
        m = free_men.pop(0)

        if next_choice_index[m] >= len(women):
            log.append(f"{m} has proposed to everyone and remains unmatched.")
            continue

        w = men_prefs[m][next_choice_index[m]]
        next_choice_index[m] += 1

        log.append(f"Round {round_no}: {m} proposes to {w}.")

        if w not in held_by_woman:
            held_by_woman[w] = m
            log.append(f"{w} is free, so {w} tentatively accepts {m}.")
        else:
            current_m = held_by_woman[w]

            if women_rank[w][m] < women_rank[w][current_m]:
                held_by_woman[w] = m
                free_men.append(current_m)
                log.append(f"{w} prefers {m} over {current_m}, so {w} keeps {m} and rejects {current_m}.")
            else:
                free_men.append(m)
                log.append(f"{w} prefers current partner {current_m}, so {w} rejects {m}.")

        round_no += 1

    matching = {m: w for w, m in held_by_woman.items()}
    return matching, log


def matching_equals(a: Matching, b: Matching) -> bool:
    return a == b


def explain_matching(matching: Matching) -> str:
    return ", ".join([f"{m}↔{w}" for m, w in sorted(matching.items())])
