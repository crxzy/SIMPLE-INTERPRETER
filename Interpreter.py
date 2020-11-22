from Token import Token, PLUS, MINUS, INTEGER, EOF, MUL, DIV, LPAREN, RPAREN, ID, ASSIGN
from ast import NodeVisitor
from Lexer import Lexer
from AST import Num, BinOp, AST, UnaryOp, Assign, Var, NoOp, Program

class Parser(object):
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()

    def error(self):
        raise Exception('Invalid syntax')
        

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error()

    def factor(self):
        # (PLUS|MINUS)factor| INTEGER | LPARAN expr RPARAN
        token = self.current_token
        if token.type == INTEGER:
            self.eat(INTEGER)
            return Num(token)
        elif token.type == LPAREN:
            self.eat(LPAREN)
            node = self.expr()
            self.eat(RPAREN)
            return node
        elif token.type == PLUS:
            self.eat(PLUS)
            node = UnaryOp(token, self.factor())
            return node
        elif token.type == MINUS:
            self.eat(MINUS)
            node = UnaryOp(token, self.factor())
            return node
        else:
            node = self.variable()
            return node

    def term(self):
        # factor ((MUL | DIV)factor)*
        node = self.factor()
        while self.current_token.type in (MUL, DIV):
            token = self.current_token
            if token.type == MUL:
                self.eat(MUL)
            elif token.type == DIV:
                self.eat(DIV)
            
            node = BinOp(left=node, op=token, right=self.factor())

        return node


    def expr(self):
        # expr: term((PLUS|MINUS)term)*
        node = self.term()
        while self.current_token.type in (PLUS, MINUS):
            token = self.current_token
            if token.type == PLUS:
                self.eat(PLUS)              
            elif token.type == MINUS:
                self.eat(MINUS)

            node = BinOp(left=node, op=token, right=self.term())

        # if self.current_token.type != EOF:
        #     self.error()

        return node

    def program(self):
        p = Program()
        while self.current_token.type != EOF :
            p.children.append(self.statement())
        return p

    def statement(self):
        if self.current_token.type == ID:
            node = self.assignment_statement()
        else:
            node = self.empty()
        return node
    
    def assignment_statement(self):
        left = self.variable()
        token = self.current_token
        self.eat(ASSIGN)
        right = self.expr()
        node = Assign(left, token, right)
        return node

    def variable(self):
        node = Var(self.current_token)
        self.eat(ID)
        return node

    def empty(self):
        return NoOp()

    def parse(self):
        node = self.program()
        if self.current_token.type is not EOF:
            self.error()
        return node

class Interpreter(NodeVisitor):
    def __init__(self, parser):
        self.parser = parser
        self.GLOBAL_SCOPE = {}

    def visit_BinOp(self, node):
        if node.op.type == PLUS:
            return self.visit(node.left) + self.visit(node.right)
        elif node.op.type == MINUS:
            return self.visit(node.left) - self.visit(node.right)
        elif node.op.type == MUL:
            return self.visit(node.left) * self.visit(node.right)
        elif node.op.type == DIV:
            return self.visit(node.left) / self.visit(node.right)
    
    def visit_Num(self, node):
        return node.value

    def visit_UnaryOp(self, node):
        op = node.op.type
        if op == PLUS:
            return +self.visit(node.expr)
        elif op == MINUS:
            return -self.visit(node.expr)

    def visit_NoOp(self, node):
        pass

    def visit_Assign(self, node):
        var_name = node.left.value
        self.GLOBAL_SCOPE[var_name] = self.visit(node.right)

    def visit_Var(self, node):
        var_name = node.value
        val = self.GLOBAL_SCOPE.get(var_name)
        if val is None:
            raise NameError(repr(var_name))
        else:
            return val
    
    def visit_Program(self, node):
        for c in node.children:
            self.visit(c)

    def interpret(self):
        tree = self.parser.program()
        return self.visit(tree)

class NodeVisitor(object):
    def visit(self, node):
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception('No visit_{} method'.format(type(node).__name__))

if __name__ == "__main__":
    text = ''
    with open('lexer.txt', 'r') as f:
        text = f.read()
    parser = Parser(Lexer(text))
    result = Interpreter(parser).interpret()
    print(result)
        
            