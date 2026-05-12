import os
import subprocess
import cv2
import numpy as np
from typing import Tuple, List, Dict
import json


class LipSyncEngine:
    """Handle audio-video synchronization and REAL lip-sync"""

    def __init__(self):
        self.frame_rate = 30

    def get_audio_duration(self, audio_file: str) -> float:
        """Get audio duration in seconds using ffmpeg"""
        try:
            cmd = [
                'ffprobe',
                '-v',
                'error',
                '-show_entries',
                'format=duration',
                '-of',
                'default=noprint_wrappers=1:nokey=1',
                audio_file
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True
            )

            return float(result.stdout.strip())

        except Exception:
            try:
                import librosa

                y, sr = librosa.load(audio_file)
                return len(y) / sr

            except Exception:
                return 5.0

    def get_video_duration(self, video_file: str) -> float:
        """Get video duration"""

        try:
            cap = cv2.VideoCapture(video_file)

            fps = cap.get(cv2.CAP_PROP_FPS)

            frame_count = int(
                cap.get(cv2.CAP_PROP_FRAME_COUNT)
            )

            duration = frame_count / fps

            cap.release()

            return duration

        except Exception:
            return 8.0

    def get_video_info(self, video_file: str) -> Dict:
        """Get video information"""

        cap = cv2.VideoCapture(video_file)

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        fps = cap.get(cv2.CAP_PROP_FPS)

        frame_count = int(
            cap.get(cv2.CAP_PROP_FRAME_COUNT)
        )

        duration = frame_count / fps

        cap.release()

        return {
            'width': width,
            'height': height,
            'fps': fps,
            'frame_count': frame_count,
            'duration': duration
        }

    def create_looped_video(
        self,
        video_file: str,
        target_duration: float,
        output_file: str
    ) -> str:
        """
        Loop or trim video to match audio duration
        """

        video_info = self.get_video_info(video_file)

        video_duration = video_info['duration']

        if abs(video_duration - target_duration) < 0.5:
            return video_file

        if target_duration <= video_duration:
            self._trim_video(
                video_file,
                output_file,
                target_duration
            )

        else:
            self._loop_video(
                video_file,
                output_file,
                target_duration,
                video_duration
            )

        return output_file

    def _loop_video(
        self,
        input_video: str,
        output_video: str,
        target_duration: float,
        video_duration: float
    ):
        """Loop video"""

        loops_needed = int(
            np.ceil(target_duration / video_duration)
        ) + 1

        concat_file = output_video.replace(
            '.mp4',
            '_concat.txt'
        )

        with open(concat_file, 'w') as f:
            for _ in range(loops_needed):
                f.write(
                    f"file '{os.path.abspath(input_video)}'\n"
                )

        cmd = [
            'ffmpeg',
            '-y',
            '-f',
            'concat',
            '-safe',
            '0',
            '-i',
            concat_file,
            '-c',
            'copy',
            '-t',
            str(target_duration),
            output_video
        ]

        subprocess.run(
            cmd,
            capture_output=True
        )

        try:
            os.remove(concat_file)

        except Exception:
            pass

    def _trim_video(
        self,
        input_video: str,
        output_video: str,
        duration: float
    ):
        """Trim video"""

        cmd = [
            'ffmpeg',
            '-y',
            '-i',
            input_video,
            '-t',
            str(duration),
            '-c:v',
            'libx264',
            '-preset',
            'medium',
            output_video
        ]

        subprocess.run(
            cmd,
            capture_output=True
        )

    def merge_audio_video(
        self,
        video_file: str,
        audio_file: str,
        output_file: str
    ) -> str:
        """
        OLD basic merge method
        """

        audio_duration = self.get_audio_duration(audio_file)

        temp_video = output_file.replace(
            '.mp4',
            '_temp.mp4'
        )

        self.create_looped_video(
            video_file,
            audio_duration,
            temp_video
        )

        cmd = [
            'ffmpeg',
            '-y',
            '-i',
            temp_video,
            '-i',
            audio_file,
            '-c:v',
            'copy',
            '-c:a',
            'aac',
            '-map',
            '0:v:0',
            '-map',
            '1:a:0',
            output_file
        ]

        subprocess.run(
            cmd,
            capture_output=True,
            check=True
        )

        try:
            os.remove(temp_video)
        except Exception:
            pass

        return output_file

    def generate_api_lipsync(
        self,
        video_file: str,
        audio_file: str,
        output_file: str
    ) -> str:
        """
        High-quality API Lip Sync (e.g. Fal.ai or SyncLabs)
        """
        fal_key = os.getenv('FAL_KEY')
        if not fal_key:
            print("⚠️ FAL_KEY not found in environment. Using Local High-Quality LipSync (Option B).")
            # If no FAL_KEY is present, Option B uses real lipsync with GFPGAN
            try:
                return self.generate_real_lipsync(video_file, audio_file, output_file, use_gfpgan=True)
            except Exception as e:
                print(f"❌ Local LipSync failed: {e}")
                print("Falling back to basic merge.")
                return self.merge_audio_video(video_file, audio_file, output_file)
            
        print("Starting High-Quality API lip sync generation...")
        try:
            import fal_client
        except ImportError:
            print("⚠️ fal-client not installed. Please run: pip install fal-client")
            return self.merge_audio_video(video_file, audio_file, output_file)

        # Upload files to Fal temporary storage
        try:
            print("Uploading video to Fal storage...")
            video_url = fal_client.upload_file(video_file)
            print("Uploading audio to Fal storage...")
            audio_url = fal_client.upload_file(audio_file)
            
            print("Submitting to fal-ai/lipsync...")
            result = fal_client.subscribe(
                "fal-ai/lipsync",
                arguments={
                    "video_url": video_url,
                    "audio_url": audio_url
                },
                with_logs=True
            )
            
            # Download the resulting synced video
            import requests
            result_url = result.get('video', {}).get('url')
            if result_url:
                response = requests.get(result_url)
                with open(output_file, 'wb') as f:
                    f.write(response.content)
                print(f"✅ Generated synced video: {output_file}")
                return output_file
            else:
                raise Exception("No video URL returned from Fal API")
                
        except Exception as e:
            print(f"❌ API LipSync failed: {e}")
            print("Falling back to local Fast LipSync (GFPGAN disabled for speed).")
            return self.generate_real_lipsync(video_file, audio_file, output_file, use_gfpgan=False)

    def generate_real_lipsync(
        self,
        face_video: str,
        audio_file: str,
        output_file: str,
        use_gfpgan: bool = False
    ) -> str:
        """
        REAL AI Lip Sync using Wav2Lip (with optional GFPGAN enhancement)
        """

        print(f"Starting REAL lip sync generation... (GFPGAN: {use_gfpgan})")

        checkpoint_path = os.path.join(
            'models',
            'wav2lip',
            'wav2lip_gan.pth'
        )

        if not os.path.exists(checkpoint_path):
            raise Exception(
                f"Wav2Lip model not found: {checkpoint_path}"
            )

        if not os.path.exists(face_video):
            raise Exception(
                f"Face video not found: {face_video}"
            )

        if not os.path.exists(audio_file):
            raise Exception(
                f"Audio file not found: {audio_file}"
            )

        cmd = [
            'python',
            'Wav2Lip/inference.py',
            '--checkpoint_path',
            checkpoint_path,
            '--face',
            face_video,
            '--audio',
            audio_file,
            '--outfile',
            output_file
        ]
        
        if use_gfpgan:
            cmd.append('--gfpgan')

        print("Running command:")
        print(" ".join(cmd))

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )

        print(result.stdout)

        if result.returncode != 0:
            print(result.stderr)

            raise Exception(
                f"Wav2Lip failed:\n{result.stderr}"
            )

        print(f"Generated lip synced video: {output_file}")

        return output_file


class VideoProcessor:
    """Handle video processing"""

    def __init__(self):
        self.output_dir = os.path.join(
            os.path.dirname(__file__),
            '..',
            'processed_videos'
        )

        os.makedirs(
            self.output_dir,
            exist_ok=True
        )

    def blur_watermark(
        self,
        input_video: str,
        output_video: str,
        region: Tuple[int, int, int, int] = None
    ) -> str:
        """Blur watermark"""

        cap = cv2.VideoCapture(input_video)

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        fps = cap.get(cv2.CAP_PROP_FPS)

        if region is None:
            region = (
                int(width * 0.7),
                int(height * 0.85),
                width,
                height
            )

        x1, y1, x2, y2 = region

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')

        out = cv2.VideoWriter(
            output_video,
            fourcc,
            fps,
            (width, height)
        )

        while True:
            ret, frame = cap.read()

            if not ret:
                break

            frame[y1:y2, x1:x2] = cv2.GaussianBlur(
                frame[y1:y2, x1:x2],
                (51, 51),
                0
            )

            out.write(frame)

        cap.release()
        out.release()

        return output_video

    def get_video_codec_info(
        self,
        video_file: str
    ) -> Dict:
        """Codec info"""

        try:
            cmd = [
                'ffprobe',
                '-v',
                'error',
                '-select_streams',
                'v:0',
                '-show_entries',
                'stream=codec_name,codec_long_name,width,height',
                '-of',
                'json',
                video_file
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True
            )

            data = json.loads(result.stdout)

            return data['streams'][0]

        except Exception:
            return {}