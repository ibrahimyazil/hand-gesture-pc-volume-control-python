# Kütüphaneleri içe aktar
import cv2
import numpy as np
import pyautogui

# Kamera aygıtını tanımla
cap = cv2.VideoCapture(0)

# Sonsuz döngü içinde kamera görüntüsünü oku
while True:
    # Kameradan gelen görüntüyü oku
    _, frame = cap.read()
    # Görüntüyü gri tonlamaya çevir
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Görüntüyü bulanıklaştır
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    # Görüntüyü ikili hale getir
    _, thresh = cv2.threshold(blur, 100, 255, cv2.THRESH_BINARY_INV)
    # Görüntüdeki konturları bul
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # En büyük konturu bul
    max_area = 0
    max_contour = None
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > max_area:
            max_area = area
            max_contour = contour
    # En büyük konturun dışbükey kabuğunu bul
    hull = cv2.convexHull(max_contour)
    # En büyük konturun dışbükeylik kusurlarını bul
    hull = cv2.convexHull(max_contour, returnPoints=False)
    defects = cv2.convexityDefects(max_contour, hull)
    # Parmak sayısını bul
    finger_count = 0
    for i in range(defects.shape[0]):
        # Dışbükeylik kusurunun başlangıç, bitiş ve en uzak noktalarını al
        s, e, f, d = defects[i, 0]
        start = tuple(max_contour[s][0])
        end = tuple(max_contour[e][0])
        far = tuple(max_contour[f][0])
        # Başlangıç, bitiş ve en uzak noktalar arasındaki açıyı hesapla
        a = np.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)
        b = np.sqrt((far[0] - start[0]) ** 2 + (far[1] - start[1]) ** 2)
        c = np.sqrt((end[0] - far[0]) ** 2 + (end[1] - far[1]) ** 2)
        angle = np.arccos((b ** 2 + c ** 2 - a ** 2) / (2 * b * c))
        # Açı 90 dereceden küçükse, parmak sayısını artır
        if angle <= np.pi / 2:
            finger_count += 1
            # En uzak noktayı kırmızı renkle işaretle
            cv2.circle(frame, far, 8, [0, 0, 255], -1)
    # Parmak sayısına göre pc'nin sesini veya ekran parlaklığını ayarla
    if finger_count == 1:
        # Bir parmak gösterilirse, ses seviyesini artır
        pyautogui.press("volumeup")
    elif finger_count == 2:
        # İki parmak gösterilirse, ses seviyesini azalt
        pyautogui.press("volumedown")
    elif finger_count == 3:
        # Üç parmak gösterilirse, ekran parlaklığını artır
        pyautogui.hotkey("fn", "f6")
    elif finger_count == 4:
        # Dört parmak gösterilirse, ekran parlaklığını azalt
        pyautogui.hotkey("fn", "f5")
    # Parmak sayısını ve kameradan gelen görüntüyü ekranda göster
    cv2.putText(frame, str(finger_count), (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2)
    cv2.imshow("Frame", frame)
    # q tuşuna basıldığında döngüden çık
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
# Kamera aygıtını serbest bırak
cap.release()
# Tüm pencereleri kapat
cv2.destroyAllWindows()