import datetime
import json
import pathlib
import numpy as np
from typing import List

import wx
from wxmplot.plotframe import PlotFrame

from pec_trainer.pec_telescope import PECTelescope


class PECTrainer(wx.Frame):
    def __init__(self, parent=None, *args, **kwds) -> None:

        self.tel = PECTelescope()
        self.worm_period = 500
        self.n_bins = 88
        self.mount_name = 'unknown'
        self.avg = None
        self.pec_bins = set()

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

        self.cb_con = wx.CheckBox(self.panel, -1, 'Connect', size=(-1, -1))
        self.cb_con.Disable()
        cycles_label = wx.StaticText(self.panel, -1, 'N Cycles')
        cycles_label.SetToolTip('Enter the number of worm cycles to train and average')
        self.c_n_cycles = wx.Choice(self.panel, -1, choices=[str(i + 1) for i in range(10)], size=(-1, -1))
        self.c_n_cycles.SetSelection(5)
        self.cb_index = wx.CheckBox(self.panel, -1, 'Seek index', size=(-1, -1))
        self.cb_index.SetToolTip('Move the mount in RA to seek the PEC index and return (guiding should be disabled)')
        self.cb_index.Disable()
        self.b_start = wx.Button(self.panel, -1, 'Start training',    size=(-1, -1))
        self.b_start.SetToolTip('Begin the set of training cycles with guiding enabled')
        self.b_start.Disable()
        self.current_cycle_label = wx.StaticText(self.panel, -1, 'Current cycle')
        self.current_cycle_label.Disable()
        self.c_current_cycle = wx.Choice(self.panel, -1, choices=[str(i + 1) for i in range(10)], size=(-1, -1))
        self.c_current_cycle.SetSelection(0)
        self.c_current_cycle.Disable()
        self.g_progress = wx.Gauge(self.panel, -1, size=(200, -1))
        self.g_progress.SetRange(self.n_bins)
        self.g_progress.SetValue(0)
        self.g_progress.Disable()
        self.b_cancel = wx.Button(self.panel, -1, 'Stop training',    size=(-1, -1))
        self.b_cancel.Disable()
        self.b_upload = wx.Button(self.panel, -1, 'Upload to mount',    size=(-1, -1))
        self.b_upload.SetToolTip('Upload the curve to the mount')
        self.b_upload.Disable()
        self.b_download = wx.Button(self.panel, -1, 'Download from mount', size=(-1, -1))
        self.b_download.SetToolTip('Download and view PEC curve from mount')
        self.b_download.Disable()
        self.b_load_file = wx.Button(self.panel, -1, 'Load and view file',    size=(-1, -1))
        self.b_load_file.SetToolTip('Load curve from file to view with option to upload to mount')
        self.cb_rate = wx.CheckBox(self.panel, -1, 'Plot PE as rate', size=(-1, -1))
        self.cb_rate.SetValue(False)
        self.cb_rate.Enable()
        self.cb_rate.SetToolTip('Show PE as rate instead of arc-sec curve')
        self.b_playback = wx.Button(self.panel, -1, 'Enable mount PEC playback', size=(-1, -1))
        self.b_playback.Disable()

        panelsizer.Add(self.b_choose, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER | wx.LEFT, pad)
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

        panelsizer.Add(self.g_progress, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER | wx.LEFT, pad)
        panelsizer.Add(self.b_cancel, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER | wx.LEFT, pad)
        panelsizer.Add(self.b_upload, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER | wx.LEFT, pad)
        panelsizer.Add(self.b_download, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER | wx.LEFT, pad)
        panelsizer.Add(self.b_load_file, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER | wx.LEFT, pad)
        panelsizer.Add(self.cb_rate, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER | wx.LEFT, pad)
        panelsizer.Add(self.b_playback, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER | wx.LEFT, pad)

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
        self.cb_rate.Bind(wx.EVT_CHECKBOX, self.rate)
        self.b_playback.Bind(wx.EVT_CHECKBOX, self.set_playback)

        self.run_number = 0
        self.runs: List[np.array] = []

        self.Bind(wx.EVT_TIMER, self.onTimer)

        self.timer_record = wx.Timer(self)
        self.cycle_time = datetime.datetime.now()
        self.file_name = None

        self.Refresh()

    def choose(self, event: wx.Event) -> None:
        if not self.tel.choose():
            wx.MessageBox('Problem launching chooser', 'Error', wx.OK | wx.ICON_ERROR)
        self.cb_con.Enable()

    def connect(self, event: wx.Event) -> None:
        doit = event.EventObject.Value
        ok = self.tel.connect(doit)
        if doit and not ok:
            wx.MessageBox(f'Unable to connect to {self.tel.scope_name}', 'Error', wx.OK | wx.ICON_ERROR)
            self.cb_con.Value = False
            return
        self.mount_name = self.tel.scope_name
        if doit:
            self.tel.record(False)
            value, rc = self.tel.index_found()
            if not rc:
                wx.MessageBox('Error getting index status\nMake sure the mount supports PEC', 'Error', wx.OK | wx.ICON_ERROR)
                return
            if value:
                self.cb_index.Value = True
                self.cb_index.Disable()
                self.b_start.Enable()
            else:
                self.cb_index.Enable()
            self.b_playback.Enable()
            self.b_download.Enable()
            self.b_load_file.Enable()
        else:
            self.cb_index.Disable()
            self.b_start.Disable()
            self.b_cancel.Disable()
            self.b_upload.Disable()
            self.b_download.Disable()

    def find_index(self, event: wx.Event) -> None:
        print('find index')
        value, rc = self.tel.index_found()
        print('index found is', value)
        if not rc:
            wx.MessageBox('Error getting index status', 'Error', wx.OK | wx.ICON_ERROR)
            return
        if not value:
            self.tel.mark_ra()
            self.tel.seek_index()
            self.tel.return_ra()
        self.cb_index.Disable()
        self.b_start.Enable()

    def cycle_time_elapsed(self) -> float:
        return (datetime.datetime.now() - self.cycle_time).total_seconds()

    def start(self, event: wx.Event) -> None:
        "Start recording next worm cycle."
        if event:
            # this was initiated by button press so it is the first one, so clear any old info
            self.avg = None
            self.runs = []
            self.run_number = 0
            self.file_name = self.make_file_name(pathlib.Path.cwd(), 'PEC')
            self.tel.record(False)
            self.prev_index = -1
            self.g_progress.Enable()

        self.g_progress.SetValue(0)
        self.pec_bins = set()
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
        self.b_playback.Disable()
        self.timer_record.Start(1000)
        print(f'start recording cycle {self.run_number + 1}')
        self.cycle_time = datetime.datetime.now()

    def cancel(self, event: wx.Event) -> None:
        self.timer_record.Stop()
        if not self.tel.record(False):
            wx.MessageBox('Error canceling record', 'Error', wx.OK | wx.ICON_ERROR)
            return
        self.b_cancel.Disable()
        self.current_cycle_label.Disable()
        self.g_progress.SetValue(0)
        self.g_progress.Disable()
        if self.avg is not None:
            self.b_upload.Enable()
        self.b_start.Enable()
        self.b_download.Enable()
        self.b_load_file.Enable()

    def make_file_name(self, path: pathlib.Path, stem: str, suffix='json') -> pathlib.Path:
        "Find the next filename for this date."
        date = datetime.datetime.now()
        date_str = f'{date.year}{date.month:02d}{date.day:02d}'
        index = 0
        while True:
            fname = f'{stem}_{date_str}_{index:02d}.{suffix}'
            fpath = path / fname
            if not fpath.exists():
                return fpath
            index += 1

    def set_playback(self, event: wx.Event) -> None:
        if not self.tel.playback(True):
            wx.MessageBox('Error enabling playback', 'Error', wx.OK | wx.ICON_ERROR)

    def upload(self, event: wx.Event) -> None:
        if self.avg is None:
            return

        a = np.where(self.avg < 0, 256 + self.avg, self.avg)
        a = np.int32(np.round(a))

        avg_str = ','.join([str(n) for n in a])

        print('load data to mount')
        try:
            self.tel.Action('Telescope:PecSetData', avg_str)
            wx.MessageBox('Uploaded average PE curve to the mount', '', wx.OK)
        except Exception as e:
            wx.MessageBox(f'Error loading PE curve to the mount {e}', 'Error', wx.OK | wx.ICON_ERROR)
        print()
        self.b_start.Enable()

    def get_pec_from_mount(self, raw=False) -> np.array:
        print('getting pec data')
        try:
            run_str = self.tel.Action('Telescope:PecGetData', '')
        except Exception as e:
            wx.MessageBox(f'Error getting PEC data from mount {e}', 'Error', wx.OK | wx.ICON_ERROR)
            return None

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

        # clip
        run = np.where(run > 128, 128, run)
        run = np.where(run < -127, -127, run)

        # run is now signed rate relative to sidereal in units of sidereal/1024
        return run

    def get_pec_data(self) -> None:
        run = self.get_pec_from_mount()
        if run is None:
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
        self.plot_cycles()

    def download(self, event: wx.Event) -> None:
        self.avg = self.get_pec_from_mount(True)
        self.runs = []
        self.plot_cycles()

    def ShowPlotFrame(self, do_raise=True, clear=True) -> None:
        "make sure plot frame is enabled and visible"
        if self.plotframe is None:
            self.plotframe = PlotFrame(self.panel, title='PEC Training Curves')

        if clear:
            self.plotframe.panel.clear()
        if do_raise:
            self.plotframe.Raise()

        try:
            self.plotframe.Show()
        except RuntimeError:
            print('recreate plotframe')
            self.plotframe = PlotFrame(self.panel)
            self.plotframe.Show()

    def save_to_file(self) -> None:
        clean_runs = [r.tolist() for r in self.runs]
        dic = {
            'runs': clean_runs,
            'avg': self.avg.tolist(),
            'worm_period': self.worm_period,
            'ascom_mount': self.mount_name,
            'record_time': datetime.datetime.now().astimezone()
        }
        with open(self.file_name, 'w') as f:
            json.dump(dic, f, indent=4, sort_keys=True, default=str)
        print('saved to file', self.file_name)

    def onTimer(self, event: wx.Event) -> None:
        if not self.tel.record_done():
            self.pec_bins.add(self.tel.index_value())
            self.g_progress.SetValue(len(self.pec_bins))
            return
        print(f'cycle {self.run_number + 1} complete')
        self.g_progress.SetValue(0)
        # set the worm period based on measured time for each cycle
        self.worm_period = self.cycle_time_elapsed()
        self.timer_record.Stop()
        self.get_pec_data()
        # save and overwrite the file after each worm period, saving all runs each time
        self.save_to_file()
        self.run_number += 1
        self.plot_cycles()
        if self.run_number > self.c_n_cycles.GetCurrentSelection():
            # we are done training
            self.b_cancel.Disable()
            self.current_cycle_label.Disable()
            self.b_upload.Enable()
            self.b_download.Enable()
            self.b_load_file.Enable()
            self.b_playback.Enable()
            self.g_progress.Disable()
            self.upload(None)
            return
        # start next cycle
        self.start(None)

    def rate(self, event: wx.Event) -> None:
        self.plot_cycles()

    def pe(self, bins) -> np.array:
        bins = np.array(bins) * 15 / 1024
        if self.cb_rate.Value:
            return bins
        bins *= self.worm_period / self.n_bins
        return np.cumsum(bins)

    def plot_cycles(self, live=False) -> None:
        x = []
        if self.runs:
            x = np.arange(len(self.runs[0])) / len(self.runs[0]) * self.worm_period
        elif self.avg is not None:
            x = np.arange(len(self.avg)) / len(self.avg) * self.worm_period
        else:
            print('no data to plot')
            return
        self.ShowPlotFrame(False, True)
        colors = [u'#1f77b4', u'#ff7f0e', u'#2ca02c', u'#d62728', u'#9467bd', u'#8c564b', u'#e377c2', u'#7f7f7f', u'#bcbd22', u'#17becf']
        xlab = 'Cycle Time (s)'
        ylab = 'PEC Correction Rate (arc-sec/s)' if self.cb_rate.Value else 'PEC (arc-sec)'
        plotted = False
        for i, r in enumerate(self.runs):
            plotted = True
            if i == 0:
                self.plotframe.plot(
                    x, self.pe(self.runs[i]), color=colors[i % len(colors)], alpha=0.9, xmin=0, xmax=self.worm_period, xlabel=xlab, ylabel=ylab, linewidth=2, markersize=0   # noqa E501
                )
            else:
                self.plotframe.oplot(
                    x, self.pe(self.runs[i]), color=colors[i % len(colors)], alpha=0.9, linewidth=2, markersize=0
                )
        if self.avg is not None:
            if plotted:
                if len(self.runs) > 1:
                    self.plotframe.oplot(x, self.pe(self.avg), color='black', linewidth=2, markersize=0)
            else:
                self.plotframe.plot(x, self.pe(self.avg), color='black', xmin=0, xmax=self.worm_period, xlabel=xlab, ylabel=ylab, linewidth=2, markersize=0)   # noqa E501
        self.ShowPlotFrame(True, False)

    def OnExit(self, event) -> None:
        try:
            if self.plotframe is not None:
                self.plotframe.onExit()
        except:  # noqa E722
            pass
        self.Destroy()


if __name__ == '__main__':
    app = wx.App()
    trainer = PECTrainer(None, -1)
    trainer.Show(True)
    app.MainLoop()
