import streamlit as st
import pandas as pd
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="Hệ thống Tư vấn Học tập", page_icon="🎓", layout="wide")

# -----------------------------
# DỮ LIỆU CẤU HÌNH & HẰNG SỐ
# -----------------------------
PRESET_SCALES: Dict[str, Dict[str, float]] = {
    "VN 4.0 (TLU)": {"A": 4.0, "B": 3.0, "C": 2.0, "D": 1.0, "F": 0.0},
    "Simple 10-point": {str(k): float(k) for k in range(10, -1, -1)},
    "US 4.0 (with +/-)": {"A+": 4.0, "A": 4.0, "A-": 3.7, "B+": 3.3, "B": 3.0, "B-": 2.7, "C+": 2.3, "C": 2.0, "C-": 1.7, "D+": 1.3, "D": 1.0, "D-": 0.7, "F": 0.0},
}

# NÂNG CẤP: Dữ liệu được trích xuất từ hình ảnh chương trình đào tạo
DEFAULT_COURSE_CATEGORIES = [
    "Lý luận chính trị",
    "Kỹ năng",
    "Ngoại ngữ",
    "Khoa học tự nhiên và tin học",
    "Giáo dục quốc phòng an ninh",
    "Giáo dục thể chất",
    "Kiến thức cơ sở khối ngành",
    "Kiến thức cơ sở ngành",
    "Kiến thức ngành",
    "Kiến thức tự chọn",
    "Thực tập và học phần tốt nghiệp",
    "Môn học điều kiện", # Mặc dù 0 TC nhưng vẫn là một loại
    "Chuẩn đầu ra" # Mặc dù 3 TC nhưng có thể là môn đặc biệt
]

GRADUATION_REQUIREMENTS = {
    # Các khối kiến thức có tín chỉ
    "Lý luận chính trị": 13,
    "Kỹ năng": 3,
    "Ngoại ngữ": 6,
    "Khoa học tự nhiên và tin học": 21,
    "Giáo dục quốc phòng an ninh": 11,
    "Giáo dục thể chất": 34,
    "Kiến thức cơ sở khối ngành": 31,
    "Kiến thức cơ sở ngành": 22,
    "Kiến thức ngành": 39,
    "Kiến thức tự chọn": 27,
    "Thực tập và học phần tốt nghiệp": 13,
    # Tổng tín chỉ được tính tự động từ các mục trên
}
# Tính toán tổng tín chỉ yêu cầu
total_required_credits = sum(GRADUATION_REQUIREMENTS.values())
GRADUATION_REQUIREMENTS["Tổng tín chỉ tích lũy"] = total_required_credits


DEFAULT_TEMPLATE = pd.DataFrame([
    {"Course": "Môn học 1", "Credits": 3.0, "Grade": "A", "Category": "Kiến thức ngành"},
    {"Course": "Môn học 2", "Credits": 3.0, "Grade": "B", "Category": "Khoa học tự nhiên và tin học"},
])

# -----------------------------
# CÁC HÀM TIỆN ÍCH (Giữ nguyên)
# -----------------------------
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

# -----------------------------
# SIDEBAR (Giữ nguyên)
# -----------------------------
st.sidebar.title("⚙️ Cài đặt")
scale_name = st.sidebar.selectbox("Thang điểm", list(PRESET_SCALES.keys()) + ["Tùy chỉnh…"], index=0)
if scale_name == "Tùy chỉnh…":
    st.sidebar.caption("Nhập bảng quy đổi điểm chữ sang điểm số.")
    if "custom_scale" not in st.session_state: st.session_state.custom_scale = pd.DataFrame({"Grade": ["A", "B", "C", "D", "F"], "Point": [4.0, 3.0, 2.0, 1.0, 0.0]})
    st.session_state.custom_scale = st.sidebar.data_editor(st.session_state.custom_scale, num_rows="dynamic", use_container_width=True, hide_index=True, column_config={"Grade": st.column_config.TextColumn("Điểm chữ", required=True), "Point": st.column_config.NumberColumn("Điểm số", required=True)})
    grade_map = {r.Grade: float(r.Point) for r in st.session_state.custom_scale.itertuples(index=False) if pd.notna(r.Grade) and pd.notna(r.Point)}
else: grade_map = PRESET_SCALES[scale_name]
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
if upload is not None and not st.session_state.get('file_processed', False):
    try:
        df_up = pd.read_csv(upload, encoding='utf-8')
        needed = {"Course", "Credits", "Grade", "Semester", "Category"}
        if not needed.issubset(df_up.columns): st.warning("File CSV phải có các cột: Course, Credits, Grade, Semester, Category")
        else:
            df_up["Semester"] = pd.to_numeric(df_up["Semester"], errors="coerce").fillna(1).astype(int)
            max_sem = df_up["Semester"].max()
            st.session_state.n_sem_input = max_sem
            new_sems = []
            for i in range(1, max_sem + 1):
                sem_df = df_up[df_up["Semester"] == i][["Course", "Credits", "Grade", "Category"]].reset_index(drop=True)
                if sem_df.empty: sem_df = pd.DataFrame(columns=["Course", "Credits", "Grade", "Category"])
                new_sems.append(sem_df)
            st.session_state.sems = new_sems
            st.session_state.file_processed = True
            st.success(f"Đã nhập và phân bổ dữ liệu cho {max_sem} học kỳ.")
            st.rerun()
    except Exception as e: st.error(f"Không thể đọc file CSV: {e}"); st.session_state.file_processed = True

st.header("📊 Bảng tổng quan Tiến độ Tốt nghiệp")
if "sems" in st.session_state:
    progress_df = calculate_progress(st.session_state.sems, GRADUATION_REQUIREMENTS, grade_map)
    if not progress_df.empty:
        total_progress = progress_df.iloc[0]
        st.subheader(f"Tổng quan: {total_progress['Đã hoàn thành']:.0f} / {total_progress['Yêu cầu']:.0f} tín chỉ đã tích lũy")
        st.progress(total_progress['Tiến độ'], text=f"{total_progress['Tiến độ']:.1%}")
        st.markdown("---")
        detail_df = progress_df[progress_df['Yêu cầu'] > 0].iloc[1:].reset_index(drop=True)
        if not detail_df.empty:
            st.subheader("Chi tiết theo khối kiến thức")
            # NÂNG CẤP: Chia thành 2 cột để hiển thị gọn gàng
            left_col, right_col = st.columns(2)
            for i, row in detail_df.iterrows():
                target_col = left_col if i % 2 == 0 else right_col
                with target_col:
                    st.metric(label=str(row["Yêu cầu"]), value=f"{row['Đã hoàn thành']:.0f} / {row['Yêu cầu']:.0f}", delta=f"Còn lại: {row['Còn lại']:.0f}", delta_color="inverse")
                    st.progress(row['Tiến độ'])
    else: st.info("Chưa có dữ liệu để phân tích tiến độ.")
st.divider()

n_sem = st.number_input("Số học kỳ (semesters)", min_value=1, max_value=20, value=st.session_state.get('n_sem_input', 8), step=1, key="n_sem_input")
if "sems" not in st.session_state or len(st.session_state.sems) != n_sem:
    current_sems = st.session_state.get("sems", [])
    current_len = len(current_sems)
    if current_len < n_sem: current_sems += [DEFAULT_TEMPLATE.copy() for _ in range(n_sem - current_len)]
    else: current_sems = current_sems[:n_sem]
    st.session_state.sems = current_sems
    st.rerun()

sem_tabs = st.tabs([f"Học kỳ {i+1}" for i in range(n_sem)])
per_sem_gpa, per_sem_cred, warning_history = [], [], []
cumulative_f_credits, previous_warning_level = 0.0, 0
fail_grades = [grade for grade, point in grade_map.items() if point == 0.0]

for i, tab in enumerate(sem_tabs):
    with tab:
        st.write(f"### Bảng điểm Học kỳ {i+1}")
        df_with_delete = st.session_state.sems[i].copy(); df_with_delete.insert(0, "Xóa", False)
        cols_action = st.columns([0.7, 0.15, 0.15]);
        with cols_action[1]:
            if st.button("🗑️ Xóa môn đã chọn", key=f"delete_{i}", use_container_width=True):
                edited_df_state = st.session_state[f"editor_{i}"]
                rows_to_keep = [row for _, row in edited_df_state.iterrows() if not row["Xóa"]]
                st.session_state.sems[i] = pd.DataFrame(rows_to_keep).drop(columns=["Xóa"]); st.rerun()
        with cols_action[2]:
            if st.button("🔄 Reset học kỳ", key=f"reset_{i}", use_container_width=True):
                st.session_state.sems[i] = DEFAULT_TEMPLATE.copy(); st.rerun()
        grade_options = list(grade_map.keys())
        if not grade_options: st.warning("Chưa có thang điểm."); grade_options = ["..."]
        edited = st.data_editor(df_with_delete, num_rows="dynamic", hide_index=True, use_container_width=True,
            column_config={
                "Xóa": st.column_config.CheckboxColumn(width="small"), "Course": st.column_config.TextColumn("Tên môn học", width="large", required=True),
                "Credits": st.column_config.NumberColumn("Số tín chỉ", min_value=0.0, step=0.5, required=True),
                "Grade": st.column_config.SelectboxColumn("Điểm chữ", options=grade_options, required=True),
                "Category": st.column_config.SelectboxColumn("Phân loại", options=DEFAULT_COURSE_CATEGORIES, required=True)
            }, key=f"editor_{i}")
        st.session_state.sems[i] = edited.drop(columns=["Xóa"])

        current_sem_df = st.session_state.sems[i]
        gpa = calc_gpa(current_sem_df, grade_map); per_sem_gpa.append(gpa)
        creds = pd.to_numeric(current_sem_df["Credits"], errors="coerce").fillna(0.0).sum(); per_sem_cred.append(float(creds))
        current_f_credits = pd.to_numeric(current_sem_df[current_sem_df["Grade"].isin(fail_grades)]["Credits"], errors="coerce").fillna(0.0).sum()
        cumulative_f_credits += current_f_credits
        warning_level, msg, reasons = check_academic_warning(i + 1, gpa, cumulative_f_credits, previous_warning_level)
        warning_history.append({"Học kỳ": i + 1, "Mức Cảnh báo": warning_level, "Lý do": ", ".join(reasons) if reasons else "Không có"})
        m1, m2, m3 = st.columns(3)
        m1.metric("GPA học kỳ (SGPA)", f"{gpa:.3f}"); m2.metric("Tổng tín chỉ học kỳ", f"{creds:.2f}"); m3.metric("Tín chỉ nợ tích lũy", f"{cumulative_f_credits:.2f}")
        st.divider()
        if warning_level > 0: st.warning(f"**{msg}**\n\n*Lý do: {' & '.join(reasons)}*")
        else: st.success(f"**✅ {msg}**")
        previous_warning_level = warning_level

all_passed_dfs = [df[~df["Grade"].isin(fail_grades)] for df in st.session_state.sems]
master_passed_df = pd.concat(all_passed_dfs) if all_passed_dfs else pd.DataFrame()
cgpa = calc_gpa(master_passed_df, grade_map)
total_passed_credits = pd.to_numeric(master_passed_df['Credits'], errors='coerce').fillna(0).sum()

st.divider()
colA, colB, colC = st.columns([1, 1, 2])
colA.metric("🎯 GPA Tích lũy (CGPA)", f"{cgpa:.3f}")
colB.metric("📚 Tổng tín chỉ đã qua", f"{total_passed_credits:.2f}")

with colC:
    if per_sem_gpa and all(c >= 0 for c in per_sem_cred):
        try:
            fig, ax = plt.subplots(); x = np.arange(1, len(per_sem_gpa) + 1)
            ax.plot(x, per_sem_gpa, marker="o", linestyle="-", color='b')
            ax.set_xlabel("Học kỳ"); ax.set_ylabel("GPA (SGPA)"); ax.set_title("Xu hướng GPA theo học kỳ")
            ax.set_xticks(x); ax.grid(True, linestyle=":", linewidth=0.5)
            ax.set_ylim(bottom=0, top=max(4.1, max(per_sem_gpa) * 1.1 if per_sem_gpa and any(v > 0 for v in per_sem_gpa) else 4.1))
            st.pyplot(fig, use_container_width=True)
        except Exception: st.info("Chưa đủ dữ liệu để vẽ biểu đồ.")

with st.expander("❓ Hướng dẫn, Cách tính & Lịch sử cảnh báo"):
    st.markdown("##### Hướng dẫn sử dụng")
    st.markdown("""
- **Nhập/Xuất file:** File CSV phải có các cột: `Course`, `Credits`, `Grade`, `Semester`, `Category`.
- **Thêm/xóa môn học:** Dùng nút `+` để thêm và tick vào ô "Xóa" rồi nhấn nút "🗑️ Xóa môn đã chọn" để xóa.
""")
    st.markdown("---")
    st.markdown("##### Lịch sử cảnh báo học tập")
    st.dataframe(pd.DataFrame(warning
