"""
models/evaluasi_onboarding.py - Kelas EvaluasiOnboarding untuk progres checklist karyawan baru.

Tujuan:
    Menghitung persentase penyelesaian tugas orientasi (onboarding). Pada tahap UTS kelas ini
    ikut ditunjukkan sebagai contoh polymorphism ketiga; alur onboarding lengkapnya (F15-F18)
    dikerjakan di tahap UAS.

Hubungan dengan file lain:
    - Mewarisi Evaluasi dari models/base.py dan meng-override hitung_skor() (polymorphism).
    - Belum dipakai oleh services/pipeline_manager.py maupun main.py; disiapkan untuk
      diintegrasikan pada fitur onboarding di tahap UAS.
"""

from models.base import Evaluasi

 
class EvaluasiOnboarding(Evaluasi): # Inheritance
    """
    Kelas konkret turunan dari Evaluasi.
    Bertanggung jawab mengevaluasi progres orientasi (onboarding) karyawan baru.
    Mendukung penuh kelancaran Fitur F15-F18 (Manajemen Checklist Onboarding).
    Kelas ini ikut ditunjukkan sebagai contoh polymorphism, sedangkan alur onboarding lengkapnya dikerjakan di tahap UAS
    """

    def __init__(self, id_evaluasi: str, tanggal: str, total_tugas: int, tugas_selesai: int = 0):
        super().__init__(id_evaluasi, tanggal)

        # Validasi keamanan: total tugas harus bilangan bulat positif
        if not self._bilangan_bulat(total_tugas) or total_tugas <= 0:
            raise ValueError("Total tugas onboarding harus berupa bilangan bulat lebih dari 0.")

        # Validasi logika: tugas selesai tidak boleh minus atau melebihi total tugas
        if not self._bilangan_bulat(tugas_selesai) or tugas_selesai < 0 or tugas_selesai > total_tugas:
            raise ValueError(f"Jumlah tugas selesai ({tugas_selesai}) tidak valid. Maksimal adalah {total_tugas}.")

        self._total_tugas = total_tugas
        self._tugas_selesai = tugas_selesai


    @staticmethod
    def _bilangan_bulat(nilai) -> bool:
        """True jika nilai adalah int murni (True/False tidak dihitung sebagai angka)."""
        return isinstance(nilai, int) and not isinstance(nilai, bool)


    @property
    def total_tugas(self) -> int:
        return self._total_tugas

    @property
    def tugas_selesai(self) -> int:
        return self._tugas_selesai

    @property
    def sisa_tugas(self) -> int:
        return self._total_tugas - self._tugas_selesai

    @property
    def selesai(self) -> bool:
        return self._tugas_selesai == self._total_tugas


    def tambah_tugas_selesai(self, jumlah: int = 1) -> None:
        """
        Menandai sejumlah tugas checklist sebagai selesai (Mendukung Fitur F16 & F17).
        """
        if not self._bilangan_bulat(jumlah) or jumlah < 0:
            raise ValueError("Jumlah penambahan tugas harus bilangan bulat tidak negatif.")

        if self._tugas_selesai + jumlah > self._total_tugas:
            raise ValueError(f"Penambahan ditolak! Tidak bisa melebihi batas {self._total_tugas} tugas.")

        self._tugas_selesai += jumlah

    def batalkan_tugas_selesai(self, jumlah: int = 1) -> None:
        """
        Mengembalikan sejumlah tugas ke status belum selesai (Mendukung Fitur F16).
        """
        if not self._bilangan_bulat(jumlah) or jumlah < 0:
            raise ValueError("Jumlah pembatalan tugas harus bilangan bulat tidak negatif.")

        if jumlah > self._tugas_selesai:
            raise ValueError(f"Pembatalan ditolak! Baru {self._tugas_selesai} tugas yang selesai.")

        self._tugas_selesai -= jumlah


    def hitung_skor(self) -> float:
        """
        Polymorphism: Menghitung persentase progress checklist tugas onboarding (Fitur F17).
        """
        progres = (self._tugas_selesai / self._total_tugas) * 100
        return round(progres, 2)

    def __str__(self) -> str:
        """
        Magic method untuk mencetak summary progress orientasi karyawan.
        """
        return (f"Evaluasi Onboarding [{self.id_evaluasi}] - Tanggal: {self.tanggal}\n"
                f"Progres: {self._tugas_selesai} / {self._total_tugas} Tugas Selesai\n"
                f"Skor Saat Ini: {self.hitung_skor()}%")