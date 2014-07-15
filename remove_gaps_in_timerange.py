from PyReaper import *

project = ReaperProject()
track = project.selected_tracks[0]
last = None
for item in track.items_in_time_range:
	if last is not None and last.end < item.position:
		item.position = last.end
	last = item
RPR_UpdateTimeline()