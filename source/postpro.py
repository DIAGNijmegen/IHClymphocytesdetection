import argparse

from digitalpathology.image.io import imagereader as dptimagereader
import multiresolutionimageinterface as mir

import mahotas as mh
from skimage.filters import gaussian
from skimage.transform import rescale

def load_array_from_input(path):

    # load the predictions tiff, if it's not already a loaded ImageReader object
    template_image = dptimagereader.ImageReader(
                                        image_path=path,
                                        spacing_tolerance=spacing_tolerance,
                                        input_channels=None
                                        )
    # get the level of the correct pixel spacing, which is 0 in this case
    template_level = template_image.level(spacing=pixel_spacing)
    # turn the predictions tiff to an array of dimensions (26322, 11871, 3), which is 8 times smaller than the mrxs
    # NOTE: here we use the version of digitalpathology.image.imagereader.py from the folder LymphoctyeDetection_UNET, but I modified it, adding the getter content() form the pathology_fast_inference version.
    predictions_array = template_image.content(spacing=template_image.spacings[template_level]).squeeze()

    return predictions_array

def postpro(input):
    predictions_array = load_array_from_input(input)

    number_of_dimensions = result_patch_temp.ndim
    if number_of_dimensions < 3:
        image = predictions_array / 255.0
    else:
        image = predictions_array[:,:,2] / 255.0

    im_pred_center = (image).astype(np.float)

    im_pred_center_th = im_pred_center * (im_pred_center >= threshold)
    # im_pred_center_th=im_pred_center*(im_pred_center>=0.6)
    # todo: WHEN GAUSSIAN IS USED, MANY PREDICTIONS ARE NOT SEEN, I DON'T KNOW HOW TO SOLVE THIS RELIABLY, we're keeping it in
    im_pred_center_gauss=gaussian(im_pred_center_th, 2)

    im_pred_center_rmax = mh.regmax(im_pred_center_gauss,15)

    im_pred_center_lab,nr=mh.label(im_pred_center_rmax)

    im_pred_center_binary = im_pred_center_lab * (im_pred_center_lab >= 1)

def write_output_tif(input_mask, output_path,output_spacing):
    tile_size = 512 #fixed this value, because it's the fasted tile size for loading
    pixel_size_vec = mir.vector_double()
    pixel_size_vec.push_back(output_spacing)
    pixel_size_vec.push_back(output_spacing)
    dim_y, dim_x,_ = input_mask.shape
    writer = mir.MultiResolutionImageWriter()


    writer.openFile(output_path)
    writer.setTileSize(tile_size)
    writer.setCompression(mir.LZW)
    writer.setDataType(mir.UChar)
    writer.setColorType(mir.Monochrome)
    writer.writeImageInformation(dim_x, dim_y)
    writer.setSpacing(pixel_size_vec)

    for y_indx in range(0, dim_y, tile_size):
        for x_indx in range(0, dim_x, tile_size):

            tmp_patch = input_mask[y_indx:y_indx + tile_size,x_indx:x_indx + tile_size]
            if np.any(tmp_patch):
                writer.writeBaseImagePartToLocation(tmp_patch.flatten().astype(np.uint8), x_indx, y_indx)
    writer.finishImage()

if __name__ == '__main__':
    argument_parser = argparse.ArgumentParser(description='Post processing which outputs a thresholded .tiff')

    argument_parser.add_argument('-i', '--input', required=True, type=str, help='path to file to be post-processed')
    argument_parser.add_argument('-st', '--spacing_tolerance', required=True, type=float, help='spacing tolerance')
    argument_parser.add_argument('-ps', '--pixel_spacing', required=True, type=float, help='pixel spacing')
    argument_parser.add_argument('-th', '--threshold', required=True, type=float, help='at which input mask is thresholded')
    argument_parser.add_argument('-o', '--output_path', required=True, type=str, help='path for output')
    argument_parser.add_argument('-os', '--output_spacing', required=True, type=float, help='spacing for output')

    arguments = vars(argument_parser.parse_args())

    input= arguments['input']
    spacing_tolerance= arguments['spacing_tolerance']
    pixel_spacing= arguments['pixel_spacing']
    threshold= arguments['threshold']
    output_path= arguments['output_path']
    output_spacing = arguments['output_spacing']

    array = load_array_from_input(input)
    postpro_array = postpro(array)
    write_output_tif(postpro_array, output_path, output_spacing)
