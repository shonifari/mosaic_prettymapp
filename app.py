# import PIL
from typing import List
from prettymapp.geo import get_aoi
from prettymapp.osm import get_osm_geometries
from prettymapp.plotting import Plot
#from prettymapp.settings import STYLES
import os 

## GET COORDINATES
from math import cos, pi, sqrt
import subprocess

style = {
      "urban": {
        "cmap": [
          "#755a53",
          "#c77775",
          "#943434"
        ],
        "ec": "#2F3737",
        "lw": 0.5,
        "zorder": 5
      },
      "water": {
        "fc": "#a8e1e6",
        "ec": "#9bc3d4",
        "hatch_c": "#2F3737",
        "hatch": "ooo...",
        "lw": 1,
        "zorder": 3
      },
      "grassland": {
        "fc": "#8BB174",
        "ec": "#A7C497",
        "hatch": "ooo...",
        "hatch_c": "#2F3737",
        "lw": 1,
        "zorder": 1
      },
      "woodland": {
        "fc": "#64B96A",
        "ec": "#2F3737",
        "lw": 1,
        "zorder": 2
      },
      "streets": {
        "fc": "#2F3737",
        "zorder": 4,
        "ec": 475657
      },
      "other": {
        "fc": "#F2F4CB",
        "ec": "#2F3737",
        "lw": 1,
        "zorder": 3
      }
   
  }

def get_mosaic_coordinates(center_coords):
    # Calculate the coordinates of the 9 squares in the mosaic
    lat, lon = center_coords
    radius = 75 / 2 # in meters
    offsets = [-1, 0, 1]
    mosaic_coords = []
    for x_offset in offsets:
        for y_offset in offsets:
            mosaic_lat = lat + y_offset * (2 * radius / 1000) / (2 * sqrt(2))
            mosaic_lon = lon + x_offset * (2 * radius / 1000) / (2 * sqrt(2)) / cos(mosaic_lat * pi / 180)
            mosaic_coords.append((mosaic_lat, mosaic_lon))
    return mosaic_coords


def area_map(center_coordinates : List[float], location_name: str):
  
    # Get the coordinates of the 9 squares in the mosaic and create a map for each
    for i,coordinates in enumerate(get_mosaic_coordinates(center_coordinates)):

        print("\n\n", coordinates, "\n\n")

        # Get the area of interest (AOI) and the OSM geometries within it
        aoi = get_aoi(coordinates=coordinates, radius=1500, rectangular=True)
        # Extract the OSM geometries within the AOI to a GeoDataFrame
        df = get_osm_geometries(aoi=aoi)
        
        # Plot the map
        fig = Plot(
          df=df,
          aoi_bounds=aoi.bounds,
          draw_settings=style, # <-- use the custom style
          name_on= False,
          name= "",
          font_size= 27,
          font_color= "#2F3737",
          text_x= 0,
          text_y= -33,
          text_rotation= 0,
          shape= "rectangle",
          contour_width= 0,
          contour_color= "#2F3737",
          bg_shape= "rectangle",
          bg_buffer= 0,
          bg_color= "#EDEFDA"
        ).plot_all()    

        fig.savefig(f"{i}.jpg")    
    
    # Create the mosaic
    for i in range(0,9):
        cmd = (
        f"ffmpeg -y "
        f"-i \'{i}.jpg\' "
        f"-vf \"crop=in_w-83-75:in_h-57-57,scale=4083:4096,crop=in_w-55:in_h-68:0:0\" output{i}.jpg"
    )
        subprocess.run(cmd, shell=True)


    inputs = " ".join([ f"-i output{i}.jpg " for i in range(0,9)])
    
    cmd = (
    f"ffmpeg -y "
    f"{inputs}"
    f"-filter_complex \""
    f"[2:v][1:v][0:v]vstack=3[left];[5:v][4:v][3:v]vstack=3[middle];[8:v][7:v][6:v]vstack=3[right];[left][middle][right]hstack=3\" "
    f" '{location_name}'.jpg"
    )

    
    # Delete the temporary files
    for i in range(0,9):
      os.remove(f"{i}.jpg")  
    
    subprocess.run(cmd, shell=True)

 





london = [51.51234565151722, -0.09066730134071557]
area_map(london,"London")