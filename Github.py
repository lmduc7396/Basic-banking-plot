
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

# Sidebar: Choose pages
page= st.sidebar.selectbox("Choose a page", ("Banking plot","Company Table"))

# Sidebar: Choose database
db_option = st.sidebar.radio("Choose database:", ("Quarterly", "Yearly"))

if db_option == "Quarterly":
    df = df_quarter.copy()
else:
    df = df_year.copy()


def Bankplot():
    # Define your options
    bank_type = ['Sector', 'SOCB', 'Private_1', 'Private_2', 'Private_3']
    tickers = sorted([x for x in df['TICKER'].unique() if isinstance(x, str) and len(x) == 3])
    x_options = bank_type + tickers
    
    col1,col2,col3 = st.columns(3)
    with col1:
        X = st.multiselect("Select Stock Ticker or Bank Type (X):", x_options,
                          default = ['Private_1']
                          )
    with col2:
        Y = st.number_input("Number of latest periods to plot (Y):", min_value=1, max_value=20, value=10)
    with col3:
        Z = st.multiselect(
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
        metric_values=df[value_col].dropna()
        median_value=metric_values.median()
        median_value=abs(median_value)
        row = idx // 2 + 1
        col = idx % 2 + 1
        if median_value > 10:
            tick_format = ",.2s"  # SI units: k, M, B
        else:
            tick_format = ".2%"   # Percent
    
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
        height=1200,
        title_text=f"Banking Metrics: {', '.join(Z)}",
        legend_title="Ticker/Type"
    )
    for i in range(1, len(Z)+1):
        fig.update_yaxes(tickformat=tick_format, row=(i-1)//2 + 1, col=(i-1)%2 + 1)
    
    st.plotly_chart(fig, use_container_width=True)


def Banking_table():
    # Define your options
    bank_type = ['Sector', 'SOCB', 'Private_1', 'Private_2', 'Private_3']
    tickers = sorted([x for x in df['TICKER'].unique() if isinstance(x, str) and len(x) == 3])
    x_options = bank_type + tickers
    
    col1,col2,col3 = st.columns(3)
    with col1:
        X = st.selectbox("Select Stock Ticker or Bank Type (X):", x_options,
                          )
    with col2:
        Y = st.number_input("Number of latest periods to plot (Y):", min_value=1, max_value=20, value=10)

    with col3:
        if db_option == "Quarterly":
            Z = st.selectbox("QoQ or YoY growth (Z):", ['QoQ', 'YoY'], index=0)
        else:
            Z = st.selectbox("YoY (Z):", ['QoQ'], index=1)

    #Set up 
    cols_keep=pd.DataFrame({'Name':['Loan','TOI','Provision expense','PBT','ROA','ROE','NIM','Loan yield','NPL','NPL Formation (%)','GROUP 2','G2 Formation (%)','NPL Coverage ratio','Provision/ Total Loan']})
    cols_code_keep=cols_keep.merge(keyitem,on='Name',how='left')
    cols_keep_final=['Date_Quarter']+cols_code_keep['KeyCode'].tolist()

    #Set up data frame for table
    if X in bank_type:
        df_temp = (df[df['Type'] == X) & (df['TICKER'].apply(len) > 3])
        df_temp= df_temp[cols_keep_final]
    else:
        df_temp = df[df['TICKER'] == X]
        df_temp= df_temp[cols_keep_final]
    
    #Table for QoQ growth
    QoQ_change=df_temp.iloc[:,1:].pct_change()*100
    QoQ_change.columns = QoQ_change.columns.map(
        dict(zip(cols_code_keep['KeyCode'], cols_code_keep['Name'])))
    QoQ_change=QoQ_change.add_suffix(' QoQ (%)')
    QoQ_change=QoQ_change.iloc[:,:4]
    QoQ_change=pd.concat([df_temp['Date_Quarter'],QoQ_change],axis=1)

    #Table for YoY growth
    YoY_change=df_temp.iloc[:,1:].pct_change(periods=4)*100
    YoY_change.columns = YoY_change.columns.map(
        dict(zip(cols_code_keep['KeyCode'], cols_code_keep['Name'])))
    YoY_change=YoY_change.add_suffix(' YoY (%)')
    YoY_change=pd.concat([df_temp['Date_Quarter'],YoY_change],axis=1)

    df_temp.columns = df_temp.columns.map(
        dict(zip(cols_code_keep['KeyCode'], cols_code_keep['Name'])))
    df_temp=df_temp.iloc[:,1:]

    if Z == 'QoQ':
        df_temp= pd.concat([df_temp,QoQ_change],axis=1)
        order=pd.DataFrame(['Date_Quarter','Loan','Loan QoQ (%)','TOI','TOI QoQ (%)','Provision expense','Provision expense QoQ (%)','PBT','PBT QoQ (%)',
                        'ROA','ROE','NIM','Loan yield','NPL','NPL Formation (%)','GROUP 2','G2 Formation (%)','NPL Coverage ratio','Provision/ Total Loan'])
    else:
        df_temp= pd.concat([df_temp,YoY_change],axis=1)
        order=pd.DataFrame(['Date_Quarter','Loan','Loan YoY (%)','TOI','TOI YoY (%)','Provision expense','Provision expense YoY (%)','PBT','PBT YoY (%)',
                        'ROA','ROE','NIM','Loan yield','NPL','NPL Formation (%)','GROUP 2','G2 Formation (%)','NPL Coverage ratio','Provision/ Total Loan'])

    df_temp=df_temp.reindex(columns=order[0])
    df_temp=df_temp.tail(10)
    df_temp=df_temp.T
    df_temp.columns=df_temp.iloc[0]
    df_temp=df_temp[1:]

    # Show the table
    st.write("### Banking Table")
    st.dataframe(df_temp)

if page == "Banking plot":
    #Setup page:
    st.set_page_config(
        page_title="Project Banking Online",
        layout="wide")
    st.subheader("Project Banking Online")
    Bankplot()
elif page == "Company Table":
    #Setup page:
    st.set_page_config(
        layout="wide")
    st.subheader("Table")
    Banking_table()

