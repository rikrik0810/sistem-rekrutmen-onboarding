"""
models/base.py - Abstract Base Class Evaluasi, fondasi inheritance dan polymorphism.

Tujuan:
    Mendefinisikan atribut dasar semua jenis penilaian (id_evaluasi, tanggal) dan kontrak
    abstract method hitung_skor() yang wajib di-override oleh kelas turunan.
    Evaluasi juga bisa dibandingkan (<, >, <=, >=) dengan evaluasi sejenis.

Hubungan dengan file lain:
    - Tidak meng-import file proyek lain (hanya abc dan datetime dari Python).
    - Diwarisi oleh models/evaluasi_cv.py, models/evaluasi_wawancara.py,
      dan models/evaluasi_onboarding.py.
    - Dipakai services/pipeline_manager.py untuk memeriksa tipe objek (isinstance)
      pada proses_evaluasi() sebelum memanggil hitung_skor().
"""

from abc import ABC, abstractmethod
from datetime import datetime


class Evaluasi(ABC):
    """
    Abstract Base Class sebagai fondasi utama untuk semua jenis penilaian/evaluasi.
    Menerapkan konsep Abstraksi dan memaksa aturan atau kontrak ke kelas turunannya.
    """

    def __init__(self, id_evaluasi: str, tanggal: str = ""):
        if not isinstance(id_evaluasi, str) or not id_evaluasi.strip(): 
            raise ValueError("ID Evaluasi tidak boleh kosong.")
        
        self._id_evaluasi = id_evaluasi.strip()
        self._tanggal = self._tanggal_atau_sekarang(tanggal)
        

    @staticmethod
    def _tanggal_atau_sekarang(tanggal) -> str:
        """Jika tanggal kosong, pakai pakai waktu saat ini."""
        if not isinstance(tanggal, str) or not tanggal.strip():
            return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return tanggal.strip()

    def _set_tanggal(self, tanggal: str) -> None:
        """Setter untuk memperbarui tanggal."""
        if not isinstance(tanggal, str) or not tanggal.strip():
            raise ValueError("Tanggal tidak boleh kosong.")
        self._tanggal = tanggal.strip()


    # Getter untuk return nilai
    @property
    def id_evaluasi(self) -> str:
        return self._id_evaluasi

    @property
    def tanggal(self) -> str:
        return self._tanggal

    # Polymorphism
    @abstractmethod
    def hitung_skor(self) -> float:
        """
        Abstract method yang WAJIB di-override oleh setiap kelas turunan
        (seperti EvaluasiCV atau EvaluasiWawancara).
        Ini adalah pusat dari penerapan Polymorphism di sistem.

        Return:
            float: Hasil perhitungan skor akhir.
        """

    # Evaluasi hanya bisa dibandingkan dengan evaluasi sejenis (CV dengan CV, wawancara dengan wawancara). Dengan begitu sorted() dan max() langsung bisa dipakai pada daftar evaluasi tanpa kode pembanding tambahan.
    def __lt__(self, other):
        if type(other) is not type(self):
            return NotImplemented
        return self.hitung_skor() < other.hitung_skor()

    def __gt__(self, other):
        if type(other) is not type(self):
            return NotImplemented
        return self.hitung_skor() > other.hitung_skor()

    def __le__(self, other):
        if type(other) is not type(self):
            return NotImplemented
        return self.hitung_skor() <= other.hitung_skor()

    def __ge__(self, other):
        if type(other) is not type(self):
            return NotImplemented
        return self.hitung_skor() >= other.hitung_skor()

    def __str__(self) -> str:
        return f"Evaluasi [{self._id_evaluasi}] - Tanggal: {self._tanggal}"