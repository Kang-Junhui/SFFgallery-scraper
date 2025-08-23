#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

#include "EPD_3in5g.h"
#include "GUI_Paint.h"
#include "fonts.h"

const char* ssid = "wifi_name";
const char* password = "wifi_psw";
const char* server = "http://host_ip:port/";
const long refreshInterval = 5 * 60 * 1000;

unsigned long lastUpdateTime = 0;

const int rowHeight = 35;
const int colTagWidth = 40;
const int colTitleWidth = 270;
const int colDateWidth = 70;
const int startX = 1;
const int startY = 1;
const int numRows = 5;

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(500);
  }
  Serial.println("Connected to WiFi");

  DEV_Module_Init();
  EPD_3IN5G_Init();
  EPD_3IN5G_Clear(EPD_3IN5G_WHITE);
  
  updateFromServer();
  updateAndDisplay();
}

void loop() {
  if (millis() - lastUpdateTime > refreshInterval) {
    updateFromServer();
    updateAndDisplay();
    lastUpdateTime = millis();
  }
}

void updateFromServer() {
  HTTPClient http;
  http.begin(String(server) + "/update?mode=hotdeal");
  int httpCode = http.GET();
  http.end();
}

void drawGrid() {
  for (int i = 0; i <= numRows; i++) {
    int y = startY + i * rowHeight;
    Paint_DrawLine(startX, y, startX + colTagWidth + colTitleWidth + colDateWidth, y,
                   EPD_3IN5G_BLACK, DOT_PIXEL_1X1, LINE_STYLE_SOLID);
  }
  
  Paint_DrawLine(startX + colTagWidth, startY, startX + colTagWidth, startY + rowHeight * numRows,
                 EPD_3IN5G_BLACK, DOT_PIXEL_1X1, LINE_STYLE_SOLID);
  Paint_DrawLine(startX + colTagWidth + colTitleWidth, startY,
                 startX + colTagWidth + colTitleWidth, startY + rowHeight * numRows,
                 EPD_3IN5G_BLACK, DOT_PIXEL_1X1, LINE_STYLE_SOLID);

  Paint_DrawRectangle(startX, startY, startX + colTagWidth + colTitleWidth + colDateWidth,
                      startY + rowHeight * numRows, EPD_3IN5G_BLACK, DOT_PIXEL_1X1, DRAW_FILL_EMPTY);
}

void updateAndDisplay() {
  HTTPClient http;
  http.begin(String(server) + "/?mode=hotdeal");
  int httpCode = http.GET();

  if (httpCode == 200) {
    String payload = http.getString();
    StaticJsonDocument<2048> doc;
    DeserializationError err = deserializeJson(doc, payload);
    if (err) {
      Serial.println("JSON parse failed");
      return;
    }

    UBYTE* image = (UBYTE*)malloc(EPD_3IN5G_WIDTH * EPD_3IN5G_HEIGHT / 2); // 4-color용
    Paint_NewImage(image, EPD_3IN5G_WIDTH, EPD_3IN5G_HEIGHT, 90, EPD_3IN5G_WHITE);
    Paint_SetScale(4);
    Paint_Clear(EPD_3IN5G_WHITE);
    Paint_SelectImage(image);
    Paint_SetRotate(ROTATE_90);

    for (int i = 0; i < doc.size() && i < numRows; i++) {
      String tag = doc[i]["tag"].as<String>();
      String title = doc[i]["title"].as<String>();
      String date = doc[i]["date"].as<String>().substring(11, 16); // MM-dd hh:mm

      int y = startY + i * rowHeight + 6;

      Paint_DrawString_CN(startX + 5, y, tag.c_str(), &Font16CN, EPD_3IN5G_BLACK, EPD_3IN5G_WHITE);
      Paint_DrawString_CN(startX + colTagWidth + 5, y, title.c_str(), &Font16CN, EPD_3IN5G_BLACK, EPD_3IN5G_WHITE);
      Paint_DrawString_CN(startX + colTagWidth + colTitleWidth + 5, y + 2, date.c_str(), &Font16CN, EPD_3IN5G_BLACK, EPD_3IN5G_WHITE);
    }

    drawGrid();

    EPD_3IN5G_Display(image);
    free(image);
  }

  http.end();
}
