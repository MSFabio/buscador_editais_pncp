import os
import chromadb
from chromadb.utils import embedding_functions

# Configurações do Banco Vetorial
CHROMA_DATA_DIR = "./chroma_data"
# Modelo sugerido para português, com bom balanço entre tamanho e precisão
MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"

class VectorSearch:
    def __init__(self, persist_directory=CHROMA_DATA_DIR):
        # Garante que o diretório exista
        os.makedirs(persist_directory, exist_ok=True)
        
        # Inicializa o cliente ChromaDB persistente
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Inicializa a função de embedding (fará o download do modelo na 1ª vez)
        print(f"[VectorSearch] Carregando modelo '{MODEL_NAME}' (pode demorar na primeira vez)...")
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=MODEL_NAME)
        
        # Cria ou obtém a coleção de editais
        self.collection = self.client.get_or_create_collection(
            name="editais_pncp",
            embedding_function=self.embedding_fn
        )
        print("[VectorSearch] Pronto.")

    def clear_collection(self):
        """Limpa a coleção atual (útil para testes ou refresh completo)"""
        try:
            self.client.delete_collection(name="editais_pncp")
            self.collection = self.client.create_collection(
                name="editais_pncp",
                embedding_function=self.embedding_fn
            )
        except Exception:
            pass

    def add_editais(self, editais: list[dict]):
        """
        Adiciona uma lista de editais (dicionários do PNCP) ao banco vetorial.
        Converte as informações textuais relevantes para gerar o embedding.
        """
        if not editais:
            return

        documents = []
        metadatas = []
        ids = []

        for edital in editais:
            # Identificador único
            num_controle = edital.get('numeroControlePNCP')
            if not num_controle:
                continue
                
            # Monta o texto que será vetorizado e usado para a busca semântica
            objeto = edital.get('objetoCompra', '')
            info_complementar = edital.get('informacaoComplementar', '')
            orgao = edital.get('orgaoEntidade', {}).get('razaoSocial', '')
            
            # O documento semântico é uma composição descritiva
            documento = f"Órgão: {orgao}. Objeto: {objeto}. Informações Adicionais: {info_complementar}."
            
            documents.append(documento)
            
            # Os metadados guardam o resto para podermos reconstruir o resultado
            metadatas.append({
                "numeroControlePNCP": num_controle,
                "dataAbertura": edital.get('dataAberturaProposta', ''),
                "valorEstimado": float(edital.get('valorTotalEstimado', 0.0) or 0.0)
            })
            
            ids.append(num_controle)

        # Adiciona em lotes (batching) se houver muitos, ou de uma vez
        # A API do Chroma suporta até ~41666 itens por vez no SQLite
        try:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            print(f"[VectorSearch] {len(ids)} editais indexados no ChromaDB.")
        except Exception as e:
            # Ignora erros de "ID já existe" se tentarmos adicionar o mesmo edital
            print(f"[VectorSearch] Aviso ao indexar: {e}")


    def search_editais(self, query: str, n_results: int = 10, max_distance: float = 1.0, where_filter: dict = None) -> list[dict]:
        """
        Busca os editais mais similares contextualmente à query.
        Retorna os IDs e os scores de distância.
        Quanto MENOR a distância, MAIOR a similaridade.
        """
        if self.collection.count() == 0:
            return []

        # Não podemos pedir mais resultados do que o tamanho da coleção
        n_results = min(n_results, self.collection.count())
        
        kwargs = {
            "query_texts": [query],
            "n_results": n_results
        }
        if where_filter:
            kwargs["where"] = where_filter

        results = self.collection.query(**kwargs)

        
        matches = []
        if results and results['ids'] and len(results['ids']) > 0:
            # results é estruturado como listas de listas (uma por query)
            ids = results['ids'][0]
            distances = results['distances'][0]
            
            for edital_id, distance in zip(ids, distances):
                if distance <= max_distance:
                    matches.append({
                        "numeroControlePNCP": edital_id,
                        "distancia": distance
                    })
                    
        return matches
