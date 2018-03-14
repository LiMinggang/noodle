# noodle
noodle is a C10K/M network client server testing tool helping test and demonstrate many sessions with relatively low effort of configuration.

With noodle, you can run tens to hundreds thousands tcp/usp connections while controling:

number of threads in both the client ad server
connections per threads
connection life time
bandwidth per connection
ramp up in conns/sec
ip addresses and port numbers
Build:

g++ noodle.cpp -l pthread -o noodle

Example simple run:

server side:

> noodle -s

client side(10 connections, ramp up at 2 connections per second, 20 kbit per connection, never ends):

> noodle -c server_address -C 10 -n 2 -b 20
