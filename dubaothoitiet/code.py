import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error, mean_absolute_error

# 1. Tải dữ liệu từ GitHub CSSE COVID-19
url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv"
df = pd.read_csv(url)

# 2. Tiền xử lý dữ liệu: Lấy dữ liệu cho một quốc gia (ví dụ: Vietnam hoặc Global)
country = "Vietnam"
df_country = df[df['Country/Region'] == country]

# Nhóm theo quốc gia và bỏ các cột không cần thiết
df_ts = df_country.drop(columns=['Province/State', 'Country/Region', 'Lat', 'Long']).sum(axis=0)

# Chuyển đổi chỉ số thành kiểu dữ liệu Datetime
df_ts.index = pd.to_datetime(df_ts.index, format='%m/%d/%y')
df_ts = pd.DataFrame(df_ts, columns=['Confirmed'])

# Chuyển đổi số ca tích lũy sang số ca mắc mới theo ngày
df_ts['Daily_Cases'] = df_ts['Confirmed'].diff().fillna(0)
df_ts['Daily_Cases'] = df_ts['Daily_Cases'].clip(lower=0) # Loại bỏ số âm (nếu có do điều chỉnh số liệu)

# 3. Chia tập Train / Test (ví dụ: dùng 30 ngày cuối làm tập Test)
test_days = 30
train = df_ts['Daily_Cases'][:-test_days]
test = df_ts['Daily_Cases'][-test_days:]

# 4. Huấn luyện mô hình ARIMA(p,d,q)
model = ARIMA(train, order=(5, 1, 0))
model_fit = model.fit()

# Dự báo 30 ngày tới
predictions = model_fit.forecast(steps=test_days)
predictions.index = test.index

# 5. Đánh giá mô hình
rmse = np.sqrt(mean_squared_error(test, predictions))
mae = mean_absolute_error(test, predictions)
print(f"Chỉ số RMSE: {rmse:.2f}")
print(f"Chỉ số MAE: {mae:.2f}")

# 6. Trực quan hóa kết quả
plt.figure(figsize=(12, 6))
plt.plot(train.index[-60:], train[-60:], label='Train (Dữ liệu thực tế)')
plt.plot(test.index, test, label='Test (Dữ liệu thực tế)', color='green')
plt.plot(predictions.index, predictions, label='Dự báo (ARIMA)', color='red', linestyle='--')
plt.title(f'Dự báo số ca nhiễm COVID-19 mới theo ngày tại {country}')
plt.xlabel('Thời gian')
plt.ylabel('Số ca mắc mới')
plt.legend()
plt.grid(True)
plt.show()