import pandas as pd
import random

def realizar_sorteio(df_times, times_fixos=None):
    # Se não houver times fixos passados, cria um dicionário vazio
    if times_fixos is None:
        times_fixos = {}
        
    # Cria os 16 grupos de A até P vazios
    grupos = {chr(65 + i): [] for i in range(16)}
    
    # 1. ALOCAÇÃO PRÉVIA DOS CABEÇAS DE CHAVE FIXOS
    times_fixados_nomes = []
    for nome_grupo, sigla_time in times_fixos.items():
        # Encontra os dados do time na tabela pelo nome (sigla)
        time_dados = df_times[df_times['TIME'] == sigla_time].to_dict('records')
        if time_dados:
            grupos[nome_grupo].append(time_dados[0])
            times_fixados_nomes.append(sigla_time)

    # 2. INÍCIO DO SORTEIO DO POTE 1 AO 4
    for pote_atual in range(1, 5):
        # Filtra os times do pote atual, MAS REMOVE os times que já foram fixados
        times_pote = df_times[
            (df_times['POTE'] == pote_atual) & 
            (~df_times['TIME'].isin(times_fixados_nomes))
        ].to_dict('records')
        
        # Embaralha as bolinhas que sobraram
        random.shuffle(times_pote)
        
        for time in times_pote:
            alocado = False
            confed = time['CONFEDERAÇÃO']
            
            # Tenta encaixar o time nos grupos de A a P
            for nome_grupo, times_no_grupo in grupos.items():
                
                # Regra 2: Cada grupo só recebe 1 time de cada pote
                if len(times_no_grupo) == pote_atual:
                    continue
                
                # Regra 3: Limite por confederação (Máx 2 UEFA, Máx 1 para as outras)
                qtd_mesma_confed = sum(1 for t in times_no_grupo if t['CONFEDERAÇÃO'] == confed)
                limite = 2 if confed == 'UEFA' else 1
                
                if qtd_mesma_confed >= limite:
                    continue # Já atingiu o limite, tenta o próximo grupo
                
                # Regra de Segurança: Garantir pelo menos 1 time da UEFA por grupo
                vagas_vazias = 4 - len(times_no_grupo)
                tem_uefa = any(t['CONFEDERAÇÃO'] == 'UEFA' for t in times_no_grupo)
                
                if not tem_uefa and vagas_vazias == 1 and confed != 'UEFA':
                    continue 
                
                # Passou por todas as regras, o time entra
                grupos[nome_grupo].append(time)
                alocado = True
                break
            
            # Beco sem saída: o time não pôde entrar em nenhum grupo
            if not alocado:
                return None 
                
    # Validação Final de Segurança
    for times in grupos.values():
        if not any(t['CONFEDERAÇÃO'] == 'UEFA' for t in times):
            return None 
            
    return grupos

def main():
    print("Iniciando simulação do sorteio da Copa do Mundo...\n")
    
    try:
        df = pd.read_excel('times.xlsx')
    except FileNotFoundError:
        print("Erro: O arquivo 'times.xlsx' não foi encontrado.")
        return

    # --- CONFIGURAÇÃO DOS PAÍSES SEDE ---
    # Ex: {'A': 'ESP', 'B': 'POR', 'C': 'MAR'}
    alocacoes_fixas = {
        'A': 'ESP', 
        'D': 'POR',
        'F': 'MAR',
        'I': 'ARG',
        'L': 'PAR',
        'O': 'URU'
    }

    tentativas = 0
    grupos_sorteados = None
    
    # Loop de tentativas até achar um sorteio válido
    while grupos_sorteados is None:
        tentativas += 1
        grupos_sorteados = realizar_sorteio(df, times_fixos=alocacoes_fixas)
        
    print(f"Sorteio concluído com sucesso (após {tentativas} tentativa(s) interna(s)).\n")
    
    dados_exportacao = []
    
    for nome_grupo, times in grupos_sorteados.items():
        print(f"--- GRUPO {nome_grupo} ---")
        for i, time in enumerate(times):
            # Formata a exibição para mostrar se o time foi pré-fixado
            status = " [PAÍS SEDE]" if time['TIME'] in alocacoes_fixas.values() else ""
            print(f"Pote {time['POTE']}: {time['TIME']} ({time['CONFEDERAÇÃO']}){status}")
            
            dados_exportacao.append({
                'Grupo': nome_grupo,
                'Pote': time['POTE'],
                'Time': time['TIME'],
                'Confederação': time['CONFEDERAÇÃO'],
                'Status': 'Sede' if status else 'Sorteado'
            })
        print()
        
    df_exportacao = pd.DataFrame(dados_exportacao)
    df_exportacao.to_excel('grupos_sorteados.xlsx', index=False)
    print("Sucesso! Os grupos foram salvos no arquivo 'grupos_sorteados.xlsx'.")

if __name__ == "__main__":
    main()