from pofcaptcha import PofCaptcha
import os

img = os.path.join(os.getcwd(), 'images', '1.jpe')
p = PofCaptcha(img)
result = p.get_result()
print result
