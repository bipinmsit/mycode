import xml.etree.ElementTree as ET
import pandas as pd
# Reading XML File and getting root of tree
tree = ET.parse("./samethanahalli-markers.xml")
root = tree.getroot()

"""
XML Structure
======================
root
  ->chunk[0]
    ->sensors[0]
    ->cameras[1]
      ->camera[0...C] <id, label>
    ->markers[2]
      ->marker[0...M] <id, label>
        ->reference[0] <x, y, z, enabled>
    ->frames[3]
      ->frame[0]
        ->markers[0]
          ->marker[0...M] <marker_id>
            ->location[0...PM] <camera_id, x, y, pinned>


=========================

C -> Total Number of Cameras
M -> Total Number of Markers
PM -> Total Number of Projections per marker

"""
chunk = root[0]
cameras = chunk[1]
markers = chunk[2]
camera_dict = {}
marker_dict = {}

for camera in cameras:
    camera_dict[camera.attrib['id']] = camera.attrib['label']

for marker in markers:
    marker_dict[marker.attrib['id']] = marker[0].attrib

frame_markers = chunk[3][0][0]
for marker in frame_markers:
    m_id = marker.attrib['marker_id']
    marker_dict[m_id]['cameras'] = {}
    for location in marker:
        if location.attrib['pinned'] == 'true':
            c_id = location.attrib['camera_id']
            marker_dict[m_id]['cameras'][c_id] = location.attrib
            marker_dict[m_id]['cameras'][c_id]['camera_label'] = camera_dict[c_id]

# Saving to CSV
marker_keys = marker_dict.keys()
marker_keys = sorted([int(val) for val in marker_keys])
col_headers = ['camera_label', 'marker_label', 'px_x', 'px_y', 'world_x', 'world_y', 'altitude']
csv_list = [] 
m_idx = 0
for key in marker_keys:
    m_idx += 1
    if marker_dict[str(key)]['enabled'] =='true':
        wx = marker_dict[str(key)]['x']
        wy = marker_dict[str(key)]['y']
        wz = marker_dict[str(key)]['z']
        m_label = "GCP" + str(m_idx)
        m_cameras = marker_dict[str(key)]['cameras']
        for camera in m_cameras.keys():
            proj_list = [m_cameras[camera]['camera_label'], m_label, m_cameras[camera]['x'], 
                         m_cameras[camera]['y'], wx, wy, wz]
            csv_list +=  [proj_list]

pd.DataFrame(csv_list, columns=col_headers).to_csv('./test_out.csv', index=False)



    
    
