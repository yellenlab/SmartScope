"""
https://github.com/google/microscopeimagequality/blob/main/microscopeimagequality/prediction.py
"""

import logging
import sys

import numpy
import tensorflow

from smartscope.source.miq import constants
from smartscope.source.miq import evaluation

# logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

_SPLIT_NAME = 'test'

_TFRECORD_FILE_PATTERN = 'data_%s-%05d-of-%05d.tfrecord'

logger = logging.getLogger(__name__)


class ImageQualityClassifier(object):
    """Object for running image quality model inference.

    Attributes:
      graph: TensorFlow graph.
    """

    def __init__(self,
                 model_ckpt,
                 model_patch_side_length,
                 num_classes,
                 graph=None, 
                 session_config=None):
        """Initialize the model from a checkpoint.

        Args:
          model_ckpt: String, path to TensorFlow model checkpoint to load.
          model_patch_side_length: Integer, the side length in pixels of the square
            image passed to the model.
          num_classes: Integer, the number of classes the model predicts.
          graph: TensorFlow graph. If None, one will be created.
          session_config: TensorFlow session configuration.  If None, one will be created
        """
        self._model_patch_side_length = model_patch_side_length
        self._num_classes = num_classes

        if graph is None:
            graph = tensorflow.Graph()
        self.graph = graph

        with self.graph.as_default():
            self._image_placeholder = tensorflow.placeholder(
                tensorflow.float32, shape=[None, None, 1])

            self._probabilities = self._probabilities_from_image(
                self._image_placeholder, model_patch_side_length, num_classes)

            self._sess = tensorflow.Session(config=session_config)
            saver = tensorflow.train.Saver()

            saver.restore(self._sess, model_ckpt)
        logger.debug('Restored image focus prediction model from %s.', model_ckpt)

    def __del__(self):
        self._sess.close()

    def _probabilities_from_image(self, image_placeholder,
                                  model_patch_side_length, num_classes):
        """Get probabilities tensor from input image tensor.

        Args:
          image_placeholder: Float32 tensor, placeholder for input image.
          model_patch_side_length: Integer, the side length in pixels of the square
            image passed to the model.
          num_classes: Integer, the number of classes the model predicts.

        Returns:
          Probabilities tensor, shape [num_classes] representing the predicted
          probabilities for each class.
        """
        labels_fake = tensorflow.zeros([self._num_classes])

        image_path_fake = tensorflow.constant(['unused'])
        tiles, labels, _ = _get_image_tiles_tensor(
            image_placeholder, labels_fake, image_path_fake,
            model_patch_side_length)

        model_metrics = evaluation.get_model_and_metrics(
            tiles,
            num_classes=num_classes,
            one_hot_labels=labels,
            is_training=False)

        return model_metrics.probabilities

    def score(self, image, invert=False):
        """Get probability-weighted class prediction as a "score" for an image

        Args:
            image: Numpy float array, two-dimensional.
            invert: By default, the classes are ordered [0, n_classes) where lower numbers denote
                better focus so passing invert=True means that this interpretation is flipped and
                instead higher scores are better.  In other words, if invert=False (default) then
                the score returned means lower is better, whereas with invert=True higher scores
                are better
        Returns:
            Float
        """
        pred = self.predict(image)
        classes = numpy.arange(self._num_classes)
        if invert:
            classes = classes[::-1]
        assert pred.probabilities.ndim == classes.ndim == 1
        return numpy.dot(pred.probabilities, classes)

    def predict(self, image):
        """Run inference on an image.

        Args:
          image: Numpy float array, two-dimensional.

        Returns:
          A evaluation.WholeImagePrediction object.
        """
        feed_dict = {self._image_placeholder: numpy.expand_dims(image, 2)}
        [np_probabilities] = self._sess.run(
            [self._probabilities], feed_dict=feed_dict)

        return evaluation.aggregate_prediction_from_probabilities(
            np_probabilities, evaluation.METHOD_AVERAGE)

    def get_patch_predictions(self, image):
        """Run inference on each patch in an image, returning each patch score.

        Args:
          image: Numpy float array, of shape (height, width).

        Returns:
          List of tuples, with (upper_left_row, upper_left_col, height, width
          evaluation.WholeImagePrediction) which denote the patch location,
          dimensions and predition result.
        """
        results = []
        w = constants.PATCH_SIDE_LENGTH
        for i in range(0, image.shape[0] - w, w):
            for j in range(0, image.shape[1] - w, w):
                results.append((i, j, w, w, self.predict(image[i:i + w, j:j + w])))
        return results


def patch_values_to_mask(values, patch_width):
    """Construct a mask from an array of patch values.

  Args:
    values: A uint16 2D numpy array.
    patch_width: Width in pixels of each patch.

  Returns:
    The  mask, a uint16 numpy array of width patch_width *
    values.shape[0].

  Raises:
    ValueError: If the input values are invalid.
  """
    if values.dtype != numpy.uint16 or len(values.shape) != 2:
        logging.info('dtype: %s shape: %s', values.dtype, values.shape)
        raise ValueError('Input must be a 2D np.uint16 array.')

    patches_per_column = values.shape[0]
    patches_per_row = values.shape[1]

    mask = numpy.zeros(
        (patches_per_column * patch_width, patches_per_row * patch_width),
        dtype=numpy.uint16)

    for i in range(patches_per_column):
        for j in range(patches_per_row):
            ymin = i * patch_width
            xmin = j * patch_width
            mask[ymin:ymin + patch_width, xmin:xmin + patch_width] = values[i, j]

    return mask


def _get_image_tiles_tensor(image, label, image_path, patch_width):
    """Gets patches that tile the input image, starting at upper left.

    Args:
      image: Input image tensor, size [height x width x 1].
      label: Input label tensor, size [num_classes].
      image_path: Input image path tensor, size [1].
      patch_width: Integer representing width of image patch.

    Returns:
      Tensors tiles, size [num_tiles x patch_width x patch_width x 1], labels,
      size [num_tiles x num_classes], and image_paths, size [num_tiles x 1].
    """
    tiles_before_reshape = tensorflow.extract_image_patches(
        tensorflow.expand_dims(image, dim=0), [1, patch_width, patch_width, 1],
        [1, patch_width, patch_width, 1], [1, 1, 1, 1], 'VALID')
    tiles = tensorflow.reshape(tiles_before_reshape, [-1, patch_width, patch_width, 1])

    labels = tensorflow.tile(tensorflow.expand_dims(label, dim=0), [tensorflow.shape(tiles)[0], 1])
    image_paths = tensorflow.tile(
        tensorflow.expand_dims(image_path, dim=0), [tensorflow.shape(tiles)[0], 1])
    return tiles, labels, image_paths

