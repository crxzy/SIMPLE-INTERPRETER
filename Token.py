
INTEGER, PLUS, MINUS, EOF, MUL, DIV, LPAREN, RPAREN, ID, ASSIGN = 'INTEGER', 'PLUS', 'MINUS', 'EOF', 'MUL', 'DIV', '(', ')', 'ID', 'ASSIGN'



class Token(object):
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __str__(self):
        return 'Token({type}, {value})'.format(type=self.type, value=self.value)

    def __repr__(self) -> str:
        return self.__str__()

if __name__ == "__main__":
    print(Token(EOF, None))