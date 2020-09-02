# rpiTemperatureSensorsBle
Code for an python app which gathers temperature readings from BLE xiaomi miija and ruuvitag sensors and send them to azure iot hub. The idea is to run it as a root using cron.

Credits:<br/>
DeviceClient.py comes from https://github.com/bechynsky/AzureIoTDeviceClientPY<br/>
LYWSD03MMC.py comes from https://github.com/JsBergbau/MiTemperature2

To complete the solution it could be used in conjunction with azure function which pushes iot hub messages to cosmos db: https://github.com/mjazwiecki/tempReadingToCosmosDb
