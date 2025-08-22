import streamlit as st
import pandas as pd
from typing import Dict, List

st.set_page_config(page_title="CGPA Calculator", page_icon="🧮", layout="wide")

# -----------------------------
# Helpers
# -----------------------------
PRESET_SCALES: Dict[str, Dict[str, float]] = {
    "US 4.0 (with +/-)": {
        "A+": 4.0, "A": 4.0, "A-": 3.7,
        "B+": 3.3, "B": 3.0, "B-": 2.7,
        "C+": 2.3, "C": 2.0, "C-": 1.7,
        "D+": 1.3, "D": 1.0, "D-": 0.7,
        "F": 0.0,
    },
    "India UGC 10-point": {
        "O": 10, "A+": 9, "A": 8, "B+": 7, "B": 6, "C": 5, "P": 4, "F": 0,
    },
    "Simple 10-point": {str(k): float(k) for k in range(10, -1, -1)},
    "VN 4.0 (tham khảo)": {  # Tham khảo phổ biến ở VN (có thể chỉnh lại ở Custom)
        "A": 4.0, "B+": 3.5, "B": 3.0, "C+": 2.5, "C": 2.0, "D+": 1.5, "D": 1.0, "F": 0.0,
    },
}

DEFAULT_TEMPLATE = pd.DataFrame(
    [
        {"Course": "Course 1", "Credits": 3.0, "Grade": list(PRESET_SCALES["US 4.0 (with +/-)"].keys())[0]},
        {"Course": "Course 2", "Credits": 3.0, "Grade": list(PRESET_SCALES["US 4.0 (with +/-)"].keys())[3]},
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
st.sidebar.title("⚙️ Settings")
scale_name = st.sidebar.selectbox("Grading scale", list(PRESET_SCALES.keys()) + ["Custom…"], index=0)

if scale_name == "Custom…":
    st.sidebar.caption("Nhập bảng quy đổi điểm -> thang điểm (có thể là 4.0 hoặc 10 tuỳ bạn)")
    if "custom_scale" not in st.session_state:
        st.session_state.custom_scale = pd.DataFrame({"Grade": ["A", "B", "C", "D", "F"], "Point": [4, 3, 2, 1, 0]})
    st.session_state.custom_scale = st.sidebar.data_editor(
        st.session_state.custom_scale,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
    )
    grade_map = {r.Grade: float(r.Point) for r in st.session_state.custom_scale.itertuples(index=False) if pd.notna(r.Grade)}
else:
    grade_map = PRESET_SCALES[scale_name]

st.sidebar.divider()
st.sidebar.subheader("📁 Import / Export")
upload = st.sidebar.file_uploader("Import CSV (Course, Credits, Grade)", type=["csv"])

# -----------------------------
# Main UI
# -----------------------------
st.title("🧮 CGPA Calculator")
st.write(
    "Nhập các môn học theo từng học kỳ (Semester). Ứng với mỗi môn, chọn **Grade** và **Credits**.\n\n"
    "- GPA (SGPA) học kỳ = Σ(điểm quy đổi × tín chỉ) / Σ tín chỉ.\n\n"
    "- CGPA toàn khóa = Tổng tất cả Quality Points / Tổng tín chỉ.")

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

# If CSV uploaded, load into the *current* semester (tab 1)
if upload is not None:
    try:
        df_up = pd.read_csv(upload)
        needed = {"Course", "Credits", "Grade"}
        if not needed.issubset(df_up.columns):
            st.warning("CSV phải có các cột: Course, Credits, Grade")
        else:
            st.session_state.sems[0] = df_up[list(needed)]
            st.success("Đã nhập dữ liệu vào Semester 1")
    except Exception as e:
        st.error(f"Không đọc được CSV: {e}")

# Tabs for semesters
sem_tabs = st.tabs([f"Semester {i+1}" for i in range(n_sem)])

per_sem_gpa: List[float] = []
per_sem_cred: List[float] = []

for i, tab in enumerate(sem_tabs):
    with tab:
        st.write(f"### Semester {i+1}")
        # Build options for grade select
        grade_options = list(grade_map.keys())
        if len(grade_options) == 0:
            st.warning("Chưa có bảng quy đổi điểm (grade map). Hãy tạo ở Sidebar.")
            grade_options = ["F"]
        cols = st.columns([2, 1, 1])
        with cols[0]:
            st.caption("Bảng môn học")
        with cols[1]:
            add_rows = st.number_input("Thêm dòng", min_value=0, max_value=20, value=0, key=f"add_{i}")
        with cols[2]:
            if st.button("Reset học kỳ này", key=f"reset_{i}"):
                st.session_state.sems[i] = DEFAULT_TEMPLATE.copy()
        if add_rows:
            add_df = pd.DataFrame([{"Course": f"Course {len(st.session_state.sems[i])+k+1}", "Credits": 3.0, "Grade": grade_options[0]} for k in range(add_rows)])
            st.session_state.sems[i] = pd.concat([st.session_state.sems[i], add_df], ignore_index=True)

        edited = st.data_editor(
            st.session_state.sems[i],
            num_rows="dynamic",
            hide_index=True,
            use_container_width=True,
            column_config={
                "Course": st.column_config.TextColumn("Course", width="medium"),
                "Credits": st.column_config.NumberColumn("Credits", min_value=0.0, step=0.5),
                "Grade": st.column_config.SelectboxColumn("Grade", options=grade_options),
            },
            key=f"editor_{i}",
        )
        st.session_state.sems[i] = edited

        gpa = calc_gpa(edited, grade_map)
        per_sem_gpa.append(gpa)
        creds = pd.to_numeric(edited["Credits"], errors="coerce").fillna(0.0).sum()
        per_sem_cred.append(float(creds))

        m1, m2 = st.columns(2)
        m1.metric("SGPA (Semester GPA)", f"{gpa:.3f}")
        m2.metric("Tổng tín chỉ học kỳ", f"{creds:.2f}")

        st.download_button(
            label="⬇️ Tải CSV học kỳ này",
            data=to_csv(edited),
            file_name=f"semester_{i+1}.csv",
            mime="text/csv",
            key=f"dl_{i}",
        )

# Overall CGPA
all_qp = 0.0
all_cred = 0.0
for i in range(n_sem):
    df = st.session_state.sems[i]
    df = df.copy()
    df["Points"] = df["Grade"].map(grade_map).fillna(0.0)
    df["QP"] = df["Points"] * pd.to_numeric(df["Credits"], errors="coerce").fillna(0.0)
    all_qp += df["QP"].sum()
    all_cred += pd.to_numeric(df["Credits"], errors="coerce").fillna(0.0).sum()

cgpa = (all_qp / all_cred) if all_cred > 0 else 0.0
st.divider()
colA, colB, colC = st.columns([1,1,2])
colA.metric("🎯 CGPA", f"{cgpa:.3f}")
colB.metric("📚 Tổng tín chỉ", f"{all_cred:.2f}")

# Trend chart
try:
    import matplotlib.pyplot as plt
    import numpy as np
    fig, ax = plt.subplots()
    x = np.arange(1, len(per_sem_gpa)+1)
    ax.plot(x, per_sem_gpa, marker="o")
    ax.set_xlabel("Semester")
    ax.set_ylabel("SGPA")
    ax.set_title("Xu hướng SGPA theo học kỳ")
    ax.grid(True, linestyle=":", linewidth=0.5)
    colC.pyplot(fig, use_container_width=True)
except Exception as e:
    st.info("Không thể vẽ biểu đồ: " + str(e))

# Legend for scale
with st.expander("📏 Bảng quy đổi đang dùng"):
    st.write(pd.DataFrame({"Grade": list(grade_map.keys()), "Point": list(grade_map.values())}))

with st.expander("❓Cách tính & ghi chú"):
    st.markdown(
        """
        - **SGPA (Semester GPA)** = Tổng( *Point* × *Credits* ) / Tổng *Credits* của học kỳ đó.\\
        - **CGPA** = Tổng tất cả *Quality Points* / Tổng tất cả *Credits* qua các học kỳ.\\
        - Bạn có thể chuyển đổi/thêm các mức **Grade** ở thanh bên (Sidebar).\\
        - Hỗ trợ **Import/Export CSV** theo mẫu: `Course, Credits, Grade`.
        """
    )
