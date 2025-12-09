import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json

def create_tkinter_ui():
    # Main window setup
    root = tk.Tk()
    root.title("Klasifikasi Kesehatan Finansial")
    root.geometry("900x700")
    root.configure(bg='#f0f0f0')
    
    # Style configuration
    style = ttk.Style()
    style.theme_use('clam')
    style.configure('Title.TLabel', font=('Arial', 16, 'bold'), background='#f0f0f0', foreground='#2c3e50')
    style.configure('Header.TLabel', font=('Arial', 11, 'bold'), background='#f0f0f0', foreground='#34495e')
    style.configure('TLabel', font=('Arial', 10), background='#f0f0f0')
    style.configure('TEntry', font=('Arial', 10))
    style.configure('TButton', font=('Arial', 10, 'bold'), padding=10)
    style.configure('TCombobox', font=('Arial', 10))

    # Input fields dictionary to hold Entry widgets
    input_entries = {}
    
    # Model selection variable
    selected_model = tk.StringVar(value='boosting')
    
    # Define the ordered list of input labels (16 features)
    input_labels = [
        'Gaji', 'Tabungan Lama', 'Investasi', 'Pemasukan Lainnya', 'Tipe',
        'Bahan Pokok', 'Protein & Gizi Tambahan', 'Tempat Tinggal', 'Sandang',
        'Konsumsi Praktis', 'Barang & Jasa Sekunder', 'Pengeluaran Tidak Esensial',
        'Pajak', 'Asuransi', 'Sosial & Budaya', 'Tabungan / Investasi'
    ]
    
    default_values = {
        'Gaji': 5000000, 'Tabungan Lama': 1000000, 'Investasi': 500000, 
        'Pemasukan Lainnya': 500000, 'Tipe': 'normal',
        'Bahan Pokok': 1000000, 'Protein & Gizi Tambahan': 800000, 
        'Tempat Tinggal': 1500000, 'Sandang': 300000,
        'Konsumsi Praktis': 500000, 'Barang & Jasa Sekunder': 400000, 
        'Pengeluaran Tidak Esensial': 200000,
        'Pajak': 250000, 'Asuransi': 200000, 'Sosial & Budaya': 150000, 
        'Tabungan / Investasi': 1000000
    }

    # Title
    title_label = ttk.Label(root, text="📊 Sistem Klasifikasi Kesehatan Finansial", style='Title.TLabel')
    title_label.grid(row=0, column=0, columnspan=4, pady=15, padx=10)
    
    # Model Selection Frame
    model_frame = tk.LabelFrame(root, text="🤖 Pilih Model Klasifikasi", bg='#f0f0f0', 
                                font=('Arial', 11, 'bold'), fg='#2c3e50', padx=15, pady=10)
    model_frame.grid(row=1, column=0, columnspan=4, padx=10, pady=(0,10), sticky='ew')
    
    # Radio buttons for model selection
    models = [
        ('Boosting (XGBoost/AdaBoost)', 'boosting'),
        ('Bagging (Random Forest)', 'bagging'),
        ('Deep Learning (Neural Network)', 'deep_learning')
    ]
    
    for i, (text, value) in enumerate(models):
        rb = tk.Radiobutton(model_frame, text=text, variable=selected_model, value=value,
                           bg='#f0f0f0', font=('Arial', 10), fg='#34495e',
                           selectcolor='#3498db', activebackground='#f0f0f0')
        rb.pack(side='left', padx=20)
    
    # Main frame with canvas for scrolling
    main_frame = tk.Frame(root, bg='#f0f0f0')
    main_frame.grid(row=2, column=0, columnspan=4, sticky='nsew', padx=10)
    
    # Configure grid weights
    root.grid_rowconfigure(2, weight=1)
    root.grid_columnconfigure(0, weight=1)
    
    # Create canvas and scrollbar
    canvas = tk.Canvas(main_frame, bg='#f0f0f0', highlightthickness=0)
    scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg='#f0f0f0')
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    # Section 1: Pemasukan
    ttk.Label(scrollable_frame, text="💰 PEMASUKAN", style='Header.TLabel').grid(row=0, column=0, columnspan=4, pady=(10,5), sticky='w')
    pemasukan_labels = ['Gaji', 'Tabungan Lama', 'Investasi', 'Pemasukan Lainnya', 'Tipe']
    
    for i, label_text in enumerate(pemasukan_labels):
        row = i + 1
        ttk.Label(scrollable_frame, text=f"{label_text}:").grid(row=row, column=0, padx=10, pady=3, sticky='w')
        
        if label_text == 'Tipe':
            combo = ttk.Combobox(scrollable_frame, values=['normal', 'hemat', 'boros'], state='readonly', width=25)
            combo.set(default_values[label_text])
            combo.grid(row=row, column=1, padx=10, pady=3, sticky='ew')
            input_entries[label_text] = combo
        else:
            entry = ttk.Entry(scrollable_frame, width=25)
            entry.insert(0, str(default_values[label_text]))
            entry.grid(row=row, column=1, padx=10, pady=3, sticky='ew')
            input_entries[label_text] = entry
    
    # Section 2: Pengeluaran Esensial
    ttk.Label(scrollable_frame, text="🏠 PENGELUARAN ESENSIAL", style='Header.TLabel').grid(row=6, column=0, columnspan=4, pady=(15,5), sticky='w')
    esensial_labels = ['Bahan Pokok', 'Protein & Gizi Tambahan', 'Tempat Tinggal', 'Sandang']
    
    for i, label_text in enumerate(esensial_labels):
        row = i + 7
        ttk.Label(scrollable_frame, text=f"{label_text}:").grid(row=row, column=0, padx=10, pady=3, sticky='w')
        entry = ttk.Entry(scrollable_frame, width=25)
        entry.insert(0, str(default_values[label_text]))
        entry.grid(row=row, column=1, padx=10, pady=3, sticky='ew')
        input_entries[label_text] = entry
    
    # Section 3: Pengeluaran Non-Esensial
    ttk.Label(scrollable_frame, text="🛍️ PENGELUARAN NON-ESENSIAL", style='Header.TLabel').grid(row=11, column=0, columnspan=4, pady=(15,5), sticky='w')
    non_esensial_labels = ['Konsumsi Praktis', 'Barang & Jasa Sekunder', 'Pengeluaran Tidak Esensial']
    
    for i, label_text in enumerate(non_esensial_labels):
        row = i + 12
        ttk.Label(scrollable_frame, text=f"{label_text}:").grid(row=row, column=0, padx=10, pady=3, sticky='w')
        entry = ttk.Entry(scrollable_frame, width=25)
        entry.insert(0, str(default_values[label_text]))
        entry.grid(row=row, column=1, padx=10, pady=3, sticky='ew')
        input_entries[label_text] = entry
    
    # Section 4: Kewajiban & Tabungan
    ttk.Label(scrollable_frame, text="📋 KEWAJIBAN & TABUNGAN", style='Header.TLabel').grid(row=15, column=0, columnspan=4, pady=(15,5), sticky='w')
    kewajiban_labels = ['Pajak', 'Asuransi', 'Sosial & Budaya', 'Tabungan / Investasi']
    
    for i, label_text in enumerate(kewajiban_labels):
        row = i + 16
        ttk.Label(scrollable_frame, text=f"{label_text}:").grid(row=row, column=0, padx=10, pady=3, sticky='w')
        entry = ttk.Entry(scrollable_frame, width=25)
        entry.insert(0, str(default_values[label_text]))
        entry.grid(row=row, column=1, padx=10, pady=3, sticky='ew')
        input_entries[label_text] = entry
    
    # Pack canvas and scrollbar
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Output area for API response
    output_frame = tk.Frame(root, bg='#f0f0f0')
    output_frame.grid(row=3, column=0, columnspan=4, padx=10, pady=10, sticky='ew')
    
    response_label = ttk.Label(output_frame, text="📊 HASIL KLASIFIKASI:", style='Header.TLabel')
    response_label.pack(anchor='w', pady=(5,5))

    response_text_widget = tk.Text(output_frame, height=8, width=80, wrap='word', font=('Courier', 10), 
                                    bg='#ffffff', relief='solid', borderwidth=1)
    response_text_widget.pack(fill='both', expand=True, pady=5)
    response_text_widget.config(state=tk.DISABLED)

    # Function to send data to API
    def send_data():
        x_new_list = []
        # Collect input values in the specified order
        for label_text in input_labels:
            entry_widget = input_entries[label_text]
            try:
                if label_text == 'Tipe':
                    x_new_list.append(entry_widget.get())
                else:
                    x_new_list.append(float(entry_widget.get()))
            except ValueError:
                messagebox.showerror("Input Error", f"Input tidak valid untuk {label_text}.\nMohon masukkan angka yang benar.")
                return

        # Construct the JSON payload
        payload = {
            "data": [x_new_list],
            "model": selected_model.get()
        }
        input_json = json.dumps(payload)
        
        api_url = "http://localhost:8080/finance_classification"
        headers = {'Content-Type':'application/json'}

        response_text_widget.config(state=tk.NORMAL)
        response_text_widget.delete(1.0, tk.END)
        response_text_widget.insert(tk.END, "⏳ Memproses data...\n\n")
        response_text_widget.config(state=tk.DISABLED)
        root.update()

        try:
            predictions = requests.post(api_url, data=input_json, headers=headers)
            
            if predictions.ok:
                hasil = predictions.json()
                
                # Parse the JSON response
                data = hasil
                nested_data = data.get('0', {})

                # Extract cluster and label values
                cluster_value = nested_data.get('cluster')
                cluster_label = nested_data.get('cluster_label')
                model_used = nested_data.get('model_used', selected_model.get().upper())
                
                # Color coding based on cluster
                if cluster_value == 0:
                    emoji = "⚠️"
                    color_desc = "MERAH"
                elif cluster_value == 1:
                    emoji = "⚡"
                    color_desc = "KUNING"
                else:
                    emoji = "✅"
                    color_desc = "HIJAU"
                
                display_output = f"{emoji} HASIL KLASIFIKASI {emoji}\n"
                display_output += "=" * 60 + "\n\n"
                display_output += f"Model yang Digunakan: {model_used}\n"
                display_output += f"Status Finansial    : {cluster_label}\n"
                display_output += f"Cluster             : {cluster_value} ({color_desc})\n"
                display_output += f"Status API          : Sukses (HTTP {predictions.status_code})\n\n"
                display_output += "=" * 60 + "\n\n"
                
                # Add interpretation
                if cluster_value == 0:
                    display_output += "💡 INTERPRETASI:\n"
                    display_output += "   Kondisi keuangan Anda memerlukan perhatian khusus.\n"
                    display_output += "   Disarankan untuk mengurangi pengeluaran tidak esensial\n"
                    display_output += "   dan meningkatkan tabungan.\n"
                elif cluster_value == 1:
                    display_output += "💡 INTERPRETASI:\n"
                    display_output += "   Kondisi keuangan Anda cukup stabil.\n"
                    display_output += "   Pertahankan pola keuangan saat ini dan tingkatkan\n"
                    display_output += "   investasi untuk mencapai kondisi lebih baik.\n"
                else:
                    display_output += "💡 INTERPRETASI:\n"
                    display_output += "   Kondisi keuangan Anda sangat baik!\n"
                    display_output += "   Terus pertahankan manajemen keuangan yang sehat\n"
                    display_output += "   dan optimalkan investasi Anda.\n"
                
            else:
                display_output = f"❌ GAGAL\n\nStatus HTTP: {predictions.status_code}\nError: {predictions.text}"

        except requests.exceptions.ConnectionError as e:
            display_output = f"❌ CONNECTION ERROR\n\n"
            display_output += f"Tidak dapat terhubung ke server API.\n"
            display_output += f"Pastikan API server berjalan di {api_url}\n\n"
            display_output += f"Detail: {str(e)[:200]}"
        except requests.exceptions.RequestException as e:
            display_output = f"❌ REQUEST ERROR\n\n"
            display_output += f"Terjadi kesalahan saat berkomunikasi dengan API.\n\n"
            display_output += f"Detail: {str(e)[:200]}"
        except Exception as e:
            display_output = f"❌ UNEXPECTED ERROR\n\n{str(e)[:300]}"

        response_text_widget.config(state=tk.NORMAL)
        response_text_widget.delete(1.0, tk.END)
        response_text_widget.insert(tk.END, display_output)
        response_text_widget.config(state=tk.DISABLED)

    # Button frame
    button_frame = tk.Frame(root, bg='#f0f0f0')
    button_frame.grid(row=4, column=0, columnspan=4, pady=10)
    
    # Submit button with custom styling
    submit_button = tk.Button(button_frame, text="🔍 ANALISIS KESEHATAN FINANSIAL", command=send_data,
                             bg='#3498db', fg='white', font=('Arial', 11, 'bold'),
                             padx=30, pady=12, relief='raised', borderwidth=2,
                             cursor='hand2')
    submit_button.pack(side='left', padx=5)
    
    # Clear button
    def clear_fields():
        for label_text in input_labels:
            entry_widget = input_entries[label_text]
            if label_text == 'Tipe':
                entry_widget.set(default_values[label_text])
            else:
                entry_widget.delete(0, tk.END)
                entry_widget.insert(0, str(default_values[label_text]))
        response_text_widget.config(state=tk.NORMAL)
        response_text_widget.delete(1.0, tk.END)
        response_text_widget.config(state=tk.DISABLED)
    
    clear_button = tk.Button(button_frame, text="🔄 RESET", command=clear_fields,
                            bg='#95a5a6', fg='white', font=('Arial', 11, 'bold'),
                            padx=30, pady=12, relief='raised', borderwidth=2,
                            cursor='hand2')
    clear_button.pack(side='left', padx=5)
    
    # Configure column weights for responsiveness
    scrollable_frame.grid_columnconfigure(1, weight=1)

    # Footer info
    footer = ttk.Label(root, text="© 2025 - Sistem Klasifikasi Kesehatan Finansial | Pastikan API Server berjalan di localhost:8080", 
                      font=('Arial', 8), foreground='#7f8c8d')
    footer.grid(row=5, column=0, columnspan=4, pady=5)
    
    # Start the Tkinter event loop
    root.mainloop()

# Call the function to create and run the UI
if __name__ == "__main__":
    print("🚀 Memulai aplikasi Klasifikasi Kesehatan Finansial...")
    print("📌 Pastikan API server sudah berjalan di http://localhost:8080")
    create_tkinter_ui()
