import streamlit as st

st.set_page_config(page_title="Portofolio")

# Page Setup
about_me_page = st.Page(
    page = "view/aboutme.py",
    title = "About Me",
    icon = "👹",
    default=True
)
project_page = st.Page(
    page = "dashboard/dashboard.py",
    title = "Project",
    icon = "📊",
)

# Navigation
pg = st.navigation([about_me_page, project_page])
pg.run()