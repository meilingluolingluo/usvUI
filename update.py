import random
import time


def generate_data():
    data = []
    # 生成 USV 数据 (1-100)
    for i in range(1, 6):  # 假设有5个USV
        status = random.choice([0, 1])  # 随机状态
        x = random.uniform(0, 100)  # 随机 X 坐标
        y = random.uniform(0, 100)  # 随机 Y 坐标
        data.append(f"{i},{status},{x:.2f},{y:.2f}")

    # 生成 AUV 数据 (101-200)
    for i in range(101, 111):  # 假设有3个AUV
        status = random.choice([0, 1])
        x = random.uniform(0, 100)
        y = random.uniform(0, 100)
        data.append(f"{i},{status},{x:.2f},{y:.2f}")

    # 生成 UAV 数据 (201-300)
    for i in range(201, 206):  # 假设有2个UAV
        status = random.choice([0, 1])
        x = random.uniform(0, 100)
        y = random.uniform(0, 100)
        data.append(f"{i},{status},{x:.2f},{y:.2f}")

    return data


def update_data_file():
    while True:
        data = generate_data()
        with open('data.txt', 'w') as file:
            for line in data:
                file.write(line + '\n')
        print(f"Data updated at {time.strftime('%Y-%m-%d %H:%M:%S')}")
        time.sleep(2)  # 每10秒更新一次


if __name__ == "__main__":
    print("Starting data update simulation...")
    update_data_file()