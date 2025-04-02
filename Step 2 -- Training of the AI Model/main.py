import cudf
import mlModels as mL
import training as tr
import os
import preprocessing as pre
import time
import gc
from numba import cuda

if __name__ == '__main__':
    start_time = time.time()

    folder = "Datasets/Sports and Outdoors"
    json_files = [f for f in os.listdir(folder) if f.endswith('.json')]
    df = None

    batch_size = 5  # Ajustar según VRAM disponible
    for i in range(0, len(json_files), batch_size):
        batch_files = json_files[i:i + batch_size]
        print("Procesando batch:", batch_files)
        batch_df = cudf.concat([pre.execute(cudf.read_json(os.path.join(folder, f), lines=True)) for f in batch_files])
        if df is None:
            df = batch_df
        else:
            df = cudf.concat([df, batch_df])
        del batch_df
        gc.collect()
        cuda.current_context().deallocations.clear()  # Limpia memoria de CUDA

    del batch_files, json_files, folder

    print(f"\nTiempo total de preprocesamiento: {time.time() - start_time:.2f} segundos")
    print("Número de filas:", len(df))
    tr.train(df)
    #mL.execute_mL(df)

    print(f"\nTiempo total: {time.time() - start_time:.2f} segundos")