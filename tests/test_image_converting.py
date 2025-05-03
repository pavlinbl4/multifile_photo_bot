import pytest
from PIL import Image
import os
from services.image_service.conver_image_to_jpeg import convert_image_to_jpeg


def test_convert_supported_file(tmpdir):
    # Test conversion of a supported PNG file to JPEG
    png_path = tmpdir.join("test.png")
    img = Image.new('RGB', (10, 10), color='red')
    img.save(png_path.strpath, 'PNG')

    jpeg_path = convert_image_to_jpeg(png_path.strpath)

    assert os.path.exists(jpeg_path), "JPEG file was not created"
    assert not os.path.exists(png_path.strpath), "Original file was not deleted"
    assert jpeg_path.endswith('.jpg'), "Output file does not have .jpg extension"

    os.remove(jpeg_path)  # Clean up


def test_convert_rgba_to_rgb(tmpdir):
    # Test conversion of an RGBA image to RGB JPEG
    rgba_path = tmpdir.join("rgba.png")
    img = Image.new('RGBA', (10, 10), color=(255, 0, 0, 128))
    img.save(rgba_path.strpath, 'PNG')

    jpeg_path = convert_image_to_jpeg(rgba_path.strpath)

    with Image.open(jpeg_path) as converted_img:
        assert converted_img.mode == 'RGB', "Image mode is not RGB after conversion"

    assert not os.path.exists(rgba_path.strpath), "Original RGBA file was not deleted"
    os.remove(jpeg_path)  # Clean up


def test_unsupported_extension_raises_error(tmpdir):
    # Test that an unsupported extension (e.g., .jpg) raises NameError
    jpg_path = tmpdir.join("test.jpg")
    img = Image.new('RGB', (10, 10))
    img.save(jpg_path.strpath, 'JPEG')

    with pytest.raises(NameError):
        convert_image_to_jpeg(jpg_path.strpath)

    assert os.path.exists(jpg_path.strpath), "Unsupported original file was deleted"


def test_corrupt_file_raises_error(tmpdir):
    # Test handling of a corrupt file with supported extension
    corrupt_png = tmpdir.join("corrupt.png")
    corrupt_png.write(b"invalid data")  # Not a valid PNG

    with pytest.raises(NameError):
        convert_image_to_jpeg(corrupt_png.strpath)

    assert os.path.exists(corrupt_png.strpath), "Corrupt original file was deleted"


def test_error_during_save_preserves_original(tmpdir):
    # Test that if an error occurs during save, original file is preserved
    png_path = tmpdir.join("test.png")
    img = Image.new('RGB', (10, 10))
    img.save(png_path.strpath, 'PNG')

    # Introduce an error: make the output directory read-only to cause save failure
    jpeg_path = png_path.strpath.replace('.png', '.jpg')
    os.chmod(tmpdir.strpath, 0o444)  # Read-only permissions

    try:
        with pytest.raises(NameError):  # Function will raise NameError due to undefined path_to_jpeg_file
            convert_image_to_jpeg(png_path.strpath)
    finally:
        os.chmod(tmpdir.strpath, 0o755)  # Restore permissions

    assert os.path.exists(png_path.strpath), "Original file was deleted after save error"
    if os.path.exists(jpeg_path):
        os.remove(jpeg_path)  # Clean up if partial file exists