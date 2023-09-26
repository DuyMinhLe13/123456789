import torch
import torchvision
import numpy as np
from .GNNPlugins import GNNModel
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

class DensenetGnnModel(torch.nn.Module):
    def __init__(self, num_classes, embedding_size, n_layers=0, n_heads=3, model='densenet201'):
        super().__init__()
        if model == 'densenet201':
            densenet_base = torchvision.models.densenet201(weights='DEFAULT')
        elif model == 'densenet161':
            densenet_base = torchvision.models.densenet161(weights='DEFAULT')
        self.feature_extractor = torch.nn.Sequential(
            densenet_base.features,
            torch.nn.AdaptiveAvgPool2d((1, 1)),
            torch.nn.Flatten()
        )
        self.gnn_model = GNNModel(embedding_size=embedding_size, 
                                  n_layers=n_layers, 
                                  feature_size=densenet_base.classifier.in_features,
                                  n_heads=n_heads,
                                  dropout_rate=0,
                                  edge_dim=1,
                                  num_classes=num_classes)
        del densenet_base
        self.feature_extractor = self.feature_extractor.to(device)
        self.gnn_model = self.gnn_model.to(device)
    
    def get_edge_index(self, size):
        edge_index = []
        for id_x in range(size):
          for id_y in range(size):
            edge_index.append([id_x, id_y])
        edge_index = np.array(edge_index)
        return torch.tensor(edge_index, dtype=torch.int64).t().to(device)

    def get_edge_attr(self, images):
        edge_attr = []
        for data_x in images:
            for data_y in images:
              edge_attr.append(np.mean(np.absolute(data_y - data_x)))
        edge_attr = np.array(edge_attr)
        edge_attr = torch.tensor(edge_attr, dtype=torch.float32)
        edge_attr = torch.reshape(edge_attr, (len(edge_attr), 1))
        return edge_attr.to(device)
    
    def forward(self, images):
        x = self.feature_extractor(images)
        return self.gnn_model(x, self.get_edge_index(images.shape[0]), self.get_edge_attr(x.detach().cpu().numpy()))



class VitGnnModel(torch.nn.Module):
    def __init__(self, num_classes, embedding_size, n_layers=0, n_heads=3, model='swint_big'):
        super().__init__()
        if model == 'swint_big':
            vit_base = torchvision.models.swin_v2_b(weights='DEFAULT')
        elif model == 'swint_small':
            vit_base = torchvision.models.swin_v2_s(weights='DEFAULT')
        self.feature_extractor = torch.nn.Sequential(
            vit_base.features,
            vit_base.norm,
            vit_base.permute,
            vit_base.avgpool,
            vit_base.flatten
        )
        self.gnn_model = GNNModel(embedding_size=embedding_size, 
                                  n_layers=n_layers, 
                                  feature_size=vit_base.head.in_features,
                                  n_heads=n_heads,
                                  dropout_rate=0,
                                  edge_dim=1,
                                  num_classes=num_classes)
        del vit_base
        self.feature_extractor = self.feature_extractor.to(device)
        self.gnn_model = self.gnn_model.to(device)
    
    def get_edge_index(self, size):
        edge_index = []
        for id_x in range(size):
          for id_y in range(size):
            edge_index.append([id_x, id_y])
        edge_index = np.array(edge_index)
        return torch.tensor(edge_index, dtype=torch.int64).t().to(device)

    def get_edge_attr(self, images):
        edge_attr = []
        for data_x in images:
            for data_y in images:
              edge_attr.append(np.mean(np.absolute(data_y - data_x)))
        edge_attr = np.array(edge_attr)
        edge_attr = torch.tensor(edge_attr, dtype=torch.float32)
        edge_attr = torch.reshape(edge_attr, (len(edge_attr), 1))
        return edge_attr.to(device)
    
    def forward(self, images):
        x = self.feature_extractor(images)
        return self.gnn_model(x, self.get_edge_index(images.shape[0]), self.get_edge_attr(x.detach().cpu().numpy()))



class ConvNextGnnModel(torch.nn.Module):
    def __init__(self, num_classes, embedding_size, n_layers=0, n_heads=3):
        super().__init__()
        convnext_base = torchvision.models.convnext_base(weights='DEFAULT')
        self.feature_extractor = torch.nn.Sequential(
            convnext_base.features,
            convnext_base.avgpool,
            convnext_base.classifier[0],
            convnext_base.classifier[1]
        )
        self.gnn_model = GNNModel(embedding_size=embedding_size,
                                  n_layers=n_layers,
                                  feature_size=convnext_base.classifier[2].in_features,
                                  n_heads=n_heads,
                                  dropout_rate=0,
                                  edge_dim=1,
                                  num_classes=num_classes)
        del convnext_base
        self.feature_extractor = self.feature_extractor.to(device)
        self.gnn_model = self.gnn_model.to(device)

    def get_edge_index(self, size):
        edge_index = []
        for id_x in range(size):
          for id_y in range(size):
            edge_index.append([id_x, id_y])
        edge_index = np.array(edge_index)
        return torch.tensor(edge_index, dtype=torch.int64).t().to(device)

    def get_edge_attr(self, images):
        edge_attr = []
        for data_x in images:
            for data_y in images:
              edge_attr.append(np.mean(np.absolute(data_y - data_x)))
        edge_attr = np.array(edge_attr)
        edge_attr = torch.tensor(edge_attr, dtype=torch.float32)
        edge_attr = torch.reshape(edge_attr, (len(edge_attr), 1))
        return edge_attr.to(device)

    def forward(self, images):
        x = self.feature_extractor(images)
        return self.gnn_model(x, self.get_edge_index(images.shape[0]), self.get_edge_attr(x.detach().cpu().numpy()))
