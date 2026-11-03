import pandas as pd
import sqlite3

df = pd.read_csv("earthquakes_cleaned.csv")
df['time'] = pd.to_datetime(df['time'], errors='coerce')

# Auto fix missing columns if your CSV is old
if 'hour' not in df.columns:
    df['hour'] = df['time'].dt.hour
if 'year' not in df.columns:
    df['year'] = df['time'].dt.year
if 'month' not in df.columns:
    df['month'] = df['time'].dt.month
if 'day_of_week' not in df.columns:
    df['day_of_week'] = df['time'].dt.day_name()
if 'depth_category' not in df.columns:
    df['depth_category'] = pd.cut(df['depth_km'], bins=[0,70,300,1000], labels=['Shallow','Intermediate','Deep'])
if 'country' not in df.columns:
    df['country'] = df['place'].str.split(',').str[-1].str.strip()

df.to_csv("earthquakes_cleaned.csv", index=False)

conn = sqlite3.connect("seismic.db")
df.to_sql("earthquakes", conn, if_exists="replace", index=False)

queries = {
    "Q1": "SELECT place, mag, country, time FROM earthquakes ORDER BY mag DESC LIMIT 10",
    "Q2": "SELECT place, depth_km, mag, country FROM earthquakes ORDER BY depth_km DESC LIMIT 10",
    "Q3": "SELECT place, depth_km, mag FROM earthquakes WHERE depth_km < 50 AND mag > 7.5",
    "Q5": "SELECT magType, COUNT(*) as total, ROUND(AVG(mag),2) as avg_mag FROM earthquakes GROUP BY magType ORDER BY avg_mag DESC",
    "Q6": "SELECT year, COUNT(*) as cnt FROM earthquakes GROUP BY year ORDER BY cnt DESC",
    "Q7": "SELECT month, COUNT(*) as cnt FROM earthquakes GROUP BY month ORDER BY cnt DESC",
    "Q8": "SELECT day_of_week, COUNT(*) as cnt FROM earthquakes GROUP BY day_of_week ORDER BY cnt DESC",
    "Q9": "SELECT hour, COUNT(*) as cnt FROM earthquakes GROUP BY hour ORDER BY hour",
    "Q10": "SELECT net, COUNT(*) as cnt FROM earthquakes GROUP BY net ORDER BY cnt DESC LIMIT 10",
    "Q11": "SELECT place, country, sig, mag FROM earthquakes ORDER BY sig DESC LIMIT 5",
    "Q13": "SELECT CASE WHEN sig > 1000 THEN 'red' WHEN sig > 500 THEN 'orange' ELSE 'green' END as alert_level, COUNT(*) as cnt FROM earthquakes GROUP BY alert_level",
    "Q14": "SELECT status, COUNT(*) as cnt FROM earthquakes GROUP BY status",
    "Q15": "SELECT type, COUNT(*) as cnt FROM earthquakes GROUP BY type",
    "Q16": "SELECT types, COUNT(*) as cnt FROM earthquakes GROUP BY types ORDER BY cnt DESC LIMIT 10",
    "Q18": "SELECT place, nst, mag, country FROM earthquakes WHERE nst > 50 ORDER BY nst DESC LIMIT 20",
    "Q19": "SELECT year, COUNT(*) as total, SUM(tsunami) as tsunami_count FROM earthquakes GROUP BY year ORDER BY year DESC",
    "Q20": "SELECT CASE WHEN sig >= 1000 THEN 'red' WHEN sig >= 750 THEN 'orange' WHEN sig >= 500 THEN 'yellow' ELSE 'green' END as alert, COUNT(*) as cnt FROM earthquakes GROUP BY alert",
    "Q22": "SELECT country, year, month FROM earthquakes GROUP BY country, year, month HAVING SUM(CASE WHEN depth_category='Shallow' THEN 1 ELSE 0 END)>0 AND SUM(CASE WHEN depth_category='Deep' THEN 1 ELSE 0 END)>0 LIMIT 20",
    "Q23": "SELECT year, COUNT(*) as cnt FROM earthquakes GROUP BY year ORDER BY year",
    "Q25": "SELECT country, COUNT(*) as cnt, ROUND(AVG(depth_km),2) as avg_depth FROM earthquakes WHERE latitude BETWEEN -5 AND 5 GROUP BY country ORDER BY avg_depth DESC",
    "Q26": "SELECT country, SUM(CASE WHEN depth_category='Shallow' THEN 1 ELSE 0 END) as shallow, SUM(CASE WHEN depth_category='Deep' THEN 1 ELSE 0 END) as deep FROM earthquakes GROUP BY country HAVING deep>0 ORDER BY shallow DESC LIMIT 10",
    "Q27": "SELECT ROUND(AVG(CASE WHEN tsunami=1 THEN mag END),2) as avg_tsunami, ROUND(AVG(CASE WHEN tsunami=0 THEN mag END),2) as avg_no_tsunami FROM earthquakes",
    "Q28": "SELECT place, gap, rms, mag FROM earthquakes ORDER BY gap DESC LIMIT 20",
    "Q29": "SELECT place FROM earthquakes LIMIT 20",
    "Q30": "SELECT country, COUNT(*) as deep_count, ROUND(AVG(mag),2) as avg_mag FROM earthquakes WHERE depth_km>300 GROUP BY country ORDER BY deep_count DESC LIMIT 10"
}

for name, sql in queries.items():
    result = pd.read_sql_query(sql, conn)
    print(name, result.shape)
    print(result.head(2))
    print()

conn.close()

with open("app.py", "w") as f:
    f.write('import streamlit as st\nimport pandas as pd\nimport plotly.express as px\ndf = pd.read_csv("earthquakes_cleaned.csv")\nst.title("Global Seismic Trends")\nst.write(len(df))\nst.dataframe(df.head())\nst.plotly_chart(px.histogram(df, x="mag"))\nst.plotly_chart(px.scatter(df, x="depth_km", y="mag"))\n')