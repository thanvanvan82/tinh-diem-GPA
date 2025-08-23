import streamlit as st
import pandas as pd
from supabase import create_client, Client
from weasyprint import HTML
from io import BytesIO

# ======================
# Kết nối Supabase
# ======================
url = st.secrets["supabase"]["url"]
key = st.secrets["supabase"]["key"]
supabase: Client = create_client(url, key)

# ======================
# Hàm export HTML -> PDF
# ======================
def export_html_pdf(df: pd.DataFrame) -> bytes:
    # CSS giống style bảng của Streamlit
    css = """
    <style>
    body { font-family: Arial, sans-serif; padding: 20px; }
    h2 { text-align: center; }
    table {
        border-collapse: collapse;
        width: 100%;
        margin-top: 20px;
        font-size: 12pt;
    }
    th, td {
        border: 1px solid #ddd;
        padding: 8px;
        text-align: center;
    }
    th {
        background-color: #4CAF50;
        color: white;
    }
    tr:nth-child(even) {
        background-color: #f2f2f2;
    }
    tr:hover {
        background-color: #ddd;
    }
    </style>
    """

    html = f"""
    <html>
    <head>{css}</head>
    <body>
        <h2>📊 Kết quả học tập</h2>
        {df.to_html(index=False, border=0)}
    </body>
    </html>
    """

    pdf_bytes = BytesIO()
    HTML(string=html).write_pdf(pdf_bytes)
    return pdf_bytes.getvalue()

# ======================
# Ứng dụng Streamlit
# ======================
st.title("🎓 Quản lý sinh viên với Supabase")

ma_sv = st.text_input("Nhập mã sinh viên:")

if ma_sv:
    response = supabase.table("StudentDatabase").select("*").eq("ma_sv", ma_sv).execute()
    data = response.data

    if data:
        df_results = pd.DataFrame(data)
        st.subheader("📋 Thông tin sinh viên")
        st.dataframe(df_results, use_container_width=True)

        # Nút tải PDF HTML styled
        pdf_bytes = export_html_pdf(df_results)
        st.download_button(
            "📥 Tải PDF (HTML styled, y hệt bảng)",
            data=pdf_bytes,
            file_name=f"ket_qua_{ma_sv}.pdf",
            mime="application/pdf"
        )
    else:
        st.warning("❌ Không tìm thấy sinh viên.")
