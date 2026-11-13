# Sistem Rekrutmen & Onboarding (HR)

Proyek OOP berbasis **Command Line Interface (CLI)** untuk membantu tim HR mengelola proses rekrutmen: membuat lowongan, menerima lamaran, menyaring CV secara otomatis, menjadwalkan dan menilai wawancara, sampai membandingkan skor antar kandidat.

> Cakupan versi ini: **UTS** (fitur 1-10). Fitur UAS (offer letter, onboarding, laporan rekrutmen) belum dikerjakan.

## Daftar Isi
- [Fitur](#fitur)
- [Persyaratan](#persyaratan)
- [Cara Menjalankan](#cara-menjalankan)
- [Contoh Alur Demo](#contoh-alur-demo)
- [Struktur Folder](#struktur-folder)
- [Konsep OOP yang Diterapkan](#konsep-oop-yang-diterapkan)
- [Keterbatasan](#keterbatasan)
- [Anggota Kelompok](#anggota-kelompok)

## Fitur

| Menu | Fitur | Keterangan |
|---|---|---|
| 1 | Buat lowongan kerja | Isi posisi, divisi, threshold (0-100), batas lamar, dan keyword kualifikasi |
| 2 | Publikasikan lowongan | Mengubah lowongan Draft menjadi terbuka untuk lamaran |
| 3 | Lihat daftar lowongan | Menampilkan semua lowongan dan status publikasinya |
| 4 | Kandidat melamar | Menyimpan data pelamar dan teks CV (status awal: Baru) |
| 5 | Screening CV otomatis | Menghitung skor kecocokan keyword, lalu status menjadi Interview (lolos) atau Ditolak |
| 6 | Ubah status pipeline | Memindahkan status kandidat secara manual sesuai alur yang diizinkan |
| 7 | Jadwalkan wawancara | Menyimpan jadwal, pewawancara, dan tipe wawancara (HR/Teknis) |
| 8 | Input nilai wawancara | Skor akhir = 60% nilai teknis + 40% nilai soft skill |
| 9 | Komparasi skor kandidat | Peringkat kandidat dari skor wawancara tertinggi |
| 10 | Tampilkan status pipeline | Rekap seluruh kandidat dan statusnya |
| 11 | Isi data contoh | Memuat 1 lowongan dan 3 pelamar untuk keperluan demo |

**Alur status pipeline:**

```
Baru -> Screening -> Interview -> Offering -> Diterima
(dari tahap mana pun boleh ke Ditolak; Diterima dan Ditolak bersifat final)
```

## Persyaratan
- Python 3.8 atau lebih baru (diuji pada Python 3.12)
- Tidak ada library eksternal yang perlu dipasang

## Cara Menjalankan

```bash
git clone <link-repository-ini>
cd <nama-folder-repository>
python main.py
```

Jika perintah `python` tidak dikenali, coba `py main.py` (Windows) atau `python3 main.py` (Mac/Linux).

Jalankan dari folder yang berisi `main.py`, bukan dari dalam folder `models/` atau `services/`.

## Contoh Alur Demo

Cara tercepat mencoba program:

1. Jalankan `python main.py`.
2. Pilih **11** untuk mengisi data contoh.
3. Pilih **10** untuk melihat daftar kandidat dan ID-nya. ID dibuat acak setiap program dijalankan.
4. Pilih **5**, lalu masukkan ID kandidat untuk screening CV.
5. Pilih **7** untuk menjadwalkan wawancara kandidat yang lolos, lalu **8** untuk input nilai.
6. Pilih **9** untuk membandingkan skor, lalu **10** lagi untuk melihat status terbaru.

Contoh tampilan menu 5:

```
Skor CV      : 75.0% (threshold 60.0%)
Keyword cocok: Python, SQL, OOP
Hasil        : LOLOS -> status Interview
```

Contoh input dan output untuk setiap menu tersedia di file `Panduan_Input_Program.txt`.

## Struktur Folder

```
sistem_rekrutmen_dan_onboarding/
├── main.py                     # Titik masuk program (menu CLI)
├── models/
│   ├── base.py                 # Evaluasi (Abstract Base Class)
│   ├── evaluasi_cv.py          # EvaluasiCV
│   ├── evaluasi_wawancara.py   # EvaluasiWawancara
│   ├── evaluasi_onboarding.py  # EvaluasiOnboarding
│   ├── kandidat.py             # Kandidat (entity)
│   └── lowongan.py             # Lowongan (entity)
└── services/
    ├── pipeline_manager.py     # PipelineManager, KandidatIterator, exception khusus
    └── sistem_helper.py        # SistemHelper (utilitas, pembuat ID unik)
```

## Konsep OOP yang Diterapkan

| Konsep | Penerapan |
|---|---|
| Abstract Base Class | `Evaluasi` dengan abstract method `hitung_skor()` |
| Inheritance | `EvaluasiCV`, `EvaluasiWawancara`, dan `EvaluasiOnboarding` mewarisi `Evaluasi` |
| Polymorphism | `hitung_skor()` menghasilkan perhitungan berbeda di tiap kelas turunan, dipanggil lewat `PipelineManager.proses_evaluasi()` |
| Encapsulation | Atribut `_protected` dengan akses lewat `@property` |
| Exception Handling | `RekrutmenException`, `ApplicationNotFoundException`, `LowonganNotFoundException`, serta `ValueError` untuk validasi input |
| Iterator | `KandidatIterator` (`__iter__` dan `__next__`), diakses lewat `PipelineManager.iter_kandidat()` |
| Generator | `PipelineManager.kandidat_berstatus()` memakai `yield` |

## Keterbatasan
- Antarmuka berupa teks di terminal, tanpa GUI maupun web.
- Data hanya disimpan di memori, sehingga hilang saat program ditutup.
- Screening CV mencocokkan kata utuh tanpa memahami makna kalimat.
- Format waktu wawancara tidak divalidasi.

## Anggota Kelompok

**Kelompok XI**

- Hernandez Louis
- Rayvind Gebgson Limin
- Frederik Chandra
- Alvaro Davis
