# streamlit_app.py
import streamlit as st
import pandas as pd
import openai
from datetime import datetime, timedelta

# Set the OpenAI API key from Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

st.set_page_config(page_title="🏈 NCAA Betting AI Bot", layout="centered")
st.title("🏈 NCAA Football Advanced Betting Prompt Bot")

# File uploader
uploaded_file = st.file_uploader("Upload your daily slate CSV file", type=["csv"])

# Time window filter (60–75 minutes before kickoff)
time_window = st.slider("How far in advance should the analysis run? (minutes)", 60, 120, 75)

# Run analysis button
run_button = st.button("Run Game Prompt(s)")

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Check for required columns
    required_columns = ["Team 1", "Team 2", "Start Time"]
    if not all(col in df.columns for col in required_columns):
        st.error(f"CSV must contain the following columns: {', '.join(required_columns)}")
    else:
        # Parse start times
        df['Start Time'] = pd.to_datetime(df['Start Time'])
        now = datetime.now()

        # Filter games starting within the time window
        window_start = now + timedelta(minutes=0)
        window_end = now + timedelta(minutes=time_window)
        eligible_games = df[(df['Start Time'] >= window_start) & (df['Start Time'] <= window_end)]

        if run_button:
            if eligible_games.empty:
                st.warning("No games starting within the selected time window.")
            else:
                for idx, row in eligible_games.iterrows():
                    team1, team2, game_time = row["Team 1"], row["Team 2"], row["Start Time"]

                    st.subheader(f"🧠 Pre-Flight Risk Filter: {team1} vs {team2}")
                    
                    prompt = f"""
Run Advanced Betting Mode for this NCAA football matchup.
Matchup: {team1} vs {team2} on {game_time.strftime('%Y-%m-%d %I:%M %p')}

---

⚡️ Pre-Flight Risk Filter: Macro Risk Check
Before syncing any data, scan for:
- Rivalry game or revenge spot
- Lookahead (vs ranked team or conference showdown)
- Letdown spot (after upset or emotional win)
- Cross-country or timezone travel
- Sharp/public alignment + line movement with no injury confirmation

Respond with:
✅ Clean Spot
⚠️ Caution Signal
❌ Trap Game

Then give a 3-5 sentence explanation.
"""

                    with st.spinner(f"Analyzing {team1} vs {team2}..."):
                        try:
                            response = openai.ChatCompletion.create(
                                model="gpt-4",
                                messages=[
                                    {"role": "system", "content": "You are an expert sports betting model analyst."},
                                    {"role": "user", "content": prompt}
                                ],
                                temperature=0.7
                            )
                            result = response["choices"][0]["message"]["content"]
                            st.markdown(result)

                            proceed = st.radio(
                                f"✅ Do you want to continue with Step 2 for {team1} vs {team2}?",
                                ("Yes", "No"),
                                key=f"step2_{idx}"
                            )

                            if proceed == "Yes":
                                st.info("✅ Step 2 coming soon: Injury Report + Depth Chart Analysis")

                        except Exception as e:
                            st.error(f"Error from OpenAI API: {e}")
