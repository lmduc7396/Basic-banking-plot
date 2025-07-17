import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# Load your data
df_quarter = pd.read_csv('dfsectorquarter.csv')
df_year = pd.read_csv('dfsectoryear.csv')
keyitem=pd.read_excel('Key_items.xlsx')
color_sequence=px.colors.qualitative.Bold

# Sidebar: Choose database
st.set_page_config(
    page_title="Project Banking Online",
    layout="wide")
st.subheader("Project Banking Online")
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
    default = ['NIM','Loan yield','NPL','GROUP 2','NPL Formation (%)', 'G2 Formation (%)']
)

#Setup subplot

rows = len(Z) // 2 + 1
cols = 2 if len(Z) > 1 else 1

fig = make_subplots(
    rows=rows, 
    cols=cols, 
    subplot_titles=Z
)

#Draw chart

for idx, z_name in enumerate(Z):
    value_col = keyitem[keyitem['Name']==z_name]['KeyCode'].iloc[0]
    row = idx // 2 + 1
    col = idx % 2 + 1

    for i, x in enumerate(X):
        show_legend = (idx == 0)
        if len(x) == 3:  # Stock ticker
            matched_rows = df[df['TICKER'] == x]
            if not matched_rows.empty:
                df_tempY = matched_rows.tail(Y)
                fig.add_trace(
                    go.Scatter(
                        x=df_tempY['Date_Quarter'],
                        y=df_tempY[value_col],
                        mode='lines+markers',
                        name=str(x),
                        line=dict(color=color_sequence[i % len(color_sequence)]),
                        showlegend = show_legend
                    ),
                    row=row,
                    col=col
                )
        else:  # Bank type
            matched_rows = df[(df['Type'] == x) & (df['TICKER'].apply(len) > 3)]
            if not matched_rows.empty:
                primary_ticker = matched_rows.iloc[0]['TICKER']
                df_tempY = matched_rows[matched_rows['TICKER'] == primary_ticker].tail(Y)
                fig.add_trace(
                    go.Scatter(
                        x=df_tempY['Date_Quarter'],
                        y=df_tempY[value_col],
                        mode='lines+markers',
                        name=str(x),
                        line=dict(color=color_sequence[i % len(color_sequence)]),
                        showlegend = show_legend
                    ),
                    row=row,
                    col=col
                )

fig.update_layout(
    width=1400,
    height=1400,
    title_text=f"Banking Metrics: {', '.join(Z)}",
    legend_title="Ticker/Type"
)
for i in range(1, len(Z)+1):
    fig.update_yaxes(tickformat=".2%", row=(i-1)//2 + 1, col=(i-1)%2 + 1)

st.plotly_chart(fig, use_container_width=True)
