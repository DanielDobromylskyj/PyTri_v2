def Switch(x):
    return True if x == False else False

def split_string_at_chars(string, chars):
    Output = []
    prevWord = ""
    prevChar = ""

    InString = False
    StringType = None

    for StringCharacter in list(string):
        if (StringCharacter == "'") and ((StringType == "'") or (StringType == None)):
            InString = Switch(InString)
            StringType = StringCharacter if InString else None
        if (StringCharacter == '"') and ((StringType == '"') or (StringType == None)):
            InString = Switch(InString)
            StringType = StringCharacter if InString else None

        if InString:
            prevWord = prevWord + StringCharacter
        else:
            if (StringCharacter in chars):
                Output.append(prevWord)
                Output.append(StringCharacter)
                prevWord = ""
            else:
                prevWord = prevWord + StringCharacter

        prevChar = StringCharacter

    if InString:
        Output.append(prevWord)

    return Output


class Util:
    STRING_COLOUR = (10, 200, 10)
    INTEGER_COLOUR = (59, 66, 249)
    KEYWORD_COLOUR = (200, 200, 200)
    INBUILTFUNC_COLOUR = (243, 161, 20)
    OTHERFUNC_COLOUR = (240, 64, 240)
    NORMAL_CODE_COLOUR = (200, 200, 200)

    KEYWORDS = {
        "str": OTHERFUNC_COLOUR,
        "int": OTHERFUNC_COLOUR,
        "float": OTHERFUNC_COLOUR,
        "print":OTHERFUNC_COLOUR,
        "enumerate": OTHERFUNC_COLOUR,
        "eval": OTHERFUNC_COLOUR,
        "open": OTHERFUNC_COLOUR,
        "__init__": OTHERFUNC_COLOUR,

        "def":INBUILTFUNC_COLOUR,
        "class":INBUILTFUNC_COLOUR,
        "return": INBUILTFUNC_COLOUR,
        "if": INBUILTFUNC_COLOUR,
        "elif": INBUILTFUNC_COLOUR,
        "else": INBUILTFUNC_COLOUR,
        "and": INBUILTFUNC_COLOUR,
        "or": INBUILTFUNC_COLOUR,
        "with": INBUILTFUNC_COLOUR,
        "for": INBUILTFUNC_COLOUR,
        "in": INBUILTFUNC_COLOUR,
        "as": INBUILTFUNC_COLOUR,
        "import": INBUILTFUNC_COLOUR,
        "from": INBUILTFUNC_COLOUR,
        "True": INBUILTFUNC_COLOUR,
        "False": INBUILTFUNC_COLOUR,
        "None": INBUILTFUNC_COLOUR,

        "self": (180, 44, 180),
    }

    def highlight_syntax(self, code):
        code = code + " "
        highlighted_code = []

        for token in split_string_at_chars(code, "()[]{}: ,.="):
            if token == ",":
                highlighted_code.append((token, self.INBUILTFUNC_COLOUR))
            elif token in "()[]{}: =":
                highlighted_code.append((token, self.NORMAL_CODE_COLOUR))

            elif (token.startswith('"')) or (token.startswith("'") or (token.startswith("f'")) or (token.startswith('f"')) or (token.startswith('"""'))):
                highlighted_code.append((token, self.STRING_COLOUR))

            elif token.isdigit():
                highlighted_code.append((token, self.INTEGER_COLOUR))

            elif token in self.KEYWORDS:
                highlighted_code.append((token, self.KEYWORDS[token]))

            else:
                highlighted_code.append((token, self.NORMAL_CODE_COLOUR))

        return highlighted_code


    def LightIndex(self, code:list):
        Variables = {}
        Functions = {}

        for line in code:
            try:
                if ("=" in line) and not (("if" in line) or ("else" in line) or ("def" in line)): # Check for assignment operator
                    varName = line.replace(" ", "").split("=")[0].split(".")[-1]
                    varType = "Unknown"

                    Variables[varName] = varType

                if "def " in line:
                    funcName = line.replace(" ", "").split("def")[1].split("(")[0]
                    Args = line.split(funcName)[1].replace(":", "")
                    Functions[funcName] = Args

            except ValueError: # Incomplete variable / function
                pass

        return Variables, Functions



    def _recursive_word_search(self, line, pos, direction):
        if 0 < pos < len(line) - 1:
            Character = line[pos]
            if Character in """.,-+=(){}[]"' """:
                return ""

            if direction == -1:
                return self._recursive_word_search(line, pos + direction, direction) + Character
            return Character + self._recursive_word_search(line, pos + direction, direction)

        return ""


    def current_word(self, code_lines, cursor_pos):
        Line = " " + code_lines[cursor_pos[1] - 1] + " "

        LeftSide = self._recursive_word_search(Line, cursor_pos[0] - (1 if cursor_pos[0] != 0 else 0), -1)
        RightSide = self._recursive_word_search(Line, cursor_pos[0], 1)

        Word = ""
        if cursor_pos[0] != len(Line):
            Word = LeftSide + RightSide

        if Word.replace(" ", "") == "":
            return None

        return Word


    def is_current_word_complete(self, Word, Variables, Functions):
        if (Word in self.KEYWORDS) or (Word in Variables) or (Word in Functions):
            return True
        return False

    def find_percent_matched(self, a, b):
        if len(a) > len(b): # if 'a' is larger than 'b', it cant be it
            return 0

        MatchedChars = 0
        for index, charA in enumerate(list(a)):
            if charA == b[index]:
                MatchedChars += 1

        return (MatchedChars / len(a)) * 100



    def predicte_word(self, Current, Variables, Functions):
        ACCEPTABLE_PERCENTAGE = 60

        Suggested = []

        for var in Variables.keys():
            score = self.find_percent_matched(Current, var)
            if score > ACCEPTABLE_PERCENTAGE:
                Suggested.append(var)

        for func in Functions.keys():
            score = self.find_percent_matched(Current, func)
            if score > ACCEPTABLE_PERCENTAGE:
                Suggested.append(func)

        for keyword in self.KEYWORDS:
            score = self.find_percent_matched(Current, keyword)
            if score > ACCEPTABLE_PERCENTAGE:
                Suggested.append(keyword)

        return Suggested if len(Suggested) < 4 else Suggested[:3]







