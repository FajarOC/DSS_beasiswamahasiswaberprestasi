import streamlit as st
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.config import initialize_database, get_connection

# Inisialisasi database
initialize_database()

# Konfigurasi halaman
st.set_page_config(
    page_title="DSS Beasiswa SAW",
    page_icon="🎓",
    layout="wide"
)

# Ambil statistik dinamis dari database
mahasiswa_count = 0
penerima_count = 0
kriteria_count = 5

try:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM mahasiswa")
    mahasiswa_count = cursor.fetchone()[0] or 0
    cursor.execute("SELECT COUNT(*) FROM hasil_saw WHERE status_acc = 1")
    penerima_count = cursor.fetchone()[0] or 0
    cursor.close()
    conn.close()
except Exception as e:
    st.warning(f"⚠️ Gagal memuat statistik dashboard: {e}")

# CSS Custom
st.markdown("""
<style>
.main-title {
    text-align: center;
    font-size: 42px;
    font-weight: bold;
    color: #1E88E5;
}

.sub-title {
    text-align: center;
    font-size: 20px;
    color: #666;
}

.card {
    background-color: #f8f9fa;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.1);
}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown(
    '<p class="main-title">🎓 Sistem Pendukung Keputusan Penerima Beasiswa</p>',
    unsafe_allow_html=True
)

st.markdown(
    '<p class="sub-title">Metode Simple Additive Weighting (SAW)</p>',
    unsafe_allow_html=True
)

st.divider()

# Statistik Dashboard
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="👨‍🎓 Data Mahasiswa",
        value=mahasiswa_count,
        delta="Aktif"
    )

with col2:
    st.metric(
        label="📋 Kriteria",
        value=kriteria_count,
        delta="Tetap"
    )

with col3:
    st.metric(
        label="🏆 Penerima",
        value=penerima_count,
        delta="Sudah dihitung"
    )

with col4:
    st.metric(
        label="⚡ Metode",
        value="SAW"
    )

st.divider()

# Informasi Sistem
left, right = st.columns([2, 1])

with left:
    st.markdown("""
    ### 📖 Tentang Sistem

    Sistem Pendukung Keputusan (SPK) ini digunakan untuk membantu
    proses seleksi penerima beasiswa secara objektif menggunakan
    metode **Simple Additive Weighting (SAW)**.

    ### 🎯 Kriteria Penilaian

    - 📚 IPK
    - 💰 Penghasilan Orang Tua
    - 👨‍👩‍👧‍👦 Jumlah Tanggungan
    - 🏅 Prestasi
    - 🤝 Keaktifan Organisasi

    ### ⚙️ Alur Sistem

    1. Input Data Mahasiswa
    2. Input Nilai Kriteria
    3. Proses Perhitungan SAW
    4. Perankingan
    5. Penentuan Penerima Beasiswa
    """)

with right:
    st.info("""
    📌 **Informasi**

    Sistem ini membantu proses seleksi penerima beasiswa secara
    cepat, transparan, dan objektif.
    """)

    st.success("""
    ✅ Database Terhubung

    Status sistem siap digunakan.
    """)

st.divider()

# Footer
st.caption(
    "© 2026 DSS Penerima Beasiswa | Metode Simple Additive Weighting (SAW)"
)