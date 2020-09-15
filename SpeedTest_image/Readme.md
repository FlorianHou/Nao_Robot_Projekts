# ImageSpeedTest 
## YUV oder BGR:
Bei Nao ist YUV in 422(YUYV) Format. Das bedeutet, dass jeden 2 Pixels durch 4 Intergers(8bit, 0-255) beschrieben werden. Bei BGR ist jede Pixel brauche 3 Integers(8bit, 0-255[B,G,R]), deshalb jeden 2 Pixels 6 Ingegers brauche. Yuv sollte schnell als BGR.


## Geräte:
+ Router : CISCO WAP121
+ Rechner : ThinPadT420
    - Wifi: Intel Corporation Centrino Advanced-N 6205
    - Lan: Intel Corporation 82579LM Gigabit Network Connection
+ Robot Nao V6

## Vorbereiten:
+ Pose Init
+ Autonomous Aus
```
try:
    app = qi.Application(url="tcp://10.0.147.226:9559")
    # app = qi.Application(url="tcp://10.0.147.226:9559")
except RuntimeError:
    print"error!!"
    sys.exit(1)
app.start()
session = app.session
motion = session.service("ALMotion")
pose = session.service("ALRobotPosture")
pose.goToPosture("Stand", 0.5)
autonomous_service = session.service("ALAutonomousLife")
autonomous_service.setState("disabled")
motion.rest()
```
## Format:
+ Yuv(Nur "Y", SW) -- 0
+ YUV -- 9
+ BGR -- 13  
+ [mehr Info](http://doc.aldebaran.com/2-8/family/nao_technical/video_naov6.html#naov6-video)

## Erklärung:
+ Yuv: nehme Bild in Y Format auf.
+ YUV: nehme Bild in YUV Format auf, dann übersetzt zu BGR mit OpenCV
+ BGR: nehme Bild in BGR Format auf.

## Auflösung(Res):
|Auflösung: |Nr.    |Pixel      |
|---        |---    |---        |
|AL::k16VGA | 	4 	|2560x1920px|
|AL::k4VGA  | 	3  	|1280x960px |
|AL::kVGA   | 	2	|640x480px  |
|AL::kQVGA  | 	1 	|320x240px  |
|AL::       | 	0 	|160x120px  |

## Datei aus Nao Robot zu OpenCV umwandelt:
Datei aus Nao ist ein 1D Binary Array, müssen wir die Datei aufladen, dann umformen, um die an BGR anzupassen.
### Kern Programm:
+ Yuv(Gray):
```
ColorSpace = 0

    contain = video_cam.getImageRemote(nameId)
    img_buffer = np.frombuffer(contain[6], np.uint8)
    img_Yuv = img_buffer.reshape(contain[1],contain[0],-1)
```
+ YUV2BGR:
```
ColorSpace = 13

    contain = video_cam.getImageRemote(nameId)
    img_buffer = np.frombuffer(contain[6], np.uint8)
    img_YUV = img_buffer.reshape(contain[1],contain[0],-1)
    img_BGR = cv.cvtColor(img_YUV, cv.COLOR_YUV2BGR_YUYV)
```
+ BGR:
```
ColorSpace = 9

    contain = video_cam.getImageRemote(nameId)
    img_buffer = np.frombuffer(contain[6], np.uint8)
    img_BGR = img_buffer.reshape(contain[1],contain[0],-1)
```


## Ergebnis:

Einheit: Sekunde
| WIFI      |       |                                  |                | Lan            |     |       |                                  |                |
|-----------|-------|----------------------------------|----------------|----------------|-----|-------|----------------------------------|----------------|
|           |       |                                  |                |                |     |       |                                  |                |
| Yuv\(SW\) |       |                                  |                |                |     |       |                                  |                |
|           | Res   | Round                            | Delta\_t       | Zeit Per Frame | Res | Round | Delta\_t                         | Zeit Per Frame |
| 0         | 0     | 1\.9999620914                    | 0\.066665403   |                | 0   | 0     | 1\.9973220825                    | 0\.0665774028  |
| 0         | 1     | 1\.9991760254                    | 0\.0666392008  |                | 0   | 1     | 1\.9998221397                    | 0\.066660738   |
| 0         | 2     | 1\.9915120602                    | 0\.0663837353  |                | 0   | 2     | 1\.9982769489                    | 0\.0666092316  |
|           |       | durchschnittliche Zeit per frame | 0\.0665627797  |                |     |       | durchschnittliche Zeit per frame | 0\.0666157908  |
| 1         | 0     | 3\.9935028553                    | 0\.1331167618  |                | 1   | 0     | 1\.9975938797                    | 0\.0665864627  |
| 1         | 1     | 3\.9994549751                    | 0\.1333151658  |                | 1   | 1     | 1\.9983358383                    | 0\.0666111946  |
| 1         | 2     | 3\.9824690819                    | 0\.1327489694  |                | 1   | 2     | 1\.9986610413                    | 0\.0666220347  |
|           |       | durchschnittliche Zeit per frame | 0\.133060299   |                |     |       | durchschnittliche Zeit per frame | 0\.066606564   |
| 2         | 0     | 7\.2662858963                    | 0\.2422095299  |                | 2   | 0     | 1\.995661974                     | 0\.0665220658  |
| 2         | 1     | 6\.7480528355                    | 0\.2249350945  |                | 2   | 1     | 1\.9985570908                    | 0\.0666185697  |
| 2         | 2     | 6\.2563800812                    | 0\.2085460027  |                | 2   | 2     | 1\.9989290237                    | 0\.0666309675  |
|           |       | durchschnittliche Zeit per frame | 0\.225230209   |                |     |       | durchschnittliche Zeit per frame | 0\.0665905343  |
| 3         | 0     | 19\.7266030312                   | 0\.6575534344  |                | 3   | 0     | 2\.7253592014                    | 0\.0908453067  |
| 3         | 1     | 21\.5990209579                   | 0\.7199673653  |                | 3   | 1     | 2\.3231210709                    | 0\.077437369   |
| 3         | 2     | 22\.8330059052                   | 0\.7611001968  |                | 3   | 2     | 2\.2000570297                    | 0\.0733352343  |
|           |       | durchschnittliche Zeit per frame | 0\.7128736655  |                |     |       | durchschnittliche Zeit per frame | 0\.0805393034  |
| 4         | 0     | 77\.050205946                    | 2\.5683401982  |                | 4   | 0     | 3\.9979548454                    | 0\.1332651615  |
| 4         | 1     | 78\.0581359863                   | 2\.6019378662  |                | 4   | 1     | 4\.0004181862                    | 0\.1333472729  |
| 4         | 2     | 83\.4551749229                   | 2\.7818391641  |                | 4   | 2     | 4\.0045530796                    | 0\.1334851027  |
|           |       | durchschnittliche Zeit per frame | 2\.6507057428  |                |     |       | durchschnittliche Zeit per frame | 0\.1333658457  |
|           |       |                                  |                |                |     |       |                                  |                |
| BGR2BGR   |       |                                  |                |                |     |       |                                  |                |
| Res       | Round | Delta\_t                         | Zeit Per Frame |                | Res | Round | Delta\_t                         | Zeit Per Frame |
| 0         | 0     | 4\.1744689941                    | 0\.1391489665  |                | 0   | 0     | 1\.9996368885                    | 0\.066654563   |
| 0         | 1     | 3\.9316089153                    | 0\.1310536305  |                | 0   | 1     | 1\.9991221428                    | 0\.0666374048  |
| 0         | 2     | 4\.1184010506                    | 0\.137280035   |                | 0   | 2     | 1\.996612072                     | 0\.0665537357  |
|           |       | durchschnittliche Zeit per frame | 0\.135827544   |                |     |       | durchschnittliche Zeit per frame | 0\.0666152345  |
| 1         | 0     | 7\.4055809975                    | 0\.2468526999  |                | 1   | 0     | 1\.9989459515                    | 0\.0666315317  |
| 1         | 1     | 5\.9699139595                    | 0\.198997132   |                | 1   | 1     | 2\.0019419193                    | 0\.0667313973  |
| 1         | 2     | 5\.8499109745                    | 0\.1949970325  |                | 1   | 2     | 1\.9986639023                    | 0\.0666221301  |
|           |       | durchschnittliche Zeit per frame | 0\.2136156215  |                |     |       | durchschnittliche Zeit per frame | 0\.0666616864  |
| 2         | 0     | 18\.1960220337                   | 0\.6065340678  |                | 2   | 0     | 2\.064925909                     | 0\.0688308636  |
| 2         | 1     | 19\.1248290539                   | 0\.6374943018  |                | 2   | 1     | 1\.9983959198                    | 0\.0666131973  |
| 2         | 2     | 16\.0467541218                   | 0\.5348918041  |                | 2   | 2     | 2\.0599758625                    | 0\.0686658621  |
|           |       | durchschnittliche Zeit per frame | 0\.5929733912  |                |     |       | durchschnittliche Zeit per frame | 0\.068036641   |
| 3         | 0     | 67\.2272789478                   | 2\.2409092983  |                | 3   | 0     | 3\.993584156                     | 0\.1331194719  |
| 3         | 1     | 62\.2081189156                   | 2\.0736039639  |                | 3   | 1     | 3\.9961731434                    | 0\.1332057714  |
| 3         | 2     | 72\.7040500641                   | 2\.4234683355  |                | 3   | 2     | 4\.0095999241                    | 0\.1336533308  |
|           |       | durchschnittliche Zeit per frame | 2\.2459938659  |                |     |       | durchschnittliche Zeit per frame | 0\.1333261914  |
| 4         | 0     | 360\.8255310059                  | 12\.0275177002 |                | 4   | 0     | 10\.3315241337                   | 0\.3443841378  |
| 4         | 1     | 247\.9834220409                  | 8\.266114068   |                | 4   | 1     | 10\.0851240158                   | 0\.3361708005  |
| 4         | 2     | 243\.8167498112                  | 8\.1272249937  |                | 4   | 2     | 10\.0545260906                   | 0\.3351508697  |
|           |       | durchschnittliche Zeit per frame | 9\.4736189206  |                |     |       | durchschnittliche Zeit per frame | 0\.3385686027  |
|           |       |                                  |                |                |     |       |                                  |                |
|           |       |                                  |                |                |     |       |                                  |                |
| YUV2BGR   |       |                                  |                |                |     |       |                                  |                |
| Res       | Round | Delta\_t                         | Zeit Per Frame |                | Res | Round | Delta\_t                         | Zeit Per Frame |
| 0         | 0     | 2\.3256080151                    | 0\.0465121603  |                | 0   | 0     | 1\.9998378754                    | 0\.0399967575  |
| 0         | 1     | 2\.5380539894                    | 0\.0507610798  |                | 0   | 1     | 1\.9979958534                    | 0\.0399599171  |
| 0         | 2     | 2\.8013269901                    | 0\.0560265398  |                | 0   | 2     | 1\.9990649223                    | 0\.0399812984  |
|           |       | durchschnittliche Zeit per frame | 0\.0510999266  |                |     |       | durchschnittliche Zeit per frame | 0\.0399793243  |
| 1         | 0     | 5\.1178381443                    | 0\.1023567629  |                | 1   | 0     | 1\.9972240925                    | 0\.0399444818  |
| 1         | 1     | 4\.2857711315                    | 0\.0857154226  |                | 1   | 1     | 2\.0000920296                    | 0\.0400018406  |
| 1         | 2     | 4\.0194761753                    | 0\.0803895235  |                | 1   | 2     | 1\.9997489452                    | 0\.0399949789  |
|           |       | durchschnittliche Zeit per frame | 0\.0894872363  |                |     |       | durchschnittliche Zeit per frame | 0\.0399804338  |
| 2         | 0     | 12\.3067069054                   | 0\.2461341381  |                | 2   | 0     | 1\.9993178844                    | 0\.0399863577  |
| 2         | 1     | 14\.8925759792                   | 0\.2978515196  |                | 2   | 1     | 1\.9976410866                    | 0\.0399528217  |
| 2         | 2     | 18\.8919248581                   | 0\.3778384972  |                | 2   | 2     | 1\.9969630241                    | 0\.0399392605  |
|           |       | durchschnittliche Zeit per frame | 0\.3072747183  |                |     |       | durchschnittliche Zeit per frame | 0\.03995948    |
| 3         | 0     | 51\.8114199638                   | 1\.0362283993  |                | 3   | 0     | 3\.9923651218                    | 0\.0798473024  |
| 3         | 1     | 58\.1088600159                   | 1\.1621772003  |                | 3   | 1     | 3\.9952740669                    | 0\.0799054813  |
| 3         | 2     | 40\.5061500072                   | 0\.8101230001  |                | 3   | 2     | 3\.9986231327                    | 0\.0799724627  |
|           |       | durchschnittliche Zeit per frame | 1\.0028428666  |                |     |       | durchschnittliche Zeit per frame | 0\.0799084155  |
| 4         | 0     | 145\.9393258095                  | 2\.9187865162  |                | 4   | 0     | 7\.2012009621                    | 0\.1440240192  |
| 4         | 1     | 146\.8662290573                  | 2\.9373245811  |                | 4   | 1     | 6\.4016721249                    | 0\.1280334425  |
| 4         | 2     | 167\.0715620518                  | 3\.341431241   |                | 4   | 2     | 6\.5941028595                    | 0\.1318820572  |
|           |       | durchschnittliche Zeit per frame | 3\.0658474461  |                |     |       | durchschnittliche Zeit per frame | 0\.1346465063  |
