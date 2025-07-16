import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Load your data
df_quarter = pd.read_csv('dfsectorquarter.csv')
df_year = pd.read_csv('dfsectoryear.csv')
keyitem = pd.read_excel('Key_items.xlsx')

# Sidebar: Choose database
db_option = st.sidebar.radio("Choose database:", ("Quarterly", "Yearly"))

if db_option == "Quarterly":
    df = df_quarter.copy()
else:
    df = df_year.copy()

# Define your options
bank_type = ['SOCB', 'Private_1', 'Private_2', 'Private_3', 'Sector']
tickers = sorted([x for x in df['TICKER'].unique() if isinstance(x, str) and len(x) == 3])
x_options = tickers + bank_type

X = st.sidebar.multiselect("Select Stock Ticker or Bank Type (X):", x_options)
Y = st.sidebar.number_input("Number of latest periods to plot (Y):", min_value=1, max_value=20, value=10)
Z = st.sidebar.selectbox("Select Value Column (Z):", keyitem['Name'].tolist())

# Get the column name for Z
code_row = keyitem[keyitem['Name'] == Z]['KeyCode']
if not code_row.empty:
    value_col = code_row.iloc[0]
else:
    value_col = Z  # fallback, just in case

df = df.sort_values(by=['TICKER', 'ENDDATE_x'])

results = []
for x in X:
    if len(x) == 3:  # Stock ticker
        matched_rows = df[df['TICKER'] == x]
        if not matched_rows.empty:
            results.append(matched_rows)
    else:  # Bank type
        matched_rows = df[(df['Type'] == x) & (df['TICKER'].apply(len) > 3)]
        if not matched_rows.empty:
            # Get the latest group for the first TICKER in this type
            primary_ticker = matched_rows.iloc[0]['TICKER']
            matched_rows = matched_rows[matched_rows['TICKER'] == primary_ticker]
            results.append(matched_rows)

if results:
    df_temp = pd.concat(results)
    df_tempY = df_temp.tail(Y)

    fig = go.Figure(
        data=[
            go.Bar(
                x=df_tempY['Date_Quarter'],
                y=df_tempY[value_col],
            )
        ]
    )
    fig.update_layout(
        title=f'Bar plot of {", ".join(X)} {Z}',
        xaxis_title='Date_Quarter',
        yaxis_title=Z
    )
    fig.update_yaxes(tickformat=".2%")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("No data matched your selection. Please adjust X or check your dataset.")
