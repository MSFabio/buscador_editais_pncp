import pandas as pd
import requests
import time
import argparse

def get_locations_batch(ips):
    """
    Busca a localização de uma lista de IPs usando a API em lote (batch) do ip-api.com.
    Máximo de 100 IPs por requisição.
    """
    try:
        response = requests.post('http://ip-api.com/batch', json=ips)
        response.raise_for_status()
        data = response.json()
        
        results = {}
        for item in data:
            if item.get('status') == 'success':
                results[item['query']] = {
                    'País': item.get('country'),
                    'Estado/Região': item.get('regionName'),
                    'Cidade': item.get('city'),
                    'Latitude': item.get('lat'),
                    'Longitude': item.get('lon'),
                    'Provedor (ISP)': item.get('isp')
                }
            else:
                results[item.get('query')] = {
                    'País': None, 'Estado/Região': None, 'Cidade': None,
                    'Latitude': None, 'Longitude': None, 'Provedor (ISP)': None
                }
        return results
    except Exception as e:
        print(f"Erro na consulta em lote: {e}")
        return {}

def process_spreadsheet(input_file, output_file, ip_column):
    print(f"Lendo planilha: {input_file} (Isso pode levar alguns segundos dependendo do tamanho...)")
    
    if input_file.endswith('.csv'):
        df = pd.read_csv(input_file)
    else:
        df = pd.read_excel(input_file)
        
    if ip_column not in df.columns:
        raise ValueError(f"Coluna '{ip_column}' não encontrada. Colunas disponíveis: {', '.join(df.columns)}")
        
    total_rows = len(df)
    unique_ips = df[ip_column].dropna().unique().tolist()
    print(f"Total de linhas: {total_rows}. Total de IPs únicos a consultar: {len(unique_ips)}.")
    
    # Processa os IPs únicos em lotes de 100
    location_map = {}
    batch_size = 100
    
    for i in range(0, len(unique_ips), batch_size):
        batch = unique_ips[i:i+batch_size]
        print(f"Consultando lote de IPs [{i+1} a {min(i+batch_size, len(unique_ips))}]...")
        
        batch_results = get_locations_batch(batch)
        location_map.update(batch_results)
        
        # Pausa para respeitar o limite de 15 requisições/minuto no endpoint de batch
        if i + batch_size < len(unique_ips):
            time.sleep(4) 
            
    print("Mapeando resultados de volta para a planilha...")
    # Prepara listas vazias para preencher o dataframe
    countries, regions, cities, lats, lons, isps = [], [], [], [], [], []
    
    for ip in df[ip_column]:
        loc = location_map.get(ip, {})
        countries.append(loc.get('País'))
        regions.append(loc.get('Estado/Região'))
        cities.append(loc.get('Cidade'))
        lats.append(loc.get('Latitude'))
        lons.append(loc.get('Longitude'))
        isps.append(loc.get('Provedor (ISP)'))
        
    df['País'] = countries
    df['Estado/Região'] = regions
    df['Cidade'] = cities
    df['Latitude'] = lats
    df['Longitude'] = lons
    df['Provedor (ISP)'] = isps
    
    print("Salvando arquivo...")
    if output_file.endswith('.csv'):
        df.to_csv(output_file, index=False)
    else:
        df.to_excel(output_file, index=False)
        
    print(f"Processo concluído com sucesso! Arquivo salvo em: {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Correlacionar IPs de uma planilha com localização geográfica.")
    parser.add_argument("--input", "-i", required=True, help="Arquivo de entrada (CSV ou Excel)")
    parser.add_argument("--output", "-o", required=True, help="Arquivo de saída (CSV ou Excel)")
    parser.add_argument("--column", "-c", default="IP", help="Nome da coluna que contém os endereços IP")
    
    args = parser.parse_args()
    
    process_spreadsheet(args.input, args.output, args.column)
