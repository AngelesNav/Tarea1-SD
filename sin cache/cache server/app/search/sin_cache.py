import json
import numpy as np
from find_car_by_id import find_car_by_id
import time
import random

class CacheClient:
    def __init__(self):
        self.hit_count = 0
        self.miss_count = 0

    def get(self, key):
        delay = max(0, random.normalvariate(1, 0.1))
        time.sleep(delay)
        
        start_time = time.time()
        value = find_car_by_id(int(key))
        elapsed_time = time.time() - start_time
        print(f"Time taken: {elapsed_time:.5f} seconds")
        
        if value:
            self.hit_count += 1
            print("Key found in JSON.")
        else:
            self.miss_count += 1
            print("Key not found.")
        
        return value

    def get_constant_frequency(self, key):
        time.sleep(1)
        
        start_time = time.time()
        value = find_car_by_id(int(key))
        elapsed_time = time.time() - start_time
        print(f"Time taken: {elapsed_time:.5f} seconds")
        
        if value:
            self.hit_count += 1
            print("Key found in JSON.")
        else:
            self.miss_count += 1
            print("Key not found.")
        
        return value

    def simulate_searches(self, n_searches=100, constant_frequency=False):
        keys_to_search = [f"{i}" for i in range(1, n_searches + 1)]

        self.hit_count = 0
        self.miss_count = 0

        count = 0
        for key in keys_to_search:
            count += 1
            print("\033[H\033[J")
            print(f"Searching: {count}/{n_searches}")
            if constant_frequency:
                value = self.get_constant_frequency(key)
            else:
                value = self.get(key)
            if value is not None:
                print(f"Value: {value}")

        total_requests = self.hit_count + self.miss_count
        hit_rate = (self.hit_count / total_requests) * 100
        miss_rate = (self.miss_count / total_requests) * 100

        print(f"\nHit Rate: {hit_rate:.2f}%")
        print(f"Miss Rate: {miss_rate:.2f}%")

if __name__ == '__main__':
    client = CacheClient()

    while True:
        print("\nMenu SIN cache:")
        print("1. Get")
        print("2. Simulate Searches (Normal Distribution)")
        print("3. Simulate Searches (Constant Frequency)")
        print("4. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            key = input("Enter key: ")
            value = client.get(key)
            if value is not None:
                print(f"Value: {value}")
        elif choice == "2":
            n_searches = int(input("Enter the number of searches you want to simulate: "))
            client.simulate_searches(n_searches, constant_frequency=False)
        elif choice == "3":
            n_searches = int(input("Enter the number of searches you want to simulate: "))
            client.simulate_searches(n_searches, constant_frequency=True)
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Try again.")
