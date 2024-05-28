Bot který funguje ve hře Albion Online


Dělá screenshoty a detekuje objekty na obrazovce a pokud najde shodu a ta je vyhodnocena jako další akce tak tam přesune kuryor a klikne nebo podrží tlačítko 'a'


Program používa YOLO v8 jako Ai a best(1).pt můj vlastní vztrénovaný model k detekci objektů 



Chtěl Jsem vztvořit Bota který by za mě grindil MMO hru
1) DataSet creation (Program Albion/GetData took screenshots while I played the game)
2) I used Roboflow for Dataset Managment
3) I trained the costume Yolo V8 model (bets(1).pt)
4) Made the code that uses the Yolo model to detects stuff on live screenshots made with pyautogui
5) Made the decision logick on where to click and what to do


   
Code obsaen pouze v Albion_Bot.py
Image_predict vám ukáže co vydí program na screenshotu musí se jmenovat test2.png
GetData dělá a ukládá screenshoty obrayovky 1
