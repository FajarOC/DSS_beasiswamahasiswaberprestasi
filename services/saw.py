import pandas as pd
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.config import get_connection

from services.konversi_bobot import (
    bobot_ipk,
    bobot_penghasilan,
    bobot_tanggungan,
    bobot_prestasi,
    bobot_keaktifan
)


def hitung_saw():

    conn = get_connection()
    cur = conn.cursor()

    # Hapus data lama
    cur.execute("DELETE FROM nilai_kriteria")
    cur.execute("DELETE FROM hasil_saw")
    conn.commit()

    # Ambil data mahasiswa
    query = """
    SELECT
        nim,
        ipk,
        penghasilan_ortu,
        tanggungan,
        prestasi,
        keaktifan
    FROM mahasiswa
    """

    df = pd.read_sql(query, conn)

    if df.empty:
        return

    # ==========================
    # KONVERSI BOBOT
    # ==========================

    df["nilai_ipk"] = df["ipk"].apply(bobot_ipk)

    df["nilai_penghasilan"] = df["penghasilan_ortu"].apply(
        bobot_penghasilan
    )

    df["nilai_tanggungan"] = df["tanggungan"].apply(
        bobot_tanggungan
    )

    df["nilai_prestasi"] = df["prestasi"].apply(
        bobot_prestasi
    )

    df["nilai_keaktifan"] = df["keaktifan"].apply(
        bobot_keaktifan
    )

    # Simpan ke tabel nilai_kriteria

    for _, row in df.iterrows():

        sql = """
        INSERT INTO nilai_kriteria
        (
            nim,
            nilai_ipk,
            nilai_penghasilan,
            nilai_tanggungan,
            nilai_prestasi,
            nilai_keaktifan
        )
        VALUES (%s,%s,%s,%s,%s,%s)
        """

        data = (
            row["nim"],
            int(row["nilai_ipk"]),
            int(row["nilai_penghasilan"]),
            int(row["nilai_tanggungan"]),
            int(row["nilai_prestasi"]),
            int(row["nilai_keaktifan"])
        )

        cur.execute(sql, data)

    conn.commit()

    # ==========================
    # NORMALISASI SAW
    # ==========================

    kriteria = [
        "nilai_ipk",
        "nilai_penghasilan",
        "nilai_tanggungan",
        "nilai_prestasi",
        "nilai_keaktifan"
    ]

    matriks = df[kriteria].copy()

    normalisasi = pd.DataFrame()

    # IPK = Benefit
    normalisasi["ipk"] = (
        matriks["nilai_ipk"]
        / matriks["nilai_ipk"].max()
    )

    # Penghasilan = Cost
    normalisasi["penghasilan"] = (
        matriks["nilai_penghasilan"].min()
        / matriks["nilai_penghasilan"]
    )

    # Tanggungan = Benefit
    normalisasi["tanggungan"] = (
        matriks["nilai_tanggungan"]
        / matriks["nilai_tanggungan"].max()
    )

    # Prestasi = Benefit
    normalisasi["prestasi"] = (
        matriks["nilai_prestasi"]
        / matriks["nilai_prestasi"].max()
    )

    # Keaktifan = Benefit
    normalisasi["keaktifan"] = (
        matriks["nilai_keaktifan"]
        / matriks["nilai_keaktifan"].max()
    )

    # ==========================
    # BOBOT KRITERIA
    # ==========================

    bobot = {
        "ipk": 0.30,
        "penghasilan": 0.25,
        "tanggungan": 0.15,
        "prestasi": 0.15,
        "keaktifan": 0.15
    }

    # ==========================
    # HITUNG TOTAL SKOR
    # ==========================

    df["total_skor"] = (

        normalisasi["ipk"] * bobot["ipk"]

        + normalisasi["penghasilan"]
        * bobot["penghasilan"]

        + normalisasi["tanggungan"]
        * bobot["tanggungan"]

        + normalisasi["prestasi"]
        * bobot["prestasi"]

        + normalisasi["keaktifan"]
        * bobot["keaktifan"]

    )

    # Ranking

    df = df.sort_values(
        by="total_skor",
        ascending=False
    )

    df["ranking_ke"] = range(
        1,
        len(df) + 1
    )

    # Status (1 = Diterima, 0 = Tidak Diterima)

    def status(rank):

        if rank <= 3:
            return 1  # Diterima

        return 0  # Tidak Diterima

    df["status_acc"] = df["ranking_ke"].apply(
        status
    )

    # ==========================
    # SIMPAN HASIL SAW
    # ==========================

    for _, row in df.iterrows():

        sql = """
        INSERT INTO hasil_saw
        (
            nim,
            total_skor,
            ranking_ke,
            status_acc
        )
        VALUES (%s,%s,%s,%s)
        """

        data = (
            row["nim"],
            float(row["total_skor"]),
            int(row["ranking_ke"]),
            int(row["status_acc"])
        )

        cur.execute(sql, data)

    conn.commit()

    cur.close()
    conn.close()