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
    "VN 4.0 (TLU)": {"A": 4.0, "B": 3.0, "C": 2.0, "D": 1.0, "F": 0.0},
    "Simple 10-point": {str(k): float(k) for k in range(10, -1, -1)},
    "US 4.0 (with +/-)": {"A+": 4.0, "A": 4.0, "A-": 3.7, "B+": 3.3, "B": 3.0, "B-": 2.7, "C+": 2.3, "C": 2.0, "C-": 1.7, "D+": 1.3, "D": 1.0, "D-": 0.7, "F": 0.0},
}

DEFAULT_TEMPLATE = pd.DataFrame([
    {"Course": "Course 1", "Credits": 3.0, "Grade": list(PRESET_SCALES["VN 4.0 (TLU)"].keys())[0]},
    {"Course": "Course 2", "Credits": 3.0, "Grade": list(PRESET_SCALES["VN 4.0 (TLU)"].keys())[2]},
])

@st.cache_data
def to_csv(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")

def calc_gpa(df: pd.DataFrame, grade_map: Dict[str, float]) -> float:
    if df.empty: return 0.0
    work = df.copy()
    work["Points"] = work["Grade"].map(grade_map).fillna(0.0)
    work["QP"] = work["Points"] * pd.to_numeric(work["Credits"], errors="coerce").fillna(0.0)
    total_credits = pd.to_numeric(work["Credits"], errors="coerce").fillna(0.0).sum()
    if total_credits <= 0: return 0.0
    return (work["QP"].sum()) / total_credits

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.title("⚙️ Cài đặt")
scale_name = st.sidebar.selectbox("Thang điểm", list(PRESET_SCALES.keys()) + ["Tùy chỉnh…"], index=0)

if scale_name == "Tùy chỉnh…":
    st.sidebar.caption("Nhập bảng quy đổi điểm chữ sang điểm số.")
    if "custom_scale" not in st.session_state:
        st.session_state.custom_scale = pd.DataFrame({"Grade": ["A", "B", "C", "D", "F"], "Point": [4.0, 3.0, 2.0, 1.0, 0.0]})
    st.session_state.custom_scale = st.sidebar.data_editor(st.session_state.custom_scale, num_rows="dynamic", use_container_width=True, hide_index=True, column_config={"Grade": st.column_config.TextColumn("Điểm chữ", required=True), "Point": st.column_config.NumberColumn("Điểm số", required=True)})
    grade_map = {r.Grade: float(r.Point) for r in st.session_state.custom_scale.itertuples(index=False) if pd.notna(r.Grade) and pd.notna(r.Point)}
else:
    grade_map = PRESET_SCALES[scale_name]

st.sidebar.divider()
st.sidebar.subheader("📁 Nhập / Xuất File")

# NÂNG CẤP: Nút xuất toàn bộ dữ liệu
if st.sidebar.button("⬇️ Xuất toàn bộ dữ liệu (CSV)"):
    all_dfs = []
    for i, df in enumerate(st.session_state.get("sems", [])):
        df_copy = df.copy()
        df_copy["Semester"] = i + 1
        all_dfs.append(df_copy)
    if all_dfs:
        master_df = pd.concat(all_dfs, ignore_index=True)
        csv_data = to_csv(master_df)
        st.sidebar.download_button(
            label="Tải về file tổng hợp",
            data=csv_data,
            file_name="GPA_data_all_semesters.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.sidebar.warning("Chưa có dữ liệu để xuất.")

upload = st.sidebar.file_uploader("Nhập file CSV (có cột Semester)", type=["csv"], key="uploader")

# -----------------------------
# Main UI
# -----------------------------
st.title("🧮 Công cụ tính điểm GPA & CGPA")
st.write("Nhập các môn học theo từng học kỳ. Với mỗi môn, hãy nhập **Số tín chỉ (Credits)** và chọn **Điểm chữ (Grade)**.")

# NÂNG CẤP: Logic nhập file tổng hợp
if upload is not None:
    try:
        df_up = pd.read_csv(upload)
        needed = {"Course", "Credits", "Grade", "Semester"}
        if not needed.issubset(df_up.columns):
            st.warning("File CSV phải có các cột: Course, Credits, Grade, Semester")
        else:
            df_up["Semester"] = pd.to_numeric(df_up["Semester"], errors="coerce").fillna(1).astype(int)
            max_sem = df_up["Semester"].max()
            st.session_state.n_sem = max_sem
            
            new_sems = []
            for i in range(1, max_sem + 1):
                sem_df = df_up[df_up["Semester"] == i][["Course", "Credits", "Grade"]].reset_index(drop=True)
                new_sems.append(sem_df)
            
            st.session_state.sems = new_sems
            st.success(f"Đã nhập và phân bổ dữ liệu cho {max_sem} học kỳ.")
            # Xóa file đã upload khỏi state để tránh lặp lại logic
            st.session_state.uploader = None
            st.rerun()

    except Exception as e:
        st.error(f"Không thể đọc file CSV: {e}")


# Number of semesters
n_sem = st.number_input("Số học kỳ (semesters)", min_value=1, max_value=20, value=st.session_state.get('n_sem', 2), step=1, key="n_sem_input")
st.session_state.n_sem = n_sem

# Session storage for each semester dataframe
if "sems" not in st.session_state:
    st.session_state.sems: List[pd.DataFrame] = [DEFAULT_TEMPLATE.copy() for _ in range(n_sem)]

# Adjust list size when user changes n_sem
if len(st.session_state.sems) != n_sem:
    current_len = len(st.session_state.sems)
    if current_len < n_sem:
        st.session_state.sems += [DEFAULT_TEMPLATE.copy() for _ in range(n_sem - current_len)]
    else:
        st.session_state.sems = st.session_state.sems[:n_sem]
    st.rerun()

# Tabs for semesters
sem_tabs = st.tabs([f"Học kỳ {i+1}" for i in range(n_sem)])

per_sem_gpa: List[float] = []
per_sem_cred: List[float] = []

for i, tab in enumerate(sem_tabs):
    with tab:
        st.write(f"### Bảng điểm Học kỳ {i+1}")

        # NÂNG CẤP: Logic nút xóa môn học
        df_with_delete = st.session_state.sems[i].copy()
        df_with_delete.insert(0, "Xóa", False)
        
        cols_action = st.columns([0.7, 0.15, 0.15])
        with cols_action[1]:
            if st.button("🗑️ Xóa môn đã chọn", key=f"delete_{i}", use_container_width=True):
                # Lấy lại trạng thái mới nhất của các checkbox từ key của data_editor
                edited_df_state = st.session_state[f"editor_{i}"]
                rows_to_keep = [row for idx, row in edited_df_state.iterrows() if not row["Xóa"]]
                st.session_state.sems[i] = pd.DataFrame(rows_to_keep).drop(columns=["Xóa"])
                st.rerun()
        with cols_action[2]:
            if st.button("🔄 Reset học kỳ", key=f"reset_{i}", use_container_width=True):
                st.session_state.sems[i] = DEFAULT_TEMPLATE.copy()
                st.rerun()

        grade_options = list(grade_map.keys())
        if not grade_options:
            st.warning("Chưa có thang điểm. Vui lòng tạo ở thanh Cài đặt bên trái.")
            grade_options = ["..."]
        
        edited = st.data_editor(
            df_with_delete,
            num_rows="dynamic",
            hide_index=True,
            use_container_width=True,
            column_config={
                "Xóa": st.column_config.CheckboxColumn(width="small"),
                "Course": st.column_config.TextColumn("Tên môn học", width="large", required=True),
                "Credits": st.column_config.NumberColumn("Số tín chỉ", min_value=0.0, step=0.5, required=True),
                "Grade": st.column_config.SelectboxColumn("Điểm chữ", options=grade_options, required=True),
            },
            key=f"editor_{i}",
        )
        # Lưu trạng thái chỉnh sửa nhưng không lưu cột "Xóa" vào state chính
        st.session_state.sems[i] = edited.drop(columns=["Xóa"])

        gpa = calc_gpa(st.session_state.sems[i], grade_map)
        per_sem_gpa.append(gpa)
        creds = pd.to_numeric(st.session_state.sems[i]["Credits"], errors="coerce").fillna(0.0).sum()
        per_sem_cred.append(float(creds))

        m1, m2 = st.columns(2)
        m1.metric("GPA học kỳ (SGPA)", f"{gpa:.3f}")
        m2.metric("Tổng tín chỉ học kỳ", f"{creds:.2f}")

# Overall CGPA
all_qp = 0.0
all_cred = 0.0
for df in st.session_state.sems:
    work = df.copy()
    work["Points"] = work["Grade"].map(grade_map).fillna(0.0)
    work["QP"] = work["Points"] * pd.to_numeric(work["Credits"], errors="coerce").fillna(0.0)
    all_qp += work["QP"].sum()
    all_cred += pd.to_numeric(work["Credits"], errors="coerce").fillna(0.0).sum()

cgpa = (all_qp / all_cred) if all_cred > 0 else 0.0
st.divider()
colA, colB, colC = st.columns([1, 1, 2])
colA.metric("🎯 GPA Tích lũy (CGPA)", f"{cgpa:.3f}")
colB.metric("📚 Tổng tín chỉ tích lũy", f"{all_cred:.2f}")

# Trend chart
with colC:
    if per_sem_gpa and all(c >= 0 for c in per_sem_cred):
        try:
            fig, ax = plt.subplots()
            x = np.arange(1, len(per_sem_gpa) + 1)
            ax.plot(x, per_sem_gpa, marker="o", linestyle="-", color='b')
            ax.set_xlabel("Học kỳ"); ax.set_ylabel("GPA (SGPA)"); ax.set_title("Xu hướng GPA theo học kỳ")
            ax.set_xticks(x); ax.grid(True, linestyle=":", linewidth=0.5)
            ax.set_ylim(bottom=0, top=max(4.1, max(per_sem_gpa) * 1.1 if per_sem_gpa and max(per_sem_gpa) > 0 else 4.1))
            st.pyplot(fig, use_container_width=True)
        except Exception: st.info("Chưa đủ dữ liệu để vẽ biểu đồ.")

# Expander sections
with st.expander("📏 Xem bảng quy đổi điểm đang sử dụng"):
    st.dataframe(pd.DataFrame({"Điểm chữ (Grade)": list(grade_map.keys()), "Điểm số (Point)": list(grade_map.values())}), hide_index=True)

with st.expander("❓ Hướng dẫn & Cách tính"):
    st.markdown("""
- **Nhập/Xuất file:**
    - **Nhập:** Dùng nút "Nhập file CSV" ở thanh bên. File phải có các cột: `Course`, `Credits`, `Grade`, `Semester`.
    - **Xuất:** Dùng nút "Xuất toàn bộ dữ liệu (CSV)" để lưu lại toàn bộ tiến trình học tập của bạn.
- **Cách thêm/xóa môn học:**
    - **Thêm:** Nhấn vào nút `+` ở góc dưới cùng bên trái của bảng điểm.
    - **Xóa:** Tick vào ô "Xóa" ở đầu hàng của các môn muốn loại bỏ, sau đó nhấn nút "🗑️ Xóa môn đã chọn".
- **SGPA (Semester GPA)** = Tổng ( *Điểm số* × *Số tín chỉ* ) / Tổng *Số tín chỉ* của học kỳ đó.
- **CGPA (Cumulative GPA)** = Tổng tất cả *Quality Points* / Tổng tất cả *Số tín chỉ* qua các học kỳ.
""")
