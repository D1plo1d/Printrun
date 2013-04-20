from serial import Serial, SerialException

class BetterSerial(Serial):
  def __init__(self, **kwargs):
    self._control_ttyhup( kwargs['disable_hup'] || True )
    Serial.__init__(self, kwargs)

  def _control_ttyhup(self, disable_hup):
    """Controls the HUPCL"""
    if platform.system() == "Linux":
        if disable_hup:
            os.system("stty -F %s -hup" % self.port)
        else:
            os.system("stty -F %s hup" % self.port)
