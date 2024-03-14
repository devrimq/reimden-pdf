import tkinter as tk
from tkinter import filedialog, colorchooser, messagebox
from reportlab.pdfgen import canvas
from PIL import Image, ImageTk
import os
import threading
from tkinter import ttk

class ImageToPDFConvertor:
    def __init__(self, root):
        self.root = root
        self.image_paths = []
        self.output_pdf_name = tk.StringVar()
        self.background_color = "#ffffff"

        self.selected_images_listbox = tk.Listbox(root, selectmode=tk.MULTIPLE)

        self.preview_frame = tk.Frame(root)
        self.preview_frame.pack(pady=(0, 10))

        self.progress_bar = tk.DoubleVar()
        self.progress_bar_widget = ttk.Progressbar(self.root, variable=self.progress_bar, orient='horizontal', length=200, mode='determinate')

        self.initialize_ui()

    def initialize_ui(self):
        title_label = tk.Label(self.root, text="Resimden PDF", font=("Helvetica", 16, "bold"))
        title_label.pack(pady=10)
        
        select_images_button = tk.Button(self.root, text="Resim Seç", command=self.select_images)
        select_images_button.pack(pady=(0, 10))

        self.selected_images_listbox.pack(pady=(0, 10), fill=tk.BOTH, expand=True)

        label = tk.Label(self.root, text="PDF Çıktısına İsim Girin:")
        label.pack()

        pdf_name_entry = tk.Entry(self.root, textvariable=self.output_pdf_name, width=40, justify="center")
        pdf_name_entry.pack()

        convert_button = tk.Button(self.root, text="PDF'e Dönüştür", command=self.convert_images_to_pdf)
        convert_button.pack(pady=(20, 40))

        background_color_button = tk.Button(self.root, text="Arka Plan Rengi Seç", command=self.select_background_color)
        background_color_button.pack(pady=(10, 0))

        self.progress_bar_widget.pack(pady=10)

    def select_background_color(self):
        color = colorchooser.askcolor(title="Arka Plan Rengi Seçin")[1]
        if color:
            self.background_color = color

    def select_images(self):  
        self.image_paths = filedialog.askopenfilenames(title="Resim Seç", filetypes=[("Resim Dosyaları", "*.jpg;*.jpeg;*.png"), ("PDF Dosyaları", "*.pdf")])
        self.update_selected_images_listbox()
        self.update_image_previews()

    def update_selected_images_listbox(self): 
        self.selected_images_listbox.delete(0, tk.END)  

        for image_path in self.image_paths:
            _, image_name = os.path.split(image_path)
            self.selected_images_listbox.insert(tk.END, image_name)

    def update_image_previews(self):
        for widget in self.preview_frame.winfo_children():
            widget.destroy()

        for image_path in self.image_paths:
            image = Image.open(image_path)
            image.thumbnail((100, 100))
            photo = ImageTk.PhotoImage(image)
            label = tk.Label(self.preview_frame, image=photo)
            label.image = photo
            label.pack(side=tk.LEFT, padx=5)

    def convert_images_to_pdf(self):  
        if not self.image_paths:
            return
        
        output_pdf_path = self.output_pdf_name.get() + ".pdf" if self.output_pdf_name.get() else "output.pdf"

        def convert_images():
            total_images = len(self.image_paths)
            self.progress_bar_widget['maximum'] = total_images

            pdf = canvas.Canvas(output_pdf_path, pagesize=(612, 792))

            for index, image_path in enumerate(self.image_paths, start=1):
                if image_path.lower().endswith('.pdf'):
                    messagebox.showinfo("Uyarı", "PDF dosyaları yüklenemez. Lütfen sadece resim dosyaları seçin.")
                    return
                
                img = Image.open(image_path)
                available_width = 540
                available_height = 720
                scale_factor = min(available_width / img.width, available_height / img.height)
                new_width = img.width * scale_factor
                new_height = img.height * scale_factor
                x_centered = (612 - new_width) / 2
                y_centered = (792 - new_height) / 2
                
                if isinstance(self.background_color, tuple):
                    pdf.setFillColor(*self.background_color)
                else:
                    pdf.setFillColor(self.background_color)
                
                pdf.rect(0, 0, 612, 792, fill=True)
                
                pdf.drawInlineImage(img, x_centered, y_centered, width=new_width, height=new_height)
                pdf.showPage()

                self.progress_bar.set(index)
                self.root.update_idletasks()

            pdf.save()
            messagebox.showinfo("Başarılı", "Resimler PDF'e başarıyla dönüştürüldü.")

        threading.Thread(target=convert_images).start()


def main():
    root = tk.Tk()  
    root.title("Image to PDF")
    converter = ImageToPDFConvertor(root)
    root.geometry("400x600")
    root.mainloop()

if __name__ == "__main__":
    main()
