import time
import win32com.client
from typing import List, Protocol, Tuple


class ASCOMRate:
    Minimum: float
    Maximum: float


class MountASCOMInterface(Protocol):
    Connected: bool
    Tracking: bool
    Slewing: bool
    RightAscension: float
    Declination: float
    CanPark: bool
    CanUnPark: bool
    SideOfPier: int
    GuideRateRightAscension: float
    GuideRateDeclination: float
    Azimuth: float
    Altitude: float
    CanSync: bool

    def Park():
        pass

    def Unpark():
        pass

    def DestinationSideOfPier(ra: float, dec: float) -> int:
        return 0

    def CommandString(cmd: str, doit: bool) -> str:
        return ''

    def MoveAxis(ax: int, rate: float):
        pass

    def AxisRates(ax: int) -> List[ASCOMRate]:
        rate = ASCOMRate(Minimum=0, Maximum=1)
        return [rate]

    def Action(cmd: str, msg: str):
        pass

    def PulseGuide(dir: int, duration: int):
        pass

    def SyncToCoordinates(ra: float, dec: float):
        pass

    def SlewToCoordinates(ra: float, dec: float):
        pass

    def CanMoveAxis(ax: int) -> bool:
        return True


class PECTelescope:
    def __init__(self) -> None:
        self.tel: MountASCOMInterface = None
        self.ref_ra = 0

    def choose(self) -> bool:
        try:
            chooser = win32com.client.Dispatch('ASCOM.Utilities.Chooser')
        except Exception as e:
            print('error creating chooser', e)
            return False
        try:
            chooser.DeviceType = 'Telescope'
            self.scope_name = chooser.Choose(None)
            print(f'chosen scope is {self.scope_name}')
        except Exception as e:
            print('error launching chooser', e)
            return False
        return True

    def connect(self, on: bool) -> bool:
        if self.tel:
            try:
                if self.tel.Connected != on:
                    self.tel.Connected = on
                    print('connected now', on)
                    return True
            except Exception as e:
                print('error setting connect value for existing telescope', e)
                return False

        try:
            self.tel: MountASCOMInterface = win32com.client.Dispatch(self.scope_name)
            if self.tel.Connected != on:
                self.tel.Connected = on
                print('connected status now', on)
        except Exception as e:
            print('could not set connect state for telescope', e)
            return False
        print('connected status now', on)
        time.sleep(1)
        return True

    def record(self, on: bool) -> bool:
        try:
            if on:
                cmdstr = 'P\x01\x10\x0c\x00\x00\x00\x00'
                s = self.tel.CommandString(cmdstr, False)
                if s[0] != '#':
                    print('problem setting pec record', s)
                    return False
                return True
            else:
                cmdstr = 'P\x01\x10\x16\x00\x00\x00\x00'
                s = self.tel.CommandString(cmdstr, False)
                if s[0] != '#':
                    print('problem unsetting pec record', s)
                    return False
        except Exception as e:
            print('exception with pec record', e)
            return False
        return True

    def record_done(self) -> bool:
        cmdstr = 'P\x01\x10\x15\x00\x00\x00\x01'
        try:
            s = self.tel.CommandString(cmdstr, False)
            if s[0] == '\0':
                return False
            return True
        except Exception as e:
            print('exception in record_done', e)
            return False

    def seek_index(self) -> bool:
        cmdstr = 'P\x01\x10\x19\x00\x00\x00\x00'
        try:
            _ = self.tel.CommandString(cmdstr, False)
        except Exception as e:
            print('exception in seek index', e)
            return False
        return True

    def index_value(self) -> Tuple[bool, bool]:
        # returns index value and success
        cmdstr = 'P\x01\x10\x18\x00\x00\x00\x01'
        try:
            s = self.tel.CommandString(cmdstr, False)
            if s[0] == '\0':
                return False, True
            return True, True
        except Exception as e:
            print('exception in index value', e)
            return False, False

    def set_index(self) -> None:
        if self.index_value():
            print('already have index')
            return
        print('seeking index')
        self.seek_index()
        # this could go forever
        while not self.index_value():
            print('wait for index')
            time.sleep(1)
        print('have index')

    def playback(self, on: bool) -> bool:
        if on:
            cmdstr = 'P\x02\x10\x0d\x01\x00\x00\x00'
        else:
            cmdstr = 'P\x02\x10\x0d\x00\x00\x00\x00'
        try:
            s = self.tel.CommandString(cmdstr, False)
            if s[0] != '#':
                print('problem setting playback', s)
                return False
        except Exception as e:
            print('exception in playback', e)
            return False
        return True

    def get_version(self) -> str:
        cmdstr = 'P\x01\x10\xfe\x00\x00\x00\x02'
        try:
            s = self.tel.CommandString(cmdstr, False)
            return s
        except Exception as e:
            print('version exception', e)
            return 'Error'

    def Action(self, cmdstr, data) -> str:
        rc = self.tel.Action(cmdstr, data)
        return rc

    def mark_ra(self) -> None:
        self.ref_ra = self.tel.RightAscension
        print(f'reference RA is {self.ref_ra}')

    def return_ra(self) -> None:
        # query rates to make sure ascom driver is happy
        _ = self.tel.AxisRates()
        ra = self.tel.RightAscension
        deg = (self.ref_ra - ra) * 15
        deg = deg - 360 if deg >= 180 else deg
        deg = deg + 360 if deg < -180 else deg
        if abs(deg) > 5:
            print(f'Problem returning ra from index: shift is {deg}')
            return
        rate = 0.2
        t = abs(deg) / rate
        rate = rate if deg > 0 else -rate
        print(f'moving ra from {ra:.4f} to {self.ref_ra:.4f} for {t:.1f} seconds')
        self.tel.MoveAxis(0, rate)
        time.sleep(t)
        self.tel.MoveAxis(0, 0)
