import mysql.connector

# ==========================
# KONFIGURASI DATABASE
# ==========================

HOST = "localhost"
USER = "root"
PASSWORD = ""
DATABASE = "db_beasiswa"


# ==========================
# KONEKSI DATABASE
# ==========================

def get_connection():
    return mysql.connector.connect(
        host=HOST,
        user=USER,
        password=PASSWORD,
        database=DATABASE
    )


# ==========================
# INISIALISASI DATABASE
# ==========================

def initialize_database():

    try:

        # Buat database jika belum ada
        conn = mysql.connector.connect(
            host=HOST,
            user=USER,
            password=PASSWORD
        )

        cursor = conn.cursor()

        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS {DATABASE}"
        )

        cursor.close()
        conn.close()

        # Koneksi ke database
        conn = get_connection()

        cursor = conn.cursor()

        # ==========================
        # TABEL MAHASISWA
        # ==========================

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS mahasiswa (
            nim VARCHAR(20) PRIMARY KEY,
            nama VARCHAR(100) NOT NULL,
            prodi VARCHAR(100) NOT NULL,
            ipk DECIMAL(3,2) NOT NULL,
            penghasilan_ortu DECIMAL(12,2) NOT NULL,
            tanggungan INT NOT NULL,
            prestasi VARCHAR(50) NOT NULL,
            keaktifan VARCHAR(50) NOT NULL
        )
        """)

        # ==========================
        # TABEL NILAI KRITERIA
        # ==========================

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS nilai_kriteria (
            id_nilai INT AUTO_INCREMENT PRIMARY KEY,

            nim VARCHAR(20) NOT NULL,

            nilai_ipk INT NOT NULL,
            nilai_penghasilan INT NOT NULL,
            nilai_tanggungan INT NOT NULL,
            nilai_prestasi INT NOT NULL,
            nilai_keaktifan INT NOT NULL,

            CONSTRAINT fk_nilai_mahasiswa
            FOREIGN KEY (nim)
            REFERENCES mahasiswa(nim)
            ON DELETE CASCADE
            ON UPDATE CASCADE
        )
        """)

        # ==========================
        # TABEL HASIL SAW
        # ==========================

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS hasil_saw (
            id_hasil INT AUTO_INCREMENT PRIMARY KEY,

            nim VARCHAR(20) NOT NULL,

            total_skor DECIMAL(10,4) NOT NULL,
            ranking_ke INT NOT NULL,
            status_acc VARCHAR(20) NOT NULL,

            CONSTRAINT fk_hasil_mahasiswa
            FOREIGN KEY (nim)
            REFERENCES mahasiswa(nim)
            ON DELETE CASCADE
            ON UPDATE CASCADE
        )
        """)

        conn.commit()

        cursor.close()
        conn.close()

        print("Database berhasil diinisialisasi.")

    except Exception as e:
        print(f"Error database: {e}")