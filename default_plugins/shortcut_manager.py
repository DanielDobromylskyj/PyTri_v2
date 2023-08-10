if __name__ == "__main__":
    from default_plugin import DEFAULT
else:
    from default_plugins.default_plugin import DEFAULT

class Plugin(DEFAULT):
    def __init__(self, parent):
        self.PyTri = parent

    def OnType(self, key):
        if (key == "s") and (self.PyTri.CtrlPressed == True):
            self.PyTri.Save(self.PyTri.Path)
            return True

        if (key == "r") and (self.PyTri.CtrlPressed == True):
            self.PyTri.Run()
            return True

        if key == "f5":
            self.PyTri.Run()
            return True
