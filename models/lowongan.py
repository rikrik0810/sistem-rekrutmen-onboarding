"""
models/lowongan.py - Kelas entitas Lowongan (posisi pekerjaan yang dibuka).

Tujuan:
    Menyimpan detail lowongan: judul, divisi, batas lamar, daftar kualifikasi (keyword untuk screening),
    status publikasi (F1), dan threshold kelolosan (F4) beserta pengecekannya lewat cek_kelolosan().

Hubungan dengan file lain:
    - Tidak meng-import file proyek lain.
    - Dipakai services/pipeline_manager.py: kualifikasi menjadi keyword untuk EvaluasiCV,
      is_buka() memeriksa lamaran, dan cek_kelolosan() menentukan lolos/tidaknya kandidat.
    - Dipakai main.py untuk membuat, mempublikasikan, dan menampilkan lowongan.
"""

from datetime import datetime


class Lowongan:
    """
    Kelas entitas untuk merepresentasikan posisi pekerjaan yang dibuka.
    Menyimpan detail posisi, kualifikasi spesifik (untuk keyword matching),
    batas nilai threshold kelolosan, serta status publikasi (F1).
    """

    TANPA_BATAS = "Tidak ditentukan"
    FORMAT_TANGGAL = "%Y-%m-%d"

    def __init__(self, id_lowongan: str, judul_posisi: str, divisi: str,
                 skor_threshold: float, batas_lamaran: str = TANPA_BATAS):
        # Validasi data wajib
        if not id_lowongan or not id_lowongan.strip():
            raise ValueError("ID lowongan tidak boleh kosong.")
        if not judul_posisi or not judul_posisi.strip():
            raise ValueError("Judul posisi tidak boleh kosong.")
        if not divisi or not divisi.strip():
            raise ValueError("Divisi tidak boleh kosong.")

        # Validasi threshold: harus angka dan berada di rentang 0 - 100
        try:
            threshold = float(skor_threshold)
        except (TypeError, ValueError):
            raise ValueError("Skor threshold harus berupa angka.")
        if not (0.0 <= threshold <= 100.0):
            raise ValueError("Skor threshold harus berada di persentase 0.0 hingga 100.0")

        self._id_lowongan = id_lowongan.strip()
        self._judul_posisi = judul_posisi.strip()
        self._divisi = divisi.strip()
        self._skor_threshold = threshold
        self._batas_lamaran = self._normalisasi_batas(batas_lamaran)

        # Atribut untuk Fitur F1
        self._kualifikasi = []      # Daftar keyword keahlian (dipakai screening F3)
        self._dipublikasi = False   # Lowongan baru berstatus draft sampai dipublikasikan

    # -------------------------------------
    # PRIVATE HELPER
    # -------------------------------------
    @classmethod
    def _normalisasi_batas(cls, batas: str) -> str:
        """
        Memvalidasi tanggal batas lamar dan menyeragamkannya ke format YYYY-MM-DD,
        sehingga '2026-1-5' menjadi '2026-01-05'. Format salah ditolak dengan ValueError.
        """
        if batas is None or not batas.strip() or batas.strip() == cls.TANPA_BATAS:
            return cls.TANPA_BATAS
        try:
            tanggal = datetime.strptime(batas.strip(), cls.FORMAT_TANGGAL)
        except ValueError:
            raise ValueError(f"Batas lamaran '{batas}' tidak valid. Gunakan format YYYY-MM-DD, contoh 2026-12-31.")
        return tanggal.strftime(cls.FORMAT_TANGGAL)

    # -------------------------------------
    # GETTER PROPERTIES
    # -------------------------------------
    @property
    def id_lowongan(self) -> str:
        return self._id_lowongan

    @property
    def judul_posisi(self) -> str:
        return self._judul_posisi

    @property
    def divisi(self) -> str:
        return self._divisi

    @property
    def skor_threshold(self) -> float:
        return self._skor_threshold

    @property
    def batas_lamaran(self) -> str:
        return self._batas_lamaran

    @property
    def kualifikasi(self) -> list:
        # Mengembalikan salinan agar list asli tidak bisa diubah dari luar kelas
        return list(self._kualifikasi)

    @property
    def dipublikasi(self) -> bool:
        return self._dipublikasi

    # -------------------------------------
    # F1: KUALIFIKASI & PUBLIKASI
    # -------------------------------------
    def tambah_kualifikasi(self, kata_kunci: str) -> bool:
        """
        Menambahkan keyword kualifikasi yang dicari perusahaan (dipakai F3).
        Duplikat dicek tanpa membedakan huruf besar/kecil.
        Return True jika berhasil ditambahkan, False jika sudah ada.
        """
        if not kata_kunci or not kata_kunci.strip():
            raise ValueError("Kata kunci kualifikasi tidak boleh kosong.")
        kata = kata_kunci.strip()
        if kata.lower() in [k.lower() for k in self._kualifikasi]:
            return False
        self._kualifikasi.append(kata)
        return True

    def publikasikan(self) -> None:
        """
        Mempublikasikan lowongan agar bisa menerima lamaran (F1).
        Syarat: minimal satu kualifikasi, karena screening CV membutuhkan keyword.
        """
        if self._dipublikasi:
            raise ValueError(f"Lowongan [{self._id_lowongan}] sudah dipublikasikan.")
        if not self._kualifikasi:
            raise ValueError("Lowongan belum bisa dipublikasikan: tambahkan minimal 1 kualifikasi.")
        self._dipublikasi = True

    def tutup(self) -> None:
        """Menarik lowongan dari publikasi sehingga tidak menerima lamaran baru."""
        self._dipublikasi = False

    def is_buka(self) -> bool:
        """
        True jika lowongan sudah dipublikasikan DAN batas lamaran belum lewat.
        Pada hari terakhir batas lamaran, lowongan masih dianggap buka.
        """
        if not self._dipublikasi:
            return False
        if self._batas_lamaran == self.TANPA_BATAS:
            return True
        hari_ini = datetime.now().strftime(self.FORMAT_TANGGAL)
        return hari_ini <= self._batas_lamaran  # Format YYYY-MM-DD aman dibandingkan sebagai teks

    # ==========================================
    # F4: THRESHOLD
    # ==========================================
    def cek_kelolosan(self, skor: float) -> bool:
        """
        Memeriksa apakah skor evaluasi pelamar memenuhi atau melampaui threshold.
        """
        if not (0.0 <= skor <= 100.0):
            raise ValueError(f"Skor {skor} di luar rentang 0.0 - 100.0.")
        return skor >= self._skor_threshold

    def get_threshold(self) -> float:
        """
        Mengambil nilai batas minimum kelolosan lowongan (sesuai spesifikasi di UML Bab 3).
        """
        return self._skor_threshold

    def __str__(self) -> str:
        """
        Menampilkan informasi detail lowongan dengan rapi saat objek di-print().
        """
        kualifikasi_str = ", ".join(self._kualifikasi) if self._kualifikasi else "Belum ada kualifikasi spesifik"
        status = "Dipublikasikan" if self._dipublikasi else "Draft"
        return (f"[{self._id_lowongan}] {self._judul_posisi} - Divisi {self._divisi} ({status})\n"
                f"Batas Lamar: {self._batas_lamaran} | Minimal Skor (Threshold): {self._skor_threshold}\n"
                f"Kualifikasi (Keywords): {kualifikasi_str}")