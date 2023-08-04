
class DEFAULT:
    def OnType(self, char):
        """
        Is called every time the user types a character, and gives the "char" as an argument.

        :param char:
        :return:
        """
        ...

    def OnHover(self, WordHovered):
        """
        WARNING - CALLED EVERY DISPLAY TICK
        Is called when the user is typing a word and a pop-up appears to suggest a word.


        :param WordHovered Popup:
        :return:
        """
        ...

    def OnLeftClick(self, pos):
        """
        Is called every time the user clicks on something, The click co-ords are given as args. (x, y)

        :param pos:
        :return:
        """
        ...

    def OnStart(self):
        """
        Called On PyTri Start when plugin is Initialized.

        :return:
        """
        ...

    def OnClose(self):
        """
        Called On PyTri Shutdown. Only if it is "safely" shutdown.

        :return:
        """
        ...

    def OnRun(self):
        """
        Is called every time the user runs the code before it is executed

        :return:
        """
        ...

    def OnFinish(self, ExitCode, Error=None):
        """
        Is called when code execution has finished. The exitCode / error is given as an argument.

        :param ExitCode:
        :return:
        """
        ...

    def OnSave(self, path):
        """
        Is called when code in saved. the path is given as an argument.

        :param path:
        :return:
        """
        ...

    def Tick(self):
        """
        Called Every tick / screen update.

        :return:
        """
        ...

