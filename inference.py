from PIL import Image
import torch
import torch.nn as nn
import torchvision
from torchvision import models, transforms
import matplotlib.pyplot as plt

def inference(image_path):

  def initialize_model(num_classes):
      model_ft = None
      model_ft = models.resnet34()
      num_ftrs = model_ft.fc.in_features
      model_ft.fc = nn.Linear(num_ftrs, num_classes)
      
      return model_ft

  def load_classes(path):
    classes = list()
    with open(path, 'r') as file:
      data = file.readlines()

      for i in data:
        classes.append(i.strip("\n"))
    return classes


  num_classes = 12
  input_size = 224
  model_folder = "./"
  classes = load_classes(model_folder+"Classes.txt")
  finetuned_model = initialize_model(num_classes)
  finetuned_model.load_state_dict(torch.load(model_folder + "ResNet34_Finetuned_GCV2", map_location=torch.device('cpu')))
  device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
  finetuned_model.to(device)
  finetuned_model.eval()


  def transform_image(image):
    my_transforms = transforms.Compose([
          transforms.Resize(input_size),
          transforms.CenterCrop(input_size),
          transforms.ToTensor(),
          transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
      ])
    
    image = Image.open(image_path).convert('RGB')
    return my_transforms(image).unsqueeze(0)

  def get_prediction(image):
      tensor = transform_image(image)
      tensor=tensor.to(device)
      output = finetuned_model.forward(tensor)
      
      probs = torch.nn.functional.softmax(output, dim=1)
      conf, clas = probs.topk(2)
      return conf.cpu().detach().numpy()[0], [classes[i] for i in clas.cpu().detach().numpy()[0]]

  image = plt.imread(image_path)
  confidence, class_name = get_prediction(image)
  return class_name, confidence


if __name__ == "main":
  a = "do nothing"