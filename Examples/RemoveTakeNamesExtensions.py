# Item Properties - Remove extensions from take names,py
 
Verbose = True    # enable/disable console info
Item_Index = 0
Found = 0
part = ["", "", ""]
Item_Count = RPR_CountMediaItems(0) # Get number of items in current project
Selected_Count = RPR_CountSelectedMediaItems(0)    # Get number of selected items in current project
 
if not Item_Count:
    RPR_ShowMessageBox("No items found in project, nothing to remove.", "Remove extensions from take names", 0)
 
# Scan each item in current  project
if Verbose:
    RPR_ShowConsoleMsg("\nScanning for items... ")
    if not Item_Count:
        RPR_ShowConsoleMsg("No items in project.")
    elif Item_Count == 1:
        RPR_ShowConsoleMsg("1 item in project, ")
        if not Selected_Count: RPR_ShowConsoleMsg("unselected.\n\n")
        else: RPR_ShowConsoleMsg("selected.\n\n")
    else:
        Msg = "{0} items in project total, {1} of them selected.\n\n".format(Item_Count, Selected_Count)
        RPR_ShowConsoleMsg(Msg)
 
if not Selected_Count:    # if no items are selected in project, we have the choice of renaming ALL items, or none at all
    apply = RPR_ShowMessageBox("No items selected. Do you wish to apply renaming to ALL items in project?", "Remove extensions from take names", 4)
    while Item_Index < Item_Count:
        if apply == 7:    # breaking out of the loop if we picked "No"
            break
        Item_ID = RPR_GetMediaItem(0, Item_Index)
        Current_Take = RPR_GetMediaItemInfo_Value(Item_ID, "I_CURTAKE") # Get active take index for current item
        Take_ID = RPR_GetMediaItemTake(Item_ID, int(Current_Take)); 
        Take_Name = RPR_GetSetMediaItemTakeInfo_String(Take_ID, "P_NAME", "", 0)[3] # Get active take name
        part = Take_Name.rpartition('.')
        if ((part[0] == "") and (part[1] == "")):    # testing if item/take name has no extension
            Take_Name = part[2].strip()                # correcting the partitioned string to contain take name
            RPR_GetSetMediaItemTakeInfo_String(Take_ID, "P_NAME", Take_Name, 1)
            if Verbose:
                Msg = "Item {0}/{1}: no extension found, nothing to rename\n".format(Item_Index + 1, Item_Count, Take_Name, part[2])
                RPR_ShowConsoleMsg(Msg)
        else:
            Take_Name = part[0].strip()
            Found = Found + 1                        # incrementing the number of renamed items - if there was no extension removed above, the counter will not increment
            RPR_GetSetMediaItemTakeInfo_String(Take_ID, "P_NAME", Take_Name, 1) 
            if Verbose:
                Msg = "Item {0}/{1}: renamed to '{2}' (removed extension .{3})\n".format(Item_Index + 1, Item_Count, Take_Name, part[2])
                RPR_ShowConsoleMsg(Msg)
        Item_Index = Item_Index + 1;
else:    # if we have any items selected in project, then extension removal will be applied to those items only
    while Item_Index < Selected_Count:
        Item_ID = RPR_GetSelectedMediaItem(0, Item_Index)                            # Get the ID of first selected item
        Current_Take = RPR_GetMediaItemInfo_Value(Item_ID, "I_CURTAKE")                # Get active take index for current item
        Take_ID = RPR_GetMediaItemTake(Item_ID, int(Current_Take)); 
        Take_Name = RPR_GetSetMediaItemTakeInfo_String(Take_ID, "P_NAME", "", 0)[3]    # Get active take name
        part = Take_Name.rpartition('.')
        if ((part[0] == "") and (part[1] == "")):    # testing if item/take name has no extension
            Take_Name = part[2].strip()                # correcting the partitioned string to contain take name
            RPR_GetSetMediaItemTakeInfo_String(Take_ID, "P_NAME", Take_Name, 1)
            if Verbose:
                Msg = "Item {0}/{1}: no extension found, nothing to rename\n".format(Item_Index + 1, Selected_Count, Take_Name, part[2])
                RPR_ShowConsoleMsg(Msg)
        else:
            Take_Name = part[0].strip()
            Found = Found + 1                        # incrementing the number of renamed items - if there was no extension removed above, the counter will not increment
            RPR_GetSetMediaItemTakeInfo_String(Take_ID, "P_NAME", Take_Name, 1) 
            if Verbose:
                Msg = "Item {0}/{1}: renamed to '{2}' (removed extension .{3})\n".format(Item_Index + 1, Selected_Count, Take_Name, part[2])
                RPR_ShowConsoleMsg(Msg)
        Item_Index = Item_Index + 1;    
 
if not Found: RPR_ShowMessageBox("No items were renamed.", "Extension removing finished", 0)
elif Found == 1: RPR_ShowMessageBox("1 item was renamed.", "Extension removing finished", 0)
else: RPR_ShowMessageBox("%d items were renamed." % Found, "Extension removing finished", 0)
 
if Verbose:
    RPR_ShowConsoleMsg("\nExtension removing finished: ")
    if not Found:
        RPR_ShowConsoleMsg("No items renamed\n")
    elif Found == 1:
        RPR_ShowConsoleMsg("1 item renamed\n")
    else:
        RPR_ShowConsoleMsg("%d items renamed\n" % Found)
