ELV PCA 301

The elvpca switch platform allows you to control the state of your ELV PCA 301 smart switch and tranfer data of power and energy consumption to MQTT (topic elvpca).  

Add the following entry in your configuration.yaml:

```yaml
elvpca:
  device: serial port
  host: url of MQTT
  port: 1883
  username: username of MQTT
  password: password of MQTT
```
