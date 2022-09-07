from collections import Counter
import re

re_patterns = {
    r'\\frac{([^}]+)}{([^}]+)}': r'((\1)/(\2))',
    r'\\times': '*',
    r'\\left': '',
    r'\\right': '',
    r'×|\\alpha': '*',
    r's|S': '5',
    r'b': '6',
    r'g|q|\\rho': '9',
    r't': '+',
    r'L': 'c',
    r'\]|\[|l|\\mid': '1'
}


def _convert_latex(exp: str):
    """
    LaTeX formatted string (exp) and returns an operable expression. For example "\frac{7}{5+y}" returns
    "((7)/(5+y))". It does by iterating over the items in self.re_patterns, where the keys are regex patterns, and
    the values are strings which should replace the patterns.
    :param exp: A LaTeX formatted string
    :return: An interoperable string (with white-space removed)
    """
    for pattern, replace in re_patterns.items():
        exp = re.sub(pattern, replace, exp)
    exp = exp.replace(" ", "")  # Remove any remaining whitespace
    return exp.lower()  # Lowercase all values in the expression


def _syntactic_analysis(exp: str):
    """
    During syntactic analysis (parsing), the sequence of interoperable string produced by the self.convert_latex is
    examined whether or not it is a mathematically meaningful statement. For example ((2-1+) is NOT meaningful,
    whereas (2-1) is.
    :param exp: An interoperable string (as formatted by the convert_latex() method)
    :return: True if the syntax is correct, False otherwise
    """
    stack = []  # Checks whether the brackets in the expression are correct
    for i, char in enumerate(exp):
        if char == '(':
            stack.append(char)
        elif char == ')':
            if len(stack) == 0:
                return False  # Prevents )() and other such issues
            elif exp[i - 1] == '+' or exp[i - 1] == '/' or exp[i - 1] == '*' or exp[i - 1] == '-':
                return False  # +) /) ×)
            stack.pop()
            continue
        elif char == '/' or char == '*':
            if i == 0:
                return False
            elif exp[i - 1] == '+' or exp[i - 1] == '/' or exp[i - 1] == '*' or exp[i - 1] == '-' or exp[i - 1] == '=':
                return False  # /+ /- // /× =/ ×+ ×- ×/ ×× =×
        elif char == '+':
            if i == 0:  # Expression that starts with a plus is allowed
                continue
            elif exp[i - 1] == '+' or exp[i - 1] == '*' or exp[i - 1] == '/' or exp[i - 1] == '=':  # ++ ×+ /+ =+
                return False
            elif i > 2:
                if exp[i - 1] == '-' and not exp[i - 2].isnumeric():  # +-+ --+ +++ -++ (-+ etc.
                    return False
        elif char == '-':
            if i == 0:  # Expression that starts with -- is allowed
                continue
            elif i > 2:
                if (exp[i - 1] == '+' or exp[i - 1] == '-' or exp[i - 1] == '*' or exp[i - 1] == '/') \
                        and (not exp[i - 2] in 'mxcy0123456789'):  # +-- --- -+- ++- (-- *-- *+- /-- etc.
                    return False
        elif char == '=':
            if i == 0:
                continue  # Expression that starts with = is allowed
            elif exp[i - 1] == '+' or exp[i - 1] == '/' or exp[i - 1] == '*' or exp[i - 1] == '-' or exp[i - 1] == '=':
                return False  # /= -= ×= += ==
            elif len(stack) > 0:
                return False  # Prevents (x = c) = 4
        elif char.isnumeric():
            if i == 0:
                continue
            if exp[i - 1].isalpha():
                return False  # Prevents a2
        elif char.isalpha() and char not in 'ymxc':
            return False  # Not all that useful but acts as a safety net if user attempts to add other characters
    if len(stack) > 0:
        return False  # Prevents (() and other errors with opening and closing brackets
    return True


def _lexical_analysis(exp: str):
    """
    Lexical analysis (tokenization) splits the input text (a string or a text file) into minimal meaningful units.
    Takes a Python formatted expression, and arranges into a list. All - signs are replaced by + and the number
    proceeding the negative has its sign inverted. An equal sign in the expression will split the string into two
    lists.
    :param exp: An interoperable expression (see self.convert_latex for more details)
    :return: A list of lists, with each list being an expression
    """
    temp = ''  # A temporary string we will use to store numbers (since the loop will read them one at a time)
    prev = None  # Stores the previous value -> used to check for -- or +-
    res = [[]]  # Our list of lists
    for char in exp:
        if char == '=':
            if prev is None:
                continue
            if len(temp) > 0:
                res[-1].append(temp)
                temp = ''
            res.append([])
        elif char.isnumeric():
            temp += char
        else:
            if prev is None:
                if char.isnumeric():
                    temp += char
                else:
                    if char == '+' or char == '-':
                        temp += char
                    else:
                        res[-1].append(char)
            elif prev.isnumeric():
                res[-1].append(temp)
                res[-1].append(char)
                temp = ''
            elif prev == ')':
                res[-1].append(char)
                if len(temp) > 0:
                    res[-1].append(temp)
                    temp = ''
            else:
                if (char == '-' or char == '+') and (prev in '-+=()*'):
                    # For example converts (-20) into ['(','-20',')'] and 3-+4 into ['3','-','+4']
                    temp += char
                else:
                    if temp == '+' or temp == '-':
                        res[-1].append(temp)
                    res[-1].append(char)
                    temp = ''
        prev = char
    if len(temp) > 0:
        res[-1].append(temp)
    return res


def _adjust_coefficient(user_input: str, variable: str):
    """
    A function that converts Nx --> N×x
    :param user_input: A mathematical expression e.g. y=c+2x
    :param variable: The variable to be adjusted
    :return: String with the conversions, e.g. y=c+2*x
    """
    if variable not in user_input:
        return user_input
    i = user_input.index(variable)
    if i != 0:
        if user_input[i - 1].isnumeric() or user_input[i - 1] == ')':  # If Nx [and not -x (x or +x]
            user_input = user_input[:i] + '*' + user_input[i:]
        elif user_input[i - 1] == '-':  # If -x
            user_input = user_input[:i - 1] + '-1*' + user_input[i:]
    return user_input


def _check_float(string):
    """
    Call float(x) to convert string x to a float. Use try and except to check if an error occurs during the conversion.
    """
    try:
        float(string)
        return True
    except ValueError:
        return False


def _contains_number(user_input: str):
    for sublist in user_input:
        for x in sublist:
            if _check_float(x):
                return True
    return False


def parse(function):
    def wrapper(self, exp, *args, **kwargs):
        if function.__name__ == 'two':
            exp = re.sub(r"x|X", "*", exp)
        exp = _convert_latex(exp)  # Convert to a interoperable string
        if not _syntactic_analysis(exp):  # Check if string is mathematically valid
            return False
        for variable in ('x', 'y'):  # Adjust the coefficients (i.e. Nx --> N * x)
            exp = _adjust_coefficient(exp, variable)
        exp = _lexical_analysis(exp)
        return function(self, exp, *args, **kwargs)

    return wrapper


class LatexParser:

    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.m = float((y2 - y1) / (x2 - x1))
        self.c = float(y1 - (self.m * x1))

    def _evaluate_expression(self, exp: list):
        """
        Uses recursive descent parsing to evaluate an expression. The function checks for the existence of a bracket,
        if it finds one then it adds its index to the stack. When the function finds a closed bracket symbol it calls
        the evaluate_brackets() method.
        :param exp: A list of tokenized statements (see self.lexical_analysis() for more details)
        :return: False if there was a ZeroDivisionError, otherwise it returns the evaluated expression
        """
        stack = []
        for i, x in enumerate(exp):
            if x == '(':
                stack.append(i)
            elif x == ')':
                start = stack.pop()
                result = self._evaluate_brackets(exp[start + 1: i])
                if result is not False:
                    exp[start: i + 1] = result
                    return self._evaluate_expression(exp)
                else:
                    return False
        return self._evaluate_brackets(exp)

    @staticmethod
    def _evaluate_brackets(exp: list):
        """
        Evaluates an expression in the following order: Multiplication, Division, Addition, Subtraction
        :param exp: A list of tokenized statements (see self.lexical_analysis() for more details)
        :return: False if there was a ZeroDivisionError, otherwise it returns the evaluated expression
        """
        count = 1
        while len(exp) > 1:
            if '*' in exp:
                index = exp.index('*')
                product = float(exp[index - 1]) * float(exp[index + 1])
                exp.insert(index + 2, product)
                del exp[index - 1:index + 2]
                continue
            if '/' in exp:
                index = exp.index('/')
                try:
                    division = float(exp[index - 1]) / float(exp[index + 1])
                except ZeroDivisionError:
                    return False
                exp.insert(index + 2, division)
                del exp[index - 1:index + 2]
                continue
            if '+' in exp:
                index = exp.index('+')
                summation = float(exp[index - 1]) + float(exp[index + 1])
                exp.insert(index + 2, summation)
                del exp[index - 1:index + 2]
                continue
            if '-' in exp:
                index = exp.index('-')
                subtraction = float(exp[index - 1]) - float(exp[index + 1])
                exp.insert(index + 2, subtraction)
                del exp[index - 1:index + 2]
                continue
            # If the loop has descended to this point then something has gone wrong
            if count > 5:  # Prevents a infinite iterations
                break
            count += 1

        return exp

    def _check_solution(self, exp: list, solution=None):
        """
        Iterates over the list of list and reduced each expression submitted by the user to its simplest form.
        If a solution is given the function checks whether or not each given expression equals the solution. If a
        solution is not given, then the function checks whether submitted expression is equal to each other.
        :param exp: user input expressed as str in a LaTeX form
        :param solution: model answer expressed as an integer - default is None
        :return: True if all expressions reduce to "solution". False if any expression cannot be reduced to "solution".
        """
        if solution is None:
            evaluated_expressions = set()
            for expression in exp:
                simplified = self._evaluate_expression(expression)          # Evaluate each expression
                if _check_float(simplified[0]):
                    evaluated_expressions.add(float(simplified[0]))
            return len(evaluated_expressions) == 1
        else:
            for expression in exp:
                simplified = self._evaluate_expression(expression)
                if simplified is False:                                     # ZeroDivisionError
                    return False
                elif len(simplified) == 0:                                  # User left the solution blank
                    return False
                if _check_float(simplified[0]):
                    if float(simplified[0]) != solution:
                        return False
                else:
                    return False
            return True


    @staticmethod
    def _substitute_value(expression, variable: str, value: str):
        """
        :param expression: A list of lists example: [['y'], ['m', '*', 'x', '+', 'c']]
        :param variable: The variable to be substituted
        :param value: The value the variable will take
        """
        return [[value if term == variable else term for term in exp] for exp in expression]

    @staticmethod
    def _check_instance(expression, conditions: dict, equals=False):
        """
        Then checks whether variables, as specified by the conditions parameter, are in the expression.
        :param expression: A list of lists example: [['(', '(', '7', '-', '5', ')', '/', '(', '2', '-', '1', ')', ')']]
        :param conditions: A dictionary whose keys are the variables and values are the number of times they should be
                           in the expression.
        :param equals: True the expression should have an equal sign (aka contains more than one list)
        :return: True if all conditions are met, False otherwise
        """
        if equals and len(expression) == 1:  # If the expression needs to include an equal sign
            return False
        counts = Counter(x for sublist in expression for x in sublist)
        for key, value in conditions.items():
            number = counts.get(key, 0)  # If value not in Counter then it must appear 0 times
            if value == -1 and number > 0:  # At lease one of the key
                continue
            if number != value:
                return False
        return True

    def run(self, user_input: str, id_number: int):
        if id_number == 0:
            return self.zero(user_input)
        if id_number == 1:
            return self.one(user_input)
        if id_number == 2:
            return self.two(user_input)
        if id_number == 3:
            return self.three(user_input)
        if id_number == 4:
            return self.four(user_input)

    @parse
    def run_tutorial(self, user_input: str, id_number: int):
        if id_number == 4:
            return user_input == [['(', '(', '3', ')', '/', '(', '4', ')', ')']]
        if id_number == 3:
            return user_input == [['5', '*', '8'], ['40']]
        if id_number == 2:
            return user_input == [['y'], ['-3', '*', 'x', '+', 'c']]
        if id_number == 1:
            return user_input == [['(', '(', '1', ')', '/', '(', '2', ')', ')']] or [['1', '/', '2']]
        return user_input == [['y'], ['m', 'x', '+', 'c']]

    @parse
    def zero(self, user_input: str):
        """
        First checks whether solution has the correct syntax, evaluates the users solution, substituting m for the value
        of m if present. The function then checks whether each evaluated expression is equal to self.m (aka correct)
        :return True if step is correct, False otherwise
        """
        if not self._check_instance(user_input, {'c': 0, 'x': 0, 'y': 0}):  # Solution must not have c, x or y in it
            return False
        user_input = self._substitute_value(user_input, 'm', str(self.m))
        return self._check_solution(user_input, solution=self.m)

    @parse
    def one(self, user_input: str):
        """
        Checks whether the user_input is in the correct format. Then checks whether 'c', 'x', 'y' and '=' is in the user
        input. Then substitutes values.
        :return: True if step is correct, False otherwise
        """
        if not self._check_instance(user_input, {'y': 1, 'c': 1, 'm': 0}, True):
            # Solution must contain a y, x, c and an equals sign, but cannot contain an m
            return False
        solution_array = []  # Substitute both (x1, y1) and (x2, y2) into equation.
        for pair in ((('c', str(self.c)), ('x', str(self.x1)), ('y', str(self.y1))),
                     (('c', str(self.c)), ('x', str(self.x2)), ('y', str(self.y2)))):
            temp = user_input
            for (variable, value) in pair:
                temp = self._substitute_value(temp, variable, value)
            solution_array.append(temp)
        return all(map(self._check_solution, solution_array))

    @parse
    def two(self, user_input: str):
        """
        Checks whether the user_input is in the correct format. Then checks whether there is at least one 'c' in answer
        and if '=' is in the user input. Then substitutes self.c in for c.
        :return: True if step is correct, False otherwise
        """
        if not self._check_instance(user_input, {'c': -1, 'm': 0, 'y': 0}, True):
            # Solution must contain an equal sign and at least one c, and cannot contain a y or an m
            return False
        user_input = self._substitute_value(user_input, 'c', f'{self.c}')
        return self._check_solution(user_input)

    @parse
    def three(self, user_input: str):
        """
        Checks whether the user_input is in the correct format. Next it checks whether the user has submitted at least
        one number. Then, if present, substitutes values substitutes "c" for self.c
        :return: True if step is correct, False otherwise
        """
        if not _contains_number(user_input):
            return False
        if not self._check_instance(user_input, {'m': 0, 'x': 0, 'y': 0}):
            # Solution cannot contain an x, y or m
            return False
        user_input = self._substitute_value(user_input, 'c', f'{self.c}')
        return self._check_solution(user_input, self.c)

    @parse
    def four(self, user_input: str):
        """
        Checks whether solution is in correct syntax, then if '=', 'x', 'y' in user_input. Converts Nx --> N×x then
        replaces x and y with x1 and y1. Finally checks whether the solution is valid.
        :return: True if step is correct, False otherwise
        """
        if not self._check_instance(user_input, {'y': 1, 'm': 0, 'c': 0}, True):
            # Solution cannot contain an m or c and must include an x, y and an equals sign
            return False
        solution_array = []  # Substitute both (x1, y1) and (x2, y2) into equation.
        for pair in ((('x', str(self.x1)), ('y', str(self.y1))), (('x', str(self.x2)), ('y', str(self.y2)))):
            temp = user_input
            for (variable, value) in pair:
                temp = self._substitute_value(temp, variable, value)
            solution_array.append(temp)
        return all(map(self._check_solution, solution_array))


if __name__ == "__main__":

    questions = [[1, 5, 2, 7], [3, 4, 5, 20], [-3, 22, 1, 2], [-1, -4, 8, 23], [-10, 6, -2, -2], [-1, -7, 19, 133],
                 [14, 5, 6, 5], [40, 10, 20, 5]]

    test_cases = {
                    '00': ['((7-5)/(2-1))=2', '((5-7)/(1-2))=2', '2=((7-5)/(2-1))', '(2=((5-7)/(1-2)))', '((-2)/(-1))=2',
                         '2=((-2)/(-1))', '((2)/(1))=2', '2=((2)/(1))', '2', '=2', '=((7-5)/(2-1))', '((7-5)/(2-1))',
                         '((5-7)/(1-2))', '=((5-7)/(1-2))', '((-2)/(-1))', '=((-2)/(-1))', '((2)/(1))', '=((2)/(1))'],
                    '01': ['y=2x+c', 'y=c+2x', '2x+c=y', 'c+2x=y'],
                    '02': ['5=2×1+c', '5=1×2+c', '1×2+c=5', '2×1+c=5', '5=c+2×1', '5=c+1×2', 'c+2×1=5', 'c+1×2=5',
                         '2+c=5', 'c+2=5', '5=2+c', '5=c+2', 'c=5-2', '5-2=c', '7=2×2+c', '7=2×2+c', '2×2+c=7',
                         '2×2+c=7', '7=c+2×2', '7=c+2×2', 'c+2×2=7', 'c+2×2=7', '4+c=7', 'c+4=7', '7=4+c', '7=c+4',
                         'c=7-4', '7-4=c', '7=c+2x2', '5=2x1+c', '1X2+c=5'], 
                    '03': ['c=3', '3=c', '=3', '3'],
                    '04': ['y=2x+3', 'y=3+2x', '3+2x=y', '2x+3=y'],
                    '10': ['((20-4)/(5-3))=8', '((4-20)/(3-5))=8', '8=((20-4)/(5-3))', '(8=((4-20)/(3-5)))',
                         '((-16)/(-2))=8', '8=((-16)/(-2))', '((16)/(2))=8', '8=((16)/(2))', '8', '=8',
                         '=((20-4)/(5-3))', '((20-4)/(5-3))', '((4-20)/(3-5))', '=((4-20)/(3-5))', '((-16)/(-2))',
                         '=((-16)/(-2))', '((16)/(2))', '=((16)/(2))'], '11': ['y=8x+c', 'y=c+8x', '8x+c=y', 'c+8x=y'],
                    '12': ['4=8×3+c', '4=3×8+c', '3×8+c=4', '8×3+c=4', '4=c+8×3', '4=c+3×8', 'c+8×3=4', 'c+3×8=4',
                         '24+c=4', 'c+24=4', '4=24+c', '4=c+24', 'c=4-24', '4-24=c', '20=8×5+c', '20=5×8+c', '5×8+c=20',
                         '8×5+c=20', '20=c+8×5', '20=c+5×8', 'c+8×5=20', 'c+5×8=20', '40+c=20', 'c+40=20', '20=40+c',
                         '20=c+40', 'c=20-40', '20-40=c'],
                    '13': ['c=-20', '-20=c', '=-20', '-20'],
                    '14': ['y=8x-20', 'y=-20+8x', '-20+8x=y', '8x-20=y'],
                    '20': ['((2-22)/(1--3))=-5', '((22-2)/(-3-1))=-5', '-5=((2-22)/(1--3))', '(-5=((22-2)/(-3-1)))',
                         '((20)/(-4))=-5', '-5=((20)/(-4))', '((-20)/(4))=-5', '-5=((-20)/(4))', '-5', '=-5',
                         '=((2-22)/(1--3))', '((2-22)/(1--3))', '((22-2)/(-3-1))', '=((22-2)/(-3-1))', '((20)/(-4))',
                         '=((20)/(-4))', '((-20)/(4))', '=((-20)/(4))'],
                    '21': ['y=c+-5x', 'y=-5x+c', '-5x+c=y', 'c+-5x=y'],
                    '22': ['22=-5×-3+c', '22=-3×-5+c', '-3×-5+c=22', '-5×-3+c=22', '22=c+-5×-3', '22=c+-3×-5',
                         'c+-5×-3=22', 'c+-3×-5=22', '15+c=22', 'c+15=22', '22=15+c', '22=c+15', 'c=22-15', '22-15=c',
                         '2=-5×1+c', '2=1×-5+c', '1×-5+c=2', '-5×1+c=2', '2=c+-5×1', '2=c+1×-5', 'c+-5×1=2', 'c+1×-5=2',
                         '-5+c=2', 'c+-5=2', '2=-5+c', '2=c+-5', 'c=2--5', '2--5=c', '2=-5×1+c=-5+c'],
                    '23': ['c=7', '7=c', '=7', '7'],
                    '24': ['y=-5x+7', 'y=7-5x', '7-5x=y', '-5x+7=y'],
                    '30': ['((23--4)/(8--1))=3', '((-4-23)/(-1-8))=3', '3=((23--4)/(8--1))', '(3=((-4-23)/(-1-8)))',
                         '((-27)/(-9))=3', '3=((-27)/(-9))', '((27)/(9))=3', '3=((27)/(9))', '3', '=3',
                         '=((23--4)/(8--1))', '((23--4)/(8--1))', '((-4-23)/(-1-8))', '=((-4-23)/(-1-8))',
                         '((-27)/(-9))', '=((-27)/(-9))', '((27)/(9))', '=((27)/(9))'],
                    '31': ['y=3x+c', 'y=c+3x', '3x+c=y', 'c+3x=y'],
                    '32': ['-4=3×-1+c', '-4=-1×3+c', '-1×3+c=-4', '3×-1+c=-4', '-4=c+3×-1', '-4=c+-1×3', 'c+3×-1=-4',
                         'c+-1×3=-4', '-3+c=-4', 'c+-3=-4', '-4=-3+c', '-4=c+-3', 'c=-4--3', '-4--3=c', '23=3×8+c',
                         '23=8×3+c', '8×3+c=23', '3×8+c=23', '23=c+3×8', '23=c+8×3', 'c+3×8=23', 'c+8×3=23', '24+c=23',
                         'c+24=23', '23=24+c', '23=c+24', 'c=23-24', '23-24=c'], '33': ['c=-1', '-1=c', '=-1', '-1'],
                    '34': ['y=3x-1', 'y=-1+3x', '-1+3x=y', '3x-1=y'],
                    '40': ['((-2-6)/(-2--10))=-1', '((6--2)/(-10--2))=-1', '-1=((-2-6)/(-2--10))',
                         '(-1=((6--2)/(-10--2)))', '((8)/(-8))=-1', '-1=((8)/(-8))', '((-8)/(8))=-1', '-1=((-8)/(8))',
                         '-1', '=-1', '=((-2-6)/(-2--10))', '((-2-6)/(-2--10))', '((6--2)/(-10--2))',
                         '=((6--2)/(-10--2))', '((8)/(-8))', '=((8)/(-8))', '((-8)/(8))', '=((-8)/(8))'],
                    '41': ['y=-1x+c', 'y=c+-1x', '-1x+c=y', 'c+-1x=y'],
                    '42': ['6=-1×-10+c', '6=-10×-1+c', '-10×-1+c=6', '-1×-10+c=6', '6=c+-1×-10', '6=c+-10×-1',
                         'c+-1×-10=6', 'c+-10×-1=6', '10+c=6', 'c+10=6', '6=10+c', '6=c+10', 'c=6-10', '6-10=c',
                         '-2=-1×-2+c', '-2=-2×-1+c', '-2×-1+c=-2', '-1×-2+c=-2', '-2=c+-1×-2', '-2=c+-2×-1',
                         'c+-1×-2=-2', 'c+-2×-1=-2', '2+c=-2', 'c+2=-2', '-2=2+c', '-2=c+2', 'c=-2-2', '-2-2=c'],
                    '43': ['c=-4', '-4=c', '=-4', '-4'], '44': ['y=-1x-4', 'y=-4-1x', '-4-1x=y', '-1x-4=y'],
                    '50': ['((133--7)/(19--1))=7', '((-7-133)/(-1-19))=7', '7=((133--7)/(19--1))',
                         '(7=((-7-133)/(-1-19)))', '((-140)/(-20))=7', '7=((-140)/(-20))', '((140)/(20))=7',
                         '7=((140)/(20))', '7', '=7', '=((133--7)/(19--1))', '((133--7)/(19--1))', '((-7-133)/(-1-19))',
                         '=((-7-133)/(-1-19))', '((-140)/(-20))', '=((-140)/(-20))', '((140)/(20))', '=((140)/(20))'],
                    '51': ['y=7x+c', 'y=c+7x', '7x+c=y', 'c+7x=y'],
                    '52': ['-7=7×-1+c', '-7=-1×7+c', '-1×7+c=-7', '7×-1+c=-7', '-7=c+7×-1', '-7=c+-1×7', 'c+7×-1=-7',
                         'c+-1×7=-7', '-7+c=-7', 'c+-7=-7', '-7=-7+c', '-7=c+-7', 'c=-7--7', '-7--7=c', '133=7×19+c',
                         '133=19×7+c', '19×7+c=133', '7×19+c=133', '133=c+7×19', '133=c+19×7', 'c+7×19=133',
                         'c+19×7=133', '133+c=133', 'c+133=133', '133=133+c', '133=c+133', 'c=133-133', '133-133=c'],
                    '53': ['c=0', '0=c', '=0', '0'], '54': ['y=7x', '7x=y'],
                    '60': ['((5-5)/(6-14))=0', '((5-5)/(14-6))=0', '0=((5-5)/(6-14))', '(0=((5-5)/(14-6)))',
                         '((0)/(8))=0', '0=((0)/(8))', '((0)/(-8))=0', '0=((0)/(-8))', '0', '=0', '=((5-5)/(6-14))',
                         '((5-5)/(6-14))', '((5-5)/(14-6))', '=((5-5)/(14-6))', '((0)/(8))', '=((0)/(8))', '((0)/(-8))',
                         '=((0)/(-8))'], '61': ['y=0x+c', 'y=c+0x', '0x+c=y', 'c+0x=y'],
                    '62': ['5=0×14+c', '5=14×0+c', '14×0+c=5', '0×14+c=5', '5=c+0×14', '5=c+14×0', 'c+0×14=5', 'c+14×0=5',
                         '0+c=5', 'c+0=5', '5=0+c', '5=c+0', 'c=5-0', '5-0=c', '5=0×6+c', '5=6×0+c', '6×0+c=5',
                         '0×6+c=5', '5=c+0×6', '5=c+6×0', 'c+0×6=5', 'c+6×0=5', '0+c=5', 'c+0=5', '5=0+c', '5=c+0',
                         'c=5-0', '5-0=c'], '63': ['c=5', '5=c', '=5', '5'], '64': ['y=5', '5=y'],
                    '70': ["((10-5)/(40-20))=((5)/(20))=((1)/(4))"],
                    '71': ["y=((x)/(4))+c"],
                    '72': ["\\( 5=\\frac{20}{4}+c \\)"],
                    '73': ["\\( c=0 \\)"],
                    '74': ["\\( y=\\frac{x}{4} \\)"]
                }

    for i_index, (x_1, y_1, x_2, y_2) in enumerate(questions):
        solution_checker = LatexParser(x_1, y_1, x_2, y_2)
        for j_index in range(5):
            cases = test_cases[f"{i_index}{j_index}"]
            if j_index == 0:
                func = solution_checker.zero
            elif j_index == 1:
                func = solution_checker.one
            elif j_index == 2:
                func = solution_checker.two
            elif j_index == 3:
                func = solution_checker.three
            else:
                func = solution_checker.four
            print(f'--- {i_index}{j_index} ---')
            for k_index, _solution in enumerate(cases):
                _result = func(_solution)
                print(_result, test_cases[f"{i_index}{j_index}"][k_index])
