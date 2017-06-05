#!/usr/bin/python
# -*- coding: utf8 -*-

#
# cocos2d
# http://python.cocos2d.org
#

from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

import cocos, pyglet
from cocos.sprite import Sprite


class HelloWorld(cocos.layer.Layer):

    def __init__(self):
        super(HelloWorld, self).__init__()

        # a cocos.text.Label is a wrapper of pyglet.text.Label
        # with the benefit of being a cocosnode
        label = cocos.text.Label('Hello, World!',
                                 font_name='Times New Roman',
                                 font_size=32,
                                 anchor_x='center', anchor_y='center')

        label.position = 320, 240
        self.add(label)

        city_image = pyglet.resource.image('imgs/city.png')
        city_sprite = Sprite(city_image)
        city_sprite.position = 960/2,540/2
        self.add(city_sprite)

        cout_bg_image = pyglet.resource.image('imgs/city.png')
        city_sprite = Sprite(city_image)
        city_sprite.position = 960/2,540/2
        self.add(city_sprite)


if __name__ == "__main__":
    # director init takes the same arguments as pyglet.window
    cocos.director.director.init(width=960, height=540)

    # We create a new layer, an instance of HelloWorld
    hello_layer = HelloWorld()

    # A scene that contains the layer hello_layer
    main_scene = cocos.scene.Scene(hello_layer)

    # And now, start the application, starting with main_scene
    cocos.director.director.run(main_scene)

    # or you could have written, without so many comments:
    #      director.run( cocos.scene.Scene( HelloWorld() ) )
