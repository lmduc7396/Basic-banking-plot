import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Load your data
df_quarter = pd.read_csv('dfsectorquarter.csv')
df_year = pd.read_csv('dfsectoryear.csv')
keyitem = pd.read_excel('Key_items.xlsx')

#Page setting
st.set_page_config(
    page_title="Project Banking Online",
    layout="wide")
st.subheader("Project Banking Online")

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
    keyitem['Name'].tolist(),
    default=['NIM','Loan yield','NPL','GROUP 2']
)

# Create columns for every 2 charts
for i in range(0, len(Z), 2):
    cols = st.columns(2)
    for j, z_name in enumerate(Z[i:i+2]):
        value_col = keyitem[keyitem['Name'] == z_name]['KeyCode'].iloc[0]
        fig = go.Figure()
        for x in X:
            if len(x) == 3:  # Stock ticker
                matched_rows = df[df['TICKER'] == x]
                if not matched_rows.empty:
                    df_tempY = matched_rows.tail(Y)
                    fig.add_trace(go.Scatter(
                        x=df_tempY['Date_Quarter'],
                        y=df_tempY[value_col],
                        mode='lines+markers',
                        name=x
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
                        name=x
                    ))
        fig.update_layout(
            width=1200,  
            height=500, 
            title=f'Line plot of {", ".join(X)}: {z_name}',
            xaxis_title='Date_Quarter',
            yaxis_title=z_name
        )
        fig.update_yaxes(tickformat=".2%")
        cols[j].plotly_chart(fig, use_container_width=True, key=f"{z_name}_{j}")
