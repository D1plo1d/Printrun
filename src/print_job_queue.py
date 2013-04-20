class PrintJobQueue(EventEmitter):

  def __init__(self):
    super(PrintJobQueue, self).__init__()
    self.list = deque([])
    self.__last_id = 0

  def public_list(self):
    # A sanitized version of list for public consumption via construct
    l2 = []
    for job in self.list:
      l2.append(self.sanitize(job))
    return l2

  def sanitize(self, job):
    return dict(
      id = job["id"],
      original_file_name = job["original_file_name"],
      rank = job["rank"]
    )

  def order(self):
    sorted(self.list, key=lambda job: job['rank'])


  def add(self, original_file_name, body):
    ext = os.path.splitext(original_file_name)[1]
    job = dict(
      id = self.__last_id,
      rank = len(self.list),
      original_file_name=original_file_name,
      body= body,
    )
    self.__last_id += 1

    self.list.append(job)
    print "Added %s"%(original_file_name)
    self.fire("job_added", job)

  def display_summary(self):
    print "Print Jobs:"
    for job in self.list:
      print "  %i: %s"%(job['id'], job['original_file_name'])
    print ""
    return True

  def remove(self, job_id):
    job = self.find_by_id(job_id)
    if job == None:
      return False
    self.list.remove(job)
    print "Print Job Removed"
    self.fire("job_removed", job)

  def update(self, job_id, job_attrs):
    job = self.find_by_id(job_id)
    if job == None:
      return False
    job['rank'] = job_attrs['position']
    self.order()
    print "Print Job Updated"
    self.fire("job_updated", job)

  def find_by_id(self, job_id):
    for job in self.list:
      if job['id'] == job_id: return job
    return None

  def fire(self, event_name, content):
    self.display_summary()
    super(PrintJobQueue, self).fire(event_name, content)
