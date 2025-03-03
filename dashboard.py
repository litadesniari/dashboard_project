import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image

# Konfigurasi halaman
st.set_page_config(page_title="Bike Rental Dashboard", layout="wide")

# Load data dengan caching
@st.cache_data
def load_data():
    day_df = pd.read_csv("day_clean.csv")
    hour_df = pd.read_csv("hour_clean.csv")
    day_df['dteday'] = pd.to_datetime(day_df['dteday'])
    hour_df['dteday'] = pd.to_datetime(hour_df['dteday'])
    return day_df, hour_df

day_df, hour_df = load_data()

# gambar sepeda
image = Image.open("bike.png")
st.sidebar.image(image, use_container_width=True)

# Sidebar Filters
st.sidebar.header(" Filter Data")
st.sidebar.write("Gunakan filter di bawah untuk menyesuaikan tampilan data.")
min_date, max_date = day_df["dteday"].min(), day_df["dteday"].max()
date_selection = st.sidebar.date_input(
    "Pilih Rentang Tanggal:", 
    [min_date.date(), max_date.date()], min_date.date(), max_date.date()
)

# Tangani kasus satu tanggal atau rentang
if isinstance(date_selection, tuple):
    start_date, end_date = date_selection
else:
    start_date = date_selection
    end_date = max_date.date()  # Gunakan tanggal maksimum sebagai akhir rentang

# Filter data berdasarkan rentang tanggal
filtered_day_df = day_df[(day_df["dteday"] >= pd.to_datetime(start_date)) & (day_df["dteday"] <= pd.to_datetime(end_date))]
filtered_hour_df = hour_df[(hour_df["dteday"] >= pd.to_datetime(start_date)) & (hour_df["dteday"] <= pd.to_datetime(end_date))]

# **Dashboard Header**
st.title(" Bike Rental Dashboard")
st.markdown("Analisis data peminjaman sepeda berdasarkan cuaca, musim, hari kerja, dan jam penggunaan.")

# **Menggunakan Layout Berbasis Kolom Tunggal**
st.subheader("️ Pengaruh Cuaca terhadap Penggunaan Sepeda")

weather_map = {1: "Cerah", 2: "Mendung", 3: "Hujan"}
filtered_day_df["Weather Condition"] = filtered_day_df["weathersit"].map(weather_map)

# Hitung rata-rata peminjaman berdasarkan kondisi cuaca
weather_rentals = filtered_day_df.groupby("Weather Condition")["cnt"].mean().reset_index()

# Urutkan dari tinggi ke rendah
weather_rentals = weather_rentals.sort_values(by="cnt", ascending=False)

# Visualisasi hasil
fig1, ax1 = plt.subplots(figsize=(8, 4))
bars = sns.barplot(x="Weather Condition", y="cnt", data=weather_rentals, palette="Blues", ax=ax1)

# Tambahkan label nilai pada batang
for bar in bars.containers:
    ax1.bar_label(bar, fmt="%.0f", label_type="edge", fontsize=10, padding=3)

ax1.set_xlabel("Kondisi Cuaca")
ax1.set_ylabel("Rata-rata Peminjaman")
ax1.set_title("Rata-rata Peminjaman Sepeda Berdasarkan Kondisi Cuaca")
ax1.grid(axis='y', linestyle='--', alpha=0.7)
st.pyplot(fig1)


st.subheader(" Pola Penggunaan Sepeda Berdasarkan Musim")
season_map = {1: "Musim Semi", 2: "Musim Panas", 3: "Musim Gugur", 4: "Musim Dingin"}
filtered_day_df["Season"] = filtered_day_df["season"].map(season_map)

seasonal_rentals = filtered_day_df.groupby("Season")["cnt"].mean().reset_index()
fig2, ax2 = plt.subplots(figsize=(8,4))
sns.barplot(x="Season", y="cnt", data=seasonal_rentals, palette="coolwarm", ax=ax2)
ax2.set_xlabel("Musim")
ax2.set_ylabel("Rata-rata Peminjaman")
ax2.set_title("Rata-rata Peminjaman Sepeda Berdasarkan Musim")
ax2.grid(axis='y', linestyle='--', alpha=0.7)
st.pyplot(fig2)

st.subheader(" Hari Kerja vs Hari Libur")
day_map = {0: "Libur", 1: "Hari Kerja"}
filtered_day_df["Working Day"] = filtered_day_df["workingday"].map(day_map)

workingday_rentals = filtered_day_df.groupby("Working Day")["cnt"].mean().reset_index()
fig3, ax3 = plt.subplots(figsize=(8,4))
sns.barplot(x="Working Day", y="cnt", data=workingday_rentals, palette="Oranges", ax=ax3)
ax3.set_xlabel("Kategori Hari")
ax3.set_ylabel("Rata-rata Peminjaman")
ax3.set_title("Rata-rata Peminjaman Sepeda Berdasarkan Kategori Hari")
ax3.grid(axis='y', linestyle='--', alpha=0.7)
st.pyplot(fig3)

st.subheader("Pola Penggunaan Berdasarkan Jam")
hourly_rentals = filtered_hour_df.groupby("hr")["cnt"].mean().reset_index()

fig4, ax4 = plt.subplots(figsize=(10, 5)) 
sns.lineplot(x="hr", y="cnt", data=hourly_rentals, marker="o", color="blue", ax=ax4) 

ax4.set_title("Rata-rata Penggunaan Sepeda Berdasarkan Jam") 
ax4.set_xlabel("Jam dalam Sehari")
ax4.set_ylabel("Rata-rata Jumlah Penggunaan")
ax4.set_xticks(range(0, 24)) 
ax4.grid(True) 

st.pyplot(fig4)

st.subheader(" Distribusi Peminjaman Sepeda")
# Tentukan batasan bin dan label
bins = [0, 2000, 4000, 6000, 8000]
labels = ["Rendah", "Sedang", "Tinggi", "Sangat Tinggi"]

# Buat kategori berdasarkan jumlah peminjaman sepeda (cnt)
filtered_day_df["usage_category"] = pd.cut(filtered_day_df["cnt"], bins=bins, labels=labels)

# Hitung jumlah hari dalam setiap kategori
category_counts = filtered_day_df["usage_category"].value_counts().reset_index()
category_counts.columns = ["Kategori Penggunaan", "Jumlah Hari"]

# Urutkan dari tinggi ke rendah
category_counts = category_counts.sort_values(by="Jumlah Hari", ascending=False)

# Visualisasi hasil binning
fig5, ax5 = plt.subplots(figsize=(8, 5))
sns.barplot(x="Kategori Penggunaan", y="Jumlah Hari", data=category_counts, palette="coolwarm", ax=ax5)
ax5.set_title("Distribusi Kategori Penggunaan Sepeda")
ax5.set_xlabel("Kategori Penggunaan")
ax5.set_ylabel("Jumlah Hari")
ax5.grid(axis='y', linestyle='--', alpha=0.7)
st.pyplot(fig5)

# **Footer**
st.caption("Sumber Data: day_clean.csv dan hour_clean.csv | Dashboard Analysis by Saniskalita, 2025")