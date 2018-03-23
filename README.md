## POF Captcha solver

Recently pof.com updated their captcha from a ***custom*** captcha image
 to Google Invisible reCaptcha.
 
Project contains a python library that can solve ***previous*** pof.com captchas

----
The idea behind this captcha is that each time an image with 10 letters is generated. Each letter has 
 either a circle or a triangle above it. The letters required are only those under the circle. There
  are 5 circles and 5 triangles all the time. 
 
The library uses opencv2 to figure out where the circles are located and tesseract to 
find out the letters. Afterwards, this data is matched together and the *needed* 5 letters are returned. 

### Dependencies

- python2.7+
- opencv2
- pytesseract

Arch linux users can install opencv2 with `yaourt opencv2` - takes a bit to build

**Keep in mind** the library won't work as expected with opencv3. The code will
 run, but the results won't be the right ones

pytesseract can be installed  using pip `pip2.7 install pytesseract`

### Success rate

From my own tests, I've got to the conclusion that the success rate is somewhere around 72%

### License
MIT