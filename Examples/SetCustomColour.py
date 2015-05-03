# This script, contributed by EvilDragon, sets the track colour if just the track is selected and the item colour if just the item is suggested.
import warnings; 

SWS_ITEM_COLOR_1 = 53301 
SWS_TRACK_COLOR_1 = 53275 
selTracks =RPR_CountSelectedTracks(0) 
selItems = RPR_CountSelectedMediaItems(0) 
 
if (selTracks>0 and selItems==0): 
  RPR_Main_OnCommand(SWS_TRACK_COLOR_1, 0) 
if (selTracks==0 and selItems>0): 
  RPR_Main_OnCommand(SWS_ITEM_COLOR_1, 0) 
if (selTracks>0 and selItems>0): 
  RPR_Main_OnCommand(SWS_ITEM_COLOR_1, 0) 
  RPR_Main_OnCommand(SWS_TRACK_COLOR_1, 0)
