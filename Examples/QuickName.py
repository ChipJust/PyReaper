# ------------------------------------------------------------------------------
# opens a dialog box to ask user for new media item take name
# ------------------------------------------------------------------------------
# set to active project (0)
project = 0;
# get the first selected track
track = RPR_GetSelectedTrack(project, 0);
# get the first selected media item
item = RPR_GetSelectedMediaItem(project, 0);
# get active take
take = RPR_GetMediaItemInfo_Value(item, 'I_CURTAKE');
# get take id
takeid = RPR_GetMediaItemTake(item, int(take));
# get take name
takename = RPR_GetSetMediaItemTakeInfo_String(takeid, 'P_NAME', '', 0)[3];
# ------------------------------------------------------------------------------
# dialog item name
iname = 'New name';
# set number of dialog items
nitems = 1;
# maximum length of name
maxlen = 100;
# receives a tuple 'userinput'
userinput = RPR_GetUserInputs('Rename media item take', nitems, iname, takename, maxlen);
# check if first element is true (user clicked ok)
if userinput[0]:
	# change take name to userinput[3]	
	RPR_GetSetMediaItemTakeInfo_String(takeid, 'P_NAME', userinput[4], 1);
# ------------------------------------------------------------------------------
