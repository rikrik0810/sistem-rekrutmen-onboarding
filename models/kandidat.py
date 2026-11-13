"""
models/kandidat.py - Kelas entitas Kandidat (data pelamar dan status pipeline).

Tujuan:
    Menyimpan data pelamar (nama, email, no. telepon, teks CV) dan melacak statusnya di pipeline.
    ALUR_STATUS menjaga perpindahan status yang diizinkan (Baru -> Screening -> Interview -> ...),
    sehingga melompat tahap ditolak dengan ValueError (F5).

Hubungan dengan file lain:
    - Tidak meng-import file proyek lain, sehingga lapisan models tidak bergantung pada services.
      ID kandidat dibuat oleh pemanggil (lihat dari_dict).
    - Dipakai services/pipeline_manager.py (menyimpan kandidat, lamar, screening, wawancara)
      dan main.py (membuat objek lewat Kandidat.dari_dict serta membaca ALUR_STATUS).
"""

from datetime import datetime


class Kandidat:
    """
    Kelas entitas untuk merepresentasikan data pelamar pekerjaan.
    Menyimpan informasi pribadi, dokumen (CV), dan melacak status tahapan dalam pipeline.
    """

    # Alur status yang diizinkan (F5): status sekarang -> daftar status berikutnya.
    # Diterima dan Ditolak adalah status akhir, sehingga tidak punya tujuan lanjutan.
    ALUR_STATUS = {
        "Baru": ["Screening", "Ditolak"],
        "Screening": ["Interview", "Ditolak"],
        "Interview": ["Offering", "Ditolak"],
        "Offering": ["Diterima", "Ditolak"],
        "Diterima": [],
        "Ditolak": [],
    }
    STATUS_VALID = tuple(ALUR_STATUS)

    @staticmethod
    def _email_valid(email: str) -> bool:
        """Cek format email sederhana tanpa modul tambahan: satu '@', ada titik di domain."""
        email = email.strip()
        if " " in email or email.count("@") != 1:
            return False
        lokal, domain = email.split("@")
        return (lokal != "" and "." in domain and not domain.startswith(".") and not domain.endswith("."))

    def __init__(self, id_kandidat: str, nama: str, email: str, no_telp: str = "", cv_text: str = ""):
        # Validasi data wajib agar tidak ada kandidat "kosong" di dalam sistem
        if not id_kandidat or not id_kandidat.strip():
            raise ValueError("ID kandidat tidak boleh kosong.")
        if not nama or not nama.strip():
            raise ValueError("Nama kandidat tidak boleh kosong.")
        if not email or not self._email_valid(email):
            raise ValueError(f"Format email '{email}' tidak valid.")

        self._id_kandidat = id_kandidat.strip()
        self._nama = nama.strip()
        self._email = email.strip().lower()
        self._no_telp = no_telp.strip()
        self._cv_text = cv_text.strip()
        self._status_pipeline = "Baru"  # Titik awal alur F5: Baru -> Screening -> Interview
        self._tanggal_melamar = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


    @property
    def id_kandidat(self) -> str:
        return self._id_kandidat

    @property
    def nama(self) -> str:
        return self._nama

    @property
    def email(self) -> str:
        return self._email

    @property
    def no_telp(self) -> str:
        return self._no_telp

    @property
    def cv_text(self) -> str:
        return self._cv_text

    @property
    def status_pipeline(self) -> str:
        return self._status_pipeline

    @property
    def tanggal_melamar(self) -> str:
        return self._tanggal_melamar

    @property
    def punya_cv(self) -> bool:
        """True jika kandidat sudah mengisi teks CV (dipakai sebelum screening F3)."""
        return bool(self._cv_text)


    def set_cv_text(self, teks_cv: str) -> None:
        """
        Menyimpan atau memperbarui teks CV milik pelamar (Digunakan untuk F2).
        """
        if not teks_cv or not teks_cv.strip():
            raise ValueError("Teks CV tidak boleh kosong.")
        self._cv_text = teks_cv.strip()

    def update_status(self, status_baru: str) -> None:
        """
        Memperbarui tahapan status pipeline pelamar (F5).
        Hanya perpindahan sesuai ALUR_STATUS yang diizinkan, misalnya
        Baru -> Screening -> Interview. Melompat tahap akan ditolak.
        """
        status_bersih = status_baru.strip().title()  # "interview" -> "Interview"

        if status_bersih not in self.STATUS_VALID:
            raise ValueError(f"Status '{status_baru}' tidak valid. Pilih dari: {list(self.STATUS_VALID)}")

        if status_bersih == self._status_pipeline:
            raise ValueError(f"Kandidat sudah berstatus '{status_bersih}'.")

        tujuan_boleh = self.ALUR_STATUS[self._status_pipeline]
        if status_bersih not in tujuan_boleh:
            if not tujuan_boleh:
                raise ValueError(f"Status '{self._status_pipeline}' sudah final dan tidak dapat diubah.")
            raise ValueError(f"Perpindahan '{self._status_pipeline}' -> '{status_bersih}' tidak diizinkan. Tahap berikutnya yang valid: {tujuan_boleh}")

        self._status_pipeline = status_bersih

    def get_info(self) -> str:
        """
        Mengembalikan ringkasan data profil serta status terbaru kandidat.
        """
        return f"[{self._id_kandidat}] {self._nama} ({self._email}) - Status: {self._status_pipeline}"

    def __str__(self) -> str:
        """
        Magic method agar print(objek_kandidat) menampilkan informasi ringkas,
        bukan alamat memori '<Kandidat object at ...>'.
        """
        return self.get_info()

 
    @classmethod
    def dari_dict(cls, data: dict, id_kandidat: str):
        """
        Membuat objek Kandidat dari dictionary.
        ID dibuat oleh pemanggil (misalnya SistemHelper.generasi_id("K")) supaya
        kelas entitas ini tidak bergantung pada lapisan services.
        Data wajib (nama, email) yang kosong akan ditolak oleh constructor.
        """
        return cls(
            id_kandidat=id_kandidat,
            nama=data.get("nama", ""),
            email=data.get("email", ""),
            no_telp=data.get("no_telp", ""),
            cv_text=data.get("cv_text", ""),
        )