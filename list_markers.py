from PyReaper import *

project_id = 0
project = ReaperProject(project_id)
msg(len(project.simple_markers))
msg(len(project.regions))

msg(project.simple_markers[0:])
msg([region for region in project.regions])