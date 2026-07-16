import random

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Blackjack Strategy Lab", page_icon="🃏", layout="wide")

STYLES = {"Cautious": 15, "Standard": 17, "Aggressive": 19}
SUITS = ["♠", "♥", "♦", "♣"]
RANKS = [("A", 11), ("2", 2), ("3", 3), ("4", 4), ("5", 5), ("6", 6),
         ("7", 7), ("8", 8), ("9", 9), ("10", 10), ("J", 10), ("Q", 10), ("K", 10)]

st.markdown("""
<style>
    .stApp {background: radial-gradient(circle at top, #17603d, #072b1c 70%);}
    .game-panel {padding: 1.3rem; border: 1px solid #d7b95b; border-radius: 18px;
                 background: rgba(3, 30, 19, .72); box-shadow: 0 8px 25px #00180f;}
    .cards {display: flex; gap: 12px; min-height: 145px; align-items: center; flex-wrap: wrap;}
    .card {width: 86px; height: 126px; padding: 8px; border-radius: 9px; color: #151515;
           background: linear-gradient(145deg, #fff, #e8e6dd); border: 2px solid #c9c4b4;
           box-shadow: 4px 6px 10px #001d12; font: 700 25px Georgia; box-sizing: border-box;}
    .red {color: #c62828;} .suit {font-size: 36px; text-align: center; margin-top: 15px;}
    .hidden {color: #e5c85b; background: repeating-linear-gradient(45deg,#172c68,#172c68 8px,
             #29488f 8px,#29488f 16px); border: 5px solid #eee; text-align:center; padding-top:35px;}
    .advisor {padding: 1rem 1.2rem; border-left: 6px solid #e2c45c; border-radius: 10px;
              background: rgba(226,196,92,.12); margin: .5rem 0 1rem;}
</style>
""", unsafe_allow_html=True)


# ----- Cards and rules -----------------------------------------------------

def new_deck():
    deck = [(value, rank, suit) for suit in SUITS for rank, value in RANKS]
    random.shuffle(deck)
    return deck


def draw_card(deck):
    return deck.pop()


def hand_total(cards):
    total = sum(card[0] for card in cards)
    aces = sum(card[1] == "A" for card in cards)
    while total > 21 and aces:
        total -= 10
        aces -= 1
    return total


def card_name(card):
    return f"{card[1]}{card[2]}"


def cards_html(cards, hide_second=False):
    pieces = []
    for index, card in enumerate(cards):
        if hide_second and index == 1:
            pieces.append('<div class="card hidden">🂠</div>')
        else:
            color = "red" if card[2] in ["♥", "♦"] else ""
            pieces.append(
                f'<div class="card {color}">{card[1]}<div class="suit">{card[2]}</div></div>'
            )
    return '<div class="cards">' + "".join(pieces) + "</div>"


def dealer_turn(cards, deck):
    while hand_total(cards) < 17:
        cards.append(draw_card(deck))


def choose_result(player_total, dealer_total):
    if player_total > 21:
        return "Loss"
    if dealer_total > 21 or player_total > dealer_total:
        return "Win"
    if player_total < dealer_total:
        return "Loss"
    return "Tie"


def make_record(player, dealer, starting_total, hits, result, player_name, style, mode):
    return {
        "Round": len(st.session_state.history) + 1, "Mode": mode,
        "Player": player_name, "Play Style": style,
        "Starting Hand": ", ".join(card_name(card) for card in player[:2]),
        "Starting Total": starting_total, "Dealer Up Card": card_name(dealer[0]),
        "Number of Hits": hits, "Cards in Hand": len(player),
        "Final Hand": ", ".join(card_name(card) for card in player),
        "Final Player Total": hand_total(player), "Dealer Total": hand_total(dealer),
        "Player Bust": hand_total(player) > 21, "Result": result,
    }


# ----- Game and simulations ------------------------------------------------

def new_round():
    deck = new_deck()
    st.session_state.player = [draw_card(deck), draw_card(deck)]
    st.session_state.dealer = [draw_card(deck), draw_card(deck)]
    st.session_state.deck = deck
    st.session_state.starting_total = hand_total(st.session_state.player)
    st.session_state.hits = 0
    st.session_state.round_over = False
    st.session_state.message = "Choose Hit or Stand."


if "history" not in st.session_state:
    st.session_state.history = []
needed = ["player", "dealer", "deck", "starting_total", "hits"]
# Old integer-card sessions are replaced after this visual-card update.
if any(name not in st.session_state for name in needed) or isinstance(st.session_state.get("player", [0])[0], int):
    new_round()


def finish_manual_round(result, player_name):
    st.session_state.history.append(make_record(
        st.session_state.player, st.session_state.dealer, st.session_state.starting_total,
        st.session_state.hits, result, player_name, "Human Choice", "Played"
    ))
    st.session_state.round_over = True


def simulate_round(style):
    deck = new_deck()
    player = [draw_card(deck), draw_card(deck)]
    dealer = [draw_card(deck), draw_card(deck)]
    starting_total, hits = hand_total(player), 0
    while hand_total(player) < STYLES[style]:
        player.append(draw_card(deck))
        hits += 1
    if hand_total(player) <= 21:
        dealer_turn(dealer, deck)
    result = choose_result(hand_total(player), hand_total(dealer))
    return make_record(player, dealer, starting_total, hits, result,
                       f"{style} Bot", style, "Simulation")


def run_simulation(rounds, style):
    for _ in range(rounds):
        st.session_state.history.append(simulate_round(style))


def estimate_move(trials=800):
    """Estimate current Hit/Stand results without looking at the hidden card."""
    scores = {"Hit": {"wins": 0, "ties": 0, "busts": 0},
              "Stand": {"wins": 0, "ties": 0, "busts": 0}}
    unseen = st.session_state.deck + [st.session_state.dealer[1]]
    for action in scores:
        for _ in range(trials):
            deck = unseen.copy()
            random.shuffle(deck)
            player = st.session_state.player.copy()
            dealer = [st.session_state.dealer[0], draw_card(deck)]
            if action == "Hit":
                player.append(draw_card(deck))
                # After the suggested hit, use the standard rule for later decisions.
                while hand_total(player) < 17:
                    player.append(draw_card(deck))
            if hand_total(player) <= 21:
                dealer_turn(dealer, deck)
            result = choose_result(hand_total(player), hand_total(dealer))
            scores[action]["wins"] += result == "Win"
            scores[action]["ties"] += result == "Tie"
            scores[action]["busts"] += hand_total(player) > 21
    for action in scores:
        scores[action]["success"] = 100 * (
            scores[action]["wins"] + .5 * scores[action]["ties"]
        ) / trials
        scores[action]["bust_rate"] = 100 * scores[action]["busts"] / trials
    return scores


# ----- Game interface and live advisor ------------------------------------

st.title("🃏 Blackjack Strategy Lab")
st.caption("Play with friends, compare results, and learn when to hit or stand.")
player_name = st.text_input("Player name", "Player 1", max_chars=30).strip() or "Anonymous"

with st.container(border=True):
    dealer_col, player_col = st.columns(2)
    with dealer_col:
        st.subheader("Dealer")
        st.markdown(cards_html(st.session_state.dealer, not st.session_state.round_over),
                    unsafe_allow_html=True)
        st.write("Total:", hand_total(st.session_state.dealer) if st.session_state.round_over else "?")
    with player_col:
        st.subheader(player_name)
        st.markdown(cards_html(st.session_state.player), unsafe_allow_html=True)
        st.write(f"**Total:** {hand_total(st.session_state.player)} · "
                 f"**Cards:** {len(st.session_state.player)} · **Hits:** {st.session_state.hits}")

    hit, stand, again = st.columns(3)
    if hit.button("➕ Hit", disabled=st.session_state.round_over, use_container_width=True):
        st.session_state.player.append(draw_card(st.session_state.deck))
        st.session_state.hits += 1
        if hand_total(st.session_state.player) > 21:
            st.session_state.message = "Bust! You lose."
            finish_manual_round("Loss", player_name)
        else:
            st.session_state.message = "Card drawn. Review the advisor or choose again."
        st.rerun()
    if stand.button("✋ Stand", disabled=st.session_state.round_over, use_container_width=True):
        dealer_turn(st.session_state.dealer, st.session_state.deck)
        result = choose_result(hand_total(st.session_state.player), hand_total(st.session_state.dealer))
        st.session_state.message = f"{result}! Dealer total: {hand_total(st.session_state.dealer)}"
        finish_manual_round(result, player_name)
        st.rerun()
    if again.button("↻ New Round", use_container_width=True):
        new_round()
        st.rerun()
    st.warning(st.session_state.message)

st.subheader("🎯 Current Move Advisor")
if not st.session_state.round_over:
    advice = estimate_move()
    recommendation = max(advice, key=lambda action: advice[action]["success"])
    st.markdown(
        f'<div class="advisor"><b>Recommended move: {recommendation}</b><br>'
        f'Estimated success — Hit: {advice["Hit"]["success"]:.1f}% · '
        f'Stand: {advice["Stand"]["success"]:.1f}%<br>'
        f'Estimated bust risk after Hit: {advice["Hit"]["bust_rate"]:.1f}%</div>',
        unsafe_allow_html=True
    )
    st.caption("Estimate uses 800 possible deals, the visible dealer card, and a standard hit-below-17 rule. A tie counts as half a success; results are not guarantees.")
else:
    st.info("Start a new round to receive the next Hit-or-Stand estimate.")


# ----- Historical analysis -------------------------------------------------

st.divider()
st.header("📊 Player & Strategy Analysis")
simulation_style = st.selectbox("Automatic strategy to test", list(STYLES), index=1)
st.caption(f"{simulation_style} hits below {STYLES[simulation_style]} and then stands.")
sim10, sim50, clear = st.columns(3)
if sim10.button("Run 10 rounds", use_container_width=True):
    run_simulation(10, simulation_style)
    st.rerun()
if sim50.button("Run 50 rounds", use_container_width=True):
    run_simulation(50, simulation_style)
    st.rerun()
if clear.button("Clear Data", use_container_width=True):
    st.session_state.history = []
    st.rerun()

if st.session_state.history:
    data = pd.DataFrame(st.session_state.history)
    # Old saved rows remain usable after adding the Player field.
    if "Player" not in data:
        data["Player"] = "Previous Player"
    data["Win"] = (data["Result"] == "Win").astype(int)
    data["Loss"] = (data["Result"] == "Loss").astype(int)
    data["Bust"] = data["Player Bust"].astype(int)
    summary = data.groupby(["Player", "Play Style"]).agg(
        Rounds=("Result", "size"), Win_Rate=("Win", "mean"),
        Loss_Rate=("Loss", "mean"), Bust_Rate=("Bust", "mean"),
        Average_Hits=("Number of Hits", "mean"),
        Average_Cards=("Cards in Hand", "mean"),
    ).reset_index()
    for column in ["Win_Rate", "Loss_Rate", "Bust_Rate"]:
        summary[column] = (summary[column] * 100).round(1)
    summary[["Average_Hits", "Average_Cards"]] = summary[
        ["Average_Hits", "Average_Cards"]].round(2)

    player_rows = data[(data["Mode"] == "Played") & (data["Player"] == player_name)]
    bot_rows = summary[summary["Play Style"] != "Human Choice"]
    with st.container(border=True):
        st.subheader(f"Analysis for {player_name}")
        if len(player_rows):
            player_win = 100 * player_rows["Win"].mean()
            player_bust = 100 * player_rows["Bust"].mean()
            st.write(f"From **{len(player_rows)} rounds**: win rate **{player_win:.1f}%**, "
                     f"bust rate **{player_bust:.1f}%**, average hits "
                     f"**{player_rows['Number of Hits'].mean():.2f}**.")
        else:
            st.write("Complete a round with this name to create a personal analysis.")
        if len(bot_rows):
            best = bot_rows.sort_values(["Win_Rate", "Bust_Rate"], ascending=[False, True]).iloc[0]
            st.success(f"Best tested strategy so far: {best['Play Style']} "
                       f"({best['Win_Rate']:.1f}% win rate across {int(best['Rounds'])} rounds).")
        else:
            st.write("Run strategy simulations to discover which tested style performs best.")

    st.subheader("Comparison table")
    st.dataframe(summary, hide_index=True, use_container_width=True)
    st.bar_chart(summary.set_index("Player")[["Win_Rate", "Loss_Rate", "Bust_Rate"]])
    st.subheader("Round-level data")
    export = data.drop(columns=["Win", "Loss", "Bust"])
    st.dataframe(export, hide_index=True, use_container_width=True)
    st.download_button("Download data as CSV", export.to_csv(index=False),
                       "blackjack_strategy_data.csv", "text/csv")
else:
    st.info("Play a round or simulate a strategy to build the historical analysis.")
