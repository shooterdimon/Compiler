import sys
import re
import time

class Token():
    #Intialize type nad value of token
    def __init__(self,type,value):
        self.value = value
        self.type = type

    def __repr__(self):
        return f"{self.type}:{self.value}"


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


class UnOP():
    def __init__(self,op,term):
        self.op = op
        self.term = term

class BinOP():
    def __init__(self,left_term,op,right_term):
        self.op = op
        self.left_term = left_term
        self.right_term = right_term



class Parser():
    #Initialize lexer to parser
    def __init__(self,lexer):
        self.lexer=lexer
        self.token_list = self.lexer.result_tokens
    #Convert input types to output form
    def to_output_type(self):
        for token in self.token_list:
            if token.type=="octal":
                token.value = str(int(token.value,8))
            elif token.type=="char":
                token.value = str(ord((token.value).replace("'",'')))
        return self.token_list

    def find_op(self):
        for token in self.token_list:
            if token.value=='return':
                return_index = (self.token_list).index(token)
            elif token.value ==';':
                semicolon_index = (self.token_list).index(token)
        self.token_list=self.token_list[return_index+1:semicolon_index]
        token_types = [token.type for token  in self.token_list]

        if (("bitwise complement" in token_types) or ("addition" in token_types)) and (len(token_types)>1):
            if ("open parentheses" and "close parentheses") in token_types:
                list_open = [token_types.index(i) for i in token_types if i=="open parentheses"]
                list_close = [token_types.index(i) for i in token_types if i == "close parentheses"]
                try:
                    list_brackets = list(zip(list_open,list_close))
                    expr_in_brackets = [self.token_list[pair[0]+1:pair[1]] for pair in list_brackets]
                    start = 0
                    list_out_brackets = []
                    for i in range(len(list_brackets)):
                        if (start - list_brackets[i][0])>1:
                            list_out_brackets.append((start,list_out_brackets[i][0]))
                            start = list_out_brackets[i][1]
                    print(list_out_brackets)
                    print(expr_in_brackets)
                except:
                    print("Missed parentheses")
                    sys.exit(1)

            for i in range(len(self.token_list)):
                if (self.token_list[i]).type == "bitwise complement" and (self.token_list[i+1]).type == '':
                    pass
        else:
            return self.token_list



class CodeGenerator():
    def __init__(self,parser):
        self.parser=parser

    def generating(self):
        self.parser.to_output_type()
        return_expression_list = self.parser.find_op()
        if len(return_expression_list) == 0:
            exit(0)
        elif len(return_expression_list) ==1:
            return_value = return_expression_list[0].value
        elif len(return_expression_list)>1:
            print(return_expression_list)
            return_value = "".join(return_expression_list)

        #final_code = f".386\n.model flat, stdcall\n.data\n.code\nstart:\n\tpush    \n\tmov     eax, {return_value}\n\tret"
        final_code = f"mov eax, {return_value} \nmov b, eax"
        print(final_code)
        return final_code

    def writing(self,file_path):
        with open(file_path,"w") as f:
            f.write(self.generating())

lexer = Lexer("1-13-Python-IV-81-Zikratyi.txt")
print("--------------Table of tokens--------------")
lexer.next_tok()
parser = Parser(lexer)
code_gen = CodeGenerator(parser)
print()
print("Assembler code")
print()
code_gen.writing('1-13-Python-IV-81-Zikratyi.asm')
time.sleep(1000)
