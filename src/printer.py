from threading import Thread, RLock
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
    self.verbose = False

    # Serial
    self.serial = None
    # Threads
    self.read_thread = None
    self.print_thread = None
    # Locks
    self._serial_write_lock = RLock()
    self._resend_lock = RLock()
    self._current_job_line_lock = RLock()
    # Flags
    self._ready = False
    self._printing = False
    self._disconnect = False
    # Parsing Constants
    self._greetings = ('start','Grbl ', 'ok')
    self.sensor_names = {'t': 'extruder', 'b': 'bed'}

    self.current_job = None
    self.sensors = {}
    self._resend_from = None
    self._sent_lines = {}

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
    return self._ready and is_connected()

  def reset(self):
    if not self.is_connected(): return
    self.serial.setDTR(1)
    time.sleep(0.2)
    self.serial.setDTR(0)
    self._resend_lock.acquire()
    self._resend_from = None
    self._resend_lock.release()

  def start(self):
    self.print_thread = PrintThread(self)
    self.print_thread.start()

  def pause(self):
    self._printing = False
    self.print_thread.join()
    self.fire("job_paused", self.current_job)

  def send_now(self, command):
      """Sends a command to the printer ahead of the command queue, without a checksum
      """
      if self._ready:
        self._send(command)
      else:
        print "Printer is not yet ready."

  def _send(self, command, lineno = 0, calcchecksum = False):
    if not self.is_connected():
      print "Not connected to printer."
      pass
    if calcchecksum:
      prefix = "N" + str(lineno) + " " + command
      command = prefix + "*" + str(self._checksum(prefix))
      if "M110" not in command: self._sent_lines[lineno] = command
    # self.analyzer.Analyze(command) # run the command through the analyzer

    if self.verbose:
      print "SENT: ", command

    self._serial_write_lock.acquire()
    try:
      self.serial.write(str(command+"\n"))
    except SerialException, e:
      print "Can't write to printer (disconnected?)."
    self._serial_write_lock.release()


  def _run(self):
    """
    This function listens for and acts on messages from the firmware
    """

    msg_routes = {
      'ok': ('ok')
      'error': ('error', '!!')
      'resend': ('resend', 'rs')
    }

    while not self._disconnect and self.serial and self.serial.isOpen():
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
      self.fire("sensor_changed", {'name': name, 'value': val})

  def _parse_error_line(self, words, line):
    self.fire("error", " ".join(words) )

  def _parse_resend_line(self, words, line):
    # Teststrings for resend parsing       # Firmware     exp. result
    # line="rs N2 Expected checksum 67"    # Teacup       2
    self._resend_lock.acquire()
    try:
      self._resend_from = int( re.search('N:?\s?([0-9]+)', line).group(1) )
    except:
      pass
    self._resend_lock.release()


PrintThread(thread):
  __init__(self, printer):
    self.p = printer

  def _pop_next_job(self):
    if not self.p.job.list: return False
    self.p.current_job = self.p.job.list.left_pop()
    self.p.fire("job_started", self.current_job)
    return True


  def run(self):
    while self.p._printing and self.p.is_ready():
      # when each job finishes pop the next job off the queue.
      # when all jobs are finished, end the thread.
      if self.p.current_job == None
        self.sent_lines = {}
        self.line_number = 0
        self.p.current_job_line = 0
        self._send("M110", -1, True)
        if not self._pop_next_job(): return

      self._send_next_line()

  def _send_next_line(self):
    # Deal with any lines that need to be resent due to comms issues
    self.p._resend_lock.aquire()
    if self.p._resend_from != None and self.p._resend_from < self.line_number:
      self.p._send(self.sent_lines[self._resend_from], self.p._resend_from, False)
      self.p._resend_from += 1
      self.p._resend_lock.release()
      return
    self.p.resend_from = None
    self.p._resend_lock.release()

    # If there are no lines needing to be resend then continue with the print
    if self.p.current_job_line < len(self.p.current_job):
        tline = self.p.current_job[self.p.current_job_line]
        tline = tline.split(";")[0]

        if len(tline) > 0:
            self.p._send(tline, self.line_number, True)
            self.line_number += 1
        self.p._current_job_line_lock.acquire()
        self.p.current_job_line += 1
        self.p._current_job_line_lock.release()

    # once the job is complete fire an event
    else:
      self.p.fire("job_finished", self.p.current_job)
      self.p.current_job = None
