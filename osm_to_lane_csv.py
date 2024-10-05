#! /usr/bin/env python3

from typing import List, Dict
import os
import pandas as pd
import xml.etree.ElementTree as ET

def extract_ways_from_osm(osm_path: str) -> Dict[str, pd.DataFrame]:
  print("loading osm from: ", osm_path)
  tree = ET.parse(osm_path)
  root = tree.getroot()

  ways_info = {member.attrib["role"]: member.attrib["ref"] for member in root.findall(".//relation/member")}
  print("ways: ", ways_info)

  # ノードIDをキーにlocal_x, local_y, eleを格納する辞書を作成
  nodes = {}
  for node in root.findall(".//node"):
      node_id = node.attrib['id']
      local_x = node.find("tag[@k='local_x']").attrib['v']
      local_y = node.find("tag[@k='local_y']").attrib['v']
      ele = node.find("tag[@k='ele']").attrib['v']
      nodes[node_id] = {'local_x': local_x, 'local_y': local_y, 'ele': ele}

  # # way内のnd参照から、対応するノードのx, y, zを取り出す
  ways = {}
  for role, way_id in ways_info.items():
      way_nodes = []
      for way in root.findall(".//way[@id='" + way_id + "']"):
          for nd in way.findall("nd"):
              ref_id = nd.attrib['ref']
              if ref_id in nodes:
                  way_nodes.append([nodes[ref_id]['local_x'], nodes[ref_id]['local_y'], nodes[ref_id]['ele']])
      ways[role] = way_nodes

  # データフレームに変換
  dfs = {}
  for role, way_nodes in ways.items():
      dfs[role] = pd.DataFrame(way_nodes, columns=['x', 'y', 'z'])

  return dfs

def write_csv(dfs: Dict[str, pd.DataFrame]):
  for role, df in dfs.items():
    output_path = os.path.join("./" + role + "_lane_bound.csv")
    df.to_csv(output_path, index=False)

if __name__ == '__main__':
  this_dir = os.path.dirname(os.path.abspath(__file__))
  osm_path = this_dir + "/resources/osm/city_circuit_lanelet2_roborovsky.osm"
  dfs = extract_ways_from_osm(osm_path)
  write_csv(dfs)