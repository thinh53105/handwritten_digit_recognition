import cv2

img = cv2.imread("sample_img3.png", cv2.IMREAD_GRAYSCALE)

cv2.imshow("", img)
cv2.waitKey()
cv2.destroyAllWindows()
print(img)