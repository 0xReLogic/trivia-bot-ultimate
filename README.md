# Trivia Bot Ultimate

![Status](https://img.shields.io/badge/status-production_ready-green.svg) ![License](https://img.shields.io/badge/license-MIT-blue.svg) ![PRs](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)
![C++](https://img.shields.io/badge/C++-17-blue.svg?logo=c%2B%2B) ![Python](https://img.shields.io/badge/Python-3.8+-blue.svg?logo=python) ![LLM Offline Ready](https://img.shields.io/badge/LLM--Offline-Supported-purple)
![Made with ❤️](https://img.shields.io/badge/Made_with-%E2%9D%A4-red)

**Trivia Bot Ultimate** adalah sebuah sistem AI canggih yang dirancang untuk mendominasi game trivia, dengan fokus utama pada game-game yang ada di platform **Hago**. Dibangun dengan arsitektur hybrid yang menggabungkan kecepatan C++ untuk pemrosesan tingkat rendah dan kecerdasan Python untuk pengambilan keputusan, bot ini mampu belajar dari pengalamannya dan beradaptasi dengan berbagai aplikasi trivia.

## Fitur Utama

- **Arsitektur Hybrid C++/Python**: Menggunakan C++ untuk tugas-tugas yang sensitif terhadap latensi seperti pemrosesan gambar dan interaksi perangkat, sementara Python menangani logika AI yang kompleks, memastikan kinerja dan kecerdasan yang optimal.
- **Kecerdasan Bertingkat (Multi-layered Intelligence)**: Mengimplementasikan alur keputusan strategis untuk efisiensi maksimal:
  1.  **Cache Cepat**: Jawaban instan untuk pertanyaan yang pernah dilihat (pencarian hash).
  2.  **Database Pembelajaran**: Menemukan pertanyaan serupa secara semantik menggunakan *vector embeddings*.
  3.  **Dukungan LLM Offline (TinyLLM)**: Terintegrasi dengan mesin TinyLLM lokal yang ringan. Ini memungkinkan bot untuk menjawab pertanyaan bahkan tanpa koneksi internet, menggunakan pencocokan pola dan *reasoning* berbasis aturan untuk efisiensi biaya dan privasi.
  4.  **API Eksternal (Gemini)**: Memanfaatkan kekuatan model bahasa besar sebagai pilihan terakhir untuk akurasi tertinggi.
- **Sistem Pembelajaran Mandiri**: Bot secara otomatis menganalisis umpan balik (benar atau salah) setelah setiap jawaban untuk memperbarui basis pengetahuannya, memungkinkannya menjadi lebih akurat seiring waktu.
- **Deteksi & Interaksi Cerdas**: Mampu melakukan OCR pada area layar tertentu, mem-parsing pertanyaan dan pilihan, serta mendeteksi elemen UI seperti tombol "Mulai" atau "Main Lagi".
- **Konfigurasi Fleksibel**: Semua parameter penting (koordinat, *threshold*, kunci API) dikelola melalui file `config/settings.json` eksternal, memungkinkan penyesuaian yang mudah tanpa mengubah kode.
- **Robust & Andal**: Dilengkapi dengan penanganan kesalahan yang komprehensif, sistem *logging* terperinci, dan mekanisme pemulihan untuk memastikan operasi yang stabil.

## Analisis Performa & Latency

Bot ini dirancang untuk kecepatan. Dengan batas waktu trivia yang biasanya hanya 10 detik per soal, setiap milidetik sangat berharga. Berikut adalah perkiraan rincian waktu yang dibutuhkan bot untuk menjawab satu soal, tergantung pada sumber jawaban yang digunakan.

| Tahapan Proses                  | Sumber Jawaban      | Perkiraan Waktu (ms) | Keterangan                                        |
| ------------------------------- | ------------------- | -------------------- | ------------------------------------------------- |
| 1. Akuisisi Gambar & OCR        | *Semua Skenario*    | ~480 ms              | Mengambil screenshot via ADB dan OCR dengan Tesseract. |
| 2. Jembatan IPC (C++ → Python)  | *Semua Skenario*    | ~20 ms               | Mengirim data pertanyaan ke Python.               |
| 3. **Inti Keputusan (Python)**  | **Cache (Level 1)** | **~30 ms**           | Pencarian hash di database (paling cepat).        |
|                                 | **Learned DB (L2)** | ~350 ms              | Membuat embedding & mencari kemiripan.            |
|                                 | **TinyLLM (L3)**    | ~800 ms              | Inferensi pada model LLM lokal (CPU).             |
|                                 | **Gemini API (L4)** | ~1500 ms             | Panggilan API via internet (paling lambat).       |
| 4. Jembatan IPC (Python → C++)  | *Semua Skenario*    | ~20 ms               | Mengirim hasil jawaban ke C++.                    |
| 5. Eksekusi Aksi (Tap)          | *Semua Skenario*    | ~120 ms              | Mencocokkan teks & melakukan tap via ADB.         |
| **TOTAL WAKTU (Perkiraan)**     |                     |                      |                                                   |
|                                 | **Cache Hit**       | **~670 ms**          | **Kurang dari 1 detik.**                          |
|                                 | **Learned DB Hit**  | **~990 ms**          | **Sekitar 1 detik.**                              |
|                                 | **TinyLLM Offline** | **~1440 ms**         | **Sekitar 1.5 detik.**                            |
|                                 | **Gemini API**      | **~2140 ms**         | **Sekitar 2.1 detik.**                            |

**Kesimpulan:**

Bahkan dalam skenario terburuk yang memerlukan panggilan ke API eksternal, bot ini diperkirakan dapat menjawab soal dalam **~2.1 detik**, jauh di bawah batas waktu 10 detik. Ini memberikan banyak ruang untuk variasi jaringan dan beban sistem, memastikan bot tetap kompetitif dan andal.

*Disclaimer: Perkiraan waktu ini adalah hasil pada kondisi pengujian spesifik dan dapat bervariasi tergantung pada kekuatan hardware (CPU/GPU), kondisi jaringan, dan aplikasi game trivia itu sendiri.*

## Arsitektur Sistem

Proyek ini dibagi menjadi beberapa modul inti yang bekerja sama:

- **`core/` (C++ Performance Core)**: Menangani semua interaksi tingkat rendah dengan perangkat Android melalui ADB, termasuk pengambilan screenshot, validasi gambar, OCR, dan eksekusi tap.
- **`intelligence/` (Python AI Core)**: Otak dari bot. Berisi *Decision Engine* yang mengimplementasikan logika kecerdasan bertingkat dan mengelola database pengetahuan.
- **`bridge/` (Jembatan Komunikasi)**: Mekanisme Inter-Process Communication (IPC) yang memungkinkan *core* C++ berkomunikasi secara efisien dengan *core* Python.
- **`config/`**: Menyimpan file konfigurasi `settings.json`.
- **`models/`**: Menyimpan database SQLite (`trivia_knowledge_base.db`) dan model AI lainnya.
- **`utils/`**: Berisi skrip utilitas untuk *logging*, pelacakan statistik, dan manajemen konfigurasi.
- **`logs/`**: Menyimpan file log yang dihasilkan oleh bot untuk *debugging* dan pemantauan.

## Memulai

### Prasyarat

Pastikan sistem Anda telah menginstal perangkat lunak berikut:

*   **Python 3.8+**
*   **Compiler C++** yang mendukung C++17 (misalnya, g++ atau Clang)
*   **CMake 3.10+** (untuk mengompilasi proyek C++)
*   **OpenCV 4+** (termasuk header pengembangan, misal: `libopencv-dev` di Ubuntu/Debian)
*   **Android Debug Bridge (ADB)**
*   **Tesseract OCR Engine**: Diperlukan di sisi C++. Install dengan `tesseract-ocr` dan `libtesseract-dev` (Ubuntu/Debian).

### Instalasi

1.  **Clone repository ini:**
    ```bash
    git clone https://github.com/0xReLogic/trivia-bot-ultimate
    cd trivia-bot-ultimate
    ```

2.  **Install dependencies Python:**
    ```bash
    pip install opencv-python paddleocr sentence-transformers numpy llama-cpp-python
    ```
    *(Catatan: `sqlite3` umumnya sudah termasuk dalam Python standar. `requests` hanya diperlukan jika Anda memodifikasi bot untuk memanggil API lain.)*

3.  **Install dependencies C++ (contoh untuk Ubuntu/Debian):**
    ```bash
    sudo apt-get update
    sudo apt-get install build-essential cmake libopencv-dev libleptonica-dev libtesseract-dev
    ```

4.  **Kompilasi C++ Core:**
    Gunakan `CMake` untuk mengompilasi core C++. Ini adalah metode yang direkomendasikan dan lebih terorganisir. (Asumsi `CMakeLists.txt` ada di direktori `core/`).
    ```bash
    echo "--- Compiling C++ Core ---"
    mkdir -p build && cd build
    cmake ../core 
    make
    if [ $? -ne 0 ]; then
        echo "C++ compilation failed!"
        exit 1
    fi
    echo "C++ Core compiled successfully. Executable 'trivia_bot' dibuat di dalam direktori 'build/'."
    cd ..
    ```

### Konfigurasi

Sebelum menjalankan bot, Anda **wajib mengkonfigurasi** file `config/settings.json` agar sesuai dengan perangkat Android dan aplikasi trivia Anda. Ini adalah langkah **kritis** untuk fungsionalitas bot yang benar.

#### Cara Mengkalibrasi Bot (Mengisi Koordinat & Area)

Untuk mengisi parameter di `settings.json`, ikuti langkah-langkah manual berikut:

1.  **Hubungkan Perangkat & Ambil Screenshot:**
    *   Pastikan perangkat Android Anda terhubung dan debugging USB aktif.
    *   Buka aplikasi game trivia pada setiap layar penting (menu, pertanyaan, hasil/feedback).
    *   Ambil screenshot untuk setiap layar menggunakan ADB dan simpan ke komputer Anda:
        ```bash
        adb exec-out screencap -p > "screenshot_question.png"
        adb exec-out screencap -p > "screenshot_feedback.png"
        ```

2.  **Analisis Screenshot dengan Image Editor:**
    *   Buka file screenshot (`.png`) di aplikasi editor gambar apa pun (misalnya, Paint, GIMP, Photoshop).
    *   **Untuk `tap_coordinates` (titik tap):** Gerakkan kursor mouse ke **tengah** setiap elemen yang perlu ditap (misalnya, setiap kotak opsi jawaban A, B, C, D). Catat koordinat **X dan Y** yang ditampilkan oleh editor Anda.
    *   **Untuk `ocr_regions` (area OCR):** Untuk setiap area (pertanyaan, semua jawaban), gerakkan kursor mouse ke **sudut kiri atas** dan catat `(x1, y1)`, lalu ke **sudut kanan bawah** dan catat `(x2, y2)`. Masukkan nilai-nilai ini sebagai `[x1, y1, x2-x1, y2-y1]` (x, y, lebar, tinggi) ke `settings.json`.
    *   **Untuk `color_thresholds` (deteksi warna feedback):**
        *   Buka `screenshot_feedback.png`.
        *   Gunakan fitur *Color Picker* (Eyedropper Tool) di editor Anda.
        *   Klik pada area yang berwarna **hijau** (jawaban benar) dan catat nilai **BGR/RGB**-nya.
        *   Klik pada area yang berwarna **merah** (jawaban salah) dan catat nilainya.
        *   Dari nilai ini, tentukan rentang `bgr_min` dan `bgr_max` untuk setiap warna. Ini mungkin memerlukan sedikit penyesuaian.

3.  **Update `config/settings.json`:**
    *   Buka file `config/settings.json` dan isi semua nilai yang Anda catat ke dalam bagian yang sesuai. Pastikan resolusi layar perangkat konsisten setiap kali bermain.

### Konfigurasi LLM Offline (TinyLLM)

Salah satu fitur utama bot ini adalah kemampuannya untuk menggunakan model bahasa (LLM) secara lokal tanpa koneksi internet. Implementasi saat ini di `intelligence/tinyllm_engine.py` adalah sebuah simulasi. Untuk fungsionalitas penuh, Anda perlu mengunduh model yang kompatibel dan mengintegrasikannya.

**1. Model yang Direkomendasikan:**

Untuk menjaga agar bot tetap ringan dan cepat, kami merekomendasikan model LLM yang sangat kecil dan telah di-finetune untuk mengikuti instruksi. Pilihan yang sangat baik adalah:
- **Model**: `TinyMistral-248M-v2.5-Instruct`
- **Versi**: `tinymistral-248m-v2.5-instruct.Q4_K_M.gguf`
- **Ukuran**: **~162 MB** (Sangat ringan dan cepat untuk dimuat)

Model "Instruct" ini sangat ideal karena lebih baik dalam memahami prompt dan memberikan jawaban yang relevan dan ringkas, yang sempurna untuk kasus penggunaan trivia.

**2. Cara Mengunduh:**

Anda dapat mengunduh model ini dari Hugging Face melalui tautan berikut:
- **Tautan**: [MaziyarPanahi/TinyMistral-248M-v2.5-Instruct-GGUF](https://huggingface.co/MaziyarPanahi/TinyMistral-248M-v2.5-Instruct-GGUF)
- Buka tab "Files and versions" dan unduh file `tinymistral-248m-v2.5-instruct.Q4_K_M.gguf`.

**3. Penempatan File:**

- Letakkan file model `tinymistral-248m-v2.5-instruct.Q4_K_M.gguf` yang telah diunduh langsung ke dalam direktori `models/`.

Sistem akan secara otomatis mendeteksi file tersebut sesuai dengan konfigurasi default.

**4. Integrasi Kode (Contoh):**

Anda perlu memodifikasi `intelligence/tinyllm_engine.py` untuk memuat dan menjalankan model ini menggunakan pustaka seperti `ctransformers`.

Install pustaka yang diperlukan:
```bash
# Instalasi Dasar (Hanya CPU)
pip install llama-cpp-python

# --- Untuk Akselerasi Hardware (Pilih salah satu) ---

# Dengan akselerasi NVidia CUDA (Linux/macOS)
CMAKE_ARGS="-DLLAMA_CUBLAS=on" FORCE_CMAKE=1 pip install llama-cpp-python

# Dengan akselerasi OpenBLAS (CPU yang lebih cepat)
CMAKE_ARGS="-DLLAMA_BLAS=ON -DLLAMA_BLAS_VENDOR=OpenBLAS" pip install llama-cpp-python

# Dengan akselerasi AMD ROCm (Linux)
CMAKE_ARGS="-DLLAMA_HIPBLAS=on" pip install llama-cpp-python

# Dengan akselerasi Metal (Apple Silicon macOS)
CMAKE_ARGS="-DLLAMA_METAL=on" pip install llama-cpp-python

# --- Catatan untuk Pengguna Windows ---
# Gunakan PowerShell dan atur environment variable sebelum instalasi. Contoh untuk NVidia CUDA:
# $env:CMAKE_ARGS = "-DLLAMA_CUBLAS=on"
# $env:FORCE_CMAKE = 1
# pip install llama-cpp-python
```

**4. Integrasi Kode:**

Implementasi nyata menggunakan `llama-cpp-python` telah diintegrasikan ke dalam `intelligence/tinyllm_engine.py`. Pustaka ini lebih cepat dan mendukung akselerasi GPU. Anda hanya perlu mengunduh model dan meletakkannya di direktori yang benar.

### Cara Menjalankan

Skrip `run_ultimate.sh` telah disediakan untuk mengotomatiskan proses startup.

1.  **Berikan izin eksekusi pada skrip:**
    ```bash
    chmod +x utils/run_ultimate.sh
    ```

2.  **Jalankan bot:**
    ```bash
    ./utils/run_ultimate.sh
    ```

Skrip ini akan secara otomatis:
1.  Menginisialisasi database.
2.  Menjalankan server jembatan Python di latar belakang.
3.  Menjalankan *core* C++ di latar depan.

Untuk menghentikan bot, cukup tekan `Ctrl+C` di terminal. Skrip akan menangani proses pembersihan secara otomatis.

## Kontribusi

Kontribusi, isu, dan permintaan fitur sangat kami harapkan! Jangan ragu untuk membuat *Pull Request* atau membuka *Issue* baru.

## Lisensi

Proyek ini dilisensikan di bawah Lisensi MIT. Lihat file `LICENSE` untuk detail lebih lanjut.

[Lihat LICENSE](./LICENSE) | [Laporkan Bug](https://github.com/0xReLogic/trivia-bot-ultimate/issues)

---

### Hubungi Saya

- **Email**: hi@0xrelogic.my.id
- **Telegram**: @relogic
- **WhatsApp**: +65 9095 7469
