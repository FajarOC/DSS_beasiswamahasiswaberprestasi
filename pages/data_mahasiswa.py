import streamlit as st
import pandas as pd
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.config import get_connection

st.set_page_config(page_title="Data Mahasiswa", layout="wide")

# Custom styling
st.markdown("""
<style>
    .header-title {
        text-align: center;
        padding: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        color: white;
        margin-bottom: 30px;
    }
    .metric-card {
        background: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #667eea;
    }
    .success-box {
        background: #d4edda;
        padding: 12px;
        border-radius: 8px;
        border-left: 4px solid #28a745;
    }
    .form-section {
        background: #f9f9f9;
        padding: 25px;
        border-radius: 12px;
        border: 1px solid #e0e0e0;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="header-title"><h1>📊 Data Mahasiswa</h1><p>Kelola data calon penerima beasiswa</p></div>', unsafe_allow_html=True)

conn = get_connection()

# Initialize session state
if "show_edit_form" not in st.session_state:
    st.session_state.show_edit_form = False
if "selected_mahasiswa_nim" not in st.session_state:
    st.session_state.selected_mahasiswa_nim = None

income_ranges = [
    ("< 1.000.000", 0),
    ("1.000.000 - 1.999.999", 1000000),
    ("2.000.000 - 2.999.999", 2000000),
    ("3.000.000 - 3.999.999", 3000000),
    (">= 4.000.000", 4000000),
]

income_labels = [label for label, _ in income_ranges]

def get_income_label(value):
    if value < 1500000:
        return income_labels[0]
    elif value <= 3000000:
        return income_labels[1]
    elif value <= 5000000:
        return income_labels[2]
    elif value <= 7500000:
        return income_labels[3]
    return income_labels[4]

# ============ SECTION 1: TAMBAH DATA MAHASISWA ============
with st.expander("➕ Tambah Data Mahasiswa Baru", expanded=True):
    st.markdown('<div class="form-section">', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        nim = st.text_input("🆔 NIM", key="add_nim", placeholder="Contoh: 23801092")
        nama = st.text_input("👤 Nama Mahasiswa", key="add_nama", placeholder="Contoh: Graham")
        
        ipk = st.number_input(
            "📚 IPK",
            min_value=0.0,
            max_value=4.0,
            step=0.01,
            key="add_ipk",
            help="Nilai IPK dari 0.00 hingga 4.00"
        )
        
        prestasi = st.selectbox(
            "🏆 Prestasi",
            [
                "Tidak Ada",
                "Jurusan",
                "Fakultas",
                "Provinsi",
                "Nasional"
            ],
            key="add_prestasi"
        )
    
    with col2:
        prodi = st.text_input("🎓 Program Studi", key="add_prodi", placeholder="Contoh: Teknik Elektro")
        
        tanggungan = st.number_input(
            "👨‍👩‍👧 Jumlah Tanggungan",
            min_value=1,
            key="add_tanggungan",
            help="Jumlah keluarga yang menjadi tanggungan"
        )
        
        keaktifan = st.selectbox(
            "⚡ Keaktifan",
            [
                "Tidak Aktif",
                "Kurang Aktif",
                "Cukup Aktif",
                "Aktif",
                "Sangat Aktif"
            ],
            key="add_keaktifan"
        )
    
    st.markdown("---")
    st.subheader("💰 Penghasilan Orang Tua")
    
    penghasilan_option = st.radio(
        "Pilih cara input penghasilan:",
        ["Manual (Nominal)", "Range Kategori"],
        horizontal=True,
        key="add_income_method"
    )
    
    if penghasilan_option == "Manual (Nominal)":
        penghasilan = st.number_input(
            "Masukkan penghasilan orang tua (Rp)",
            min_value=0,
            step=100000,
            key="add_penghasilan_manual",
            format="%d",
            help="Masukkan nominal penghasilan dalam Rupiah"
        )
        penghasilan_label = get_income_label(penghasilan)
        st.info(f"📊 Kategori: {penghasilan_label}")
    else:
        penghasilan_label = st.selectbox(
            "Pilih range penghasilan:",
            income_labels,
            key="add_penghasilan_range"
        )
        penghasilan = dict(income_ranges)[penghasilan_label]
        st.info(f"💵 Nominal awal: Rp{penghasilan:,}")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    col_button1, col_button2, col_button3 = st.columns([2, 1, 1])
    
    with col_button1:
        if st.button("✅ Simpan Data", use_container_width=True, type="primary", key="add_simpan"):
            if not nim or not nama or not prodi:
                st.error("❌ NIM, Nama, dan Program Studi wajib diisi.")
            else:
                cur = conn.cursor()
                sql = """
                INSERT INTO mahasiswa
                (
                    nim,
                    nama,
                    prodi,
                    ipk,
                    penghasilan_ortu,
                    tanggungan,
                    prestasi,
                    keaktifan
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                """

                data = (
                    nim,
                    nama,
                    prodi,
                    ipk,
                    penghasilan,
                    tanggungan,
                    prestasi,
                    keaktifan
                )

                try:
                    cur.execute(sql, data)
                    conn.commit()
                    st.success(f"✅ Data mahasiswa {nama} berhasil disimpan!")
                except Exception as e:
                    st.error(f"❌ Gagal menyimpan data: {e}")

st.divider()

# ============ SECTION 2: DAFTAR MAHASISWA ============
st.subheader("📋 Daftar Mahasiswa")

# Load data mahasiswa
query = "SELECT * FROM mahasiswa ORDER BY nama"
df = pd.read_sql(query, conn)

# Statistik Ringkas
if not df.empty:
    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
    with col_stat1:
        st.metric("👥 Total Mahasiswa", len(df))
    with col_stat2:
        avg_ipk = df['ipk'].mean()
        st.metric("📚 Rata-rata IPK", f"{avg_ipk:.2f}")
    with col_stat3:
        avg_tanggungan = df['tanggungan'].mean()
        st.metric("👨‍👩‍👧 Rata-rata Tanggungan", f"{avg_tanggungan:.1f}")
    with col_stat4:
        avg_penghasilan = df['penghasilan_ortu'].mean()
        st.metric("💰 Rata-rata Penghasilan", f"Rp{int(avg_penghasilan):,}")
    
    st.divider()

if df.empty:
    st.warning("⚠️ Belum ada data mahasiswa. Silakan tambahkan data terlebih dahulu.")
else:
    # Display tabel dengan styling
    df_display = df.copy()
    df_display['penghasilan_ortu'] = df_display['penghasilan_ortu'].apply(lambda x: f"Rp{x:,}")
    df_display['ipk'] = df_display['ipk'].apply(lambda x: f"{x:.2f}")
    
    st.dataframe(
        df_display,
        use_container_width=True,
        hide_index=True,
        column_config={
            "nim": st.column_config.TextColumn("🆔 NIM", width="small"),
            "nama": st.column_config.TextColumn("👤 Nama"),
            "prodi": st.column_config.TextColumn("🎓 Program Studi"),
            "ipk": st.column_config.TextColumn("📚 IPK", width="small"),
            "penghasilan_ortu": st.column_config.TextColumn("💰 Penghasilan", width="medium"),
            "tanggungan": st.column_config.NumberColumn("👨‍👩‍👧 Tanggungan", width="small"),
            "prestasi": st.column_config.TextColumn("🏆 Prestasi"),
            "keaktifan": st.column_config.TextColumn("⚡ Keaktifan"),
        }
    )
    
    st.divider()
    
    # ============ SECTION 3: EDIT / HAPUS DATA ============
    st.subheader("✏️ Edit atau Hapus Data")

    df = df.set_index("nim", drop=False)
    mahasiswa_options = [""] + df.index.tolist()
    
    def on_mahasiswa_selected():
        selected = st.session_state.select_mahasiswa
        if selected:
            st.session_state.selected_mahasiswa_nim = selected
            st.session_state.show_edit_form = True
        else:
            st.session_state.show_edit_form = False
    
    st.selectbox(
        "🔍 Pilih Mahasiswa untuk Edit/Hapus",
        options=mahasiswa_options,
        format_func=lambda x: f"{x} - {df.at[x, 'nama']}" if x else "-- Pilih mahasiswa --",
        key="select_mahasiswa",
        on_change=on_mahasiswa_selected
    )

    if st.session_state.show_edit_form and st.session_state.selected_mahasiswa_nim:
        selected_nim = st.session_state.selected_mahasiswa_nim
        selected_record = df.loc[selected_nim]

        st.markdown(f'<div class="form-section">', unsafe_allow_html=True)
        st.subheader(f"✏️ Edit Data: {selected_record['nama']}")
        
        with st.form("edit_mahasiswa_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                edit_nim = st.text_input("🆔 NIM", value=selected_record["nim"], key="edit_nim")
                edit_nama = st.text_input("👤 Nama Mahasiswa", value=selected_record["nama"], key="edit_nama")
                
                edit_ipk = st.number_input(
                    "📚 IPK",
                    min_value=0.0,
                    max_value=4.0,
                    step=0.01,
                    value=float(selected_record["ipk"]),
                    key="edit_ipk"
                )
                
                edit_prestasi = st.selectbox(
                    "🏆 Prestasi",
                    [
                        "Tidak Ada",
                        "Kampus",
                        "Kabupaten",
                        "Provinsi",
                        "Nasional"
                    ],
                    index=[
                        "Tidak Ada",
                        "Kampus",
                        "Kabupaten",
                        "Provinsi",
                        "Nasional"
                    ].index(selected_record["prestasi"]),
                    key="edit_prestasi"
                )
            
            with col2:
                edit_prodi = st.text_input("🎓 Program Studi", value=selected_record["prodi"], key="edit_prodi")
                
                edit_tanggungan = st.number_input(
                    "👨‍👩‍👧 Jumlah Tanggungan",
                    min_value=1,
                    value=int(selected_record["tanggungan"]),
                    key="edit_tanggungan"
                )
                
                edit_keaktifan = st.selectbox(
                    "⚡ Keaktifan",
                    [
                        "Tidak Aktif",
                        "Kurang Aktif",
                        "Cukup Aktif",
                        "Aktif",
                        "Sangat Aktif"
                    ],
                    index=[
                        "Tidak Aktif",
                        "Kurang Aktif",
                        "Cukup Aktif",
                        "Aktif",
                        "Sangat Aktif"
                    ].index(selected_record["keaktifan"]),
                    key="edit_keaktifan"
                )
            
            st.markdown("---")
            st.subheader("💰 Penghasilan Orang Tua")
            
            edit_penghasilan_option = st.radio(
                "Pilih cara input penghasilan:",
                ["Manual (Nominal)", "Range Kategori"],
                horizontal=True,
                key="edit_income_method"
            )
            
            if edit_penghasilan_option == "Manual (Nominal)":
                edit_penghasilan = st.number_input(
                    "Masukkan penghasilan orang tua (Rp)",
                    min_value=0,
                    value=int(selected_record["penghasilan_ortu"]),
                    step=100000,
                    key="edit_penghasilan_manual",
                    format="%d"
                )
                edit_penghasilan_label = get_income_label(edit_penghasilan)
                st.info(f"📊 Kategori: {edit_penghasilan_label}")
            else:
                edit_penghasilan_label = st.selectbox(
                    "Pilih range penghasilan:",
                    income_labels,
                    index=income_labels.index(get_income_label(int(selected_record["penghasilan_ortu"]))),
                    key="edit_penghasilan_range"
                )
                edit_penghasilan = dict(income_ranges)[edit_penghasilan_label]
                st.info(f"💵 Nominal awal: Rp{edit_penghasilan:,}")

            col_btn1, col_btn2, col_btn3 = st.columns(3)
            with col_btn1:
                update_button = st.form_submit_button("✏️ Perbarui", use_container_width=True, type="primary")
            with col_btn2:
                delete_button = st.form_submit_button("🗑️ Hapus", use_container_width=True, type="secondary")
            with col_btn3:
                cancel_button = st.form_submit_button("❌ Batal", use_container_width=True, type="secondary")

        st.markdown('</div>', unsafe_allow_html=True)

        if update_button:
            if not edit_nim or not edit_nama or not edit_prodi:
                st.error("❌ NIM, Nama, dan Program Studi wajib diisi.")
            else:
                cur = conn.cursor()
                try:
                    if edit_nim != selected_nim:
                        cur.execute(
                            "UPDATE hasil_saw SET nim=%s WHERE nim=%s",
                            (edit_nim, selected_nim)
                        )

                    sql = """
                    UPDATE mahasiswa
                    SET nim=%s,
                        nama=%s,
                        prodi=%s,
                        ipk=%s,
                        penghasilan_ortu=%s,
                        tanggungan=%s,
                        prestasi=%s,
                        keaktifan=%s
                    WHERE nim=%s
                    """
                    data = (
                        edit_nim,
                        edit_nama,
                        edit_prodi,
                        edit_ipk,
                        edit_penghasilan,
                        edit_tanggungan,
                        edit_prestasi,
                        edit_keaktifan,
                        selected_nim
                    )
                    cur.execute(sql, data)
                    conn.commit()
                    st.success(f"✅ Data {edit_nama} berhasil diperbarui!")
                    st.session_state.show_edit_form = False
                    st.session_state.selected_mahasiswa_nim = None
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Gagal memperbarui data: {e}")

        if delete_button:
            cur = conn.cursor()
            try:
                cur.execute("DELETE FROM hasil_saw WHERE nim=%s", (selected_nim,))
                cur.execute("DELETE FROM mahasiswa WHERE nim=%s", (selected_nim,))
                conn.commit()
                st.success(f"✅ Data {selected_record['nama']} berhasil dihapus!")
                st.session_state.show_edit_form = False
                st.session_state.selected_mahasiswa_nim = None
                st.rerun()
            except Exception as e:
                st.error(f"❌ Gagal menghapus data: {e}")

        if cancel_button:
            st.session_state.show_edit_form = False
            st.session_state.selected_mahasiswa_nim = None
            st.rerun()