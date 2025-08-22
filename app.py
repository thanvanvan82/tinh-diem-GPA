import streamlit as st
import pandas as pd
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
import numpy as np
from fpdf import FPDF
import base64

st.set_page_config(page_title="Hệ thống Tư vấn Học tập", page_icon="🎓", layout="wide")

# -----------------------------
# DỮ LIỆU CẤU HÌNH & HẰNG SỐ
# -----------------------------
MAJORS_DATA = {
    "Công nghệ kỹ thuật xây dựng": {
        "course_categories": ["Lý luận chính trị", "Kỹ năng", "Ngoại ngữ", "Khoa học tự nhiên và tin học", "Giáo dục quốc phòng an ninh", "Giáo dục thể chất", "Kiến thức cơ sở khối ngành", "Kiến thức cơ sở ngành", "Kiến thức ngành", "Kiến thức tự chọn", "Thực tập và học phần tốt nghiệp", "Môn học điều kiện", "Chuẩn đầu ra"],
        "graduation_requirements": {"Lý luận chính trị": 13, "Kỹ năng": 3, "Ngoại ngữ": 6, "Khoa học tự nhiên và tin học": 21, "Giáo dục quốc phòng an ninh": 11, "Giáo dục thể chất": 34, "Kiến thức cơ sở khối ngành": 31, "Kiến thức cơ sở ngành": 22, "Kiến thức ngành": 39, "Kiến thức tự chọn": 27, "Thực tập và học phần tốt nghiệp": 13},
        # NÂNG CẤP: Thêm toàn bộ chương trình đào tạo để so sánh
        "full_curriculum": [
            # Dữ liệu này được tổng hợp từ file chương trình đào tạo và bảng điểm
            {'Course': 'Bóng chuyền 1', 'Credits': 1, 'Category': 'Giáo dục thể chất'}, {'Course': 'Bóng chuyền 2', 'Credits': 1, 'Category': 'Giáo dục thể chất'}, {'Course': 'Bóng rổ', 'Credits': 1, 'Category': 'Giáo dục thể chất'}, {'Course': 'Hóa học đại cương', 'Credits': 3, 'Category': 'Khoa học tự nhiên và tin học'}, {'Course': 'Cầu lông', 'Credits': 1, 'Category': 'Giáo dục thể chất'}, {'Course': 'Tin học cơ bản', 'Credits': 2, 'Category': 'Khoa học tự nhiên và tin học'}, {'Course': 'Giải tích hàm một biến', 'Credits': 3, 'Category': 'Khoa học tự nhiên và tin học'}, {'Course': 'Kỹ năng mềm và tinh thần khởi nghiệp', 'Credits': 3, 'Category': 'Kỹ năng'}, {'Course': 'Sức bền vật liệu 1', 'Credits': 3, 'Category': 'Kiến thức cơ sở ngành'}, {'Course': 'Vật liệu xây dựng', 'Credits': 3, 'Category': 'Kiến thức cơ sở ngành'}, {'Course': 'Sức bền vật liệu 2', 'Credits': 2, 'Category': 'Kiến thức cơ sở ngành'}, {'Course': 'Tiếng Anh 1', 'Credits': 3, 'Category': 'Ngoại ngữ'}, {'Course': 'Cơ học chất lỏng', 'Credits': 3, 'Category': 'Kiến thức cơ sở ngành'}, {'Course': 'Pháp luật đại cương', 'Credits': 2, 'Category': 'Lý luận chính trị'}, {'Course': 'Địa chất công trình', 'Credits': 2, 'Category': 'Kiến thức cơ sở khối ngành'}, {'Course': 'Triết học Mác - Lênin', 'Credits': 3, 'Category': 'Lý luận chính trị'}, {'Course': 'Vật lý 2', 'Credits': 3, 'Category': 'Khoa học tự nhiên và tin học'}, {'Course': 'Đồ họa kỹ thuật 1', 'Credits': 2, 'Category': 'Kiến thức cơ sở khối ngành'}, {'Course': 'Đồ họa kỹ thuật 2', 'Credits': 2, 'Category': 'Kiến thức cơ sở khối ngành'}, {'Course': 'Kỹ thuật điện', 'Credits': 3, 'Category': 'Kiến thức cơ sở khối ngành'}, {'Course': 'Nền móng', 'Credits': 2, 'Category': 'Kiến thức ngành'}, {'Course': 'Cơ học đất', 'Credits': 3, 'Category': 'Kiến thức ngành'}, {'Course': 'Tư tưởng Hồ Chí Minh', 'Credits': 2, 'Category': 'Lý luận chính trị'}, {'Course': 'Thủy lực công trình', 'Credits': 3, 'Category': 'Kiến thức ngành'}, {'Course': 'Thủy văn công trình', 'Credits': 3, 'Category': 'Kiến thức ngành'}, {'Course': 'Giải tích hàm nhiều biến', 'Credits': 3, 'Category': 'Khoa học tự nhiên và tin học'}, {'Course': 'Kinh tế chính trị Mác - Lênin', 'Credits': 2, 'Category': 'Lý luận chính trị'}, {'Course': 'Nhập môn ngành Công nghệ kỹ thuật xây dựng', 'Credits': 2, 'Category': 'Kiến thức cơ sở khối ngành'}, {'Course': 'Chủ nghĩa xã hội khoa học', 'Credits': 2, 'Category': 'Lý luận chính trị'}, {'Course': 'Thống kê trong kỹ thuật', 'Credits': 2, 'Category': 'Khoa học tự nhiên và tin học'}, {'Course': 'Trắc địa', 'Credits': 2, 'Category': 'Kiến thức cơ sở khối ngành'}, {'Course': 'Thực tập trắc địa', 'Credits': 1, 'Category': 'Kiến thức cơ sở khối ngành'}, {'Course': 'Kinh tế xây dựng 1', 'Credits': 2, 'Category': 'Kiến thức ngành'}, {'Course': 'Cơ sở thiết kế công trình dân dụng và công nghiệp', 'Credits': 2, 'Category': 'Kiến thức ngành'}, {'Course': 'Ứng dụng BIM trong xây dựng', 'Credits': 2, 'Category': 'Kiến thức ngành'}, {'Course': 'Công nghệ xây dựng công trình bê tông', 'Credits': 2, 'Category': 'Kiến thức ngành'}, {'Course': 'Công nghệ xây dựng công trình đất đá', 'Credits': 2, 'Category': 'Kiến thức ngành'}, {'Course': 'Công nghệ xử lý nền móng', 'Credits': 2, 'Category': 'Kiến thức ngành'}, {'Course': 'Quản lý đầu tư xây dựng', 'Credits': 3, 'Category': 'Kiến thức ngành'}, {'Course': 'An toàn xây dựng', 'Credits': 2, 'Category': 'Kiến thức ngành'}, {'Course': 'Tổ chức xây dựng', 'Credits': 2, 'Category': 'Kiến thức ngành'}, {'Course': 'Thi công công trình ngầm', 'Credits': 2, 'Category': 'Kiến thức ngành'}, {'Course': 'Lịch sử Đảng Cộng sản Việt Nam', 'Credits': 2, 'Category': 'Lý luận chính trị'}, {'Course': 'Máy xây dựng', 'Credits': 3, 'Category': 'Kiến thức ngành'}, {'Course': 'Giới thiệu và cơ sở thiết kế công trình thủy', 'Credits': 2, 'Category': 'Kiến thức ngành'}, {'Course': 'Thiết kế công trình cầu đường', 'Credits': 3, 'Category': 'Kiến thức ngành'}, {'Course': 'Thiết kế đê và công trình bảo vệ bờ sông', 'Credits': 2, 'Category': 'Kiến thức ngành'}, {'Course': 'Thực tập địa chất công trình', 'Credits': 1, 'Category': 'Kiến thức cơ sở khối ngành'}, {'Course': 'Thực tập kỹ thuật và tổ chức xây dựng', 'Credits': 3, 'Category': 'Thực tập và học phần tốt nghiệp'}, {'Course': 'Đồ án tổ chức xây dựng', 'Credits': 1, 'Category': 'Thực tập và học phần tốt nghiệp'}, {'Course': 'Đồ án công nghệ xây dựng công trình bê tông', 'Credits': 1, 'Category': 'Thực tập và học phần tốt nghiệp'}, {'Course': 'Đồ án công nghệ xây dựng công trình đất đá', 'Credits': 1, 'Category': 'Thực tập và học phần tốt nghiệp'}, {'Course': 'Dẫn dòng thi công và công tác hố móng', 'Credits': 2, 'Category': 'Kiến thức ngành'}, {'Course': 'Đồ án dẫn dòng thi công và công tác hố móng', 'Credits': 1, 'Category': 'Thực tập và học phần tốt nghiệp'}, {'Course': 'Giám sát chất lượng công trình', 'Credits': 3, 'Category': 'Kiến thức ngành'},
        ],
        "preloaded_data": [
            {'Course': 'Bóng chuyền 1', 'Credits': 1, 'Grade': 'D', 'Category': 'Giáo dục thể chất', 'Semester': 1}, {'Course': 'Bóng chuyền 2', 'Credits': 1, 'Grade': 'C', 'Category': 'Giáo dục thể chất', 'Semester': 1}, {'Course': 'Bóng rổ', 'Credits': 1, 'Grade': 'B', 'Category': 'Giáo dục thể chất', 'Semester': 1}, {'Course': 'Hóa học đại cương', 'Credits': 3, 'Grade': 'D', 'Category': 'Khoa học tự nhiên và tin học', 'Semester': 1}, {'Course': 'Cầu lông', 'Credits': 1, 'Grade': 'C', 'Category': 'Giáo dục thể chất', 'Semester': 1}, {'Course': 'Tin học cơ bản', 'Credits': 2, 'Grade': 'B', 'Category': 'Khoa học tự nhiên và tin học', 'Semester': 1}, {'Course': 'Giải tích hàm một biến', 'Credits': 3, 'Grade': 'C', 'Category': 'Khoa học tự nhiên và tin học', 'Semester': 1}, {'Course': 'Kỹ năng mềm và tinh thần khởi nghiệp', 'Credits': 3, 'Grade': 'B', 'Category': 'Kỹ năng', 'Semester': 1},
            {'Course': 'Sức bền vật liệu 1', 'Credits': 3, 'Grade': 'C', 'Category': 'Kiến thức cơ sở ngành', 'Semester': 2}, {'Course': 'Vật liệu xây dựng', 'Credits': 3, 'Grade': 'C', 'Category': 'Kiến thức cơ sở ngành', 'Semester': 2}, {'Course': 'Sức bền vật liệu 2', 'Credits': 2, 'Grade': 'C', 'Category': 'Kiến thức cơ sở ngành', 'Semester': 2}, {'Course': 'Tiếng Anh 1', 'Credits': 3, 'Grade': 'C', 'Category': 'Ngoại ngữ', 'Semester': 2}, {'Course': 'Cơ học chất lỏng', 'Credits': 3, 'Grade': 'C', 'Category': 'Kiến thức cơ sở ngành', 'Semester': 2}, {'Course': 'Pháp luật đại cương', 'Credits': 2, 'Grade': 'C', 'Category': 'Lý luận chính trị', 'Semester': 2}, {'Course': 'Địa chất công trình', 'Credits': 2, 'Grade': 'D', 'Category': 'Kiến thức cơ sở khối ngành', 'Semester': 2}, {'Course': 'Triết học Mác - Lênin', 'Credits': 3, 'Grade': 'D', 'Category': 'Lý luận chính trị', 'Semester': 2},
    "Quản lý xây dựng": {
        "course_categories": ["Kinh tế", "Luật", "Quản lý dự án", "Kỹ thuật cơ sở"],
        "graduation_requirements": { "Kinh tế": 40, "Luật": 20, "Quản lý dự án": 50, "Kỹ thuật cơ sở": 40, },
        "full_curriculum": [ # Dữ liệu mẫu
            {'Course': 'Kinh tế vi mô', 'Credits': 3, 'Category': 'Kinh tế'}, {'Course': 'Luật xây dựng', 'Credits': 2, 'Category': 'Luật'}, {'Course': 'Quản lý dự án xây dựng', 'Credits': 3, 'Category': 'Quản lý dự án'},
        ],
        "preloaded_data": [
            {'Course': 'Kinh tế vi mô', 'Credits': 3, 'Grade': 'A', 'Category': 'Kinh tế', 'Semester': 1},
            {'Course': 'Luật xây dựng', 'Credits': 2, 'Grade': 'B', 'Category': 'Luật', 'Semester': 1},
# -----------------------------
# CÁC HÀM TIỆN ÍCH
# -----------------------------
# ... (Các hàm khác giữ nguyên)
# ... (Các hàm calc_gpa, check_academic_warning, v.v. giữ nguyên và thêm hàm PDF)
@st.cache_data
def to_csv(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")
    total_credits = pd.to_numeric(work_passed["Credits"], errors="coerce").fillna(0.0).sum()
    if total_credits <= 0: return 0.0
    return (work_passed["QP"].sum()) / total_credits

# SỬA LỖI: Khôi phục lại hàm cảnh báo chính xác
def check_academic_warning(semester_number: int, sgpa: float, cumulative_f_credits: float, previous_warning_level: int) -> Tuple[int, str, List[str]]:
    reasons, is_warning_condition_met = [], False
    if semester_number == 1 and sgpa < 0.80: is_warning_condition_met = True; reasons.append(f"SGPA học kỳ 1 ({sgpa:.2f}) < 0.80")
    elif semester_number > 1 and sgpa < 1.00: is_warning_condition_met = True; reasons.append(f"SGPA ({sgpa:.2f}) < 1.00")
    if cumulative_f_credits > 24: is_warning_condition_met = True; reasons.append(f"Tổng tín chỉ nợ ({cumulative_f_credits:.1f}) > 24")
    
    current_warning_level = 0
    if is_warning_condition_met:
        if previous_warning_level == 2: current_warning_level = 3
        elif previous_warning_level == 1: current_warning_level = 2
        else: current_warning_level = 1
    # Nếu không vi phạm, mức cảnh báo sẽ là 0 (đã được reset ở dòng trên)
    
    if current_warning_level > 0: return current_warning_level, f"Cảnh báo học tập Mức {current_warning_level}", reasons
    return 0, "Đạt yêu cầu", []

def calculate_progress(all_sems_data: List[pd.DataFrame], requirements: Dict, grade_map: Dict):
    if not any(not df.empty for df in all_sems_data): return pd.DataFrame()
    master_df = pd.concat(all_sems_data, ignore_index=True)
    if 1.50 <= gpa < 2.00: return "Trung bình yếu"
    if 1.00 <= gpa < 1.50: return "Yếu"
    return "Kém"

# NÂNG CẤP: Các hàm gợi ý học tập
def get_unregistered_courses(all_sems_data, full_curriculum_df):
    if not all_sems_data or full_curriculum_df.empty: return pd.DataFrame()
    taken_courses = set(pd.concat(all_sems_data)["Course"])
    unregistered_df = full_curriculum_df[~full_curriculum_df["Course"].isin(taken_courses)]
    return unregistered_df.reset_index(drop=True)
def get_courses_for_improvement(all_sems_data, grade_map):
    if not any(not df.empty for df in all_sems_data): return pd.DataFrame()
    master_df = pd.concat(all_sems_data, ignore_index=True)
    master_df['Points'] = master_df['Grade'].map(grade_map)
    # Tìm điểm cao nhất cho mỗi môn học
    best_grades_df = master_df.loc[master_df.groupby('Course')['Points'].idxmax()]
    # Lọc ra những môn có điểm D
    d_grade = 'D'
    improve_df = best_grades_df[best_grades_df['Grade'] == d_grade]
    return improve_df[['Course', 'Credits', 'Grade', 'Category']].reset_index(drop=True)

class PDF(FPDF):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
if "sems" not in st.session_state: on_major_change()
GRADUATION_REQUIREMENTS_CURRENT = MAJORS_DATA[selected_major]['graduation_requirements']
DEFAULT_COURSE_CATEGORIES_CURRENT = MAJORS_DATA[selected_major]['course_categories']
FULL_CURRICULUM_DF = pd.DataFrame(MAJORS_DATA[selected_major]['full_curriculum'])
if upload is not None and not st.session_state.get('file_processed', False):
    try:
        df_up = pd.read_csv(upload, encoding='utf-8')
            else:
                st.metric("Kết quả XLHV dự kiến:", f"Mức {auto_warning_level}" if auto_warning_level > 0 else "Không", delta="Dựa trên điểm kỳ này", delta_color="off")
            manual_warning_options = ["Không", "Mức 1", "Mức 2", "Mức 3", "Xóa tên khỏi danh sách"]
            selected_warning_str = st.selectbox("Xử lý học vụ (chính thức):", options=manual_warning_options, index=manual_warning_options.index(st.session_state.manual_warnings[i]), key=f"manual_warning_{i}")
            selected_warning_str = st.selectbox("Xử lý học vụ (chính thức):", options=manual_warning_options, index=WARNING_STR_TO_LEVEL[st.session_state.manual_warnings[i]] if st.session_state.manual_warnings[i] in WARNING_STR_TO_LEVEL else 0, key=f"manual_warning_{i}")
            st.session_state.manual_warnings[i] = selected_warning_str
            final_warning_level = WARNING_STR_TO_LEVEL[selected_warning_str]
            warning_history.append({"Học kỳ": i + 1, "Mức Cảnh báo": final_warning_level, "Lý do": ", ".join(auto_reasons) if auto_reasons else "Không có"})
    with colB: st.metric("📚 Tổng tín chỉ đã qua", f"{total_passed_credits:.2f}")
    with colC: st.metric("🧑‍🎓 Trình độ sinh viên", get_student_level(total_passed_credits))
    with colD: st.metric("🏆 Xếp loại học lực", get_gpa_ranking(cgpa))
    
    st.subheader("💡 Gợi ý học tập")
    g1, g2 = st.columns(2)
    with g1:
        with st.expander("📚 Các môn chưa đăng ký học"):
            unregistered = get_unregistered_courses(st.session_state.sems, FULL_CURRICULUM_DF)
            if not unregistered.empty:
                st.dataframe(unregistered, use_container_width=True, hide_index=True)
            else:
                st.success("Chúc mừng! Bạn đã học tất cả các môn trong chương trình.")
    with g2:
        with st.expander("🎯 Các môn có thể học cải thiện (Điểm D)"):
            improve = get_courses_for_improvement(st.session_state.sems, grade_map)
            if not improve.empty:
                st.dataframe(improve, use_container_width=True, hide_index=True)
            else:
                st.success("Tuyệt vời! Không có môn nào cần học cải thiện.")
    
    chart_col, _ = st.columns([1, 1])
    with chart_col:
        st.subheader("Xu hướng GPA theo học kỳ")
        st.subheader("📈 Xu hướng GPA theo học kỳ")
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
with st.expander("📜 Cách tính & Lịch sử xử lý học vụ"):
    def style_warning_html(level):
        if level == 0: return f'<p style="color: green; margin:0;">Không</p>'
        if level == 1: return f'<p style="color: orange; font-weight: bold; margin:0;">Mức {level}</p>'
        if level == 2 or level == 3: return f'<p style="color: red; font-weight: bold; margin:0;">Mức {level}</p>'
        if level == 4: return f'<p style="color: #A30000; font-weight: bold; margin:0;">Xóa tên</p>'
    display_df = pd.DataFrame(warning_history)
    display_df["Mức Xử lý"] = display_df["Mức Cảnh báo"].apply(style_warning_html)
    display_df = display_df.rename(columns={"Học kỳ": "<b>Học kỳ</b>", "Mức Xử lý": "<b>Mức Xử lý</b>", "Lý do": "<b>Lý do (gợi ý)</b>"})
    st.markdown(display_df[["<b>Học kỳ</b>", "<b>Mức Xử lý</b>", "<b>Lý do (gợi ý)</b>"]].to_html(escape=False, index=False), unsafe_allow_html=True)
with st.expander("❓ Hướng dẫn"):
    st.markdown("""- **Nhập/Xuất file:** File CSV phải có các cột: `Course`, `Credits`, `Grade`, `Semester`, `Category`.\n- **Thêm/xóa môn học:** Dùng nút `+` để thêm và tick vào ô "Xóa" rồi nhấn nút "🗑️ Xóa môn đã chọn" để xóa.\n- **Xử lý học vụ:** Chọn mức xử lý chính thức của nhà trường tại mỗi học kỳ. Kết quả này sẽ được dùng để tính toán mức cảnh báo dự kiến cho học kỳ tiếp theo.""")
