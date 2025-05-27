import ply.lex as lex


tokens=(
    'MAPA_API', 'API', 'RECURSO', 'DE', 'PARA', 'EM', 'METODO',
    'PARAMETRO', 'CAMPO', 'FORMATO', 'TRANSFORMAR', 'VALOR',
    'CONVERTER', 'COM', 'CABECALHO', 'FUNCAO',
    'LBRACE', 'RBRACE', 'SEMICOLON', 'COLON', 'LPAREN', 'RPAREN', 'COMMA', 'DOT',
    'IDENTIFIER', 'STRING',
    'OPERATOR_EQ', 'OPERATOR_ASSIGN',
)


#palavras reservadas e seus tokens correspondentes
palavras_reservadas={
    'MAPA_API':'MAPA_API',
    'API':'API',
    'RECURSO':'RECURSO',
    'DE':'DE',
    'PARA':'PARA',
    'EM':'EM',
    'METODO':'METODO',
    'PARAMETRO':'PARAMETRO',
    'CAMPO':'CAMPO',
    'FORMATO':'FORMATO',
    'TRANSFORMAR':'TRANSFORMAR',
    'valor':'VALOR',#'valor' (minusculo)→ palavra-chave que gera o token VALOR
    'CONVERTER':'CONVERTER',
    'COM':'COM',
    'CABECALHO':'CABECALHO',
    'FUNCAO':'FUNCAO',
}

#expressoes regulares p/ tokens
t_LBRACE=r'\{'
t_RBRACE=r'\}'
t_SEMICOLON=r';'
t_COLON=r':'
t_LPAREN=r'\('
t_RPAREN=r'\)'
t_COMMA=r','
t_DOT=r'\.'
t_OPERATOR_EQ=r'=='
t_OPERATOR_ASSIGN=r'='


#regra para tratativas de strings (conteudo entre aspas duplas)
def t_STRING(t):
    r'"[^"]*"'
    t.value=t.value[1:-1]#remove as aspas delimitadoras
    return t


#regra para identificadores e checagem de palavra reservada
def t_IDENTIFIER(t):
    r'[a-zA-Z_][a-zA-Z_0-9-]*'#permite letras, numeros, underscore, e hifen (mas nao no inicio)
    t.type=palavras_reservadas.get(t.value,'IDENTIFIER')#verifica se o valor do token é uma palavra reservada
    return t


#regra para ignorar comentarios de linha (comecando com //) conforme exemplo do professor no fórum
def t_COMMENT(t):
    r'//.*'
    pass  #nenhum token é retornado quando for comentario


#regra para rastrear numeros de linha e a posicao do inicio da linha
def t_newline(t):
    r'\n+'#uma ou mais novas linhas
    t.lexer.lineno+=len(t.value)#incrementa o contador de linhas
    t.lexer.linepos=t.lexpos    #armazena a posicao absoluta do token de nova linha
                                #usado para calcular a coluna de erros com precisao


#string contendo caracteres a serem ignorados (espaços e tabs)
t_ignore = ' \t'


#funcao para tratamento de erro lexico (caracteres invalidos)
def t_error(t):
    coluna=t.lexpos-t.lexer.linepos #calcula a coluna relativa ao inicio da linha
    print(f"LEXER ERRO: Caractere nao reconhecido '{t.value[0]}' na linha {t.lexer.lineno}, coluna {coluna + 1}.")#coluna +1 para ser 1-indexed
    t.lexer.skip(1)#pula o caractere invalido e tenta continuar



lexer=lex.lex()
lexer.linepos=0 #inicializa a posicao do inicio da linha. A primeira linha comeca na posicao 0 do input.