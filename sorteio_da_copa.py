import pandas as pd
import random

def realizar_sorteio(df_times):
    # Cria os 16 grupos de A até P vazios
    grupos = {chr(65 + i): [] for i in range(16)}
    
    # Sorteia do pote 1 ao pote 4
    for pote_atual in range(1, 5):
        times_pote = df_times[df_times['POTE'] == pote_atual].to_dict('records')
        random.shuffle(times_pote)
        
        for time in times_pote:
            alocado = False
            confed = time['CONFEDERAÇÃO']
            
            # Tenta encaixar o time nos grupos de A a P
            for nome_grupo, times_no_grupo in grupos.items():
                
                # Regra 2: Cada grupo só recebe 1 time de cada pote (respeita a ordem dos potes)
                if len(times_no_grupo) == pote_atual:
                    continue
                
                # Regra 3: Limite por confederação (Máx 2 UEFA, Máx 1 para as outras)
                qtd_mesma_confed = sum(1 for t in times_no_grupo if t['CONFEDERAÇÃO'] == confed)
                limite = 2 if confed == 'UEFA' else 1
                
                if qtd_mesma_confed >= limite:
                    continue # Já atingiu o limite dessa confederação no grupo, vai pro próximo
                
                # NOVA REGRA: Garantir pelo menos 1 time da UEFA por grupo
                vagas_vazias = 4 - len(times_no_grupo)
                tem_uefa = any(t['CONFEDERAÇÃO'] == 'UEFA' for t in times_no_grupo)
                
                # Se o grupo só tem mais 1 vaga e ainda não tem UEFA, APENAS um time UEFA pode entrar
                if not tem_uefa and vagas_vazias == 1 and confed != 'UEFA':
                    continue 
                
                # Se passou por todas as regras, o time entra no grupo
                grupos[nome_grupo].append(time)
                alocado = True
                break
            
            # Beco sem saída: o time não pôde entrar em nenhum grupo
            if not alocado:
                return None 
                
    # Validação Final de Segurança: Verifica se TODOS os grupos têm pelo menos 1 UEFA
    for times in grupos.values():
        if not any(t['CONFEDERAÇÃO'] == 'UEFA' for t in times):
            return None # Se algum grupo não tiver UEFA, descarta e tenta de novo
            
    return grupos

def main():
    print("Iniciando simulação do sorteio da Copa do Mundo...\n")
    
    try:
        df = pd.read_excel('times.xlsx')
    except FileNotFoundError:
        print("Erro: O arquivo 'times.xlsx' não foi encontrado.")
        return

    tentativas = 0
    grupos_sorteados = None
    
    # Loop de tentativas até achar um sorteio 100% válido
    while grupos_sorteados is None:
        tentativas += 1
        grupos_sorteados = realizar_sorteio(df)
        
    print(f"Sorteio concluído com sucesso (após {tentativas} tentativa(s) interna(s)).\n")
    
    dados_exportacao = []
    
    for nome_grupo, times in grupos_sorteados.items():
        print(f"--- GRUPO {nome_grupo} ---")
        for i, time in enumerate(times):
            print(f"Pote {i+1}: {time['TIME']} ({time['CONFEDERAÇÃO']})")
            
            dados_exportacao.append({
                'Grupo': nome_grupo,
                'Pote': time['POTE'],
                'Time': time['TIME'],
                'Confederação': time['CONFEDERAÇÃO']
            })
        print()
        
    df_exportacao = pd.DataFrame(dados_exportacao)
    df_exportacao.to_excel('grupos_sorteados.xlsx', index=False)
    print("Sucesso! Os grupos foram salvos no arquivo 'grupos_sorteados.xlsx'.")

if __name__ == "__main__":
    main()