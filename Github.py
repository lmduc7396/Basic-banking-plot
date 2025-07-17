import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Load your data
df_quarter = pd.read_csv('dfsectorquarter.csv')
df_year = pd.read_csv('dfsectoryear.csv')
keyitem=pd.read_excel('Key_items.xlsx')
color_sequence=px.colors.qualitative.Bold

# Sidebar: Choose database
db_option = st.sidebar.radio("Choose database:", ("Quarterly", "Yearly"))

if db_option == "Quarterly":
    df = df_quarter.copy()
else:
    df = df_year.copy()

# Define your options
bank_type = ['Sector', 'SOCB', 'Private_1', 'Private_2', 'Private_3']
tickers = sorted([x for x in df['TICKER'].unique() if isinstance(x, str) and len(x) == 3])
x_options = bank_type + tickers

X = st.sidebar.multiselect("Select Stock Ticker or Bank Type (X):", x_options)
Y = st.sidebar.number_input("Number of latest periods to plot (Y):", min_value=1, max_value=20, value=10)
Z = st.sidebar.multiselect(
    "Select Value Column(s) (Z):", 
    keyitem['Name'].tolist()
)
if len(Z) > 4:
    st.warning("Please select up to 4 metrics only!")
    Z = Z[:4]

# Loop for each Z
for z_name in Z:
    value_col = keyitem[keyitem['Name']==z_name]['KeyCode'].iloc[0]
    fig = go.Figure()
    for i, x in enumerate(X):
        if len(x) == 3:  # Stock ticker
            matched_rows = df[df['TICKER'] == x]
            if not matched_rows.empty:
                df_tempY = matched_rows.tail(Y)
                fig.add_trace(go.Scatter(
                    x=df_tempY['Date_Quarter'],
                    y=df_tempY[value_col],
                    mode='lines+markers',
                    name=x,
                    line=dict(color=color_sequence[i % len(color_sequence)])
                ))
        else:  # Bank type
            matched_rows = df[(df['Type'] == x) & (df['TICKER'].apply(len) > 3)]
            if not matched_rows.empty:
                primary_ticker = matched_rows.iloc[0]['TICKER']
                df_tempY = matched_rows[matched_rows['TICKER'] == primary_ticker].tail(Y)
                fig.add_trace(go.Scatter(
                    x=df_tempY['Date_Quarter'],
                    y=df_tempY[value_col],
                    mode='lines+markers',
                    name=x,
                    line=dict(color=color_sequence[i % len(color_sequence)])
                ))
    fig.update_layout(
        title=f'Line plot of {', '.join(X)}: {z_name}',
        xaxis_title='Date_Quarter',
        yaxis_title=z_name
    )
    fig.update_yaxes(tickformat=".2%")
    st.plotly_chart(fig, use_container_width=True)
