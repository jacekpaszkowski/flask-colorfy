#!/usr/bin/env python3
#coding=utf-8

import numpy as np
from PIL import Image
from sklearn.cluster import KMeans


class SpotifyBackgroundColor():
    """Analyzes an image and finds a fitting background color.

    Main use is to analyze album artwork and calculate the background
    color Spotify sets when playing on a Chromecast.

    Attributes:
        img (ndarray): The image to analyze.

    """

    def __init__(self, img, format='RGB', image_processing_size=None):
        """Prepare the image for analyzation.

        Args:
            img (ndarray): The image to analyze.
            format (str): Format of `img`, either RGB or BGR.
            image_processing_size: (int/float/tuple): Process image or not.
                int - Percentage of current size.
                float - Fraction of current size.
                tuple - Size of the output image (must be integers).

        Raises:
            ValueError: If `format` is not RGB or BGR.

        """
        if format == 'RGB':
            self.img = img
        elif format == 'BGR':
            self.img = img[..., ::-1]
        else:
            raise ValueError('Invalid format. Only RGB and BGR image '\
                             'format supported.')

        if image_processing_size:
            self.img = self._resize(self.img, image_processing_size)

    @staticmethod
    def _resize(img, size):
        """Bilinear resize, same size semantics as scipy.misc.imresize.

        `size` is an int (percent), a float (fraction) or a tuple
        (height, width).

        """
        pil_img = Image.fromarray(img)
        width, height = pil_img.size
        if isinstance(size, int):
            new_size = (int(width * size / 100.0), int(height * size / 100.0))
        elif isinstance(size, float):
            new_size = (int(width * size), int(height * size))
        else:
            new_size = (int(size[1]), int(size[0]))
        return np.array(pil_img.resize(new_size, Image.Resampling.BILINEAR))

    def best_color(self, k=8, color_tol=10):
        """Returns a suitable background color for the given image.

        Uses k-means clustering to find `k` distinct colors in
        the image. A colorfulness index is then calculated for each
        of these colors. The color with the highest colorfulness
        index is returned if it is greater than or equal to the
        colorfulness tolerance `color_tol`. If no color is colorful
        enough, a gray color will be returned. Returns more or less
        the same color as Spotify in 80 % of the cases.

        Args:
            k (int): Number of clusters to form.
            color_tol (float): Tolerance for a colorful color.
                Colorfulness is defined as described by Hasler and
                Süsstrunk (2003) in https://infoscience.epfl.ch/
                record/33994/files/HaslerS03.pdf.

        Returns:
            tuple: (R, G, B). The calculated background color.

        """
        try:
          self.img = self.img.reshape((self.img.shape[0]*self.img.shape[1], 3))
        except Exception as err:
          pass
        
        clt = KMeans(n_clusters=k, n_init=10)
        clt.fit(self.img)
        centroids = clt.cluster_centers_

        colorfulness = [self.colorfulness(color[0], color[1], color[2]) for color in centroids]
        max_colorful = np.max(colorfulness)

        if max_colorful < color_tol:
            # If not colorful, set to gray
            best_color = [230, 230, 230]
        else:
            # Pick the most colorful color
            best_color = centroids[np.argmax(colorfulness)]

        return best_color[0], best_color[1], best_color[2]

    def find_histogram(self, clt):
        """Create a histogram of image.

        Args:
            clt (array_like): Input data.

        Returns:
            array: The values of the histogram.

        """
        num_labels = np.arange(0, len(np.unique(clt.labels_)) + 1)
        hist, _ = np.histogram(clt.labels_, bins=num_labels)

        hist = hist.astype('float')
        hist /= hist.sum()

        return hist

    def colorfulness(self, r, g, b):
        """Returns a colorfulness index of given RGB combination.

        Implementation of the colorfulness metric proposed by
        Hasler and Süsstrunk (2003) in https://infoscience.epfl.ch/
        record/33994/files/HaslerS03.pdf.

        Args:
            r (int): Red component.
            g (int): Green component.
            b (int): Blue component.

        Returns:
            float: Colorfulness metric.

        """
        rg = np.absolute(r - g)
        yb = np.absolute(0.5 * (r + g) - b)

        # Compute the mean and standard deviation of both `rg` and `yb`.
        rb_mean, rb_std = (np.mean(rg), np.std(rg))
        yb_mean, yb_std = (np.mean(yb), np.std(yb))

        # Combine the mean and standard deviations.
        std_root = np.sqrt((rb_std ** 2) + (yb_std ** 2))
        mean_root = np.sqrt((rb_mean ** 2) + (yb_mean ** 2))

        return std_root + (0.3 * mean_root)
