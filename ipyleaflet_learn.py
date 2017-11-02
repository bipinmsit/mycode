!pip install ipyleaflet

!jupyter nbextension enable --py --sys-prefix ipyleaflet

from ipyleaflet import (Map, DrawControl)
myMap=Map(center=[32.7766, -96.789], zoom=10)
dc=DrawControl(circle={'shapeOptions':{'color':'#0000FF'}},rectangle={'shapeOptions':{'color':'#0000FF'}})
myMap.add_control(dc)

myMap
