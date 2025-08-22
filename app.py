import streamlit as st
import pandas as pd
from typing import Dict, List
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="CGPA Calculator", page_icon="🧮", layout="wide")

# -----------------------------
# Helpers
# -----------------------------
PRESET_SCALES: Dict[str, Dict[str, float]] = {
    "VN 4.0 (TLU)": {
        "A": 4.0, "B": 3.0, "C": 2.0, "D": 1.0, "F": 0.0,
    },
    "Simple 10-point": {str(k): float(k) for k in range(10, -1, -1)},
    "US 4.0 (with +/-)": {
        "A+": 4.0, "A": 4.0, "A-": 3.7,
        "B+": 3.3, "B": 3.0, "B-": 2.7,
        "C+": 2.3, "C": 2.0, "C-": 1.7,
        "D+": 1.3, "D": 1.0, "D-": 0.7,
        "F": 0.0,
    },
}

DEFAULT_TEMPLATE = pd.DataFrame(
    [
        {"Course": "Course 1", "Credits": 3.0, "Grade": list(PRESET_SCALES["VN 4.0 (TLU)"].keys())[0]},
        {"Course": "Course 2", "Credits": 3.0, "Grade": list(PRESET_SCALES["VN 4.0 (TLU)"].keys())[2]},
    ]
)

@st.cache_data
def to_csv(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")


def calc_gpa(df: pd.DataFrame, grade_map: Dict[str, float]) -> float:
    if df.empty:
        return 0.0
    work = df.copy()
    work["Points"] = work["Grade"].map(grade_map).fillna(0.0)
    work["QP"] = work["Points"] * pd.to_numeric(work["Credits"], errors="coerce").fillna(0.0)
    total_credits = pd.to_numeric(work["Credits"], errors="coerce").fillna(0.0).sum()
    if total_credits <= 0:
        return 0.0
    return (work["QP"].sum()) / total_credits


# -----------------------------
# Sidebar: grade scale + CSV
# -----------------------------
st.sidebar.title("⚙️ Cài đặt")
scale_name = st.sidebar.selectbox("Thang điểm", list(PRESET_SCALES.keys()) + ["Tùy chỉnh…"], index=0)

if scale_name == "Tùy chỉnh…":
    st.sidebar.caption("Nhập bảng quy đổi điểm chữ sang điểm số.")
    if "custom_scale" not in st.session_state:
        st.session_state.custom_scale = pd.DataFrame({"Grade": ["A", "B", "C", "D", "F"], "Point": [4.0, 3.0, 2.0, 1.0, 0.0]})
    
    st.session_state.custom_scale = st.sidebar.data_editor(
        st.session_state.custom_scale,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        column_config={
            "Grade": st.column_config.TextColumn("Điểm chữ", required=True),
            "Point": st.column_config.NumberColumn("Điểm số", required=True),
        }
    )
    grade_map = {r.Grade: float(r.Point) for r in st.session_state.custom_scale.itertuples(index=False) if pd.notna(r.Grade) and pd.notna(r.Point)}
else:
    grade_map = PRESET_SCALES[scale_name]

st.sidebar.divider()
st.sidebar.subheader("📁 Nhập / Xuất File")
upload = st.sidebar.file_uploader("Nhập file CSV (Course, Credits, Grade)", type=["csv"])

# -----------------------------
# Main UI
# -----------------------------
st.title("🧮 Công cụ tính điểm GPA & CGPA")
st.write(
    "Nhập các môn học theo từng học kỳ (Semester). Với mỗi môn, hãy nhập **Số tín chỉ (Credits)** và chọn **Điểm chữ (Grade)**."
)

# Number of semesters
n_sem = st.number_input("Số học kỳ (semesters)", min_value=1, max_value=20, value=2, step=1)

# Session storage for each semester dataframe
if "sems" not in st.session_state:
    st.session_state.sems: List[pd.DataFrame] = [DEFAULT_TEMPLATE.copy() for _ in range(n_sem)]

# Adjust list size when user changes n_sem
if len(st.session_state.sems) < n_sem:
    st.session_state.sems += [DEFAULT_TEMPLATE.copy() for _ in range(n_sem - len(st.session_state.sems))]
elif len(st.session_state.sems) > n_sem:
    st.session_state.sems = st.session_state.sems[:n_sem]

# If CSV uploaded, load into the *first* semester (tab 1)
if upload is not None:
    try:
        df_up = pd.read_csv(upload)
        needed = {"Course", "Credits", "Grade"}
        if not needed.issubset(df_up.columns):
            st.warning("File CSV phải có các cột: Course, Credits, Grade")
        else:
            st.session_state.sems[0] = df_up[list(needed)]
            st.success("Đã nhập dữ liệu vào Học kỳ 1")
    except Exception as e:
        st.error(f"Không thể đọc file CSV: {e}")

# Tabs for semesters
sem_tabs = st.tabs([f"Học kỳ {i+1}" for i in range(n_sem)])

per_sem_gpa: List[float] = []
per_sem_cred: List[float] = []

for i, tab in enumerate(sem_tabs):
    with tab:
        cols = st.columns([0.8, 0.2])
        with cols[0]:
            st.write(f"### Bảng điểm Học kỳ {i+1}")
        with cols[1]:
            if st.button("Reset học kỳ này", key=f"reset_{i}", use_container_width=True):
                st.session_state.sems[i] = DEFAULT_TEMPLATE.copy()
                st.rerun()

        # Build options for grade select
        grade_options = list(grade_map.keys())
        if not grade_options:
            st.warning("Chưa có thang điểm. Vui lòng tạo ở thanh Cài đặt bên trái.")
            grade_options = ["..."]
        
        # SỬA LỖI: Loại bỏ widget "Thêm dòng" và logic liên quan
        # Giờ đây việc thêm/xóa hàng được thực hiện trực tiếp trên data_editor
        edited = st.data_editor(
            st.session_state.sems[i],
            num_rows="dynamic", # Cho phép thêm/xóa hàng
            hide_index=True,
            use_container_width=True,
            column_config={
                "Course": st.column_config.TextColumn("Tên môn học", width="large", required=True),
                "Credits": st.column_config.NumberColumn("Số tín chỉ", min_value=0.0, step=0.5, required=True),
                "Grade": st.column_config.SelectboxColumn("Điểm chữ", options=grade_options, required=True),
            },
            key=f"editor_{i}",
        )
        st.session_state.sems[i] = edited

        gpa = calc_gpa(edited, grade_map)
        per_sem_gpa.append(gpa)
        creds = pd.to_numeric(edited["Credits"], errors="coerce").fillna(0.0).sum()
        per_sem_cred.append(float(creds))

        m1, m2 = st.columns(2)
        m1.metric("GPA học kỳ (SGPA)", f"{gpa:.3f}")
        m2.metric("Tổng tín chỉ học kỳ", f"{creds:.2f}")

        st.download_button(
            label="⬇️ Tải file CSV của học kỳ này",
            data=to_csv(edited),
            file_name=f"hoc_ky_{i+1}.csv",
            mime="text/csv",
            key=f"dl_{i}",
        )

# Overall CGPA
all_qp = 0.0
all_cred = 0.0
for df in st.session_state.sems:
    work = df.copy()
    work["Points"] = work["Grade"].map(grade_map).fillna(0.0)
    work["QP"
