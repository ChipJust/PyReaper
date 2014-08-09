from PyReaper import *

project = ReaperProject()
project.selected_tracks[:-1]
project.selected_tracks[-1:]
track = project.selected_tracks[0]
msg(len(track.items))
item = track.items[project.time_range[0]]
item.selected = True
item2 = track.items._get_left(project.time_range[1])
item2.selected = True
RPR_UpdateTimeline()