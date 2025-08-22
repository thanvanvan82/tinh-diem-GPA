import streamlit as st
import pandas as pd
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
import numpy as np
from fpdf import FPDF
import base64
import tempfile
import os

st.set_page_config(page_title="Hệ thống Tư vấn Học tập", page_icon="🎓", layout="wide")

# -----------------------------
# DỮ LIỆU CẤU HÌNH & HẰNG SỐ
# -----------------------------
# NÂNG CẤP: Nhúng font chữ Base64 để sửa lỗi FileNotFoundError
ROBOTO_FONT_BASE64 = "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AAgAAAAMACQCkAAIAcAAAAgAAAAkAYwAAAQAAAAIAAAAAAAAAAAAAAAAAAAAAQQAHAUcABgEcAAYBFQACARMAAgEOAAUB8AAGAAAAAAABAAAAAAAAABwACgAHAAgACwAKAAgABQAFAAsABQAGAAkADgAQAAQACwAHAAQACQAACgAMAA4ACwAMAAwADAAOAAAAEgADAAAAAAcABAAMAAAACgAFAAkAAAADAAQABwADAAQACAAAAAYAAAAGAAAAAgAHAAcAAQAJAAIABQAFAAYAAQAAAAAAAgADAAcAAQAJAAUAAAAAAAQAAwAHAAQABwALAA0AAAAMAA8ACwAMAA8ADwAQAAUAAAACAAQAAwAHAAwACgAFAAcAAAACAAQACAAFAAUAAgAAAAkACgAFAAUAAgAHAAcAAAAHAAQADAAJAAkABAALAAcAAAALAAcABQAIAAAAAgABAAAAAgACAAUACAAIAAgAAAALAAcABQAIAAgACQAJAAcACAAHAAYAAQAEAAAAAQAGAAkACgAAAAUAAAAEAAQABQAAAAEABgABAAQAAAACAAQABAAFAAAAAAEABwAGAAUAAQAAAAAAAgAEAAQAAAABAAIABgABAAAAAgAFAAYAAAAEAAgABQAFAAYAAgACAAQAAAAEAAYAAwAEAAIAAgAGAAIAAgABAAEAAwAHAAcABwADAAcABwAHAAQACQAIAAkACAAJAAgADgAJAA4ACQAOAA4AEAAGAAsAAwALAAQABwALAAQACwAFAAUABwAFAAkAAAACAAEAAAAEAAQAAgABAAEAAAACAAcABQAIAAcABAAGAAQABQAFAAYAAwAAAAUAAwAEAAgAAQAIAAEABAAEAAQAAgADAAQAAwAAAAcAAQAFAAUABAABAAcAAQAJAAQABAALAAUAAQAAAAAAAgAGAAUAAwADAAcABQAFAAYAAQAAAAAAAgAGAAUABAAGAAgABQAFAAYAAgACAAQABAAHAAcAAQAAAAAIAAEACAAHAAUAAgADAAIAAQAFAAIAAwAAAAAABwAIAAcAAAADAAUABgAFAAUAAgADAAgAAAACAAEAAgACAAIABQAIAAoACAAIAAUACAAHAAAAAAQAAQADAAQABAAJAA4AAAADAAQACAAAAAIAAAADAAAAAQAAAgADAAgAAgAAAAAABwAIAAcAAAAFAAUABQAFAAUABgAIAAkABAAMAAcABAAMAAgABAAMAAoABAAMAAwABAAMAA4ABAAMAAsACAAFAAsACAAHAAcADAAIAAkACAALAAkADAAJAAkABAALAAkABAALAAkACgALAAkADAALAAkADgALAAkADAAMAAgADAAMAAkADAAMAAoADAAMAAsADAANAAsADQANAAsADQANAAsADQAKAAgADQALAAgADQAMAAgADQANAAsAAwADAAQAAwAFAAMABgADAAcAAwACAAUAAQADAAMAAwAEAAAAAAQAAQAEAAUAAQAEAAAAAAcAAAADAAAAAwAAAAEAAAADAAAAAQACAAQACQAIAAEAAwAAAAEABAAEAAAAAAcAAAACAAAAAAAGAAAABQAAAAAAAAAAAAUAAQAAAEABQADAAUAAwAFAAMAAAAAAAUACwADAAUACwAFAAsACgAHAAUABwAHAAUAAwAEAAIABQAFAAYAAQAIAAcAAAADAAcABAANABAAAAAIAAQACAAKAA8ADQAPAAcADgAHAAUACQAFAA8ADwAPABAAAAAGAAEACAAIAAIAAwAAAAAAAAMAAAACAAEACQAAAAMAAAABAAAAAgAAAAAABAACAAIABAABAAkABAADAAIABQAFAAIACwACAAcABwAJAAcABQAAAAAABQACAAEAAQAFAAEABwABAAkABAADAAcABQAJAAUAAAAAAAQAAwAHAAQABwALAA0AAAANAA8ADQAQABQADQARAA8AAAACAAIAAQAJAAkABQAJAAUACgAJAAIAAwAEAAIAAwADAAIAAQABAAIABQABAAgAAAAkABQADAAIABAACAAsADQANAAkABQAFAA8ADQAIABAAAAAEAAEAAwAGAAAAAwAHAAkACwAIAAEACQAAAAMAAAACAAAAAQAAAAIABQAFAA4AFQAFAAkACgAJAAUACAAHAAAAAAQAAQADAAEABAABAAkAAwAEAAcAAQAAAAUABQAHAAQABwALAA0AAAAIAAQABQALAAUAAwAAAAAABwACAAEAAQAFAAUABwAEAAkABAACAAIAAQAJAAkABAADAAUACAAHAAkABQAAAAAAAAEAAwACAAEABAACAAcACQALAAIABQAFAA8ADwAIABAAAAAEAAEAAwAGAAAAAwAGAAkABQAIAAEACAAAAAMAAAACAAAAAQAAAAIABQAFAA4AFQAFAAkACgAJAAUACAAHAAAAAAQAAQADAAEABAABAAkAAwAEAAcAAQAAAAAABQAIAAcAAAACAAQAAwAHAAQABwANABAAAAAJAAUABgAFAAUAAgAAAAAAAwABAAQAAwAHAAUAAQAAAAAAAgACAAIABAADAAkACwAJAAQACgAFAAUACQAJAAIAAwAEAAIAAwADAAIAAwABAAUAAQADAAIAAQAJAAkABwAIAAEAAAAAABEAAAAAAAAAAQAAAEsAEgAaACAABQAJAAcABAADAAIAAgAEAAEAAAAAAAYAAgABAAIAAgACAAIABQAHAAgACQAHAAcABwAAAAAADgAIAAQABgAHAA8ADwAQAAUAAAACAAQACgAKAA8ADQAPABAAAAAHAAIAAgABAAEAAQAFAAEACQAEAAEAAwACAAUABQAFAAkABgAJAAcAAAABAAEABAACAAEABAAFAAcACAAJAAcABwAGAAUAAwAEAAQAAQAGAAkACgAAAAUAAAAEAAQABQAAAAEABgABAAQAAAACAAQABAAFAAAAAAEABwAGAAUAAQAAAAAAAgAEAAQAAAABAAIABgABAAAAAgAFAAYAAAAEAAgABQAFAAYAAgACAAQAAAAEAAYAAwAEAAIAAgAGAAIAAgABAAEAAwAHAAcABwADAAcABwAHAAQACQAIAAkACAAJAAgADgAJAA4ACQAOAA4AEAAGAAsAAwALAAQABwALAAQACwAFAAUABwAFAAkAAAACAAEAAAAEAAQAAgABAAEAAAACAAcABQAIAAcABAAGAAQABQAFAAYAAwAAAAUAAwAEAAgAAQAIAAEABAAEAAQAAgADAAQAAwAAAAcAAQAFAAUABAABAAcAAQAJAAQABAALAAUAAQAAAAAAAgAGAAUAAwADAAcABQAFAAYAAQAAAAAAAgAGAAUABAAGAAgABQAFAAYAAgACAAQABAAHAAcAAQAAAAAIAAEACAAHAAUAAgADAAIAAQAFAAIAAwAAAAAABwAIAAcAAAADAAUABgAFAAUAAgADAAgAAAACAAEAAgACAAIABQAIAAoACAAIAAUACAAHAAAAAAQAAQADAAQABAAJAA4AAAADAAQACAAAAAIAAAADAAAAAQAAAgADAAgAAgAAAAAABwAIAAcAAAAFAAUABQAFAAUABgAIAAkABAAMAAcABAAMAAgABAAMAAoABAAMAAwABAAMAA4ABAAMAAsACAAFAAsACAAHAAcADAAIAAkACAALAAkADAAJAAkABAALAAkABAALAAkACgALAAkADAALAAkADgALAAkADAAMAAgADAAMAAkADAAMAAoADAAMAAsADAANAAsADQANAAsADQANAAsADQAKAAgADQALAAgADQAMAAgADQANAAsAAwADAAQAAwAFAAMABgADAAcAAwACAAUAAQADAAMAAwAEAAAAAAQAAQAEAAUAAQAEAAAAAAcAAAADAAAAAwAAAAEAAAADAAAAAQACAAQACQAIAAEAAwAAAAEABAAEAAAAAAcAAAACAAAAAAAGAAAABQAAAAAAAAAAAAUAAQAAAEABQADAAUAAwAFAAMAAAAAAAUACwADAAUACwAFAAsACgAHAAUABwAHAAUAAwAEAAIABQAFAAYAAQAIAAcAAAADAAcABAANABAAAAAIAAQACAAKAA8ADQAPAAcADgAHAAUACQAFAA8ADwAPABAAAAAGAAEACAAIAAIAAwAAAAAAAAMAAAACAAEACQAAAAMAAAABAAAAAgAAAAAABAACAAIABAABAAkABAADAAIABQAFAAIACwACAAcABwAJAAcABQAAAAAABQACAAEAAQAFAAEABwABAAkABAADAAcABQAJAAUAAAAAAAQAAwAHAAQABwALAA0AAAAIAAQAAQAJAAUACgAJAAUACgAJAAIAAwAEAAIAAwADAAIAAQABAAIABQABAAgAAAACAAQAAwAHAAIABQAFAA8ADwAIABAAAAAEAAEAAwAGAAAAAwAGAAkACwAIAAEACQAAAAMAAAACAAAAAQAAAAIABQAFAA4AFQAFAAkACgAJAAUACAAHAAAAAAQAAQADAAEABAABAAkAAwAEAAcAAQAAAAAABQAIAAcAAAACAAQAAwAHAAQABwANABAAAAAJAAUABgAFAAUAAgAAAAAAAwABAAQAAwAHAAUAAQAAAAAAAgACAAIABAADAAkACwAJAAQACgAFAAUACQAJAAIAAwAEAAIAAwADAAIAAwABAAUAAQADAAIAAQAJAAkABwAIAAEAAAAAABEAAAA=)
<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')

# -----------------------------
# CÁC HÀM TIỆN ÍCH
# -----------------------------
class PDF(FPDF):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            # Decode the font from base64 and write to a temporary file
            font_data = base64.b64decode(ROBOTO_FONT_BASE64)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".ttf") as temp_font_file:
                temp_font_file.write(font_data)
                self.font_path = temp_font_file.name
            
            self.add_font('Roboto', '', self.font_path, uni=True)
            self.font_family = 'Roboto'
        except Exception as e:
            st.error(f"Lỗi khi tải font chữ cho PDF: {e}. Sử dụng font mặc định.")
            self.font_family = 'Arial' # Fallback font

    def __del__(self):
        # Clean up the temporary font file when the object is destroyed
        if hasattr(self, 'font_path') and os.path.exists(self.font_path):
            os.remove(self.font_path)
            
    def header(self): self.set_font(self.font_family, 'B', 16); self.cell(0, 10, 'BÁO CÁO KẾT QUẢ HỌC TẬP', 0, 1, 'C'); self.ln(5)
    def footer(self): self.set_y(-15); self.set_font(self.font_family, 'I', 8); self.cell(0, 10, f'Trang {self.page_no()}/{{nb}}', 0, 0, 'C')
    def chapter_title(self, title): self.set_font(self.font_family, 'B', 12); self.cell(0, 10, title, 0, 1, 'L'); self.ln(2)
    def student_info(self, info: Dict):
        self.set_font(self.font_family, '', 11)
        for key, value in info.items():
            self.set_font(self.font_family, 'B', 11); self.cell(40, 7, f'{key}:'); self.set_font(self.font_family, '', 11); self.cell(0, 7, value); self.ln()
        self.ln(5)
    def create_table(self, data: pd.DataFrame, column_widths: List):
        self.set_font(self.font_family, 'B', 10)
        for col, width in zip(data.columns, column_widths): self.cell(width, 8, col, 1, 0, 'C')
        self.ln()
        self.set_font(self.font_family, '', 10)
        for _, row in data.iterrows():
            for col, width in zip(data.columns, column_widths):
                text = str(row[col]).replace('**', ''); self.cell(width, 7, text, 1, 0, 'C' if col not in ["Học kỳ", "Course", "Tên môn học"] else "L")
            self.ln()
# ... (Các hàm calc_gpa, check_academic_warning, v.v. giữ nguyên)
@st.cache_data
def to_csv(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")
def calc_gpa(df: pd.DataFrame, grade_map: Dict[str, float]) -> float:
    if df.empty: return 0.0
    work = df.copy()
    fail_grades = [grade for grade, point in grade_map.items() if point == 0.0]
    work_passed = work[~work["Grade"].isin(fail_grades)]
    if work_passed.empty: return 0.0
    work_passed["Points"] = work_passed["Grade"].map(grade_map).fillna(0.0)
    work_passed["QP"] = work_passed["Points"] * pd.to_numeric(work_passed["Credits"], errors="coerce").fillna(0.0)
    total_credits = pd.to_numeric(work_passed["Credits"], errors="coerce").fillna(0.0).sum()
    if total_credits <= 0: return 0.0
    return (work_passed["QP"].sum()) / total_credits
def check_academic_warning(semester_number: int, sgpa: float, cumulative_f_credits: float, previous_warning_level: int) -> Tuple[int, str, List[str]]:
    reasons, is_warning_condition_met = [], False
    if semester_number == 1 and sgpa < 0.80: is_warning_condition_met = True; reasons.append(f"SGPA học kỳ 1 ({sgpa:.2f}) < 0.80")
    elif semester_number > 1 and sgpa < 1.00: is_warning_condition_met = True; reasons.append(f"SGPA ({sgpa:.2f}) < 1.00")
    if cumulative_f_credits > 24: is_warning_condition_met = True; reasons.append(f"Tổng tín chỉ nợ ({cumulative_f_credits}) > 24")
    current_warning_level = 0
    if is_warning_condition_met: current_warning_level = min(previous_warning_level + 1, 3)
    if current_warning_level > 0: return current_warning_level, f"Cảnh báo học tập Mức {current_warning_level}", reasons
    return 0, "Đạt yêu cầu", []
def calculate_progress(all_sems_data: List[pd.DataFrame], requirements: Dict, grade_map: Dict):
    if not any(not df.empty for df in all_sems_data): return pd.DataFrame()
    master_df = pd.concat(all_sems_data, ignore_index=True)
    fail_grades = [grade for grade, point in grade_map.items() if point == 0.0]
    passed_df = master_df[~master_df["Grade"].isin(fail_grades)].copy()
    passed_df["Credits"] = pd.to_numeric(passed_df["Credits"], errors="coerce").fillna(0.0)
    progress_data = []
    total_completed = passed_df["Credits"].sum()
    total_required = requirements.get("Tổng tín chỉ tích lũy", 1)
    progress_data.append({"Khối kiến thức": "Tổng tín chỉ", "Tín chỉ Hoàn thành": total_completed, "Tín chỉ Yêu cầu": total_required})
    category_credits = passed_df.groupby("Category")["Credits"].sum()
    for category_name, required in requirements.items():
        if category_name == "Tổng tín chỉ tích lũy": continue
        completed = category_credits.get(category_name, 0.0)
        progress_data.append({"Khối kiến thức": category_name, "Tín chỉ Hoàn thành": completed, "Tín chỉ Yêu cầu": required})
    df = pd.DataFrame(progress_data)
    df["Còn lại"] = (df["Tín chỉ Yêu cầu"] - df["Tín chỉ Hoàn thành"]).clip(lower=0)
    df["Tiến độ"] = (df["Tín chỉ Hoàn thành"] / df["Tín chỉ Yêu cầu"]).clip(0, 1) if df["Tín chỉ Yêu cầu"].all() > 0 else 0
    return df
def get_preloaded_sems_from_major(major_name):
    data = MAJORS_DATA[major_name].get("preloaded_data", [])
    if not data: return [], 1
    df = pd.DataFrame(data)
    max_sem = df["Semester"].max() if "Semester" in df.columns and not df.empty else 1
    sems = []
    for i in range(1, int(max_sem) + 1):
        sem_df = df[df["Semester"] == i][["Course", "Credits", "Grade", "Category"]].reset_index(drop=True)
        sems.append(sem_df if not sem_df.empty else pd.DataFrame(columns=["Course", "Credits", "Grade", "Category"]))
    return sems, int(max_sem)
def get_student_level(credits: float) -> str:
    if credits < 37: return "Năm thứ nhất"
    if 37 <= credits <= 72: return "Năm thứ hai"
    if 73 <= credits <= 108: return "Năm thứ ba"
    if 109 <= credits <= 142: return "Năm thứ tư"
    return "Năm thứ năm"
def get_gpa_ranking(gpa: float) -> str:
    if gpa >= 3.60: return "Xuất sắc"
    if 3.20 <= gpa < 3.60: return "Giỏi"
    if 2.50 <= gpa < 3.20: return "Khá"
    if 2.30 <= gpa < 2.50: return "Trung bình khá"
    if 2.00 <= gpa < 2.30: return "Trung bình"
    if 1.50 <= gpa < 2.00: return "Trung bình yếu"
    if 1.00 <= gpa < 1.50: return "Yếu"
    return "Kém"
def generate_pdf_report(student_info, summary_df, detailed_dfs, total_summary):
    pdf = PDF()
    pdf.alias_nb_pages(); pdf.add_page()
    pdf.student_info(student_info)
    pdf.chapter_title('Bảng điểm Tổng hợp')
    pdf.create_table(summary_df, column_widths=[50, 30, 30, 25, 35])
    pdf.ln(5)
    pdf.chapter_title('Tổng kết Toàn khóa')
    pdf.set_font(pdf.font_family, '', 11)
    for key, value in total_summary.items():
        pdf.set_font(pdf.font_family, 'B', 11); pdf.cell(50, 7, f'{key}:'); pdf.set_font(pdf.font_family, '', 11); pdf.cell(0, 7, str(value)); pdf.ln()
    pdf.ln(5)
    pdf.add_page()
    pdf.chapter_title('Bảng điểm Chi tiết')
    for i, df in enumerate(detailed_dfs):
        if not df.empty:
            pdf.set_font(pdf.font_family, 'B', 11); pdf.cell(0, 10, f'Học kỳ {i+1}', 0, 1)
            df_display = df.copy(); df_display.insert(0, 'STT', range(1, len(df_display) + 1))
            pdf_display = df_display.rename(columns={"Course": "Tên môn học", "Credits": "TC", "Grade": "Điểm", "Category": "Phân loại"})
            pdf.create_table(df_display[['STT', 'Tên môn học', 'TC', 'Điểm', 'Phân loại']], column_widths=[10, 80, 15, 15, 70])
            pdf.ln(5)
    return pdf.output(dest='S').encode('latin1')

# -----------------------------
# SIDEBAR
# -----------------------------
with st.sidebar:
    st.title("⚙️ Cài đặt & Thao tác")
    st.subheader("Thang điểm")
    scale_name = st.selectbox("Chọn thang điểm:", list(PRESET_SCALES.keys()), index=0)
    grade_map = PRESET_SCALES[scale_name]
    st.divider()
    st.subheader("📁 Nhập / Xuất File")
    if st.button("⬇️ Xuất toàn bộ dữ liệu (CSV)"):
        all_dfs = [];
        for i, df in enumerate(st.session_state.get("sems", [])):
            df_copy = df.copy(); df_copy["Semester"] = i + 1; all_dfs.append(df_copy)
        if any(not df.empty for df in all_dfs):
            master_df = pd.concat(all_dfs, ignore_index=True)
            st.download_button(label="Tải về file tổng hợp", data=to_csv(master_df), file_name="GPA_data_all_semesters.csv", mime="text/csv", use_container_width=True)
        else: st.warning("Chưa có dữ liệu để xuất.")
    def on_file_upload(): st.session_state.file_processed = False
    upload = st.file_uploader("Nhập file CSV (có cột Semester, Category)", type=["csv"], key="uploader", on_change=on_file_upload)
    st.divider()
    st.subheader("🖨️ In Báo cáo")
    if st.button("Tạo Báo cáo PDF", use_container_width=True): st.session_state.pdf_generated = True

# -----------------------------
# GIAO DIỆN CHÍNH
# -----------------------------
st.title("🎓 Hệ thống Tư vấn Học tập")
with st.container(border=True):
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Họ và tên:", value="Nguyễn Đình Mai Nam", key="sv_hoten")
        st.text_input("Mã số sinh viên:", value="2151113235", key="sv_mssv")
    with col2:
        st.text_input("Lớp:", value="63CT2", key="sv_lop")
        def on_major_change():
            major = st.session_state.major_selector
            sems, max_sem = get_preloaded_sems_from_major(major)
            st.session_state.sems = sems; st.session_state.n_sem_input = max_sem
        selected_major = st.selectbox("Ngành học:", options=list(MAJORS_DATA.keys()), key="major_selector", on_change=on_major_change)
st.divider()
if "sems" not in st.session_state: on_major_change()
GRADUATION_REQUIREMENTS_CURRENT = MAJORS_DATA[selected_major]['graduation_requirements']
DEFAULT_COURSE_CATEGORIES_CURRENT = MAJORS_DATA[selected_major]['course_categories']
if upload is not None and not st.session_state.get('file_processed', False):
    try:
        df_up = pd.read_csv(upload, encoding='utf-8')
        needed = {"Course", "Credits", "Grade", "Semester", "Category"}
        if not needed.issubset(df_up.columns): st.warning("File CSV phải có các cột: Course, Credits, Grade, Semester, Category")
        else:
            df_up["Semester"] = pd.to_numeric(df_up["Semester"], errors="coerce").fillna(1).astype(int)
            max_sem = df_up["Semester"].max()
            st.session_state.n_sem_input = max_sem
            new_sems = [df_up[df_up["Semester"] == i][["Course", "Credits", "Grade", "Category"]].reset_index(drop=True) for i in range(1, max_sem + 1)]
            st.session_state.sems = new_sems
            st.session_state.file_processed = True; st.success(f"Đã nhập và phân bổ dữ liệu cho {max_sem} học kỳ."); st.rerun()
    except Exception as e: st.error(f"Không thể đọc file CSV: {e}"); st.session_state.file_processed = True
tab1, tab2 = st.tabs(["Bảng điểm Chi tiết", "Bảng điểm Tổng hợp"])
with tab1:
    st.header("📊 Bảng tổng quan Tiến độ Tốt nghiệp")
    progress_df = calculate_progress(st.session_state.sems, GRADUATION_REQUIREMENTS_CURRENT, grade_map)
    if not progress_df.empty:
        total_progress = progress_df.iloc[0]
        st.subheader(f"Tổng quan: {total_progress['Tín chỉ Hoàn thành']:.0f} / {total_progress['Tín chỉ Yêu cầu']:.0f} tín chỉ đã tích lũy")
        st.progress(total_progress['Tiến độ'], text=f"{total_progress['Tiến độ']:.1%}")
        st.markdown("---")
        detail_df = progress_df[progress_df['Tín chỉ Yêu cầu'] > 0].iloc[1:].reset_index(drop=True)
        if not detail_df.empty:
            st.subheader("Chi tiết theo khối kiến thức")
            left_col, right_col = st.columns(2)
            for i, row in detail_df.iterrows():
                target_col = left_col if i % 2 == 0 else right_col
                with target_col:
                    delta_text = f"Còn lại: {row['Còn lại']:.0f}"; delta_color = "inverse"
                    if row['Còn lại'] == 0: delta_text = "✅ Hoàn thành"; delta_color = "off"
                    st.metric(label=str(row["Khối kiến thức"]), value=f"{row['Tín chỉ Hoàn thành']:.0f} / {row['Tín chỉ Yêu cầu']:.0f}", delta=delta_text, delta_color=delta_color)
                    st.progress(row['Tiến độ'])
    else: st.info("Chưa có dữ liệu để phân tích tiến độ.")
    st.divider()
    n_sem = st.number_input("Số học kỳ (semesters)", min_value=1, max_value=20, value=st.session_state.get('n_sem_input', 8), step=1, key="n_sem_input")
    if "manual_warnings" not in st.session_state or len(st.session_state.manual_warnings) != n_sem: st.session_state.manual_warnings = ["Không"] * n_sem
    if len(st.session_state.sems) != n_sem:
        current_sems = st.session_state.get("sems", []); current_len = len(current_sems)
        if current_len < n_sem: current_sems += [pd.DataFrame(columns=["Course", "Credits", "Grade", "Category"]) for _ in range(n_sem - current_len)]
        else: current_sems = current_sems[:n_sem]
        st.session_state.sems = current_sems; st.rerun()
    sem_tabs = st.tabs([f"Học kỳ {i+1}" for i in range(n_sem)])
    per_sem_gpa, per_sem_cred, warning_history = [], [], []
    cumulative_f_credits, previous_warning_level = 0.0, 0
    fail_grades = [grade for grade, point in grade_map.items() if point == 0.0]
    for i, tab in enumerate(sem_tabs):
        with tab:
            st.write(f"### Bảng điểm Học kỳ {i+1}")
            df_with_delete = st.session_state.sems[i].copy(); df_with_delete.insert(0, "Xóa", False)
            grade_options = list(grade_map.keys())
            if not grade_options: st.warning("Chưa có thang điểm."); grade_options = ["..."]
            edited = st.data_editor(df_with_delete, num_rows="dynamic", hide_index=True, use_container_width=True,
                column_config={"Xóa": st.column_config.CheckboxColumn(width="small"), "Course": st.column_config.TextColumn("Tên môn học", width="large", required=True),"Credits": st.column_config.NumberColumn("Số tín chỉ", min_value=0.0, step=0.5, required=True),"Grade": st.column_config.SelectboxColumn("Điểm chữ", options=grade_options, required=True),"Category": st.column_config.SelectboxColumn("Phân loại", options=DEFAULT_COURSE_CATEGORIES_CURRENT, required=True)}, key=f"editor_{i}")
            st.session_state.sems[i] = edited.drop(columns=["Xóa"])
            current_sem_df = st.session_state.sems[i]
            gpa = calc_gpa(current_sem_df, grade_map); per_sem_gpa.append(gpa)
            creds = pd.to_numeric(current_sem_df["Credits"], errors="coerce").fillna(0.0).sum(); per_sem_cred.append(float(creds))
            current_f_credits = pd.to_numeric(current_sem_df[current_sem_df["Grade"].isin(fail_grades)]["Credits"], errors="coerce").fillna(0.0).sum()
            cumulative_f_credits += current_f_credits
            auto_warning_level, _, auto_reasons = check_academic_warning(i + 1, gpa, cumulative_f_credits, previous_warning_level)
            st.divider()
            m1, m2, m3 = st.columns(3)
            m1.metric("GPA học kỳ (SGPA)", f"{gpa:.3f}"); m2.metric("Tổng tín chỉ học kỳ", f"{creds:.2f}")
            m3.metric("Tín chỉ nợ tích lũy", value=f"{cumulative_f_credits:.2f}", delta=f"{current_f_credits:.2f} TC nợ mới" if current_f_credits > 0 else None, delta_color="inverse")
            st.write("##### Tình trạng học vụ")
            if i > 0:
                w_col1, w_col2 = st.columns(2)
                with w_col1: st.metric("Kết quả XLHV học kỳ trước:", f"Mức {previous_warning_level}" if previous_warning_level > 0 else "Không")
                with w_col2: st.metric("Kết quả XLHV dự kiến:", f"Mức {auto_warning_level}" if auto_warning_level > 0 else "Không", delta="Dựa trên điểm kỳ này", delta_color="off")
            else:
                st.metric("Kết quả XLHV dự kiến:", f"Mức {auto_warning_level}" if auto_warning_level > 0 else "Không", delta="Dựa trên điểm kỳ này", delta_color="off")
            
            manual_warning_options = ["Không", "Mức 1", "Mức 2", "Mức 3", "Xóa tên khỏi danh sách"]
            selected_warning_str = st.selectbox("Xử lý học vụ (chính thức):", options=manual_warning_options, index=manual_warning_options.index(st.session_state.manual_warnings[i]) if st.session_state.manual_warnings[i] in manual_warning_options else 0, key=f"manual_warning_{i}")
            st.session_state.manual_warnings[i] = selected_warning_str
            
            warning_map = {"Không": 0, "Mức 1": 1, "Mức 2": 2, "Mức 3": 3, "Xóa tên khỏi danh sách": 4}
            final_warning_level = warning_map.get(selected_warning_str, 0)
            
            warning_history.append({"Học kỳ": i + 1, "Mức Cảnh báo": final_warning_level, "Lý do": ", ".join(auto_reasons) if auto_reasons else "Không có"})
            previous_warning_level = final_warning_level
            with st.expander("🔴 Thao tác Nguy hiểm"):
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("🗑️ Xóa môn đã chọn", key=f"delete_{i}", use_container_width=True, type="secondary"):
                        rows_to_keep = [row for _, row in edited.iterrows() if not row["Xóa"]]
                        st.session_state.sems[i] = pd.DataFrame(rows_to_keep).drop(columns=["Xóa"]); st.rerun()
                with c2:
                    if st.button("🔄 Reset học kỳ", key=f"confirm_reset_btn_{i}", use_container_width=True, type="secondary"): st.session_state[f"confirm_reset_{i}"] = True
                if st.session_state.get(f"confirm_reset_{i}", False):
                    st.warning("Bạn có chắc chắn muốn xóa toàn bộ dữ liệu của học kỳ này không?")
                    cc1, cc2 = st.columns(2)
                    with cc1:
                        if st.button("⚠️ Vâng, tôi chắc chắn", key=f"reset_yes_{i}", use_container_width=True, type="primary"):
                            st.session_state.sems[i] = pd.DataFrame(columns=["Course", "Credits", "Grade", "Category"])
                            st.session_state[f"confirm_reset_{i}"] = False; st.rerun()
                    with cc2:
                        if st.button("Hủy bỏ", key=f"reset_no_{i}", use_container_width=True):
                            st.session_state[f"confirm_reset_{i}"] = False; st.rerun()
    st.divider()
    st.header("Tổng kết Toàn khóa")
    all_passed_dfs = [df[~df["Grade"].isin(fail_grades)] for df in st.session_state.sems]
    master_passed_df = pd.concat(all_passed_dfs) if all_passed_dfs else pd.DataFrame()
    cgpa = calc_gpa(master_passed_df, grade_map)
    total_passed_credits = pd.to_numeric(master_passed_df['Credits'], errors='coerce').fillna(0).sum()
    colA, colB = st.columns(2); colC, colD = st.columns(2)
    with colA: st.metric("🎯 GPA Tích lũy (CGPA)", f"{cgpa:.3f}")
    with colB: st.metric("📚 Tổng tín chỉ đã qua", f"{total_passed_credits:.2f}")
    with colC: st.metric("🧑‍🎓 Trình độ sinh viên", get_student_level(total_passed_credits))
    with colD: st.metric("🏆 Xếp loại học lực", get_gpa_ranking(cgpa))
    chart_col, _ = st.columns([1, 1])
    with chart_col:
        st.subheader("Xu hướng GPA theo học kỳ")
        if per_sem_gpa and all(c >= 0 for c in per_sem_cred):
            try:
                fig, ax = plt.subplots(); x = np.arange(1, len(per_sem_gpa) + 1)
                ax.plot(x, per_sem_gpa, marker="o", linestyle="-", color='b')
                ax.set_xlabel("Học kỳ"); ax.set_ylabel("GPA (SGPA)"); ax.set_title("Biểu đồ GPA các học kỳ")
                ax.set_xticks(x); ax.grid(True, linestyle=":", linewidth=0.5)
                ax.set_ylim(bottom=0, top=max(4.1, max(per_sem_gpa) * 1.1 if per_sem_gpa and any(v > 0 for v in per_sem_gpa) else 4.1))
                st.pyplot(fig, use_container_width=True)
            except Exception: st.info("Chưa đủ dữ liệu để vẽ biểu đồ.")

with tab2:
    st.header("Bảng điểm Tổng hợp theo Học kỳ và Năm học")
    summary_data, cumulative_credits, cumulative_qp = [], 0.0, 0.0
    year_map = {1: "thứ nhất", 2: "thứ hai", 3: "thứ ba", 4: "thứ tư", 5: "thứ năm"}
    for i in range(len(st.session_state.sems)):
        sem_df = st.session_state.sems[i]
        sem_gpa = per_sem_gpa[i]
        passed_df = sem_df[~sem_df['Grade'].isin(fail_grades)]
        passed_credits = pd.to_numeric(passed_df['Credits'], errors='coerce').fillna(0).sum()
        sem_qp = calc_gpa(passed_df, grade_map) * passed_credits
        cumulative_credits += passed_credits; cumulative_qp += sem_qp
        cumulative_gpa = (cumulative_qp / cumulative_credits) if cumulative_credits > 0 else 0.0
        summary_data.append({"Học kỳ": f"Học kỳ {i + 1}", "TBC Hệ 4 (SGPA)": f"{sem_gpa:.2f}", "TBTL Hệ 4 (CGPA)": f"{cumulative_gpa:.2f}", "Số TC Đạt": int(passed_credits), "Số TCTL Đạt": int(cumulative_credits)})
        if (i + 1) % 2 == 0:
            year_number = (i // 2) + 1; year_text = year_map.get(year_number, f"thứ {year_number}"); year_str = f"Năm {year_text}"
            summary_data.append({"Học kỳ": f"**{year_str}**", "TBC Hệ 4 (SGPA)": "", "TBTL Hệ 4 (CGPA)": f"**{cumulative_gpa:.2f}**", "Số TC Đạt": f"**{int(per_sem_cred[i] + per_sem_cred[i-1])}**", "Số TCTL Đạt": f"**{int(cumulative_credits)}**"})
    st.dataframe(pd.DataFrame(summary_data), use_container_width=True, hide_index=True)

if st.session_state.get('pdf_generated', False):
    student_info_dict = {"Họ và tên": st.session_state.sv_hoten, "Mã SV": st.session_state.sv_mssv, "Lớp": st.session_state.sv_lop, "Ngành học": selected_major}
    summary_df_pdf = pd.DataFrame(summary_data)
    total_summary_dict = {"GPA Tích lũy (CGPA)": f"{cgpa:.3f}", "Tổng tín chỉ đã qua": f"{total_passed_credits:.2f}", "Trình độ sinh viên": get_student_level(total_passed_credits), "Xếp loại học lực": get_gpa_ranking(cgpa)}
    pdf_data = generate_pdf_report(student_info_dict, summary_df_pdf, st.session_state.sems, total_summary_dict)
    st.sidebar.download_button(label="Tải về Báo cáo PDF", data=pdf_data, file_name=f"Bao_cao_hoc_tap_{st.session_state.sv_mssv}.pdf", mime="application/pdf", use_container_width=True)
    st.session_state.pdf_generated = False

with st.expander("❓ Hướng dẫn"):
    st.markdown("""- **Nhập/Xuất file:** File CSV phải có các cột: `Course`, `Credits`, `Grade`, `Semester`, `Category`.\n- **Thêm/xóa môn học:** Dùng nút `+` để thêm và tick vào ô "Xóa" rồi nhấn nút "🗑️ Xóa môn đã chọn" để xóa.\n- **Xử lý học vụ:** Chọn mức cảnh báo chính thức của nhà trường tại mỗi học kỳ để ghi đè lên kết quả tính toán tự động của ứng dụng.""")
with st.expander("📜 Cách tính & Lịch sử xử lý học vụ"):
    def style_warning_html(level):
        if level == 0: return f'<p style="color: green; margin:0;">Không</p>'
        if level == 1: return f'<p style="color: orange; font-weight: bold; margin:0;">Mức {level}</p>'
        if level in [2, 3]: return f'<p style="color: red; font-weight: bold; margin:0;">Mức {level}</p>'
        if level == 4: return f'<p style="color: white; background-color: black; font-weight: bold; margin:0; padding: 2px 5px; border-radius: 3px;">Xóa tên</p>'
    display_df = pd.DataFrame(warning_history)
    display_df["Mức Cảnh báo"] = display_df["Mức Cảnh báo"].apply(style_warning_html)
    display_df = display_df.rename(columns={"Học kỳ": "<b>Học kỳ</b>", "Mức Cảnh báo": "<b>Mức Xử lý</b>", "Lý do": "<b>Lý do (gợi ý)</b>"})
    st.markdown(display_df.to_html(escape=False, index=False), unsafe_allow_html=True)
