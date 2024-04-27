import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import altair as alt
import calendar
from bokeh.plotting import figure
from bokeh.models import RangeTool

# Load data
@st.cache
def load_data():
    df = pd.read_csv("./MarketData.csv")
    df['Date'] = pd.to_datetime(df['Date'])
    df['Price_Change'] = df['Adj Close'] - df['Open']
    df['Price_Change_Direction'] = df['Price_Change'].apply(lambda x: 1 if x > 0 else 0)
    df['Price_Percentage_Change'] = ((df['Close'] - df['Open']) / df['Open']) * 100
    df['Price_Percentage_Change_Direction'] = df['Price_Percentage_Change'].apply(lambda x: 1 if x > 0 else 0)
    df['Moving_Average'] = df['Adj Close'].rolling(window=5).mean()
    return df

df = load_data()

# Sidebar for year selection
unique_years = sorted(df['Date'].dt.year.unique())
year = st.sidebar.selectbox('Select Year:', unique_years)

# Visualization 1: Counts of losses and profits occurred per day by Ticker
filtered_data = df[df['Date'].dt.year == year]
grouped_data = filtered_data.groupby('Ticker')['Price_Change_Direction'].value_counts().unstack().fillna(0)
fig, ax = plt.subplots(figsize=(10, 6))
grouped_data.plot(kind='bar', stacked=True, ax=ax, color=['red', 'green'])
ax.set_title(f"Counts of Losses and Profits by Ticker in {year}")
ax.set_ylabel("Count")
ax.set_xlabel("Ticker")
st.pyplot(fig)

# Visualization 2: Bar Chart of Price Percentage Change
filtered_data = df[df['Date'].dt.year == year]
st.bar_chart(filtered_data[['Date', 'Price_Percentage_Change']].set_index('Date'))

# Visualization 3: Monthly Volume Sum for Each Ticker in Selected Year
months_order = [calendar.month_name[i] for i in range(1, 13)]
alt_chart = alt.Chart(filtered_data).mark_bar().encode(
    x=alt.X('Month_Name:O', title='Month', sort=months_order),
    y='sum(Volume):Q',
    color='Ticker_Name:N'
).properties(title="Monthly Volume Sum for Each Ticker")
st.altair_chart(alt_chart, use_container_width=True)

# Visualization 4: Line chart with interactive range selection
p = figure(title="Adjusted Close Over Time", x_axis_type="datetime",
           x_range=(filtered_data['Date'].min(), filtered_data['Date'].max()), height=300, width=700)
p.line(filtered_data['Date'], filtered_data['Adj Close'], color='navy', legend_label='Adj Close')
range_tool = RangeTool(x_range=p.x_range)
range_tool.overlay.fill_color = 'navy'
range_tool.overlay.fill_alpha = 0.2
p.add_tools(range_tool)
st.bokeh_chart(p, use_container_width=True)
