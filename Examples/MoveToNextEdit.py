# MoveToNextEdit.py / MoveToPrevEdit.py
# Moves the cursor to the closest project marker or
# item edit point on the selected track(s).
# Snaps to project start, project markers,
# item start/ends and fade points.
#
# Written by Thomas Eberger
# Use at your own risk!
 
# Search direction
# 1 = forwards, -1 = backwards
direction = 1
 
cursorTime = RPR_GetCursorPosition()
timeList = []
 
# Collect all selected Tracks
noTracks = RPR_CountSelectedTracks(0)
currTrack = 0
selectedTracks = []
while (currTrack < noTracks):
    selectedTracks.append(RPR_GetSelectedTrack(0, currTrack))
    currTrack += 1
 
# Iterate through all items
noItems = RPR_CountMediaItems(0) + 1
currItem = 0
while (currItem < noItems):
    item = RPR_GetMediaItem(0, currItem)
    if RPR_GetMediaItem_Track(item) in selectedTracks:
        start = RPR_GetMediaItemInfo_Value(item, 'D_POSITION')
        end = start + RPR_GetMediaItemInfo_Value(item, 'D_LENGTH')
        fadein = start + RPR_GetMediaItemInfo_Value(item, 'D_FADEINLEN')
        fadeout = end - RPR_GetMediaItemInfo_Value(item, 'D_FADEOUTLEN')
        templist = [start, end, fadein, fadeout]
        for temptime in templist:
            delta = direction * (temptime - cursorTime)
            if (delta > 0):
                timeList.append(delta)
    currItem += 1
 
# Iterate through all markers
markerID = 0
done = 0
while (done == 0):
    (svar1, svar2, svar3, start, end, svar6, svar7) = RPR_EnumProjectMarkers(markerID, 0, 0, 0, "", 1)
    if svar1 == 0:
        done = 1
    else:
        delta = direction * (start - cursorTime)
        if (delta > 0):
            timeList.append(delta)
        delta = direction * (end - cursorTime)
        if (delta > 0):
            timeList.append(delta)
 
    markerID += 1
 
# Add project start as possible position
delta = direction * cursorTime * -1
if (delta > 0):
    timeList.append(delta)
 
# Find closest position
if (len(timeList) > 0):
    newTime = direction * min(timeList) + cursorTime
else:
    newTime = cursorTime
 
# Set the new cursor position
RPR_SetEditCurPos(newTime, 1, 1)
