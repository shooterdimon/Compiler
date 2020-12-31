import time
import sys

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
    def __init__(self,string,exp,stack_index):
        self.stack_index = stack_index
        self.string = string
        self.exp = exp
    def asm(self):
        return f'mov eax, [ebp{str(self.stack_index)}]'
    def __repr__(self):
        return f"{str(self.string)}={str(self.exp)}"
    def get_stack_index(self):
        return self.stack_index

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
                if isinstance(self.right_term,Assignment):
                    return f"mov ebx{self.right_term.asm()[7:]}\nadd eax, ebx"
                else:
                    return f"add eax, {self.right_term}"
            elif self.op == 'difference':
                if isinstance(self.right_term,Assignment):
                    return f"mov ebx{self.right_term.asm()[7:]}\nsub eax, ebx"
                else:
                    return f"sub eax, {self.right_term}"
            elif self.op == 'bit shift left':
                if isinstance(self.right_term,Assignment):
                    return f"mov ebx{self.right_term.asm()[7:]}\nsal eax, ebx"
                else:
                    return f"sal eax, {self.right_term}"
        elif isinstance(self.left_term,UnOP):
            return f"add eax, {self.right_term}"
        elif isinstance(self.left_term, Assignment):
            if self.op == 'addition':
                if isinstance(self.right_term,Assignment):
                    return f"{self.left_term.asm()}\nmov ebx{self.right_term.asm()[7:]}\nadd eax, ebx"
                else:
                    return f"{self.left_term.asm()}\nadd eax, {self.right_term}"
            elif self.op == 'difference':
                if isinstance(self.right_term,Assignment):
                    return f"{self.left_term.asm()}\nmov ebx{self.right_term.asm()[7:]}\nsub eax, ebx"
                else:
                    return f"{self.left_term.asm()}\nsub eax, {self.right_term}"
            elif self.op == 'bit shift left':
                if isinstance(self.right_term,Assignment):
                    return f"{self.left_term.asm()}\nmov ebx{self.right_term.asm()[7:]}\nsal eax, ebx"
                else:
                    return f"{self.left_term.asm()}\nsal eax, {self.right_term}"

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


class Block():
    def __init__(self,lexer,var_table={},stack_index=-4):
        self.result_asm = ''
        self.var_table = var_table
        #self.line_counter=1
        self.stack_index = stack_index
        self.variables = 0
        self.block_variables = []
        self.lexer = lexer
        self.metka = 0

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
            print(f"Parser Erorr\nMissed open parentheses at 2 line")
            time.sleep(10000)
            sys.exit(1)
        elif open_par>close_par:
            print(f"Parser Erorr\nMissed close parentheses at 2 line")
            time.sleep(10000)
            sys.exit(1)

    def parse_factor(self,token_list):
        self.check_parentheses(token_list.get_list())
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
            if next_tok.type == 'open parentheses' :
                next_tok = next(token_list)
                if self.check_var(next_tok.value) :
                    self.result_asm += '\n' + self.get_var(next_tok).asm()
                    self.result_asm += '\n' + f'cmp eax, 0'
                    block = Block(self.lexer, self.var_table, self.stack_index)
                    block.parse_factor(token_list)
                    next_tok = next(token_list)
                    if next_tok.type == 'else keyword' :
                        self.result_asm += '\n' + f'je _e{self.metka}'
                        else_block = Block(self.lexer, self.var_table, self.stack_index)
                        else_block.parse_factor(token_list)
                        self.result_asm += block.result_asm
                        self.result_asm += '\n' + f'jmp _post_conditional{self.metka}'
                        self.result_asm += '\n' + f'_e{self.metka}:'
                        self.result_asm += else_block.result_asm
                        self.result_asm += '\n' + f'_post_conditional{self.metka}:'
                    else :
                        self.result_asm += '\n' + f'je _post_conditional{self.metka}'
                        self.result_asm += block.result_asm
                        self.result_asm += '\n' + f'_post_conditional{self.metka}:'
                        token_list.back()
                    self.metka += 1
                    self.parse_factor(token_list)
        elif next_tok.type == 'close brace':
            self.block_variables = set(self.block_variables)
            self.stack_index+=4*len(self.block_variables)
            for var in self.block_variables:
                self.var_table.pop(var)
            self.result_asm+='\npop ecx'*len(self.block_variables)
            return self.result_asm
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
            self.variables +=1
            self.block_variables.append(var_assign.string.string)
        elif next_tok.type == 'semicolon' :
            self.var_table[var.string]=(var,self.stack_index)
            self.variables += 1
            self.block_variables.append(var.string)



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

class FunctionBlock(Block):
    def __init__(self, lexer, var_table={}, stack_index=-4) :
        self.result_asm = ''
        self.var_table = var_table
        self.function_table = {}
        # self.line_counter=1
        self.stack_index = stack_index
        self.variables = 0
        self.block_variables = []
        self.lexer = lexer
        self.metka = 0

    def parse_factor(self,token_list):
        self.check_parentheses(token_list.get_list())
        try :
            next_tok = next(token_list)
        except :
            print("All tokens parsed")
        if next_tok.type == 'open parentheses' :
            exp = self.parse_exp(token_list)
            if next(token_list).type != 'close parentheses' :
                print("Error: ')' Expected")
                sys.exit(1)
                time.sleep(10000)
            return exp
        elif self.is_unop(next_tok) :
            op = self.convert_to_op(next_tok)
            next_tok = next(token_list)
            if next_tok.type == 'int' :
                un_op = UnOP(op, next_tok.value)
                self.result_asm += '\n' + un_op.asm()
                next_tok = next(token_list)
                if next_tok.type == 'semicolon' :
                    token_list.back()
                    return un_op
                else :
                    term = un_op
                    while next_tok.type == 'addition' or next_tok.type == 'bit shift complement' or next_tok.type == 'difference' :
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
            un_op = UnOP(op, factor)
            self.result_asm += '\n' + un_op.asm()
            return un_op
        elif next_tok.type == 'int' :
            token_list.back()
            const = self.parse_exp(token_list)
            if isinstance(const, Const) :
                self.result_asm += '\n' + const.asm()
        elif next_tok.type == 'identifier' :
            if self.check_var(next_tok.value) :
                next_tok = next(token_list)
                if next_tok.type in ['addition', 'difference', 'bit shift left'] :
                    token_list.back()
                    token_list.back()
                    exp = self.parse_exp(token_list)
                    # self.parse_factor(token_list)
                else :
                    token_list.back()
                    token_list.back()
                    next_tok = next(token_list)
                    self.parse_assignment(token_list, next_tok)
                    self.parse_factor(token_list)
                # exp = self.parse_exp(token_list)
            else :
                print(f"{self.lexer.get_line(next_tok)[2]}")
                print(f"Line {self.lexer.get_line(next_tok)[0]}, symbol {self.lexer.get_line(next_tok)[1]}")
                print(f"SyntaxError: variable '{next_tok.value}' has not assigned yet")
                time.sleep(1000)
                sys.exit(1)


        elif next_tok.type == 'int keyword' :
            variable = next(token_list)
            if self.check_var(variable.value) :
                print(f"{self.lexer.get_line(variable)[2]}")
                print(f"Line {self.lexer.get_line(variable)[0]}, symbol {self.lexer.get_line(variable)[1]}")
                print(f"SyntaxError: variable assignment. Variable '{variable.value}' can not be assign twice")
                time.sleep(1000)
                sys.exit(1)
            self.parse_assignment(token_list, variable)
            self.parse_factor(token_list)
        elif next_tok.type == 'if keyword' :
            next_tok = next(token_list)
            if next_tok.type == 'open parentheses' :
                next_tok = next(token_list)
                if self.check_var(next_tok.value) :
                    self.result_asm += '\n' + self.get_var(next_tok).asm()
                    self.result_asm += '\n' + f'cmp eax, 0'
                    block = Block(self.lexer, self.var_table, self.stack_index)
                    block.parse_factor(token_list)
                    next_tok = next(token_list)
                    if next_tok.type == 'else keyword' :
                        self.result_asm += '\n' + f'je _e{self.metka}'
                        else_block = Block(self.lexer, self.var_table, self.stack_index)
                        else_block.parse_factor(token_list)
                        self.result_asm += block.result_asm
                        self.result_asm += '\n' + f'jmp _post_conditional{self.metka}'
                        self.result_asm += '\n' + f'_e{self.metka}:'
                        self.result_asm += else_block.result_asm
                        self.result_asm += '\n' + f'_post_conditional{self.metka}:'
                    else :
                        self.result_asm += '\n' + f'je _post_conditional{self.metka}'
                        self.result_asm += block.result_asm
                        self.result_asm += '\n' + f'_post_conditional{self.metka}:'
                        token_list.back()
                    self.metka += 1
                    self.parse_factor(token_list)
        elif next_tok.type == 'close brace' :
            self.stack_index=-4
            self.result_asm += '\npop ecx' * len(self.var_table)
            return self.result_asm
        else :
            self.parse_factor(token_list)
