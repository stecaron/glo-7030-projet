import torch
import torch.nn as nn
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import torch.nn.functional as F

from torchvision import transforms
from torch import optim
from PIL import Image
from src.create_image_label.create_image_label import CreateLabel
from src.unet.unet_model import UNet
from src.loss import DiceCoeff
from src.unet.utils import readfile


{'ice': 1, 'board': 2, 'circlezone': 3, 'circlemid': 4, 'goal': 5, 'blue': 6, 'red': 7, 'fo': 8}
colors = ['black', 'white', 'yellow', 'pink', 'coral', 'crimson', 'blue', 'red', 'magenta']
cmap = mpl.colors.ListedColormap(colors)


path_img = 'data/train/rimage-120.png'
path_pkl = 'data/train/rimage-120.pkl'
data_augmentation = True

labels = readfile(path_pkl.replace('.pkl', ''))

normalize = transforms.Normalize(
   mean=[0.485, 0.456, 0.406],
   std=[0.229, 0.224, 0.225]
)


img = np.array(Image.open(path_img))[..., :3]
plt.imshow(img, cmap=cmap)
plt.show()
plt.imshow(labels, cmap=cmap)
plt.show()

preprocess = transforms.Compose([
    transforms.ToTensor(),
    normalize
])

img_tensor = preprocess(img)



# Vu qu'on test avec une batch_size de 1 pour le moment
img_tensor.unsqueeze_(0)
# On enleve la premiere ligne et la premiere colone car on commencait a 1
labels = labels[1:, 1:]
labels_tensor = torch.LongTensor(labels).unsqueeze(0)

net = UNet(3, 9)
labels_tensor_array = np.array(labels_tensor.data[0])
weight_learn = torch.FloatTensor(np.array([np.exp(1-(labels_tensor_array == i).mean()) for i in range(9)]))
weight_learn[5] = weight_learn[5] + 10  # more weight to goal line
weight_learn[8] = weight_learn[8] + 10  # more weight to face-off dot
# Parametres d'entrainement
optimizer = optim.SGD(net.parameters(),
                          lr=0.05,
                          momentum=0.9,
                          weight_decay=0.0005)

criterion = nn.CrossEntropyLoss()#weight=weight_learn)
criterion = DiceCoeff()
net.train()


for i in range(21):
    preds = net(img_tensor)

    if i % 10 == 0:
        preds_img = preds.max(dim=1)[1]
        plt.imshow(preds_img[0], cmap=cmap)
        plt.show()
    optimizer.zero_grad()
    loss = criterion(preds, labels_tensor)
    print('iter {} loss : {}'.format(i, loss))
    loss.backward()
    optimizer.step()

net.eval()
preds_img = preds.max(dim=1)[1]
plt.imshow(preds_img[0], cmap=cmap)
plt.show()
preds_img.unique()
preds_softmax = F.softmax(preds, dim=1)
preds_array = np.array(preds_softmax.data[0])
preds_array.shape
labels_tensor_array = np.array(labels_tensor.data[0])
labels_tensor_array.shape

loss_array = []
for i in range(labels_tensor_array.shape[0]):
    for j in range(labels_tensor_array.shape[1]):
        loss_array.append(-np.log(preds_array[labels_tensor_array[i][j]])[i][j])

mean_loss = np.array(loss_array).mean()
print(mean_loss)
labels_tensor.unique()