# noodle
noodle is an iperf-like network test - client-server tool.

with noodle, unlike iperf, you can control:

1. number of threads in both the client ad server
2. connections per threads
3. connection life time
4. bandwidth per connection
5. ramp up in conns/sec


Build:

g++ noodle.cpp -l pthread -o noodle

Example simple run:

server side:

> noodle -s

client side(10 connections, ramp up at 2 connections per second, 20 kbit per connection, never ends):

> noodle -c server_address -C 10 -n 2 -b 20
