import tkinter as tk
from tkinter import ttk, messagebox
from docx import Document
from docx.shared import Cm, Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from datetime import date
import os

# --- إعدادات الواجهة (Lacoste Style) ---
class AskaouenApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Commune Askaouen - Gestion des Marchés")
        self.root.geometry("800x650")
        self.root.configure(bg="#f0f0f0")

        # الألوان
        self.green_lacoste = "#004526" # الأخضر الملكي
        self.white = "#ffffff"

        # --- العنوان العلوي ---
        header = tk.Frame(root, bg=self.green_lacoste, height=80)
        header.pack(fill="x")
        tk.Label(header, text="ASKAOUN PRO - SYSTÈME PV", font=("Helvetica", 18, "bold"), fg=self.white, bg=self.green_lacoste).pack(pady=20)

        # --- منطقة المدخلات ---
        main_frame = tk.Frame(root, bg="#f0f0f0")
        main_frame.pack(pady=20, padx=20, fill="both", expand=True)

        # رقم السند
        tk.Label(main_frame, text="N° Bon de Commande:", bg="#f0f0f0", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w", pady=5)
        self.entry_bc = tk.Entry(main_frame, width=40)
        self.entry_bc.insert(0, "01/ASK/2026")
        self.entry_bc.grid(row=0, column=1, pady=5, padx=10)

        # رقم المحضر
        tk.Label(main_frame, text="Sélectionner le PV:", bg="#f0f0f0", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky="w", pady=5)
        self.pv_var = tk.StringVar(value="1")
        self.pv_combo = ttk.Combobox(main_frame, textvariable=self.pv_var, values=["1", "2", "3", "4", "5", "6"], state="readonly")
        self.pv_combo.grid(row=1, column=1, pady=5, padx=10, sticky="w")

        # خيار الحالة للمحضر 6
        self.status_var = tk.StringVar(value="Attribution")
        self.status_frame = tk.LabelFrame(main_frame, text="Résultat (Pour PV 6)", bg="#f0f0f0")
        self.status_frame.grid(row=2, column=0, columnspan=2, pady=10, sticky="ew")
        tk.Radiobutton(self.status_frame, text="Attribution (إسناد)", variable=self.status_var, value="Attribution", bg="#f0f0f0").pack(side="left", padx=20)
        tk.Radiobutton(self.status_frame, text="B.C Infructueux (غير مثمر)", variable=self.status_var, value="Infructueux", bg="#f0f0f0").pack(side="left", padx=20)

        # زر الإنشاء
        self.btn_gen = tk.Button(root, text="🚀 إنشاء المحضر (DOCX)", command=self.generate_pv, 
                                 bg=self.green_lacoste, fg=self.white, font=("Arial", 12, "bold"), 
                                 padx=30, pady=10, cursor="hand2")
        self.btn_gen.pack(pady=20)

    def generate_pv(self):
        try:
            doc = Document()
            pv_num = self.pv_var.get()
            bc_num = self.entry_bc.get()
            
            # --- الترويسة ---
            section = doc.sections[0]
            header_table = doc.add_table(1, 2, Inches(6.5))
            header_table.rows[0].cells[0].text = "ROYAUME DU MAROC\nMINISTERE DE L'INTERIEUR\nCOMMUNE D'ASKAOUN"
            header_table.rows[0].cells[1].text = "المملكة المغربية\nوزارة الداخلية\nجماعة أسكاون"
            header_table.rows[0].cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT

            # --- العنوان ---
            p = doc.add_paragraph("\n")
            p = doc.add_heading(f"{pv_num}éme Procès verbal", 1)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
            # منطق الأمانة النصية للمحضر 6
            if pv_num == "6" and self.status_var.get() == "Infructueux":
                doc.add_paragraph(f"\nObjet : Bon de commande n° {bc_num}")
                doc.add_paragraph("\nPAR CONSEQUENT, LA COMMISSION DECLARE QUE CE BON DE COMMANDE EST :").alignment = WD_ALIGN_PARAGRAPH.CENTER
                inf = doc.add_paragraph("INFRUCTUEUX")
                inf.alignment = WD_ALIGN_PARAGRAPH.CENTER
                inf.bold = True
            else:
                doc.add_paragraph(f"\nProcédure de consultation pour le BC n° {bc_num}")
                doc.add_paragraph("La commission a décidé l'attribution du marché...")

            # حفظ الملف في سطح المكتب
            desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
            save_path = os.path.join(desktop, f"PV_{pv_num}_Askaouen.docx")
            doc.save(save_path)
            
            messagebox.showinfo("نجاح", f"تم إنشاء المحضر وحفظه في سطح المكتب:\n{save_path}")
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء الإنشاء: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AskaouenApp(root)
    root.mainloop()
