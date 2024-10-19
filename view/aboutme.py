import streamlit as st

# Hero Section
col_photo, col_about = st.columns([1, 3], gap="medium")

with col_photo:
    st.image("assets/kucing_magic.png", width=180)

with col_about:
    st.title("Azriel Akbar Alfarez")
    st.write("""
        Saya tertarik untuk menjadi seorang **Data Analyst** dan memiliki ketertarikan yang mendalam dalam **analisis data**, **visualisasi data**, dan **machine learning**.
        Saya memiliki kemampuan teknis yang kuat dan terus mengembangkan keterampilan saya untuk berkontribusi di dunia data.
    """)

# Experience & Skills Section
st.write("---")

col_exp, col_skills = st.columns(2, gap="medium")

with col_exp:
    st.subheader("Experience")
    st.write("""
        **PT APIK MEDIA INOVASI, Jakarta** (Maret 2022 – Mei 2022)  
        *Praktik Kerja Industri*  
        - Memperdalam pengetahuan mengenai Cisco, konfigurasi jaringan, protokol, dan keamanan jaringan.
        - Bertanggung jawab atas pemeliharaan server fisik untuk memastikan kinerja server tetap optimal.
        - Berinteraksi langsung dengan klien untuk memahami kebutuhan dan masalah terkait server.
    """)

with col_skills:
    st.subheader("Skills")
    st.write("""
        - **Programming Languages**: Python
        - **Tools**: Streamlit, Pandas, Microsoft Excel
        - **Data Visualization**: Matplotlib, Seaborn
    """)


# Projects Section
st.write("---")

st.subheader("Projects")
st.write("""
    Berikut beberapa proyek yang telah saya kerjakan:

    - [E-Commerce Analytics Dashboard](https://github.com/azrielll/eccomerce-dashboard): Dashboard interaktif untuk menganalisis kinerja e-commerce menggunakan Python, Pandas, dan Streamlit.
""")

# Footer Section
st.write("---")
st.write("Copyright © 2024 Azriel Akbar Alfarez")
