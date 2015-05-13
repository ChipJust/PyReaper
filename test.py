
#
# Junk to do
#   create a new tack on the selected track
#   copy the take to the new take
#
#   rescale the whole project by the time slice highlighted
#   possibly even aligning the start and end of the time slice to the closest event, i.e. onset of a beat identified by transients
#

# Int RPR_ShowMessageBox(String msg, String title, Int type)
# type 0=OK,1=OKCANCEL,2=ABORTRETRYIGNORE,3=YESNOCANCEL,4=YESNO,5=RETRYCANCEL : ret 1=OK,2=CANCEL,3=ABORT,4=RETRY,5=IGNORE,6=YES,7=NO

# NEWREL: We need to make these some sort of enum like thing in PyReaper
MessageBoxType_OK = 0
MessageBoxType_OKCANCEL = 1
MessageBoxType_ABORTRETRYIGNORE = 2
MessageBoxType_YESNOCANCEL = 3
MessageBoxType_YESNO = 4
MessageBoxType_RETRYCANCEL = 5
MessageBoxRet_OK = 1
MessageBoxRet_CANCEL = 2
MessageBoxRet_ABORT = 3
MessageBoxRet_RETRY = 4
MessageBoxRet_IGNORE = 5
MessageBoxRet_YES = 6
MessageBoxRet_NO = 7

import PyReaper

def SelectedMediaItems (proj=0):
    for i in range (RPR_CountSelectedMediaItems (proj)):
        yield RPR_GetSelectedMediaItem (proj, i)

#Int RPR_GetMediaItemNumTakes(MediaItem* item)
def ItemTakes (item):
    for i in range(RPR_GetMediaItemNumTakes (item)):
        yield RPR_GetMediaItemTake (item, i)

#(Boolean retval, MediaItem_Take* tk, String parmname, String stringNeedBig, Boolean setnewvalue) = RPR_GetSetMediaItemTakeInfo_String(tk, parmname, stringNeedBig, setnewvalue)

def show_selected():
    s = ""
    for item in SelectedMediaItems():
        for take in ItemTakes(item):
            source = RPR_GetSetMediaItemTakeInfo_String(take, "P_NAME", "", 0)
            s += "item:%s\ntake:%s\nsource:%s\n" % (item, take, source)
    #RPR_ShowMessageBox (s, "Debug", MessageBoxType_OKCANCEL)
    RPR_ShowConsoleMsg (s)

def show_stuff():
    number_items_selected = RPR_CountSelectedMediaItems (0)
    RPR_ShowConsoleMsg ("number_items_selected %d\n" % number_items_selected)
    cursor_position = RPR_GetCursorPosition ()
    RPR_ShowConsoleMsg ("cursor_position %d\n" % cursor_position)
    num_tracks = RPR_CountTracks (0)
    RPR_ShowConsoleMsg ("num_tracks %d\n" % num_tracks)

def add_a_take():
    """Operates on the first selected media item and creates another take on it."""
    number_items_selected = RPR_CountSelectedMediaItems (0)
    if number_items_selected < 1:
        RPR_ShowConsoleMsg ("No media items selected.")
        return
    if number_items_selected > 1:
        RPR_ShowConsoleMsg ("More than one media item selected.")
        return
    #ok make the new take already
    media_item = RPR_GetSelectedMediaItem (0, 0)
    take = RPR_AddTakeToMediaItem( media_item )
    RPR_UpdateItemInProject( media_item )

def Tracks(proj=0):
    for i in range(RPR_CountTracks(proj)):
        yield RPR_GetTrack(proj, i)

def show_tracks():
    s = ""
    for track in Tracks():
        s += str(RPR_GetTrackState(track, 0)) + "\n"
    RPR_ShowConsoleMsg (s)

# How do I find the track that a media item is
# How do I determine if a media item is a midi or not
# What are all the possible things a media item can be?

#RPR_GetAudioAccessorEndTime -- what that do

def ProjectSettings():
    what = RPR_Main_OnCommand(40021, 0)
    RPR_ShowConsoleMsg (str(what))

def SetProjectTimeFromSelection():
    what = RPR_Main_OnCommand(40843, 0)
    RPR_ShowConsoleMsg (str(what))

def show_chunk():
    number_items_selected = RPR_CountSelectedMediaItems (0)
    if number_items_selected < 1:
        RPR_ShowConsoleMsg ("No media items selected.")
        return
    if number_items_selected > 1:
        RPR_ShowConsoleMsg ("More than one media item selected.")
        return
    media_item = RPR_GetSelectedMediaItem (0, 0)
    chunk = "" # Empty string means get
    maxlen = 1024*1024 # 1MB is the max chunk size
    (status, media_item, chunk, maxlen) = RPR_GetSetItemState(media_item, chunk, maxlen)
    RPR_ShowConsoleMsg ("status=%s, media_item=%s, maxlen=%s\n" % (status, media_item, maxlen))
    RPR_ShowConsoleMsg ("chunk:\n%s\n" % (chunk))

def main():
    #PyReaper.find_select_range()
    show_chunk()
    

if __name__ == '__main__':
    main()
    