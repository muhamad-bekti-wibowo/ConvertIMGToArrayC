import re
import struct
import numpy as np
from PIL import Image
import tkinter as tk
from tkinter import filedialog, ttk
import os

# Fungsi konversi dari RGB565 ke RGB888
def rgb565_to_rgb888(value):
    r = ((value >> 11) & 0x1F) * 255 // 31
    g = ((value >> 5) & 0x3F) * 255 // 63
    b = (value & 0x1F) * 255 // 31
    return (r, g, b)

# Fungsi konversi dari RGB888 ke RGB565 dengan berbagai format
def rgb888_to_rgb565(r, g, b):
    rgb565 = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
    return ((rgb565 & 0xFF) << 8) | (rgb565 >> 8)  # Little Endian

def rgb888_to_rgb565_big(r, g, b):
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)  # Big Endian

def rgb888_to_rgb565_big_swap(r, g, b):
    rgb565 = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
    return ((rgb565 >> 11) | (rgb565 & 0x07E0) | ((rgb565 & 0x001F) << 11))

def rgb888_to_rgb565_little_swap(r, g, b):
    rgb565 = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
    rgb565 = ((rgb565 >> 11) | (rgb565 & 0x07E0) | ((rgb565 & 0x001F) << 11))
    return ((rgb565 & 0xFF) << 8) | (rgb565 >> 8)  # Swap bytes for Little Endian

# Fungsi untuk menyesuaikan warna 
def adjust_color(r, g, b):
    # Uncomment atau modifikasi sesuai kebutuhan
    # if r > 50 and g > 50 and b < 200:
    #     g = int(g * 0.7)
    #     r = min(r + 20, 255)
    return r, g, b

# Fungsi untuk membaca file header .h dan mengembalikannya menjadi gambar
def convert_h_to_image(header_file, output_image):
    with open(header_file, "r") as file:
        data = file.read()

    # Cari array dalam file header
    match = re.search(r'\{([^}]*)\}', data, re.DOTALL)
    if not match:
        raise ValueError("Array tidak ditemukan dalam file header")

    # Ambil nilai array, pisahkan dengan koma
    array_values = match.group(1).replace("\n", "").split(',')

    # Konversi ke integer (RGB565)
    pixels = [int(value.strip(), 16) for value in array_values if value.strip()]

    # Baca ukuran dari file header
    match_width = re.search(r"#define IMAGE_WIDTH (\d+)", data)
    match_height = re.search(r"#define IMAGE_HEIGHT (\d+)", data)
    if not match_width or not match_height:
        raise ValueError("Dimensi gambar tidak ditemukan dalam file header")

    width = int(match_width.group(1))
    height = int(match_height.group(1))

    if len(pixels) != width * height:
        raise ValueError("Jumlah data array tidak sesuai dengan dimensi gambar")

    # Konversi ke RGB888
    img_data = [rgb565_to_rgb888(pixel) for pixel in pixels]

    # Buat gambar
    img = Image.new("RGB", (width, height))
    img.putdata(img_data)

    # Simpan gambar
    img.save(output_image)
    return f"Gambar berhasil dikonversi dari {header_file} ke {output_image}"

def sanitize_variable_name(name):
    # Ganti karakter non-alfanumerik dengan garis bawah
    import re
    name = re.sub(r'[^a-zA-Z0-9]', '_', name)
    # Pastikan nama variabel tidak dimulai dengan angka
    if name and name[0].isdigit():
        name = '_' + name
    return name

# Fungsi untuk mengonversi gambar ke RGB565 dan menyimpannya sebagai BMP dan header file .h
def convert_image_to_rgb565(input_path, output_dir, basename, formats):
    img = Image.open(input_path).convert("RGB")
    width, height = img.size
    results = []
    
    for format_type in formats:
        rgb565_data = []
        for y in range(height):
            for x in range(width):
                r, g, b = img.getpixel((x, y))
                r, g, b = adjust_color(r, g, b)
                
                if format_type == "little_endian":
                    rgb565_data.append(rgb888_to_rgb565(r, g, b))
                elif format_type == "big_endian":
                    rgb565_data.append(rgb888_to_rgb565_big(r, g, b))
                elif format_type == "big_endian_swap":
                    rgb565_data.append(rgb888_to_rgb565_big_swap(r, g, b))
                elif format_type == "little_endian_swap":
                    rgb565_data.append(rgb888_to_rgb565_little_swap(r, g, b))

        # Tambahkan suffix format untuk nama file
        suffix = "_" + format_type
        bmp_output = os.path.join(output_dir, f"{basename}{suffix}.bmp")
        header_output = os.path.join(output_dir, f"{basename}{suffix}.h")

        # Simpan dalam format BMP 16-bit
        #with open(bmp_output, "wb") as f:
        #    f.write(b'BM')  # Signature
        #    file_size = 54 + (width * height * 2)
        #    f.write(struct.pack('<I', file_size))  # File size
        #    f.write(b'\x00\x00')  # Reserved
        #    f.write(b'\x00\x00')  # Reserved
        #    f.write(struct.pack('<I', 54))  # Offset ke data gambar

            # DIB Header
        #    f.write(struct.pack('<I', 40))  # Header size
        #    f.write(struct.pack('<I', width))  # Width
        #    f.write(struct.pack('<i', -height))  # Height (top-down)
        #    f.write(struct.pack('<H', 1))  # Planes
        #    f.write(struct.pack('<H', 16))  # Bits per pixel (RGB565)
        #    f.write(struct.pack('<I', 3))  # Compression = BI_BITFIELDS
        #    f.write(struct.pack('<I', width * height * 2))  # Image size
        #    f.write(struct.pack('<I', 2835))  # X pixels per meter
        #    f.write(struct.pack('<I', 2835))  # Y pixels per meter
        #    f.write(struct.pack('<I', 0))  # Total colors
        #    f.write(struct.pack('<I', 0))  # Important colors

            # Mask untuk RGB565
        #    f.write(struct.pack('<I', 0x001F))  # Red mask (sekarang biru)
        #    f.write(struct.pack('<I', 0x07E0))  # Green mask
        #    f.write(struct.pack('<I', 0xF800))  # Blue mask (sekarang merah)
        #    f.write(struct.pack('<I', 0x0000))  # Alpha mask

            # Simpan data gambar
        #    for pixel in rgb565_data:
        #        f.write(struct.pack('<H', pixel))

        # Buat nama variabel dari basename (uppercase untuk define, lowercase untuk variabel)
        upper_name = basename.upper()
        lower_name = basename.lower()
        basename = sanitize_variable_name(basename)
        
        # Simpan ke file header (.h)
        with open(header_output, "w") as f:
            f.write("#include <Arduino.h>\n\n")
            f.write(f"#ifndef {basename}_RGB565_H\n#define {basename}_RGB565_H\n\n")
            f.write(f"#define {basename}_WIDTH {width}\n")
            f.write(f"#define {basename}_HEIGHT {height}\n\n")
            f.write(f"const uint16_t {basename}_data[] = ")
            f.write("{\n")
            for i, pixel in enumerate(rgb565_data):
                if i % 10 == 0:
                    f.write("\n    ")  # Baris baru setiap 10 angka
                f.write(f"0x{pixel:04X}, ")
            f.write("\n};")
            f.write(f"\n\n#endif // {basename}_RGB565_H\n")

        #results.append(f"Format {format_type}: Gambar berhasil dikonversi ke {bmp_output}")
        results.append(f"Format {format_type}: Array C berhasil disimpan di {header_output}")

    return "\n".join(results)

# GUI Application
class RGB565ConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("RGB565 Image Converter")
        self.root.geometry("800x600")
        
        # Variables
        self.input_image_path = tk.StringVar()
        self.input_header_path = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.output_basename = tk.StringVar()
        
        # Format variables
        self.little_endian = tk.BooleanVar(value=True)
        self.big_endian = tk.BooleanVar(value=False)
        self.little_endian_swap = tk.BooleanVar(value=False)
        self.big_endian_swap = tk.BooleanVar(value=False)
        
        # Main Frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Input Frame for Image to Header
        input_frame = ttk.LabelFrame(main_frame, text="Image to Header Conversion", padding="10")
        input_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(input_frame, text="Input Image:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(input_frame, textvariable=self.input_image_path, width=50).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(input_frame, text="Browse", command=self.browse_input_image).grid(row=0, column=2, padx=5, pady=5)
        
        ttk.Label(input_frame, text="Output Directory:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(input_frame, textvariable=self.output_dir, width=50).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(input_frame, text="Browse", command=self.browse_output_dir).grid(row=1, column=2, padx=5, pady=5)
        
        ttk.Label(input_frame, text="Output Basename:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(input_frame, textvariable=self.output_basename, width=50).grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Button(input_frame, text="Convert Image to Header", command=self.convert_image_to_header).grid(row=3, column=1, pady=10)
        
        # Input Frame for Header to Image
        header_frame = ttk.LabelFrame(main_frame, text="Header to Image Conversion", padding="10")
        header_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(header_frame, text="Input Header (.h):").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(header_frame, textvariable=self.input_header_path, width=50).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(header_frame, text="Browse", command=self.browse_input_header).grid(row=0, column=2, padx=5, pady=5)
        
        ttk.Label(header_frame, text="Output Directory:").grid(row=1, column=0, sticky=tk.W, pady=5)
        h2i_output_dir_entry = ttk.Entry(header_frame, textvariable=self.output_dir, width=50)
        h2i_output_dir_entry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(header_frame, text="Browse", command=self.browse_output_dir).grid(row=1, column=2, padx=5, pady=5)
        
        ttk.Button(header_frame, text="Convert Header to Image", command=self.convert_header_to_image).grid(row=2, column=1, pady=10)
        
        # Format Frame with checkboxes - DIUBAH untuk memungkinkan multiple selections
        format_frame = ttk.LabelFrame(main_frame, text="RGB565 Format Settings", padding="10")
        format_frame.pack(fill=tk.X, pady=5)
        
        ttk.Checkbutton(format_frame, text="Little Endian", variable=self.little_endian, 
                        command=lambda: self.toggle_format("little_endian")).grid(row=0, column=0, padx=20, pady=5, sticky=tk.W)
        ttk.Checkbutton(format_frame, text="Big Endian", variable=self.big_endian,
                        command=lambda: self.toggle_format("big_endian")).grid(row=0, column=1, padx=20, pady=5, sticky=tk.W)
        ttk.Checkbutton(format_frame, text="Little Endian Swap", variable=self.little_endian_swap,
                        command=lambda: self.toggle_format("little_endian_swap")).grid(row=1, column=0, padx=20, pady=5, sticky=tk.W)
        ttk.Checkbutton(format_frame, text="Big Endian Swap", variable=self.big_endian_swap,
                        command=lambda: self.toggle_format("big_endian_swap")).grid(row=1, column=1, padx=20, pady=5, sticky=tk.W)
        
        # Log Frame
        log_frame = ttk.LabelFrame(main_frame, text="Log Output", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.log_text = tk.Text(log_frame, wrap=tk.WORD, height=15)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.log_text, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        
    # DIUBAH: toggle_format sekarang memungkinkan multiple selections
    def toggle_format(self, selected_format):
        # Hanya pastikan minimal satu checkbox dipilih
        if not any([self.little_endian.get(), self.big_endian.get(), 
                    self.little_endian_swap.get(), self.big_endian_swap.get()]):
            # Jika semua dimatikan, nyalakan kembali yang baru saja dimatikan
            if selected_format == "little_endian":
                self.little_endian.set(True)
            elif selected_format == "big_endian":
                self.big_endian.set(True)
            elif selected_format == "little_endian_swap":
                self.little_endian_swap.set(True)
            elif selected_format == "big_endian_swap":
                self.big_endian_swap.set(True)
    
    # DIUBAH: get_selected_formats (dengan 's' untuk menunjukkan jamak) sekarang mengembalikan list
    def get_selected_formats(self):
        formats = []
        if self.little_endian.get():
            formats.append("little_endian")
        if self.big_endian.get():
            formats.append("big_endian")
        if self.little_endian_swap.get():
            formats.append("little_endian_swap")
        if self.big_endian_swap.get():
            formats.append("big_endian_swap")
        
        # Jika tidak ada yang dipilih, gunakan little_endian sebagai default
        if not formats:
            formats.append("little_endian")
            self.little_endian.set(True)
            
        return formats
        
    def browse_input_image(self):
        file_path = filedialog.askopenfilename(
            title="Select Input Image",
            filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp"), ("All files", "*.*")]
        )
        if file_path:
            self.input_image_path.set(file_path)
            # Set default output basename
            basename = os.path.splitext(os.path.basename(file_path))[0]
            self.output_basename.set(basename)
            # Set default output directory
            self.output_dir.set(os.path.dirname(file_path))
    
    def browse_input_header(self):
        file_path = filedialog.askopenfilename(
            title="Select Input Header File",
            filetypes=[("Header files", "*.h"), ("All files", "*.*")]
        )
        if file_path:
            self.input_header_path.set(file_path)
            # Set default output basename
            basename = os.path.splitext(os.path.basename(file_path))[0]
            self.output_basename.set(basename)
            # Set default output directory
            self.output_dir.set(os.path.dirname(file_path))
    
    def browse_output_dir(self):
        dir_path = filedialog.askdirectory(title="Select Output Directory")
        if dir_path:
            self.output_dir.set(dir_path)
    
    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
    
    # DIUBAH: convert_image_to_header sekarang mendukung multiple formats
    def convert_image_to_header(self):
        input_path = self.input_image_path.get()
        output_dir = self.output_dir.get() or os.path.dirname(input_path)
        basename = self.output_basename.get() or os.path.splitext(os.path.basename(input_path))[0]
        formats = self.get_selected_formats()
        
        if not input_path:
            self.log("Error: Tidak ada gambar input yang dipilih")
            return
            
        if not os.path.isfile(input_path):
            self.log("Error: File gambar input tidak ditemukan")
            return
            
        try:
            # Convert untuk semua format yang dipilih
            self.log(f"Mulai konversi untuk {len(formats)} format: {', '.join(formats)}")
            result = convert_image_to_rgb565(input_path, output_dir, basename, formats)
            self.log(result)
            
        except Exception as e:
            self.log(f"Error: {str(e)}")
    
    def convert_header_to_image(self):
        input_path = self.input_header_path.get()
        output_dir = self.output_dir.get() or os.path.dirname(input_path)
        basename = self.output_basename.get() or os.path.splitext(os.path.basename(input_path))[0]
        
        if not input_path:
            self.log("Error: Tidak ada file header input yang dipilih")
            return
            
        if not os.path.isfile(input_path):
            self.log("Error: File header input tidak ditemukan")
            return
            
        if not input_path.lower().endswith('.h'):
            self.log("Error: File input harus berupa header (.h)")
            return
            
        try:
            output_image = os.path.join(output_dir, f"{basename}.png")
            result = convert_h_to_image(input_path, output_image)
            self.log(result)
            
        except Exception as e:
            self.log(f"Error: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = RGB565ConverterApp(root)
    root.mainloop()