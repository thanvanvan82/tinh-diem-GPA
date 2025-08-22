import streamlit as st
import pandas as pd
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="Hệ thống Tư vấn Học tập", page_icon="🎓", layout="wide")

# -----------------------------
# DỮ LIỆU CẤU HÌNH & HẰNG SỐ
# -----------------------------

# NÂNG CẤP: Cấu trúc dữ liệu trung tâm cho nhiều ngành học
# Để thêm ngành mới, chỉ cần sao chép cấu trúc của một ngành và cập nhật dữ liệu.
MAJORS_DATA = {
    "Công nghệ kỹ thuật xây dựng": {
        "student_info": "2151113235 - Nguyễn Đình Mai Nam - 63CT2 - Công nghệ kỹ thuật xây dựng",
        "course_categories": [
            "Lý luận chính trị", "Kỹ năng", "Ngoại ngữ", "Khoa học tự nhiên và tin học",
            "Giáo dục quốc phòng an ninh", "Giáo dục thể chất", "Kiến thức cơ sở khối ngành",
            "Kiến thức cơ sở ngành", "Kiến thức ngành", "Kiến thức tự chọn",
            "Thực tập và học phần tốt nghiệp", "Môn học điều kiện", "Chuẩn đầu ra"
        ],
        "graduation_requirements": {
            "Lý luận chính trị": 13, "Kỹ năng": 3, "Ngoại ngữ": 6, "Khoa học tự nhiên và tin học": 21,
            "Giáo dục quốc phòng an ninh": 11, "Giáo dục thể chất": 34, "Kiến thức cơ sở khối ngành": 31,
            "Kiến thức cơ sở ngành": 22, "Kiến thức ngành": 39, "Kiến thức tự chọn": 27,
            "Thực tập và học phần tốt nghiệp": 13,
        },
        "preloaded_data": [
            # Dữ liệu điểm của sinh viên Nguyễn Đình Mai Nam được đặt ở đây
            {'Course': 'Bóng chuyền 1', 'Credits': 1, 'Grade': 'D', 'Category': 'Giáo dục thể chất', 'Semester': 1},
            {'Course': 'Bóng chuyền 2', 'Credits': 1, 'Grade': 'C', 'Category': 'Giáo dục thể chất', 'Semester': 1},
            {'Course': 'Bóng rổ', 'Credits': 1, 'Grade': 'B', 'Category': 'Giáo dục thể chất', 'Semester': 1},
            {'Course': 'Hóa học đại cương', 'Credits': 3, 'Grade': 'D', 'Category': 'Khoa học tự nhiên và tin học', 'Semester': 1},
            {'Course': 'Cầu lông', 'Credits': 1, 'Grade': 'C', 'Category': 'Giáo dục thể chất', 'Semester': 1},
            {'Course': 'Tin học cơ bản', 'Credits': 2, 'Grade': 'B', 'Category': 'Khoa học tự nhiên và tin học', 'Semester': 1},
            {'Course': 'Giải tích hàm một biến', 'Credits': 3, 'Grade': 'C', 'Category': 'Khoa học tự nhiên và tin học', 'Semester': 1},
            {'Course': 'Kỹ năng mềm và tinh thần khởi nghiệp', 'Credits': 3, 'Grade': 'B', 'Category': 'Kỹ năng', 'Semester': 1},
            {'Course': 'Sức bền vật liệu 1', 'Credits': 3, 'Grade': 'C', 'Category': 'Kiến thức cơ sở ngành', 'Semester': 2},
            {'Course': 'Vật liệu xây dựng', 'Credits': 3, 'Grade': 'C', 'Category': 'Kiến thức cơ sở ngành', 'Semester': 2},
            {'Course': 'Sức bền vật liệu 2', 'Credits': 2, 'Grade': 'C', 'Category': 'Kiến thức cơ sở ngành', 'Semester': 2},
            {'Course': 'Tiếng Anh 1', 'Credits': 3, 'Grade': 'C', 'Category': 'Ngoại ngữ', 'Semester': 2},
            {'Course': 'Cơ học chất lỏng', 'Credits': 3, 'Grade': 'C', 'Category': 'Kiến thức cơ sở ngành', 'Semester': 2},
            {'Course': 'Pháp luật đại cương', 'Credits': 2, 'Grade': 'C', 'Category': 'Lý luận chính trị', 'Semester': 2},
            {'Course': 'Địa chất công trình', 'Credits': 2, 'Grade': 'D', 'Category': 'Kiến thức cơ sở khối ngành', 'Semester': 2},
            {'Course': 'Triết học Mác - Lênin', 'Credits': 3, 'Grade': 'D', 'Category': 'Lý luận chính trị', 'Semester': 2},
            {'Course': 'Vật lý 2', 'Credits': 3, 'Grade': 'C', 'Category': 'Khoa học tự nhiên và tin học', 'Semester': 3},
            {'Course': 'Đồ họa kỹ thuật 1', 'Credits': 2, 'Grade': 'D', 'Category': 'Kiến thức cơ sở khối ngành', 'Semester': 3},
            {'Course': 'Đồ họa kỹ thuật 2', 'Credits': 2, 'Grade': 'C', 'Category': 'Kiến thức cơ sở khối ngành', 'Semester': 3},
            {'Course': 'Kỹ thuật điện', 'Credits': 3, 'Grade': 'D', 'Category': 'Kiến thức cơ sở khối ngành', 'Semester': 3},
            {'Course': 'Nền móng', 'Credits': 2, 'Grade': 'D', 'Category': 'Kiến thức ngành', 'Semester': 3},
            {'Course': 'Cơ học đất', 'Credits': 3, 'Grade': 'D', 'Category': 'Kiến thức ngành', 'Semester': 3},
            {'Course': 'Tư tưởng Hồ Chí Minh', 'Credits': 2, 'Grade': 'D', 'Category': 'Lý luận chính trị', 'Semester': 3},
            {'Course': 'Thủy lực công trình', 'Credits': 3, 'Grade': 'C', 'Category': 'Kiến thức ngành', 'Semester': 4},
            {'Course': 'Thủy văn công trình', 'Credits': 3, 'Grade': 'D', 'Category': 'Kiến thức ngành', 'Semester': 4},
            {'Course': 'Giải tích hàm nhiều biến', 'Credits': 3, 'Grade': 'C', 'Category': 'Khoa học tự nhiên và tin học', 'Semester': 4},
            {'Course': 'Kinh tế chính trị Mác - Lênin', 'Credits': 2, 'Grade': 'C', 'Category': 'Lý luận chính trị', 'Semester': 4},
            {'Course': 'Nhập môn ngành Công nghệ kỹ thuật xây dựng', 'Credits': 2, 'Grade': 'A', 'Category': 'Kiến thức cơ sở khối ngành', 'Semester': 4},
            {'Course': 'Chủ nghĩa xã hội khoa học', 'Credits': 2, 'Grade': 'D', 'Category': 'Lý luận chính trị', 'Semester': 4},
            {'Course': 'Thống kê trong kỹ thuật', 'Credits': 2, 'Grade': 'C', 'Category': 'Khoa học tự nhiên và tin học', 'Semester': 4},
            {'Course': 'Trắc địa', 'Credits': 2, 'Grade': 'D', 'Category': 'Kiến thức cơ sở khối ngành', 'Semester': 5},
            {'Course': 'Thực tập trắc địa', 'Credits': 1, 'Grade': 'C', 'Category': 'Kiến thức cơ sở khối ngành', 'Semester': 5},
            {'Course': 'Kinh tế xây dựng 1', 'Credits': 2, 'Grade': 'B', 'Category': 'Kiến thức ngành', 'Semester': 5},
            {'Course': 'Cơ sở thiết kế công trình dân dụng và công nghiệp', 'Credits': 2, 'Grade': 'C', 'Category': 'Kiến thức ngành', 'Semester': 5},
            {'Course': 'Ứng dụng BIM trong xây dựng', 'Credits': 2, 'Grade': 'B', 'Category': 'Kiến thức ngành', 'Semester': 5},
            {'Course': 'Công nghệ xây dựng công trình bê tông', 'Credits': 2, 'Grade': 'B', 'Category': 'Kiến thức ngành', 'Semester': 5},
            {'Course': 'Công nghệ xây dựng công trình đất đá', 'Credits': 2, 'Grade': 'B', 'Category': 'Kiến thức ngành', 'Semester': 6},
            {'Course': 'Công nghệ xử lý nền móng', 'Credits': 2, 'Grade': 'B', 'Category': 'Kiến thức ngành', 'Semester': 6},
            {'Course': 'Quản lý đầu tư xây dựng', 'Credits': 3, 'Grade': 'B', 'Category': 'Kiến thức ngành', 'Semester': 6},
            {'Course': 'An toàn xây dựng', 'Credits': 2, 'Grade': 'C', 'Category': 'Kiến thức ngành', 'Semester': 6},
            {'Course': 'Tổ chức xây dựng', 'Credits': 2, 'Grade': 'D', 'Category': 'Kiến thức ngành', 'Semester': 6},
            {'Course': 'Thi công công trình ngầm', 'Credits': 2, 'Grade': 'C', 'Category': 'Kiến thức ngành', 'Semester': 6},
            {'Course': 'Lịch sử Đảng Cộng sản Việt Nam', 'Credits': 2, 'Grade': 'D', 'Category': 'Lý luận chính trị', 'Semester': 7},
            {'Course': 'Máy xây dựng', 'Credits': 3, 'Grade': 'D', 'Category': 'Kiến thức ngành', 'Semester': 7},
            {'Course': 'Giới thiệu và cơ sở thiết kế công trình thủy', 'Credits': 2, 'Grade': 'D', 'Category': 'Kiến thức ngành', 'Semester': 7},
            {'Course': 'Thiết kế công trình cầu đường', 'Credits': 3, 'Grade': 'D', 'Category': 'Kiến thức ngành', 'Semester': 7},
            {'Course': 'Thiết kế đê và công trình bảo vệ bờ sông', 'Credits': 2, 'Grade': 'A', 'Category': 'Kiến thức ngành', 'Semester': 7},
            {'Course': 'Thực tập địa chất công trình', 'Credits': 1, 'Grade': 'C', 'Category': 'Kiến thức cơ sở khối ngành', 'Semester': 7},
            {'Course': 'Thực tập kỹ thuật và tổ chức xây dựng', 'Credits': 3, 'Grade': 'A', 'Category': 'Thực tập và học phần tốt nghiệp', 'Semester': 8},
            {'Course': 'Đồ án tổ chức xây dựng', 'Credits': 1, 'Grade': 'A', 'Category': 'Thực tập và học phần tốt nghiệp', 'Semester': 8},
            {'Course': 'Đồ án công nghệ xây dựng công trình bê tông', 'Credits': 1, 'Grade': 'B', 'Category': 'Thực tập và học phần tốt nghiệp', 'Semester': 8},
            {'Course': 'Đồ án công nghệ xây dựng công trình đất đá', 'Credits': 1, 'Grade': 'B', 'Category': 'Thực tập và học phần tốt nghiệp', 'Semester': 8},
            {'Course': 'Dẫn dòng thi công và công tác hố móng', 'Credits': 2, 'Grade': 'B', 'Category': 'Kiến thức ngành', 'Semester': 8},
            {'Course': 'Đồ án dẫn dòng thi công và công tác hố móng', 'Credits': 1, 'Grade': 'B', 'Category': 'Thực tập và học phần tốt nghiệp', 'Semester': 8},
            {'Course': 'Giám sát chất lượng công trình', 'Credits': 3, 'Grade': 'B', 'Category': 'Kiến thức ngành', 'Semester': 8},
        ]
    },
    "Quản lý xây dựng": {
        "student_info": "Nhập thông tin sinh viên ngành Quản lý xây dựng",
        "course_categories": ["Kinh tế", "Luật", "Quản lý dự án", "Kỹ thuật cơ sở"], # Ví dụ
        "graduation_requirements": { # Dữ liệu mẫu, cần thay thế
            "Kinh tế": 40, "Luật": 20, "Quản lý dự án": 50, "Kỹ thuật cơ sở": 40,
        },
        "preloaded_data": [ # Dữ liệu mẫu, cần thay thế
            {'Course': 'Kinh tế vi mô', 'Credits': 3, 'Grade': 'A', 'Category': 'Kinh tế', 'Semester': 1},
            {'Course': 'Luật xây dựng', 'Credits': 2, 'Grade': 'B', 'Category': 'Luật', 'Semester': 1},
        ]
    }
}

# Tính toán các giá trị tổng
for major in MAJORS_DATA:
    total_required = sum(MAJORS_DATA[major]["graduation_requirements"].values())
    MAJORS_DATA[major]["graduation_requirements"]["Tổng tín chỉ tích lũy"] = total_required

PRESET_SCALES: Dict[str, Dict[str, float]] = {
    "VN 4.0 (TLU)": {"A": 4.0, "B": 3.0, "C": 2.0, "D": 1.0, "F": 0.0},
}
# -----------------------------
# CÁC HÀM TIỆN ÍCH (Giữ nguyên)
# -----------------------------
# ... (Các hàm calc_gpa, check_academic_warning, calculate_progress, to_csv giữ nguyên)
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
    progress_data.append({"Yêu cầu": "Tổng tín chỉ", "Đã hoàn thành": total_completed, "Yêu cầu": total_required})
    category_credits = passed_df.groupby("Category")["Credits"].sum()
    for category_name, required in requirements.items():
        if category_name == "Tổng tín chỉ tích lũy": continue
        completed = category_credits.get(category_name, 0.0)
        progress_data.append({"Yêu cầu": category_name, "Đã hoàn thành": completed, "Yêu cầu": required})
    df = pd.DataFrame(progress_data)
    df["Còn lại"] = (df["Yêu cầu"] - df["Đã hoàn thành"]).clip(lower=0)
    df["Tiến độ"] = (df["Đã hoàn thành"] / df["Yêu cầu"]).clip(0, 1) if df["Yêu cầu"].all() > 0 else 0
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

# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.title("⚙️ Cài đặt")
scale_name = st.sidebar.selectbox("Thang điểm", list(PRESET_SCALES.keys()), index=0)
grade_map = PRESET_SCALES[scale_name]
st.sidebar.divider()
st.sidebar.subheader("📁 Nhập / Xuất File")
if st.sidebar.button("⬇️ Xuất toàn bộ dữ liệu (CSV)"):
    all_dfs = []
    for i, df in enumerate(st.session_state.get("sems", [])):
        df_copy = df.copy(); df_copy["Semester"] = i + 1; all_dfs.append(df_copy)
    if any(not df.empty for df in all_dfs):
        master_df = pd.concat(all_dfs, ignore_index=True)
        st.sidebar.download_button(label="Tải về file tổng hợp", data=to_csv(master_df), file_name="GPA_data_all_semesters.csv", mime="text/csv", use_container_width=True)
    else: st.sidebar.warning("Chưa có dữ liệu để xuất.")
def on_file_upload(): st.session_state.file_processed = False
upload = st.sidebar.file_uploader("Nhập file CSV (có cột Semester, Category)", type=["csv"], key="uploader", on_change=on_file_upload)

# -----------------------------
# GIAO DIỆN CHÍNH
# -----------------------------
st.title("🎓 Hệ thống Tư vấn Học tập")

def on_major_change():
    major = st.session_state.major_selector
    sems, max_sem = get_preloaded_sems_from_major(major)
    st.session_state.sems = sems
    st.session_state.n_sem_input = max_sem

selected_major = st.selectbox(
    "Chọn ngành học:",
    options=list(MAJORS_DATA.keys()),
    key="major_selector",
    on_change=on_major_change
)

if "sems" not in st.session_state:
    on_major_change()

st.markdown(f"`{MAJORS_DATA[selected_major]['student_info']}`")
GRADUATION_REQUIREMENTS_CURRENT = MAJORS_DATA[selected_major]['graduation_requirements']
DEFAULT_COURSE_CATEGORIES_CURRENT = MAJORS_DATA[selected_major]['course_categories']

# Logic xử lý file upload
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
            st.session_state.file_processed = True
            st.success(f"Đã nhập và phân bổ dữ liệu cho {max_sem} học kỳ.")
            st.rerun()
    except Exception as e: st.error(f"Không thể đọc file CSV: {e}"); st.session_state.file_processed = True

tab1, tab2 = st.tabs(["Bảng điểm Chi tiết", "Bảng điểm Tổng hợp"])

with tab1:
    st.header("📊 Bảng tổng quan Tiến độ Tốt nghiệp")
    progress_df = calculate_progress(st.session_state.sems, GRADUATION_REQUIREMENTS_CURRENT, grade_map)
    if not progress_df.empty:
        total_progress = progress_df.iloc[0]
        st.subheader(f"Tổng quan: {total_progress['Đã hoàn thành']:.0f} / {total_progress['Yêu cầu']:.0f} tín chỉ đã tích lũy")
        st.progress(total_progress['Tiến độ'], text=f"{total_progress['Tiến độ']:.1%}")
        st.markdown("---")
        detail_df = progress_df[progress_df['Yêu cầu'] > 0].iloc[1:].reset_index(drop=True)
        if not detail_df.empty:
            st.subheader("Chi tiết theo khối kiến thức")
            left_col, right_col = st.columns(2)
            for i, row in detail_df.iterrows():
                target_col = left_col if i % 2 == 0
