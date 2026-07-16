import random

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Blackjack Strategy Lab", page_icon="🃏")

# Each style stands at a different total. This is our experiment variable.
STYLES = {"Cautious": 15, "Standard": 17, "Aggressive": 19}


# ----- Game functions ------------------------------------------------------

def new_deck():
    """Create and shuffle a real 52-card deck using card values."""
    deck = ([11, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10] * 4)
    random.shuffle(deck)
    return deck


def draw_card(deck):
    return deck.pop()


def hand_total(cards):
    """Count an ace as 1 instead of 11 when the hand would bust."""
    total = sum(cards)
    aces = cards.count(11)
    while total > 21 and aces > 0:
        total -= 10
        aces -= 1
    return total


def show_cards(cards):
    return "  ".join("A" if card == 11 else str(card) for card in cards)


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
    """Create one useful row of data describing the player's round."""
    return {
        "Round": len(st.session_state.history) + 1,
        "Mode": mode,
        "Player": player_name,
        "Play Style": style,
        "Starting Total": starting_total,
        "Dealer Up Card": dealer[0],
        "Number of Hits": hits,
        "Cards in Hand": len(player),
        "Final Player Total": hand_total(player),
        "Dealer Total": hand_total(dealer),
        "Player Bust": hand_total(player) > 21,
        "Result": result,
    }


# ----- Session state -------------------------------------------------------

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
required_game_data = ["player", "dealer", "deck", "starting_total", "hits"]
if any(name not in st.session_state for name in required_game_data):
    new_round()


def finish_manual_round(result, player_name):
    record = make_record(
        st.session_state.player, st.session_state.dealer,
        st.session_state.starting_total, st.session_state.hits,
        result, player_name, "Human Choice", "Played"
    )
    st.session_state.history.append(record)
    st.session_state.round_over = True


def simulate_round(style):
    """Play one automatic round using the selected strategy."""
    deck = new_deck()
    player = [draw_card(deck), draw_card(deck)]
    dealer = [draw_card(deck), draw_card(deck)]
    starting_total = hand_total(player)
    hits = 0

    while hand_total(player) < STYLES[style]:
        player.append(draw_card(deck))
        hits += 1
    if hand_total(player) <= 21:
        dealer_turn(dealer, deck)

    result = choose_result(hand_total(player), hand_total(dealer))
    return make_record(
        player, dealer, starting_total, hits, result,
        f"{style} Bot", style, "Simulation"
    )


def run_simulation(rounds, style):
    for _ in range(rounds):
        st.session_state.history.append(simulate_round(style))


# ----- Player interface ----------------------------------------------------

st.title("🃏 Blackjack Strategy Lab")
st.caption("Play with friends, compare player results, and test automatic strategies.")
player_name = st.text_input(
    "Player name",
    value="Player 1",
    max_chars=30,
    help="This name is saved with each round for the player analysis."
)
player_name = player_name.strip() or "Anonymous"

dealer_col, player_col = st.columns(2)
with dealer_col:
    visible = show_cards(st.session_state.dealer)
    if not st.session_state.round_over:
        visible = f"{st.session_state.dealer[0]}  ?"
    st.subheader("Dealer")
    st.info(visible)
with player_col:
    st.subheader("Your hand")
    st.success(show_cards(st.session_state.player))
    st.write("Total:", hand_total(st.session_state.player))
    st.write("Cards in hand:", len(st.session_state.player))

hit, stand, again = st.columns(3)
if hit.button("Hit", disabled=st.session_state.round_over, use_container_width=True):
    st.session_state.player.append(draw_card(st.session_state.deck))
    st.session_state.hits += 1
    if hand_total(st.session_state.player) > 21:
        st.session_state.message = "Bust! You lose."
        finish_manual_round("Loss", player_name)
    else:
        st.session_state.message = "You drew a card. Hit again or stand?"
    st.rerun()

if stand.button("Stand", disabled=st.session_state.round_over, use_container_width=True):
    dealer_turn(st.session_state.dealer, st.session_state.deck)
    result = choose_result(hand_total(st.session_state.player), hand_total(st.session_state.dealer))
    st.session_state.message = f"{result}! Dealer total: {hand_total(st.session_state.dealer)}"
    finish_manual_round(result, player_name)
    st.rerun()

if again.button("New Round", use_container_width=True):
    new_round()
    st.rerun()

st.warning(st.session_state.message)


# ----- Strategy experiment and analysis -----------------------------------

st.divider()
st.header("Strategy Experiment")
simulation_style = st.selectbox("Strategy to simulate", list(STYLES), index=1)
st.caption(
    f"{simulation_style} players hit below {STYLES[simulation_style]} and stand at "
    f"{STYLES[simulation_style]} or higher. The dealer always hits below 17."
)

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
    # Keep older session rows usable after this player-name feature was added.
    if "Player" not in data.columns:
        data["Player"] = "Previous Player"
    data["Win"] = (data["Result"] == "Win").astype(int)
    data["Loss"] = (data["Result"] == "Loss").astype(int)
    data["Bust"] = data["Player Bust"].astype(int)

    summary = data.groupby(["Player", "Play Style"]).agg(
        Rounds=("Result", "size"),
        Win_Rate=("Win", "mean"),
        Loss_Rate=("Loss", "mean"),
        Bust_Rate=("Bust", "mean"),
        Average_Hits=("Number of Hits", "mean"),
        Average_Cards=("Cards in Hand", "mean"),
    ).reset_index()
    for column in ["Win_Rate", "Loss_Rate", "Bust_Rate"]:
        summary[column] = (summary[column] * 100).round(1)
    summary[["Average_Hits", "Average_Cards"]] = summary[
        ["Average_Hits", "Average_Cards"]
    ].round(2)

    st.subheader("Player and strategy comparison")
    st.dataframe(summary, hide_index=True, use_container_width=True)
    st.bar_chart(summary.set_index("Player")[["Win_Rate", "Loss_Rate", "Bust_Rate"]])

    st.subheader("Round-level data")
    st.dataframe(data.drop(columns=["Win", "Loss", "Bust"]), hide_index=True)
    st.download_button(
        "Download all round data as CSV",
        data.drop(columns=["Win", "Loss", "Bust"]).to_csv(index=False),
        "blackjack_strategy_data.csv",
        "text/csv",
    )
else:
    st.info("Play a round or simulate a strategy to build the analysis.")
