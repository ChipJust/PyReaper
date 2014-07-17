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
from sws_python import *
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

# use for get functions used in GenericListers
def supports_slice(func):
    func.supports_slice = True
    return func

class GenericLister(object):
    def __init__(self, cls, count_f, get_f, const_args=[], contains_attr=None):
        self.cls = cls
        self.count_f = count_f
        self.get_f = get_f
        self.const_args = const_args
        self.contains_attr = contains_attr
        # assign after __init__ for further customization
        self.instance_args = []

    def _inst(self, key, vals=None):
        if vals is None:
            vals = self.get_f(*(self.const_args + [key]))
        args = list(self.instance_args)
        args.extend(vals)
        return self.cls(*args)

    def __len__(self):
        return self.count_f(*self.const_args)

    def __getitem__(self, key):
        if isinstance(key, int):
            if key < 0 or key > self.__len__()-1:
                raise IndexError()
            else:
                return self._inst(key)
        elif isinstance(key, slice):
            if getattr(self.get_f, 'supports_slice', False):
                # forward to get function if it supports slices
                return [self._inst(-1, vals) for vals in self.get_f(*(self.const_args + [key]))]
            ret = list()
            for i in xrange(key.start or 0, key.stop or self.__len__(), key.step or 1):
                ret.append(self._inst(i))
            return ret
        else:
            raise TypeError()

    def __contains__(self, item):
        if getattr(self.contains_attr, '__call__'):
            return self.coontains_attr(item)
        elif isinstance(self.contains_attr, basestring):
            return bool(getattr(item, self.contains_attr))
        else:
            # if no 'contains' check was provided, we have worst case scenario
            # and check every single record until we find it
            for obj in self:
                if obj == item:
                    return True
            return False

class GenericObject(object):
    def __eq__(self, other):
        return type(self) == type(other) and self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)

class ReaperProject(GenericObject):
    def __init__(self, id=0):
        self.id = id

        track_in_prj = lambda t: t.project.id == id
        get_sel_track = lambda *args: (self, RPR_GetSelectedTrack(*args))
        self.selected_tracks = GenericLister(ReaperTrack, RPR_CountSelectedTracks, RPR_GetSelectedTrack, [id], lambda t: track_in_prj(t) and track.selected)
        self.selected_tracks.instance_args = [self]
        self.all_tracks = GenericLister(ReaperTrack, RPR_CountTracks, RPR_GetTrack, [id], track_in_prj)
        self.all_tracks.instance_args = [self]

        self.markers = GenericLister(ReaperMarker, self._count_markers, self._get_marker, [0])
        self.markers.instance_args = [self]
        self.simple_markers = GenericLister(ReaperMarker, self._count_markers, self._get_marker, [1])
        self.simple_markers.instance_args = [self]
        self.regions = GenericLister(ReaperMarker, self._count_markers, self._get_marker, [2])
        self.regions.instance_args = [self]

    ### marker_type = 0 (all), 1 (simple), 2 (region)
    def _count_markers(self, marker_type=0):
        i = marker_type + 1 if marker_type > 0 else 0
        return RPR_CountProjectMarkers(self.id, 0, 0)[i]

    @supports_slice
    def _get_marker(self, marker_type, id):
        if isinstance(id, int):
            for i in range(self._count_markers()):
                marker = RPR_EnumProjectMarkers3(self.id, i, False, 0., 0., '', 0, 0)
                if  marker[7] == id + 1 and (marker_type == 0 or marker[3] == marker_type - 1):
                    return marker
            raise IndexError()
        elif isinstance(id, slice): # TODO: this is still unused, need to 
            indexes = range(id.start or 0, id.stop or self._count_markers(marker_type), id.step or 1)
            ret = list()
            for i in range(self._count_markers()):
                marker = RPR_EnumProjectMarkers3(self.id, i, False, 0., 0., '', 0, 0)
                if marker[7] == indexes[0] + 1 and (marker_type == 0 or marker[3] == marker_type - 1):
                    del indexes[0]
                    ret.append(marker)
                if len(indexes) == 0:
                    break
            if len(indexes) > 0:
                raise IndexError()
            return ret
        else:
            raise TypeError()

    @property
    def time_range(self):
        return RPR_GetSet_LoopTimeRange2(self.id, False, False, 0., 0., False)[3:5]

    @time_range.setter
    def time_range(self, time_range):
        return RPR_GetSet_LoopTimeRange2(self.id, True, False, time_range[0], time_range[1], False)

    @property
    def loop(self):
        return RPR_GetSet_LoopTimeRange2(self.id, False, True, 0., 0., False)[3:5]

    @loop.setter
    def loop(self, time_range):
        return RPR_GetSet_LoopTimeRange2(self.id, True, True, time_range[0], time_range[1], False)



class ReaperMarker(GenericObject):
    def __init__(self, prj, global_index, project_num, idx, is_rgn, pos, pos_end, blackhole, index, color):
        self.project = prj
        self.id = global_index - 1
        self.is_region = bool(is_rgn)
        self._pos = pos
        self._pos_end = pos_end
        self.index = index
        self.color = color

    def __eq__(self, other):
        add_check = self.project == other.project
        return super(self, GenericObject).__eq__(other) and add_check

    @property
    def name(self):
        fast_str = SNM_CreateFastString('')
        SNM_GetProjectMarkerName(self.project.id, self.index, self.is_region, fast_str)
        ret = SNM_GetFastString(fast_str)
        SNM_DeleteFastString(fast_str)
        return ret

    @name.setter
    def name(self, name):
        pass # not implemented yet

    def __repr__(self):
        args = [self.id, self.name, self.position, self.end or '']
        if args[-1]:
            args[-1] = '-' + str(args[-1])
        return '{0}: {1} ({2}{3})'.format(*args)

    @property
    def position(self):
        return self._pos

    @position.setter
    def position(self, pos):
        pass # not implemented

    @property
    def end(self):
        return self._pos_end

    @end.setter
    def end(self, pos_end):
        pass # not implemented


class ReaperMediaItem(GenericObject):
    def __init__(self, project, track, id):
        self.project = project
        self.track = track
        self.id = id

    def __eq__(self, other):
        add_check = self.project == other.project and self.track == other.track
        return super(self, GenericObject).__eq__(other) and add_check

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



class ReaperTrack(GenericObject):
    def __init__(self, project, id):
        self.project = project
        self.id = id

        self.items = GenericLister(ReaperMediaItem, RPR_GetTrackNumMediaItems, lambda *args: (project, self, RPR_GetTrackMediaItem(*args)), [id]) # FIXME: contains?

    def __eq__(self, other):
        add_check = self.project == other.project
        return add_check and super(self, GenericObject).__eq__(other)

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