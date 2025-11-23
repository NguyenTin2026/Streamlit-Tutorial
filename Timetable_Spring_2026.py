import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from io import BytesIO
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import streamlit.components.v1 as components
import plotly.io as pio
import time

# ========================
# PAGE CONFIG
# ========================
st.set_page_config(page_title="Smart Timetable Spring 2026", page_icon="📅", layout="wide")
st.title("📅 Smart Timetable — Live Animated Timetable (Spring 2026)")
st.markdown("### Total Credit Hours: **16.000**")
st.markdown("🟢 **Spring 2026 Start Date:** 21 Jan 2026")
st.divider()

# ========================
# COURSE DATA
# ========================
courses = [
    {"Course":"Cybersecurity (CSCI 270)","Instructor":"Mehdi Hasan","Days":["Tuesday","Thursday"],"Start":"11:50","End":"13:05","BaseColor":"#6366F1"},
    {"Course":"Environmental Science (ENV 150)","Instructor":"Shagufta Gaffar","Days":["Tuesday","Thursday"],"Start":"10:25","End":"11:40","BaseColor":"#10B981"},
    {"Course":"College Writing (WRTG 101)","Instructor":"Cara N. Anan","Days":["Tuesday","Thursday"],"Start":"14:40","End":"15:55","BaseColor":"#F59E0B"},
    {"Course":"Software Engineering (CSCI 340)","Instructor":"Alexander Rudniy","Days":["Monday","Wednesday"],"Start":"11:50","End":"13:05","BaseColor":"#0EA5E9"},
]

rows = []
for c in courses:
    for d in c["Days"]:
        rows.append({
            "Course": c["Course"],
            "Instructor": c["Instructor"],
            "Day": d,
            "Start_Time": c["Start"],
            "End_Time": c["End"],
            "BaseColor": c["BaseColor"]
        })
df = pd.DataFrame(rows)

def time_to_float(t):
    h, m = map(int, t.split(":"))
    return h + m/60

df["Start_float"] = df["Start_Time"].apply(time_to_float)
df["End_float"] = df["End_Time"].apply(time_to_float)
df["label"] = df.apply(lambda r: f"{r['Course']}\n{r['Start_Time']}–{r['End_Time']}\n{r['Instructor']}", axis=1)

# ========================
# TABULAR VIEW
# ========================
st.subheader("📋 Tabular Timetable with Time")
pivot = pd.pivot_table(
    df,
    index=["Start_Time","End_Time"],
    columns="Day",
    values="Course",
    aggfunc=lambda x: " | ".join(x)
)
st.dataframe(pivot.fillna(""), use_container_width=True)

# ========================
# TIME CONFLICT CHECK
# ========================
st.subheader("⚠️ Time Conflicts Check")
conflicts = []
color_map_all = df.set_index("Course")["BaseColor"].to_dict()
for day in df["Day"].unique():
    day_df = df[df["Day"]==day]
    for i, row1 in day_df.iterrows():
        for j, row2 in day_df.iterrows():
            if i >= j: continue
            start1 = datetime.strptime(row1["Start_Time"], "%H:%M")
            end1 = datetime.strptime(row1["End_Time"], "%H:%M")
            start2 = datetime.strptime(row2["Start_Time"], "%H:%M")
            end2 = datetime.strptime(row2["End_Time"], "%H:%M")
            if max(start1,start2) < min(end1,end2):
                conflicts.append(f"{row1['Course']} conflicts with {row2['Course']} on {day}")
                color_map_all[row1["Course"]] = "#EF4444"
                color_map_all[row2["Course"]] = "#EF4444"

if conflicts:
    st.warning("Found time conflicts:")
    for c in conflicts: st.write(f"- {c}")
else:
    st.success("No time conflicts detected ✅")

# ========================
# UPCOMING CLASS REMINDERS
# ========================
st.subheader("⏰ Upcoming Class Reminders (Next 60 min)")
today_name = datetime.now().strftime("%A")
today_df = df[df["Day"]==today_name]
for _, row in today_df.iterrows():
    start_dt = datetime.strptime(row["Start_Time"], "%H:%M").replace(
        year=datetime.now().year, month=datetime.now().month, day=datetime.now().day)
    delta = (start_dt - datetime.now()).total_seconds()/60
    if 0 < delta <= 60:
        st.info(f"{row['Course']} starts in {int(delta)} minutes at {row['Start_Time']}")
        components.html(f"<script>alert('Reminder: {row['Course']} starts at {row['Start_Time']}!');</script>", height=0)

from streamlit_autorefresh import st_autorefresh

# ========================
# LIVE ANIMATED TIMELINE (mượt)
# ========================
st.subheader("🔴 Live Animated Timeline")
st.markdown("Lớp đang học nhấp nháy sáng/tối mỗi giây.")

# auto refresh mỗi 1 giây
st_autorefresh(interval=1000, key="auto_refresh_timeline")

placeholder = st.empty()

now = datetime.now()
second = now.second

color_map = {}
for i, row in df.iterrows():
    start_dt = datetime.strptime(row["Start_Time"], "%H:%M").replace(
        year=now.year, month=now.month, day=now.day
    )
    end_dt = datetime.strptime(row["End_Time"], "%H:%M").replace(
        year=now.year, month=now.month, day=now.day
    )
    if start_dt <= now <= end_dt:
        # nhấp nháy lớp đang học
        color_map[row["Course"]] = row["BaseColor"] if second % 2 == 0 else "#FFFFFF"
    elif now < start_dt:
        color_map[row["Course"]] = "#D1D5DB"
    else:
        color_map[row["Course"]] = "#9CA3AF"

fig = px.timeline(
    df,
    x_start="Start_float",
    x_end="End_float",
    y="Day",
    color="Course",
    text="label",
    color_discrete_map=color_map
)
fig.update_traces(marker=dict(line=dict(width=1, color="black")), textposition="inside")
fig.update_yaxes(autorange="reversed")
fig.update_xaxes(title="Time (Hour)", tickvals=list(range(8,19)), ticktext=[f"{h}:00" for h in range(8,19)])
fig.update_layout(height=650, margin=dict(l=50,r=50,t=50,b=50), showlegend=True)

placeholder.plotly_chart(fig, use_container_width=True, key="live_timeline")


# ========================
# EXPORT PDF / EXCEL
# ========================
st.subheader("📄 Export Timeline as PDF")
if st.button("Export Timeline PDF"):
    fig_export = px.timeline(
        df,
        x_start="Start_float",
        x_end="End_float",
        y="Day",
        color="Course",
        text="label",
        color_discrete_map=df.set_index("Course")["BaseColor"].to_dict()
    )
    fig_export.update_yaxes(autorange="reversed")
    img_bytes = pio.to_image(fig_export, format='png', width=1200, height=700, scale=2)
    img = Image.open(BytesIO(img_bytes))
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    img_width, img_height = img.size
    scale = min(width/img_width*0.9, height/img_height*0.9)
    img_width_scaled = img_width*scale
    img_height_scaled = img_height*scale
    x = (width - img_width_scaled)/2
    y = (height - img_height_scaled)/2
    img.save("temp_timetable.png")
    c.drawImage("temp_timetable.png", x, y, img_width_scaled, img_height_scaled)
    c.showPage()
    c.save()
    buffer.seek(0)
    st.download_button("Download PDF", data=buffer, file_name="Spring_2026_Timetable_4courses_Live.pdf", mime="application/pdf")

st.subheader("📘 Export Timeline as Excel")
def to_excel(df):
    output = BytesIO()
    df_export = df.copy()
    df_export = df_export[["Day","Start_Time","End_Time","Course","Instructor"]]
    df_export.to_excel(output, index=False, sheet_name="Timetable")
    return output.getvalue()
st.download_button(label="Download Excel", data=to_excel(df), file_name="Spring_2026_Timetable_4courses_Live.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# ========================
# INSTRUCTOR DETAILS
# ========================
with st.expander("📚 Instructor Details"):
    st.markdown("""
    - **CSCI 270 - Cybersecurity:** Mehdi Hasan — Online (Tuesday) & In-person (Thursday)  
    - **CSCI 340 - Software Engineering:** Alexander Rudniy — Classroom, In-person (Monday & Wednesday)  
    - **ENV 150 - Environmental Science:** Shagufta Gaffar — Classroom, In-person (Tuesday & Thursday)  
    - **WRTG 101 - College Writing:** Cara N. Anan — Classroom, In-person (Tuesday & Thursday)
    """)

st.caption("© 2026 Drew University — Smart Live Timetable (4 courses) with Animation by Tin Tin Do 🧠")