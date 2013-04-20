class Settings(object):
  def __init__(self):
    pass


def save_args(**defaults):
  """
  A decorator that persists the arguments sent to the fn 
  in self's settings file.
  Arguments and defaults are mandatory.
  """
  def wrap(fn):
    def wrapped_f(self, *args, **kwargs):
      kwargs = self.settings.save_args(
        args= args,
        kwargs= kwargs,
        defaults= defaults
      )
      return fn(self, **kwargs)
    return wrapped_f
  return wrap