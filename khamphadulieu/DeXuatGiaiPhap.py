import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import IsolationForest

print("[1] Đang lay dữ liệu...")
df_qg = pd.read_csv('THPT 2018 Quoc gia.csv', low_memory=False)
df_hg = pd.read_csv('THPT 2018 Ha Giang.csv', low_memory=False)

subjects = ['Math', 'Viet', 'English', 'Physics', 'Chemistry', 'Biology', 'History', 'Geography', 'KhoiA', 'KhoiA1']
for col in subjects:
    if col in df_qg.columns:
        df_qg[col] = pd.to_numeric(df_qg[col], errors='coerce')
    if col in df_hg.columns:
        df_hg[col] = pd.to_numeric(df_hg[col], errors='coerce')

print("\n[2] PHÂN TÍCH TỶ LỆ TOÀN QUỐC VS HÀ GIANG")
qg_a1_27 = (df_qg['KhoiA1'] >= 27.0).sum()
hg_a1_27 = (df_hg['KhoiA1'] >= 27.0).sum()

print(f"- Số thí sinh Khối A1 >= 27 điểm Toàn quốc: {qg_a1_27} / {len(df_qg)} ({qg_a1_27/len(df_qg)*100:.4f}%)")
print(f"- Số thí sinh Khối A1 >= 27 điểm Hà Giang : {hg_a1_27} / {len(df_hg)} ({hg_a1_27/len(df_hg)*100:.4f}%)")
print(f"=> Tỷ lệ thí sinh điểm cao Khối A1 ở Hà Giang cao gấp { (hg_a1_27/len(df_hg)) / (qg_a1_27/len(df_qg)):.1f} lần toàn quốc!")

df_hg['Nat_Avg'] = df_hg[['Math', 'Physics', 'Chemistry']].mean(axis=1)
df_hg['Disparity'] = df_hg['Nat_Avg'] - df_hg['Viet']

top_anomalies_rule = df_hg.sort_values(by='Disparity', ascending=False)[['SoBD', 'Math', 'Physics', 'Chemistry', 'Viet', 'Disparity']].head(10)
print("\n[3] TOP THÍ SINH CÓ ĐỘ CHÊNH LỆCH ĐIỂM (KHOA HỌC TỰ NHIÊN VS NGỮ VĂN):")
print(top_anomalies_rule.to_string(index=False))

print("\n[4] CHẠY MÔ HÌNH ISOLATION FOREST...")
df_clean = df_hg.dropna(subset=['Math', 'Physics', 'Chemistry']).copy()

model = IsolationForest(contamination=0.02, random_state=42)
df_clean['Anomaly_Score'] = model.fit_predict(df_clean[['Math', 'Physics', 'Chemistry']])

anomalies = df_clean[df_clean['Anomaly_Score'] == -1]
print(f"-> Đã phát hiện {len(anomalies)} trường hợp dị biệt điểm số bằng Isolation Forest.")

plt.figure(figsize=(10, 6))
sns.scatterplot(
    data=df_clean,
    x='Math',
    y='Physics',
    hue='Anomaly_Score',
    palette={1: '#1f77b4', -1: '#d62728'},
    style='Anomaly_Score',
    s=70
)
plt.title('Phát hiện Điểm Bất thường (Isolation Forest) - Môn Toán & Vật Lý tại Hà Giang', fontsize=12)
plt.xlabel('Điểm Toán', fontsize=10)
plt.ylabel('Điểm Vật Lý', fontsize=10)
plt.legend(title='Cảnh báo', labels=['Nghi vấn bất thường (-1)', 'Bình thường (1)'])
plt.grid(True, linestyle='--', alpha=0.5)

# Lưu đồ thị ra file ảnh
plt.tight_layout()
plt.savefig('ketqua.png', dpi=300)
print("\n[5] Đã xuất biểu đồ kết quả vào file 'ketqua.png'")