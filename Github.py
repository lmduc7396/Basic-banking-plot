import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Load your data
df_quarter = pd.read_csv('dfsectorquarter.csv')
df_year = pd.read_csv('dfsectoryear.csv')
keyitem=pd.read_excel('Key_items.xlsx')

# Sidebar: Choose database
db_option = st.sidebar.radio(
    "Choose database:",
    ("Quarterly", "Yearly")
)

if db_option == "Quarterly":
    df = df_quarter.copy()
else:
    df = df_year.copy()

# Define your options
bank_type = ['SOCB', 'Private_1', 'Private_2', 'Private_3', 'Sector']
tickers = sorted([x for x in df['TICKER'].unique() if isinstance(x, str) and len(x) == 3])
x_options = tickers + bank_type

X = st.sidebar.selectbox("Select Stock Ticker or Bank Type (X):", x_options)
Y = st.sidebar.number_input("Number of latest periods to plot (Y):", min_value=1, max_value=20, value=10)
Z = st.sidebar.selectbox(
    "Select Value Column (Z):", keyitem['Name'].tolist()
)

df = df.sort_values(by=['TICKER', 'ENDDATE_x'])
item=keyitem[keyitem['Name']==Z]['KeyCode']
item=item.iloc[0]

if len(X)==3:
    df_temp=df[df.TICKER==X]
else:
    df_temp=df[df['TICKER'].apply(len) >3]
    df_temp=df_temp[df_temp['Type']==X]
    df_temp=df_temp[df_temp['TICKER']==df_temp.iloc[0]['TICKER']]

df_tempY = df_temp.tail(Y)

# Plotting with Plotly
fig = go.Figure(
    data=[
        go.Bar(
            x=df_tempY['Date_Quarter'],
            y=df_tempY[item]
        )
    ]
)
fig.update_layout(
    title=f'Bar plot of {X} {Z}',
    xaxis_title='Date_Quarter',
    yaxis_title=Z
)
fig.update_yaxes(tickformat=".2%")

st.plotly_chart(fig, use_container_width=True)
