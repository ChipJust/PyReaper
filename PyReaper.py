from reaper_python import *
from sws_python import *
from math import log


# TODO:
# 1) Implement bulk functions/properties? on genericlister so that this would be possible:
#      item_list[:100].mute = True # mute items from first up to 100th
# 2) Implement hybrid slices, e.g.:
#      item_list["1.1.0":50] or item_list[:224.4:2]
# 3) Implement lazy properties as in http://stackoverflow.com/a/3013910, e.g. (in ReaperProject):
#      @lazyprop
#      all_tracks(self):
#          return GenericLister(ReaperTrack, RPR_CountTracks, RPR_GetTrack, [id], track_in_prj)
#      # (instead of initializing in constructor)

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

# GenericLister: lazy iteration and indexing for (almost) any sorted list in reaper
class GenericLister(object):
    ## this encapsulates any sorted list in Reaper. Arguments should be the following:
    ## cls: Python class for all objects in this list (e.g. ReaperTrack for items in project.tracks)
    ## count_f: function which returns how many objects are in this list (must return non-negative integer). Receives const_args as arguments.
    ## get_f:
    ## const_args: list of arguments which will be passed to count_f, get_f and delete_f as first arguments
    ## contains_check:
    ## # additional arguments can be assigned after __init__:
    ## instance_args:
    ## delete_f: function which deletes objects in this list. Receives *const_args, id as arguments. 
    def __init__(self, cls, count_f, get_f, const_args=[], contains_check=None):
        self.cls = cls
        self.count_f = count_f
        self.get_f = get_f
        self.const_args = const_args
        self.contains_check = contains_check
        # assign after __init__ for further customization
        self.instance_args = []
        self.delete_f = None # no delete func by default
        self.limits = None # use _set_limits
        self.steps = None # use _set_limits

    def clone(self, insert_args=[]):
        args = [self.cls, self.count_f, self.get_f, self.const_args, self.contains_check]
        for ins_arg in reversed(insert_args):
            args.insert(0, ins_arg)
        new = self.__class__(*args)
        new.instance_args = self.instance_args
        new.limits = self.limits
        new.steps = self.steps
        return new
    
    def _resolve_key(self, key):
        if isinstance(key, int):
            if key < 0:
                key = self.__len__() + key
            if key < 0 or key > self.__len__()-1:
                raise IndexError('array index {0} out of range (0, {1})'.format(key, self.__len__()-1))
            return self.steps and self.steps[key] or key
        if isinstance(key, slice):
            # first let's normalize slice start and stop to non-negative values
            # use slice as a list since slice attributes are readonly
            new_slice=[key.start, key.stop, key.step]
            if new_slice[0] is None:
                new_slice[0] = 0
            if new_slice[0] and new_slice[0] < 0:
                new_slice[0] = self.__len__()+new_slice[0]
            if new_slice[1] is None:
                new_slice[1] = self.__len__()
            if new_slice[1] and new_slice[1] < 0:
                new_slice[1] = self.__len__()+new_slice[1]
            # if limits are already set, let's absolutize supplied limits
            if self.limits is not None:
                if self.limits.start:
                    new_slice[0] = self.limits.start + new_slice[0]
                if self.limits.stop:
                    diff = self.limits.stop - new_slice[1]
                    new_slice[1] = new_slice[1] - diff
            # if steps are already set, let's transform them according to new slice
            new_steps = None
            if new_slice[2] and new_slice[2] > 1:
                if self.steps is not None:
                    current_steps = list(self.steps[new_slice[0]:new_slice[1]])
                    new_steps = current_steps[::new_slice[2]]
                else:
                    new_steps = xrange(new_slice[0], new_slice[1], new_slice[2])
            return (new_slice, new_steps or self.steps)
        raise TypeError('type of key is unrecognized')

    def _inst(self, key, vals=None):
        if vals is None:
            vals = self.get_f(*(self.const_args + [key]))
        args = list(self.instance_args)
        if not isinstance(vals, tuple): # let's not get fooled by other iterable types (like string)
            vals = (vals,)
        args.extend(vals)
        return self.cls(*args)

    # return length of actual items we are operating on
    def _real_length(self):
        return self.count_f(*self.const_args)
    
    def __delitem__(self, key):
        if self.delete_f is None:
            raise NotImplementedError('delete functionality is not implemented on this list')
        key = self._resolve_key(key)
        if isinstance(key, int):
            to_delete = (self.get_f(*(self.const_args + [key])),)
        elif isinstance(key, tuple):
            key_range = key[1]
            if not key_range:
                key_range = xrange(key[0][0] or 0, key[0][1] or self._real_length())
            to_delete = list()
            for i in key_range:
                to_delete.append(self.get_f(*(self.const_args + [i]))[-1])
        for item in to_delete:
            self.delete_f(*(self.const_args + [item]))

    # return length limited by self.limits and self.steps
    def __len__(self):
        if self.limits is not None:
            if self.steps is not None:
                return len(self.steps)
            return self.limits[1] - self.limits[0]
        return self._real_length()

    #def __iter__(self):
    #    pass

    def __getitem__(self, key):
        key = self._resolve_key(key)
        if isinstance(key, int):
            return self._inst(key)
        elif isinstance(key, tuple):
            clone = self.clone()
            clone.limits = slice(*key[0])
            clone.steps = key[1]
            return clone
            #msg(key) # FIXME: do clone() and _set_limits() on new instance, return new instance
            #if getattr(self.get_f, 'supports_slice', False):
            #    # forward to get function if it supports slices
            #    return [self._inst(-1, vals) for vals in self.get_f(*(self.const_args + [key]))]
            #ret = list()
            #for i in xrange(key.start or 0, key.stop or self.__len__(), key.step or 1):
            #    ret.append(self._inst(i))
            #return ret
        else:
            raise TypeError('key of type {0} is not supported'.format(type(key)))

    def __contains__(self, item):
        if self.limits is None:
            if getattr(self.contains_check, '__call__'):
                return self.contains_check(item)
            elif isinstance(self.contains_check, basestring):
                return bool(getattr(item, self.contains_check))
        # if no 'contains' check was provided or limits are set
        # then we have worst case scenario
        # and check every single record until we find it
        for obj in self:
            if obj == item:
                return True
        return False

# GenericTimelineLister: lazy binary search based iteration and indexing for (almost) any sorted time based lists in Reaper
class GenericTimelineLister(GenericLister):
    def __init__(self, pos_attr, *args, **kwargs):
        self.pos_attr = pos_attr
        super(GenericTimelineLister, self).__init__(*args, **kwargs)

    def _is_time(self, val): # FIXME: this should probably be extended and become a global function
        return isinstance(val, float) or isinstance(val, basestring)

    def _normalize_time(self, val): # FIXME: this should probably be extended and become a global function
        if isinstance(val, basestring):
            val = val # FIXME: convert to float representation
        return val

    def clone(self):
        return super(GenericTimelineLister, self).clone([self.pos_attr])

    def _bisect(self, key, comp_func):
        if self._is_time(key):
            key = self._normalize_time(key)
            # this search algorithm is equivalent to bisect_left or bisect_right (depending on comp_func)
            if key < 0:
                raise IndexError('time must be non-negative')
            lo = 0
            hi = self.__len__()
            while lo < hi:
                mid = (lo+hi)//2
                (lo, hi) = comp_func(lo, mid, hi)
            return lo
        return None

    def _get_left(self, key):
        def f(lo, mid, hi):
            if getattr(self[mid], self.pos_attr) < key: lo = mid+1
            else: hi = mid
            return (lo, hi)
        return self._bisect(key, f)

    def _get_right(self, key):
        def f(lo, mid, hi):
            if key < getattr(self[mid], self.pos_attr): hi = mid
            else: lo = mid+1
            return (lo, hi)
        return self._bisect(key, f)
    
    def __delitem__(self, key):
        # TODO: if key is in time formats, resolve it no int/slice!
        return super(GenericTimelineLister, self).__delitem__(key)

    def __getitem__(self, key):
        if self._is_time(key):
            return self[self._get_right(key)]
        if isinstance(key, slice):
            start_is_t = self._is_time(key.start)
            stop_is_t = self._is_time(key.stop)
            if start_is_t or stop_is_t:
                # convert slice start/stop to normal indexes
                new_slice = [key.start, key.stop, key.step] # slice attrs are readonly
                if start_is_t: new_slice[0] = self._get_right(new_slice[0])
                if stop_is_t: new_slice[1] = self._get_left(new_slice[1])
                key = slice(*new_slice)
                # continue to super().__getitem__
        return super(GenericTimelineLister, self).__getitem__(key)


class GenericObject(object):
    def __eq__(self, other):
        return type(self) == type(other) and self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)

class MarkerList(object):
    def __init__(self, project):
        self.project = project
        self._marker_map = None
        self._marker_store = None

    ### marker_type = 0 (all), 1 (simple), 2 (region)
    def _count_markers(self, marker_type=0):
        i = marker_type + 1 if marker_type > 0 else 0
        return RPR_CountProjectMarkers(self.project.id, 0, 0)[i]

    def build_from_reaper(self):
        if self._marker_store is None:
            self._marker_map = list()
            self._marker_store = dict()
        # the following code is pretty much the same as SWS MarkerList/MarkerListClass.cpp - MarkerList::BuildFromReaper()
        i = 0
        while i < self._count_markers():
            marker_data = [self.project]
            marker_data.extend(RPR_EnumProjectMarkers3(self.project.id, i, False, 0., 0., '', 0, 0))
            if i >= len(self._marker_map) or not self._marker_store[self._marker_map[i]].compare_by_val(*marker_data):
                # not found, try one more ahead
                if i+1 >= len(self._marker_map) or not self._marker_store[self._marker_map[i+1]].compare_by_val(*marker_data):
                    # not found, assume new and insert at current position
                    marker = ReaperMarker(*marker_data)
                    self._marker_map.insert(i, marker.internal_index)
                    self._marker_store[marker.internal_index] = marker
                else:
                    # found one ahead, the current one must have been deleted
                    del self._marker_store[self._marker_map[i]]
                    del self._marker_map[i]
            i += 1
        if i < len(self._marker_map):
            for d in range(i, len(self._marker_map)):
                del self._marker_store[self._marker_map[d]]
            del self._marker_map[i:]

    @property
    def marker_store(self):
        if self._marker_store is None:
            self.build_from_reaper()
        return self._marker_store

    @property
    def markers(self):
        pass     

    @property
    def regions(self):
        pass

    @property
    def markers_in_time(self):
        pass

    @property
    def regions_in_time(self):
        pass


class ReaperProject(GenericObject):
    def __init__(self, id=0):
        self.id = id

        track_in_prj = lambda t: t.project.id == id
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
        #elif isinstance(id, slice):
        #    indexes = range(id.start or 0, id.stop or self._count_markers(marker_type), id.step or 1)
        #    ret = list()
        #    for i in range(self._count_markers()):
        #        marker = RPR_EnumProjectMarkers3(self.id, i, False, 0., 0., '', 0, 0)
        #        if marker[7] == indexes[0] + 1 and (marker_type == 0 or marker[3] == marker_type - 1):
        #            del indexes[0]
        #            ret.append(marker)
        #        if len(indexes) == 0:
        #            break
        #    if len(indexes) > 0:
        #        raise IndexError()
        #    return ret
        else:
            raise TypeError()

    def create_marker(self, position, name, color=0, wantidx=-1):
        return ReaperMarker._create(self, False, position, 0., name, color, wantidx)

    def create_region(self, position, end, name, color=0, wantidx=-1):
        return ReaperMarker._create(self, True, position, end, name, color, wantidx)

    @property
    def cursor_position(self):
        return RPR_GetCursorPositionEx(self.id)

    @cursor_position.setter
    def cursor_position(self, value):
        if isinstance(value, float):
            value = (value, True, True)
        RPR_SetEditCurPos2(self.id, *value)

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
    def __init__(self, prj, global_index, blackhole, blackhole1, is_rgn, pos, pos_end, blackhole2, index, color, name=None):
        self.project = prj
        self.id = global_index - 1
        self.is_region = bool(is_rgn)
        self._pos = pos
        self._pos_end = pos_end
        self.index = index
        self.color = color
        self._name = name

    def __eq__(self, other):
        add_check = self.project == other.project
        return super(ReaperMarker, self).__eq__(other) and add_check

    @property
    def internal_index(self):
        return '{0}{1}'.format(self.index, 'r' if self.is_region else 'm')

    def compare_by_val(self, *args):
        pass

    @classmethod
    def _create(cls, project, is_rgn, position, end, name, color, wantidx):
        index = RPR_AddProjectMarker2(project.id, is_rgn, position, end, name, wantidx, color)
        if index == -1:
            raise Exception("Could not add marker")
        return cls(project, index, None, None, is_rgn, position, end, None, None, color, name) # FIXME: unable to get index (among markers of same type) at this point (search?)

    @property
    def name(self):
        if self._name is not None:
            return self._name
        if self.index is None:
            raise Exception("No index provided")
        fast_str = SNM_CreateFastString('')
        SNM_GetProjectMarkerName(self.project.id, self.index, self.is_region, fast_str)
        self._name = SNM_GetFastString(fast_str)
        SNM_DeleteFastString(fast_str)
        return self._name

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
        return super(ReaperMediaItem, self).__eq__(other) and add_check
    
    def delete(self):
        RPR_DeleteTrackMediaItem(self.track, self.id)

    def get_all_takes(self):
        takes = []
        num_takes = RPR_GetMediaItemNumTakes(self.id)
        for take in range(num_takes):
            takes.append(RPR_GetMediaItemTake(self.id, take))
        return takes
    
    @property
    def mute(self):
        return bool(RPR_GetMediaItemInfo_Value(self.id, 'B_MUTE'))

    @mute.setter
    def mute(self, b):
        RPR_SetMediaItemInfo_Value(self.id, 'B_MUTE', float(b))


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
        RPR_SetMediaItemSelected(self.id, int(value))



class ReaperFX(object):
    def __init__(self):
        pass



class ReaperTrack(GenericObject):
    def __init__(self, project, id):
        self.project = project
        self.id = id

        self.items = GenericTimelineLister('position', ReaperMediaItem, RPR_GetTrackNumMediaItems, lambda *args: (project, self, RPR_GetTrackMediaItem(*args)), [id]) # FIXME: contains?
        self.items.delete_f = RPR_DeleteTrackMediaItem

    def __eq__(self, other):
        add_check = self.project == other.project
        return add_check and super(ReaperTrack, self).__eq__(other)

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
        return bool(RPR_GetMediaTrackInfo_Value(self.id, 'B_MUTE'))

    @mute.setter
    def mute(self, b):
        RPR_SetMediaTrackInfo_Value(self.id, 'B_MUTE', float(b))


    #solo property
    @property
    def solo(self):
        #replace with GetMediaTrackInfo_Value
        flag = RPR_GetTrackState(self.id, 0)[2]
        return bool(flag & 16)

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
        return bool(RPR_GetMediaTrackInfo_Value(self.id, 'B_PHASE'))

    @phase_invert.setter
    def phase_invert(self, value):
        RPR_SetMediaTrackInfo_Value(self.id, 'B_PHASE', float(bool(value)))

    @property
    def record_monitor(self):
        return int(RPR_GetMediaTrackInfo_Value(self.id, 'I_RECMON'))

    @record_monitor.setter
    def record_monitor(self, value):
        RPR_SetMediaTrackInfo_Value(self.id, 'I_RECMON', value)


    @property
    def fx_enabled(self):
        return bool(RPR_GetMediaTrackInfo_Value(self.id, 'I_FXEN'))

    @fx_enabled.setter
    def fx_enabled(self, value):
        RPR_SetMediaTrackInfo_Value(self.id, 'I_FXEN', float(bool(value)))


    @property
    def record_arm(self):
        return bool(RPR_GetMediaTrackInfo_Value(self.id, 'I_RECARM'))

    @record_arm.setter
    def record_arm(self, value):
        RPR_SetMediaTrackInfo_Value(self.id, 'I_RECARM', float(bool(value)))


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
        return bool(RPR_IsTrackSelected(self.id))

    @selected.setter
    def selected(self, value):
        RPR_SetTrackSelected(self.id, int(bool(value)))
