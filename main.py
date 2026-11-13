"""
main.py - Titik masuk (entry point) program Sistem Rekrutmen & Onboarding (CLI).

Tujuan:
    Menyediakan menu terminal untuk HR: membuat dan mempublikasikan lowongan (F1),
    kandidat melamar (F2), screening CV otomatis (F3-F6), jadwal dan penilaian
    wawancara (F7-F9), serta menampilkan status pipeline (F10).

Hubungan dengan file lain:
    - models/kandidat.py        : membuat objek Kandidat (Kandidat.dari_dict) dan membaca ALUR_STATUS.
    - models/lowongan.py        : membuat objek Lowongan beserta kualifikasinya.
    - services/pipeline_manager.py : semua logika bisnis dijalankan lewat PipelineManager;
                                  exception RekrutmenException ditangkap di sini.
    - services/sistem_helper.py : membuat ID acak dan merapikan teks input.
    File ini hanya menangani input dan output; tidak ada file lain yang meng-import main.py.
"""

from models.kandidat import Kandidat
from models.lowongan import Lowongan
from services.pipeline_manager import PipelineManager, RekrutmenException
from services.sistem_helper import SistemHelper



def input_teks(label: str) -> str:
    """Membaca satu baris input dan merapikan spasinya."""
    return SistemHelper.bersihkan_teks(input(f"{label}: "))


def input_angka(label: str) -> float:
    """Membaca angka; jika salah ketik, diminta mengulang sampai valid."""
    while True:
        try:
            return float(input_teks(label).replace(",", "."))
        except ValueError:
            print("  ! Masukkan angka yang valid.")


def id_baru(prefix: str, daftar_objek, nama_atribut: str) -> str:
    """Membuat ID acak yang tidak bentrok dengan ID yang sudah ada."""
    terpakai = [getattr(objek, nama_atribut) for objek in daftar_objek]
    return SistemHelper.generasi_id(prefix, terpakai)



# MENU: LOWONGAN (F1)
def buat_lowongan(pm: PipelineManager) -> None:
    print("\n--- BUAT LOWONGAN KERJA ---")
    judul = input_teks("Judul posisi")
    divisi = input_teks("Divisi")
    threshold = input_angka("Skor threshold kelolosan (0-100)")
    batas = input_teks("Batas lamar YYYY-MM-DD (kosongkan jika tidak ada)")
    lowongan = Lowongan(id_baru("L", pm.daftar_lowongan, "id_lowongan"), judul, divisi, threshold, batas)

    for kata in input_teks("Kualifikasi/keyword (pisahkan dengan koma)").split(","):
        if kata.strip():
            lowongan.tambah_kualifikasi(kata)

    pm.tambah_lowongan(lowongan)
    print(f"Lowongan berhasil dibuat dengan ID {lowongan.id_lowongan} (status Draft).")

    if input_teks("Publikasikan sekarang? (y/n)").lower() == "y":
        lowongan.publikasikan()
        print("Lowongan dipublikasikan dan siap menerima lamaran.")


def publikasikan_lowongan(pm: PipelineManager) -> None:
    print("\n--- PUBLIKASIKAN LOWONGAN ---")
    lowongan = pm.cari_lowongan(input_teks("ID lowongan"))
    lowongan.publikasikan()
    print(f"Lowongan [{lowongan.id_lowongan}] berhasil dipublikasikan.")


def tampil_lowongan(pm: PipelineManager) -> None:
    print("\n--- DAFTAR LOWONGAN ---")
    if not pm.daftar_lowongan:
        print("Belum ada lowongan.")
    for lowongan in pm.daftar_lowongan:
        print(lowongan)
        print()



# MENU: KANDIDAT & SCREENING (F2 - F6)
def kandidat_melamar(pm: PipelineManager) -> None:
    print("\n--- KANDIDAT MELAMAR ---")
    id_lowongan = input_teks("ID lowongan yang dilamar")
    data = {
        "nama": input_teks("Nama lengkap"),
        "email": input_teks("Email"),
        "no_telp": input_teks("No. telepon (boleh kosong)"),
        "cv_text": input_teks("Teks CV (satu baris)"),
    }
    kandidat = Kandidat.dari_dict(data, id_baru("K", pm.daftar_kandidat, "id_kandidat"))
    pm.lamar(kandidat, id_lowongan)
    print(f"Lamaran diterima. ID kandidat Anda: {kandidat.id_kandidat}")


def screening_cv(pm: PipelineManager) -> None:
    print("\n--- SCREENING CV OTOMATIS ---")
    hasil = pm.screening_cv(input_teks("ID kandidat"))
    print(f"Skor CV      : {hasil['skor']}% (threshold {hasil['threshold']}%)")
    print(f"Keyword cocok: {', '.join(hasil['keyword_cocok']) or '-'}")
    print(f"Hasil        : {'LOLOS' if hasil['lolos'] else 'TIDAK LOLOS'} -> status {hasil['status']}")


def ubah_status(pm: PipelineManager) -> None:
    print("\n--- UBAH STATUS PIPELINE ---")
    kandidat = pm.cari_kandidat(input_teks("ID kandidat"))
    berikutnya = Kandidat.ALUR_STATUS[kandidat.status_pipeline]
    print(f"Status saat ini: {kandidat.status_pipeline} | Tahap berikutnya yang diizinkan: {berikutnya or 'tidak ada (status final)'}")
    kandidat.update_status(input_teks("Status baru"))
    print(f"Status berhasil diubah menjadi {kandidat.status_pipeline}.")



# MENU: WAWANCARA (F7 - F9)
def jadwalkan_wawancara(pm: PipelineManager) -> None:
    print("\n--- JADWALKAN WAWANCARA ---")
    wawancara = pm.jadwalkan_wawancara(
        input_teks("ID kandidat"),
        input_teks("Nama interviewer"),
        input_teks("Tipe (HR/Teknis)"),
        input_teks("Waktu (contoh 2026-11-05 10:00)"),
    )
    print("Jadwal tersimpan:")
    print(wawancara)


def nilai_wawancara(pm: PipelineManager) -> None:
    print("\n--- INPUT NILAI WAWANCARA (Teknis 60% + Soft Skill 40%) ---")
    skor = pm.nilai_wawancara(
        input_teks("ID kandidat"),
        input_angka("Nilai teknis (0-100)"),
        input_angka("Nilai soft skill (0-100)"),
    )
    print(f"Penilaian tersimpan. Skor akhir wawancara: {skor}")


def komparasi_skor(pm: PipelineManager) -> None:
    pm.komparasi_skor_kandidat()



# MENU: PIPELINE (F10) & DATA CONTOH
def tampil_pipeline(pm: PipelineManager) -> None:
    pm.tampil_pipeline()


# def isi_data_contoh(pm: PipelineManager) -> None:
#     """Mengisi satu lowongan dan tiga pelamar agar program mudah diuji/didemokan."""
#     lowongan = Lowongan(id_baru("L", pm.daftar_lowongan, "id_lowongan"), "Software Engineer", "IT", 60.0)
#     for kata in ["Python", "SQL", "OOP", "Git"]:
#         lowongan.tambah_kualifikasi(kata)
#     lowongan.publikasikan()
#     pm.tambah_lowongan(lowongan)

#     contoh = [
#         ("Erik", "erik@email.com", "Berpengalaman Python, SQL, OOP, dan Git di proyek kampus"),
#         ("Albeth", "albeth@email.com", "Menguasai Python dan SQL untuk analisis data"),
#         ("Budi", "budi@email.com", "Berpengalaman di bidang pemasaran dan penjualan"),
#     ]
#     for nama, email, cv in contoh:
#         kandidat = Kandidat.dari_dict({"nama": nama, "email": email, "cv_text": cv},
#                                       id_baru("K", pm.daftar_kandidat, "id_kandidat"))
#         pm.lamar(kandidat, lowongan.id_lowongan)

#     print(f"Data contoh dimuat: lowongan {lowongan.id_lowongan} dan {len(contoh)} pelamar.")


# MENU UTAMA
MENU = {
    "1": ("Buat lowongan kerja", buat_lowongan),
    "2": ("Publikasikan lowongan", publikasikan_lowongan),
    "3": ("Lihat daftar lowongan", tampil_lowongan),
    "4": ("Kandidat melamar", kandidat_melamar),
    "5": ("Screening CV otomatis", screening_cv),
    "6": ("Ubah status pipeline", ubah_status),
    "7": ("Jadwalkan wawancara", jadwalkan_wawancara),
    "8": ("Input nilai wawancara", nilai_wawancara),
    "9": ("Komparasi skor kandidat", komparasi_skor),
    "10": ("Tampilkan status pipeline", tampil_pipeline)
    # "11": ("Isi data contoh", isi_data_contoh),
}


def tampil_menu() -> None:
    print("\n" + "=" * 45)
    print("   SISTEM REKRUTMEN & ONBOARDING (HR)")
    print("=" * 45)
    for nomor, (nama, _) in MENU.items():
        print(f"{nomor:>3}. {nama}")
    print("  0. Keluar")
    print("=" * 45)


def main() -> None:
    pm = PipelineManager()
    while True:
        tampil_menu()
        pilihan = input("Pilih menu: ").strip()

        if pilihan == "0":
            print("Terima kasih. Program selesai.")
            break

        if pilihan not in MENU:
            print("Pilihan tidak tersedia. Pilih nomor yang ada di menu.")
            continue

        # Exception Handling: setiap kesalahan ditampilkan sebagai pesan, program tidak berhenti
        try:
            MENU[pilihan][1](pm)
        except RekrutmenException as e:  # ApplicationNotFoundException, LowonganNotFoundException
            print(f"\n[TIDAK DITEMUKAN] {e}")
        except (ValueError, TypeError) as e:
            print(f"\n[DITOLAK] {e}")


if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print("\nProgram dihentikan.")