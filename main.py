from pygame.locals import *
import pygame
import math
import os
import sys

from syntaxHighlighter import Util

pygame.init()

def get_shifted_character(char, shift_pressed):
    if not isinstance(char, str) or len(char) != 1:
        raise ValueError("Input must be a single character")

    if shift_pressed:
        shifted_chars = {
            '1': '!',
            '2': '"',
            '3': '£',
            '4': '$',
            '5': '%',
            '6': '^',
            '7': '&',
            '8': '*',
            '9': '(',
            '0': ')',
            '`': '¬',
            '-': '_',
            '=': '+',
            '[': '{',
            ']': '}',
            '\\': '|',
            ';': ':',
            "'": '@',
            ',': '<',
            '.': '>',
            '/': '?',
        }
        if char in shifted_chars:
            return shifted_chars[char]
        else:
            return char.upper()

    return char.upper()

def MyPrint(*args, sep=" ", end="\n"):
    text = sep.join(map(str, args)) + end

    global Client
    Client.TerminalText += text

    Client.DisplayTerminal()
    pygame.display.flip()


class PyTri:
    def __init__(self, screen, path):
        self.Path = path
        self.Program, self.ProgramLines = self.ReadProgram(path)
        self.Screen = screen
        self.ScreenSize = screen.get_size()

        # Basic Colour Indexing
        self.ProgramUtil = Util()
        self.Plugins = []
        
        # Consts
        self.NORMAL_CODE_COLOUR = (200, 200, 200)
        self.INTIGER_COLOUR = (100, 100, 200)
        self.STRING_COLOUR = (10, 200, 10)

        # Variables
        self.running = True
        self.ScrollIndex = 0
        self.CursorPos = [0, 1]
        self.TerminalText = ""
        self.PopupSelected = 0

        # Load some data about the program
        with open("version.txt", "r") as VersionFile:
            VersionData = VersionFile.read().split("\n")

        self.Version = VersionData[1]
        self.Build = VersionData[2]

    def Hook(self, Plugin): # I really need to improve this. jesus - Look it somehow works
        exec(f"from {Plugin.replace('/', '.')} import Plugin as _{Plugin.replace('/', '_')}") # Import Plugin
        LoadedPlugin = eval(f"_{Plugin.replace('/', '_')}(self)")

        LoadedPlugin.OnStart()
        self.Plugins.append(LoadedPlugin)

    def ReadProgram(self, path):
        with open(path, "r") as f:
            program = f.read()

        return program, program.split("\n")

    def DrawText(self, text, x, y, colour, size=20, blit=True):
        font = pygame.font.Font("CONSOLA.TTF", size)
        text_surface = font.render(text, True, colour)
        text_rect = text_surface.get_rect()
        text_rect.topleft  = (x, y)
        if blit == True:
            self.Screen.blit(text_surface, text_rect)
        return text_surface.get_width(), text_surface.get_height()

    def Display(self):
        self.DisplayHeader() # Unsure if I need to do this first or last
        self.DisplayLines()
        self.DisplayPopupIfNeeded()

        if self.TerminalText != "":
            self.DisplayTerminal()

    def DisplayPopupIfNeeded(self):
        CurrentWord = self.ProgramUtil.current_word(self.ProgramLines, self.CursorPos)

        self.PopupOpen = False
        if not self.ProgramUtil.is_current_word_complete(CurrentWord, self.LocalVariables, self.LocalFunctions):
            if CurrentWord != None:
                Suggestions = self.ProgramUtil.predicte_word(CurrentWord, self.LocalVariables, self.LocalFunctions)
                self.DisplayPopup(Suggestions)
                self.PopupOpen = True

                for plugin in self.Plugins:
                    plugin.OnHover(CurrentWord)


    def DisplayHeader(self):
        HEADER_COLOUR = (90, 90, 90)
        LIGHT_PURPLE = (161, 132, 241)
        DARK_PURPLE = (139, 102, 238)
        WHITE = (250, 250, 250)
        GREEN = (53, 158, 18)

        # Draw / shade triangles
        pygame.draw.rect(self.Screen, HEADER_COLOUR, pygame.rect.Rect(0, 0, self.ScreenSize[0], 100))
        pygame.draw.polygon(self.Screen, LIGHT_PURPLE, [(15, 81), (100, 79), (30, 20)])
        pygame.draw.polygon(self.Screen, DARK_PURPLE, [(15, 81), (95, 79), (19, 65)])

        # Tidy up logo
        self.Screen.set_at((56, 80), DARK_PURPLE)
        self.Screen.set_at((57, 80), DARK_PURPLE)
        self.Screen.set_at((58, 80), DARK_PURPLE)

        # Draw text
        self.DrawText("PyTri", 20, 30, WHITE, size=50)
        self.DrawText(self.Version, 155, 53, GREEN, size=20)



    def DisplayPopup(self, SuggestedItems):
        self.SuggestedItems = SuggestedItems
        Y_Offset = 105

        LongestItem = ""
        for string in SuggestedItems:
            # Check if the current string's length is greater than the length of the stored string
            if len(string) > len(LongestItem):
                # If it is, update the value of 'x' to the current string
                LongestItem = string

        if 0 < (self.CursorPos[1] - self.ScrollIndex) < 50:
            a, b = self.DrawText("|", self.Xpos - 2, ((self.CursorPos[1] - 1 - self.ScrollIndex) * self.LineSeperationDistance) + Y_Offset, self.ProgramUtil.NORMAL_CODE_COLOUR, blit=False)

            X = self.Xpos - 2 + a
            Y = ((self.CursorPos[1] - 1 - self.ScrollIndex) * self.LineSeperationDistance) + Y_Offset + b

            MaxWidth, _ = self.DrawText(LongestItem, 0, 0, self.ProgramUtil.NORMAL_CODE_COLOUR, blit=False)

            if -self.PopupSelected > (len(SuggestedItems) - 1):
                self.PopupSelected = -(len(SuggestedItems) - 1)
            if -self.PopupSelected < 0:
                self.PopupSelected = 0

            # Base colour
            pygame.draw.rect(self.Screen, (50, 50, 50),  pygame.rect.Rect(X, Y, MaxWidth, self.YChange * len(SuggestedItems)))
            # Selected Item
            pygame.draw.rect(self.Screen, (10, 10, 150), pygame.rect.Rect(X, Y - (self.YChange * self.PopupSelected), MaxWidth, self.YChange))

            # Display Text
            for index, suggestion in enumerate(SuggestedItems):
                self.DrawText(suggestion, X, Y + (self.YChange * index), self.NORMAL_CODE_COLOUR)

    def AutoComplete(self):
        CurrentWord = self.ProgramUtil.current_word(self.ProgramLines, self.CursorPos)

        CorrectWord = self.SuggestedItems[-self.PopupSelected]

        self.ProgramLines[self.CursorPos[1] - 1] = self.ProgramLines[self.CursorPos[1] - 1][:self.CursorPos[0] - len(CurrentWord)] + CorrectWord + self.ProgramLines[self.CursorPos[1] - 1][self.CursorPos[0]:]

        self.CursorPos[0] += len(CorrectWord) - len(CurrentWord)

    def DisplayLines(self, X_Offset=0, Y_Offset=105):
        LineOffset = 0
        NumberOffset = 50
        
        y = Y_Offset

        _ = 0
        for LineIndex, Line in enumerate(self.ProgramLines[self.ScrollIndex:self.ScrollIndex + 50]):
            NewXOffset, NewYOffset = self.DrawText(str(LineIndex + self.ScrollIndex + 1), X_Offset, y, self.NORMAL_CODE_COLOUR)

            Colourized = self.ProgramUtil.highlight_syntax(Line)
            sub_x = 0
            for character, colour in Colourized:
                t, _ = self.DrawText(str(character) , X_Offset + NumberOffset + sub_x, y, colour)
                sub_x += t
            y += (NewYOffset + LineOffset)
        self.LineSeperationDistance = _ + LineOffset

        # Draw Cursor
        YChange = 0
        Xpos = X_Offset + LineOffset + NumberOffset
        for Index, char in enumerate(self.ProgramLines[self.CursorPos[1] - 1]):
            if Index == self.CursorPos[0]:
                break
            XChange, YChange = self.DrawText(char, 0, 0, (0, 0, 0), blit=False)
            Xpos += XChange

        self.YChange = YChange
        self.Xpos = Xpos

        if 0 < (self.CursorPos[1] - self.ScrollIndex) < 50:
            self.DrawText("|", Xpos - 2, ((self.CursorPos[1] - 1 - self.ScrollIndex) * self.LineSeperationDistance) + Y_Offset, self.ProgramUtil.NORMAL_CODE_COLOUR)

    def DisplayTerminal(self):
        pygame.draw.rect(self.Screen, (60, 60, 60), pygame.rect.Rect(0.0, self.ScreenSize[1] * 0.6, self.ScreenSize[0], self.ScreenSize[1] * 0.4))
        Ypos = self.ScreenSize[1] * 0.6 + 10


        for index, line in enumerate(self.TerminalText.split("\n")):
            dx, dy = self.DrawText(line, 5, Ypos, self.ProgramUtil.NORMAL_CODE_COLOUR)
            Ypos += dy


    def Tick(self):
        self.LocalVariables, self.LocalFunctions = self.ProgramUtil.LightIndex(self.ProgramLines)

        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False

                # Run exit plugins
                for plugin in self.Plugins:
                    plugin.OnClose()
                return

            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                if event.button == 4:  # Scroll Up
                    if self.ScrollIndex <= 0:
                        self.ScrollIndex = 0
                    else:
                        self.ScrollIndex -= 1
                elif event.button == 5:  # Scroll Down
                    self.ScrollIndex += 1
                elif event.button == 1:
                    self.LeftClick(x, y)

            if event.type == pygame.KEYDOWN:
                self.Type(pygame.key.name(event.key))

        self.ShiftPressed = pygame.key.get_pressed()[pygame.K_LSHIFT]
        self.CtrlPressed = pygame.key.get_pressed()[pygame.K_LCTRL]

        for plugin in self.Plugins:
            plugin.Tick()

    def LeftClick(self, x, y):
        for plugin in self.Plugins:
            plugin.OnLeftClick([x, y])

        if (y > 105):
            try:
                LineNumber = math.floor((y - 105) / self.LineSeperationDistance) + 1

                # Run through all characters in the line as all characters are slightly different sizes.
                CharacterNumber, XChange, Xpos = 0, 0, 50
                for char in self.ProgramLines[LineNumber - 1 + self.ScrollIndex]:
                    if Xpos > x:
                        break
                    XChange, YChange = self.DrawText(char, 0, 0, (0, 0, 0), blit=False)
                    Xpos += XChange
                    CharacterNumber += 1

                self.CursorPos = [CharacterNumber, LineNumber + self.ScrollIndex]
            except IndexError:
                pass # No text to click on - Do nothing

    def Type(self, key):
        for plugin in self.Plugins:
            exitTrue = plugin.OnType(key)
            if exitTrue:
                return


        if len(key) != 1:
            if key == "backspace":
                if (self.CursorPos[0] == 0) and (self.CursorPos[1] == 1):
                    return

                if self.CursorPos[0] != 0:
                    self.ProgramLines[self.CursorPos[1] - 1] = self.ProgramLines[self.CursorPos[1] - 1][:self.CursorPos[0]-1] +\
                                                               self.ProgramLines[self.CursorPos[1] - 1][self.CursorPos[0]:]
                    self.CursorPos[0] -= 1
                elif self.CursorPos[1] != 0:
                    x, y = self.CursorPos
                    t = len(self.ProgramLines[y - 2])
                    self.ProgramLines[y - 2] = self.ProgramLines[y - 2] + self.ProgramLines[y - 1]
                    self.ProgramLines.pop(y - 1)
                    self.CursorPos[1] -= 1
                    self.CursorPos[0] = t

            elif key == "delete":
                if self.CursorPos[1] == len(self.ProgramLines):
                    return

                if self.ProgramLines[self.CursorPos[1] - 1][self.CursorPos[0]:] == "":
                    self.ProgramLines[self.CursorPos[1] - 1] = self.ProgramLines[self.CursorPos[1] - 1][:self.CursorPos[0]] +\
                                                               self.ProgramLines[self.CursorPos[1]]
                    self.ProgramLines.pop(self.CursorPos[1])
                else:
                    self.ProgramLines[self.CursorPos[1] - 1] = self.ProgramLines[self.CursorPos[1] - 1][:self.CursorPos[0]] +\
                                                               self.ProgramLines[self.CursorPos[1] - 1][self.CursorPos[0]+1:]
            elif key == "return":
                self.ProgramLines.insert(self.CursorPos[1], self.ProgramLines[self.CursorPos[1] - 1][self.CursorPos[0]:])
                self.ProgramLines[self.CursorPos[1]-1] = self.ProgramLines[self.CursorPos[1]-1][:self.CursorPos[0]]
                self.CursorPos = [0, self.CursorPos[1] + 1]

            elif key == "space":
                self.ProgramLines[self.CursorPos[1] - 1] = self.ProgramLines[self.CursorPos[1] - 1][:self.CursorPos[0]] + " " + self.ProgramLines[self.CursorPos[1] - 1][self.CursorPos[0]:]
                self.CursorPos[0] += 1

            elif key == "tab":
                if self.PopupOpen:
                    self.AutoComplete()

                else:
                    self.ProgramLines[self.CursorPos[1] - 1] = self.ProgramLines[self.CursorPos[1] - 1][:self.CursorPos[0]] + "    " + self.ProgramLines[self.CursorPos[1] - 1][self.CursorPos[0]:]
                    self.CursorPos[0] += 4

            elif key == "left":
                if self.CursorPos[0] != 0:
                    self.CursorPos[0] -= 1

            elif key == "right":
                if self.CursorPos[0] < len(self.ProgramLines[self.CursorPos[1] - 1]) :
                    self.CursorPos[0] += 1

            elif key == "up":
                if self.PopupOpen:
                    if self.PopupSelected != 0:
                        self.PopupSelected += 1
                else:
                    if self.CursorPos[1] != 1:
                        self.CursorPos[1] -= 1

            elif key == "down":
                if self.PopupOpen:
                    self.PopupSelected -= 1
                else:
                    if self.CursorPos[1] != len(self.ProgramLines):
                        self.CursorPos[1] += 1

            return

        ShiftPressed = pygame.key.get_pressed()[pygame.K_LSHIFT]

        if ShiftPressed:
            key = get_shifted_character(key, ShiftPressed)

        self.ProgramLines[self.CursorPos[1] - 1] = self.ProgramLines[self.CursorPos[1] - 1][:self.CursorPos[0]] + key + self.ProgramLines[self.CursorPos[1] - 1][self.CursorPos[0]:]
        self.CursorPos[0] += 1

    def UpdateProgram(self):
        self.Program = "\n".join(self.ProgramLines)

    def Save(self, path=None):
        self.UpdateProgram()

        if path == None:
            return self.Program

        for plugin in self.Plugins:
            plugin.OnSave(path)

        Mode = "w" if os.path.exists(path) else "x"
        with open(path, Mode) as f:
            f.write(self.Program)

    def PrintData(self, *args, sep=" ", end="\n"): # broken
        PrintList = [str(x) for x in args]
        PrintString = sep.join(PrintList) + end

        self.TerminalText += PrintString

        self.DisplayTerminal()
        pygame.display.flip()

    def UpdateTerminal(self):
        pass

    def Run(PyTri_Instance, PyTri_Instance_BreakLine=None, PyTri_Instance_OpenVariableWindow=True):
        # This is just the bare bones. need to add breaks and variable windows
        for PyTri_Plugin in PyTri_Instance.Plugins:
            PyTri_Plugin.OnRun()

        PyTri_Instance.TerminalText = ""
        # Set print function to our custom one
        global print
        PyTri_Instance_NormalPrint = print
        print = MyPrint


        PyTri_ExitCode = 0
        PyTri_ErrorCode = None

        try:
            exec(PyTri_Instance.Program)
        except Exception as e:
            PyTri_ErrorCode = e
            print(e)

        # Reset/Restore print function
        print = PyTri_Instance_NormalPrint

        for plugin in PyTri_Instance.Plugins:
            plugin.OnFinish(PyTri_ExitCode, PyTri_ErrorCode)


def Run():
    width = 1920
    height = 1080
    screen = pygame.display.set_mode((width, height))

    global Client
    Client = PyTri(screen, "testScript.py")

    # DEFAULT PLUGINS
    Client.Hook("default_plugins/undo")
    Client.Hook("default_plugins/shortcut_manager")

    while Client.running:
        # Update Pygame and Inputs
        Client.Tick()

        # Display
        screen.fill((40, 40, 43))
        Client.Display()

        pygame.display.flip()  # Update the screen (Flip Double Buffer)

    pygame.quit()


if __name__ == "__main__":
    Run()