import sys
import re
import time
from custom_iterators import CustomIterator



class Token():
    #Intialize type nad value of token
    def __init__(self,type,value):
        self.value = value
        self.type = type

    def __repr__(self):
        return f"{self.type}:{self.value}"



class Program():
    def __init__(function):
        self.function = function


class Function():
    def __init__(self,name,statement):
        self.name = name
        self.statement = statement


class statement_Return():
    def __init__(self,exp):
        self.exp = exp


class Var():
    def __init__(self,string):
        self.string = string
    def asm(self):
        return 'push eax'
    def __repr__(self):
        return str(self.string)

class Assignment():
    def __init__(self,string,exp):
        self.string = string
        self.exp = exp
    def asm(self):
        string_asm = f'push eax'
        return string_asm
    def __repr__(self):
        return str(self.string)

class UnOP():
    def __init__(self,op,term):
        self.op = op
        self.term = term
        #print("UnOP", op, term)
    def __repr__(self):
        return f'{self.op} {self.term}'
    def asm(self):
        if isinstance(self.term, BinOP) :
            return f"not eax"
        else:
            return f"mov eax, {self.term}\nnot eax"

class BinOP():
    def __init__(self,left_term,op,right_term):
        self.op = op
        self.left_term = left_term
        self.right_term = right_term
        #print("BinOP",left_term,op,right_term)
    def __repr__(self):
        return f'{self.left_term} {self.op} {self.right_term}'
    def asm(self):
        if isinstance(self.left_term,BinOP):
            if self.op == 'addition':
                return f"add eax, {self.right_term}"
            elif self.op == 'difference':
                return f"sub eax, {self.right_term}"
            elif self.op == 'bit shift left':
                return f"sal eax, {self.right_term}"
        elif isinstance(self.left_term,UnOP):
            return f"add eax, {self.right_term}"
        elif isinstance(self.left_term, Assignment):
            if self.op == 'addition':
                return f"pop eax\nmov dword ptr[ebp+4], eax\nadd eax, {self.right_term}"
            elif self.op == 'difference':
                return f"pop eax\nmov dword ptr[ebp+4], eax\nsub eax, {self.right_term}"
            elif self.op == 'bit shift left':
                return f"pop eax\nmov dword ptr[ebp+4], eax\nsal eax, {self.right_term}"

        else:
            if self.op == 'addition':
                return f"mov eax, {self.left_term}\nadd eax, {self.right_term}"
            elif self.op == 'difference':
                return f"mov eax, {self.left_term}\nsub eax, {self.right_term}"
            elif self.op == 'bit shift left':
                return f"mov eax, {self.left_term}\nsal eax, {self.right_term}"


class Const():
    def __init__(self,token):
        self.const = token.value
        self.type = token.type
    def __repr__(self):
        return f'{self.const}'
    def asm(self):
        return f"mov eax, {self.const}"


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
    search_tokens = [('int keyword', rb'\bint\b'),
              ('char keyword', rb'\bchar\b'),
              ('return keyword', rb'\breturn\b'),
              ('comment', rb'//(([a-zA-Z0-9]+)(\s)?)*\.'),
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
                    time.sleep(10)
                    exit(1)

        self.result_tokens = [token for token in self.result_tokens if token.type != 'comment']
        self.print_result_tokens()



class Parser():
    #Initialize lexer to parser
    def __init__(self,lexer):
        self.lexer=lexer
        self.token_list = self.lexer.result_tokens
        self.result_asm = '#include <iostream>\n#include <string>\n#include <stdint.h>\n#include <conio.h>\nusing namespace std;\nint main(){\nint32_t b;\n__asm {\nmain:\n\tpush ebp\n\tmov ebp, esp'
        self.var_table={}
        self.line_counter=1
        self.function_call=[]
        self.flag = True
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
            if str(key.string) == var:
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
            print(f"Parser Erorr:\nMissed open parentheses at 2 line")
            time.sleep(10000)
            sys.exit(1)
        elif open_par>close_par:
            print(f"Parser Erorr:\nMissed close parentheses at 2 line")
            time.sleep(10000)
            sys.exit(1)

    def parse_factor(self,token_list):
        self.check_parentheses(token_list.get_list())
        #if token_list.if_in("open brace"):
            #while next(token_list).type != 'open brace':
                #pass
        try:
            if self.flag:
                token_list.back()
                next_tok = next(token_list)
                token_list.back()
            else:
                next_tok = next(token_list)
        except:
            print("All tokens parsed")
        if next_tok.type == 'open parentheses' :
            exp = self.parse_exp(token_list)
            if next(token_list).type != 'close parentheses' :
                print(f"{self.lexer.get_line(next_tok)[2]}")
                print(f"Line {self.lexer.get_line(next_tok)[0]}, symbol {self.lexer.get_line(next_tok)[1]}")
                print(f"ParserError: ')' expected ")
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
                #token_list.back()
                self.parse_assignment(token_list,next_tok)
                self.parse_factor(token_list)
                #exp = self.parse_exp(token_list)
            elif next_tok.value.lower() in self.function_call:
                next(token_list)
                input_var = next(token_list).value

                self.function_asm = self.function_asm.replace("input_variable",input_var)
                self.result_asm+='\n'+f'\tcall {next_tok.value.lower()}'

            else:
                print(f"{self.lexer.get_line(next_tok)[2]}")
                print(f"Line {self.lexer.get_line(next_tok)[0]}, symbol {self.lexer.get_line(next_tok)[1]}")
                print(f"SyntaxError: variable '{next_tok.value}' has not assigned yet")
                sys.exit(1)
        elif next_tok.type == "int keyword":
            self.function_asm =""
            next(token_list)
            next_tok = next(token_list)
            next_next_tok = next(token_list)
            if next_next_tok.type == "open parentheses":
                var_function_table = []
                type_tok = next(token_list)
                self.function_asm+="\n"+f"{next_tok.value.lower()}:\n\tpush ebp\n\tmov esp, ebp"
                while type_tok.type == "char keyword" or type_tok.type == "int keyword":
                    var_tok = next(token_list)
                    var_function_table.append((type_tok.value,var_tok.value))
                    sem_tok=next(token_list)
                    if sem_tok.type =='semicolon':
                        type_tok = next(token_list)
                    else:
                        break
                while next(token_list).type != "close brace":
                    pass
                self.function_asm+="\n"+f"\tmov eax, input_variable\n\tpush eax\n\tpop eax\n\tmov dword ptr[ebp+4], eax\n\tadd eax, {32}" + '\n\tpop ebp\n\tmov b, eax'
                self.function_call.append(next_tok.value.lower())
                next_tok = next(token_list)
                while next_tok.type != "open brace":
                    next_tok = next(token_list)
                self.flag = False
                self.parse_factor(token_list)

            elif next_next_tok.type == "semicolon":
                token_list.back()
                token_list.back
                variable = next(token_list)
                if self.check_var(variable.value):
                    print(f"{self.lexer.get_line(variable)[2]}")
                    print(f"Line {self.lexer.get_line(variable)[0]}, symbol {self.lexer.get_line(variable)[1]}")
                    print(f"SyntaxError: variable assignment. Variable '{variable.value}' can not be assign twice")
                    sys.exit(1)
                self.parse_assignment(token_list,variable)
                self.parse_factor(token_list)
        else:
            self.parse_factor(token_list)


    def parse_assignment(self,token_list,variable):
        next_tok = next(token_list)
        var = Var(variable.value)
        if next_tok.type == 'assignment' :
            exp = self.parse_exp(token_list)
            self.result_asm += '\n' + exp.asm()
            var_assign = Assignment(var, exp)
            self.var_table.setdefault(var_assign, 0)
            self.result_asm += '\n' + var.asm()
        elif next_tok.type == 'semicolon' :
            self.var_table.setdefault(var, 0)


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
            if str(key.string) == token.value:
                return key



class CodeGenerator():
    def __init__(self,parser):
        self.parser=parser

    def generating(self):
        self.parser.parse_factor(parser.to_output_type())
        output_asm = self.parser.result_asm +'\n\tpop ebp' +'\n\tmov b, eax' + parser.function_asm
        output_asm+='\n}\ncout << b << endl;\nsystem("pause");\n}'
        print(output_asm)
        return output_asm

    def writing(self,file_path):
        with open(file_path,"w") as f:
            f.write(self.generating())


lexer = Lexer("КР-13-Python-IV-81-Zikratyi.c")
print("--------------Table of tokens--------------")
lexer.next_tok()
parser = Parser(lexer)
code_gen = CodeGenerator(parser)
print()
print("Assembly code")
print()
code_gen.writing('KR-13-Python-IV-81-Zikratyi.cpp')
time.sleep(1000)
