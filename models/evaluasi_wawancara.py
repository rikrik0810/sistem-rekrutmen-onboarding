"""
models/evaluasi_wawancara.py - Kelas EvaluasiWawancara untuk jadwal dan penilaian wawancara.

Tujuan:
    Menyimpan jadwal wawancara (waktu, pewawancara, tipe HR/Teknis) untuk F7 dan nilai per aspek
    (teknis dan soft skill) untuk F8, lalu menghitung skor akhir berbobot 60% teknis + 40% soft skill.

Hubungan dengan file lain:
    - Mewarisi Evaluasi dari models/base.py dan meng-override hitung_skor() (polymorphism).
    - Dibuat dan dikelola oleh services/pipeline_manager.py pada jadwalkan_wawancara()
      dan nilai_wawancara(); skor akhirnya menjadi bahan komparasi kandidat (F9).
    - Tidak di-import langsung oleh main.py.
"""

from models.base import Evaluasi


class EvaluasiWawancara(Evaluasi): # Inheritance
    """
    Kelas konkret turunan dari Evaluasi.
    Bertanggung jawab untuk mengevaluasi hasil sesi wawancara pelamar,
    serta menyimpan data penjadwalan (Mendukung Fitur F7 dan F8).
    """

    BOBOT_TEKNIS = 0.6
    BOBOT_SOFTSKILL = 0.4
    TIPE_VALID = {"hr": "HR", "teknis": "Teknis"}
    BELUM_DITENTUKAN = "Belum ditentukan"

    def __init__(self, id_evaluasi: str, tanggal: str = "", skor_teknis: float = 0.0, skor_softskill: float = 0.0):
        super().__init__(id_evaluasi, tanggal)

        self._skor_teknis = self._validasi_skor(skor_teknis)
        self._skor_softskill = self._validasi_skor(skor_softskill)

        # Tanggal dianggap sudah dijadwalkan hanya jika diisi saat pembuatan atau lewat jadwalkan()
        self._sudah_dijadwalkan = isinstance(tanggal, str) and bool(tanggal.strip())
        self._interviewer = self.BELUM_DITENTUKAN
        self._tipe_interview = self.BELUM_DITENTUKAN


    @staticmethod
    def _validasi_skor(nilai) -> float:
        """Memastikan skor berupa angka dalam rentang 0.0 - 100.0, lalu mengembalikannya sebagai float."""
        try:
            skor = float(nilai)
        except (TypeError, ValueError):
            raise ValueError("Skor harus berupa angka.")
        if not (0.0 <= skor <= 100.0):
            raise ValueError("Skor harus berada di dalam rentang 0.0 sampai 100.0.")
        return skor


    @property
    def skor_teknis(self) -> float:
        return self._skor_teknis

    @property
    def skor_softskill(self) -> float:
        return self._skor_softskill

    @property
    def interviewer(self) -> str:
        return self._interviewer

    @property
    def tipe_interview(self) -> str:
        return self._tipe_interview

    @property
    def sudah_dijadwalkan(self) -> bool:
        return self._sudah_dijadwalkan


    def jadwalkan(self, nama_interviewer: str, tipe: str, waktu_baru: str) -> None:
        """
        Metode untuk menyetel detail jadwal wawancara (Memenuhi Fitur F7).
        Tipe wawancara yang diterima: HR atau Teknis.
        """
        if not isinstance(nama_interviewer, str) or not nama_interviewer.strip():
            raise ValueError("Nama interviewer tidak boleh kosong.")
        if not isinstance(waktu_baru, str) or not waktu_baru.strip():
            raise ValueError("Waktu wawancara tidak boleh kosong.")
        tipe_bersih = tipe.strip().lower() if isinstance(tipe, str) else ""
        if tipe_bersih not in self.TIPE_VALID:
            raise ValueError(f"Tipe interview '{tipe}' tidak valid. Pilih: {list(self.TIPE_VALID.values())}")

        self._interviewer = nama_interviewer.strip()
        self._tipe_interview = self.TIPE_VALID[tipe_bersih]
        self._set_tanggal(waktu_baru)  
        self._sudah_dijadwalkan = True

    def input_nilai(self, skor_teknis: float, skor_softskill: float) -> None:
        """
        Metode untuk menginput atau mengubah nilai setelah wawancara selesai (Memenuhi Fitur F8).
        Kedua nilai divalidasi dulu sebelum disimpan, sehingga tidak ada yang tersimpan separuh.
        """
        teknis = self._validasi_skor(skor_teknis)
        softskill = self._validasi_skor(skor_softskill)
        self._skor_teknis = teknis
        self._skor_softskill = softskill

    def hitung_skor(self) -> float:
        """
        Polymorphism: Menghitung nilai rata-rata tertimbang (Fitur F8).
        60% Teknis, 40% Soft Skill.
        """
        skor_akhir = (self._skor_teknis * self.BOBOT_TEKNIS) + (self._skor_softskill * self.BOBOT_SOFTSKILL)
        return round(skor_akhir, 2)

    def __str__(self) -> str:
        waktu = self.tanggal if self._sudah_dijadwalkan else "Belum dijadwalkan"
        return (f"Evaluasi Wawancara [{self.id_evaluasi}] - Jadwal: {waktu}\nPewawancara: {self._interviewer} ({self._tipe_interview})\nNilai Teknis: {self._skor_teknis} | Soft Skill: {self._skor_softskill}\nSkor Akhir: {self.hitung_skor()}")