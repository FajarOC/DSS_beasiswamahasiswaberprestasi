import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.config import get_connection

st.set_page_config(page_title="Ranking Beasiswa", layout="wide")
st.title("🏆 Hasil Ranking Beasiswa")

conn = get_connection()

query = """
SELECT
    m.nim,
    m.nama,
    m.prodi,
    h.total_skor,
    h.ranking_ke,
    h.status_acc
FROM mahasiswa m
JOIN hasil_saw h
ON m.nim = h.nim
ORDER BY h.ranking_ke
"""

df = pd.read_sql(query, conn)

# Pastikan status_acc adalah integer dan hanya bernilai 0 atau 1
df['status_acc'] = pd.to_numeric(df['status_acc'], errors='coerce').fillna(0).astype(int)

# ============ SECTION 1: STATISTIK RINGKAS ============
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("📊 Total Peserta", len(df))

with col2:
    accepted = len(df[df['status_acc'] == 1]) if 'status_acc' in df.columns else 0
    st.metric("✅ Diterima", accepted)

with col3:
    if len(df) > 0:
        max_skor = df['total_skor'].max()
        st.metric("🎯 Skor Tertinggi", f"{max_skor:.4f}")

with col4:
    if len(df) > 0:
        min_skor = df['total_skor'].min()
        st.metric("📉 Skor Terendah", f"{min_skor:.4f}")

st.divider()

# ============ SECTION 2: PODIUM TOP 3 ============
if len(df) >= 3:
    st.subheader("🥇 Podium Tertinggi")
    
    podium_col1, podium_col2, podium_col3 = st.columns([1, 1, 1])
    
    # Peringkat 2 (kiri)
    with podium_col1:
        rank2 = df.iloc[1]
        st.markdown(
            f"""
            <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #c0c0c0, #e8e8e8); 
            border-radius: 15px; border: 3px solid #c0c0c0;'>
                <h2>🥈</h2>
                <h3 style='margin: 10px 0;'>Peringkat 2</h3>
                <p style='font-size: 20px; font-weight: bold; color: #333;'>{rank2['nama']}</p>
                <p style='font-size: 14px; color: #666;'>{rank2['prodi']}</p>
                <p style='font-size: 16px; color: #c0c0c0; font-weight: bold;'>Skor: {rank2['total_skor']:.4f}</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # Peringkat 1 (tengah)
    with podium_col2:
        rank1 = df.iloc[0]
        st.markdown(
            f"""
            <div style='text-align: center; padding: 30px; background: linear-gradient(135deg, #FFD700, #FFA500); 
            border-radius: 15px; border: 3px solid #FFD700; margin-top: -20px;'>
                <h1>🥇</h1>
                <h2 style='margin: 10px 0;'>Peringkat 1</h2>
                <p style='font-size: 22px; font-weight: bold; color: #fff;'>{rank1['nama']}</p>
                <p style='font-size: 16px; color: #fff;'>{rank1['prodi']}</p>
                <p style='font-size: 18px; color: #fff; font-weight: bold;'>Skor: {rank1['total_skor']:.4f}</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # Peringkat 3 (kanan)
    with podium_col3:
        rank3 = df.iloc[2]
        st.markdown(
            f"""
            <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #CD7F32, #DAA520); 
            border-radius: 15px; border: 3px solid #CD7F32;'>
                <h2>🥉</h2>
                <h3 style='margin: 10px 0;'>Peringkat 3</h3>
                <p style='font-size: 20px; font-weight: bold; color: #fff;'>{rank3['nama']}</p>
                <p style='font-size: 14px; color: #fff;'>{rank3['prodi']}</p>
                <p style='font-size: 16px; color: #fff; font-weight: bold;'>Skor: {rank3['total_skor']:.4f}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

st.divider()

# ============ SECTION 4: TABEL RANKING LENGKAP ============
st.subheader("📋 Daftar Ranking Lengkap")

# Filter dan pencarian
col_filter1, col_filter2, col_filter3 = st.columns(3)

with col_filter1:
    search_nama = st.text_input("🔍 Cari Nama", placeholder="Ketik nama mahasiswa...")

with col_filter2:
    prodi_list = df['prodi'].unique().tolist()
    selected_prodi = st.multiselect("📚 Filter Prodi", prodi_list, default=prodi_list)

with col_filter3:
    status_filter = st.selectbox(
        "✅ Status",
        ["Semua", "Diterima", "Tidak Diterima"]
    )

# Apply filters
df_filtered = df.copy()

if search_nama:
    df_filtered = df_filtered[df_filtered['nama'].str.contains(search_nama, case=False, na=False)]

df_filtered = df_filtered[df_filtered['prodi'].isin(selected_prodi)]

if status_filter == "Diterima":
    df_filtered = df_filtered[df_filtered['status_acc'] == 1]
elif status_filter == "Tidak Diterima":
    df_filtered = df_filtered[df_filtered['status_acc'] == 0]

# Format untuk display
df_display = df_filtered.copy()
df_display['ranking_ke'] = df_display['ranking_ke'].astype(int)
df_display['total_skor'] = df_display['total_skor'].apply(lambda x: f"{x:.4f}")
df_display['Status'] = df_display['status_acc'].apply(
    lambda x: "✅ Diterima" if x == 1 else "❌ Tidak Diterima"
)

# Dropdown columns untuk display
df_display = df_display[['ranking_ke', 'nim', 'nama', 'prodi', 'total_skor', 'Status']]
df_display.columns = ['Ranking', 'NIM', 'Nama', 'Prodi', 'Skor', 'Status']

# Tampilkan tabel dengan styling
st.dataframe(
    df_display,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Ranking": st.column_config.NumberColumn(width="small"),
        "NIM": st.column_config.TextColumn(width="medium"),
        "Nama": st.column_config.TextColumn(),
        "Prodi": st.column_config.TextColumn(),
        "Skor": st.column_config.TextColumn(width="small"),
        "Status": st.column_config.TextColumn(width="medium"),
    }
)

# Info hasil filter
if len(df_filtered) > 0:
    st.info(f"📊 Menampilkan {len(df_filtered)} dari {len(df)} peserta")
else:
    st.warning("⚠️ Tidak ada data yang sesuai dengan filter")

st.divider()

# ============ SECTION 5: RINGKASAN ============
st.subheader("📌 Ringkasan")
col_summary1, col_summary2, col_summary3 = st.columns(3)

with col_summary1:
    avg_skor = df['total_skor'].mean()
    st.metric("Rata-rata Skor", f"{avg_skor:.4f}")

with col_summary2:
    median_skor = df['total_skor'].median()
    st.metric("Median Skor", f"{median_skor:.4f}")

with col_summary3:
    std_skor = df['total_skor'].std()
    st.metric("Standar Deviasi", f"{std_skor:.4f}")