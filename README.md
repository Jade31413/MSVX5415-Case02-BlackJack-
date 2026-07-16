# Blackjack Lite — Python and Streamlit

A beginner-friendly blackjack strategy experiment with a game, detailed results
table, comparison chart, CSV download, and 10- or 50-round simulations.

## Play it online here -> https://xafpzb2lygzjr34tcclb8r.streamlit.app/
## Play it online here -> https://xafpzb2lygzjr34tcclb8r.streamlit.app/
## Play it online here -> https://xafpzb2lygzjr34tcclb8r.streamlit.app/

## Analysis question

1. **How do human players compare in win rate, loss rate, and bust rate?**
2. **Which automatic play style performs best in the collected simulations?**

The experiment compares three simple strategies:

- **Cautious:** hit below 15, then stand.
- **Standard:** hit below 17, then stand.
- **Aggressive:** hit below 19, then stand.

Each round records the player name, play style, starting hand, dealer up card,
number of hits, number of cards held, final hand, totals, bust status, and result.
This makes it possible to analyze why outcomes differ instead of only counting wins.

## Recommendation features

- The **Current Move Advisor** compares Hit and Stand using 800 possible deals.
  It uses only visible information and reports estimated success and bust rates.
- The **Player & Strategy Analysis** summarizes the named player's past rounds.
  After simulations are collected, it identifies the tested style with the highest
  observed win rate, using the lower bust rate to break a tie.
- Visual cards use a complete shuffled 52-card deck with ranks and suits.

## Run locally

```bash
python3 -m pip install -r requirements.txt
streamlit run app.py
```

## Publish and receive a URL

1. Create a new public GitHub repository.
2. Upload `app.py`, `requirements.txt`, and this `README.md` to its root.
3. Sign in at <https://share.streamlit.io> with GitHub.
4. Choose **Create app**, select the repository, and use `app.py` as the entrypoint.
5. Copy the generated `https://...streamlit.app` URL for the assignment.

## What the code demonstrates

- Variables and lists store cards and totals.
- Functions organize reusable game behavior.
- Conditions decide wins, losses, and ties.
- Loops control the dealer and simulations.
- Random selection creates unpredictable cards.
- Streamlit session state remembers rounds after button clicks.
- Pandas groups the data by strategy and calculates rates and averages.
- The downloadable CSV contains one detailed row for every completed round.
