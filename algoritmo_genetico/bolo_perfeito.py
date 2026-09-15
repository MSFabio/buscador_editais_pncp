import sys
import random

# Configura a saída padrão para UTF-8 no terminal Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# ==========================================
# BLOCO 1: AMBIENTE E FUNÇÃO DE APTIDÃO (FITNESS)
# ==========================================
RECEITA_PERFEITA = [50, 30, 20]  # Farinha: 50g, Açúcar: 30g, Fermento: 20g

def calcular_fitness(tentativa_bolo):
    """Calcula a soma das diferenças absolutas em relação à receita perfeita.
    Quanto mais próximo de 0, melhor!"""
    erro_total = 0
    for i in range(len(tentativa_bolo)):
        erro_total += abs(tentativa_bolo[i] - RECEITA_PERFEITA[i])
    return erro_total

def gerar_bolo_aleatorio():
    """Gera uma receita aleatória com valores entre 0 e 100 para cada ingrediente."""
    return [random.randint(0, 100), random.randint(0, 100), random.randint(0, 100)]

# ==========================================
# BLOCO 2: SELEÇÃO DOS PAIS (TORNEIO)
# ==========================================
def selecionar_pai(populacao, tamanho_torneio=3):
    competidores = random.sample(populacao, tamanho_torneio)
    competidores.sort(key=calcular_fitness)
    return competidores[0]

# ==========================================
# BLOCO 3: CRUZAMENTO (CROSSOVER) E MUTAÇÃO
# ==========================================
def cruzar(pai1, pai2):
    ponto_corte = random.randint(1, 2)
    filho = pai1[:ponto_corte] + pai2[ponto_corte:]
    return filho

def mutar(bolo, taxa_mutacao=0.25, escala_mutacao=5):
    bolo_mutado = bolo.copy()
    for i in range(len(bolo_mutado)):
        if random.random() < taxa_mutacao:
            variacao = random.randint(-escala_mutacao, escala_mutacao)
            bolo_mutado[i] = max(0, min(100, bolo_mutado[i] + variacao))
    return bolo_mutado

# ==========================================
# BLOCO 4: CICLO EVOLUTIVO
# ==========================================
def main():
    random.seed(42)  # Semente fixa para reprodutibilidade demonstrativa
    
    TAMANHO_POPULACAO = 20
    GERACOES = 60
    TAXA_MUTACAO = 0.3
    
    print("=" * 55)
    print("🍰 LABORATÓRIO: A RECEITA DO BOLO PERFEITO COM AG")
    print("=" * 55)
    print(f"🎯 Receita Secreta (Alvo): {RECEITA_PERFEITA}\n")
    
    # Geração 0 (População Inicial)
    populacao = [gerar_bolo_aleatorio() for _ in range(TAMANHO_POPULACAO)]
    
    print("--- 📌 Geração 0: Amostra da População Inicial ---")
    for i in range(min(5, len(populacao))):
        print(f"Bolo {i+1}: {populacao[i]} -> Erro (Fitness): {calcular_fitness(populacao[i])}")
    print()
    
    print("--- 🚀 Evolução pelas Gerações ---")
    melhor_da_geracao = None
    geracao_sucesso = None
    
    for geracao in range(1, GERACOES + 1):
        populacao.sort(key=calcular_fitness)
        melhor_da_geracao = populacao[0]
        melhor_fitness = calcular_fitness(melhor_da_geracao)
        
        # Exibe progresso a cada 10 gerações ou quando atinge perfeição
        if geracao == 1 or geracao % 10 == 0 or melhor_fitness == 0:
            print(f"Geração {geracao:02d} | Melhor Bolo: {melhor_da_geracao} | Erro: {melhor_fitness}")
            
        if melhor_fitness == 0:
            geracao_sucesso = geracao
            print(f"\n🎉 Parabéns! Bolo perfeito encontrado na Geração {geracao}!")
            break
            
        nova_populacao = []
        # Elitismo: preserva o campeão atual
        nova_populacao.append(melhor_da_geracao)
        
        while len(nova_populacao) < TAMANHO_POPULACAO:
            pai1 = selecionar_pai(populacao)
            pai2 = selecionar_pai(populacao)
            filho = cruzar(pai1, pai2)
            filho = mutar(filho, taxa_mutacao=TAXA_MUTACAO)
            nova_populacao.append(filho)
            
        populacao = nova_populacao
        
    print("\n" + "=" * 55)
    print(f"Resultado Final:")
    print(f"- Receita Alvo:     {RECEITA_PERFEITA}")
    print(f"- Melhor Encontrado: {melhor_da_geracao}")
    print(f"- Erro Final:        {calcular_fitness(melhor_da_geracao)}")
    if geracao_sucesso:
        print(f"- Convergência em:   {geracao_sucesso} gerações")
    print("=" * 55)

if __name__ == "__main__":
    main()
