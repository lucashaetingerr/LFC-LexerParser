import tkinter as tk
from tkinter import filedialog,scrolledtext,messagebox, font as tkfont
import json
import time


#dimensoes e componentes da interface tkinter
LARGURA_JANELA_PADRAO=1280
ALTURA_JANELA_PADRAO=720
COR_FUNDO_APP="#f0f2f5"
COR_FUNDO_WIDGETS="#ffffff"
COR_TEXTO_PADRAO="#212529"
COR_TEXTO_SECUNDARIO="#495057"
COR_TEXTO_PLACEHOLDER="#6c757d"
COR_TEXTO_TITULO_APP="#333333"
COR_PRIMARIA_BOTAO="#007bff"
COR_TEXTO_BOTAO_CLARO="#ffffff"
COR_PRIMARIA_BOTAO_HOVER="#0056b3"
COR_SECUNDARIA_BOTAO="#6c757d"
COR_SECUNDARIA_BOTAO_HOVER="#545b62"
COR_BOTAO_COPIAR_FUNDO="#e9ecef"
COR_BOTAO_COPIAR_TEXTO="#212529"
COR_SUCESSO_TEXTO_STATUS="#155724"
COR_ERRO_TEXTO_STATUS="#721c24"
COR_TERMINAL_FUNDO_ESCURO="#1e1e1e"
COR_TERMINAL_TEXTO_CLARO="#dcdcdc"
COR_TERMINAL_TEXTO_ERRO="#ff7b7b"
FONTE_FAMILIA_PADRAO="Segoe UI"
FONTE_FAMILIA_MONOESPACADA="Consolas"


try:
    from parser import parse_dsl_from_string
except ImportError:
    messagebox.showerror("Erro de Importação Crítico",#tab titulo
                         "O arquivo 'parser.py' não foi encontrado ou está com problemas.\n"
                         "Verifique se ele está no mesmo diretório que este script.")
    exit()



class AnalisadorDSLAppTk:
    def __init__(self, janela_mestra_tk):
        self.janela_mestra=janela_mestra_tk
        janela_mestra_tk.title("Trabalho de LFC - APIs")
        janela_mestra_tk.configure(bg=COR_FUNDO_APP)


        self.fonte_padrao_ui=tkfont.Font(family=FONTE_FAMILIA_PADRAO, size=11)
        self.fonte_label_ui=tkfont.Font(family=FONTE_FAMILIA_PADRAO, size=12, weight="bold")
        self.fonte_titulo_app_ui=tkfont.Font(family=FONTE_FAMILIA_PADRAO, size=21, weight="bold")
        self.fonte_terminal_ui=tkfont.Font(family=FONTE_FAMILIA_MONOESPACADA, size=11)


        largura_tela=janela_mestra_tk.winfo_screenwidth()
        altura_tela=janela_mestra_tk.winfo_screenheight()
        pos_x=(largura_tela//2)-(LARGURA_JANELA_PADRAO//2)
        pos_y=(altura_tela//2)-(ALTURA_JANELA_PADRAO//2)
        janela_mestra_tk.geometry(f"{LARGURA_JANELA_PADRAO}x{ALTURA_JANELA_PADRAO}+{pos_x}+{pos_y}")
        janela_mestra_tk.minsize(900,650)


        self.conteudo_arquivo_lido=None
        self.nome_arquivo_atual_dsl=""


        self._criar_componentes_interface()



    def _criar_componentes_interface(self):
        frame_centralizador_geral=tk.Frame(self.janela_mestra,bg=COR_FUNDO_APP)
        frame_centralizador_geral.pack(expand=True,fill=tk.BOTH)

        frame_area_principal=tk.Frame(frame_centralizador_geral,bg=COR_FUNDO_WIDGETS,
                                      relief=tk.RIDGE, bd=1,padx=35,pady=35)
        frame_area_principal.place(relx=0.5, rely=0.5, anchor=tk.CENTER,width=900,height=680)

        tk.Label(frame_area_principal,text="LFC - Integração API com API",
                 font=self.fonte_titulo_app_ui,bg=COR_FUNDO_WIDGETS, fg=COR_TEXTO_TITULO_APP
                 ).pack(pady=(0, 30))


        frame_label_instrucao_arquivo=tk.Frame(frame_area_principal, bg=COR_FUNDO_WIDGETS)
        frame_label_instrucao_arquivo.pack(pady=(0,5))#pack() centraliza por padrao no frame_area_principal


        tk.Label(frame_label_instrucao_arquivo, text="Selecione um arquivo no formato esperado e com a extenção `.txt`",
                 font=self.fonte_label_ui,bg=COR_FUNDO_WIDGETS,fg=COR_TEXTO_SECUNDARIO).pack()#p/ label vai se ajustar ao texto


        frame_botao_selecao_container=tk.Frame(frame_area_principal, bg=COR_FUNDO_WIDGETS)
        frame_botao_selecao_container.pack(pady=(5,10))

        self.widget_botao_procurar=tk.Button(frame_botao_selecao_container, text="Procurar Arquivo...",
                                             font=self.fonte_padrao_ui,command=self.evento_selecionar_arquivo,
                                             relief=tk.GROOVE, bd=1,width=25, # Largura ajustada
                                             bg=COR_SECUNDARIA_BOTAO,fg=COR_TEXTO_BOTAO_CLARO,
                                             activebackground=COR_SECUNDARIA_BOTAO_HOVER, activeforeground=COR_TEXTO_BOTAO_CLARO)
        self.widget_botao_procurar.pack()


        self.widget_label_status_arquivo=tk.Label(frame_area_principal,text="Nenhum arquivo selecionado.",
                                                  font=self.fonte_padrao_ui,bg=COR_FUNDO_WIDGETS,
                                                  fg=COR_TEXTO_PLACEHOLDER
                                                  #justify=tk.CENTER nao eh necessario se o proprio Label
                                                  #nao preenche X e o frame pai o centraliza
                                                  )
        self.widget_label_status_arquivo.pack(pady=(0,20))


        frame_grupo_botoes_acao=tk.Frame(frame_area_principal, bg=COR_FUNDO_WIDGETS)
        frame_grupo_botoes_acao.pack(pady=15)


        self.widget_botao_analisar=tk.Button(frame_grupo_botoes_acao,text="Analisar Código",
                                             font=self.fonte_padrao_ui,command=self.evento_analisar_dsl,
                                             state=tk.DISABLED, relief=tk.GROOVE, bd=1, width=20,
                                             bg=COR_PRIMARIA_BOTAO,fg=COR_TEXTO_BOTAO_CLARO,
                                             activebackground=COR_PRIMARIA_BOTAO_HOVER, activeforeground=COR_TEXTO_BOTAO_CLARO)
        self.widget_botao_analisar.pack(side=tk.LEFT,padx=10)



        self.widget_botao_limpar=tk.Button(frame_grupo_botoes_acao, text="Limpar Interface",
                                          font=self.fonte_padrao_ui,command=self.evento_limpar_interface,
                                          relief=tk.GROOVE,bd=1,width=20,
                                          bg=COR_SECUNDARIA_BOTAO,fg=COR_TEXTO_BOTAO_CLARO,
                                          activebackground=COR_SECUNDARIA_BOTAO_HOVER, activeforeground=COR_TEXTO_BOTAO_CLARO)
        self.widget_botao_limpar.pack(side=tk.LEFT,padx=10)

        self.widget_frame_resultado_analise=tk.Frame(frame_area_principal,bg=COR_FUNDO_WIDGETS)

        tk.Label(self.widget_frame_resultado_analise, text="Resultado da Análise:",
                 font=self.fonte_label_ui, bg=COR_FUNDO_WIDGETS,fg=COR_TEXTO_SECUNDARIO).pack(anchor="w",pady=(20, 5))



        self.widget_area_terminal=scrolledtext.ScrolledText(self.widget_frame_resultado_analise, wrap=tk.WORD,
                                                            font=self.fonte_terminal_ui, height=15,
                                                            bg=COR_TERMINAL_FUNDO_ESCURO,fg=COR_TERMINAL_TEXTO_CLARO,
                                                            relief=tk.SUNKEN,bd=1,
                                                            insertbackground=COR_TERMINAL_TEXTO_CLARO)
        self.widget_area_terminal.pack(expand=True,fill=tk.BOTH, pady=(0,10))
        self.widget_area_terminal.tag_config("erro_de_sintaxe",foreground=COR_TERMINAL_TEXTO_ERRO,font=(FONTE_FAMILIA_MONOESPACADA,self.fonte_terminal_ui.cget("size"), "bold"))


        self.widget_botao_copiar =tk.Button(self.widget_frame_resultado_analise, text="📋 Copiar Resultado",
                                           font=self.fonte_padrao_ui,
                                           state=tk.DISABLED, relief=tk.GROOVE, bd=1,
                                           bg=COR_BOTAO_COPIAR_FUNDO, fg=COR_BOTAO_COPIAR_TEXTO,
                                           activebackground="#d3d3d3")
        self.widget_botao_copiar.pack(pady=5)

        self._gerenciar_visibilidade_resultado(mostrar=False)


    def _gerenciar_visibilidade_resultado(self, mostrar):
        if mostrar:
            if not self.widget_frame_resultado_analise.winfo_ismapped():
                self.widget_frame_resultado_analise.pack(expand=True, fill=tk.BOTH,pady=(10,0),padx=5)
        else:
            if self.widget_frame_resultado_analise.winfo_ismapped():
                self.widget_frame_resultado_analise.pack_forget()
            self.widget_area_terminal.config(state=tk.NORMAL)
            self.widget_area_terminal.delete("1.0",tk.END)
            self.widget_area_terminal.config(state=tk.DISABLED)
            self.widget_botao_copiar.config(state=tk.DISABLED)



    def evento_selecionar_arquivo(self):
        caminho_arquivo_dsl= filedialog.askopenfilename(
            title="Selecionar Arquivo",
            filetypes=(("Arquivos de Texto", "*.txt"),("Todos os Arquivos", "*.*"))
        )
        if not caminho_arquivo_dsl:
            if not self.conteudo_arquivo_lido:
                self.widget_label_status_arquivo.config(text="Nenhum arquivo selecionado.",fg=COR_TEXTO_PLACEHOLDER)
            return
        
        self._gerenciar_visibilidade_resultado(mostrar=False)
        
        try:
            with open(caminho_arquivo_dsl,'r',encoding='utf-8') as f_aberto:
                self.conteudo_arquivo_lido=f_aberto.read()
            self.nome_arquivo_atual_dsl=caminho_arquivo_dsl.split('/')[-1]
            self.widget_label_status_arquivo.config(text=f"Arquivo Carregado: {self.nome_arquivo_atual_dsl}",fg=COR_SUCESSO_TEXTO_STATUS)
            self.widget_botao_analisar.config(state=tk.NORMAL)
        except Exception as e_leitura:
            self.conteudo_arquivo_lido=None
            self.nome_arquivo_atual_dsl=""
            self.widget_label_status_arquivo.config(text="Erro ao carregar o arquivo!",fg=COR_ERRO_TEXTO_STATUS)
            messagebox.showerror("Erro na Leitura do Arquivo",
                                 f"Não foi possível ler o arquivo selecionado:\n'{caminho_arquivo_dsl}'.\n\nDetalhes: {e_leitura}")
            self.widget_botao_analisar.config(state=tk.DISABLED)

    def evento_analisar_dsl(self):
        if not self.conteudo_arquivo_lido:
            messagebox.showwarning("Ação Necessária", "Por favor, selecione um arquivo com código válido antes de prosseguir.")
            return


        self._gerenciar_visibilidade_resultado(mostrar=True)
        self.widget_area_terminal.config(state=tk.NORMAL)
        self.widget_area_terminal.delete("1.0",tk.END)
        self.widget_area_terminal.insert("1.0",f"Analisando o arquivo '{self.nome_arquivo_atual_dsl}'...\nPor favor, aguarde um momento.\n\n")
        self.widget_area_terminal.config(state=tk.DISABLED)
        self.widget_botao_copiar.config(state=tk.DISABLED)
        self.janela_mestra.update_idletasks()#p/ atualizar a interface
        time.sleep(0.3)
        

        resultado_analise_ast, erros_detectados_parser=None, None
        try:
            resultado_analise_ast, erros_detectados_parser=parse_dsl_from_string(self.conteudo_arquivo_lido)
            

            self.widget_area_terminal.config(state=tk.NORMAL)
            self.widget_area_terminal.delete("1.0", tk.END)
            

            if erros_detectados_parser:
                self.widget_area_terminal.insert("1.0", "Erros de Sintaxe Encontrados durante a Análise:\n\n")
                for erro_individual in erros_detectados_parser:
                    self.widget_area_terminal.insert(tk.END, f"• {erro_individual}\n", "erro_de_sintaxe")
                self.widget_area_terminal.insert(tk.END, "\nAnálise concluída com um ou mais erros de sintaxe.")
                self.widget_botao_copiar.config(state=tk.DISABLED)
            elif resultado_analise_ast:
                try:
                    json_para_exibicao=json.dumps(resultado_analise_ast, indent=2, ensure_ascii=False)
                    self.widget_area_terminal.insert("1.0", json_para_exibicao)
                    self.widget_botao_copiar.config(state=tk.NORMAL)
                except TypeError as e_json_type:
                    msg_erro_format_json=(f"Erro Interno ao Gerar Saída JSON:\n"
                                          f"A estrutura de dados resultante não pôde ser convertida para JSON.\n"
                                          f"Detalhes: {e_json_type}\n\n"
                                          f"Estrutura Bruta (string):\n{resultado_analise_ast}")
                    self.widget_area_terminal.insert("1.0", msg_erro_format_json, "erro_de_sintaxe")
                    self.widget_botao_copiar.config(state=tk.DISABLED)
                    messagebox.showerror("Erro de Formatação da Saída", "Falha ao converter o resultado para JSON.")
            else:
                self.widget_area_terminal.insert("1.0",
                                                "Falha Inesperada na Análise:\n"
                                                "O processo de análise não produziu um resultado válido nem erros específicos.\n"
                                                "Consulte o console do sistema para possíveis mensagens de debug do analisador.", "erro_de_sintaxe")
                self.widget_botao_copiar.config(state=tk.DISABLED)
        except Exception as e_geral_analise:
            self.widget_area_terminal.config(state=tk.NORMAL)
            self.widget_area_terminal.delete("1.0", tk.END)
            self.widget_area_terminal.insert("1.0", f"Erro Crítico Durante a Análise do Código:\n\n"
                                                  f"Tipo: {type(e_geral_analise).__name__}\n"
                                                  f"Mensagem: {e_geral_analise}", "erro_de_sintaxe")
            self.widget_botao_copiar.config(state=tk.DISABLED)
            messagebox.showerror("Erro Inesperado na Aplicação",
                                 f"Ocorreu uma falha crítica:\n{e_geral_analise}")
        finally:
            self.widget_area_terminal.config(state=tk.DISABLED)



    def evento_limpar_interface(self):
        self.conteudo_arquivo_lido=None
        self.nome_arquivo_atual_dsl=""
        self.widget_label_status_arquivo.config(text="Nenhum arquivo selecionado.",fg=COR_TEXTO_PLACEHOLDER)
        self.widget_botao_analisar.config(state=tk.DISABLED)
        self._gerenciar_visibilidade_resultado(mostrar=False)


if __name__== "__main__":
    root_window=tk.Tk()
    app_gui=AnalisadorDSLAppTk(root_window)
    root_window.mainloop()
