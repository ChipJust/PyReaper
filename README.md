PyReaper
========

This project seeks to make a reasonable Pythonic wrapper to the Reaper API.

[ReaScript](http://www.reaper.fm/sdk/reascript/reascript.php)
To create Python modules with ReaScript functionality they must import the function bindings.

```python
from reaper_python import * 
```

A closer inspection of "C:\Program Files\REAPER (x64)\Plugins\reaper_python.py" (or similar path)
shows just what the Python bindings provided are giving us. Here is a sample:

```python
def RPR_AddMediaItemToTrack(p0):
  a=_ft['AddMediaItemToTrack']
  f=CFUNCTYPE(c_uint64,c_uint64)(a)
  t=(rpr_packp('MediaTrack*',p0),)
  r=f(t[0])
  return rpr_unpackp('MediaItem*',r)
```

All of the API bindings are done this way, some with a little string (re) processing.
This creates a very c-like set of functions to use in Python.

[Reaper Documentation](http://wiki.cockos.com/wiki/index.php/Reaper_Documentation)

[Reaper API Functions](http://wiki.cockos.com/wiki/index.php/REAPER_API_Functions)

[State Chunk Definitions](http://wiki.cockos.com/wiki/index.php/State_Chunk_Definitions) shows the format of the various data structures.

[API Examples](http://wiki.cockos.com/wiki/index.php/SeeAlsoTemplates) provides links, organized by category, to a pages for each function that have coding examples and some explainations for how to use each.
Not all of the functions have the information filled in, but it is a great refernce when the information is provided.

[Example Scripts](http://wiki.cockos.com/wiki/index.php/Python#Example_Scripts) provided on the Cockos wiki.
These Scripts have been added to this repo under the Examples folder.

# Credits
Started by [Brent Elliott](https://github.com/brentelliott)
