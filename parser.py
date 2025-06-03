import ply.yacc as yacc
from lexer import tokens, lexer



parsed_api_map_config_global={}#variavel global para armazenar a estrutura parseada (AST simplificada). renomeada para evitar conflito com nome de regra
parser_gui_errors_list=[]



def p_error(p_token):
    global parser_gui_errors_list
    if p_token:
        linha_num=getattr(lexer,'lineno', p_token.lineno if hasattr(p_token,'lineno') else 0)
        posicao_lexica=p_token.lexpos if hasattr(p_token, 'lexpos') else -1
        posicao_inicio_linha=getattr(lexer, 'linepos', 0)
        coluna_calc=-1
        if posicao_lexica !=-1:
            coluna_calc=posicao_lexica - posicao_inicio_linha
        coluna_display=coluna_calc +1 if isinstance(coluna_calc, (int,float)) and coluna_calc !=-1 else '(desconhecida)'
        msg_erro_detalhada = (f"Erro de Sintaxe: Token inesperado '{p_token.value}' (tipo {p_token.type}) "
                              f"na linha {linha_num}, coluna ~{coluna_display} (posicao {posicao_lexica}).")
        parser_gui_errors_list.append(msg_erro_detalhada)
    else:
        msg_erro_generica = "Erro de Sintaxe: Fim inesperado do arquivo (EOF) ou erro antes do primeiro token."
        parser_gui_errors_list.append(msg_erro_generica)



#--- Regras da Gramatica ---
#PLY pega a primeira funcao p_... como regra inicial ou usa a variavel 'start'
#mantem os nomes das regras nas docstrings como PLY espera.
start='api_map_definition'# <<< DECLARA EXPLICITAMENTE A REGRA INICIAL


def p_api_map_definition(p):
    '''api_map_definition : MAPA_API LBRACE optional_declarations RBRACE'''
    global parsed_api_map_config_global
    conteudo_mapa=p[3] if p[3] is not None else []
    parsed_api_map_config_global = {'api_map_definition': conteudo_mapa}
    p[0]=parsed_api_map_config_global

def p_optional_declarations(p):
    '''optional_declarations : declarations
                             | empty_rule'''
    p[0]=p[1]

def p_declarations(p):
    '''declarations : declarations declaration
                    | declaration'''
    if len(p)==3:
        lista_base=p[1] if p[1] is not None else []
        item_atual=[p[2]] if p[2] is not None else []
        p[0]=lista_base + item_atual
    else:
        p[0]=[p[1]] if p[1] is not None else []
    p[0]=[item for item in p[0] if item is not None] if p[0] else []


def p_declaration(p):
    '''declaration : api_declaration
                   | resource_definition
                   | header_definition
                   | function_definition'''
    p[0]=p[1]



def p_api_declaration(p):
    '''api_declaration : API IDENTIFIER COLON STRING SEMICOLON'''
    p[0]={'declaration_type': 'api_source','logical_name': p[2],'base_url': p[4]}


def p_resource_definition(p):
    '''resource_definition : RECURSO STRING DE IDENTIFIER PARA STRING EM IDENTIFIER LBRACE optional_resource_body RBRACE'''
    lista_mapeamentos=p[10] if p[10] is not None else []
    p[0]={
        'declaration_type': 'resource_mapping',
        'source_endpoint': p[2],
        'source_api_ref': p[4],
        'target_endpoint': p[6],
        'target_api_ref': p[8],
        'mappings': lista_mapeamentos
    }



def p_optional_resource_body(p):
    '''optional_resource_body : resource_body
                               | empty_rule'''
    p[0]=p[1]

def p_resource_body(p):
    '''resource_body : resource_body resource_statement
                     | resource_statement'''
    if len(p)==3:
        lista_base=p[1] if p[1] is not None else []
        item_atual=[p[2]] if p[2] is not None else []
        p[0]=lista_base + item_atual
    else:
        p[0]=[p[1]] if p[1] is not None else []
    p[0]=[item for item in p[0] if item is not None] if p[0] else []


def p_resource_statement(p):
    '''resource_statement : method_definition
                          | parameter_definition
                          | field_definition
                          | transformation_definition'''
    p[0]=p[1]



def p_method_definition(p):
    '''method_definition : METODO IDENTIFIER PARA IDENTIFIER SEMICOLON'''
    p[0]={'mapping_type': 'http_method', 'source_method': p[2], 'target_method': p[4]}



def p_parameter_definition(p):
    '''parameter_definition : PARAMETRO STRING DE IDENTIFIER PARA STRING EM IDENTIFIER optional_parameter_converter SEMICOLON
                            | PARAMETRO STRING DE IDENTIFIER optional_parameter_converter SEMICOLON'''
    mapa_parametro={
        'mapping_type': 'query_parameter',
        'source_param_name': p[2],
        'source_api_ref': p[4]
    }
    idx_conversor=5
    if len(p)>7 and p[5]=='PARA':
        mapa_parametro['target_param_name']=p[6]
        mapa_parametro['target_api_ref']=p[8]
        idx_conversor=9
    else:
        mapa_parametro['target_param_name']=p[2]


    if len(p)>idx_conversor and p[idx_conversor] is not None:
        mapa_parametro['value_converter_function']=p[idx_conversor]
    p[0]=mapa_parametro



def p_optional_parameter_converter(p):
    '''optional_parameter_converter : LBRACE CONVERTER COM STRING SEMICOLON RBRACE
                                    | empty_rule'''
    if len(p)==6:
        p[0]=p[4]
    else:
        p[0]=None


def p_field_definition(p):
    '''field_definition : CAMPO STRING DE IDENTIFIER PARA STRING EM IDENTIFIER optional_format optional_converter SEMICOLON'''
    mapa_campo={
        'mapping_type':'body_field',
        'source_field_path':p[2],
        'source_api_ref':p[4],
        'target_field_path': p[6],
        'target_api_ref':p[8]
    }

    if p[9]:
        mapa_campo['format_conversion'] = p[9]
    if p[10]:
        mapa_campo['value_converter_function'] = p[10]
    p[0]=mapa_campo


def p_optional_format(p):
    '''optional_format : FORMATO STRING
                       | empty_rule'''
    if len(p)==3:
        p[0]=p[2]
    else:
        p[0]=None



def p_optional_converter(p):
    '''optional_converter : LBRACE CONVERTER COM STRING SEMICOLON RBRACE
                          | empty_rule'''
    if len(p)==6:
        p[0]=p[4]
    else:
        p[0]=None


def p_transformation_definition(p):
    '''transformation_definition : TRANSFORMAR VALOR source_condition PARA target_assignment SEMICOLON'''
    
    p[0]={
        'mapping_type': 'value_transformation',
        'source_condition_details':p[3],
        'target_assignment_details':p[5]
    }



def p_field_path_segments(p):#definido antes das regras que o usam
    '''field_path_segments : IDENTIFIER
                           | field_path_segments DOT IDENTIFIER'''
    if len(p)==2:
        p[0]=p[1]
    else:
        p[0]=f"{p[1]}.{p[3]}"



def p_source_condition(p):
    '''source_condition : IDENTIFIER DOT field_path_segments OPERATOR_EQ STRING'''
    p[0]={'api_ref': p[1],'field_path': p[3],'operator': p[4],'value_to_compare':p[5]}



def p_target_assignment(p):
    '''target_assignment : IDENTIFIER DOT field_path_segments OPERATOR_ASSIGN STRING'''
    p[0]={'api_ref': p[1], 'field_path': p[3], 'operator': p[4], 'value_to_assign': p[5]}



def p_header_definition(p):
    '''header_definition : CABECALHO STRING DE IDENTIFIER PARA STRING EM IDENTIFIER SEMICOLON
                         | CABECALHO STRING COM STRING SEMICOLON'''
    
    if len(p)==9:
        p[0]={
            'declaration_type':'dynamic_header_mapping',
            'source_header_name':p[2],
            'source_api_ref':p[4],
            'target_header_name':p[6],
            'target_api_ref':p[8]
        }
    else:
        p[0]={
            'declaration_type':'fixed_header_value',
            'target_header_name':p[2],
            'fixed_value':p[4]
        }


def p_function_param_identifier(p):
    '''function_param_identifier : IDENTIFIER
                                 | VALOR'''
    p[0]=p[1]



def p_function_param_list(p):
    '''function_param_list : function_param_list COMMA function_param_identifier
                           | function_param_identifier'''
    if len(p)==4:
        p[0]=p[1]+[p[3]]
    else:
        p[0]=[p[1]]



def p_optional_function_params(p):
    '''optional_function_params : function_param_list
                                | empty_rule'''
    p[0]=p[1]



def p_function_definition(p):
    '''function_definition : FUNCAO IDENTIFIER LPAREN optional_function_params RPAREN LBRACE function_body_placeholder RBRACE'''
    lista_parametros=p[4] if p[4] is not None else []
    p[0]={
        'declaration_type':'conversion_function_definition',
        'function_name': p[2],
        'parameters': lista_parametros,
        'body_placeholder_text': p[7]
    }



def p_function_body_placeholder(p):
    '''function_body_placeholder : empty_rule'''
    p[0]="Corpo da funcao (implementacao externa ou comentarios)"



def p_empty_rule(p):
    '''empty_rule :'''
    p[0] = None



#construindo o analisador sintatico
#o PLY usa 'parser' como nome padrao para a instancia do yacc se este arquivo é importado.
#Se voce renomear esta variavel (ex: 'meu_parser'), entao parse_dsl_from_string precisaria usar 'meu_parser.parse()'
parser=yacc.yacc()



def parse_dsl_from_string(data_string_input):
    global parser_gui_errors_list
    parser_gui_errors_list=[]#limpa erros anteriores


    lexer.lineno=1
    lexer.linepos=0


    #'parser' aqui refere-se a instancia criada por yacc.yacc() acima.
    parsing_result=parser.parse(data_string_input, lexer=lexer)


    if parser_gui_errors_list:
        return None, parser_gui_errors_list


    if parsing_result is None and not parser_gui_errors_list:
        return None,["Erro de parsing desconhecido: o analisador retornou 'None' sem erros especificos relatados."]
    

    return parsing_result, None