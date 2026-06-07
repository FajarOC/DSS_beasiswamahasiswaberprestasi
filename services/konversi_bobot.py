def bobot_ipk(ipk):

    if ipk >= 3.75:
        return 5
    elif ipk >= 3.50:
        return 4
    elif ipk >= 3.00:
        return 3
    elif ipk >= 2.75:
        return 2
    else:
        return 1


def bobot_penghasilan(p):

    if p < 1500000:
        return 5
    elif p <= 3000000:
        return 4
    elif p <= 5000000:
        return 3
    elif p <=7500000:
        return 2
    else:
        return 1


def bobot_tanggungan(t):

    if t >= 5:
        return 5
    elif t == 4:
        return 4
    elif t == 3:
        return 3
    elif t == 2:
        return 2
    else:
        return 1


def bobot_prestasi(prestasi):

    mapping = {
        "Tidak Ada": 1,
        "Jurusan": 2,
        "Fakultas": 3,
        "Provinsi": 4,
        "Nasional": 5
    }

    return mapping.get(prestasi, 1)


def bobot_keaktifan(keaktifan):

    mapping = {
        "Tidak Aktif": 1,
        "Kurang Aktif": 2,
        "Cukup Aktif": 3,
        "Aktif": 4,
        "Sangat Aktif": 5
    }

    return mapping.get(keaktifan, 1)