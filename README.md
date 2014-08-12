pyGlances-Pushover
==================

If Idle_CPU or Idle_RAM is under 20%, notify on Pushover


Requirements
-------

Python-Glances:target: https://github.com/nicolargo/glances
Get Archive file or install using command-line
Debian or Ubuntu : ``apt-get install python-glances``
python : ``pip install glances`` or ``easy_install glances``

Pushover:target:https://pushover.net


Usage
-----

1. Run glances
``glances -s -p <port> (-B <Bind Address>)``
2. Run this script 
``sudo python main.py``