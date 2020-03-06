import os
import pandas
import numpy

from PIL import Image
from torch.utils.data import Dataset


class DataBoxesGenerator(Dataset):

    def __init__(self, images_path, annotations_path, transform):
        self.transform = transform
        self.images = images_path
        # Load annotations file
        dtype = {
            'image_filename': 'str',
            'classname': 'str',
            'x0': 'int',
            'y0': 'int',
            'x1': 'int',
            'y1': 'int',
            'class': 'int'
        }
        self.annotations = pandas.read_csv(annotations_path, dtype = dtype)
        
    def __getitem__(self, index):
        # Load image
        selected_image = self.images[index]
        with open(selected_image, 'rb') as f:
            image = numpy.array(Image.open(f))[..., :3]
        
        # Find boxes
        selected_annotations = self.annotations.loc[self.annotations['image_filename'] == selected_image.split('/')[-1]]
        boxes_array = numpy.zeros((len(selected_annotations), 5))

        for idx, annot in selected_annotations.iterrows():
            boxes_array[idx, 0] = float(annot['x0'])
            boxes_array[idx, 1] = float(annot['y0'])
            boxes_array[idx, 2] = float(annot['x1'])
            boxes_array[idx, 3] = float(annot['y1'])
            boxes_array[idx, 4] = annot['class']
        
        img_tensor, boxes_tensor = self.transform.fit(image, boxes_array)

        return img_tensor, boxes_tensor
    

    def __len__(self):
        return len(self.images)

