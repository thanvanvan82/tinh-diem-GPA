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
        # Sử dụng font mặc định của FPDF thay vì font tùy chỉnh
        self.set_font("Arial", size=12)
    
    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "Bao cao ket qua hoc tap", ln=True, align="C")
        self.ln(10)
    
    def chapter_title(self, title):
        self.set_font("Arial", "B", 12)
        # Chuyển đổi tiếng Việt thành không dấu để tránh lỗi encoding
        title_ascii = self.convert_to_ascii(title)
        self.cell(0, 10, title_ascii, ln=True, align="L")
        self.ln(5)
    
    def chapter_table(self, df):
        self.set_font("Arial", size=10)
        col_width = self.epw / len(df.columns)
        
        # Header
        for col in df.columns:
            col_ascii = self.convert_to_ascii(str(col))
            self.cell(col_width, 10, col_ascii, border=1, align="C")
        self.ln()
        
        # Rows
        for _, row in df.iterrows():
            for item in row:
                item_ascii = self.convert_to_ascii(str(item))
                self.cell(col_width, 10, item_ascii, border=1, align="C")
            self.ln()
    
    def convert_to_ascii(self, text):
        """Chuyển đổi tiếng Việt sang không dấu"""
        vietnamese_chars = {
            'à': 'a', 'á': 'a', 'ạ': 'a', 'ả': 'a', 'ã': 'a',
            'ă': 'a', 'ằ': 'a', 'ắ': 'a', 'ặ': 'a', 'ẳ': 'a', 'ẵ': 'a',
            'â': 'a', 'ầ': 'a', 'ấ': 'a', 'ậ': 'a', 'ẩ': 'a', 'ẫ': 'a',
            'è': 'e', 'é': 'e', 'ẹ': 'e', 'ẻ': 'e', 'ẽ': 'e',
            'ê': 'e', 'ề': 'e', 'ế': 'e', 'ệ': 'e', 'ể': 'e', 'ễ': 'e',
            'ì': 'i', 'í': 'i', 'ị': 'i', 'ỉ': 'i', 'ĩ': 'i',
            'ò': 'o', 'ó': 'o', 'ọ': 'o', 'ỏ': 'o', 'õ': 'o',
            'ô': 'o', 'ồ': 'o', 'ố': 'o', 'ộ': 'o', 'ổ': 'o', 'ỗ': 'o',
            'ơ': 'o', 'ờ': 'o', 'ớ': 'o', 'ợ': 'o', 'ở': 'o', 'ỡ': 'o',
            'ù': 'u', 'ú': 'u', 'ụ': 'u', 'ủ': 'u', 'ũ': 'u',
            'ư': 'u', 'ừ': 'u', 'ứ': 'u', 'ự': 'u', 'ử': 'u', 'ữ': 'u',
            'ỳ': 'y', 'ý': 'y', 'ỵ': 'y', 'ỷ': 'y', 'ỹ': 'y',
            'đ': 'd',
            # Uppercase
            'À': 'A', 'Á': 'A', 'Ạ': 'A', 'Ả': 'A', 'Ã': 'A',
            'Ă': 'A', 'Ằ': 'A', 'Ắ': 'A', 'Ặ': 'A', 'Ẳ': 'A', 'Ẵ': 'A',
            'Â': 'A', 'Ầ': 'A', 'Ấ': 'A', 'Ậ': 'A', 'Ẩ': 'A', 'Ẫ': 'A',
            'È': 'E', 'É': 'E', 'Ẹ': 'E', 'Ẻ': 'E', 'Ẽ': 'E',
            'Ê': 'E', 'Ề': 'E', 'Ế': 'E', 'Ệ': 'E', 'Ể': 'E', 'Ễ': 'E',
            'Ì': 'I', 'Í': 'I', 'Ị': 'I', 'Ỉ': 'I', 'Ĩ': 'I',
            'Ò': 'O', 'Ó': 'O', 'Ọ': 'O', 'Ỏ': 'O', 'Õ': 'O',
            'Ô': 'O', 'Ồ': 'O', 'Ố': 'O', 'Ộ': 'O', 'Ổ': 'O', 'Ỗ': 'O',
            'Ơ': 'O', 'Ờ': 'O', 'Ớ': 'O', 'Ợ': 'O', 'Ở': 'O', 'Ỡ': 'O',
            'Ù': 'U', 'Ú': 'U', 'Ụ': 'U', 'Ủ': 'U', 'Ũ': 'U',
            'Ư': 'U', 'Ừ': 'U', 'Ứ': 'U', 'Ự': 'U', 'Ử': 'U', 'Ữ': 'U',
            'Ỳ': 'Y', 'Ý': 'Y', 'Ỵ': 'Y', 'Ỷ': 'Y', 'Ỹ': 'Y',
            'Đ': 'D'
        }
        
        result = ""
        for char in str(text):
            result += vietnamese_chars.get(char, char)
        return result

# =========================
# CLASS PDF VỚI UNICODE HỖ TRỢ
# =========================
class PDFUnicode(FPDF):
    def __init__(self):
        super().__init__()
        self.add_page()
        # Thử sử dụng font hỗ trợ Unicode, nếu không có thì dùng Arial
        try:
            # Tải font DejaVu Sans (thường có sẵn trên nhiều hệ thống)
            self.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)
            self.font_family = 'DejaVu'
        except:
            # Nếu không có DejaVu, dùng Arial
            self.font_family = 'Arial'
        
        self.set_font(self.font_family, size=12)
    
    def header(self):
        self.set_font(self.font_family, "B", 14)
        if self.font_family == 'DejaVu':
            self.cell(0, 10, "Báo cáo kết quả học tập", ln=True, align="C")
        else:
            self.cell(0, 10, "Bao cao ket qua hoc tap", ln=True, align="C")
        self.ln(10)
    
    def chapter_title(self, title):
        self.set_font(self.font_family, "B", 12)
        if self.font_family != 'DejaVu':
            title = self.convert_to_ascii(title)
        self.cell(0, 10, title, ln=True, align="L")
        self.ln(5)
    
    def chapter_table(self, df):
        self.set_font(self.font_family, size=10)
        col_width = self.epw / len(df.columns)
        
        # Header
        for col in df.columns:
            text = str(col)
            if self.font_family != 'DejaVu':
                text = self.convert_to_ascii(text)
            self.cell(col_width, 10, text, border=1, align="C")
        self.ln()
        
        # Rows
        for _, row in df.iterrows():
            for item in row:
                text = str(item)
                if self.font_family != 'DejaVu':
                    text = self.convert_to_ascii(text)
                self.cell(col_width, 10, text, border=1, align="C")
            self.ln()
    
    def convert_to_ascii(self, text):
        """Chuyển đổi tiếng Việt sang không dấu (giống hàm trên)"""
        vietnamese_chars = {
            'à': 'a', 'á': 'a', 'ạ': 'a', 'ả': 'a', 'ã': 'a',
            'ă': 'a', 'ằ': 'a', 'ắ': 'a', 'ặ': 'a', 'ẳ': 'a', 'ẵ': 'a',
            'â': 'a', 'ầ': 'a', 'ấ': 'a', 'ậ': 'a', 'ẩ': 'a', 'ẫ': 'a',
            'è': 'e', 'é': 'e', 'ẹ': 'e', 'ẻ': 'e', 'ẽ': 'e',
            'ê': 'e', 'ề': 'e', 'ế': 'e', 'ệ': 'e', 'ể': 'e', 'ễ': 'e',
            'ì': 'i', 'í': 'i', 'ị': 'i', 'ỉ': 'i', 'ĩ': 'i',
            'ò': 'o', 'ó': 'o', 'ọ': 'o', 'ỏ': 'o', 'õ': 'o',
            'ô': 'o', 'ồ': 'o', 'ố': 'o', 'ộ': 'o', 'ổ': 'o', 'ỗ': 'o',
            'ơ': 'o', 'ờ': 'o', 'ớ': 'o', 'ợ': 'o', 'ở': 'o', 'ỡ': 'o',
            'ù': 'u', 'ú': 'u', 'ụ': 'u', 'ủ': 'u', 'ũ': 'u',
            'ư': 'u', 'ừ': 'u', 'ứ': 'u', 'ự': 'u', 'ử': 'u', 'ữ': 'u',
            'ỳ': 'y', 'ý': 'y', 'ỵ': 'y', 'ỷ': 'y', 'ỹ': 'y',
            'đ': 'd',
            'À': 'A', 'Á': 'A', 'Ạ': 'A', 'Ả': 'A', 'Ã': 'A',
            'Ă': 'A', 'Ằ': 'A', 'Ắ': 'A', 'Ặ': 'A', 'Ẳ': 'A', 'Ẵ': 'A',
            'Â': 'A', 'Ầ': 'A', 'Ấ': 'A', 'Ậ': 'A', 'Ẩ': 'A', 'Ẫ': 'A',
            'È': 'E', 'É': 'E', 'Ẹ': 'E', 'Ẻ': 'E', 'Ẽ': 'E',
            'Ê': 'E', 'Ề': 'E', 'Ế': 'E', 'Ệ': 'E', 'Ể': 'E', 'Ễ': 'E',
            'Ì': 'I', 'Í': 'I', 'Ị': 'I', 'Ỉ': 'I', 'Ĩ': 'I',
            'Ò': 'O', 'Ó': 'O', 'Ọ': 'O', 'Ỏ': 'O', 'Õ': 'O',
            'Ô': 'O', 'Ồ': 'O', 'Ố': 'O', 'Ộ': 'O', 'Ổ': 'O', 'Ỗ': 'O',
            'Ơ': 'O', 'Ờ': 'O', 'Ớ': 'O', 'Ợ': 'O', 'Ở': 'O', 'Ỡ': 'O',
            'Ù': 'U', 'Ú': 'U', 'Ụ': 'U', 'Ủ': 'U', 'Ũ': 'U',
            'Ư': 'U', 'Ừ': 'U', 'Ứ': 'U', 'Ự': 'U', 'Ử': 'U', 'Ữ': 'U',
            'Ỳ': 'Y', 'Ý': 'Y', 'Ỵ': 'Y', 'Ỷ': 'Y', 'Ỹ': 'Y',
            'Đ': 'D'
        }
        
        result = ""
        for char in str(text):
            result += vietnamese_chars.get(char, char)
        return result

# =========================
# XUẤT PDF (bảng cơ bản)
# =========================
def generate_pdf_report(student_info_dict, df, sems, summary_dict):
    try:
        # Thử sử dụng PDF với Unicode
        pdf = PDFUnicode()
    except:
        # Nếu không được, dùng PDF cơ bản
        pdf = PDF()
    
    pdf.chapter_title("Thong tin sinh vien")
    for k, v in student_info_dict.items():
        text = f"{k}: {v}"
        if hasattr(pdf, 'font_family') and pdf.font_family != 'DejaVu':
            text = pdf.convert_to_ascii(text)
        pdf.cell(0, 10, text, ln=True)
    
    pdf.ln(5)
    pdf.chapter_title("Bang diem chi tiet")
    pdf.chapter_table(df)
    
    pdf.chapter_title("Tom tat")
    for k, v in summary_dict.items():
        text = f"{k}: {v}"
        if hasattr(pdf, 'font_family') and pdf.font_family != 'DejaVu':
            text = pdf.convert_to_ascii(text)
        pdf.cell(0, 10, text, ln=True)
    
    return pdf.output(dest="S").encode("latin-1")

# =========================
# XUẤT HTML → PDF (giữ style y hệt Streamlit)
# =========================
def generate_html_pdf(df):
    try:
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
    except Exception as e:
        st.error(f"Lỗi khi tạo PDF từ HTML: {str(e)}")
        return None

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
        try:
            pdf_data = generate_pdf_report(student_info, df, None, summary_dict)
            st.download_button("Tải PDF", data=pdf_data, file_name="report.pdf", mime="application/pdf")
        except Exception as e:
            st.error(f"Lỗi khi tạo PDF: {str(e)}")
    
    # Nút export PDF (HTML → PDF, giữ style)
    if st.button("📄 Xuất PDF (HTML, giữ nguyên style)"):
        try:
            pdf_data = generate_html_pdf(df)
            if pdf_data:
                st.download_button("Tải PDF đẹp", data=pdf_data, file_name="report_styled.pdf", mime="application/pdf")
        except Exception as e:
            st.error(f"Lỗi khi tạo PDF từ HTML: {str(e)}")

if __name__ == "__main__":
    main()