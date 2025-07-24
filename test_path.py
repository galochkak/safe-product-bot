import os

print("Текущая папка:", os.getcwd())

# Попробуем создать папку data
data_dir = os.path.join(os.getcwd(), "data")
os.makedirs(data_dir, exist_ok=True)
print("Папка data будет создана здесь:", data_dir)

# Проверим, можно ли записать туда файл
test_file = os.path.join(data_dir, "test.txt")
with open(test_file, "w") as f:
    f.write("Тестовая запись")

print("Файл создан:", test_file)