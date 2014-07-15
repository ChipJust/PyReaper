#RPR_APITest()

#PyReaper v0.00002
#by Brent Elliott


#ReaperProject
##get_all_tracks
##get_all_media_items
##get_all_takes

#ReaperTrack
##get_all_children
##get_all_media_items
#ReaperFX


##ReaperMediaItem
##ReaperTake

####get_tracks(selected=True)
####gradient(listOfItemsOrTracks, colorA, colorB)

from reaper_python import *
from math import log

def msg(m):
    RPR_ShowConsoleMsg(m)
    RPR_ShowConsoleMsg('\n')

#i hate this
def time_to_beats(f):
    beat_tuple = RPR_TimeMap2_timeToBeats(0, f, 0, 0, 0, 0)
    bars = int(beat_tuple[3]+1)
    beats = int(beat_tuple[0]+1)
    decimal = int(round(beat_tuple[0]-(beats-1), 2)*100)
    return (bars, beats, decimal)

class GenericLister(object):
    def __init__(self, count_f, get_f, const_args, contains_attr, cls):
        self.count_f = count_f
        self.get_f = get_f
        self.const_args = const_args
        self.contains_attr = contains_attr
        self.cls = cls

    def __len__(self):
        return self.count_f(*self.const_args)

    def __getitem__(self, key):
        if isinstance(key, int):
            if key < 0 or key > self.__len__()-1:
                raise IndexError()
            else:
                return self.cls(*self.get_f(*(self.const_args + [key])))
        elif isinstance(key, slice):
            ret = list()
            for i in xrange(key.start or 0, key.stop or self.__len__(), key.step or 1):
                ret.append(self.cls(*self.get_f(*(self.const_args + [key]))))
            return ret
        else:
            raise TypeError()

    #def __iter__():
    #    pass

    def __contains__(self, item):
        return bool(getattr(item, self.contains_attr))

class ReaperProject(object):
    def __init__(self, project_number=0):
        #set project 0 as default
        #globalize this
        self.project_number = project_number

        self.selected_tracks = GenericLister(RPR_CountSelectedTracks, lambda *args: (self, RPR_GetSelectedTrack(*args)), [project_number], 'selected', ReaperTrack)
        self.all_tracks = GenericLister(RPR_CountTracks, lambda *args: (self, RPR_GetTrack(*args)), [project_number], '', ReaperTrack) # FIXME: contains?
        marker_count = lambda p: RPR_CountProjectMarkers(p)[0]
        self.markers = GenericLister(marker_count, RPR_EnumProjectMarkers2, [project_number], '', ReaperMarker)

    @property
    def time_range(self):
        return RPR_GetSet_LoopTimeRange2(self.project_number, False, False, 0., 0., False)[3:5]

    @time_range.setter
    def time_range(self, time_range):
        return RPR_GetSet_LoopTimeRange2(self.project_number, True, False, time_range[0], time_range[1], False)

    @property
    def loop(self):
        return RPR_GetSet_LoopTimeRange2(self.project_number, False, True, 0., 0., False)[3:5]

    @loop.setter
    def loop(self, time_range):
        return RPR_GetSet_LoopTimeRange2(self.project_number, True, True, time_range[0], time_range[1], False)

    # def get_all_tracks():
    #     tracks = []
    #     for i in range(RPR_CountTracks(0)):
    #         tracks.append(ReaperTrack(RPR_GetTrack(0, i)))
    #     return tracks

    # def get_selected_tracks():
    #     tracks = []
    #     for i in range(RPR_CountSelectedTracks(0)):
    #         tracks.append(ReaperTrack(RPR_GetSelectedTrack(0, i)))
    #     return tracks

class ReaperMarker(object):
    def __init__(self, id, is_region, pos, pos_end, name, index):
        self.id = id
        self.is_region = is_region
        self.position = pos
        self.position_end = pos_end
        self.name = name
        self.index = index

class ReaperMediaItem(object):
    def __init__(self, project, track, id):
        self.project = project
        self.track = track
        self.id = id


    def get_all_takes(self):
        takes = []
        num_takes = RPR_GetMediaItemNumTakes(self.id)
        for take in range(num_takes):
            takes.append(RPR_GetMediaItemTake(self.id, take))
        return takes
    #mute
    @property
    def mute(self):
        if RPR_GetMediaItemInfo_Value(self.id, 'B_MUTE') == 0.0:
            return False
        else:
            return True

    @mute.setter
    def mute(self, b):
        if b:
            RPR_SetMediaItemInfo_Value(self.id, 'B_MUTE', 1.0)
        else:
            RPR_SetMediaItemInfo_Value(self.id, 'B_MUTE', 0.0)




    @property
    def length(self):
        return RPR_GetMediaItemInfo_Value(self.id, 'D_LENGTH')

    @length.setter
    def length(self, l):
        pass


    @property
    def position(self):
        return RPR_GetMediaItemInfo_Value(self.id, 'D_POSITION')

    @position.setter
    def position(self, l):
        RPR_SetMediaItemInfo_Value(self.id, 'D_POSITION', l)


    @property
    def length(self):
        return RPR_GetMediaItemInfo_Value(self.id, 'D_LENGTH')

    @length.setter
    def length(self, l):
        RPR_SetMediaItemInfo_Value(self.id, 'D_LENGTH', l)

    @property
    def end(self):
        return self.position + self.length

    #selection
    @property
    def selected(self):
        return bool(RPR_IsMediaItemSelected(self.id))

    @selected.setter
    def selected(self, value):
        RPR_SetMediaItemSelected(self.id, 1 if value else 0)



class ReaperFX(object):
    def __init__(self):
        pass



class ReaperTrack(object):
    def __init__(self, project, id):
        self.project = project
        self.id = id

        self.items = GenericLister(RPR_GetTrackNumMediaItems, lambda *args: (project, self, RPR_GetTrackMediaItem(*args)), [id], '', ReaperMediaItem) # FIXME: contains?

    #def get_all_media_items(self):
    #    media_items = []
    #    num_items = RPR_GetTrackNumMediaItems(self.id)
    #    for item in range(num_items):
    #        media_items.append(ReaperMediaItem(RPR_GetTrackMediaItem(self.id, item)))
    #    return media_items

    @property
    def items_in_time_range(self):
        loop = self.project.time_range
        for item in self.items:
            if item.position >= loop[0] and item.position+item.length <= loop[1]:
                yield item

    @property
    def number(self):
        return int(RPR_GetMediaTrackInfo_Value(self.id, 'IP_TRACKNUMBER'))

    #volume getter and setter
    @property
    def volume(self):
        return RPR_GetMediaTrackInfo_Value(self.id, 'D_VOL')

    @volume.setter
    def volume(self, value):
        RPR_SetMediaTrackInfo_Value(self.id, 'D_VOL', value)




    #db getter and setter
    @property
    def db(self):
        volume = RPR_GetMediaTrackInfo_Value(self.id, 'D_VOL')
        return (20 * log(volume)) / log(10)
    
    @db.setter
    def db(self, value):
        volume = 10 ** (float(value) / 20)
        RPR_SetMediaTrackInfo_Value(self.id, 'D_VOL', volume)




    #pan getter and setter
    @property
    def pan(self):
        return RPR_GetMediaTrackInfo_Value(self.id, 'D_PAN')

    @pan.setter
    def pan(self, value):
        RPR_SetMediaTrackInfo_Value(self.id, 'D_PAN', value)




    #mute
    @property
    def mute(self):
        if RPR_GetMediaTrackInfo_Value(self.id, 'B_MUTE') == 0.0:
            return False
        else:
            return True

    @mute.setter
    def mute(self, b):
        if b:
            RPR_SetMediaTrackInfo_Value(self.id, 'B_MUTE', 1.0)
        else:
            RPR_SetMediaTrackInfo_Value(self.id, 'B_MUTE', 0.0)




    #solo property
    @property
    def solo(self):
        #replace with GetMediaTrackInfo_Value
        flag = RPR_GetTrackState(self.id, 0)[2]
        if flag & 16:
            return True
        else:
            return False

    @solo.setter
    def solo(self, value):
        #solo_type
        #0 = off
        #1 = solo
        #2 = solo in place
        RPR_SetMediaTrackInfo_Value(self.id, 'I_SOLO', value)




    #phase_invert
    @property
    def phase_invert(self):
        if RPR_GetMediaTrackInfo_Value(self.id, 'B_PHASE') == 0.0:
            return False
        else:
            return True

    @phase_invert.setter
    def phase_invert(self, value):
        if value:
            RPR_SetMediaTrackInfo_Value(self.id, 'B_PHASE', 1.0)
        else:
            RPR_SetMediaTrackInfo_Value(self.id, 'B_PHASE', 0.0)




    @property
    def record_monitor(self):
        return int(RPR_GetMediaTrackInfo_Value(self.id, 'I_RECMON'))

    @record_monitor.setter
    def record_monitor(self, value):
        RPR_SetMediaTrackInfo_Value(self.id, 'I_RECMON', value)




    @property
    def fx_enabled(self):
        if RPR_GetMediaTrackInfo_Value(self.id, 'I_FXEN') == 0.0:
            return False
        else:
            return True

    @fx_enabled.setter
    def fx_enabled(self, value):
        if value:
            RPR_SetMediaTrackInfo_Value(self.id, 'I_FXEN', 1.0)
        else:
            RPR_SetMediaTrackInfo_Value(self.id, 'I_FXEN', 0.0)




    @property
    def record_arm(self):
        if RPR_GetMediaTrackInfo_Value(self.id, 'I_RECARM') == 0.0:
            return False
        else:
            return True

    @record_arm.setter
    def record_arm(self, value):
        if value:
            RPR_SetMediaTrackInfo_Value(self.id, 'I_RECARM', 1.0)
        else:
            RPR_SetMediaTrackInfo_Value(self.id, 'I_RECARM', 0.0)


    #name getter and setter
    @property
    def name(self):
        return RPR_GetSetMediaTrackInfo_String(self.id, "P_NAME", '', False)[3]

    @name.setter
    def name(self, value):
        #holy shit GetSetTrackState is a disaster
        RPR_GetSetMediaTrackInfo_String(self.id, "P_NAME", value, True)




    #color getter and setter
    @property
    def color(self):
        return RPR_GetTrackColor(self.id)

    @color.setter
    def color(self, value):
        if type(value) is str:
            if value.startswith('#'):
                RPR_SetTrackColor(self.id, int(value.strip('#'), 16))
        elif type(value) is tuple:
            h = '%02x%02x%02x' % value
            RPR_SetTrackColor(self.id, int(h, 16))
        else:
            raise TypeError




    #selection
    @property
    def selected(self):
        flag = RPR_GetTrackState(self.id, 0)[2]
        return bool(flag & 2)

    @selected.setter
    def selected(self, value):
        if value:
            RPR_SetTrackSelected(self.id, 1)
        else:
            RPR_SetTrackSelected(self.id, 0)















#for track in get_all_tracks():
    #track.phase_invert = True
    #track.record_monitor = 2
    #track.fx_enabled = True
    #track.record_arm = True
    #track.db = track.db -0.5
    #track.color = '#000000'
    #media_items = track.get_all_media_items()
    #f media_items:
      #  for item in media_items:
       #     for take in item.get_all_takes():
        #        msg(take)

        #track.color = (100,100,100)
        #track.db = 0
        #track.pan = -0.1
        #msg(track.phase_reverse)
        #msg(track.phase_reverse)
    #if track.name.startswith('dick'):
    #    msg(track.volume)
    #track.solo = 0
    #track.get_media_items()
    #for each in track.media_items:
    #   msg(time_to_beats(each.position))