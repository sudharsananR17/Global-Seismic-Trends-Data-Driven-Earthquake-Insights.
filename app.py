import streamlit as st
import pandas as pd
import plotly.express as px
df = pd.read_csv("earthquakes_cleaned.csv")
st.title("Global Seismic Trends")
st.write(len(df))
st.dataframe(df.head())
st.plotly_chart(px.histogram(df, x="mag"))
st.plotly_chart(px.scatter(df, x="depth_km", y="mag"))
