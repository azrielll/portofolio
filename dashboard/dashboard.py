import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import seaborn as sns
import streamlit as st
import urllib
from babel.numbers import format_currency
#.set(style='dark')

def create_daily_orders_df(df):
    # Pastikan kolom 'order_approved_at' memiliki format datetime
    df['order_approved_at'] = pd.to_datetime(df['order_approved_at'], errors='coerce')
    
    # Resample data berdasarkan hari ('D')
    daily_orders_df = df.resample(rule='D', on='order_approved_at').agg({
        "order_id": "nunique",
        "payment_value": "sum"
    })
    
    daily_orders_df = daily_orders_df.reset_index()
    
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "payment_value": "revenue"
    }, inplace=True)
        
    return daily_orders_df

def create_sum_order_items_df(df):
    # Menghitung total produk per kategori
    sum_order_items_df = df.groupby("product_category_name_english")["product_id"].count().reset_index()
    sum_order_items_df.rename(columns={
        "product_id": "product_count"
    }, inplace=True)
    
    # Mengurutkan data berdasarkan jumlah produk dari tertinggi ke terendah
    sum_order_items_df = sum_order_items_df.sort_values(by='product_count', ascending=False)

    return sum_order_items_df

def create_tipe_pembayaran(df):
    # Menghitung jumlah order per tipe pembayaran
    tipe_pembayaran_df = df.groupby("payment_type")["order_id"].count().sort_values(ascending=False).reset_index()
    tipe_pembayaran_df.rename(columns={"order_id": "payment_count"}, inplace=True)
    return tipe_pembayaran_df

def review_score_df(df):
    review_scores = df['review_score'].value_counts().sort_values(ascending=False)
    most_common_score = review_scores.idxmax()

    return review_scores, most_common_score

def create_sum_spend_df(df):
    sum_spend_df = df.resample(rule='D', on='order_approved_at').agg({
        "payment_value": "sum"
    })
    sum_spend_df = sum_spend_df.reset_index()
    sum_spend_df.rename(columns={
        "payment_value": "total_spend"
    }, inplace=True)

    return sum_spend_df

def create_bystate_df(df):
    bystate_df = df.groupby(by="customer_state").customer_id.nunique().reset_index()
    bystate_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)
    most_common_state = bystate_df.loc[bystate_df['customer_count'].idxmax(), 'customer_state']
    bystate_df = bystate_df.sort_values(by='customer_count', ascending=False)

    return bystate_df, most_common_state

def create_order_status(df):
    order_status_df = df["order_status"].value_counts().sort_values(ascending=False)
    most_common_status = order_status_df.idxmax()

    return order_status_df, most_common_status

def create_rfm_df(df):
    # Pastikan kolom 'order_purchase_timestamp' memiliki format datetime
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'], errors='coerce')

    rfm_df = df.groupby(by="customer_id", as_index=False).agg({
        "order_purchase_timestamp": "max",  # Mengambil tanggal order terakhir
        "order_id": "nunique",  # Menghitung jumlah unik order_id
        "price": "sum"   # Menghitung total harga
    })
    rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]

    # Menghitung Recency
    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    recent_date = df["order_purchase_timestamp"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)

    return rfm_df



# Load data
all_df = pd.read_csv("data/all_data.csv")
rfm_df = create_rfm_df(all_df)

#datetime
datetime_columns = ["order_delivered_customer_date", "order_delivered_carrier_date", "order_approved_at"]
all_df.sort_values(by="order_delivered_customer_date", inplace=True)
all_df.reset_index(inplace=True)

for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

# Header
st.header('E-Commerce Analytics Dashboard :sparkles:')

# Side Bar
min_date = all_df["order_delivered_customer_date"].min()
max_date = all_df["order_delivered_customer_date"].max()


with st.sidebar:
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# Filter DataFrame berdasarkan rentang waktu yang dipilih
filtered_df = all_df[(all_df['order_delivered_customer_date'] >= pd.Timestamp(start_date)) &
                      (all_df['order_delivered_customer_date'] <= pd.Timestamp(end_date))]

# Geolocation Dataset
class BrazilMapPlotter:
    def __init__(self, data, plt, mpimg, urllib, st):
        self.data = data
        self.plt = plt
        self.mpimg = mpimg
        self.urllib = urllib
        self.st = st

    def plot(self):
        # Memuat gambar peta Brasil
        brazil = self.mpimg.imread(self.urllib.request.urlopen('https://i.pinimg.com/originals/3a/0c/e1/3a0ce18b3c842748c255bc0aa445ad41.jpg'), 'jpg')
        
        # Membuat figure dan axis untuk plotting
        fig, ax = self.plt.subplots(figsize=(10, 10))
        
        # Plot scatter geolocation pada peta Brasil
        self.data.plot(kind="scatter", x="geolocation_lng", y="geolocation_lat", alpha=0.3, s=0.3, c='#90CAF9', ax=ax)
        
        # Mematikan axis dan menampilkan gambar peta di latar belakang
        ax.axis('off')
        ax.imshow(brazil, extent=[-73.98283055, -33.8, -33.75116944, 5.4])
        
        # Menampilkan plot dengan Streamlit
        self.st.pyplot(fig)

geolocation = pd.read_csv('data/geolocation.csv')
data = geolocation.drop_duplicates(subset='customer_unique_id')
map_plot = BrazilMapPlotter(data, plt, mpimg, urllib, st)

# Data Frame
daily_orders_df = create_daily_orders_df(filtered_df)
sum_order_items_df = create_sum_order_items_df(filtered_df)
tipe_pembayaran_df = create_tipe_pembayaran(filtered_df)
review_score, common_score = review_score_df(filtered_df)
sum_spend_df = create_sum_spend_df(filtered_df)
state, most_common_state = create_bystate_df(filtered_df)
order_status, common_status = create_order_status(filtered_df)


# Daily Orders
st.subheader("Daily Orders")

col1, col2 = st.columns(2)

with col1:
    total_order = daily_orders_df["order_count"].sum()
    st.markdown(f"Total Order: **{total_order}**")

with col2:
    total_revenue = format_currency(daily_orders_df["revenue"].sum(), "BRL", locale='pt_BR')
    st.markdown(f"Total Revenue: **{total_revenue}**")

fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(
    daily_orders_df["order_approved_at"],
    daily_orders_df["order_count"],
    marker="o",
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis="x", rotation=45)
ax.tick_params(axis="y", labelsize=15)
st.pyplot(fig)


# Customer & Product Overview
st.subheader("Customer & Product Overview")
tab1, tab2, tab3,tab4= st.tabs(["Customer Spend Money","Category Product", "Payment Types","Review Score"])

# Customer Spend Money
with tab1:
    col1, col2 = st.columns(2)

    with col1:
        total_spend = format_currency(sum_spend_df["total_spend"].sum(), "BRL", locale='pt_BR')
        st.markdown(f"Total Spend: **{total_spend}**")

    with col2:
        avg_spend = format_currency(sum_spend_df["total_spend"].mean(), "BRL", locale='pt_BR')
        st.markdown(f"Average Spend: **{avg_spend}**")

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(
        sum_spend_df["order_approved_at"],
        sum_spend_df["total_spend"],
        marker="o",
        linewidth=2,
        color="#90CAF9"
    )
    ax.tick_params(axis="x", rotation=45)
    ax.tick_params(axis="y", labelsize=15)
    st.pyplot(fig)


# Best & Worst Performing Category Product
with tab2:
    best_category_product = sum_order_items_df.iloc[0]['product_category_name_english']
    st.markdown(f"Best Category Products: **{best_category_product}**")
    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(45, 25))
    colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

    sns.barplot(x="product_count", y="product_category_name_english", 
                data=sum_order_items_df.nlargest(5, "product_count"), 
                palette=colors, ax=ax[0])
    ax[0].set_ylabel(None)
    ax[0].set_xlabel("Number of Sales", fontsize=30)
    ax[0].set_title("Best Category Product", loc="center", fontsize=50)
    ax[0].tick_params(axis='y', labelsize=35)
    ax[0].tick_params(axis='x', labelsize=30)

    sns.barplot(x="product_count", y="product_category_name_english", 
                data=sum_order_items_df.nsmallest(5, "product_count"), 
                palette=colors, ax=ax[1])
    ax[1].set_ylabel(None)
    ax[1].set_xlabel("Number of Sales", fontsize=30)
    ax[1].invert_xaxis() 
    ax[1].yaxis.set_label_position("right")
    ax[1].yaxis.tick_right()
    ax[1].set_title("Worst Category Product", loc="center", fontsize=50)
    ax[1].tick_params(axis='y', labelsize=35)
    ax[1].tick_params(axis='x', labelsize=30)
    st.pyplot(fig)

    with st.expander("See Explanation"):
        st.header("Interpretasi Best Product")
        st.write("Produk dalam kategori **bed_bath_table** memiliki jumlah penjualan tertinggi, mendekati **12.000 unit**. "
                "Diikuti oleh kategori **health_beauty**, **sports_leisure**, **furniture_decor**, dan **computers_accessories** "
                "yang semuanya memiliki penjualan lebih dari **6.000 unit**.")

        st.subheader("Saran:")
        st.write("Lanjutkan strategi promosi dan distribusi pada kategori **bed_bath_table** dan **health_beauty**, "
                "karena produk-produk ini memiliki penjualan tertinggi. "
                "Selain itu, evaluasi strategi pemasaran untuk kategori di bawahnya, seperti **sports_leisure** dan **furniture_decor**, "
                "untuk melihat apakah penjualan dapat ditingkatkan lebih lanjut.")

        st.header("Interpretasi Worst Product")
        st.write("Kategori produk dengan kinerja terendah adalah **arts_and_craftsmanship**, dengan penjualan di bawah **5 unit**. "
                "Kategori lain seperti **la_cuisine**, **cds_dvds_musicals**, **fashion_childrens_clothes**, dan **security_and_services** "
                "memiliki penjualan di bawah **25 unit**, yang menunjukkan performa yang sangat rendah.")

        st.subheader("Saran:")
        st.write("Untuk produk dengan kinerja rendah seperti **arts_and_craftsmanship** dan **la_cuisine**, "
                "perlu dilakukan evaluasi pasar untuk memahami mengapa penjualannya rendah. "
                "Pertimbangkan untuk mengurangi stok atau menghentikan penjualan jika permintaan sangat rendah. "
                "Selain itu, tinjau ulang strategi pemasaran untuk kategori ini atau lakukan riset lebih lanjut "
                "untuk menentukan apakah ada potensi pertumbuhan pasar yang belum dimanfaatkan.")

# Most Common Payment Type
with tab3:
    most_common_payment_type = tipe_pembayaran_df.iloc[tipe_pembayaran_df['payment_count'].idxmax()]['payment_type']
    st.markdown(f"Most Common Payment Types: **{most_common_payment_type}**")
    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(45, 25))
    colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]




    total_payments = tipe_pembayaran_df["payment_count"].sum()
    st.markdown(f"Total Payments: **{total_payments}**")

    fig, ax = plt.subplots(figsize=(12, 6))

    colors = colors

    sns.barplot(x="payment_count", y="payment_type", data=tipe_pembayaran_df, palette=colors, ax=ax)
    ax.set_ylabel(None)
    ax.set_xlabel("Number of Payments", fontsize=15)
    ax.set_title("Most Common Payment Types", loc="center", fontsize=20)
    ax.tick_params(axis='y', labelsize=12)
    ax.tick_params(axis='x', labelsize=12)

    st.pyplot(fig)

# Review Score
with tab4:
    most_frequently_given_rating = common_score 
    
    st.markdown(f"Most Frequently Given Rating: **{most_frequently_given_rating}**")
    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(45, 25))
    colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
  

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(x=review_score.index, 
                y=review_score.values, 
                order=review_score.index,
                palette=colors
                )

    plt.title("Rating by customers for service", fontsize=15)
    plt.xlabel("Rating")
    plt.ylabel("Count")
    plt.xticks(fontsize=12)
    st.pyplot(fig)

    with st.expander("See Explanation"):
        st.header("Interpretasi")
        
        st.write("""
        **Tingkat Kepuasan yang Tinggi**: Sebagian besar pelanggan memberikan rating yang tinggi, terutama rating 5.0 yang mendominasi. 
        Hal ini menandakan bahwa layanan yang diberikan umumnya sesuai atau bahkan melebihi ekspektasi pelanggan.
        
        **Rendahnya Rating Negatif**: Jumlah pelanggan yang memberikan rating rendah (1.0, 2.0, dan 3.0) sangat sedikit. 
        Ini menunjukkan bahwa hanya sebagian kecil pelanggan yang merasa tidak puas, yang merupakan sinyal positif bagi kualitas layanan.
        """)
        
        st.subheader("Saran:")
        
        st.write("""
        1. **Pertahankan Kualitas Layanan**: Karena tingkat kepuasan pelanggan umumnya tinggi, penting untuk terus menjaga dan meningkatkan standar kualitas layanan. 
        Melakukan evaluasi berkala terhadap layanan yang diberikan akan membantu menjaga tingkat kepuasan ini.
        
        2. **Dengarkan Umpan Balik**: Meskipun sebagian besar pelanggan memberikan rating tinggi, penting untuk tetap mendengarkan umpan balik dari pelanggan yang memberikan rating di bawah 5.0. 
        Identifikasi area yang masih memerlukan perbaikan akan membantu meningkatkan loyalitas pelanggan.
        
        3. **Tingkatkan Program Penghargaan Pelanggan**: Pertimbangkan untuk mengimplementasikan program penghargaan bagi pelanggan yang memberikan rating tinggi. 
        Ini dapat mendorong mereka untuk terus menggunakan layanan dan dapat menarik pelanggan baru melalui ulasan positif.
        
        4. **Fokus pada Pengembangan Layanan**: Meskipun pelanggan umumnya puas, berinvestasi dalam pengembangan atau peningkatan layanan yang ada tetap penting. 
        Ini akan membantu menarik perhatian pelanggan baru dan menjaga kepuasan pelanggan yang sudah ada.
        """)

# Customer Demographic
st.subheader("Customer Demographic")
tab1, tab2, tab3= st.tabs(["State", "Order Status","Geolocation"])

# Most Common State
with tab1:
    most_common_state = state.customer_state.value_counts().index[0]
    st.markdown(f"Most Common State: **{most_common_state}**")

    fig, ax = plt.subplots(figsize=(12, 6))
    
    palette = ["#90CAF9" if state == most_common_state else "#D3D3D3" for state in state.customer_state.value_counts().index]
    
    sns.barplot(
        x=state.customer_state.value_counts().index,
        y=state.customer_count.values,
        data=state,
        palette=palette
    )

    plt.title("Number customers from State", fontsize=15)
    plt.xlabel("State")
    plt.ylabel("Number of Customers")
    plt.xticks(fontsize=12)
    st.pyplot(fig)

    with st.expander("See Explanation"):
        st.header("Interpretasi")
        
        st.write("""
        **Negara Bagian Paling Umum**: SP (São Paulo) memiliki jumlah pelanggan tertinggi, dengan hampir 40.000 pelanggan, jauh lebih tinggi dibandingkan negara bagian lain.
        
        **Distribusi Tidak Merata**: Setelah SP, negara bagian RJ (Rio de Janeiro) dan MG (Minas Gerais) memiliki jumlah pelanggan yang jauh lebih sedikit, di bawah 10.000. Negara bagian lainnya memiliki pelanggan dalam jumlah yang lebih rendah lagi.
        
        **Dominasi SP**: Dominasi pelanggan dari São Paulo sangat jelas, menunjukkan bahwa perusahaan atau layanan ini mungkin lebih berfokus di area tersebut, atau populasi di São Paulo yang memang lebih besar berperan dalam jumlah pelanggan yang tinggi.
        """)
        
        st.subheader("Saran:")
        
        st.write("""
        1. **Ekspansi Pasar**: Mengingat dominasi pelanggan dari SP, perusahaan bisa mempertimbangkan strategi untuk meningkatkan penetrasi di negara bagian lain, terutama RJ, MG, RS, PR, dan negara bagian lainnya yang juga memiliki basis pelanggan yang potensial.
        
        2. **Studi Spesifik Tiap Wilayah**: Lakukan analisis lebih mendalam di negara bagian seperti RJ dan MG untuk mengetahui mengapa jumlah pelanggan mereka lebih rendah, dan bagaimana meningkatkan keterlibatan mereka.
        
        3. **Diversifikasi Strategi Pemasaran**: Mungkin perlu ada strategi pemasaran yang lebih lokal untuk meningkatkan visibilitas di negara bagian dengan jumlah pelanggan lebih rendah.
        
        4. **Fokus Pada SP**: Di sisi lain, mengingat tingginya jumlah pelanggan di SP, perusahaan juga bisa memaksimalkan kehadiran dan meningkatkan layanan di SP untuk mempertahankan keunggulan mereka di wilayah tersebut.
        """)


    
 # Order Status
with tab2:
    order_status_counts = all_df['order_status'].value_counts()
    most_common_status = order_status_counts.index[0]
    st.markdown(f"Most Order Status: **{most_common_status}**")

    plt.figure(figsize=(8, 6))
    order_status_counts.plot(kind='bar', color='skyblue')
    plt.title('Order Status')
    plt.xlabel('Status')
    plt.ylabel('Number of Orders')

    fig = plt.gcf()
    st.pyplot(fig)

#Geolocation
with tab3:
    map_plot.plot()



# RFM PARAMETERS
st.subheader("Best Customer Based on RFM Parameters")

col1, col2, col3 = st.columns(3)

with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)

with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)

with col3:
    avg_monetary = format_currency(rfm_df.monetary.mean(), "AUD", locale='es_CO') 
    st.metric("Average Monetary", value=avg_monetary)

fig, axs = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))  
colors = ["#90CAF9"] * 5  

# Bar chart berdasarkan Recency
sns.barplot(y="recency", x="customer_id", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=axs[0])  # Ganti ax[0] menjadi axs[0]
axs[0].set_ylabel(None)
axs[0].set_xlabel("customer_id", fontsize=30)
axs[0].set_title("By Recency (days)", loc="center", fontsize=50)
axs[0].tick_params(axis='y', labelsize=30)
axs[0].tick_params(axis='x', labelbottom=False)


# Bar chart berdasarkan Frequency
sns.barplot(y="frequency", x="customer_id", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=axs[1])  # Ganti ax[1] menjadi axs[1]
axs[1].set_ylabel(None)
axs[1].set_xlabel("customer_id", fontsize=30)
axs[1].set_title("By Frequency", loc="center", fontsize=50)
axs[1].tick_params(axis='y', labelsize=30)
axs[1].tick_params(axis='x', labelbottom=False)


# Bar chart berdasarkan Monetary
sns.barplot(y="monetary", x="customer_id", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=axs[2])  # Ganti ax[2] menjadi axs[2]
axs[2].set_ylabel(None)
axs[2].set_xlabel("customer_id", fontsize=30)
axs[2].set_title("By Monetary", loc="center", fontsize=50)
axs[2].tick_params(axis='y', labelsize=30)
axs[2].tick_params(axis='x', labelbottom=False)

st.pyplot(fig)

st.caption('Copyright (c) Azriel Akbar Alfarez')

