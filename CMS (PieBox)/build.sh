#!/bin/sh
# build.sh
# Build PieBox

python3 -m compileall *.py
cd __pycache__

mv action.cpython-34.pyc action.pyc
mv analytics.cpython-34.pyc analytics.pyc
mv baker.cpython-34.pyc baker.pyc
mv content.cpython-34.pyc content.pyc
mv datastore.cpython-34.pyc datastore.pyc
mv delivery.cpython-34.pyc delivery.pyc
mv gpiocontroller.cpython-34.pyc gpiocontroller.pyc
mv link.cpython-34.pyc link.pyc
mv main.cpython-34.pyc main.pyc
mv office.cpython-34.pyc office.pyc
mv order.cpython-34.pyc order.pyc
mv playlist.cpython-34.pyc playlist.pyc
mv sandtimer.cpython-34.pyc sandtimer.pyc
mv sequence.cpython-34.pyc sequence.pyc
mv settings.cpython-34.pyc settings.pyc
mv trigger.cpython-34.pyc trigger.pyc
mv videoplayer.cpython-34.pyc videoplayer.pyc

rm *.cpython-34.pyc
