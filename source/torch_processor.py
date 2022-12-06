# original from John-Melle in Z:\users\johnmelle\playground\code\pathology-fast-inference-121021\fastinference\processors
import numpy as np
import cv2
import torch
import torch.nn as nn
from importlib import import_module
import torch.utils.data as data
import segmentation_models_pytorch as smp
import yaml
from ..async_tile_processor import async_tile_processor

class torch_processor(async_tile_processor):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sigmoid_fn = nn.Sigmoid()

    def get_config_from_yaml(self, config_path: str) -> dict:
        with open(file=config_path, mode='r') as param_file:
            parameters = yaml.load(stream=param_file, Loader=yaml.SafeLoader)
        return parameters['model'], parameters['sampler'], parameters['training']

    def _load_network_model(self):
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        # config_path = self._model_path.split("_epoch")[0].split("_best")[0] + '.yaml'
        #
        # model_parameters, sampler_parameters, training_parameters = self.get_config_from_yaml(config_path)
        # n_classes = len(np.unique(list(sampler_parameters['training']['label_map'].values())))

        model = smp.Unet(encoder_name='efficientnet-b0',
                encoder_weights='imagenet')

        state_dict = torch.load(self._model_path)
        model.load_state_dict(state_dict)
        print("Model succesfully loaded!")
        model.to(device)

        return model

    def _predict_tile_batch(self, tile_batch=None, info=None):
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        if self._ax_order == 'cwh':
            tile_batch = tile_batch.transpose(0, 3, 1, 2)

        tile_batch = torch.from_numpy(tile_batch).to(device)

        with torch.cuda.amp.autocast():
            result = self._model.predict(tile_batch)

        result = self.sigmoid_fn(result)
        result = result.detach().cpu().numpy()

        if self._ax_order == 'cwh':
            result = result.transpose(0, 2, 3, 1)

        return result

    def _send_reconstruction_info(self):
        self._write_queues[0].put(('recon_info',
                                   '',1))

    def _process_tile_batch(self, tile_batch=None, info=None):
        """
        Processes the tile batch on the GPU. Optionally performs test time augmentation.
        Args:
            tile_batch (np.array):
            info (tuple):

        Returns:

        """
        if self._augment:
            result_stack = list()
            for flip in (True, False):
                flipped_tile = np.flip(m=tile_batch, axis=1) if flip else tile_batch
                for rot_k in range(4):
                    augmented_tile = np.rot90(m=flipped_tile, k=rot_k, axes=(1, 2))
                    augmented_result = self._predict_tile_batch(tile_batch=augmented_tile, info=info)
                    augmented_result = np.rot90(m=augmented_result, k=-rot_k, axes=(1, 2))
                    augmented_result = np.flip(m=augmented_result, axis=1) if flip else augmented_result
                    result_stack.append(augmented_result)

            return scipy.stats.mstats.gmean(a=np.stack(result_stack), axis=0)
        else:
            return self._predict_tile_batch(tile_batch=tile_batch, info=info)
