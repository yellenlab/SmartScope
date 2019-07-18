import os
import sys
sys.path.append('../maskrcnn')

import maskrcnn.utils as utils
import model as modellib
import visualize
from config import Config

class MarkConfig(Config):
    """Configuration for training on the cell dataset.
    Derives from the base Config class and overrides some values.
    """
    # Give the configuration a recognizable name
    NAME = "mark"

    GPU_COUNT = 1
    IMAGES_PER_GPU = 1

    # Number of classes (including background)
    NUM_CLASSES = 1 + 1  # Background + cell

    # Number of training steps per epoch
    STEPS_PER_EPOCH = 200
    
    # set validation steps 
    VALIDATION_STEPS = 50
    
    # Skip detections with < 90% confidence
    DETECTION_MIN_CONFIDENCE = 0.9


class MarkDataset(utils.Dataset):

    def load_shapes(self, subset):
        # Add classes. We have only one class to add.
        self.add_class("mark", 1, "mark")

        # Train or validation dataset?
        dataset_dir = os.path.join("./", subset)
        
        if subset == 'train/train':
            annotations = json.load(open('alignment_labels.json', 'r'))
        else:
            annotations = json.load(open('alignment_val.json', 'r'))
        
        # Add images annotated with Labelbox 
        for a in annotations:
            polys = [r['geometry'] for r in a['Label']['Mark']]  
            polygons = []
        
            for i, p in enumerate(polys):
                x_points = [x['x'] for x in p]
                y_points = [y['y'] for y in p]
                polygons.append({'all_points_x': x_points, 'all_points_y': y_points})
            
            # Get Image Size 
            image_path = os.path.join(dataset_dir, a['External ID'])
            image = imread(image_path)
            height, width = image.shape[:2]

            self.add_image(
                "mark",
                image_id=a['External ID'],  # use file name as a unique image id
                path=image_path,
                width=width, height=height,
                polygons=polygons)
        


    def load_mask(self, image_id):
        """Generate instance masks for an image.
       Returns:
        masks: A bool array of shape [height, width, instance count] with
            one mask per instance.
        class_ids: a 1D array of class IDs of the instance masks.
        """
        # If not a balloon dataset image, delegate to parent class.
        image_info = self.image_info[image_id]
        if image_info["source"] != "mark":
            return super(self.__class__, self).load_mask(image_id)

        # Convert polygons to a bitmap mask of shape
        # [height, width, instance_count]
        info = self.image_info[image_id]
        mask = np.zeros([info["height"], info["width"], len(info["polygons"])],
                        dtype=np.uint8)
        for i, p in enumerate(info["polygons"]):
            # Get indexes of pixels inside the polygon and set them to 1
            rr, cc = skimage.draw.polygon(p['all_points_y'], p['all_points_x'])
            mask[rr, cc, i] = 1

        # Return mask, and array of class IDs of each instance. Since we have
        # one class ID only, we return an array of 1s
        return mask.astype(np.bool), np.ones([mask.shape[-1]], dtype=np.int32)

    def image_reference(self, image_id):
        """Return the path of the image."""
        info = self.image_info[image_id]
        if info["source"] == "mark":
            return info["path"]
        else:
            super(self.__class__, self).image_reference(image_id)

class InferenceConfig(MarkConfig):
    # Set batch size to 1 since we'll be running inference on
    # one image at a time. Batch size = GPU_COUNT * IMAGES_PER_GPU
    GPU_COUNT = 1
    IMAGES_PER_GPU = 1