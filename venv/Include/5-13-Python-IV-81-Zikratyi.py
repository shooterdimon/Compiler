import sys
import re
import time
from custom_iterators import CustomIterator
from classes import*


class Lexer():
    #Initialize filepath
    def __init__(self,file_path):
        self.file_path = file_path

    #Read file
    def reader(self):
        f = open(self.file_path, "rb")
        text = f.read()
        f.close()
        return text

    #Clean input text
    def clean_input(self,text):
        text = text.replace(b"\r\n",b"")
        return text

    def cut_text(self,text,value):
        start = len(text)
        text = text[len(value):].lstrip()
        return text,start-(len(text))

    #Print errors
    def error(self,msg):
        print("Lexer error: ", msg)
        sys.exit(1)

    #List with tokens that are searched
    search_tokens = [('function identifier', rb'int\s([A-z]+)(\([^{]*\))'),
              ('function call', rb'([A-z]+)(\([^{]*\))'),
              ('int keyword', rb'\bint\b'),
              ('char keyword', rb'\bchar\b'),
              ('return keyword', rb'\breturn\b'),
              ('if keyword', rb'\bif\b'),
              ('else keyword', rb'\belse\b'),
              ('identifier', rb'\b[A-z]+\b'),
              ('addition', rb'\+'),
              ('difference', rb'\-'),
              ('assignment', rb'\='),
              ('bit shift left', rb'\<<'),
              ('bitwise complement', rb'\~'),
              ('open parentheses', rb'\('),
              ('close parentheses', rb'\)'),
              ('open brace', rb'\{'),
              ('close brace', rb'\}'),
              ('comma', rb','),
              ('semicolon', rb';'),
              ('octal', rb'\b0\d+\b'),
              ('int', rb'\b\d+\b'),
              ('char', rb"\'\w\'"),]

    #List with tokens will be find
    result_tokens=[]
    def print_result_tokens(self):
        for token in self.result_tokens:
            print(token)
    def get_line(self,token):
        ids = [ self.result_tokens.index(token)+1 for token in self.result_tokens if token.value in [';','{','}']]
        ids.insert(0,0)
        line_ids = [(ids[i],ids[i+1]) for i in range(0,len(ids)-1)]
        lines = [self.result_tokens[id[0]:id[1]] for id in line_ids]
        for i in range(len(lines)):
            if token in lines[i]:
                id = lines[i].index(token)
                string = lines[i][:id]
                len_line = 0
                for el in string:
                    len_line+=len(el.value)
                list_line = [token.value for token in lines[i]]
                return i+1,len_line+len(lines[i][id].value)+1, " ".join(list_line)

    #Identify tokens
    def next_tok(self):
        self.result_tokens = []
        input_text = self.clean_input(self.reader())
        position = 0
        while input_text:
            flag = False
            for lexem_type, re_pattern in self.search_tokens:
                find_result = re.match(re_pattern,input_text)
                if find_result:
                    token = Token(lexem_type,(find_result.group()).decode("utf-8"))
                    input_text, change_position = self.cut_text(input_text,find_result.group())
                    position+=change_position
                    self.result_tokens.append(token)
                    flag = True
                    break
            if flag == False:

                    print(Exception(f"Invalid token or can not be detected at {position} position"))
                    time.sleep(1000)
                    exit(1)

        self.print_result_tokens()




class Parser():
    #Initialize lexer to parser
    def __init__(self,lexer):
        self.lexer=lexer
        self.token_list = self.lexer.result_tokens
        self.result_asm = 'main:\npush ebp\nmov ebp, esp'
        self.var_table={}
        self.function_table={}
        self.line_counter=1
        self.stack_index = -4
        self.first_in = True
        self.metka = 0

    #Convert input types to output form
    def to_output_type(self):
        for token in self.token_list:
            if token.type=="octal":
                token.value = str(int(token.value,8))
            elif token.type=="char":
                token.value = str(ord((token.value).replace("'",'')))
        return CustomIterator(self.token_list)

    def convert_to_int(self,token):
        return int(token.value)

    def is_unop(self,token):
        if token.type == 'bitwise complement':
            return True
        else:
            return False

    def check_var(self,var):
        for key in self.var_table.keys():
            if str(key) == var:
                return True
        else:
            return False

    def convert_to_op(self,token):
        if token.type == 'bitwise complement' :
            return 'bitwise complement'
        elif token.type == 'addition' :
            return 'addition'
        elif token.type == 'difference' :
            return 'difference'
        elif token.type == 'bit shift left' :
            return 'bit shift left'
    def check_parentheses(self,tokens):
        open_par = 0
        close_par = 0
        for tok in tokens:
            if tok.value == "(":
                open_par+=1
            elif tok.value ==")":
                close_par+=1
        if close_par>open_par:
            print(f"Parser Erorr\nMissed open parentheses at 3 line")
            time.sleep(10000)
            sys.exit(1)
        elif open_par>close_par:
            print(f"Parser Erorr\nMissed close parentheses at 3 line")
            time.sleep(10000)
            sys.exit(1)

    def parse_factor(self,token_list):
        self.check_parentheses(token_list.get_list())
        if self.first_in:
            token_list.back()
            self.first_in = False
        try:
            next_tok = next(token_list)
        except:
            return 0
        if next_tok.type == 'open parentheses' :
            exp = self.parse_exp(token_list)
            if next(token_list).type != 'close parentheses' :
                print("Error: ')' Expected")
                sys.exit(1)
                time.sleep(10000)
            return exp
        elif self.is_unop(next_tok):
            op = self.convert_to_op(next_tok)
            next_tok = next(token_list)
            if next_tok.type == 'int':
                un_op = UnOP(op, next_tok.value)
                self.result_asm += '\n' + un_op.asm()
                next_tok = next(token_list)
                if next_tok.type == 'semicolon':
                    token_list.back()
                    return un_op
                else:
                    term = un_op
                    while next_tok.type == 'addition' or next_tok.type == 'bit shift complement' or next_tok.type == 'difference':
                        op = self.convert_to_op(next_tok)
                        next_tok = next(token_list)
                        next_term = self.parse_term(next_tok)
                        bin_op = BinOP(term, op, next_term)
                        term = bin_op
                        self.result_asm += '\n' + bin_op.asm()
                        next_tok = next(token_list)
                    return term
            token_list.back()
            factor = self.parse_factor(token_list)
            un_op = UnOP (op, factor)
            self.result_asm+='\n'+un_op.asm()
            return un_op
        elif next_tok.type == 'int':
            token_list.back()
            const = self.parse_exp(token_list)
            if isinstance(const, Const) :
                self.result_asm += '\n' + const.asm()
        elif next_tok.type == 'identifier':
            if self.check_var(next_tok.value):
                next_tok = next(token_list)
                if next_tok.type in ['addition','difference','bit shift left']:
                    token_list.back()
                    token_list.back()
                    exp = self.parse_exp(token_list)
                    #self.parse_factor(token_list)
                else:
                    token_list.back()
                    token_list.back()
                    next_tok=next(token_list)
                    self.parse_assignment(token_list,next_tok)
                    self.parse_factor(token_list)
                #exp = self.parse_exp(token_list)
            else:
                print(f"{self.lexer.get_line(next_tok)[2]}")
                print(f"Line {self.lexer.get_line(next_tok)[0]}, symbol {self.lexer.get_line(next_tok)[1]}")
                print(f"SyntaxError: variable '{next_tok.value}' has not assigned yet")
                time.sleep(1000)
                sys.exit(1)
        elif next_tok.type == 'function identifier':
            func_with_vars = next_tok.value[4:]
            vars=func_with_vars[(func_with_vars.index('('))+1:-1]
            list_vars = vars.split(';')
            list_vars = [i for i in list_vars if i]
            func_var_table = {}
            for var in list_vars:
                var_class = Var(var)
                func_var = Assignment(var_class,0,(list_vars.index(var)+1)*(-4))
                func_var_table.setdefault(func_var.string.string,func_var)
            func_name=func_with_vars[:(func_with_vars.index('('))]
            if func_name == 'main' :
                self.parse_factor(token_list)
            else:
                next_tok=next(token_list)
                if next_tok.type=='open brace':
                    func_block = FunctionBlock(self.lexer,func_var_table,(len(list_vars)+1)*(-4))
                    func_block.parse_factor(token_list)
                    self.function_table.setdefault(func_name,func_block.result_asm)
                    #print(func_block.result_asm)
                    self.parse_factor(token_list)
        elif next_tok.type == 'function call':
            func_with_vars = next_tok.value
            vars = func_with_vars[(func_with_vars.index('('))+1:-1]
            list_vars = vars.split(';')
            list_vars = [i for i in list_vars if i]
            func_name = func_with_vars[:(func_with_vars.index('('))]
            func_asm = f'\n{func_name}:\npush ebp\nmov ebp, esp'
            if func_name in self.function_table.keys():
                self.result_asm+=f'\ncall {func_name}'
                for var in list_vars:
                    func_asm+=f'\nmov eax, {var}\npush eax'
                func_asm+=self.function_table[func_name]
                self.function_table[func_name] = func_asm



        elif next_tok.type == 'int keyword':
            variable = next(token_list)
            if self.check_var(variable.value):
                print(f"{self.lexer.get_line(variable)[2]}")
                print(f"Line {self.lexer.get_line(variable)[0]}, symbol {self.lexer.get_line(variable)[1]}")
                print(f"SyntaxError: variable assignment. Variable '{variable.value}' can not be assign twice")
                time.sleep(1000)
                sys.exit(1)
            self.parse_assignment(token_list,variable)
            self.parse_factor(token_list)
        elif next_tok.type == 'if keyword':
            next_tok = next(token_list)
            if next_tok.type == 'open parentheses':
                next_tok = next(token_list)
                if self.check_var(next_tok.value):
                    self.result_asm+='\n'+self.get_var(next_tok).asm()
                    self.result_asm+='\n'+f'cmp eax, 0'
                    block = Block(self.lexer,self.var_table,self.stack_index)
                    block.parse_factor(token_list)
                    next_tok = next(token_list)
                    if next_tok.type =='else keyword':
                        self.result_asm += '\n' + f'je _e{self.metka}'
                        else_block = Block(self.lexer,self.var_table,self.stack_index)
                        else_block.parse_factor(token_list)
                        self.result_asm += block.result_asm
                        self.result_asm += '\n' + f'jmp _post_conditional{self.metka}'
                        self.result_asm += '\n' + f'_e{self.metka}:'
                        self.result_asm += else_block.result_asm
                        self.result_asm += '\n' + f'_post_conditional{self.metka}:'
                    else:
                        self.result_asm += '\n' + f'je _post_conditional{self.metka}'
                        self.result_asm += block.result_asm
                        self.result_asm += '\n' + f'_post_conditional{self.metka}:'
                        token_list.back()
                    self.metka += 1
                    self.parse_factor(token_list)
        else:
            self.parse_factor(token_list)


    def parse_assignment(self,token_list,variable):
        next_tok = next(token_list)
        var = Var(variable.value)
        if next_tok.type == 'assignment' :
            exp = self.parse_exp(token_list)
            self.result_asm += '\n' + exp.asm()
            var_assign = Assignment(var, exp,self.stack_index)
            self.stack_index-=4
            self.var_table[var_assign.string.string]=var_assign
            self.result_asm += '\n' + var.asm()
        elif next_tok.type == 'semicolon' :
            self.var_table[var.string]=(var,self.stack_index)



    def parse_exp(self,token_list):
        term = self.parse_term(next(token_list))
        try:
            next_tok = next(token_list)
        except:
            return Const(term)
        if next_tok.type == 'addition' or next_tok.type =='difference' or next_tok.type =='bit shift left':
            while next_tok.type == 'addition' or next_tok.type =='difference' or next_tok.type =='bit shift left':
                op = self.convert_to_op(next_tok)
                next_tok = next(token_list)
                next_term = self.parse_term(next_tok)
                bin_op = BinOP(term, op, next_term)
                term = bin_op
                self.result_asm+='\n'+bin_op.asm()
                if next(token_list).type == 'close parentheses':
                    token_list.back()
                    return bin_op
                token_list.back()
                next_tok = next(token_list)
            return bin_op
        elif next_tok.type == 'semicolon':
            token_list.back()
            token_list.back()
            return Const(next(token_list))


    def parse_term(self,token):
        if token.type=="int":
            return token.value
        elif token.type =="identifier":
            return self.get_var(token)


    def get_var(self,token):
        for key in self.var_table.keys():
            if str(key) == token.value:
                return self.var_table[key]
        else:
            print(f"{self.lexer.get_line(token)[2]}")
            print(f"Line {self.lexer.get_line(token)[0]}, symbol {self.lexer.get_line(token)[1]}")
            print(f"SyntaxError: variable '{token.value}' has not assigned yet")
            time.sleep(1000)
            sys.exit(1)

    def add_func_asm(self):
        func_asm = ''
        for func in self.function_table.keys():
            func_asm+=self.function_table[func]+'\nmov esp, ebp\npop ebp' +'\nmov b, eax'
        return func_asm

class CodeGenerator():
    def __init__(self,parser):
        self.parser=parser

    def generating(self):
        self.parser.parse_factor(parser.to_output_type())
        output_asm = self.parser.result_asm +'\nmov esp, ebp\npop ebp' +'\nmov b, eax'
        output_asm+= self.parser.add_func_asm()
        print(output_asm)
        return output_asm

    def writing(self,file_path):
        with open(file_path,"w") as f:
            f.write(self.generating())


lexer = Lexer("5-13-Python-IV-81-Zikratyi.txt")
print("--------------Table of tokens--------------")
lexer.next_tok()
parser = Parser(lexer)
code_gen = CodeGenerator(parser)
print()
print("Assembler code")
print()
code_gen.writing('5-13-Python-IV-81-Zikratyi.asm')
time.sleep(1000)
