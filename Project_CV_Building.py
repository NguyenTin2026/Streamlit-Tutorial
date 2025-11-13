import streamlit as st
import os

# ----- CONFIG -----
st.set_page_config(
    page_title="Nguyen Tin Tin Do — Resume & Portfolio",
    page_icon=":male-technologist:",
    layout="wide"
)

# ----- DARK MODE -----
dark_mode = st.checkbox("Dark Mode")
if dark_mode:
    st.markdown("""
    <style>
    body {background-color:#121212; color:#e0e0e0;}
    h1, h2, h3 {color:#90caf9;}
    .section-title {border-bottom:2px solid #90caf9; color:#90caf9;}
    a {color:#82b1ff;}
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
    h1, h2, h3 {color: #2c3e50;}
    body {background-color: #f9f9f9; color:#000;}
    .section-title {font-size: 22px; font-weight: 600; color: #1e3a8a; border-bottom: 2px solid #1e3a8a; padding-bottom: 3px; margin-top: 25px;}
    a {color:#1e3a8a;}
    ul {margin-top:0; margin-bottom:0;}
    </style>
    """, unsafe_allow_html=True)

# ----- HEADER -----
col1, col2 = st.columns([2, 3])
with col1:
    st.title("Nguyen Tin Tin Do")
    st.write("(862) 579-6543 | ndo1@drew.edu")
    st.write("[LinkedIn](https://linkedin.com/in/nguyen-tin-tin-do) | [GitHub](https://github.com/NguyenTin)")
    st.write("[LinkedIn](https://github.com/NguyenTin2026) | [GitHub](https://github.com/NguyenTin)")
with col2:
    st.markdown("""
**Computer Science major with a Data Science minor, specializing in Artificial Intelligence and Deep Learning.**  
Skilled in Python, TensorFlow, PyTorch, and OpenCV, building real-time face and object recognition systems.  
Aspiring AI Engineer passionate about intelligent visual systems.
""")

# ----- IMAGE FOLDER -----
image_folder = "images"

def safe_image(path, caption="Image"):
    if os.path.exists(path):
        st.image(path, caption=caption, use_column_width=True)
    else:
        st.info(f"[Placeholder] {caption} not found: {path}")

# ----- TABS -----
tabs = st.tabs(["Education", "Projects", "Experience", "Leadership", "Skills", "Other"])

# ----- EDUCATION -----
with tabs[0]:
    st.markdown('<div class="section-title">EDUCATION</div>', unsafe_allow_html=True)
    st.write("""
**Drew University** — *Madison, New Jersey*  
**B.Sc. in Computer Science | Minor: Data Science | GPA 3.7/4.0**  
Expected Graduation: May 2027  
- Merit Scholarship, $15,000 (Fall 2025 – Spring 2026) for GPA ≥ 3.5  
- Relevant Coursework: AI, Data Science, Database Systems
""")
    safe_image(os.path.join(image_folder, "drew_campus.png"), "Drew University Campus")

# ----- PROJECTS -----
with tabs[1]:
    st.markdown('<div class="section-title">PROJECTS</div>', unsafe_allow_html=True)

    with st.expander("Face Recognition via Webcam, Images, and Videos (Aug 2025 – Oct 2025)"):
        st.markdown("""
- Real-time face detection & recognition using OpenCV & Haar Cascade.  
- Webcam input for live identification, 30FPS CPU / 60FPS GPU.  
- Optimized frame-by-frame processing, ~25% latency reduction.
""")
        safe_image(os.path.join(image_folder, "face_recognition_demo.png"), "Face Recognition Demo")

    with st.expander("API Testing & Coding Projects (Aug 2024 – Sep 2024)"):
        st.markdown("- Tested APIs using Postman & FastAPI; version control with Git, GitHub, Bitbucket.")
        safe_image(os.path.join(image_folder, "api_testing.png"), "API Testing Screenshot")

    with st.expander("Data Analysis & Visualization (Jun 2023 – Present)"):
        st.markdown("""
- Data analysis using Python, Jupyter Notebook, Google Colab.  
- PostgreSQL queries & visualization for insights.
""")
        safe_image(os.path.join(image_folder, "data_viz.png"), "Sample Data Visualization")

# ----- EXPERIENCE -----
with tabs[2]:
    st.markdown('<div class="section-title">WORK EXPERIENCE</div>', unsafe_allow_html=True)
    st.write("**Freelance AI Developer / Independent Researcher | Remote** — *Aug 2025 – Present*")
    st.markdown("""
- Built & deployed object detection using YOLOv5 & OpenCV.  
- Dataset collection, cleaning & visualization with Pandas, Matplotlib, Seaborn.
""")

    st.write("**Freelancer – Social Media Content Creator | Remote** — *Jan 2021 – May 2025*")
    st.markdown("""
- Managed TikTok (22K followers), Instagram (12K), Threads (1K), Facebook (18K).  
- Multimedia content production increased view duration by 25%.
""")

# ----- LEADERSHIP -----
with tabs[3]:
    st.markdown('<div class="section-title">LEADERSHIP AND ACTIVITIES</div>', unsafe_allow_html=True)
    st.write("**Founder & Volunteer English Instructor | Self-Initiated Projects** — *May 2023 – May 2025*")
    st.markdown("""
- Founded two free English learning platforms (900+ followers).  
- Delivered presentations & online tutoring in English & Math.  
- Mentored six learners weekly to improve communication.
""")

# ----- SKILLS -----
with tabs[4]:
    st.markdown('<div class="section-title">TECHNICAL SKILLS</div>', unsafe_allow_html=True)
    st.markdown("""
- **Programming & Data Science:** Python, R, Java, C++, TypeScript, JS, HTML, CSS, SQL  
- **Libraries & Tools:** NumPy, Pandas, SciPy, Matplotlib, Seaborn, TensorFlow, Scikit-learn, OpenCV, PyTorch, Keras, YOLO  
- **Version Control & Collaboration:** Git, GitHub, GitLab, Bitbucket, Docker, Postman  
- **Environments:** Jupyter, VS Code, Anaconda, Colab, Sublime, PyCharm, Kaggle
""")

# ----- OTHER SKILLS -----
with tabs[5]:
    st.markdown('<div class="section-title">OTHER SKILLS</div>', unsafe_allow_html=True)
    st.markdown("""
- **Productivity & Collaboration:** Google Workspace, MS Office  
- **Soft Skills:** Teamwork, Communication, Critical Thinking, Problem Solving  
- **Creative & Media Tools:** CapCut, Photoshop, Canva  
- **Languages:** English (Proficient), Vietnamese (Native), Spanish (Basic)
""")

# ----- FOOTER -----
st.markdown("---")
st.caption("© 2025 Nguyen Tin Tin Do · Drew University · Created with Streamlit")