import ply.yacc as yacc
from Type import *
from AST import *
from Tokenizer import tokens

precedence = (
    ('right', 'ASSIGN', 'ASSIGN_PLUS', 'ASSIGN_MINUS', 'ASSIGN_MULTIPLY', 'ASSIGN_DIVIDE', 'ASSIGN_REMAINDER',
              'ASSIGN_BITAND', 'ASSIGN_BITOR', 'ASSIGN_BITXOR', 'ASSIGN_SHIFTLEFT', 'ASSIGN_SHIFTRIGHT'),
    ('left', 'LOR'),
    ('left', 'LAND'),
    ('left', 'BITOR'),
    ('left', 'BITXOR'),
    ('left', 'BITAND'),
    ('left', 'EQ', 'NE'),
    ('nonassoc', 'LT', 'LE', 'GT', 'GE'),
    ('left', 'SHIFTLEFT', 'SHIFTRIGHT'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'MULTIPLY', 'DIVIDE', 'REMAINDER'),
    ('right', 'UMINUS', 'UPLUS', 'BITNOT', 'LNOT'),
)

def p_module(p):
    'module : module_element_list'
    p[0] = TranslationUnit(None, p[1])

def p_module_element_list(p):
    'module_element_list : '
    p[0] = []
    
def p_module_element_list_append(p):
    'module_element_list : module_element_list module_element'
    p[0] = p[1] + [ p[2] ]
    
def p_module_element(p):
    '''module_element : function_declaration
                    | function_definition
                    | struct_definition'''
    p[0] = p[1]
    
def p_function_kind_empty(p):
    'function_kind : '
    p[0] = FunctionKindNode(None, FUNCTION_KIND_NORMAL)

def p_function_kind_kernel(p):
    'function_kind : KERNEL LPAREN IDENTIFIER RPAREN'
    p[0] = FunctionKindNode(p[1].position, p[3].value)

def p_prototype_arguments(p):
    '''prototype_arguments : prototype_arguments_empty
                           | prototype_arguments_nonempty'''
    p[0] = p[1]
    
def p_prototype_arguments_empty(p):
    'prototype_arguments_empty : '
    p[0] = []
    
def p_prototype_arguments_nonempty_first(p):
    'prototype_arguments_nonempty : prototype_argument'
    p[0] = [ p[1] ]
    
def p_prototype_arguments_nonempty_rest(p):
    'prototype_arguments_nonempty : prototype_arguments_nonempty COMMA prototype_argument'
    p[0] = p[1] + [ p[3] ]

def p_prototype_argument(p):
    'prototype_argument : argument_pass_type type_expr IDENTIFIER'
    p[0] = FunctionArgumentNode(p[1], p[2], p[3].value)
    
def p_argument_pass_type_empty(p):
    '''argument_pass_type : '''
    p[0] = 'normal'

def p_argument_pass_type_nonempty(p):
    '''argument_pass_type : IN
                          | OUT
                          | INOUT'''
    p[0] = p[1].value

def p_function_prototype(p):
    'function_prototype : function_kind type_expr IDENTIFIER LPAREN prototype_arguments RPAREN'
    position = p[2].position
    if p[1].position is not None:
        position = p[1].position
    p[0] = FunctionPrototype(position, p[1], p[2], p[3].value, p[5])
    
def p_function_declaration(p):
    'function_declaration : function_prototype SEMICOLON'
    p[0] = FunctionDeclaration(p[1])

def p_function_definition(p):
    'function_definition : function_prototype LCBRACKET statement_list RCBRACKET'
    p[0] = FunctionDefinition(p[1], p[3])
    
def p_statement_list_empty(p):
    'statement_list : '
    p[0] = []

def p_statement_list_rest(p):
    'statement_list : statement_list statement'
    p[0] = p[1] + [p[2]]

def p_statement(p):
    '''statement : null_statement
                 | block_statement
                 | if_statement
                 | while_statement
                 | do_while_statement
                 | break_statement
                 | continue_statement
                 | discard_statement
                 | return_statement
                 | variables_declaration
                 | expression_statement'''
    p[0] = p[1]
    
def p_variables_declaration(p):
    'variables_declaration : type_expr variables_names SEMICOLON'
    p[0] = VariablesDeclaration(p[1], p[2])
    
def p_variables_names_first(p):
    'variables_names : variable_name'
    p[0] = [ p[1] ]

def p_variables_names_rest(p):
    'variables_names : variables_names COMMA variable_name'
    p[0] = p[1] + [ p[3] ]
    
def p_variable_name(p):
    'variable_name : IDENTIFIER'
    p[0] = VariableDeclaration(p[1].position, p[1].value, None)
    
def p_variable_name_initial(p):
    'variable_name : IDENTIFIER ASSIGN expression'
    p[0] = VariableDeclaration(p[1].position, p[1].value, p[3])

def p_null_statement(p):
    'null_statement : SEMICOLON'
    p[0] = NullStatement(p[1].position)

def p_block_statement(p):
    'block_statement : LCBRACKET statement_list RCBRACKET'
    p[0] = BlockStatement(p[1].position, p[2])

def p_if_statement(p):
    'if_statement : IF LPAREN expression RPAREN statement'
    p[0] = IfStatement(p[1].position, p[3], p[5], None)

def p_if_else_statement(p):
    'if_statement : IF LPAREN expression RPAREN statement ELSE statement'
    p[0] = IfStatement(p[1].position, p[3], p[5], p[7])

def p_while_statement(p):
    'while_statement : WHILE LPAREN expression RPAREN statement'
    p[0] = WhileStatement(p[1].position, p[3], p[5])

def p_do_while_statement(p):
    'do_while_statement : DO statement WHILE LPAREN expression RPAREN'
    p[0] = DoWhileStatement(p[1].position, p[2], p[5])

def p_break_statement(p):
    'break_statement : BREAK SEMICOLON'
    p[0] = BreakStatement(p[1].position)

def p_continue_statement(p):
    'continue_statement : CONTINUE SEMICOLON'
    p[0] = ContinueStatement(p[1].position)

def p_discard_statement(p):
    'discard_statement : DISCARD SEMICOLON'
    p[0] = DiscardStatement(p[1].position)

def p_return_statement(p):
    'return_statement : RETURN SEMICOLON'
    p[0] = ReturnStatement(p[1].position, None)

def p_return_value_statement(p):
    'return_statement : RETURN expression SEMICOLON'
    p[0] = ReturnStatement(p[1].position, p[2])

def p_expression_statement(p):
    'expression_statement : expression SEMICOLON'
    p[0] = ExpressionStatement(p[1])

def p_expression(p):
    '''expression : primary_expression'''
    p[0] = p[1]

def p_expression_binary(p):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression MULTIPLY expression
                  | expression DIVIDE expression
                  | expression REMAINDER expression
                  
                  | expression LT expression
                  | expression LE expression
                  | expression EQ expression
                  | expression NE expression
                  | expression GT expression
                  | expression GE expression
                  
                  | expression LAND expression
                  | expression LOR expression
                  
                  | expression BITAND expression
                  | expression BITOR expression
                  | expression BITXOR expression
                  | expression SHIFTLEFT expression
                  | expression SHIFTRIGHT expression
                  '''
    p[0] = BinaryExpression(p[2].position, p[2].value, p[1], p[3])

def p_expression_binary_assignment(p):
    '''expression : expression ASSIGN expression
                 
                  | expression ASSIGN_PLUS expression
                  | expression ASSIGN_MINUS expression
                  | expression ASSIGN_MULTIPLY expression
                  | expression ASSIGN_DIVIDE expression
                  | expression ASSIGN_REMAINDER expression
                 
                  | expression ASSIGN_BITOR expression
                  | expression ASSIGN_BITAND expression
                  | expression ASSIGN_BITXOR expression
                 
                  | expression ASSIGN_SHIFTLEFT expression
                  | expression ASSIGN_SHIFTRIGHT expression
                  '''
    p[0] = BinaryAssignmentExpression(p[2].position, p[2].value, p[1], p[3])
    
def p_expression_unary(p):
    '''expression : PLUS expression %prec UPLUS
                  | MINUS expression %prec UMINUS
                  | LNOT expression
                  | BITNOT expression'''
    p[0] = UnaryExpression(p[1].position, p[1].value, p[2])
    
def p_primary_expression(p):
    '''primary_expression : constant
                | identifier
                | parenthesis_expression
                | member_access
                | subscript_access
                | call_expression'''
    p[0] = p[1]
    
def p_parenthesis_expression(p):
    'parenthesis_expression : LPAREN expression RPAREN'
    p[0] = p[2]

def p_member_access(p):
    'member_access : primary_expression DOT IDENTIFIER '
    p[0] = MemberAccess(p[2].position, p[1], p[3].value)

def p_subscript_access(p):
    'subscript_access : primary_expression LBRACKET expression RBRACKET '
    p[0] = SubscriptAccess(p[2].position, p[1], p[3])

def p_call_expression(p):
    'call_expression : primary_expression LPAREN call_arguments RPAREN '
    p[0] = CallExpression(p[2].position, p[1], p[3])

def p_call_arguments(p):
    '''call_arguments : call_arguments_empty
                      | call_arguments_nonempty'''
    p[0] = p[1]
    
def p_call_arguments_empty(p):
    'call_arguments_empty : '
    p[0] = []

def p_call_arguments_nonempty_first(p):
    'call_arguments_nonempty : expression'
    p[0] = [p[1]]

def p_call_arguments_nonempty_rest(p):
    'call_arguments_nonempty : call_arguments_nonempty COMMA expression'
    p[0] = p[1] + [p[3]]
    
def p_constant(p):
    '''constant : integer_constant
                | boolean_constant
                | real_constant
                | string_literal'''
    p[0] = p[1]

def p_integer_constant(p):
    'integer_constant : INTEGER'
    p[0] = IntegerConstant(p[1].position, p[1].value)

def p_boolean_constant(p):
    '''boolean_constant : TRUE
                        | FALSE'''
    p[0] = BooleanConstant(p[1].position, p[1].value)
    
def p_real_constant(p):
    'real_constant : REAL'
    p[0] = RealConstant(p[1].position, p[1].value)

def p_string_literal(p):
    'string_literal : STRING'
    p[0] = StringLiteral(p[1].position, p[1].value)

def p_type_expr(p):
    '''type_expr : type
               | identifier'''
    p[0] = p[1]

def p_type(p):
    'type : TYPE'
    p[0] = TypeNode(p[1].position, p[1].value)
    
def p_identifier(p):
    'identifier : IDENTIFIER'
    p[0] = IdentifierExpr(p[1].position, p[1].value)

def p_struct_definition(p):
    'struct_definition : optional_attribute_list  STRUCT IDENTIFIER LCBRACKET struct_fields RCBRACKET SEMICOLON'
    p[0] = StructDefinition(p[2].position, p[3].value, p[5], p[1])

def p_struct_fields_nonempty(p):
    'struct_fields : struct_fields struct_field'
    p[0] = p[1] + [p[2]]

def p_struct_fields_empty(p):
    'struct_fields : '
    p[0] = []

def p_struct_field(p):
    'struct_field : optional_attribute_list type IDENTIFIER SEMICOLON'
    p[0] = StructField(p[2], p[3].value, p[1]);

def p_optional_attribute_list_empty(p):
    'optional_attribute_list : '
    p[0] = []

def p_optional_attribute_list_rest(p):
    'optional_attribute_list : optional_attribute_list attribute'
    p[0] = p[1] + [p[2]]

def p_attribute(p):
    'attribute : LBRACKET IDENTIFIER attribute_arguments RBRACKET'
    p[0] = AttributeDefinition(p[1].position, p[2].value, p[3])

def p_attribute_arguments_empty(p):
    'attribute_arguments : '
    p[0] = []

def p_attribute_arguments_nonempty(p):
    'attribute_arguments : LPAREN call_arguments RPAREN'
    p[0] = p[2]

# Error rule for syntax errors
def p_error(p):
    print "Syntax error in input " , str(p.lineno)
    
parser = yacc.yacc()
