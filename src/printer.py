from threading import Thread
import re
from better_serial import BetterSerial
from event_emitter import EventEmitter
from print_job_queue import PrintJobQueue
from settings import Settings, save_args

class Printer(EventEmitter):

  def __init__(self):
    super(PrintCore, self)
    self.jobs = PrintJobQueue()
    self.settings = Settings()
    self.serial = None
    self._ready = False
    self._disconnect = False
    self._greetings = ('start','Grbl ', 'ok')
    self.sensor_names = {'t': 'extruder', 'b': 'bed'}
    self.sensors = {}
    self._resend = None
    self.verbose = False

  @save_args(port=None, baud=None)
  def connect(self, port, baud):
    if port == None or baud == None: return
    # disconnect if there is an open serial connection
    if self.is_connected(): self.disconnect()
    # connect
    self.serial = BetterSerial(
      port = port,
      baudrate = baud,
      timeout = 0.25
    )
    self.read_thread = Thread(target = self._run)
    self.read_thread.start()
    self.fire("connected")

  def disconnect(self):
    if self.is_connected():
      if self.read_thread and threading.currentThread() != self.read_thread:
        self._disconnect = True
        self.read_thread.join()
        self._disconnect = False
      self.printer.close()
    self._ready = False
    self.printer = None
    self.fire("disconnected")

  def is_connected(self):
    """
    Returns true if the printer has connected via serial.
    """
    return self.serial != None

  def is_ready(self):
    """
    Returns true if the printer is connected AND is ready receive gcodes.
    """
    return self._ready

  def reset(self):
    if not self.is_connected(): return
    self.serial.setDTR(1)
    time.sleep(0.2)
    self.serial.setDTR(0)
    self._resend = None

  def start(self, lines):
    pass

  def pause(self):
    pass

  def send_now(self):
    pass

  def _run(self):
    """
    This function listens for and acts on messages from the firmware
    """

    msg_routes = {
      'ok': ('ok')
      'error': ('error', '!!')
      'resend': ('resend', 'rs')
    }

    while(not self._disconnect and self.serial and self.serial.isOpen())
      line = self._readline()
      try:
        line = self.serial.readline().lower().strip()
      except:
        # connection problem
        # workaround cases where M105 was sent before printer Serial
        # was online an empty line means read timeout was reached,
        # meaning no data was received.
        if not self._ready:
          self._send("M105")
          sleep(0.25)
          continue()
        # Actual serial disconnect, crash and burn baby.
        print "Can't read from printer (disconnected?)."
        self.disconnect()
        break

      fire("line_received", line)
      if self.verbose: print "RECV: ", line.rstrip()

      if line.startswith('debug_'): continue
      if line.startswith('echo:'): continue

      if not self._ready: self._check_for_header(line)
      else: parse_line(line)

  def _check_for_header(self, line):
    if line.startswith(self._greetings):
      # header messages seem to conform to no standard whatsoever
      # and some firmwares (MARLIN) do not like it if we start sending commands 
      # before they are done so we just wait 1 second for them to go away.
      sleep(1)
      self._ready = True
      self.fire("ready")
    else:
      self._send("M105")
      sleep(0.25)


  def parse_line(self, line):
    words = line.split()
    cmd, words = words[0], words[1:]
    for name, prefixes in msg_routes.itter_items():
      if not cmd in prefixes: continue
      getattr(self, "_parse_%s_line"%name)(words, line)

  def _parse_ok_line(self, words, line):
    if "echo:" in words: words = words[0..words.index("echo:")]

    sensor_strs = filter(lambda s: s.find(":") > 0, words)
    for s in sensor_strs:
      k, val = s.split(":")
      if not k in sensor_names: continue
      name = sensor_names[k]
      self.sensors[name] = val
      self.fire("sensor_changed", {'name': sensor_names[k], 'value': val})

  def _parse_error_line(self, words, line):
    self.fire("error", words.join(" "))

  def _parse_resend_line(self, words, line):
    # Teststrings for resend parsing       # Firmware     exp. result
    # line="rs N2 Expected checksum 67"    # Teacup       2
    try:
      self._resend = int( re.search('N:?\s?([0-9]+)', line).group(1) )
    except:
      pass


