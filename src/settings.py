class Settings(object):
  def __init__(self):
    self.setting_store = {}
  def update_setting(self, name, val):
    if val or not self.setting_store.has_key(name):
      self.setting_store[name] = val
      return val
    else:
      return self.setting_store[name]  


def save_args(**defaults):
  """
  A decorator that persists the arguments sent to the fn 
  in self's settings file.
  Arguments and defaults are mandatory. 

  Example
  =======

  @save_args(port=None, baud=None)
  def connect(self, port, baud):
    ...
  """
  arg_names = defaults.keys()
  def wrap(fn):
    def wrapped_f(self, *args, **kwargs):
      # Key word arguments are easy. We find the names not filled by them...
      unused_arg_names = [name for name in arg_names if name not in kwargs.keys() ]
      # And try to fill those, going through possible names and assigning args.
      args = list(args)
      args.reverse()
      for name in unused_arg_names[:]:
        if args:
          unused_arg_names.remove(name)
          kwargs[name] = args.pop()
        else:
          break
      # If we don't use up all the arguments, we error.
      if args:
        str_args = {"name": fn.__name__, "arg_num" : len(defaults), "arg_given" : len(args) + len(kwargs)}
        raise TypeError("%(name)s() takes at most %(arg_num)s arguments (%(arg_given)s given)" % str_args)
      # Finally, we fill in the other values as defaults.
      dkwargs = defaults.copy()
      dkwargs.update(kwargs)
      for name in dkwargs:
        dkwargs[name] = self.settings.update_setting(name, dkwargs[name])
      return fn(self, **dkwargs)
    return wrapped_f
  return wrap
