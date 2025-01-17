import  os
import numpy as np
import torch
import torch.nn as nn
from torch.autograd import Variable
from terminaltables import AsciiTable

from utils.stats import (
    non_max_suppression, to_cpu, xywh2xyxy, 
    get_batch_statistics, ap_per_class, load_classe_names)


@torch.no_grad()
def val(model, optimizer, dataloader, epoch, opt, val_logger, visualizer=None):
    labels = []
    sample_matrics = []
    for i, (images, targets) in enumerate(dataloader):
        labels += targets[:, 1].tolist()
        targets[:, 2:] = xywh2xyxy(targets[:, 2:])
        targets[:, 2:] *= opt.image_size

        outputs = model.forward(images)
        outputs = non_max_suppression(outputs, opt.conf_thres, opt.nms_thres)
        sample_matrics += get_batch_statistics(outputs, targets, iou_threshold=0.5)

        if visualizer is not None:
            vis.plot_current_visuals(images, outputs)
    
    true_positives, pred_scores, pred_labels = [np.concatenate(x, 0) for x in list(zip(*sample_matrics))]
    precision, recall, AP, f1, ap_class = ap_per_class(true_positives, pred_scores, pred_labels, labels)
    
    # logging
    metric_table_data = [
        ['Metrics', 'Value'], ['precision', precision.mean()], ['recall', recall.mean()], 
        ['f1', f1.mean()], ['mAP', AP.mean()]]
     
    metric_table = AsciiTable(
            metric_table_data,
            title='[Epoch {:d}/{:d}'.format(epoch, opt.num_epochs))
    print('{}\n\n\n'.format(metric_table.table))
    
    class_names = load_classe_names(opt.classname_path)
    for i, c in enumerate(ap_class):
        metric_table_data += [['AP-{}'.format(class_names[c]), AP[i]]]
    metric_table.table_data = metric_table_data
    val_logger.write('{}\n\n\n'.format(metric_table.table))