import html
import itertools
import random
import streamlit as st


# ============================================================
# Stable Match Lab v2.2
# Single-file fixed version
# 핵심 로직을 app.py 안에 넣어서 matching_engine.py 버전 불일치 문제를 제거했습니다.
# ============================================================

st.set_page_config(
    page_title="Stable Match Lab",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="collapsed",
)


MALE_KOREAN_NAMES = [
    "민준", "서준", "도윤", "예준", "시우", "하준", "주원", "지호",
    "지후", "준우", "현우", "도현", "건우", "우진", "선우", "유준",
    "은우", "연우", "이준", "지안", "태오", "윤재", "서진", "재원"
]

FEMALE_KOREAN_NAMES = [
    "서연", "서윤", "지우", "하은", "민서", "지유", "윤서", "채원",
    "수아", "지아", "지민", "은서", "예은", "다은", "하윤", "소율",
    "예린", "유나", "나은", "서현", "아린", "유진", "다연", "채은"
]


def generate_people(n: int, seed: int | None = None):
    rng = random.Random(seed)
    men = rng.sample(MALE_KOREAN_NAMES, n)
    women = rng.sample(FEMALE_KOREAN_NAMES, n)
    return men, women


def generate_preferences(n: int, seed: int | None = None, name_seed: int | None = None):
    rng = random.Random(seed)
    men, women = generate_people(n, seed=name_seed)

    men_prefs = {}
    women_prefs = {}

    for m in men:
        prefs = women[:]
        rng.shuffle(prefs)
        men_prefs[m] = prefs

    for w in women:
        prefs = men[:]
        rng.shuffle(prefs)
        women_prefs[w] = prefs

    return men, women, men_prefs, women_prefs


def make_rankings(prefs):
    return {
        person: {candidate: rank for rank, candidate in enumerate(pref_list)}
        for person, pref_list in prefs.items()
    }


def invert_matching(matching):
    return {w: m for m, w in matching.items()}


def is_complete_one_to_one(matching, men, women):
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


def find_blocking_pairs(matching, men_prefs, women_prefs):
    men_rank = make_rankings(men_prefs)
    women_rank = make_rankings(women_prefs)
    woman_to_man = invert_matching(matching)

    blocking_pairs = []

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


def is_stable(matching, men_prefs, women_prefs):
    return len(find_blocking_pairs(matching, men_prefs, women_prefs)) == 0


def satisfaction_score(matching, men_prefs, women_prefs):
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


def all_matchings(men, women):
    return [dict(zip(men, perm)) for perm in itertools.permutations(women)]


def stable_matchings(men, women, men_prefs, women_prefs):
    return [
        matching
        for matching in all_matchings(men, women)
        if is_stable(matching, men_prefs, women_prefs)
    ]


def find_best_stable_matching(men, women, men_prefs, women_prefs):
    candidates = stable_matchings(men, women, men_prefs, women_prefs)

    if not candidates:
        return None, None, []

    scored = [(satisfaction_score(m, men_prefs, women_prefs), m) for m in candidates]
    best_score = max(score for score, _ in scored)
    best = [m for score, m in scored if score == best_score]

    return best[0], best_score, best


def gale_shapley_men_propose(men, women, men_prefs, women_prefs):
    women_rank = make_rankings(women_prefs)

    free_men = men[:]
    next_choice_index = {m: 0 for m in men}
    held_by_woman = {}
    log = []

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
            log.append(f"{w}은/는 아직 보류 중인 상대가 없으므로 {m}의 제안을 임시로 받아들입니다.")
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


def explain_matching(matching):
    return ", ".join([f"{m}↔{w}" for m, w in sorted(matching.items())])


CSS = """
<style>
:root {
    --bg: #f6f7fb;
    --card: #ffffff;
    --ink: #172033;
    --muted: #64748b;
    --line: #e5e7eb;
    --blue: #2563eb;
    --blue-soft: #eff6ff;
    --green: #16a34a;
    --green-soft: #ecfdf5;
    --red: #dc2626;
    --red-soft: #fef2f2;
    --amber: #d97706;
    --amber-soft: #fffbeb;
    --purple: #7c3aed;
    --purple-soft: #f5f3ff;
}

.block-container {
    padding-top: 1.4rem;
    padding-bottom: 3rem;
    max-width: 1200px;
}

div[data-testid="stVerticalBlock"] {
    gap: 0.85rem;
}

.sml-hero {
    padding: 2.1rem 2.2rem;
    border-radius: 28px;
    background: radial-gradient(circle at top left, #dbeafe 0, transparent 30%),
                radial-gradient(circle at bottom right, #ede9fe 0, transparent 32%),
                linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
    border: 1px solid #e5e7eb;
    box-shadow: 0 18px 45px rgba(15, 23, 42, 0.08);
    margin-bottom: 1.2rem;
}

.sml-title {
    font-size: 3.2rem;
    line-height: 1.05;
    font-weight: 850;
    letter-spacing: -0.06em;
    color: var(--ink);
    margin: 0 0 0.6rem 0;
}

.sml-subtitle {
    font-size: 1.08rem;
    color: var(--muted);
    max-width: 760px;
    margin: 0;
}

.stage-card {
    min-height: 275px;
    padding: 1.35rem;
    border-radius: 24px;
    background: var(--card);
    border: 1px solid var(--line);
    box-shadow: 0 10px 30px rgba(15, 23, 42, 0.06);
}

.stage-card h3 {
    margin: 0.45rem 0 0.45rem 0;
    letter-spacing: -0.03em;
    font-size: 1.35rem;
}

.stage-icon {
    width: 42px;
    height: 42px;
    border-radius: 16px;
    display: grid;
    place-items: center;
    font-size: 1.35rem;
    background: var(--blue-soft);
}

.stage-meta {
    display: inline-flex;
    gap: 0.35rem;
    align-items: center;
    color: var(--muted);
    font-size: 0.88rem;
    margin: 0.35rem 0 0.7rem 0;
}

.pill {
    display: inline-flex;
    align-items: center;
    border-radius: 999px;
    padding: 0.22rem 0.58rem;
    font-size: 0.78rem;
    font-weight: 700;
    margin: 0.16rem 0.18rem 0.16rem 0;
    border: 1px solid transparent;
}

.pill-blue { background: var(--blue-soft); color: var(--blue); border-color: #bfdbfe; }
.pill-green { background: var(--green-soft); color: var(--green); border-color: #bbf7d0; }
.pill-red { background: var(--red-soft); color: var(--red); border-color: #fecaca; }
.pill-amber { background: var(--amber-soft); color: var(--amber); border-color: #fde68a; }
.pill-purple { background: var(--purple-soft); color: var(--purple); border-color: #ddd6fe; }
.pill-gray { background: #f8fafc; color: #475569; border-color: #e2e8f0; }

.section-title {
    font-size: 1.3rem;
    font-weight: 850;
    color: var(--ink);
    letter-spacing: -0.03em;
    margin: 0.4rem 0 0.5rem 0;
}

.person-card {
    border-radius: 22px;
    background: white;
    border: 1px solid var(--line);
    padding: 1rem;
    box-shadow: 0 8px 24px rgba(15, 23, 42, 0.045);
    margin-bottom: 0.7rem;
}

.person-card.danger {
    border-color: #fecaca;
    box-shadow: 0 12px 26px rgba(220, 38, 38, 0.09);
    background: linear-gradient(180deg, #fff 0%, #fff7f7 100%);
}

.person-head {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.55rem;
}

.person-name {
    font-size: 1.05rem;
    font-weight: 850;
    color: var(--ink);
}

.avatar {
    width: 34px;
    height: 34px;
    border-radius: 14px;
    display: grid;
    place-items: center;
    background: #f1f5f9;
}

.pref-list {
    display: grid;
    gap: 0.34rem;
}

.pref-row {
    display: flex;
    align-items: center;
    gap: 0.45rem;
    font-size: 0.88rem;
    color: #334155;
}

.rank-dot {
    width: 1.65rem;
    height: 1.65rem;
    border-radius: 999px;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    display: grid;
    place-items: center;
    font-size: 0.78rem;
    font-weight: 800;
    color: #475569;
}

.match-board {
    border-radius: 26px;
    border: 1px solid var(--line);
    background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
    padding: 1rem;
    box-shadow: 0 10px 30px rgba(15, 23, 42, 0.055);
}

.pair-chip {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    padding: 0.72rem 0.9rem;
    border-radius: 18px;
    border: 1px solid #dbeafe;
    background: #eff6ff;
    color: #1e3a8a;
    margin-bottom: 0.55rem;
    font-weight: 780;
}

.pair-chip.pending {
    border-color: #e5e7eb;
    background: #f8fafc;
    color: #64748b;
}

.feedback-card {
    border-radius: 24px;
    padding: 1.05rem;
    border: 1px solid var(--line);
    background: white;
    box-shadow: 0 10px 30px rgba(15, 23, 42, 0.05);
}

.feedback-card.success {
    border-color: #bbf7d0;
    background: linear-gradient(180deg, #ffffff 0%, #f0fdf4 100%);
}

.feedback-card.fail {
    border-color: #fecaca;
    background: linear-gradient(180deg, #ffffff 0%, #fef2f2 100%);
}

.feedback-card.info {
    border-color: #bfdbfe;
    background: linear-gradient(180deg, #ffffff 0%, #eff6ff 100%);
}

.metric-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 0.55rem;
}

.metric-box {
    border-radius: 18px;
    border: 1px solid #e2e8f0;
    background: #f8fafc;
    padding: 0.8rem;
}

.metric-label {
    color: #64748b;
    font-size: 0.78rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}

.metric-value {
    color: #0f172a;
    font-size: 1.35rem;
    font-weight: 850;
}

.help-box {
    border: 1px dashed #cbd5e1;
    border-radius: 22px;
    padding: 1rem;
    background: #f8fafc;
    color: #334155;
}

.small-muted {
    color: var(--muted);
    font-size: 0.92rem;
}

.gs-log {
    border-radius: 18px;
    background: #0f172a;
    color: #e2e8f0;
    padding: 1rem;
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    font-size: 0.84rem;
    line-height: 1.7;
    max-height: 420px;
    overflow-y: auto;
}
</style>
"""


def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)


def esc(x):
    return html.escape(str(x))


def init_state():
    defaults = {
        "view": "home",
        "stage": 1,
        "pref_seed": 100,
        "name_seed": 777,
        "n": 4,
        "submitted": False,
        "show_solution": False,
        "show_hint": False,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def clear_choice_state():
    keys_to_delete = [key for key in st.session_state.keys() if key.startswith("match_")]
    for key in keys_to_delete:
        del st.session_state[key]

    st.session_state.submitted = False
    st.session_state.show_solution = False
    st.session_state.show_hint = False


def start_stage(stage: int):
    st.session_state.stage = stage
    st.session_state.view = "game"
    clear_choice_state()
    st.rerun()


def new_puzzle():
    st.session_state.pref_seed += 1
    st.session_state.name_seed += 1
    clear_choice_state()
    st.rerun()


def reshuffle_preferences():
    st.session_state.pref_seed += 1
    clear_choice_state()
    st.rerun()


def back_home():
    st.session_state.view = "home"
    clear_choice_state()
    st.rerun()


STAGE_INFO = {
    1: {
        "title": "1단계 — 안정 매칭",
        "short": "Blocking pair가 없도록 1:1 매칭을 만드세요.",
        "goal": "모든 사람을 1:1로 연결하되, 서로 현재 파트너보다 더 선호하는 두 사람이 생기지 않도록 만드세요.",
        "clear": "성공 조건: 완전한 1:1 매칭 + blocking pair 0개",
        "difficulty": "입문",
        "icon": "🧩",
        "tag": "안정성",
        "button": "1단계 플레이",
    },
    2: {
        "title": "2단계 — 최적 안정 매칭",
        "short": "안정 매칭 중 전체 만족도 점수가 가장 높은 매칭을 찾으세요.",
        "goal": "안정 매칭은 여러 개일 수 있습니다. 그중 참가자들의 전체 만족도 점수가 가장 높은 매칭을 찾으세요.",
        "clear": "성공 조건: 안정 매칭 + 최고 만족도 점수",
        "difficulty": "중급",
        "icon": "🎯",
        "tag": "최적성",
        "button": "2단계 플레이",
    },
    3: {
        "title": "3단계 — 게일-섀플리 챌린지",
        "short": "남성 제안형 Gale-Shapley 알고리즘의 결과를 예측하세요.",
        "goal": "선호표를 보고, 남성들이 차례로 제안할 때 Gale-Shapley 알고리즘이 만드는 최종 매칭을 예측하세요.",
        "clear": "성공 조건: 알고리즘 결과와 정확히 같은 매칭",
        "difficulty": "고급",
        "icon": "⚙️",
        "tag": "알고리즘",
        "button": "3단계 플레이",
    },
}


def stage_card(stage: int):
    info = STAGE_INFO[stage]
    st.markdown(
        f"""
        <div class="stage-card">
            <div class="stage-icon">{info["icon"]}</div>
            <h3>{info["title"]}</h3>
            <div class="stage-meta">
                <span class="pill pill-blue">{info["tag"]}</span>
                <span class="pill pill-gray">{info["difficulty"]}</span>
            </div>
            <p class="small-muted">{info["short"]}</p>
            <div class="help-box" style="margin-top:0.8rem;">
                <b>목표</b><br/>
                {info["goal"]}<br/><br/>
                <b>성공 조건</b><br/>
                {info["clear"]}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button(info["button"], key=f"play_stage_{stage}", use_container_width=True):
        start_stage(stage)


def render_home():
    st.markdown(
        """
        <div class="sml-hero">
            <div class="sml-title">Stable Match Lab</div>
            <p class="sml-subtitle">
                매칭 이론을 게임처럼 익히는 작은 퍼즐 실험실입니다.
                직접 매칭을 만들고, blocking pair를 피하고,
                최적 안정 매칭과 Gale-Shapley 알고리즘의 결과를 탐구해보세요.
            </p>
            <div style="margin-top:1rem;">
                <span class="pill pill-blue">매칭 이론</span>
                <span class="pill pill-green">퍼즐 학습</span>
                <span class="pill pill-purple">한국어 UI</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        stage_card(1)
    with col2:
        stage_card(2)
    with col3:
        stage_card(3)

    st.markdown("<br/>", unsafe_allow_html=True)
    with st.expander("매칭 이론 빠른 설명"):
        st.markdown(
            """
            **안정 매칭 stable matching**은 현재 매칭을 깨고 서로 새롭게 짝을 이루고 싶어 하는 두 사람이 없는 매칭입니다.

            **Blocking pair**는 서로 현재 파트너보다 상대방을 더 선호하는 한 쌍입니다. Blocking pair가 하나라도 있으면 현재 매칭은 불안정합니다.

            **최적 안정 매칭**은 먼저 안정 매칭이어야 하고, 그 안정 매칭들 중 전체 만족도 점수가 가장 높은 매칭입니다.

            **Gale-Shapley 알고리즘**은 안정 매칭을 찾는 대표적인 알고리즘입니다. 이 앱의 3단계에서는 남성 제안형 Gale-Shapley 알고리즘의 결과를 예측합니다.
            """
        )


def rank_badge(rank: int):
    if rank == 1:
        return "🥇"
    if rank == 2:
        return "🥈"
    if rank == 3:
        return "🥉"
    return str(rank)


def render_person_card(name: str, prefs: list[str], danger: bool = False, side: str = "M"):
    danger_class = " danger" if danger else ""
    avatar = "👨‍🔬" if side == "M" else "👩‍🔬"

    rows = "".join(
        [
            (
                f'<div class="pref-row">'
                f'<div class="rank-dot">{rank_badge(idx)}</div>'
                f'<div>{esc(partner)}</div>'
                f'</div>'
            )
            for idx, partner in enumerate(prefs, start=1)
        ]
    )

    card_html = (
        f'<div class="person-card{danger_class}">'
        f'<div class="person-head">'
        f'<div class="person-name">{esc(name)}</div>'
        f'<div class="avatar">{avatar}</div>'
        f'</div>'
        f'<div class="pref-list">{rows}</div>'
        f'</div>'
    )

    st.markdown(card_html, unsafe_allow_html=True)


def render_preferences(men, women, men_prefs, women_prefs, highlighted_men=None, highlighted_women=None):
    highlighted_men = highlighted_men or set()
    highlighted_women = highlighted_women or set()

    st.markdown('<div class="section-title">선호도 카드</div>', unsafe_allow_html=True)
    col_m, col_w = st.columns(2)

    with col_m:
        st.markdown('<span class="pill pill-blue">남성</span>', unsafe_allow_html=True)
        for m in men:
            render_person_card(m, men_prefs[m], danger=m in highlighted_men, side="M")

    with col_w:
        st.markdown('<span class="pill pill-purple">여성</span>', unsafe_allow_html=True)
        for w in women:
            render_person_card(w, women_prefs[w], danger=w in highlighted_women, side="W")


def render_stage_explanation(stage: int):
    info = STAGE_INFO[stage]
    st.markdown(
        f"""
        <div class="feedback-card info">
            <span class="pill pill-blue">{info["difficulty"]}</span>
            <span class="pill pill-purple">{info["tag"]}</span>
            <h3 style="margin:0.4rem 0 0.4rem 0;">{info["title"]}</h3>
            <p style="margin-bottom:0.5rem;">{info["goal"]}</p>
            <b>{info["clear"]}</b>
        </div>
        """,
        unsafe_allow_html=True,
    )


def widget_key(m):
    return f"match_{st.session_state.stage}_{st.session_state.pref_seed}_{st.session_state.name_seed}_{m}"


def get_matching_from_widgets(men, women):
    matching = {}
    for m in men:
        selected = st.session_state.get(widget_key(m), "—")
        if selected != "—":
            matching[m] = selected
    return matching


def render_matching_inputs(men, women):
    st.markdown('<div class="section-title">매칭 만들기</div>', unsafe_allow_html=True)

    left, right = st.columns([0.95, 1.05])

    with left:
        st.markdown('<div class="match-board">', unsafe_allow_html=True)
        for m in men:
            st.selectbox(
                f"{m} ↔",
                ["—"] + women,
                key=widget_key(m),
                label_visibility="visible",
            )
        st.markdown("</div>", unsafe_allow_html=True)

    matching = get_matching_from_widgets(men, women)

    with right:
        st.markdown('<div class="match-board">', unsafe_allow_html=True)
        st.markdown("<b>현재 매칭 보드</b>", unsafe_allow_html=True)

        for m in men:
            w = matching.get(m)
            if w:
                st.markdown(f'<div class="pair-chip"><span>{esc(m)}</span><span>↔</span><span>{esc(w)}</span></div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="pair-chip pending"><span>{esc(m)}</span><span>↔</span><span>아직 매칭 안 됨</span></div>', unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    return matching


def render_metrics(matching, men_prefs, women_prefs, best_score=None, gs_target=None):
    complete_count = len(matching)
    n = len(men_prefs)

    score_text = "—"
    if complete_count == n and len(set(matching.values())) == n:
        score_text = str(satisfaction_score(matching, men_prefs, women_prefs))

    best_text = "—" if best_score is None else str(best_score)
    target_text = "숨김" if gs_target is not None else "—"

    st.markdown(
        f"""
        <div class="metric-grid">
            <div class="metric-box">
                <div class="metric-label">매칭 완료</div>
                <div class="metric-value">{complete_count}/{n}</div>
            </div>
            <div class="metric-box">
                <div class="metric-label">내 점수</div>
                <div class="metric-value">{score_text}</div>
            </div>
            <div class="metric-box">
                <div class="metric-label">최고 안정 점수</div>
                <div class="metric-value">{best_text}</div>
            </div>
            <div class="metric-box">
                <div class="metric-label">GS 정답</div>
                <div class="metric-value">{target_text}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_blocking_pair_details(blocking_pairs):
    st.markdown("**발견된 blocking pair:**")
    for bp in blocking_pairs:
        st.markdown(
            f"""
            <div class="feedback-card fail" style="margin-bottom:0.6rem;">
                <span class="pill pill-red">{esc(bp["man"])} ↔ {esc(bp["woman"])}</span><br/>
                {esc(bp["man"])}은/는 현재 상대 {esc(bp["man_current"])}을/를 #{bp["man_current_rank"]}순위로 생각하지만,
                {esc(bp["woman"])}을/를 #{bp["man_new_rank"]}순위로 더 선호합니다.<br/>
                {esc(bp["woman"])}은/는 현재 상대 {esc(bp["woman_current"])}을/를 #{bp["woman_current_rank"]}순위로 생각하지만,
                {esc(bp["man"])}을/를 #{bp["woman_new_rank"]}순위로 더 선호합니다.
            </div>
            """,
            unsafe_allow_html=True,
        )


def evaluate_submission(stage, matching, men, women, men_prefs, women_prefs):
    complete, message = is_complete_one_to_one(matching, men, women)
    if not complete:
        return {
            "ok": False,
            "kind": "incomplete",
            "title": "완전한 1:1 매칭이 아닙니다",
            "message": message,
            "blocking_pairs": [],
            "score": None,
            "best_score": None,
            "best_matching": None,
            "gs_matching": None,
            "gs_log": [],
        }

    blocking_pairs = find_blocking_pairs(matching, men_prefs, women_prefs)
    score = satisfaction_score(matching, men_prefs, women_prefs)
    best_matching, best_score, _ = find_best_stable_matching(men, women, men_prefs, women_prefs)
    gs_matching, gs_log = gale_shapley_men_propose(men, women, men_prefs, women_prefs)

    if stage == 1:
        if not blocking_pairs:
            return {
                "ok": True,
                "kind": "stable",
                "title": "성공! 안정 매칭입니다.",
                "message": "Blocking pair가 하나도 없습니다.",
                "blocking_pairs": [],
                "score": score,
                "best_score": best_score,
                "best_matching": best_matching,
                "gs_matching": gs_matching,
                "gs_log": gs_log,
            }
        return {
            "ok": False,
            "kind": "blocking",
            "title": "불안정한 매칭입니다",
            "message": "Blocking pair가 존재합니다.",
            "blocking_pairs": blocking_pairs,
            "score": score,
            "best_score": best_score,
            "best_matching": best_matching,
            "gs_matching": gs_matching,
            "gs_log": gs_log,
        }

    if stage == 2:
        if blocking_pairs:
            return {
                "ok": False,
                "kind": "blocking",
                "title": "아직 안정 매칭이 아닙니다",
                "message": "2단계에서는 먼저 blocking pair를 모두 없앤 뒤, 그중 가장 높은 만족도 점수를 찾아야 합니다.",
                "blocking_pairs": blocking_pairs,
                "score": score,
                "best_score": best_score,
                "best_matching": best_matching,
                "gs_matching": gs_matching,
                "gs_log": gs_log,
            }

        if score == best_score:
            return {
                "ok": True,
                "kind": "optimal",
                "title": "완벽합니다! 최적 안정 매칭입니다.",
                "message": f"내 점수 {score}점이 가능한 최고 안정 점수와 같습니다.",
                "blocking_pairs": [],
                "score": score,
                "best_score": best_score,
                "best_matching": best_matching,
                "gs_matching": gs_matching,
                "gs_log": gs_log,
            }

        return {
            "ok": False,
            "kind": "stable_not_optimal",
            "title": "안정적이지만 최적은 아닙니다",
            "message": f"현재 매칭은 안정적이지만 점수는 {score}점입니다. 가능한 최고 안정 점수는 {best_score}점입니다.",
            "blocking_pairs": [],
            "score": score,
            "best_score": best_score,
            "best_matching": best_matching,
            "gs_matching": gs_matching,
            "gs_log": gs_log,
        }

    if stage == 3:
        if matching == gs_matching:
            return {
                "ok": True,
                "kind": "gs_correct",
                "title": "정답입니다! Gale-Shapley 결과를 맞혔습니다.",
                "message": "이 매칭은 남성 제안형 Gale-Shapley 알고리즘의 결과와 정확히 같습니다.",
                "blocking_pairs": blocking_pairs,
                "score": score,
                "best_score": best_score,
                "best_matching": best_matching,
                "gs_matching": gs_matching,
                "gs_log": gs_log,
            }

        return {
            "ok": False,
            "kind": "gs_wrong",
            "title": "Gale-Shapley 결과와 다릅니다",
            "message": "현재 매칭이 안정적일 수도 있지만, 남성 제안형 Gale-Shapley 알고리즘의 결과는 아닙니다.",
            "blocking_pairs": blocking_pairs,
            "score": score,
            "best_score": best_score,
            "best_matching": best_matching,
            "gs_matching": gs_matching,
            "gs_log": gs_log,
        }


def render_feedback(result):
    css_class = "success" if result["ok"] else "fail"
    icon = "✅" if result["ok"] else "❌"

    st.markdown(
        f"""
        <div class="feedback-card {css_class}">
            <h3 style="margin-top:0;">{icon} {esc(result["title"])}</h3>
            <p>{esc(result["message"])}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if result["blocking_pairs"]:
        render_blocking_pair_details(result["blocking_pairs"])

    if result["score"] is not None:
        st.markdown(
            f"""
            <div class="feedback-card info">
                <span class="pill pill-blue">내 점수: {result["score"]}</span>
                <span class="pill pill-green">최고 안정 점수: {result["best_score"]}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_solution_panel(stage, result):
    if result is None:
        return

    if stage in [1, 2]:
        label = "최적 안정 매칭 보기"
        if st.button(label, use_container_width=True):
            st.session_state.show_solution = not st.session_state.show_solution

        if st.session_state.show_solution and result.get("best_matching"):
            st.info(f"최적 안정 매칭: {explain_matching(result['best_matching'])}")
            st.info(f"최고 안정 점수: {result['best_score']}")

    if stage == 3:
        if st.button("Gale-Shapley 결과와 과정 보기", use_container_width=True):
            st.session_state.show_solution = not st.session_state.show_solution

        if st.session_state.show_solution:
            st.info(f"Gale-Shapley 결과: {explain_matching(result['gs_matching'])}")
            log_html = "<br/>".join(esc(line) for line in result["gs_log"])
            st.markdown(f'<div class="gs-log">{log_html}</div>', unsafe_allow_html=True)


def render_hint(stage, men, women, men_prefs, women_prefs, matching):
    if st.button("힌트", use_container_width=True):
        st.session_state.show_hint = not st.session_state.show_hint

    if not st.session_state.show_hint:
        return

    complete, _ = is_complete_one_to_one(matching, men, women)

    if not complete:
        st.warning("먼저 완전한 1:1 매칭을 만들어보세요. 같은 사람이 두 번 선택되면 안 됩니다.")

    elif stage in [1, 2]:
        blocking_pairs = find_blocking_pairs(matching, men_prefs, women_prefs)
        if blocking_pairs:
            bp = blocking_pairs[0]
            st.warning(
                f"{bp['man']}와 {bp['woman']}을/를 유심히 보세요. "
                f"두 사람이 서로 현재 파트너보다 상대방을 더 선호할 수 있습니다."
            )
        else:
            if stage == 1:
                st.success("이미 안정 매칭으로 보입니다. 제출해보세요!")
            else:
                best_matching, best_score, _ = find_best_stable_matching(men, women, men_prefs, women_prefs)
                score = satisfaction_score(matching, men_prefs, women_prefs)
                if score == best_score:
                    st.success("안정적이면서 최적인 매칭으로 보입니다. 제출해보세요!")
                else:
                    st.info(
                        "현재 매칭은 안정적이지만, 더 높은 만족도 점수를 가진 안정 매칭이 있을 수 있습니다. "
                        "Blocking pair를 만들지 않으면서 점수를 높여보세요."
                    )

    else:
        st.info(
            "남성 제안형 Gale-Shapley에서는 남성들이 자신의 선호 순서대로 제안하고, "
            "여성은 지금까지 받은 제안 중 가장 선호하는 사람만 임시로 보류합니다."
        )


def render_game():
    stage = st.session_state.stage
    info = STAGE_INFO[stage]

    top1, top2, top3, top4, top5 = st.columns([0.9, 1.1, 1.3, 0.8, 1.2])
    with top1:
        if st.button("← 홈", use_container_width=True):
            back_home()
    with top2:
        if st.button("새 퍼즐", use_container_width=True):
            new_puzzle()
    with top3:
        if st.button("선호도 랜덤 변경", use_container_width=True):
            reshuffle_preferences()
    with top4:
        n = st.selectbox("인원", [3, 4, 5, 6], index=[3, 4, 5, 6].index(st.session_state.n), label_visibility="collapsed")
        if n != st.session_state.n:
            st.session_state.n = n
            new_puzzle()
    with top5:
        st.markdown(
            f'<span class="pill pill-blue">{esc(info["title"])}</span>',
            unsafe_allow_html=True,
        )

    st.markdown(
        f"""
        <div class="sml-hero" style="padding:1.35rem 1.55rem;">
            <div style="font-size:2rem;font-weight:850;letter-spacing:-0.04em;">{info["icon"]} {esc(info["title"])}</div>
            <p class="sml-subtitle">{esc(info["short"])}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_stage_explanation(stage)

    men, women, men_prefs, women_prefs = generate_preferences(
        st.session_state.n,
        seed=st.session_state.pref_seed,
        name_seed=st.session_state.name_seed,
    )

    matching = get_matching_from_widgets(men, women)

    highlighted_men, highlighted_women = set(), set()
    result_key = (st.session_state.pref_seed, st.session_state.name_seed)
    if "last_result" in st.session_state and st.session_state.get("last_seed_key") == result_key:
        last_result = st.session_state["last_result"]
        for bp in last_result.get("blocking_pairs", []):
            highlighted_men.add(bp["man"])
            highlighted_women.add(bp["woman"])

    main_left, main_right = st.columns([1.15, 0.85])

    with main_left:
        render_preferences(men, women, men_prefs, women_prefs, highlighted_men, highlighted_women)

    with main_right:
        matching = render_matching_inputs(men, women)

        best_matching, best_score, _ = find_best_stable_matching(men, women, men_prefs, women_prefs)
        gs_matching, gs_log = gale_shapley_men_propose(men, women, men_prefs, women_prefs)

        st.markdown('<div class="section-title">상태</div>', unsafe_allow_html=True)
        render_metrics(matching, men_prefs, women_prefs, best_score=best_score, gs_target=gs_matching if stage == 3 else None)

        submit_col, clear_col = st.columns(2)
        with submit_col:
            if st.button("제출", type="primary", use_container_width=True):
                result = evaluate_submission(stage, matching, men, women, men_prefs, women_prefs)
                st.session_state.last_result = result
                st.session_state.last_seed_key = result_key
                st.session_state.submitted = True
                st.session_state.show_solution = False
                st.rerun()

        with clear_col:
            if st.button("선택 초기화", use_container_width=True):
                clear_choice_state()
                st.rerun()

        st.markdown('<div class="section-title">도움말</div>', unsafe_allow_html=True)
        render_hint(stage, men, women, men_prefs, women_prefs, matching)

        if st.session_state.get("submitted") and st.session_state.get("last_seed_key") == result_key:
            st.markdown('<div class="section-title">결과</div>', unsafe_allow_html=True)
            result = st.session_state["last_result"]
            render_feedback(result)
            render_solution_panel(stage, result)


def main():
    inject_css()
    init_state()

    if st.session_state.view == "home":
        render_home()
    else:
        render_game()


if __name__ == "__main__":
    main()
