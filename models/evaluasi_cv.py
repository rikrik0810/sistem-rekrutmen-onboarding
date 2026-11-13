"""
models/evaluasi_cv.py - Kelas EvaluasiCV untuk menilai kecocokan CV dengan kualifikasi lowongan.

Tujuan:
    Menghitung skor screening CV (F3) berupa persentase keyword lowongan yang ditemukan
    di teks CV sebagai kata utuh, serta mencatat keyword yang cocok untuk transparansi HR.

Hubungan dengan file lain:
    - Mewarisi Evaluasi dari models/base.py dan meng-override hitung_skor() (polymorphism).
    - Dibuat dan dipakai oleh services/pipeline_manager.py pada screening_cv().
      Teks CV berasal dari models/kandidat.py, keyword berasal dari models/lowongan.py.
    - Tidak di-import langsung oleh main.py.
"""

from models.base import Evaluasi


class EvaluasiCV(Evaluasi): # Inheritance
    """
    Kelas konkret turunan dari Evaluasi.
    Bertanggung jawab untuk mengevaluasi kecocokan CV pelamar berdasarkan kata kunci.
    """

    # "C++" dan "C#" tidak berubah menjadi "c" saat dibersihkan.
    _KARAKTER_KHUSUS = "+#"

    def __init__(self, id_evaluasi: str, tanggal: str, cv_text: str, keyword_req: list):
        super().__init__(id_evaluasi, tanggal)

        # Validasi teks CV (Exception Handling)
        if not isinstance(cv_text, str) or not cv_text.strip():
            raise ValueError("Teks CV tidak boleh kosong untuk dievaluasi.")

        # Validasi daftar keyword (Exception Handling)
        if not isinstance(keyword_req, (list, tuple)):
            raise ValueError("Keyword harus berupa list atau tuple.")
        daftar = []
        sudah_ada = set()

        for kw in keyword_req:
            if not isinstance(kw, str) or not self._bersihkan_teks(kw):
                raise ValueError(f"Keyword '{kw}' tidak valid (kosong atau tanpa huruf/angka).")
            bentuk_bersih = self._bersihkan_teks(kw)
            if bentuk_bersih not in sudah_ada:  
                sudah_ada.add(bentuk_bersih)
                daftar.append(kw.strip())

        self._cv_text = cv_text.strip()
        self._keyword_req = daftar

        # Riwayat keyword yang berhasil Match (transparansi penilaian untuk HR)
        self._matched_keywords = []
        self._skor_terakhir = None  # None = hitung_skor() belum pernah dipanggil

    @property
    def cv_text(self) -> str:
        return self._cv_text

    @property
    def keyword_req(self) -> list:
        return list(self._keyword_req) 

    @property
    def matched_keywords(self) -> list:
        return list(self._matched_keywords)


    @staticmethod
    def _bersihkan_teks(teks: str) -> str:
        hasil = ""
        for huruf in teks.lower():
            if huruf.isalnum() or huruf in EvaluasiCV._KARAKTER_KHUSUS:
                hasil += huruf
            else:
                hasil += " "
        return " ".join(hasil.split())

    def hitung_skor(self) -> float: #Polymorphism
        """
        Menghitung persentase keyword yang ditemukan di CV.
        Pencocokan berupa kata utuh, sehingga "Java" tidak cocok dengan "JavaScript"
        dan "SQL" tidak cocok dengan "MySQL".
        """
        if not self._keyword_req:
            raise ValueError("Daftar kualifikasi/keyword dari lowongan belum ditentukan.")

        # Spasi di kedua ujung membuat keyword di awal/akhir teks tetap terdeteksi,
        # dan memastikan kecocokan hanya terjadi pada batas kata.
        cv_bersih = " " + self._bersihkan_teks(self._cv_text) + " " 

        self._matched_keywords.clear()

        for kw in self._keyword_req:
            if " " + self._bersihkan_teks(kw) + " " in cv_bersih: #" Aku Bisa Python "--> " Python " --> Cocok
                self._matched_keywords.append(kw)

        skor = (len(self._matched_keywords) / len(self._keyword_req)) * 100
        self._skor_terakhir = round(skor, 2)
        return self._skor_terakhir

    def __str__(self) -> str:
        """
        Ringkasan evaluasi. Tidak memanggil hitung_skor() sehingga aman dicetak
        kapan saja dan tidak mengubah isi matched_keywords.
        """
        skor = "belum dihitung" if self._skor_terakhir is None else f"{self._skor_terakhir}%"
        return (f"Evaluasi CV [{self.id_evaluasi}] - Tanggal: {self.tanggal}\nKeywords Dicari: {len(self._keyword_req)} | Cocok: {len(self._matched_keywords)}\nSkor Akhir: {skor}")