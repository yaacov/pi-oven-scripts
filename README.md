# pi-oven-scripts

Raspberry PI scripts used for home oven control. 

## Prototype images

![Oven automation prototype](/img/open-pi.jpg?raw=true "Oven automation prototype")


![Oven automation prototype](/img/node-red.jpg?raw=true "Oven automation prototype")

## Oven API examples

``` bash
curl -s "http://oven:5000/status" | jq
```

``` json
{
  "back": false,
  "bottom": false,
  "cooling": false,
  "fan": false,
  "light": true,
  "set_back": false,
  "set_bottom": false,
  "set_fan": false,
  "set_light": true,
  "set_temp": 180,
  "set_top": false,
  "temp": 21,
  "top": false
}
```

``` bash
curl -s "http://oven:5000/set?temp=180" | jq
```

``` json
{
  "back": false,
  "bottom": false,
  "cooling": false,
  "fan": false,
  "light": true,
  "set_back": false,
  "set_bottom": false,
  "set_fan": false,
  "set_light": true,
  "set_temp": 180,
  "set_top": false,
  "temp": 21,
  "top": false
}
```

``` bash
curl -s "http://oven:5000/set?light=on" | jq
```

``` json
{
  "back": false,
  "bottom": false,
  "cooling": false,
  "fan": false,
  "light": true,
  "set_back": false,
  "set_bottom": false,
  "set_fan": false,
  "set_light": true,
  "set_temp": 180,
  "set_top": false,
  "temp": 20,
  "top": false
}
```

``` bash
curl -s http://oven:5000/metrics | sort
```
```
back 0.0
bottom 0.0
cooling 0.0
fan 0.0
light 0.0
set_back 0.0
set_bottom 0.0
set_fan 0.0
set_light 0.0
set_temp 0.0
set_top 0.0
temp 25.0
timer 0.0
timer_left 0.0
timer_minutes 0.0
timer_start 1552054754.0
top 0.0
```
