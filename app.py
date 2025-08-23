import streamlit as st
import pandas as pd
from fpdf import FPDF
from weasyprint import HTML
import tempfile
import os

# =========================
# CLASS XUẤT PDF (FPDF)
# =========================
class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_page()
        # Dùng font hệ thống có sẵn (không cần .ttf)
        self.set_font("Helvetica", size=12)

    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.cell(0, 10, "Báo cáo kết quả học tập", ln=True, align="C")
        self.ln(10)

    def chapter_title(self, title):
        self.set_font("Helvetica", "B", 12)
        self.cell(0, 10, title, ln=True, align="L")
        self.ln(5)

    def chapter_table(self, df):
        self.set_font("Helvetica", size=10)
        col_width = self.epw / len(df.columns)
        # Header
        for col in df.columns:
            self.cell(col_width, 10, str(col), border=1, align="C")
        self.ln()
        # Rows
        for _, row in df.iterrows():
            for item in row:
                self.cell(col_width, 10, str(item), border=1, align="C")
            self.ln()

# =========================
# XUẤT PDF (bảng cơ bản)
# =========================
def generate_pdf_report(student_info_dict, df, sems, summary_dict):
    pdf = PDF()
    pdf.chapter_title("Thông tin sinh viên")
    for k, v in student_info_dict.items():
        pdf.cell(0, 10, f"{k}: {v}", ln=True)
    pdf.ln(5)

    pdf.chapter_title("Bảng điểm chi tiết")
    pdf.chapter_table(df)

    pdf.chapter_title("Tóm tắt")
    for k, v in summary_dict.items():
        pdf.cell(0, 10, f"{k}: {v}", ln=True)

    return pdf.output(dest="S").encode("latin-1")

# =========================
# XUẤT HTML → PDF (giữ style y hệt Streamlit)
# =========================
def generate_html_pdf(df):
    # Convert DataFrame thành HTML
    html_content = f"""
    <html>
    <head>
      <meta charset="utf-8">
      <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: center; }}
        th {{ background-color: #4CAF50; color: white; }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
      </style>
    </head>
    <body>
      <h2>Bảng điểm sinh viên</h2>
      {df.to_html(index=False, escape=False)}
    </body>
    </html>
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
        HTML(string=html_content).write_pdf(tmp_pdf.name)
        tmp_pdf.seek(0)
        pdf_bytes = tmp_pdf.read()
    os.unlink(tmp_pdf.name)
    return pdf_bytes

# =========================
# STREAMLIT APP
# =========================
def main():
    st.title("Ứng dụng quản lý điểm sinh viên")

    # Demo dữ liệu
    student_info = {"Mã SV": "123456", "Họ tên": "Nguyễn Văn A", "Ngành": "CNTT"}
    df = pd.DataFrame({
        "Môn học": ["Toán", "Lý", "Hóa", "Văn"],
        "Điểm": [8.5, 7.0, 9.0, 6.5]
    })
    summary_dict = {"GPA": 7.75, "Xếp loại": "Khá"}

    st.subheader("Thông tin sinh viên")
    st.json(student_info)

    st.subheader("Bảng điểm")
    st.dataframe(df, use_container_width=True)

    st.subheader("Tóm tắt")
    st.json(summary_dict)

    # Nút export PDF (FPDF)
    if st.button("📄 Xuất PDF (bảng cơ bản)"):
        pdf_data = generate_pdf_report(student_info, df, None, summary_dict)
        st.download_button("Tải PDF", data=pdf_data, file_name="report.pdf", mime="application/pdf")

    # Nút export PDF (HTML → PDF, giữ style)
    if st.button("📄 Xuất PDF (HTML, giữ nguyên style)"):
        pdf_data = generate_html_pdf(df)
        st.download_button("Tải PDF đẹp", data=pdf_data, file_name="report_styled.pdf", mime="application/pdf")

if __name__ == "__main__":
    main()
