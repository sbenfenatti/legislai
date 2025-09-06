#!/usr/bin/env python3
import os
import zipfile
import glob

# Encontrar o arquivo ZIP na pasta
zip_files = glob.glob('/workspace/user_input_files/*.zip')
if not zip_files:
    print("Nenhum arquivo ZIP encontrado!")
    exit(1)

zip_path = zip_files[0]
print(f"Encontrado arquivo ZIP: {zip_path}")

# Extrair o arquivo
extract_path = '/workspace/backend_files'
os.makedirs(extract_path, exist_ok=True)

try:
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)
        print(f"Arquivo extraído para: {extract_path}")
        
        # Listar arquivos extraídos
        print("\nArquivos extraídos:")
        for root, dirs, files in os.walk(extract_path):
            for file in files:
                file_path = os.path.join(root, file)
                print(file_path)
                
except Exception as e:
    print(f"Erro ao extrair: {e}")