import cv2 as cv
import numpy as np
class find_particles:
    def __init__(self, image_name=None):
        if image_name == None:
            raise ValueError('no image is given, please enter the image for calculation as filename.jpg')
        self.image_name = image_name
        self.img = cv.imread(image_name)

    def blurring(self, method=None, threshold=None, blocksize=13, contrast=-9):
        self.maxValue = 255
        self.img = self.img.copy()
        self.img = cv.cvtColor(self.img, cv.COLOR_BGR2GRAY)
        self.img = cv.GaussianBlur(self.img, (3, 3), 0)
        if method == None:  # Default is Gaussian, can also be mean
            self.method = cv.ADAPTIVE_THRESH_GAUSSIAN_C
        if threshold == None:
            self.threshold = cv.THRESH_BINARY

        img_thresholded = cv.adaptiveThreshold(self.img, self.maxValue, self.method, threshold, blocksize, contrast)
        self.contours, tier = cv.findContours(img_thresholded, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    def add_contours(self, magnification=1.1, filter = 11.5, save_image=True):
        res = np.array(self.img)
        res = cv.cvtColor(res, cv.COLOR_GRAY2BGR)
        w_ref = h_ref = magnification

        self.particle_count = 0
        self.particle_size = []
        for _c in self.contours:
            (x, y), (w, h), theta = cv.minAreaRect(_c)
            realWidth = w / w_ref
            realHeight = h / h_ref
            if realWidth < 11.5 and realHeight < 11.5 and (realWidth * realHeight > 0.01):
                self.particle_count += 1
                self.particle_size.append(realWidth * realHeight)
                box = cv.boxPoints(((x, y), (w, h), theta))
                box = np.intp(box)
                cv.drawContours(res, [box], -1, (0, 0, 255), 2)
                cv.putText(res, "{0:.1f}".format(realWidth) + " x " + "{0:.1f}".format(realHeight) + " microns",
                           (int(x) - 20, int(y) - 10), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv.LINE_AA)
        self.particle_size = np.array(self.particle_size)
        if save_image:  # Saving the image
            filename = 'marked_' + self.image_name
            cv.imwrite(filename, res)

    def particle_stats(self, save_particle_profiles=True):
        print('there are total of ' + str(self.particle_count) + ' particles in this image')
        mean = self.particle_size.sum() / self.particle_count
        print('the average particle size is: ' + str(round(mean, 1)) + ' um^2')
        print('the sample standard deviation is: ' + str(
            round(np.sqrt(np.sum((self.particle_size - mean) ** 2) / self.particle_count), 2)) + ' um^2')
        if save_particle_profiles:
            filename = 'particle_size_of_' + self.image_name.replace('.jpg', '.csv')
            np.savetxt(filename, self.particle_size)

if __name__ == '__main__':
    test = find_particles('example.jpg')
    test.blurring()
    test.add_contours(save_image=True)
    test.particle_stats()
