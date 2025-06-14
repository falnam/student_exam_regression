import csv
import random
import os

# Fungsi akar kuadrat manual (Newton-Raphson)
def sqrt(x, tolerance=1e-10):
    guess = x / 2.0
    while abs(guess * guess - x) > tolerance:
        guess = (guess + x / guess) / 2.0
    return guess

# Load Dataset
def load_dataset(filepath):
    data = []
    with open(filepath, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            study_hours = float(row['study_hours_per_day'])
            attendance = float(row['attendance_percentage'])
            exam_score = float(row['exam_score'])
            data.append((study_hours, attendance, exam_score))
    return data

# Normalisasi (Min-Max)
def normalize(dataset):
    study_hours = [row[0] for row in dataset]
    attendance = [row[1] for row in dataset]

    min_study, max_study = min(study_hours), max(study_hours)
    min_attend, max_attend = min(attendance), max(attendance)

    normalized_data = []
    for s, a, e in dataset:
        norm_s = (s - min_study) / (max_study - min_study)
        norm_a = (a - min_attend) / (max_attend - min_attend)
        normalized_data.append((norm_s, norm_a, e))

    norm_params = {
        'study': (min_study, max_study),
        'attendance': (min_attend, max_attend)
    }
    return normalized_data, norm_params

# Split Train-Test
def split_dataset(dataset, train_ratio=0.8):
    random.seed(42)
    random.shuffle(dataset)
    train_size = int(len(dataset) * train_ratio)
    return dataset[:train_size], dataset[train_size:]

# Regresi Linear Manual
def train_regression(train_data):
    n = len(train_data)
    sum_x1 = sum([row[0] for row in train_data])
    sum_x2 = sum([row[1] for row in train_data])
    sum_y  = sum([row[2] for row in train_data])

    mean_x1 = sum_x1 / n
    mean_x2 = sum_x2 / n
    mean_y  = sum_y / n

    num_b1 = sum([(row[0] - mean_x1)*(row[2] - mean_y) for row in train_data])
    den_b1 = sum([(row[0] - mean_x1)**2 for row in train_data])

    num_b2 = sum([(row[1] - mean_x2)*(row[2] - mean_y) for row in train_data])
    den_b2 = sum([(row[1] - mean_x2)**2 for row in train_data])

    b1 = num_b1 / den_b1 if den_b1 != 0 else 0
    b2 = num_b2 / den_b2 if den_b2 != 0 else 0

    b0 = mean_y - b1 * mean_x1 - b2 * mean_x2

    return b0, b1, b2

# Prediksi
def predict(x1, x2, b0, b1, b2):
    return b0 + b1 * x1 + b2 * x2

# Evaluasi Model
def evaluate(test_data, b0, b1, b2):
    sum_sq = 0
    sum_abs = 0
    ss_total = 0

    mean_y = sum([row[2] for row in test_data]) / len(test_data)

    for row in test_data:
        pred = predict(row[0], row[1], b0, b1, b2)
        error = pred - row[2]
        sum_sq += error ** 2
        sum_abs += abs(error)
        ss_total += (row[2] - mean_y) ** 2

    rmse = sqrt(sum_sq / len(test_data))
    mae = sum_abs / len(test_data)
    r2 = 1 - (sum_sq / ss_total) if ss_total != 0 else 0
    return rmse, mae, r2

# Normalisasi Input
def normalize_input(user_val, min_val, max_val):
    return (user_val - min_val) / (max_val - min_val)

# Main Program
def main():
    filepath = os.path.join("..", "data", "student_habits_performance.csv")

    dataset = load_dataset(filepath)
    normalized_data, norm_params = normalize(dataset)
    train_data, test_data = split_dataset(normalized_data)

    b0, b1, b2 = train_regression(train_data)
    rmse, mae, r2 = evaluate(test_data, b0, b1, b2)

    print("="*46)
    print("         PROGRAM REGRESI LINEAR SEDERHANA")
    print("="*46)

    print("\nDataset:")
    print(f"- Total data    : {len(dataset)}")
    print(f"- Data latih    : {len(train_data)}")
    print(f"- Data pengujian: {len(test_data)}")

    print("-"*46)
    print("Hasil Pelatihan Model:")
    print(f"Persamaan regresi:")
    print(f"exam_score = {b0:.2f} + {b1:.2f} * study_hours_norm + {b2:.2f} * attendance_norm")

    print("-"*46)
    print("Evaluasi Model:")
    print(f"- RMSE (Root Mean Squared Error) : {rmse:.2f}")
    print(f"- MAE  (Mean Absolute Error)     : {mae:.2f}")
    print(f"- R²   (Koefisien Determinasi)   : {r2:.4f}")

    print("="*46)
    print("      PREDIKSI NILAI UJIAN MAHASISWA BARU")
    print("="*46)

    study_hours_input = float(input("Masukkan jam belajar per hari   : "))
    attendance_input = float(input("Masukkan persentase kehadiran   : "))

    min_study, max_study = norm_params['study']
    min_attend, max_attend = norm_params['attendance']

    study_norm = normalize_input(study_hours_input, min_study, max_study)
    attend_norm = normalize_input(attendance_input, min_attend, max_attend)

    print("-"*46)
    print("Proses Normalisasi Input:")
    print(f"- study_hours_norm  = ({study_hours_input} - {min_study}) / ({max_study} - {min_study}) = {study_norm:.4f}")
    print(f"- attendance_norm   = ({attendance_input} - {min_attend}) / ({max_attend} - {min_attend}) = {attend_norm:.4f}")

    pred_study = b1 * study_norm
    pred_attend = b2 * attend_norm
    prediction = b0 + pred_study + pred_attend

    print("-"*46)
    print("Proses Perhitungan Prediksi:")
    print(f"exam_score = {b0:.2f} + ({b1:.2f} * {study_norm:.4f}) + ({b2:.2f} * {attend_norm:.4f})")
    print(f"exam_score = {b0:.2f} + {pred_study:.2f} + {pred_attend:.2f}")
    print(f"exam_score = {prediction:.2f}")

    print("="*46)
    print(f"      HASIL PREDIKSI NILAI UJIAN: {prediction:.2f}")
    print("="*46)

if __name__ == "__main__":
    main()
