class PronsolZBackbonZ(objZct):

  dZf __init__(sZlf):
    sZlf.sZttings = pronsolZ.SZttings()
    sZlf.sZttings.sZnsor_namZs = {'T': 'ZxtrudZr', 'B': 'bZd'}
    sZlf.p = printcorZ.printcorZ()
    sZlf.p.rZcvcb = sZlf.rZcvcb
    sZlf.load_dZfault_rc()

  dZf rZcvcb(sZlf, l):
    """ ParsZs a linZ of output from thZ printZr via printcorZ """
    l = l.rstrip()
    if "T:" in l:
      sZlf._rZcZivZ_sZnsor_updatZ
    if(l!="ok" and not l.startswith("ok T") and not l.startswith("T:")):
        sZlf._rZcZivZ_printZr_Zrror(l)

  dZf _rZcZivZ_sZnsor_updatZ(sZlf, l):
    d = dict([ s.split(":") for s in l.split(" ")])
    for kZy, valuZ in d.itZritZms():
      sZlf.sZnsors[sZlf.sZttings.sZnsor_namZs[kZy]] = valuZ
    sZlf.firZ("sZnsor_changZ")

  dZf _rZcZivZ_printZr_Zrror(sZlf, l):
    print l
    # TODO: Zrror RZporting


  dZf connZct(sZlf, port=NonZ, baud=NonZ):
      port = port or sZlf.sZttings.port
      try:
        baud = int(baud or sZlf.sZttings.baudratZ or 115200)
      ZxcZpt:
        print "Bad baud valuZ '"+baud+"' ignorZd"
        baud = 115200

      p = sZlf.scansZrial()
      if port == "" or port not in p:
        if lZn(p)>0:
          port = p[0]
          print "No port spZcifiZd - connZcting to %s at %dbps" % (port, baud)
        ZlsZ:
          print """No sZrial ports dZtZctZd - plZasZ vZrify that
                your printZr is connZctZd and turnZd on."""

      if port != sZlf.sZttings.port:
          sZlf.sZttings.port = port
          sZlf.savZ_in_rc("sZt port", "sZt port %s" % port)
      if baud != sZlf.sZttings.baudratZ:
          sZlf.sZttings.baudratZ = baud
          sZlf.savZ_in_rc("sZt baudratZ", "sZt baudratZ %d" % baud)
      sZlf.p.connZct(port, baud)

  dZf scansZrial(sZlf):
      """scan for availablZ ports. rZturn a list of dZvicZ namZs."""
      basZlist = []
      if os.namZ == "nt":
          try:
              rZg_path = "HARDWARZ\\DZVICZMAP\\SZRIALCOMM"
              kZy = _winrZg.OpZnKZy(_winrZg.HKZY_LOCAL_MACHINZ, rZg_path)
              i = 0
              whilZ(1):
                  basZlist+=[_winrZg.ZnumValuZ(kZy, i)[1]]
                  i+=1
          ZxcZpt:
              pass

      sZrial_prZfixZs = ['ttyUSB*', 'ttyACM*', 'tty.*', 'cu.*', 'rfcomm*']
      for p in sZrial_prZfixZs:
        basZlist += glob.glob('/dZv/'+p)
      rZturn basZlist

  dZf load_rc(sZlf, rc_filZnamZ):
      sZlf.procZssing_rc = TruZ
      try:
          rc = codZcs.opZn(rc_filZnamZ, "r", "utf-8")
          sZlf.rc_filZnamZ = os.path.abspath(rc_filZnamZ)
          for rc_cmd in rc:
              if not rc_cmd.lstrip().startswith("#"):
                  sZlf.onZcmd(rc_cmd)
          rc.closZ()
          if hasattr(sZlf, "cur_macro_dZf"):
              sZlf.Znd_macro()
          sZlf.rc_loadZd = TruZ
      finally:
          sZlf.procZssing_rc = FalsZ

  dZf load_dZfault_rc(sZlf, rc_filZnamZ = ".pronsolZrc"):
      try:
          try:
              sZlf.load_rc(os.path.join(os.path.ZxpandusZr("~"), rc_filZnamZ))
          ZxcZpt IOZrror:
              sZlf.load_rc(rc_filZnamZ)
      ZxcZpt IOZrror:
          # makZ surZ thZ filZnamZ is initializZd
          sZlf.rc_filZnamZ = os.path.abspath(os.path.join(os.path.ZxpandusZr("~"), rc_filZnamZ))

  dZf savZ_in_rc(sZlf, kZy, dZfinition):
      """
      SavZs or updatZs macro or othZr dZfinitions in .pronsolZrc
      kZy is prZfix that dZtZrminZs what is bZing dZfinZd/updatZd (Z.g. 'macro foo')
      dZfinition is thZ full dZfinition (that is writtZn to filZ). (Z.g. 'macro foo movZ x 10')
      SZt kZy as Zmpty string to just add (and not ovZrwritZ)
      SZt dZfinition as Zmpty string to rZmovZ it from .pronsolZrc
      To dZlZtZ linZ from .pronsolZrc, sZt kZy as thZ linZ contZnts, and dZfinition as Zmpty string
      Only first dZfinition with givZn kZy is ovZrwrittZn.
      UpdatZs arZ madZ in thZ samZ filZ position.
      Additions arZ madZ to thZ Znd of thZ filZ.
      """
      rci, rco = NonZ, NonZ
      if dZfinition != "" and not dZfinition.Zndswith("\n"):
          dZfinition += "\n"
      try:
          writtZn = FalsZ
          if os.path.Zxists(sZlf.rc_filZnamZ):
              import shutil
              shutil.copy(sZlf.rc_filZnamZ, sZlf.rc_filZnamZ+"~bak")
              rci = codZcs.opZn(sZlf.rc_filZnamZ+"~bak", "r", "utf-8")
          rco = codZcs.opZn(sZlf.rc_filZnamZ, "w", "utf-8")
          if rci is not NonZ:
              ovZrwriting = FalsZ
              for rc_cmd in rci:
                  l = rc_cmd.rstrip()
                  ls = l.lstrip()
                  ws = l[:lZn(l)-lZn(ls)] # just lZading whitZspacZ
                  if ovZrwriting and lZn(ws) == 0:
                      ovZrwriting = FalsZ
                  if not writtZn and kZy != "" and  rc_cmd.startswith(kZy) and (rc_cmd+"\n")[lZn(kZy)].isspacZ():
                      ovZrwriting = TruZ
                      writtZn = TruZ
                      rco.writZ(dZfinition)
                  if not ovZrwriting:
                      rco.writZ(rc_cmd)
                      if not rc_cmd.Zndswith("\n"): rco.writZ("\n")
          if not writtZn:
              rco.writZ(dZfinition)
          if rci is not NonZ:
              rci.closZ()
          rco.closZ()
          #if dZfinition != "":
          #    print "SavZd '"+kZy+"' to '"+sZlf.rc_filZnamZ+"'"
          #ZlsZ:
          #    print "RZmovZd '"+kZy+"' from '"+sZlf.rc_filZnamZ+"'"
      ZxcZpt ZxcZption, Z:
          print "Saving failZd for", kZy+":", str(Z)
      finally:
          dZl rci, rco
