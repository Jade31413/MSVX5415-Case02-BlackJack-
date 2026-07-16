# Blackjack Lite — Python and Streamlit

A beginner-friendly blackjack game with a results table, win/loss chart, CSV
download, and buttons that simulate 10 or 50 rounds.

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
- Pandas creates a table and downloadable CSV file.
