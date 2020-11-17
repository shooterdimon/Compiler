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
            return f"add eax, {self.right_term}"
        elif isinstance(self.left_term,UnOP):
            return f"add eax, {self.right_term}"
        else:
            return f"mov eax, {self.left_term}\nadd eax, {self.right_term}"


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
              ('identifier', rb'\b[A-z]+\b'),
              ('addition', rb'\+'),
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

        self.print_result_tokens()




class Parser():
    #Initialize lexer to parser
    def __init__(self,lexer):
        self.lexer=lexer
        self.token_list = self.lexer.result_tokens
        self.result_asm = ''
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

    def convert_to_op(self,token):
        if token.type == 'bitwise complement' :
            return 'bitwise complement'
        elif token.type == 'addition' :
            return 'addition'
    def check_parentheses(self,tokens):
        open_par = 0
        close_par = 0
        for tok in tokens:
            if tok.value == "(":
                open_par+=1

            elif tok.value ==")":
                close_par+=1
        if close_par>open_par:
            print(f"Parser Erorr\nMissed open parentheses at 2 line")
            time.sleep(10000)
            sys.exit(1)
        elif open_par>close_par:
            print(f"Parser Erorr\nMissed close parentheses at 2 line")
            time.sleep(10000)
            sys.exit(1)

    def parse_factor(self,token_list):
        self.check_parentheses(token_list.get_list())
        if token_list.if_in("return keyword"):
            while next(token_list).type != 'return keyword':
                pass
        try:
            next_tok = next(token_list)
        except:
            print("All tokens parsed")
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
                    while next_tok.type == 'addition':
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
        elif next_tok.type in ['return keyword','identifier','open brace','close brace']:
            self.parse_factor(token_list)
        else:
            if next_tok.type == 'int':
                #sys.exit(1)
                token_list.back()
                const = self.parse_exp(token_list)
                if isinstance(const,Const):
                    self.result_asm+='\n'+const.asm()


    def parse_exp(self,token_list):
        term = self.parse_term(next(token_list))
        try:
            next_tok = next(token_list)
        except:
            return Const(term)
        if next_tok.type == 'addition':
            while next_tok.type == 'addition':
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
        return token.value



class CodeGenerator():
    def __init__(self,parser):
        self.parser=parser

    def generating(self):
        self.parser.parse_factor(parser.to_output_type())
        output_asm = self.parser.result_asm + "\nmov b, eax"
        print(output_asm)
        return output_asm

    def writing(self,file_path):
        with open(file_path,"w") as f:
            f.write(self.generating())


lexer = Lexer("2-13-Python-IV-81-Zikratyi.txt")
print("--------------Table of tokens--------------")
lexer.next_tok()
parser = Parser(lexer)
code_gen = CodeGenerator(parser)
print()
print("Assembler code")
print()
code_gen.writing('2-13-Python-IV-81-Zikratyi.asm')
time.sleep(1000)
