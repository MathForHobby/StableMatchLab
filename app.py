import html
import streamlit as st

from matching_engine import (
    generate_preferences,
    is_complete_one_to_one,
    find_blocking_pairs,
    satisfaction_score,
    find_best_stable_matching,
    gale_shapley_men_propose,
    explain_matching,
)


st.set_page_config(
    page_title="Stable Match Lab",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="collapsed",
)


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
    min-height: 255px;
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

hr {
    margin: 1rem 0;
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
        "seed": 100,
        "n": 4,
        "submitted": False,
        "show_solution": False,
        "show_hint": False,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def start_stage(stage: int):
    st.session_state.stage = stage
    st.session_state.view = "game"
    st.session_state.submitted = False
    st.session_state.show_solution = False
    st.session_state.show_hint = False
    st.rerun()


def new_puzzle():
    st.session_state.seed += 1
    st.session_state.submitted = False
    st.session_state.show_solution = False
    st.session_state.show_hint = False
    st.rerun()


def back_home():
    st.session_state.view = "home"
    st.session_state.submitted = False
    st.session_state.show_solution = False
    st.session_state.show_hint = False
    st.rerun()


STAGE_INFO = {
    1: {
        "title": "Stage 1 — Stable Matching",
        "short": "Create a one-to-one matching with no blocking pairs.",
        "goal": "모든 사람을 1:1로 연결하되, 서로 현재 파트너보다 더 선호하는 blocking pair가 없도록 만드세요.",
        "clear": "성공 조건: 완전한 1:1 매칭 + blocking pair 0개",
        "difficulty": "Beginner",
        "icon": "🧩",
        "tag": "Stability",
    },
    2: {
        "title": "Stage 2 — Optimal Stable Matching",
        "short": "Find the stable matching with the highest overall satisfaction.",
        "goal": "안정 매칭 중에서도 전체 만족도 점수가 가장 높은 매칭을 찾으세요.",
        "clear": "성공 조건: stable matching + 최고 만족도 점수",
        "difficulty": "Intermediate",
        "icon": "🎯",
        "tag": "Optimality",
    },
    3: {
        "title": "Stage 3 — Gale-Shapley Challenge",
        "short": "Predict the result of the men-proposing Gale-Shapley algorithm.",
        "goal": "남성 제안형 Gale-Shapley 알고리즘이 만드는 최종 매칭을 예측하세요.",
        "clear": "성공 조건: 알고리즘 결과와 정확히 같은 매칭",
        "difficulty": "Advanced",
        "icon": "⚙️",
        "tag": "Algorithm",
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
                <b>Goal</b><br/>
                {info["goal"]}<br/><br/>
                <b>Clear</b><br/>
                {info["clear"]}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button(f"Play Stage {stage}", key=f"play_stage_{stage}", use_container_width=True):
        start_stage(stage)


def render_home():
    st.markdown(
        """
        <div class="sml-hero">
            <div class="sml-title">Stable Match Lab</div>
            <p class="sml-subtitle">
                A small puzzle lab for matching theory. Build matchings, avoid blocking pairs,
                compare optimal stable outcomes, and predict Gale-Shapley results through play.
            </p>
            <div style="margin-top:1rem;">
                <span class="pill pill-blue">Matching Theory</span>
                <span class="pill pill-green">Puzzle Learning</span>
                <span class="pill pill-purple">Streamlit MVP</span>
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
    with st.expander("Matching Theory quick guide"):
        st.markdown(
            """
            **Stable matching** means that there is no pair of participants who would both rather leave their current partners and match with each other.

            **Blocking pair** is exactly such a pair. If a blocking pair exists, the current matching is unstable.

            **Optimal stable matching** adds a second condition: among stable matchings, we choose the one with the best total satisfaction score.

            **Gale-Shapley algorithm** is a classic algorithm that always finds a stable matching. In this app, Stage 3 asks you to predict the result of the men-proposing version.
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

    rows = []
    for idx, partner in enumerate(prefs, start=1):
        rows.append(
            f"""
            <div class="pref-row">
                <div class="rank-dot">{rank_badge(idx)}</div>
                <div>{esc(partner)}</div>
            </div>
            """
        )

    st.markdown(
        f"""
        <div class="person-card{danger_class}">
            <div class="person-head">
                <div class="person-name">{esc(name)}</div>
                <div class="avatar">{avatar}</div>
            </div>
            <div class="pref-list">
                {''.join(rows)}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_preferences(men, women, men_prefs, women_prefs, highlighted_men=None, highlighted_women=None):
    highlighted_men = highlighted_men or set()
    highlighted_women = highlighted_women or set()

    st.markdown('<div class="section-title">Preference Cards</div>', unsafe_allow_html=True)
    col_m, col_w = st.columns(2)

    with col_m:
        st.markdown('<span class="pill pill-blue">Men</span>', unsafe_allow_html=True)
        for m in men:
            render_person_card(m, men_prefs[m], danger=m in highlighted_men, side="M")

    with col_w:
        st.markdown('<span class="pill pill-purple">Women</span>', unsafe_allow_html=True)
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


def get_matching_from_widgets(men, women):
    matching = {}
    for m in men:
        selected = st.session_state.get(f"match_{st.session_state.stage}_{st.session_state.seed}_{m}", "—")
        if selected != "—":
            matching[m] = selected
    return matching


def render_matching_inputs(men, women):
    st.markdown('<div class="section-title">Build Your Matching</div>', unsafe_allow_html=True)

    left, right = st.columns([0.95, 1.05])

    with left:
        st.markdown('<div class="match-board">', unsafe_allow_html=True)
        for m in men:
            st.selectbox(
                f"{m} ↔",
                ["—"] + women,
                key=f"match_{st.session_state.stage}_{st.session_state.seed}_{m}",
                label_visibility="visible",
            )
        st.markdown("</div>", unsafe_allow_html=True)

    matching = get_matching_from_widgets(men, women)

    with right:
        st.markdown('<div class="match-board">', unsafe_allow_html=True)
        st.markdown("<b>Current Matching Board</b>", unsafe_allow_html=True)

        for m in men:
            w = matching.get(m)
            if w:
                st.markdown(f'<div class="pair-chip"><span>{esc(m)}</span><span>↔</span><span>{esc(w)}</span></div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="pair-chip pending"><span>{esc(m)}</span><span>↔</span><span>Not matched</span></div>', unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    return matching


def render_metrics(matching, men_prefs, women_prefs, best_score=None, gs_target=None):
    complete_count = len(matching)
    n = len(men_prefs)

    score_text = "—"
    if complete_count == n and len(set(matching.values())) == n:
        score_text = str(satisfaction_score(matching, men_prefs, women_prefs))

    best_text = "—" if best_score is None else str(best_score)
    target_text = "Hidden" if gs_target is not None else "—"

    st.markdown(
        f"""
        <div class="metric-grid">
            <div class="metric-box">
                <div class="metric-label">Matched</div>
                <div class="metric-value">{complete_count}/{n}</div>
            </div>
            <div class="metric-box">
                <div class="metric-label">Your Score</div>
                <div class="metric-value">{score_text}</div>
            </div>
            <div class="metric-box">
                <div class="metric-label">Best Stable Score</div>
                <div class="metric-value">{best_text}</div>
            </div>
            <div class="metric-box">
                <div class="metric-label">GS Target</div>
                <div class="metric-value">{target_text}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_blocking_pair_details(blocking_pairs):
    st.markdown("**Blocking pairs found:**")
    for bp in blocking_pairs:
        st.markdown(
            f"""
            <div class="feedback-card fail" style="margin-bottom:0.6rem;">
                <span class="pill pill-red">{esc(bp["man"])} ↔ {esc(bp["woman"])}</span><br/>
                {esc(bp["man"])} currently has {esc(bp["man_current"])} as rank #{bp["man_current_rank"]},
                but prefers {esc(bp["woman"])} as rank #{bp["man_new_rank"]}.<br/>
                {esc(bp["woman"])} currently has {esc(bp["woman_current"])} as rank #{bp["woman_current_rank"]},
                but prefers {esc(bp["man"])} as rank #{bp["woman_new_rank"]}.
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
            "title": "Not a complete one-to-one matching",
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
                "title": "Success! This is a stable matching.",
                "message": "No blocking pair exists.",
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
            "title": "Unstable matching",
            "message": "At least one blocking pair exists.",
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
                "title": "Not stable yet",
                "message": "Stage 2 requires stability first. Remove every blocking pair before optimizing score.",
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
                "title": "Perfect! This is an optimal stable matching.",
                "message": f"Your score is {score}, which matches the best stable score.",
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
            "title": "Stable, but not optimal",
            "message": f"Your matching is stable, but its score is {score}. The best stable score is {best_score}.",
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
                "title": "Correct! You predicted the Gale-Shapley outcome.",
                "message": "This is exactly the men-proposing Gale-Shapley result.",
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
            "title": "Not the Gale-Shapley result",
            "message": "Your matching may or may not be stable, but it is not the men-proposing Gale-Shapley outcome.",
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
                <span class="pill pill-blue">Your Score: {result["score"]}</span>
                <span class="pill pill-green">Best Stable Score: {result["best_score"]}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_solution_panel(stage, result):
    if result is None:
        return

    if stage in [1, 2]:
        label = "Show one best stable matching"
        if st.button(label, use_container_width=True):
            st.session_state.show_solution = not st.session_state.show_solution

        if st.session_state.show_solution and result.get("best_matching"):
            st.info(f"Best stable matching: {explain_matching(result['best_matching'])}")
            st.info(f"Best stable score: {result['best_score']}")

    if stage == 3:
        if st.button("Show Gale-Shapley result and process", use_container_width=True):
            st.session_state.show_solution = not st.session_state.show_solution

        if st.session_state.show_solution:
            st.info(f"Gale-Shapley result: {explain_matching(result['gs_matching'])}")
            log_html = "<br/>".join(esc(line) for line in result["gs_log"])
            st.markdown(f'<div class="gs-log">{log_html}</div>', unsafe_allow_html=True)


def render_hint(stage, men, women, men_prefs, women_prefs, matching):
    if st.button("Hint", use_container_width=True):
        st.session_state.show_hint = not st.session_state.show_hint

    if not st.session_state.show_hint:
        return

    complete, _ = is_complete_one_to_one(matching, men, women)

    if not complete:
        st.warning("First, make a complete one-to-one matching. No woman should be selected twice.")

    elif stage in [1, 2]:
        blocking_pairs = find_blocking_pairs(matching, men_prefs, women_prefs)
        if blocking_pairs:
            bp = blocking_pairs[0]
            st.warning(
                f"Look carefully at {bp['man']} and {bp['woman']}. "
                f"They may both prefer each other over their current partners."
            )
        else:
            if stage == 1:
                st.success("This already looks stable. Submit it!")
            else:
                best_matching, best_score, _ = find_best_stable_matching(men, women, men_prefs, women_prefs)
                score = satisfaction_score(matching, men_prefs, women_prefs)
                if score == best_score:
                    st.success("This looks stable and optimal. Submit it!")
                else:
                    st.info(
                        "This is stable, but there may be a more satisfying stable matching. "
                        "Try improving the total score without creating a blocking pair."
                    )

    else:
        st.info(
            "In men-proposing Gale-Shapley, each man proposes down his preference list, "
            "while each woman keeps only her favorite proposal so far."
        )


def render_game():
    stage = st.session_state.stage
    info = STAGE_INFO[stage]

    top1, top2, top3, top4 = st.columns([1.1, 1, 1, 1])
    with top1:
        if st.button("← Home", use_container_width=True):
            back_home()
    with top2:
        if st.button("New Puzzle", use_container_width=True):
            new_puzzle()
    with top3:
        n = st.selectbox("Size", [3, 4, 5, 6], index=[3, 4, 5, 6].index(st.session_state.n), label_visibility="collapsed")
        if n != st.session_state.n:
            st.session_state.n = n
            new_puzzle()
    with top4:
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

    men, women, men_prefs, women_prefs = generate_preferences(st.session_state.n, seed=st.session_state.seed)

    matching = get_matching_from_widgets(men, women)
    last_result = None

    highlighted_men, highlighted_women = set(), set()
    if "last_result" in st.session_state and st.session_state.get("last_seed") == st.session_state.seed:
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

        st.markdown('<div class="section-title">Status</div>', unsafe_allow_html=True)
        render_metrics(matching, men_prefs, women_prefs, best_score=best_score, gs_target=gs_matching if stage == 3 else None)

        submit_col, clear_col = st.columns(2)
        with submit_col:
            if st.button("Submit", type="primary", use_container_width=True):
                result = evaluate_submission(stage, matching, men, women, men_prefs, women_prefs)
                st.session_state.last_result = result
                st.session_state.last_seed = st.session_state.seed
                st.session_state.submitted = True
                st.session_state.show_solution = False
                st.rerun()

        with clear_col:
            if st.button("Reset choices", use_container_width=True):
                for m in men:
                    key = f"match_{stage}_{st.session_state.seed}_{m}"
                    if key in st.session_state:
                        del st.session_state[key]
                st.session_state.submitted = False
                st.session_state.show_solution = False
                st.session_state.show_hint = False
                st.rerun()

        st.markdown('<div class="section-title">Help</div>', unsafe_allow_html=True)
        render_hint(stage, men, women, men_prefs, women_prefs, matching)

        if st.session_state.get("submitted") and st.session_state.get("last_seed") == st.session_state.seed:
            st.markdown('<div class="section-title">Result</div>', unsafe_allow_html=True)
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
