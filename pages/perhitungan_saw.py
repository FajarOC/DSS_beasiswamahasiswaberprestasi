import streamlit as st
import pandas as pd
import sys
import os
import time

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.saw import hitung_saw

st.set_page_config(page_title="Perhitungan SAW", layout="wide")

# Custom styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 30px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        color: white;
        margin-bottom: 30px;
    }
    .info-box {
        background: #e3f2fd;
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #2196f3;
        margin-bottom: 20px;
    }
    .parameter-box {
        background: #f5f5f5;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #ddd;
        margin: 10px 0;
    }
    .success-box {
        background: #d4edda;
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #28a745;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h1>⚙️ Perhitungan SAW (Simple Additive Weighting)</h1>
    <p>Sistem penilaian berbasis metode SAW untuk penentuan penerima beasiswa</p>
</div>
""", unsafe_allow_html=True)

# ============ INFORMASI METODE SAW ============
with st.expander("📚 Tentang Metode SAW", expanded=False):
    st.markdown("""
    ### Simple Additive Weighting (SAW)
    
    SAW adalah metode Multi-Criteria Decision Making (MCDM) yang:
    - Melakukan **normalisasi** matriks keputusan
    - Menghitung **skor tertimbang** setiap kriteria
    - **Merangking** alternatif berdasarkan total skor
    
    **Kriteria Penilaian:**
    1. **IPK** (30%) - Benefit (semakin tinggi semakin baik)
    2. **Penghasilan Orang Tua** (25%) - Cost (semakin rendah semakin baik)
    3. **Jumlah Tanggungan** (15%) - Benefit (semakin tinggi semakin baik)
    4. **Prestasi** (15%) - Benefit (semakin tinggi semakin baik)
    5. **Keaktifan** (15%) - Benefit (semakin tinggi semakin baik)
    """)

# ============ PARAMETER SAW ============
st.subheader("⚙️ Parameter Perhitungan")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="parameter-box">
        <h4>📚 IPK</h4>
        <p><strong>Bobot:</strong> 30%</p>
        <p><strong>Tipe:</strong> Benefit</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="parameter-box">
        <h4>💰 Penghasilan Orang Tua</h4>
        <p><strong>Bobot:</strong> 25%</p>
        <p><strong>Tipe:</strong> Cost</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="parameter-box">
        <h4>👨‍👩‍👧 Tanggungan</h4>
        <p><strong>Bobot:</strong> 15%</p>
        <p><strong>Tipe:</strong> Benefit</p>
    </div>
    """, unsafe_allow_html=True)

col4, col5 = st.columns(2)

with col4:
    st.markdown("""
    <div class="parameter-box">
        <h4>🏆 Prestasi</h4>
        <p><strong>Bobot:</strong> 15%</p>
        <p><strong>Tipe:</strong> Benefit</p>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown("""
    <div class="parameter-box">
        <h4>⚡ Keaktifan</h4>
        <p><strong>Bobot:</strong> 15%</p>
        <p><strong>Tipe:</strong> Benefit</p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ============ BUTTON PERHITUNGAN ============
st.subheader("🚀 Jalankan Perhitungan")

col_info, col_button = st.columns([2, 1])

with col_info:
    st.markdown("""
    <div class="info-box">
        <strong>⚠️ Perhatian:</strong> Proses ini akan:
        <ul>
            <li>Menghapus data perhitungan sebelumnya</li>
            <li>Menormalisasi nilai kriteria dari semua mahasiswa</li>
            <li>Menghitung skor tertimbang berdasarkan bobot</li>
            <li>Menghasilkan ranking dan status penerimaan</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col_button:
    st.write("")
    st.write("")
    if st.button("▶️ Proses SAW", use_container_width=True, type="primary", key="btn_saw"):
        with st.spinner("⏳ Sedang memproses perhitungan SAW..."):
            try:
                # Jalankan perhitungan
                hitung_saw()
                time.sleep(1)  # Simulasi loading

                st.success("✅ Perhitungan SAW berhasil dijalankan!")
                
            except Exception as e:
                st.error(f"❌ Error saat perhitungan: {str(e)}")
                st.warning("Pastikan sudah ada data mahasiswa sebelum melakukan perhitungan SAW")

st.divider()

# ============ CATATAN PENTING ============
st.subheader("⚠️ Catatan Penting")

col_note1, col_note2 = st.columns(2)

with col_note1:
    st.info("""
    **📌 Sebelum Menjalankan:**
    - Pastikan sudah menambahkan data mahasiswa
    - Verifikasi kelengkapan data di halaman Data Mahasiswa
    - Setiap perhitungan akan menimpa hasil sebelumnya
    """)

with col_note2:
    st.info("""
    **📌 Status Penerimaan:**
    - Ranking 1-3: ✅ **Diterima**
    - Ranking > 3: ❌ **Tidak Diterima**
    
    Anda dapat mengubah ambang batas di pengaturan sistem
    """)