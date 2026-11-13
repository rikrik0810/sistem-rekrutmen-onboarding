"""
services/pipeline_manager.py - PipelineManager dan custom exception sistem rekrutmen.

Tujuan:
    Pusat logika bisnis: menyimpan kumpulan Kandidat dan Lowongan, mencatat lamaran (F2),
    menjalankan screening CV (F3-F5), menjadwalkan dan menilai wawancara (F7-F8),
    mengomparasi skor kandidat (F9), dan menampilkan pipeline (F10).
    File ini juga mendefinisikan RekrutmenException, ApplicationNotFoundException (F6),
    dan LowonganNotFoundException.

Hubungan dengan file lain:
    - Meng-import models/kandidat.py, models/lowongan.py, models/base.py (Evaluasi),
      models/evaluasi_cv.py, dan models/evaluasi_wawancara.py.
    - Dipakai main.py: semua menu memanggil PipelineManager, dan RekrutmenException
      ditangkap di main().
    - Tidak meng-import services/sistem_helper.py; pembuatan ID dilakukan oleh main.py.
"""

from models.kandidat import Kandidat
from models.lowongan import Lowongan
from models.base import Evaluasi
from models.evaluasi_cv import EvaluasiCV
from models.evaluasi_wawancara import EvaluasiWawancara


# -------------------------------------
# CUSTOM EXCEPTION (Memenuhi Fitur F6)
# -------------------------------------
class RekrutmenException(Exception):
    """Kelas dasar untuk semua exception khusus pada sistem rekrutmen."""
    pass


class ApplicationNotFoundException(RekrutmenException):
    """Exception khusus yang dinaikkan ketika ID Kandidat tidak ditemukan dalam sistem."""
    pass


class LowonganNotFoundException(RekrutmenException):
    """Exception khusus yang dinaikkan ketika ID Lowongan tidak ditemukan dalam sistem."""
    pass


class PipelineManager:
    """
    Kelas manager untuk mengelola kumpulan objek Kandidat dan Lowongan,
    serta mengeksekusi proses evaluasi secara terpusat.
    """

    def __init__(self):
        self._daftar_kandidat = []
        self._daftar_lowongan = []
        self._lamaran = {}          # {id_kandidat: id_lowongan} -> kandidat melamar ke lowongan mana
        self._wawancara = {}        # {id_kandidat: EvaluasiWawancara} -> jadwal & nilai wawancara
        self._skor_cv = {}          # {id_kandidat: skor screening CV}
        self._skor_wawancara = {}   # {id_kandidat: skor akhir wawancara} -> bahan komparasi F9

    # -------------------------------------
    # GETTER PROPERTIES
    # -------------------------------------
    @property
    def daftar_kandidat(self) -> list:
        return list(self._daftar_kandidat)  # Salinan, agar list asli tidak diubah dari luar

    @property
    def daftar_lowongan(self) -> list:
        return list(self._daftar_lowongan)

    # -------------------------------------
    # METHODS TAMBAH & CARI DATA
    # -------------------------------------
    def tambah_kandidat(self, kandidat: Kandidat) -> None:
        """Menambahkan objek kandidat baru ke dalam daftar pengawasan pipeline."""
        if not isinstance(kandidat, Kandidat):
            raise TypeError("Objek yang dimasukkan bukan instansi dari kelas Kandidat.")
        if any(k.id_kandidat == kandidat.id_kandidat for k in self._daftar_kandidat):
            raise ValueError(f"ID kandidat '{kandidat.id_kandidat}' sudah terdaftar.")
        self._daftar_kandidat.append(kandidat)

    def tambah_lowongan(self, lowongan: Lowongan) -> None:
        """Menambahkan objek lowongan pekerjaan baru ke dalam sistem."""
        if not isinstance(lowongan, Lowongan):
            raise TypeError("Objek yang dimasukkan bukan instansi dari kelas Lowongan.")
        if any(l.id_lowongan == lowongan.id_lowongan for l in self._daftar_lowongan):
            raise ValueError(f"ID lowongan '{lowongan.id_lowongan}' sudah terdaftar.")
        self._daftar_lowongan.append(lowongan)

    def cari_kandidat(self, id_kandidat: str) -> Kandidat:
        """
        Mencari objek kandidat berdasarkan ID.
        Akan memicu ApplicationNotFoundException jika gagal (Fitur F6).
        """
        for k in self._daftar_kandidat:
            if k.id_kandidat == id_kandidat:
                return k

        # Fitur F6 berjalan di sini!
        raise ApplicationNotFoundException(f"GAGAL: Kandidat dengan ID '{id_kandidat}' tidak terdaftar di pipeline.")

    def cari_lowongan(self, id_lowongan: str) -> Lowongan:
        """Mencari objek lowongan berdasarkan ID. Memicu LowonganNotFoundException jika gagal."""
        for l in self._daftar_lowongan:
            if l.id_lowongan == id_lowongan:
                return l
        raise LowonganNotFoundException(f"GAGAL: Lowongan dengan ID '{id_lowongan}' tidak ditemukan.")

    def lowongan_kandidat(self, id_kandidat: str) -> Lowongan:
        """Mengambil lowongan tempat kandidat melamar."""
        self.cari_kandidat(id_kandidat)
        id_lowongan = self._lamaran.get(id_kandidat)
        if id_lowongan is None:
            raise ValueError(f"Kandidat '{id_kandidat}' belum tercatat melamar ke lowongan mana pun.")
        return self.cari_lowongan(id_lowongan)

    # -------------------------------------
    # F2: KANDIDAT MELAMAR
    # -------------------------------------
    def lamar(self, kandidat: Kandidat, id_lowongan: str) -> None:
        """
        Mencatat lamaran kandidat ke sebuah lowongan (F2).
        Syarat: lowongan masih buka, CV sudah diisi, dan kandidat belum pernah
        melamar ke lowongan yang sama (dicek lewat email).
        """
        if not isinstance(kandidat, Kandidat):
            raise TypeError("Objek yang dimasukkan bukan instansi dari kelas Kandidat.")

        lowongan = self.cari_lowongan(id_lowongan)
        if not lowongan.is_buka():
            raise ValueError(f"Lowongan [{id_lowongan}] tidak menerima lamaran (belum dipublikasikan atau sudah ditutup).")
        if not kandidat.punya_cv:
            raise ValueError("Kandidat wajib mengisi teks CV sebelum melamar.")

        for k in self._daftar_kandidat:
            if k.email == kandidat.email and self._lamaran.get(k.id_kandidat) == id_lowongan:
                raise ValueError(f"Email '{kandidat.email}' sudah melamar ke lowongan [{id_lowongan}].")

        self.tambah_kandidat(kandidat)
        self._lamaran[kandidat.id_kandidat] = id_lowongan

    # -------------------------------------
    # PROSES INTI
    # -------------------------------------
    def proses_evaluasi(self, id_kandidat: str, evaluasi: Evaluasi) -> float:
        """
        Mengeksekusi method polymorphism hitung_skor() dari objek evaluasi
        yang dikirimkan, lalu mengembalikan nilai skor akhirnya.
        """
        # Jika kandidat tidak ada, baris ini melempar ApplicationNotFoundException
        self.cari_kandidat(id_kandidat)

        if not isinstance(evaluasi, Evaluasi):
            raise TypeError("Objek evaluasi harus turunan dari kelas Evaluasi.")

        # Polimorfisme berjalan di sini (memanggil hitung_skor sesuai jenis kelas turunan evaluasi)
        return evaluasi.hitung_skor()

    def screening_cv(self, id_kandidat: str) -> dict:
        """
        Menjalankan alur F3 - F5 untuk satu kandidat:
        hitung skor CV dengan keyword lowongan -> bandingkan dengan threshold ->
        pindahkan status (lolos: Interview, tidak lolos: Ditolak).
        Return dictionary berisi ringkasan hasil screening.
        """
        kandidat = self.cari_kandidat(id_kandidat)
        lowongan = self.lowongan_kandidat(id_kandidat)

        if kandidat.status_pipeline not in ("Baru", "Screening"):
            raise ValueError(f"Screening hanya untuk kandidat berstatus Baru/Screening, "
                             f"sedangkan status saat ini '{kandidat.status_pipeline}'.")
        if not kandidat.punya_cv:
            raise ValueError("Kandidat belum memiliki teks CV untuk di-screening.")

        # Hitung skor lebih dulu: jika gagal (misalnya keyword kosong), status belum berubah
        evaluasi = EvaluasiCV(f"CV-{id_kandidat}", "", kandidat.cv_text, lowongan.kualifikasi)
        skor = self.proses_evaluasi(id_kandidat, evaluasi)
        lolos = lowongan.cek_kelolosan(skor)

        if kandidat.status_pipeline == "Baru":
            kandidat.update_status("Screening")
        kandidat.update_status("Interview" if lolos else "Ditolak")
        self._skor_cv[id_kandidat] = skor

        return {
            "id_kandidat": id_kandidat,
            "skor": skor,
            "threshold": lowongan.get_threshold(),
            "lolos": lolos,
            "keyword_cocok": evaluasi.matched_keywords,
            "status": kandidat.status_pipeline,
        }

    # -------------------------------------
    # F7 & F8: WAWANCARA
    # -------------------------------------
    def jadwalkan_wawancara(self, id_kandidat: str, nama_interviewer: str, tipe: str, waktu: str) -> EvaluasiWawancara:
        """Menjadwalkan (atau menjadwalkan ulang) wawancara untuk kandidat berstatus Interview (F7)."""
        kandidat = self.cari_kandidat(id_kandidat)
        if kandidat.status_pipeline != "Interview":
            raise ValueError(f"Wawancara hanya untuk kandidat berstatus Interview, "
                             f"sedangkan status saat ini '{kandidat.status_pipeline}'.")

        wawancara = self._wawancara.get(id_kandidat) or EvaluasiWawancara(f"WW-{id_kandidat}")
        wawancara.jadwalkan(nama_interviewer, tipe, waktu)  # Jika gagal validasi, tidak ada yang tersimpan
        self._wawancara[id_kandidat] = wawancara
        return wawancara

    def nilai_wawancara(self, id_kandidat: str, skor_teknis: float, skor_softskill: float) -> float:
        """Menyimpan penilaian wawancara dan mengembalikan skor akhirnya (F8)."""
        self.cari_kandidat(id_kandidat)
        wawancara = self._wawancara.get(id_kandidat)
        if wawancara is None or not wawancara.sudah_dijadwalkan:
            raise ValueError("Wawancara kandidat ini belum dijadwalkan.")

        wawancara.input_nilai(skor_teknis, skor_softskill)
        skor = self.proses_evaluasi(id_kandidat, wawancara)
        self._skor_wawancara[id_kandidat] = skor
        return skor

    def get_wawancara(self, id_kandidat: str) -> EvaluasiWawancara:
        """Mengambil data wawancara milik kandidat."""
        self.cari_kandidat(id_kandidat)
        wawancara = self._wawancara.get(id_kandidat)
        if wawancara is None:
            raise ValueError("Kandidat ini belum memiliki data wawancara.")
        return wawancara

    # -------------------------------------
    # F9 & F10: KOMPARASI & TAMPILAN
    # -------------------------------------
    def komparasi_skor_kandidat(self, data_skor: dict = None) -> list:
        """
        Memenuhi Fitur F9: Mengomparasi dan merangking skor antar kandidat.
        Menerima dictionary {id_kandidat: skor}. Jika tidak diberikan, memakai
        skor wawancara yang sudah tersimpan. Skor yang sama mendapat peringkat yang sama.
        Return list berisi tuple (id_kandidat, skor) yang sudah terurut.
        """
        if data_skor is None:
            data_skor = dict(self._skor_wawancara)

        if not data_skor:
            print("Belum ada data skor untuk dikomparasi.")
            return []

        print("\n=== LEADERBOARD (KOMPARASI KANDIDAT) ===")
        # Mengurutkan dari skor tertinggi ke terendah (Descending)
        ranking = sorted(data_skor.items(), key=lambda item: item[1], reverse=True)

        peringkat = 0
        skor_sebelumnya = None
        for urutan, (id_kand, skor) in enumerate(ranking, start=1):
            if skor != skor_sebelumnya:
                peringkat = urutan
                skor_sebelumnya = skor
            try:
                kandidat = self.cari_kandidat(id_kand)
                print(f"Rank {peringkat}. {kandidat.nama} (ID: {id_kand}) -> Skor Akhir: {skor}")
            except ApplicationNotFoundException:
                print(f"Rank {peringkat}. [Data Pelamar Dihapus/Tidak Valid] -> Skor Akhir: {skor}")

        return ranking

    def tampil_pipeline(self) -> None:
        """Menampilkan seluruh daftar kandidat beserta status tahapannya secara terpusat (Fitur F10)."""
        print("\n" + "=" * 45)
        print("         REKAP PIPELINE REKRUTMEN")
        print("=" * 45)

        if not self._daftar_kandidat:
            print("Belum ada data kandidat di dalam pipeline.")
            print("=" * 45)
            return

        print(f"Total Pelamar Aktif: {len(self._daftar_kandidat)} orang\n")
        for kandidat in self._daftar_kandidat:
            id_lowongan = self._lamaran.get(kandidat.id_kandidat, "-")
            print(f"{kandidat} | Lowongan: {id_lowongan}")

        print("=" * 45)

    # -------------------------------------
    # ITERATOR PATTERN: KANDIDAT PER LOWONGAN
    # -------------------------------------
    def __iter__(self):
        """Membuat PipelineManager bisa di-loop: for kandidat in pm. Mengiterasi semua kandidat."""
        return KandidatIterator(self._daftar_kandidat, self._lamaran)

    def iter_kandidat(self, id_lowongan: str = None):
        """
        Mengembalikan iterator kandidat. Jika id_lowongan diberikan, hanya kandidat
        yang melamar ke lowongan tersebut. Memicu LowonganNotFoundException jika ID salah.
        """
        if id_lowongan is not None:
            self.cari_lowongan(id_lowongan)
        return KandidatIterator(self._daftar_kandidat, self._lamaran, id_lowongan)


    # -------------------------------------
    # GENERATOR: KANDIDAT BERDASARKAN STATUS
    # -------------------------------------
    def kandidat_berstatus(self, status: str):
        """
        Generator (memakai yield): menghasilkan kandidat satu per satu yang status
        pipeline-nya sama dengan `status` (huruf besar/kecil diabaikan).
        Contoh: for k in pm.kandidat_berstatus("Interview"): print(k.nama)
        """
        status_bersih = status.strip().capitalize()
        for kandidat in self._daftar_kandidat:
            if kandidat.status_pipeline == status_bersih:
                yield kandidat


# -------------------------------------
# ITERATOR PATTERN
# -------------------------------------
class KandidatIterator:
    """
    Iterator untuk menelusuri kandidat satu per satu tanpa membuka struktur list internal.
    - __iter__ : mengembalikan dirinya sendiri (objek iterator).
    - __next__ : mengembalikan kandidat berikutnya, atau raise StopIteration jika habis.
    Jika id_lowongan diisi, kandidat yang tidak melamar ke lowongan itu dilewati.
    """

    def __init__(self, daftar_kandidat: list, lamaran: dict, id_lowongan: str = None):
        self._daftar_kandidat = list(daftar_kandidat)   # Salinan, agar aman dari perubahan saat iterasi
        self._lamaran = dict(lamaran)
        self._id_lowongan = id_lowongan
        self._indeks = 0

    def __iter__(self):
        return self

    def __next__(self) -> Kandidat:
        while self._indeks < len(self._daftar_kandidat):
            kandidat = self._daftar_kandidat[self._indeks]
            self._indeks += 1
            if self._id_lowongan is None or self._lamaran.get(kandidat.id_kandidat) == self._id_lowongan:
                return kandidat
        raise StopIteration
