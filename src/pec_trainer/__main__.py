import wx

from pec_trainer.pec_trainer_main import PECTrainer


def main():
    app = wx.App()
    trainer = PECTrainer(None, -1)
    trainer.Show(True)
    app.MainLoop()


if __name__ == '__main__':
    main()
