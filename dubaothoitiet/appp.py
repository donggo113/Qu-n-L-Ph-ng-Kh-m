import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA

st.title("Ứng dụng Dự báo Dịch bệnh COVID-19")

@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv"
    df = pd.read_csv(url)
    return df

df = load_data()

# Chọn quốc gia
countries = df['Country/Region'].unique()
selected_country = st.selectbox("Chọn quốc gia cần dự báo:", countries, index=list(countries).index("Vietnam") if "Vietnam" in countries else 0)

# Lựa chọn số ngày dự báo
forecast_days = st.slider("Số ngày muốn dự báo tương lai:", 7, 60, 14)

# Tiền xử lý
df_country = df[df['Country/Region'] == selected_country]
df_ts = df_country.drop(columns=['Province/State', 'Country/Region', 'Lat', 'Long']).sum(axis=0)
df_ts.index = pd.to_datetime(df_ts.index, format='%m/%d/%y')
daily_cases = df_ts.diff().fillna(0).clip(lower=0)

# Huấn luyện & Dự báo
model = ARIMA(daily_cases, order=(5, 1, 0))
model_fit = model.fit()
future_forecast = model_fit.forecast(steps=forecast_days)

# Hiển thị đồ thị
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(daily_cases.index[-90:], daily_cases[-90:], label="Lịch sử (90 ngày gần nhất)")
ax.plot(future_forecast.index, future_forecast, label=f"Dự báo ({forecast_days} ngày tới)", color="red", linestyle="--")
ax.set_title(f"Dự báo ca nhiễm COVID-19 tại {selected_country}")
ax.set_ylabel("Số ca mắc mới")
ax.legend()
ax.grid(True)

st.pyplot(fig)