import random
import math
import time


class Vehicle:
    def __init__(self, id, x, y, speed, direction):
        self.id = id
        self.x = x
        self.y = y
        self.speed = speed  # 速度，单位可以是 km/h
        self.direction = direction  # 方向，用弧度表示
        self.status = 1  # 1 表示存活，0 表示损毁

    def move(self):
        # 转换速度为每秒移动的距离（假设单位是 km/h，转换为每秒移动的 km）
        distance = self.speed / 3600

        # 计算 x 和 y 方向上的移动
        dx = distance * math.cos(self.direction)
        dy = distance * math.sin(self.direction)

        self.x += dx
        self.y += dy

        # 确保位置在 0-100 范围内
        self.x = max(0, min(100, self.x))
        self.y = max(0, min(100, self.y))

        # 随机微调方向（增加一些随机性）
        self.direction += random.uniform(-0.1, 0.1)

    def __str__(self):
        return f"{self.id},{self.status},{self.x:.2f},{self.y:.2f}"


def create_vehicles(num_usv, num_auv, num_uav):
    vehicles = []
    for i in range(1, num_usv + 1):
        vehicles.append(Vehicle(i, random.uniform(0, 100), random.uniform(0, 100),
                                random.uniform(50, 150), random.uniform(0, 2 * math.pi)))
    for i in range(101, 101 + num_auv):
        vehicles.append(Vehicle(i, random.uniform(0, 100), random.uniform(0, 100),
                                random.uniform(30, 100), random.uniform(0, 2 * math.pi)))
    for i in range(201, 201 + num_uav):
        vehicles.append(Vehicle(i, random.uniform(0, 100), random.uniform(0, 100),
                                random.uniform(200, 500), random.uniform(0, 2 * math.pi)))
    return vehicles


def simulate(vehicles, duration, interval):
    start_time = time.time()
    while time.time() - start_time < duration:
        with open('data.txt', 'w') as file:
            for vehicle in vehicles:
                vehicle.move()
                if random.random() < 0.001:  # 极小概率损毁
                    vehicle.status = 0
                file.write(str(vehicle) + '\n')
        time.sleep(interval)


if __name__ == "__main__":
    vehicles = create_vehicles(5, 10, 5)  # 创建 5 个 USV，3 个 AUV，2 个 UAV
    simulate(vehicles, 3600, 0.1)  # 模拟 1 小时，每秒更新一次
