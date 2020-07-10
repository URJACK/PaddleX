#copyright (c) 2020 PaddlePaddle Authors. All Rights Reserve.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from six import text_type as _text_type
import argparse
import sys
from utils import logging 
import paddlex as pdx

def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model_dir",
        "-m",
        type=_text_type,
        default=None,
        help="define model directory path")
    parser.add_argument(
        "--save_dir",
        "-s",
        type=_text_type,
        default=None,
        help="path to save inference model")
    parser.add_argument(
        "--fixed_input_shape",
        "-fs",
        default=None,
        help="export openvino model with  input shape:[h,w]")
    return parser


    


def export_openvino_model(model, args):
    if model.model_type == "detector" or model.__class__.__name__ == "FastSCNN":
        logging.error(
            "Only image classifier models and semantic segmentation models(except FastSCNN) are supported to export to openvino")
    try:
        import x2paddle
        if x2paddle.__version__ < '0.7.4':
            logging.error("You need to upgrade x2paddle >= 0.7.4")
    except:
        logging.error(
            "You need to install x2paddle first, pip install x2paddle>=0.7.4")
        
    from x2paddle.op_mapper.paddle_op_mapper import PaddleOpMapper
    mapper = PaddleOpMapper()
    mapper.convert(model.test_prog, args.save_dir)

    import mo.main as mo
    from mo.utils.cli_parser import get_onnx_cli_parser
    onnx_parser = get_onnx_cli_parser()
    onnx_parser.add_argument("--model_dir",type=_text_type)
    onnx_parser.add_argument("--save_dir",type=_text_type)
    onnx_parser.add_argument("--fixed_input_shape")
    onnx_input = os.path.join(args.save_dir, 'x2paddle_model.onnx')
    onnx_parser.set_defaults(input_model=onnx_input)
    onnx_parser.set_defaults(output_dir=args.save_dir)
    shape = '[1,3,'
    shape =  shape + args.fixed_input_shape[1:]
    onnx_parser.set_defaults(input_shape = shape)
    mo.main(onnx_parser,'onnx')


def main():
    parser = arg_parser()
    args = parser.parse_args()
    assert args.model_dir is not None, "--model_dir should be defined while exporting openvino model"
    assert args.save_dir is not None, "--save_dir should be defined to create openvino model"
    model = pdx.load_model(args.model_dir)
    if model.status == "Normal" or model.status == "Prune":
        logging.error(
            "Only support inference model, try to export model first as below,",
            exit=False)
    export_openvino_model(model, args)

if  __name__ == "__main__":
    main()


