import time
import numpy as np
from find_car_by_id import find_car_by_id
import memcache



class CacheClient:
    def __init__(self, host="memcached", port=11211):
        self.memcached_client = memcache.Client([f"{host}:{port}"])
        self.cache_hits = 0
        self.total_searches = 0
        

    def get(self, key, simulated=False):
        start_time = time.time()  # Inicio del temporizador
        value = self.memcached_client.get(key)

        if value is not None:  # Comprobar si hay un valor, en lugar de 'exists'
            elapsed_time = time.time() - start_time  # Calcula el tiempo transcurrido
            print(f"Time taken (cache): {elapsed_time:.5f} seconds")
            self.cache_hits += 1 
            return value

        else:
            delay = np.random.normal(2, 0.5)
            print(f"Key not found in cache. Waiting {delay:.5f} seconds...")

            if not simulated:
                time.sleep(delay)

            value = find_car_by_id(int(key))
            value = str(value) 
            if value:
                print("Key found in JSON. Adding to cache...")
                # Agregando la llave-valor al caché
                self.memcached_client.set(key, value)
                elapsed_time = time.time() - start_time  # Calcula el tiempo transcurrido  
                
                if simulated:
                    # add delay to time just sum
                    elapsed_time += delay
                print(f"Time taken (JSON + delay): {elapsed_time:.5f} seconds")
                
                return value
            else:
                elapsed_time = time.time() - start_time  # Calcula el tiempo transcurrido
                print(f"Time taken: {elapsed_time:.5f} seconds")
                print("Key not found.")
                return None 
           
        

            
    def simulate_scenarios(self, n_searches=100, constant_frequency = False):
        keys_to_search = [f"{i}" for i in np.random.randint(1, 101, n_searches)]

        # Métricas
        time_without_cache = 0
        time_with_cache = 0
        avoided_json_lookups = 0

        count = 0
        for key in keys_to_search:
            # clear console
            count += 1
            print("\033[H\033[J")
            print(f"Searching : {count}/{n_searches}")
            start_time = time.time()
            time_without_cache += 3 + 0.001  # Estimado de tiempo de búsqueda en JSON
            self.get(key, simulated = constant_frequency)
            elapsed_time = time.time() - start_time
            time_with_cache += elapsed_time

            if elapsed_time < 1:
                avoided_json_lookups += 1

            self.total_searches += 1    

        time_saved = time_without_cache - time_with_cache
        print(f"\nTime saved thanks to cache: {time_saved:.2f} seconds")
        print(f"Number of times JSON lookup was avoided: {avoided_json_lookups}")
        
        hit_rate = self.cache_hits / self.total_searches
        print(f"Hit Rate del cache: {hit_rate:.2%}")

if __name__ == '__main__':
    client = CacheClient()

    while True:
        print("\nMenu CON cache:")
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
            client.simulate_scenarios(n_searches, constant_frequency=False)
        elif choice == "3":
            n_searches = int(input("Enter the number of searches you want to simulate: "))
            client.simulate_scenarios(n_searches, constant_frequency=True)
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Try again.")