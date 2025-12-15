# Finance Classification Web Application

Sistem Klasifikasi Kesehatan Finansial berbasis Machine Learning dengan antarmuka web modern.

## Fitur

- 🎨 UI Modern dengan Tailwind CSS
- 🤖 3 Model Machine Learning (Boosting, Bagging, Deep Learning)
- 📊 Analisis Real-time
- 📱 Responsive Design
- 📈 Visualisasi Hasil Klasifikasi

## Dataset

Dataset yang digunakan: [Indonesian Personal Finance](https://www.kaggle.com/datasets/harrymardika/indonesian-personal-finance)

## Instalasi

1. Install dependencies:
```bash
pip install flask scikit-learn pandas numpy joblib
```

2. Pastikan model sudah tersedia di folder `model/`:
   - `finance_boosting_model.sav`
   - `finance_bagging_model.sav`
   - `finance_deep_learning_model.sav`
   - `scaler_finance.sav`

## Cara Menjalankan

1. Jalankan Flask server:
```bash
python api_local.py
```

2. Buka browser dan akses:
```
http://localhost:8080
```

## Struktur Folder

```
finance_classification/
├── api_local.py              # Flask API server
├── finance_UI.py             # Tkinter UI (versi desktop)
├── templates/
│   ├── index.html           # Halaman utama web
│   └── about.html           # Halaman informasi dataset
├── model/
│   ├── finance_boosting_model.sav
│   ├── finance_bagging_model.sav
│   ├── finance_deep_learning_model.sav
│   └── scaler_finance.sav
└── dataset/
    ├── data_keuangan_labeled.csv
    └── dataset_keuangan.csv
```

## API Endpoints

### Web Pages
- `GET /` - Halaman utama aplikasi
- `GET /about` - Halaman informasi dataset

### API
- `POST /finance_classification` - Endpoint untuk klasifikasi

**Request Body:**
```json
{
  "data": [[gaji, tabungan_lama, investasi, pemasukan_lainnya, tipe, 
            bahan_pokok, protein_gizi, tempat_tinggal, sandang, 
            konsumsi_praktis, barang_jasa_sekunder, pengeluaran_tidak_esensial,
            pajak, asuransi, sosial_budaya, tabungan_investasi]],
  "model": "boosting"
}
```

**Response:**
```json
{
  "0": {
    "cluster": 2,
    "cluster_label": "Sehat Finansial",
    "model_used": "BOOSTING"
  }
}
```

## Klasifikasi

- **Cluster 0** (🔴 MERAH): Rawan Finansial
- **Cluster 1** (🟡 KUNING): Menengah Stabil
- **Cluster 2** (🟢 HIJAU): Sehat Finansial

## Technology Stack

- **Backend**: Flask, Python
- **Frontend**: HTML, Tailwind CSS, JavaScript
- **ML Libraries**: scikit-learn, pandas, numpy
- **UI Framework**: Tailwind CSS v3

## Credits

Dataset by Harry Mardika - [Kaggle](https://www.kaggle.com/datasets/harrymardika/indonesian-personal-finance)

## License

MIT License
