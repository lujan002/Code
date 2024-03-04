#include <PS4Controller.h>
#include <esp_bt_main.h>
#include <esp_bt_device.h>

void setup()
{
  Serial.begin(115200);
  PS4.begin();
  const uint8_t* address = esp_bt_dev_get_address();
  char str[100];
  sprintf(str, "ESP32's Bluetooth MAC address is - %02x:%02x:%02x:%02x:%02x:%02x", address[0],address[1],address[2],address[3],address[4],address[5]);
  Serial.println(str);
}

void loop()
{

}

// ets Jul 29 2019 12:21:46

// rst:0x1 (POWERON_RESET),boot:0x13 (SPI_FAST_FLASH_BOOT)
// configsip: 0, SPIWP:0xee
// clk_drv:0x00,q_drv:0x00,d_drv:0x00,cs0_drv:0x00,hd_drv:0x00,wp_drv:0x00
// mode:DIO, clock div:1
// load:0x3fff0030,len:1344
// load:0x40078000,len:13964
// load:0x40080400,len:3600
// entry 0x400805f0
// E (241) psram: PSRAM ID read error: 0xffffffff
// ESP32's Bluetooth MAC address is - d8:bc:38:e5:6f:12