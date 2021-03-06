import cv2
import numpy as np
import subprocess as sp
import shlex

class H265Writer:
    def __init__(self, outfile,fps, width, height):
        self.outfile = outfile
        self.fourcc = cv2.VideoWriter_fourcc(*'H265')
        self.fps = fps
        self.width = width
        self.height = height

        # Open ffmpeg application as sub-process
        # FFmpeg input PIPE: RAW images in BGR color format
        # FFmpeg output MP4 file encoded with HEVC codec.
        # Arguments list:
        # -y                   Overwrite output file without asking
        # -s {width}x{height}  Input resolution width x height (1344x756)
        # -pixel_format bgr24  Input frame color format is BGR with 8 bits per color component
        # -f rawvideo          Input format: raw video
        # -r {fps}             Frame rate: fps (25fps)
        # -i pipe:             ffmpeg input is a PIPE
        # -vcodec libx265      Video codec: H.265 (HEVC)
        # -pix_fmt yuv420p     Output video color space YUV420 (saving space compared to YUV444)
        # -crf 24              Constant quality encoding (lower value for higher quality and larger output file).
        # {output_filename}    Output file name: output_filename (output.mp4)
        self.process = sp.Popen(shlex.split(f'ffmpeg -y -s {width}x{height} -pixel_format bgr24 -f rawvideo -r {fps} -i pipe: -vcodec libx265 -pix_fmt yuv420p -crf 24 {output_filename}'), stdin=sp.PIPE)


    def write(self, frame):
        # Write raw video frame to input stream of ffmpeg sub-process.
        self.process.stdin.write(frame.tobytes())

    def close(self):
        # Close and flush stdin
        self.process.stdin.close()

        # Wait for sub-process to finish
        self.process.wait()

        # Terminate the sub-process
        self.process.terminate()

    def __del__(self):
        self.close()

if __name__=='__main__':
    width, height, n_frames, fps = 1344, 756, 50, 25  # 50 frames, resolution 1344x756, and 25 fps

    output_filename = 'output.mp4'

    cap = H265Writer(output_filename, fps, width, height)

    # Build synthetic video frames and write them to ffmpeg input stream.
    for i in range(n_frames):
        # Build synthetic image for testing ("render" a video frame).
        img = np.full((height, width, 3), 60, np.uint8)
        cv2.putText(img, str(i+1), (width//2-100*len(str(i+1)), height//2+100), cv2.FONT_HERSHEY_DUPLEX, 10, (255, 30, 30), 20)  # Blue number

        # Write raw video frame to input stream of ffmpeg sub-process.
        cap.write(img)

    cap.close()

