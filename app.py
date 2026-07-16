import random

import pandas as pd
import streamlit as st


st.set_page_config(page_title="Blackjack Lite", page_icon="🃏", layout="centered")


# ----- Card and scoring functions -----------------------------------------

def draw_card():
    """Return a random card value. Jack, Queen, and King all equal 10."""
    return random.choice([2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11])


def hand_total(cards):
    """Add the cards, changing an ace from 11 to 1 when needed."""
    total = sum(cards)
    aces = cards.count(11)
    while total > 21 and aces > 0:
        total -= 10
        aces -= 1
    return total


def show_cards(cards):
    """Turn a list such as [11, 10] into the text 'A  10'."""
    return "  ".join("A" if card == 11 else str(card) for card in cards)


def dealer_turn(cards):
    """The dealer must draw while the total is below 17."""
    while hand_total(cards) < 17:
        cards.append(draw_card())
    return cards


def choose_result(player_total, dealer_total):
    """Use conditions to decide the result of one round."""
    if player_total > 21:
        return "Loss"
    if dealer_total > 21 or player_total > dealer_total:
        return "Win"
    if player_total < dealer_total:
        return "Loss"
    return "Tie"


# ----- Session state keeps information after a button is clicked -----------

if "player" not in st.session_state:
    st.session_state.player = [draw_card(), draw_card()]
    st.session_state.dealer = [draw_card(), draw_card()]
    st.session_state.round_over = False
    st.session_state.message = "Choose Hit or Stand."
    st.session_state.history = []


def save_round(result, mode="Played"):
    """Save one completed round as a dictionary for the results table."""
    st.session_state.history.append({
        "Round": len(st.session_state.history) + 1,
        "Mode": mode,
        "Player Total": hand_total(st.session_state.player),
        "Dealer Total": hand_total(st.session_state.dealer),
        "Result": result,
    })
    st.session_state.round_over = True


def new_round():
    st.session_state.player = [draw_card(), draw_card()]
    st.session_state.dealer = [draw_card(), draw_card()]
    st.session_state.round_over = False
    st.session_state.message = "New round! Choose Hit or Stand."


def simulate_round():
    """Simulated player uses one simple rule: hit below 17, then stand."""
    player = [draw_card(), draw_card()]
    dealer = [draw_card(), draw_card()]
    while hand_total(player) < 17:
        player.append(draw_card())
    if hand_total(player) <= 21:
        dealer_turn(dealer)
    return hand_total(player), hand_total(dealer), choose_result(
        hand_total(player), hand_total(dealer)
    )


def run_simulation(number_of_rounds):
    """Add 10 or 50 automatically played rounds to the history."""
    for _ in range(number_of_rounds):
        player_total, dealer_total, result = simulate_round()
        st.session_state.history.append({
            "Round": len(st.session_state.history) + 1,
            "Mode": "Simulation",
            "Player Total": player_total,
            "Dealer Total": dealer_total,
            "Result": result,
        })


# ----- Page and button events ---------------------------------------------

st.title("🃏 Blackjack Lite")
st.caption("Get closer to 21 than the dealer without going over.")

left, right = st.columns(2)
with left:
    dealer_cards = show_cards(st.session_state.dealer)
    if not st.session_state.round_over:
        dealer_cards = str(st.session_state.dealer[0]) + "  ?"
    st.subheader("Dealer")
    st.info(dealer_cards)
with right:
    st.subheader("Your hand")
    st.success(show_cards(st.session_state.player))
    st.write("Total:", hand_total(st.session_state.player))

hit, stand, again = st.columns(3)
if hit.button("Hit", disabled=st.session_state.round_over, use_container_width=True):
    st.session_state.player.append(draw_card())
    if hand_total(st.session_state.player) > 21:
        st.session_state.message = "Bust! You lose."
        save_round("Loss")
    else:
        st.session_state.message = "You drew a card. Hit again or stand?"
    st.rerun()

if stand.button("Stand", disabled=st.session_state.round_over, use_container_width=True):
    dealer_turn(st.session_state.dealer)
    result = choose_result(hand_total(st.session_state.player), hand_total(st.session_state.dealer))
    st.session_state.message = f"{result}! Dealer total: {hand_total(st.session_state.dealer)}"
    save_round(result)
    st.rerun()

if again.button("New Round", use_container_width=True):
    new_round()
    st.rerun()

st.warning(st.session_state.message)


# ----- Analytics, simulations, and data export ----------------------------

st.divider()
st.header("Game Analytics")
sim10, sim50, clear = st.columns(3)
if sim10.button("Simulate 10", use_container_width=True):
    run_simulation(10)
    st.rerun()
if sim50.button("Simulate 50", use_container_width=True):
    run_simulation(50)
    st.rerun()
if clear.button("Clear Data", use_container_width=True):
    st.session_state.history = []
    st.rerun()

if st.session_state.history:
    data = pd.DataFrame(st.session_state.history)
    counts = data["Result"].value_counts().reindex(["Win", "Loss", "Tie"], fill_value=0)
    total = len(data)

    win_rate = 100 * counts["Win"] / total
    loss_rate = 100 * counts["Loss"] / total
    st.metric("Rounds recorded", total)
    st.write(f"Win rate: **{win_rate:.1f}%** · Loss rate: **{loss_rate:.1f}%**")
    st.bar_chart(counts, color="#d4af37")
    st.dataframe(data, hide_index=True, use_container_width=True)
    st.download_button(
        "Download results as CSV",
        data.to_csv(index=False),
        file_name="blackjack_results.csv",
        mime="text/csv",
    )
else:
    st.info("Finish a round or run a simulation to create the chart and table.")
