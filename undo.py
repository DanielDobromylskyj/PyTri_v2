if __name__ == "__main__":
    from default_plugin import DEFAULT
else:
    from default_plugins.default_plugin import DEFAULT

class Plugin(DEFAULT):
    SAVE_DEPTH = 100

    def __init__(self, parent):
        self.PyTri = parent

    def OnStart(self):
        self.Memory = []

    def OnType(self, key):
        if (key == "z") and (self.PyTri.CtrlPressed == True):
            if len(self.Memory) != 0:
                self.Memory[-1].Reverse(self.PyTri)
                self.Memory = self.Memory[:-1]

        else:
            self.Memory.append(
                Change(eval(str(self.PyTri.ProgramLines)), eval(str(self.PyTri.CursorPos)))
            )

        # To much data saved, remove first (remembered) object
        if len(self.Memory) > self.SAVE_DEPTH:
            self.Memory.pop(0)

        if (key == "z") and (self.PyTri.CtrlPressed):
            return True



class Change():
    def __init__(self, data, cursor):
        self.Data = data
        self.CursorPos = cursor

    def Reverse(self, PyTri):
        PyTri.ProgramLines = eval(str(self.Data))
        PyTri.CursorPos = eval(str(self.CursorPos))
