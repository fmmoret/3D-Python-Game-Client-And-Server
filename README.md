# 3D-Python-Game-Client-And-Server
This repo includes the code for the start of an online, multiplayer, 3d game.

Built in python 2.7.

Requires Panda3D to be installed on the machine. https://www.panda3d.org/download.php?sdk&version=1.9.4

It uses Panda3D for rendering the scene, collision detection, and capturing inputs.
It runs on TCP, does not yet have client prediction / lag compensation.
No GUI implemented yet.

**Start the server by running run_server.sh from the project root.
Start a client by running run_client.sh from the project root.
A match starts for every 2 clients started.**

![Screenshot](/README_Resources/screenshot.png?raw=true "2 clients + server in debug mode")

**Client/**

Player.py has objects for maintaining state of all projectiles / spells / players.

MatchWorld.py has all code for setting up and manipulating the 3D environment.

MatchClient.py accepts messages from the server and sends messages to the server. 
Upon getting messages, it updates states of in-game objects.

ClientNetworking.py defines messages that the client will send and receive.

**Server/**

Player.py has objects for maintaining state of all projectiles / spells / players.
It also detects collisions between objects.

MatchWorld.py is used for map-object collisions and testing line-of-sight.
It renders the scene when in debug mode.

Match.py represents a single match and is used for accepting messages from clients and sending messages to clients.

MatchServer.py queues client connections up and assigns pairs to Match instances.

ServerNetworking.py defines messages that the server will send and receive.

**********
It has no lag compensation built in.
This can be tested by running Test/lag_localhost.sh with a number like "50" for 50ms of lag.
Clear the lag by running Test/clearlag_localhost.sh.

The intent was to use a headless browser for the GUI; starter code for this is in Client/uitest.py that was copied from the example here https://gist.github.com/croxis/9789973.
I'd recommend using something else for the GUI; in my tests, the browser is very heavy.
