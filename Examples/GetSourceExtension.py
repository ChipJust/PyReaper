#
# GetSourceExtension.py
#
 
sel = RPR_CountSelectedMediaItems(0)
item = RPR_GetSelectedMediaItem(0,0)
take = RPR_GetMediaItemTake(item,0)
source = RPR_GetSetMediaItemTakeInfo_String(take, "P_NAME", "", 0)[3]
part1 = source.rpartition('.')
part2 = part1[2]
part2 = part2.rpartition('_')
 
if ((part2[0] == "") and (part2[1] == "")):
	part2 = part2[2]
else:
	part2 = part2[0]
 
if sel != 0:
	RPR_ShowConsoleMsg("Extension of selected item is: %s" %part2)
