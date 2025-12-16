import streamlit as st
import pandas as pd
from sleeper_wrapper import League

# -------------------------------
# Streamlit setup
# -------------------------------
st.set_page_config(page_title="League Scoreboards")
st.title(":blue[2025 Guillotine League Championship Scoreboards]")

# -------------------------------
# Helper function to build scoreboard
# -------------------------------
def build_scoreboard(leagueid, final_four, title):
    league = League(leagueid)

    # Detect current week dynamically
    currentweek = 0
    for wk in range(1, 18):
        data = league.get_matchups(wk)
        if not data:
            break
        currentweek = wk

    if currentweek == 0:
        st.error(f"Could not determine current week for league {leagueid}")
        return

    # Users and rosters
    users = pd.DataFrame(league.get_users())
    rosters = pd.DataFrame(league.get_rosters())
    users_df = pd.merge(
        rosters[['roster_id','owner_id']],
        users[['user_id','display_name']],
        left_on='owner_id', right_on='user_id'
    )
    users_df = users_df[['display_name','roster_id']]
    users_df.rename(columns={'display_name':'Manager'}, inplace=True)

    # Expand weeks
    df = users_df.loc[users_df.index.repeat(currentweek)].reset_index(drop=True)
    df['Week'] = df.groupby('Manager').cumcount() + 1

    # Matchups
    all_matchups = pd.DataFrame()
    for i in range(1, currentweek + 1):
        data = league.get_matchups(i)
        if not data:
            break
        data1 = pd.DataFrame(data)
        data1['Week'] = i
        all_matchups = pd.concat([all_matchups, data1])

    all_matchups = pd.merge(all_matchups, users_df, on='roster_id')
    all_matchups = pd.merge(df, all_matchups, on=['Manager','Week'], how='left')

    all_matchups.rename(columns={"points": "Points"}, inplace=True)
    all_matchups = all_matchups[['Week','Manager','Points']]
    all_matchups['Points'] = all_matchups['Points'].astype(float)
    all_matchups['Cumulative Points'] = all_matchups.groupby('Manager')['Points'].cumsum()

    # Championship filter
    championship_weeks = range(15, currentweek + 1)
    all_matchups = all_matchups[
        all_matchups['Manager'].isin(final_four) &
        all_matchups['Week'].isin(championship_weeks)
    ]

    # Wide table
    all_matchups_wide = all_matchups.pivot(index='Manager', columns='Week', values='Points')
    all_matchups_wide['Total'] = all_matchups_wide.sum(axis=1)
    all_matchups_wide = all_matchups_wide.sort_values(by='Total', ascending=False)

    st.subheader(title)
    st.dataframe(all_matchups_wide)

# -------------------------------
# Tabs for multiple leagues
# -------------------------------
tab1, tab2 = st.tabs(["A Cut Above", "You Blew It!"])

with tab1:
    build_scoreboard(
        leagueid="1268223965571072000",
        final_four=["mswatek","Brandon5592","CircletheWagon60","naghazzoul"],
        title="A Cut Above - Championship Scoreboard"
    )

with tab2:
    build_scoreboard(
        leagueid="1269040885585170432",
        final_four=["ZN715","40fnNiners","rbd85","trazdoor"],
        title="You Blew It! - Championship Scoreboard"
    )