# noodle
noodle is a network test client-server program.

with noodle, unlike iperf, you can control:

1. number of threads
2. connections per threads
3. connection life time
4. bandwidth per connection
5. ramp up in conns/sec

Build:
g++ noodle.cpp -l pthread -o noodle

Example simple run:
server side:
noodle -s
client side(10 connections rampup at 2 connections per second at 20 kbit per connection never ends)
noodle -c server_address -C 10 -n 2 -b 20
