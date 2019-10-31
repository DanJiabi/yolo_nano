import argparse
import os
import torch

class Opt():
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.initialized = False

    def initialize(self):
        # project root, dataset, checkpoint resume and pretrained model path
        self.parser.add_argument("--project_root", type=str, default=".", help="root directory path of project")
        self.parser.add_argument("--dataset_path", type=str, default="datasets", help="directory path of dataset")
        self.parser.add_argument("--checkpoint_path", type=str, default="checkpoints", help="directory path of checkpoints")
        self.parser.add_argument("--resume_path", type=str, default="", help="save data (.pth) of previous training")
        self.parser.add_argument("--pretrain_path", type=str, default="", help="path of pretrain model (.pth)")
        # self.parser.add_argument("--result_path", type=str, default="results", help="directory path of results")

        # common options that are used in both train and test
        self.parser.add_argument("--manual_seed", type=int, default=42, help="manual_seed of pytorch")
        self.parser.add_argument("--gpu_ids", type=str, default="0,1")
        self.parser.add_argument("--num_threads", type=int, default=8, help="# of cpu threads to use for batch generation")
        self.parser.add_argument("--dataset", default="coco", help="specify the type of custom dataset to create")
        self.parser.add_argument("--dataset_mode", default="list", help="specify the type of custom dataset to create")
        self.parser.add_argument("--checkpoint_interval", type=int, default=10, help="interval between saving model weights")
        self.parser.add_argument("--evaluation_interval", type=int, default=1, help="interval evaluations on validation set")

        self.parser.add_argument("--model", type=str, default="yolo_nano", help="choose which model to use")
        self.parser.add_argument("--optimizer", type=str, default="Adam", help="optimizer (Adam | SGD)")
        self.parser.add_argument("--image_size", type=int, default=416, help="size of image")
        self.parser.add_argument("--num_classes", type=int, default=3, help="# of classes of the dataset")
        self.parser.add_argument('--num_epochs', type=int, default=20, help='# of epochs')
        self.parser.add_argument('--begin_epoch', type=int, default=0, help='# of epochs')
        self.parser.add_argument("--batch_size", type=int, default=2, help="batch size")
        self.parser.add_argument('--lr', type=float, default=1e-4, help="divided by `lr_patience` while training by lr scheduler")
        self.parser.add_argument('--lr_patience', type=int, default=10, help="patience of LR scheduler -- ReduceLROnPlateau")
        # self.parser.add_argument("--gradient_accumulations", type=int, default=2, help="# of gradient accums before step")
        
        # object detection options
        self.parser.add_argument("--conf_thres", type=float, default=.8)
        self.parser.add_argument("--nms_thres", type=float, default=.5)
        self.parser.add_argument("--num_anchors", type=int, default=3, help="# of anchors in each perdiction")
        self.parser.add_argument("--multiscale", default=True, help="allow for multi-scale training")
        self.parser.add_argument("--hflip", default=True, help="horizontal flip ")
        # self.parser.add_argument("--compute_map", default=False, help="if True computes mAP every 10th batch")

        self.parser.add_argument("--train", default=True, help="training")
        self.parser.add_argument("--val", default=True, help="validation")
        self.parser.add_argument("--test", default=False, help="test")
        
        # self.parser.add_argument("--display_freq", type=int, default=10, help='display the results in every # iterations')
        self.parser.add_argument("--ncols", type=int, default=5, help="images to show each columns (for visulizer)")

        self.parser.add_argument("--print_options", default=True, help="print options or not")

        self.initialized = True

    def print_options(self):
        message = ''
        message += '------------------------ OPTIONS -----------------------------\n'
        for k,v in sorted(vars(self.opt).items()):
            comment = ''
            default = self.parser.get_default(k)
            if v != default:
                comment = '\t[default: %s]' % str(default)
            message += '{:>25}: {:<30}\n'.format(str(k), str(v), comment)
        message += '------------------------  END   ------------------------------\n'
        print(message)

    def parse(self):
        if not self.initialized:
            self.initialize()

        self.opt = self.parser.parse_args()

        if self.opt.project_root != '':
            self.opt.dataset_path = os.path.join(self.opt.project_root, self.opt.dataset_path)
            self.opt.checkpoint_path = os.path.join(self.opt.project_root, self.opt.checkpoint_path)
            if self.opt.resume_path:
                self.opt.resume_path = os.path.join(self.opt.project_root, self.opt.resume_path)
            if self.opt.pretrain_path:
                self.opt.pretrain_path = os.path.join(self.opt.project_root, self.opt.pretrain_path)

        os.makedirs(self.opt.checkpoint_path, exist_ok=True)
        os.makedirs(self.opt.checkpoint_path, exist_ok=True)

        os.environ['CUDA_VISIBLE_DEVICES'] = self.opt.gpu_ids
        str_ids = self.opt.gpu_ids.split(',')
        self.opt.gpu_ids = []
        for str_id in str_ids:
            id = int(str_id)
            if id >= 0:
                self.opt.gpu_ids.append(id)
        if len(self.opt.gpu_ids) > 0:
            self.opt.device = torch.device('cuda')
        else:
            self.opt.device = torch.device('cpu')

        #self.opt.anchors = [[10,13], [16,30], [33,23], [30, 61], [62, 45], [59, 119], [116, 90], [156, 198], [373, 326]]
        # self.opt.class_names = ['car', 'person', 'fire']

        if self.opt.print_options:
            self.print_options()

        return self.opt