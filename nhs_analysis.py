import pandas as pd
import glob
import os

# ================================================
# NHS Appointments Analysis
# Analyst: Azeem Malik
# Data: NHS Digital — Appointments in General 
# Practice April 2026
# ================================================

# Load all regional CSV files and combine them
print("Loading NHS appointment data...")

# Find all Regional CSV files
all_files = glob.glob('Regional_CSV_*.csv')
print(f"Found {len(all_files)} regional files")

# Load and combine all files
df_list = []
for file in all_files:
    df_temp = pd.read_csv(file)
    df_list.append(df_temp)

df = pd.concat(df_list, ignore_index=True)

print(f"Total rows loaded: {len(df):,}")
print(f"Columns: {list(df.columns)}")
print(f"\nFirst 3 rows:")
print(df.head(3).to_string())

# ================================================
# INSPECTION — Check Data Quality
# ================================================

print("\n=== Data Shape ===")
print(f"Rows: {len(df):,}")
print(f"Columns: {len(df.columns)}")

print("\n=== Missing Values ===")
print(df.isnull().sum())

print("\n=== Data Types ===")
print(df.dtypes)

print("\n=== Unique Values In Key Columns ===")
print(f"Regions: {df['REGION_NAME'].nunique()}")
print(f"Months: {df['APPOINTMENT_MONTH'].nunique()}")
print(f"Appt Status: {df['APPT_STATUS'].unique()}")
print(f"HCP Types: {df['HCP_TYPE'].unique()}")
print(f"Appt Modes: {df['APPT_MODE'].unique()}")

# ================================================
# QUESTION 1 — DNA Rate Across Regions
# ================================================

# Group by region and appointment status
region_status = df.groupby(
    ['REGION_NAME', 'APPT_STATUS']
)['COUNT_OF_APPOINTMENTS'].sum().reset_index()

# Calculate total appointments per region
region_total = df.groupby(
    'REGION_NAME'
)['COUNT_OF_APPOINTMENTS'].sum().reset_index()
region_total.columns = ['REGION_NAME', 'TOTAL']

# Get DNA counts only
region_dna = region_status[
    region_status['APPT_STATUS'] == 'DNA'
].copy()
region_dna.columns = ['REGION_NAME', 'APPT_STATUS', 'DNA_COUNT']

# Merge and calculate DNA rate
region_dna = region_dna.merge(region_total, on='REGION_NAME')
region_dna['DNA_RATE'] = round(
    region_dna['DNA_COUNT'] / region_dna['TOTAL'] * 100, 2
)

# Sort by DNA rate highest first
region_dna = region_dna.sort_values('DNA_RATE', ascending=False)

print("\n=== Question 1 — DNA Rate By Region ===")
print(region_dna[['REGION_NAME', 'DNA_COUNT', 'TOTAL', 'DNA_RATE']].to_string(index=False))

# ================================================
# QUESTION 2 — Appointment Mode Trends
# ================================================

# Group by month and appointment mode
mode_trend = df.groupby(
    ['APPOINTMENT_MONTH', 'APPT_MODE']
)['COUNT_OF_APPOINTMENTS'].sum().reset_index()

# Filter out Unknown
mode_trend = mode_trend[
    mode_trend['APPT_MODE'] != 'Unknown'
]

# Get totals per mode across all months
mode_total = mode_trend.groupby(
    'APPT_MODE'
)['COUNT_OF_APPOINTMENTS'].sum().reset_index()
mode_total.columns = ['APPT_MODE', 'TOTAL']
mode_total = mode_total.sort_values('TOTAL', ascending=False)

print("\n=== Question 2 — Appointments By Mode ===")
print(mode_total.to_string(index=False))

# ================================================
# QUESTION 3 — Appointments By HCP Type
# ================================================

# Group by HCP type
hcp_total = df.groupby(
    'HCP_TYPE'
)['COUNT_OF_APPOINTMENTS'].sum().reset_index()
hcp_total.columns = ['HCP_TYPE', 'TOTAL']
hcp_total = hcp_total.sort_values('TOTAL', ascending=False)

# Calculate percentage
hcp_total['PERCENTAGE'] = round(
    hcp_total['TOTAL'] / hcp_total['TOTAL'].sum() * 100, 2
)

print("\n=== Question 3 — Appointments By HCP Type ===")
print(hcp_total.to_string(index=False))

# ================================================
# QUESTION 4 — Busiest Appointment Months
# ================================================

# Group by month
monthly_total = df.groupby(
    'APPOINTMENT_MONTH'
)['COUNT_OF_APPOINTMENTS'].sum().reset_index()
monthly_total.columns = ['MONTH', 'TOTAL_APPOINTMENTS']
monthly_total = monthly_total.sort_values(
    'TOTAL_APPOINTMENTS', ascending=False
)

print("\n=== Question 4 — Top 10 Busiest Months ===")
print(monthly_total.head(10).to_string(index=False))

# ================================================
# QUESTION 5 — Booking Lead Time Analysis
# ================================================

# Group by time between booking and appointment
lead_time = df.groupby(
    'TIME_BETWEEN_BOOK_AND_APPT'
)['COUNT_OF_APPOINTMENTS'].sum().reset_index()
lead_time.columns = ['LEAD_TIME', 'TOTAL']

# Calculate percentage
lead_time['PERCENTAGE'] = round(
    lead_time['TOTAL'] / lead_time['TOTAL'].sum() * 100, 2
)

lead_time = lead_time.sort_values('TOTAL', ascending=False)

print("\n=== Question 5 — Booking Lead Time ===")
print(lead_time.to_string(index=False))

import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style='darkgrid')

# ================================================
# CHART 1 — DNA Rate By Region
# ================================================

plt.figure(figsize=(12, 6))
sns.barplot(
    data=region_dna,
    x='DNA_RATE',
    y='REGION_NAME',
    color='#e74c3c'
)
plt.title('GP Appointment DNA Rate By Region',
          fontsize=16, fontweight='bold', pad=20)
plt.xlabel('DNA Rate (%)', fontsize=12)
plt.ylabel('Region', fontsize=12)
plt.tight_layout()
plt.savefig('nhs_chart1_dna_rate.png', dpi=150)
print("Chart 1 saved.")

# ================================================
# CHART 2 — Appointment Mode Breakdown
# ================================================

plt.figure(figsize=(8, 6))
colors = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12']
plt.pie(
    mode_total['TOTAL'],
    labels=mode_total['APPT_MODE'],
    colors=colors,
    autopct='%1.1f%%',
    startangle=90,
    textprops={'fontsize': 11}
)
plt.title('GP Appointments By Mode',
          fontsize=16, fontweight='bold', pad=20)
plt.tight_layout()
plt.savefig('nhs_chart2_appt_mode.png', dpi=150)
print("Chart 2 saved.")

# ================================================
# CHART 3 — HCP Type Breakdown
# ================================================

plt.figure(figsize=(8, 6))
colors = ['#9b59b6', '#3498db', '#95a5a6']
plt.pie(
    hcp_total['TOTAL'],
    labels=hcp_total['HCP_TYPE'],
    colors=colors,
    autopct='%1.1f%%',
    startangle=90,
    textprops={'fontsize': 11}
)
plt.title('GP Appointments By HCP Type',
          fontsize=16, fontweight='bold', pad=20)
plt.tight_layout()
plt.savefig('nhs_chart3_hcp_type.png', dpi=150)
print("Chart 3 saved.")

# ================================================
# CHART 4 — Top 10 Busiest Months
# ================================================

plt.figure(figsize=(12, 6))
sns.barplot(
    data=monthly_total.head(10),
    x='MONTH',
    y='TOTAL_APPOINTMENTS',
    color='#2ecc71'
)
plt.title('Top 10 Busiest GP Appointment Months',
          fontsize=16, fontweight='bold', pad=20)
plt.xlabel('Month', fontsize=12)
plt.ylabel('Total Appointments', fontsize=12)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('nhs_chart4_busiest_months.png', dpi=150)
print("Chart 4 saved.")

# ================================================
# CHART 5 — Booking Lead Time
# ================================================

plt.figure(figsize=(12, 6))
sns.barplot(
    data=lead_time[lead_time['LEAD_TIME'] != 'Unknown / Data Quality'],
    x='PERCENTAGE',
    y='LEAD_TIME',
    color='#3498db'
)
plt.title('GP Appointment Booking Lead Time',
          fontsize=16, fontweight='bold', pad=20)
plt.xlabel('Percentage of Appointments (%)', fontsize=12)
plt.ylabel('Time Between Booking and Appointment', fontsize=12)
plt.tight_layout()
plt.savefig('nhs_chart5_lead_time.png', dpi=150)
print("Chart 5 saved.")

print("\nAll NHS charts saved successfully!")