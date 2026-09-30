#!/usr/bin/env python3
#coding=utf-8

from flask import Flask, request, Response

from spotify_background_color import SpotifyBackgroundColor

import json
import numpy as np
from io import BytesIO
import urllib.request
from PIL import Image
import traceback

app = Flask(__name__)

@app.route('/background_color', methods=['POST'])
def index():
    try:
        content = request.get_json(silent=True)
        image_url = content['image_url']
        
        size = (200, 200)
        
        k_means = 8
        color_tol = 2
        
        if 'image_processing_width' in content and 'image_processing_height' in content:
          size = (content['image_processing_width'], content['image_processing_height'])
          
        if 'k_means' in content:
          k_means = int(content['k_means'])
          
        if 'color_tolerance' in content:
          color_tol = int(content['color_tolerance'])
        
        image_bytes = BytesIO(urllib.request.urlopen(image_url).read())
        
        img = Image.open(image_bytes)
        
        if img.mode != "RGB":
            img = img.convert('RGB')
        
        image = np.array(img)
        
        background_color = SpotifyBackgroundColor(
            img=image, image_processing_size=size)
        
        r, g, b = background_color.best_color(
            k=k_means, color_tol=color_tol)
        
        color =    {
          "r": int(round(r)),
          "g": int(round(g)),
          "b": int(round(b))
        }
        
        color_json = json.dumps(color)
        
        return Response(color_json, status=200, mimetype='application/json')
    except Exception as err:
        return Response(json.dumps({"error": str(err), "stacktrace": traceback.format_exc()}), status=500, mimetype='application/json')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)