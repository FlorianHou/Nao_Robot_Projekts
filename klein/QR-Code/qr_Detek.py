import cv2 as cv
import numpy as np

def get_QR_Info():
    """nehme Ecke der QR und StringInfo der QR"""
    detector = cv.QRCodeDetector()
    String, Ecks, _ = detector.detectAndDecode(img)
    if Ecks is False:
        ##Python2
        # print "Keine QR wird gefunden!"
        #Python3:
        print("Keine QR wird gefunden")

    return Ecks, String

def kreisZeichnen(Ecks):
    """Zeichnen 4 Ecks auf QR Code"""
    names = ["a","b","c","d"]
    Ecks_int = Ecks.astype(int)
    for name, eck in zip(names,Ecks_int[0]):
        cv.circle(img, tuple(eck), 10, (255,0,0),-1)
        po_text = eck + np.array([10,-5])
        cv.putText(img, name, tuple(po_text), cv.FONT_HERSHEY_SIMPLEX, 1.2, (125, 175,125),2)
    

if __name__ == "__main__":
    img  = cv.imread("klein\\QR-Code\\datei\\963.png")
    print(img.shape)
    ecks, str = get_QR_Info()
    print(ecks, str)

    kreisZeichnen(ecks)
    cv.imshow("", img)
    cv.waitKey(0)
    cv.destroyAllWindows()