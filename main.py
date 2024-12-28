import tkinter as tk
from tkinter import filedialog, messagebox
import heapq
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import pickle
import os

# Узел дерева Хаффмана
class Node:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq

    def __lt__(self, other):
        return self.freq < other.freq

# Функция для создания кодов
def create_codes(node, prefix="", codebook={}):
    if isinstance(node, str):
        codebook[node] = prefix
    else:
        create_codes(node[0], prefix + "0", codebook)
        create_codes(node[1], prefix + "1", codebook)
    return codebook

# Функция для сжатия блока данных
def compress_block(data):
    frequency = defaultdict(int)
    for char in data:
        frequency[char] += 1

    heap = [Node(char, freq) for char, freq in frequency.items()]
    heapq.heapify(heap)

    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        merged = Node(None, left.freq + right.freq)
        heapq.heappush(heap, (merged, left, right))

    root = heap[0]
    codebook = create_codes(root)

    compressed_data = ''.join(codebook[char] for char in data)
    return compressed_data, codebook

# Функция для декомпрессии данных
def decompress(compressed_data, codebook):
    reverse_codebook = {v: k for k, v in codebook.items()}
    current_code = ""
    decompressed_data = ""

    for bit in compressed_data:
        current_code += bit
        if current_code in reverse_codebook:
            decompressed_data += reverse_codebook[current_code]
            current_code = ""

    return decompressed_data

# Основная функция для сжатия данных с многопоточностью
def compress(data, num_threads=4):
    block_size = len(data) // num_threads
    blocks = [data[i:i + block_size] for i in range(0, len(data), block_size)]

    compressed_blocks = []
    codebooks = []

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = {executor.submit(compress_block, block): block for block in blocks}
        for future in as_completed(futures):
            compressed_data, codebook = future.result()
            compressed_blocks.append(compressed_data)
            codebooks.append(codebook)

    final_compressed_data = ''.join(compressed_blocks)
    final_codebook = {**codebooks[0], **codebooks[1]}  # Пример объединения, можно улучшить

    return final_compressed_data, final_codebook

# Функция для сжатия текстового файла с использованием алгоритма
def compress_text_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = f.read()
    compressed_data, codebook = compress(data)
    compressed_file_path = file_path + '.huff'
    with open(compressed_file_path, 'wb') as f:
        pickle.dump((compressed_data, codebook), f)
    return compressed_file_path

# Функция для сжатия бинарного файла с использованием алгоритма
def compress_binary_file(file_path):
    with open(file_path, 'rb') as f:
        data = f.read()
    # Преобразуем бинарные данные в строку для сжатия
    compressed_data, codebook = compress(data.decode('latin-1'))  # Используем 'latin-1' для сохранения байтов
    compressed_file_path = file_path + '.huff'
    with open(compressed_file_path, 'wb') as f:
        pickle.dump((compressed_data, codebook), f)
    return compressed_file_path

# Функция для обработки выбора файла и сжатия
def compress_file():
    file_path = filedialog.askopenfilename()
    if file_path:
        if file_path.endswith('.txt'):
            compressed_file_path = compress_text_file (file_path)
        else:
            compressed_file_path = compress_binary_file(file_path)
        messagebox.showinfo("Success", f"File compressed to: {compressed_file_path}")

# Создание основного окна
root = tk.Tk()
root.title("File Compressor")

# Кнопка для сжатия файла
compress_button = tk.Button(root, text="Compress File", command=compress_file)
compress_button.pack(pady=20)

# Запуск интерфейса
root.mainloop()