import datetime
import json
import pathlib
import numpy as np
import wx
import wx.lib.agw.floatspin as FS
from wxmplot.plotframe import PlotFrame
from PECTelescope import PECTelescope
from typing import List


class PecTrainer(wx.Frame):
    def __init__(self, parent=None, *args, **kwds):

        self.tel = PECTelescope()
        self.worm_period = 299.1
        self.mount_name = 'unknown'
        self.avg = None

        kwds["style"] = wx.DEFAULT_FRAME_STYLE | wx.RESIZE_BORDER | wx.TAB_TRAVERSAL

        wx.Frame.__init__(self, parent, -1, '',  wx.DefaultPosition, wx.Size(-1, -1), **kwds)
        self.SetTitle("PEC Trainer")

        self.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD, False))

        self.plotframe = None

        framesizer = wx.BoxSizer(wx.VERTICAL)

        self.panel = wx.Panel(self, -1, size=(-1, -1))
        panelsizer = wx.BoxSizer(wx.VERTICAL)
        pad = 10

        panelsizer.Add(wx.StaticText(self.panel, -1, 'PEC Trainer for Celestron'), 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER | wx.LEFT, pad)
        panelsizer.Add(wx.StaticText(self.panel, -1, 'by Frank Freestar8n'), 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER | wx.LEFT, pad)

        self.b_choose = wx.Button(self.panel, -1, 'Choose mount',    size=(-1, -1))
        period_label = wx.StaticText(self.panel, -1, 'Worm Period (s)')
        period_label.SetToolTip('Enter the worm period for the mount')
        self.fs_period = FS.FloatSpin(self.panel, -1, min_val=100, max_val=900, increment=0.1, value=self.worm_period, size=(80, -1))
        self.fs_period.SetFormat("%f")
        self.fs_period.SetDigits(1)
        self.cb_con = wx.CheckBox(self.panel, -1, 'Connect', size=(-1, -1))
        cycles_label = wx.StaticText(self.panel, -1, 'N Cycles')
        cycles_label.SetToolTip('Enter the number of worm cycles to train and average')
        self.c_n_cycles = wx.Choice(self.panel, -1, choices=[str(i + 1) for i in range(10)], size=(-1, -1))
        self.c_n_cycles.SetSelection(5)
        self.cb_index = wx.CheckBox(self.panel, -1, 'Seek Index', size=(-1, -1))
        self.cb_index.Disable()
        self.b_start = wx.Button(self.panel, -1, 'Start Training',    size=(-1, -1))
        self.b_start.Disable()
        self.current_cycle_label = wx.StaticText(self.panel, -1, 'Curr Cycle:')
        self.current_cycle_label.Disable()
        self.c_current_cycle = wx.Choice(self.panel, -1, choices=[str(i + 1) for i in range(10)], size=(-1, -1))
        self.c_current_cycle.SetSelection(0)
        self.c_current_cycle.Disable()
        self.b_cancel = wx.Button(self.panel, -1, 'Stop Training',    size=(-1, -1))
        self.b_cancel.Disable()
        self.b_upload = wx.Button(self.panel, -1, 'Upload',    size=(-1, -1))
        self.b_upload.SetToolTip('Upload the curve to the mount')
        self.b_upload.Disable()
        self.b_download = wx.Button(self.panel, -1, 'Download from mount', size=(-1, -1))
        self.b_download.SetToolTip('Download and view PEC curve from mount')
        self.b_download.Disable()
        self.b_load_file = wx.Button(self.panel, -1, 'Load File',    size=(-1, -1))
        self.b_load_file.SetToolTip('Load curve from file to view with option to upload to mount')
        self.cb_playback = wx.CheckBox(self.panel, -1, 'Playback', size=(-1, -1))
        self.cb_playback.Disable()

        panelsizer.Add(self.b_choose, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER | wx.LEFT, pad)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(period_label, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER | wx.LEFT, pad)
        hbox.AddStretchSpacer(1)
        hbox.Add(self.fs_period, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER | wx.LEFT, pad)
        panelsizer.Add(hbox, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER | wx.LEFT, pad)

        panelsizer.Add(self.cb_con, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER | wx.LEFT, pad)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(cycles_label, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER | wx.LEFT, pad)
        hbox.AddStretchSpacer(1)
        hbox.Add(self.c_n_cycles, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER | wx.LEFT, pad)
        panelsizer.Add(hbox, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER | wx.LEFT, pad)

        panelsizer.Add(self.cb_index, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER | wx.LEFT, pad)
        panelsizer.Add(self.b_start, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER | wx.LEFT, pad)
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        hbox2.Add(self.current_cycle_label, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER | wx.LEFT, pad)
        hbox2.AddStretchSpacer(1)
        hbox2.Add(self.c_current_cycle, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER | wx.LEFT, pad)
        panelsizer.Add(hbox2, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER | wx.LEFT, pad)
        panelsizer.Add(self.b_cancel, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER | wx.LEFT, pad)
        panelsizer.Add(self.b_upload, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER | wx.LEFT, pad)
        panelsizer.Add(self.b_download, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER | wx.LEFT, pad)
        panelsizer.Add(self.b_load_file, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER | wx.LEFT, pad)
        panelsizer.Add(self.cb_playback, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER | wx.LEFT, pad)

        self.panel.SetSizer(panelsizer)
        panelsizer.Fit(self.panel)

        framesizer.Add(self.panel, 0, wx.ALIGN_LEFT | wx.EXPAND, 2)
        self.SetSizer(framesizer)
        framesizer.Fit(self)

        self.b_choose.Bind(wx.EVT_BUTTON, self.choose)
        self.cb_con.Bind(wx.EVT_CHECKBOX, self.connect)
        self.cb_index.Bind(wx.EVT_CHECKBOX, self.find_index)
        self.b_start.Bind(wx.EVT_BUTTON, self.start)
        self.b_cancel.Bind(wx.EVT_BUTTON, self.cancel)
        self.b_upload.Bind(wx.EVT_BUTTON, self.upload)
        self.b_download.Bind(wx.EVT_BUTTON, self.download)
        self.b_load_file.Bind(wx.EVT_BUTTON, self.load_file)
        self.cb_playback.Bind(wx.EVT_CHECKBOX, self.set_playback)

        self.run_number = 0
        self.runs: List[np.array] = []

        self.Bind(wx.EVT_TIMER, self.onTimer)

        self.timer_record = wx.Timer(self)
        self.cycle_time = datetime.datetime.now()

        self.Refresh()

    def choose(self, event: wx.Event):
        if not self.tel.choose():
            wx.MessageBox('Problem launching chooser', 'Error', wx.OK | wx.ICON_ERROR)

    def connect(self, event: wx.Event):
        doit = event.EventObject.Value
        ok = self.tel.connect(doit)
        if doit and not ok:
            wx.MessageBox(f'Unable to connect to {self.tel.scope_name}', 'Error', wx.OK | wx.ICON_ERROR)
            self.cb_con.Value = False
            return
        self.mount_name = self.tel.scope_name
        if doit:
            value, rc = self.tel.index_value()
            if not rc:
                wx.MessageBox('Error getting index status', 'Error', wx.OK | wx.ICON_ERROR)
                return
            if value:
                self.cb_index.Value = True
                self.cb_index.Disable()
                self.b_start.Enable()
            else:
                self.cb_index.Enable()
            self.cb_playback.Enable()
            # we cant query playback status so assume it is off
            self.cb_playback.Value = False
            self.b_download.Enable()
        else:
            self.cb_index.Disable()
            self.b_start.Disable()
            self.b_cancel.Disable()
            self.b_upload.Disable()
            self.b_download.Disable()

    def find_index(self, event: wx.Event):
        value, rc = self.tel.index_value()
        if not rc:
            wx.MessageBox('Error getting index status', 'Error', wx.OK | wx.ICON_ERROR)
            return
        if not value:
            self.tel.mark_ra()
            self.tel.seek_index()
            self.tel.return_ra()
        self.cb_index.Disable()
        self.b_start.Enable()

    def cycle_time_elapsed(self):
        return (datetime.datetime.now() - self.cycle_time).total_seconds()

    def start(self, event: wx.Event):
        # start next record of worm period
        if event:
            # this was initiated by button press so it is the first one
            self.avg = None
            self.runs = []
        if not self.tel.record(True):
            wx.MessageBox('Error starting record', 'Error', wx.OK | wx.ICON_ERROR)
            return
        self.b_start.Disable()
        self.b_cancel.Enable()
        self.c_current_cycle.SetSelection(self.run_number)
        self.current_cycle_label.Enable()
        self.b_upload.Disable()
        self.b_download.Disable()
        self.b_load_file.Disable()
        self.timer_record.Start(1000)
        print('start record')
        self.cycle_time = datetime.datetime.now()

    def cancel(self, event: wx.Event):
        self.timer_record.Stop()
        if not self.tel.record(False):
            wx.MessageBox('Error canceling record', 'Error', wx.OK | wx.ICON_ERROR)
            return
        self.b_cancel.Disable()
        self.current_cycle_label.Disable()
        if self.avg is not None:
            self.b_upload.Enable()
        self.b_start.Enable()
        self.b_download.Enable()

    def make_file_name(self, path: pathlib.Path, stem: str, suffix='json'):
        date = datetime.datetime.now()
        date_str = f'{date.year}{date.month:02d}{date.day:02d}'
        index = 0
        while True:
            fname = f'{stem}_{date_str}_{index:02d}.{suffix}'
            fpath = path / fname
            if not fpath.exists():
                return fpath

    def set_playback(self, event: wx.Event):
        if not self.tel.playback(self.cb_playback.Value):
            wx.MessageBox('Error setting playback', 'Error', wx.OK | wx.ICON_ERROR)

    def upload(self, event: wx.Event):
        if self.avg is None:
            return
        a = np.where(self.avg < 0, 256 + self.avg, self.avg)
        a = np.int32(np.round(a))

        avg_str = ','.join([str(n) for n in a])

        print('final avg string:')
        print(avg_str)
        print()

        print('load data to mount')
        try:
            self.tel.Action('Telescope:PecSetData', avg_str)
        except Exception as e:
            wx.MessageBox(f'Error loading data to mount {e}', 'Error', wx.OK | wx.ICON_ERROR)

        print()
        fpath = self.make_file_name(pathlib.Path.cwd(), 'PEC')
        dic = {
            'runs': self.runs,
            'avg': self.avg,
            'worm_period': self.worm_period,
            'ascom_mount': self.mount_name,
            'record_time': datetime.datetime.now().astimezone()
        }
        with open(fpath, 'w') as f:
            json.dump(dic, f)
        print('saved to file', fpath)
        self.b_start.Enable()

    def get_pec_from_mount(self, raw=False) -> np.array:
        print('getting pec data')
        try:
            run_str = self.tel.Action('Telescope:PecGetData', '')
        except Exception as e:
            wx.MessageBox(f'Error getting PEC data from mount {e}', 'Error', wx.OK | wx.ICON_ERROR)
            return None
        print('run string is:')
        print(run_str)
        print()
        # convert to signed integer
        run = np.array([int(s) for s in run_str.split(',')])
        run = np.where(run > 128, run - 256, run)
        print('raw signed values:')
        s = [str(int(p)) for p in run]
        print(' '.join(s))
        if raw:
            return run
        # remove drift
        run = run - np.sum(run) / len(run)
        run = np.where(run > 128, 128, run)
        run = np.where(run < -127, -127, run)
        # run is now signed rate relative to sidereal in units of sidereal/1024
        return run

    def get_pec_data(self) -> None:
        run = self.get_pec_from_mount()
        if not run:
            return
        self.runs.append(run)
        self.avg = np.mean(self.runs, axis=0)
        self.avg = self.avg - np.sum(self.avg) / len(self.avg)

    def load_file(self, event: wx.Event) -> None:
        fd = wx.FileDialog(self.panel, 'Load PEC file', '', '', 'PEC Files (PEC*.json)|PEC*.json', wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        fd.ShowModal()
        fpath = fd.GetPath()
        fd.Destroy()
        if not fpath:
            return
        with open(fpath, 'r') as f:
            dic = json.load(f)

        self.avg = dic['avg']
        self.runs = dic['runs']
        self.worm_period = dic['worm_period']
        self.plot_cycles(False)

    def download(self, event: wx.Event) -> None:
        self.avg = self.get_pec_from_mount(True)
        self.runs = []
        self.plot_cycles(False)

    def ShowPlotFrame(self, do_raise=True, clear=True):
        "make sure plot frame is enabled and visible"
        if self.plotframe is None:
            print('create plotframe')
            self.plotframe = PlotFrame(self.panel)

        if do_raise:
            self.plotframe.Raise()
        if clear:
            self.plotframe.panel.clear()
            self.plotframe.reset_config()

        try:
            self.plotframe.Show()
        except RuntimeError:
            print('recreate plotframe')
            self.plotframe = PlotFrame(self.panel)
            self.plotframe.Show()

    def onTimer(self, event: wx.Event):
        if not self.tel.record_done():
            self.plot_cycles()
            return
        print('record done')
        self.timer_record.Stop()
        self.get_pec_data()
        self.run_number += 1
        if self.run_number >= self.c_n_cycles.GetCurrentSelection() + 1:
            # we are done training
            self.b_cancel.Disable()
            self.current_cycle_label.Disable()
            self.b_upload.Enable()
            self.b_download.Enable()
            self.b_load_file.Enable()
            self.plot_cycles(False)
            return
        # start next cycle
        self.start(None)

    def plot_cycles(self, live=True):
        elapsed = self.cycle_time_elapsed() if live else 0
        self.ShowPlotFrame(False, False)
        self.worm_period = self.fs_period.GetValue()
        if live and not self.runs:
            self.plotframe.plot([elapsed], [0], xmin=0, xmax=self.worm_period, ymin=-5, ymax=5, marker='o')
            self.ShowPlotFrame(True, False)
            return
        self.plotframe.plot([elapsed], [0], xmin=0, xmax=self.worm_period)
        x = []
        if self.runs:
            x = np.arange(len(self.runs[0])) / len(self.runs[0]) * self.worm_period
        elif self.avg is not None:
            x = np.arange(len(self.avg)) / len(self.avg) * self.worm_period
        else:
            print('no data to plot')
            return
        colors = ['brown', 'pink', 'gray', 'olive', 'cyan', 'seagreen', 'cornflowerblue', 'coral', 'gold']
        for i, r in enumerate(self.runs):
            self.plotframe.oplot(x, self.runs[i] * 15 / 1024, color=colors[i % len(colors)], alpha=0.7)
        if self.avg is not None:
            self.plotframe.oplot(x, self.avg * 15 / 1024, color='black', linewidth=2)
        self.plotframe.set_xlabel('cycle time (s)')
        self.plotframe.set_ylabel('PEC Correction (arc-sec/s)')
        self.ShowPlotFrame(True, False)

    def OnExit(self, event):
        try:
            if self.plotframe is not None:
                self.plotframe.onExit()
        except:  # noqa E722
            pass
        self.Destroy()


if __name__ == '__main__':
    app = wx.App()
    f = PecTrainer(None, -1)
    f.Show(True)
    app.MainLoop()
