#! /usr/bin/env python3

from typing import Dict
import os
import argparse
import pandas as pd
import xml.etree.ElementTree as ET


def extract_ways_from_osm(osm_path: str) -> Dict[str, pd.DataFrame]:
  print("loading osm from: ", osm_path)
  tree = ET.parse(osm_path)
  root = tree.getroot()

  ways_info = {member.attrib["role"]: member.attrib["ref"] for member in root.findall(".//relation/member")}

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

def write_csv(dfs: Dict[str, pd.DataFrame], directory: str):
  for role, df in dfs.items():
    output_path = os.path.join(directory + "/" + role + "_lane_bound.csv")
    df.to_csv(output_path, index=False)

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("osm_filename", help="osm file name in resources/osm")
  args = parser.parse_args()

  this_dir = os.path.dirname(os.path.abspath(__file__))
  osm_path = this_dir + "/../resources/osm/" + args.osm_filename
  dfs = extract_ways_from_osm(osm_path)

  # resources/bounds/args.osm_filename が存在しない場合は生成
  bounds_dir = this_dir + "/../resources/bounds/" + args.osm_filename.split(".")[0]
  if not os.path.exists(bounds_dir):
    os.makedirs(bounds_dir)
  write_csv(dfs, bounds_dir)