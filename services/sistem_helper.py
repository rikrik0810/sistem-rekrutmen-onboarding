"""
services/sistem_helper.py - Kelas utilitas SistemHelper (fungsi bantu umum).

Tujuan:
    Menyediakan static method yang bisa dipanggil tanpa membuat objek:
    generasi_id() untuk ID unik acak (contoh K-A9X2) yang tidak bentrok dengan ID lama,
    dan bersihkan_teks() untuk merapikan spasi pada input pengguna.

Hubungan dengan file lain:
    - Tidak meng-import file proyek lain.
    - Dipakai main.py (id_baru() dan input_teks()). Tidak dipakai oleh models/ maupun
      services/pipeline_manager.py, agar lapisan models tetap mandiri.
"""

import random

# Konstanta global untuk kumpulan karakter pembentuk ID acak
CHAR_POOL = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
PANJANG_KODE = 4
BATAS_PERCOBAAN = 1000


class SistemHelper:
    """
    Kelas utilitas pendukung (Helper Class) yang berisi kumpulan fungsi bantu
    menggunakan @staticmethod agar dapat dipanggil langsung tanpa instansiasi objek.
    """

    @staticmethod
    def generasi_id(prefix: str, terpakai=None) -> str:
        """
        Menggenerasi ID unik secara otomatis berdasarkan prefix yang diberikan
        (Contoh: K-A9X2, L-8B1Y).

        Jika `terpakai` diberikan (list/set berisi ID yang sudah ada), ID yang dihasilkan
        dijamin tidak bentrok dengan isinya.
        """
        if not isinstance(prefix, str) or not prefix.strip():
            prefix = "SYS"
        prefix = prefix.strip().upper()

        for _ in range(BATAS_PERCOBAAN):
            random_code = "".join(random.choices(CHAR_POOL, k=PANJANG_KODE))
            id_baru = f"{prefix}-{random_code}"
            if terpakai is None or id_baru not in terpakai:
                return id_baru

        raise RuntimeError(f"Gagal membuat ID unik untuk prefix '{prefix}'.")

    @staticmethod
    def bersihkan_teks(teks: str) -> str:
        """
        Membersihkan teks dari kelebihan spasi di awal, akhir,
        maupun spasi ganda di tengah teks (standarisasi input pengguna).
        """
        if not isinstance(teks, str):
            return ""

        # strip() membuang spasi pinggir, split() memecah spasi berlebih, join() merangkai kembali
        return " ".join(teks.strip().split())