#include <TFT_eSPI.h>  

TFT_eSPI tft = TFT_eSPI();  

#include "arduino_little_endian.h"  // File header yang berisi array gambar

void setup() {  
    tft.init();  
    tft.setRotation(3);  
    tft.pushImage(0, 0, arduino_WIDTH, arduino_HEIGHT, arduino_data);  
}  

void loop() {  
    // Tidak ada loop karena gambar hanya ditampilkan sekali
}
