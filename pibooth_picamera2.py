try:
    import pibooth
except Exception as e:
    print(e)
    exit()
# import picamera2
import pygame
import time
import cv2
import PIL


from libcamera import Transform
from io import BytesIO
from PIL import Image

from pibooth.utils import LOGGER
from pibooth.camera.rpi import RpiCamera
from pibooth.language import get_translated_text


# Release version
__version__ = "1.0.2"

@pibooth.hookimpl 
def pibooth_configure(cfg):
    """Declare new configuration options.
    """
    cfg.add_option('CAMERA','use_picamera2',1,
                    "Boolean value to use Picamera2 library and the new raspberry pi camera v3")

# This hook returns the custom camera proxy.
# It is defined here because yield statement in a hookwrapper with a 
# similar name is used to invoke it later. But check first if other cameras
# are installed or if the user specifically asks for this
@pibooth.hookimpl
def pibooth_setup_camera(cfg):
    
    rpi_picamera2_proxy = None
    if cfg.get('CAMERA','use_picamera2'):
        rpi_picamera2_proxy = get_rpi_picamera2_proxy()
    
    if not rpi_picamera2_proxy:
        LOGGER.info('Could not find picamera2')
        LOGGER.info('Attempting to configure other cameras')
        return
    return Rpi_Picamera2(rpi_picamera2_proxy) 


def get_rpi_picamera2_proxy():
    try:
        from picamera2 import Picamera2
        cam = Picamera2()
    except Exception as e:
        cam = None 
    if cam:
        LOGGER.info('Use Picamera2 library')
        return cam
    return None 


class Rpi_Picamera2(RpiCamera):

    """Raspberry pi module v3 camera management
    """
    # Maximum resolution of the camera v3 module
    MAX_RESOLUTION = (4608,2592)
    IMAGE_EFFECTS = [u'none',
                     u'blur',
                     u'contour',
                     u'detail',
                     u'edge_enhance',
                     u'edge_enhance_more',
                     u'emboss',
                     u'find_edges',
                     u'smooth',
                     u'smooth_more',
                     u'sharpen']

    def __init__(self, camera_proxy):
        super().__init__(camera_proxy)
        self._preview_config = None
        self._capture_config = None
        
    def _specific_initialization(self):
        """Camera initialization.
        """
        resolution = self._transform()
        # Create preview configuration
        self._preview_config = self._cam.create_preview_configuration(main={'size':resolution}, 
                                transform=Transform(hflip=self.preview_flip))
        
        self._capture_config = self._cam.create_still_configuration(main={'size':resolution},
                                transform=Transform(hflip=self.capture_flip))
    
    def _show_overlay(self, text, alpha):
        """Add an image as an overlay
        """
        if self._window:
            # return a rect the size of the preview window(Keep overlay the same with
            # rotate=False)
            rect = self.get_rect(self.MAX_RESOLUTION, rotate=False)

            # Create an image padded to the required size
            size = (((rect.width + 31) // 32) * 32, ((rect.height + 15) // 16) * 16)

            # return a pil image with timeout on it
            image = self.build_overlay(size, str(text), alpha)

            # convert pil image to pygame.Surface
            self._overlay = pygame.image.frombuffer(image.tobytes(),size,'RGBA')
            self.update_preview()

    def _hide_overlay(self):
        """"""
        if self._overlay:
            self._overlay = None
            self.update_preview()

    def _post_process_capture(self,capture_data):

        img = super()._post_process_capture(capture_data)
        return self._rotate_image(img)
        

    def _transform(self):
        """Return tuple for configuring picamera"""
        if self.preview_rotation in (90,270):
            return self.resolution[1], self.resolution[0]
        else:
            return self.resolution
    
    def _rotate_image(self, image:PIL.Image.Image | pygame.Surface):
        """Rotate image clockwise"""
        # Camera rotation is the same for both preview and capture
        if self.capture_rotation != 0 and self.preview_rotation != 0:
            if isinstance(image, PIL.Image.Image):
                return image.transpose(getattr(Image,f'ROTATE_{self.capture_rotation}'))
            return pygame.transform.rotate(image,360-self.preview_rotation)
        return image
        
    def get_rect(self, max_size, rotate=True):
        """Get preview window. Rotate window to match camera rotation.
        Not implemented in picamera2. 
        """
        if self.preview_rotation in (90,270) and rotate:
            rect = super().get_rect(max_size)
            rect.width, rect.height = rect.height, rect.width 
            return rect
        return super().get_rect(max_size) 

    def preview(self, window, flip=True):
        if self._cam._preview:
            # Preview is still running
            return
        # create rect dimensions for preview window
        self._window = window
        
        # if the camera image has been flipped don't flip a second time
        # The flip overrides any previous flip value
        if self.preview_flip != flip:
            self.preview_flip = flip
            # if rotation is 90 or 270 degrees, vertically flip the image
            # when the image is rotated, the horizontally flipping is done
            # by vertically flipping it.
            if self.preview_rotation in (90,270):
                self._preview_config['transform'] = Transform(vflip=flip)
            else:
                self._preview_config['transform'] = Transform(hflip=flip)

        self._cam.configure(self._preview_config)
        self._cam.start()
        self.update_preview()

    def preview_countdown(self, timeout, alpha=60):
        """Show a countdown of 'timeout' seconds on the preview.
        Returns when the countdown is finished.
        Uses the same implementation as the parent but changes preview to _preview
        because of the difference between picamera and picamera2.
        """
        timeout = int(timeout)
        if timeout < 1:
            raise ValueError('Start time shall be greater than 0')
        if not self._cam._preview:
            raise RuntimeError('Preview shall be started first')
        time_stamp = time.time() 
        
        while timeout > 0:
            self._show_overlay(timeout, alpha)
            if time.time()-time_stamp > 1:
                timeout -= 1
                time_stamp = time.time()
                self._hide_overlay()
        # Keep smile for 1 second
        while time.time()-time_stamp < 1:
            self._show_overlay(get_translated_text('smile'), alpha)
        # Remove smile
        # _hide_overlay sets self._overlay = None otherwise app stalls after capture method is called
        self._hide_overlay()

    def preview_wait(self, timeout, alpha=60):
        time_stamp = time.time()
        # Keep preview for the duration of timeout
        while time.time() - time_stamp < timeout:
            self.update_preview()
        time_stamp = time.time()
        # Keep smile for 1 second
        while time.time()-time_stamp < 1:
            self._show_overlay(get_translated_text('smile'), alpha)
        self._hide_overlay()

    def update_preview(self):
        """Capture image and update screen with image"""
        array = self._cam.capture_array('main')
        rect = self.get_rect(self.MAX_RESOLUTION)
        # Resize high resolution image to fit smaller window
        res = cv2.resize(array, dsize=(rect.width,rect.height), 
                interpolation=cv2.INTER_CUBIC)
        # RGBX is 32 bit and has an unused 8 bit channel described as X
        # XBGR is used in the preview configuration
        pg_image = pygame.image.frombuffer(res.data, 
                    (rect.width, rect.height), 'RGBX')
        pg_image = self._rotate_image(pg_image)
        screen_rect = self._window.surface.get_rect()
        self._window.surface.blit(pg_image,
                                pg_image.get_rect(center=screen_rect.center))
        if self._overlay:
            self._window.surface.blit(self._overlay, self._overlay.get_rect(center=screen_rect.center))
        pygame.display.update() 

    def stop_preview(self):
        if self._cam._preview:
            # Use method implemented in the parent class
            super().stop_preview()
            LOGGER.info('Sopped preview')
            
    def capture(self, effect=None):
        """Capture a new picture in a file.
        """
        effect = str(effect).lower()
        if effect not in self.IMAGE_EFFECTS:
            LOGGER.info(f'{effect} not in capture effects')
        if effect != 'none' and effect in self.IMAGE_EFFECTS:
            LOGGER.info(f'{self.__class__.__name__} has not been implemented with any effects')

        stream = BytesIO()
        
        self._cam.switch_mode(self._capture_config)
        self._cam.capture_file(stream, format='jpeg')

        self._captures.append(stream)
        # Reconfigure and Stop camera before next preview
        self._cam.switch_mode(self._preview_config)
        self._cam.stop()
       

    def quit(self):
        """Close camera
        """
        self._cam.close()