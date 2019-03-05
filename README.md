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
curl -s "http://oven:5000/set?dev=temp&value=180" | jq
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
curl -s "http://oven:5000/set?dev=light&value=on" | jq
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
