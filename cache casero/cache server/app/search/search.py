import grpc
import json
import time
import numpy as np
import cache_service_pb2
import cache_service_pb2_grpc
from find_car_by_id import find_car_by_id

class CacheClient:
    def __init__(self, host="master", port=50051):
        self.channel = grpc.insecure_channel(f"{host}:{port}")
        self.stub = cache_service_pb2_grpc.CacheServiceStub(self.channel)
        self.cache_hits = 0  # Contador de búsquedas resueltas en caché
        self.cache_misses = 0  # Contador de búsquedas en caché que resultan en fallos
        self.total_searches = 0  # Contador del total de búsquedas

    def get(self, key, simulated=False):
        start_time = time.time()  # Inicio del temporizador

        response = self.stub.Get(cache_service_pb2.Key(key=key))
        
        if response.value:
            elapsed_time = time.time() - start_time  # Calcula el tiempo transcurrido
            print(f"Time taken (cache): {elapsed_time:.5f} seconds")
            
            # Incrementa el contador de búsquedas resueltas en caché
            self.cache_hits += 1

            return response.value
        else:
            # Simulamos un retraso aleatorio de 1 a 3 segundos, con una distribución normal en 2
            delay = np.random.normal(2, 0.5)
            print(f"Key not found in cache. Waiting {delay:.5f} seconds...")

            if not simulated:
                time.sleep(delay)

            # Si no está en el caché, buscar en el JSON
            value = find_car_by_id(int(key))
            value = str(value)
            if value:
                print("Key found in JSON. Adding to cache...")
                # Agregando la llave-valor al caché
                self.stub.Put(cache_service_pb2.CacheItem(key=key, value=value))
                
                elapsed_time = time.time() - start_time  # Calcula el tiempo transcurrido
                if simulated:
                    # Agregar el retraso al tiempo solo si es una simulación
                    elapsed_time += delay
                print(f"Time taken (JSON + delay): {elapsed_time:.5f} seconds")
                
                # Incrementar el contador de búsquedas en caché que resultan en fallos
                self.cache_misses += 1

                return value
            else:
                elapsed_time = time.time() - start_time  # Calcula el tiempo transcurrido
                print(f"Time taken: {elapsed_time:.5f} seconds")
                print("Key not found.")
                return None
            
    def simulate_scenarios(self, n_searches=100, constant_frequency=False):
        keys_to_search = [f"{i}" for i in np.random.randint(1, 101, n_searches)]

        # Métricas
        time_without_cache = 0
        time_with_cache = 0
        avoided_json_lookups = 0

        count = 0
        for key in keys_to_search:
            # Limpiar la consola
            count += 1
            print("\033[H\033[J")
            print(f"Searching : {count}/{n_searches}")
            start_time = time.time()
            time_without_cache += 3 + 0.001  # Estimado de tiempo de búsqueda en JSON
            self.get(key, simulated=constant_frequency)
            elapsed_time = time.time() - start_time
            time_with_cache += elapsed_time

            if elapsed_time < 1:
                avoided_json_lookups += 1

            # Incrementar el contador del total de búsquedas
            self.total_searches += 1

        time_saved = time_without_cache - time_with_cache
        print(f"\nTime saved thanks to cache: {time_saved:.2f} seconds")
        print(f"Number of times JSON lookup was avoided: {avoided_json_lookups}")

        # Calcular la tasa de fallos (miss rate) y el hit rate del caché
        miss_rate = self.cache_misses / self.total_searches
        hit_rate = self.cache_hits / self.total_searches

        print(f"Miss Rate (Cache): {miss_rate:.2%}")
        print(f"Hit Rate (Cache): {hit_rate:.2%}")
    
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
