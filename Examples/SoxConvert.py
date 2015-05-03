# Sample rate conversation with SOX and ReaScript by dub3000:
import re
import os.path
import subprocess
 
RPR_ShowConsoleMsg("BETA TEST ONLY! SOX massconvert util for Reaper by dan@remaincalm.org\n")
# NOTE: probably not compatible with multiple take items!
# USE AT OWN RISK!
# Usage: have SOX installed
# Select items. Run this script. SOX will be invoked on everything and 
# the resulting files will be added to Reaper session on new tracks.
# Code tries to be safe and not overwrite files etc but please use caution regardless!
 
try:
 
    sox = "C:\Program Files\sox\sox.exe"
    preOpts = ["-V"]     #verbosity
    midOpts = ["-b","16"]    # bitdepth
    postOpts = ["rate","-m","44k"] # output rate, change -m to -h or -v for high/extreme quality

    # project num
    defaultProject = 0
    itemsToAdd = {} # hash of filename => position

    # count selected items
    numItems = RPR_CountSelectedMediaItems(defaultProject)

    # for each item
    for itemIdx in range(numItems):
 
        # get item                # TODO: handle takes?
        mediaItem = RPR_GetSelectedMediaItem(defaultProject, itemIdx);

        # extract file info:
        rawData = ""
        maxLen = 16 * 1024 - 1
        result = RPR_GetSetItemState(mediaItem,"",maxLen)
        regExp = re.compile("SOURCE WAVE\\s*FILE\\s\"([^\\s\"]*)\"")
        rawData = str(result[2])
        matched = regExp.search(rawData)
        if(matched != None):
            # we found a file
            infile = str(matched.group(1))
            outfile = infile + ".resampled.wav"
 
            RPR_ShowConsoleMsg("Attempting to process " + infile + "\n")
            if(os.path.exists(outfile) == 0):
                # invoke sox
                RPR_ShowConsoleMsg("Processing...\n")
                subprocess.call([sox] + preOpts + [infile] + midOpts + [outfile] + postOpts)
 
                # add to list of media items to add at end of process
                # (we do that there so our item selection doesn't get messed up)
                position = RPR_GetMediaItemInfo_Value(mediaItem, "D_POSITION")
                itemsToAdd[outfile] = position
            else:
                RPR_ShowConsoleMsg("Skipping item, output file already exists (can't overwrite)!\n")
        else:
            RPR_ShowConsoleMsg("Skipping item, no file source detected!\n")
 
    # now add all media items to their own track
    for itemFilename in itemsToAdd.keys():
        RPR_ShowConsoleMsg("Inserting " + itemFilename + " into project\n")
 
        # make new track
        RPR_InsertTrackAtIndex(0,0)
        newTrack = RPR_GetTrack(defaultProject, 0)
 
        # set cursor pos 
        itemPos = itemsToAdd[itemFilename]
        RPR_SetEditCurPos2(defaultProject, itemPos, 1, 0)
 
        # select track and insert
        RPR_SetTrackSelected(newTrack,1)
        RPR_InsertMedia(itemFilename,0)

    # finished
    RPR_ShowConsoleMsg("Done!\n")

except Exception as inst:
    # handle errors
    RPR_ShowConsoleMsg(str(inst))
