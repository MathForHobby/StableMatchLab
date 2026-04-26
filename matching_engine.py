import itertools
import random
from typing import Dict, List, Tuple, Any


Matching = Dict[str, str]
Preferences = Dict[str, List[str]]


MALE_KOREAN_NAMES = [
    "민준", "서준", "도윤", "예준", "시우", "하준", "주원", "지호",
    "지후", "준우", "현우", "도현", "건우", "우진", "선우", "유준",
    "은우", "연우", "이준", "지안"
]

FEMALE_KOREAN_NAMES = [
    "서연", "서윤", "지우", "하은", "민서", "지유", "윤서", "채원",
    "수아", "지아", "지민", "은서", "예은", "다은", "하윤", "소율",
    "예린", "유나", "나은", "서현"
]


def generate_people(n: int, seed: int | None = None) -> Tuple[List[str], List[str]]:
    """Generate Korean display names for both sides."""
    rng = random.Random(seed)

    if n > len(MALE_KOREAN_NAMES) or n > len(FEMALE_KOREAN_NAMES):
        raise ValueError("n is larger than the prepared Korean name pool.")

    men = rng.sample(MALE_KOREAN_NAMES, n)
    women = rng.sample(FEMALE_KOREAN_NAMES, n)

    return men, women


def generate_preferences(
    n: int,
    seed: int | None = None,
    name_seed: int | None = None,
) -> Tuple[List[str], List[str], Preferences, Preferences]:
    """
    Generate random complete preference rankings for a balanced two-sided matching problem.

    - name_seed controls the Korean names.
    - seed controls the preference order.
    This lets the UI reshuffle preferences while keeping the same people.
    """
    rng = random.Random(seed)

    men, women = generate_people(n, seed=name_seed)

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
        return False, "왼쪽 그룹의 모든 사람이 매칭되어야 합니다."

    selected = list(matching.values())
    if any(w not in women for w in selected):
        return False, "선택한 상대 중 올바르지 않은 항목이 있습니다."

    if len(selected) != len(women):
        return False, "아직 매칭되지 않은 사람이 있습니다."

    if len(set(selected)) != len(selected):
        return False, "오른쪽 그룹의 한 사람이 두 번 이상 매칭되었습니다."

    return True, "완전한 1:1 매칭입니다."


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
            log.append(f"{m}은/는 모든 사람에게 제안했지만 매칭되지 않았습니다.")
            continue

        w = men_prefs[m][next_choice_index[m]]
        next_choice_index[m] += 1

        log.append(f"{round_no}단계: {m}이/가 {w}에게 제안합니다.")

        if w not in held_by_woman:
            held_by_woman[w] = m
            log.append(f"{w}은/는 아직 제안을 보류 중인 상대가 없으므로 {m}의 제안을 임시로 받아들입니다.")
        else:
            current_m = held_by_woman[w]

            if women_rank[w][m] < women_rank[w][current_m]:
                held_by_woman[w] = m
                free_men.append(current_m)
                log.append(f"{w}은/는 {current_m}보다 {m}을/를 더 선호하므로 {m}을/를 보류하고 {current_m}을/를 거절합니다.")
            else:
                free_men.append(m)
                log.append(f"{w}은/는 현재 보류 중인 {current_m}을/를 더 선호하므로 {m}을/를 거절합니다.")

        round_no += 1

    matching = {m: w for w, m in held_by_woman.items()}
    return matching, log


def matching_equals(a: Matching, b: Matching) -> bool:
    return a == b


def explain_matching(matching: Matching) -> str:
    return ", ".join([f"{m}↔{w}" for m, w in sorted(matching.items())])
