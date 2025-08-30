import cv2 #type: ignore
import os
import numpy as np #type: ignore
import argparse

class ThermalPersonDetector:
    def __init__(self, threshold=150, min_area=300, max_area=10000):
        """
        Initialize the detector.
        :param threshold: pixel intensity threshold for detecting heat blobs (lower = more sensitive)
        :param min_area: minimum contour area to be considered a person
        :param max_area: maximum contour area to be considered a person
        """
        self.threshold = threshold
        self.min_area = min_area
        self.max_area = max_area

    def analyze_frame_intensity(self, frame):
        """Analyze frame intensity to help set threshold"""
        if len(frame.shape) == 3 and frame.shape[2] == 3:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        else:
            gray = frame.copy()
        
        # Calculate statistics
        min_val = np.min(gray)
        max_val = np.max(gray)
        mean_val = np.mean(gray)
        std_val = np.std(gray)
        
        print(f"Frame intensity - Min: {min_val}, Max: {max_val}, Mean: {mean_val:.1f}, Std: {std_val:.1f}")
        
        # Suggest threshold based on statistics
        suggested_threshold = int(mean_val + std_val)
        print(f"Suggested threshold: {suggested_threshold}")
        
        return gray, min_val, max_val, mean_val, std_val

    def process_frame(self, frame, debug=False):
        """
        Process a single frame: detect hot blobs and return annotated frame.
        :param frame: raw thermal frame (BGR or grayscale)
        :param debug: show debug information
        :return: annotated frame, list of bounding boxes
        """
        if len(frame.shape) == 3 and frame.shape[2] == 3:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        else:
            gray = frame.copy()

        if debug:
            print(f"Processing frame - Shape: {gray.shape}, Type: {gray.dtype}")

        # Blur and threshold
        blur = cv2.GaussianBlur(gray, (5,5), 0)
        _, thresh = cv2.threshold(blur, self.threshold, 255, cv2.THRESH_BINARY)

        if debug:
            # Show thresholded image
            cv2.imshow("Thresholded", thresh)
            cv2.imshow("Original Gray", gray)

        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if debug:
            print(f"Found {len(contours)} contours")

        boxes = []
        for i, cnt in enumerate(contours):
            area = cv2.contourArea(cnt)
            if self.min_area <= area <= self.max_area:
                x, y, w, h = cv2.boundingRect(cnt)
                boxes.append((x, y, w, h))
                
                # Draw bounding box
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.putText(frame, f"Person {i+1}", (x, y-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1)
                
                if debug:
                    print(f"  Contour {i+1}: Area={area:.0f}, Box=({x},{y},{w},{h})")
            elif debug and area > 0:
                print(f"  Contour {i+1}: Area={area:.0f} (filtered out)")

        return frame, boxes

    def detect_in_video(self, input_video_path, output_video_path=None, display=False, debug=False):
        """
        Process a full video and optionally save output.
        :param input_video_path: path to raw thermal video
        :param output_video_path: path to save annotated video (optional)
        :param display: show frames live (bool)
        :param debug: show debug information (bool)
        :return: list of frame-wise detections [(frame_number, [boxes])]
        """
        if not os.path.exists(input_video_path):
            print(f"❌ Error: Video file '{input_video_path}' not found!")
            return []
        
        cap = cv2.VideoCapture(input_video_path)
        if not cap.isOpened():
            print(f"❌ Error: Could not open video file '{input_video_path}'!")
            return []
        
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        print(f"📹 Video info: {width}x{height}, {fps:.1f} FPS, {total_frames} frames")
        print(f"🔧 Detection params: threshold={self.threshold}, min_area={self.min_area}, max_area={self.max_area}")

        if output_video_path:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

        frame_count = 0
        all_detections = []
        detection_count = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Analyze first frame for intensity
            if frame_count == 0:
                gray, min_val, max_val, mean_val, std_val = self.analyze_frame_intensity(frame)
                print(f"📊 First frame analysis:")
                print(f"   Intensity range: {min_val} - {max_val}")
                print(f"   Suggested threshold: {int(mean_val + std_val)}")
                print(f"   Current threshold: {self.threshold}")
                if self.threshold > max_val:
                    print(f"   ⚠️ Warning: Threshold {self.threshold} > max intensity {max_val}")
                    print(f"   💡 Try lowering threshold to {int(max_val * 0.8)}")

            # Process frame
            annotated_frame, boxes = self.process_frame(frame, debug=debug)
            all_detections.append((frame_count, boxes))
            
            if boxes:
                detection_count += len(boxes)
                if debug:
                    print(f"Frame {frame_count}: {len(boxes)} detections")

            if output_video_path:
                out.write(annotated_frame)
            
            if display:
                # Resize for display if too large
                display_frame = annotated_frame
                if width > 800 or height > 600:
                    scale = min(800/width, 600/height)
                    new_width = int(width * scale)
                    new_height = int(height * scale)
                    display_frame = cv2.resize(annotated_frame, (new_width, new_height))
                
                cv2.imshow("Thermal Detection", display_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            frame_count += 1
            
            # Progress indicator
            if frame_count % 50 == 0:
                progress = (frame_count / total_frames) * 100
                print(f"Progress: {progress:.1f}% ({frame_count}/{total_frames})")

        cap.release()
        if output_video_path:
            out.release()
        cv2.destroyAllWindows()
        
        print(f"\n🎯 Detection Summary:")
        print(f"   Total frames processed: {frame_count}")
        print(f"   Total detections: {detection_count}")
        print(f"   Frames with detections: {len([d for d in all_detections if d[1]])}")
        
        return all_detections

    def tune_parameters(self, video_path, test_frames=10):
        """Test different parameters to find optimal settings"""
        print(f"🔧 Tuning parameters on {test_frames} frames...")
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print("❌ Could not open video for parameter tuning")
            return
        
        # Test different thresholds
        thresholds = [100, 150, 200, 250, 300]
        min_areas = [200, 300, 500, 1000]
        
        best_params = None
        best_detections = 0
        
        for threshold in thresholds:
            for min_area in min_areas:
                self.threshold = threshold
                self.min_area = min_area
                
                detections = 0
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                
                for _ in range(test_frames):
                    ret, frame = cap.read()
                    if not ret:
                        break
                    
                    _, boxes = self.process_frame(frame)
                    detections += len(boxes)
                
                print(f"  Threshold={threshold}, MinArea={min_area}: {detections} detections")
                
                if detections > best_detections:
                    best_detections = detections
                    best_params = (threshold, min_area)
        
        cap.release()
        
        if best_params:
            print(f"\n✅ Best parameters: threshold={best_params[0]}, min_area={best_params[1]}")
            print(f"   Detections: {best_detections}")
            self.threshold, self.min_area = best_params
        else:
            print("❌ No detections found with any parameter combination")


def main():
    """Main function with command line arguments"""
    parser = argparse.ArgumentParser(description='Thermal Camera Person Detection')
    parser.add_argument('--video', '-v', default='thermal_video.mp4', 
                       help='Input video file path')
    parser.add_argument('--output', '-o', default='output_detected.mp4',
                       help='Output video file path')
    parser.add_argument('--threshold', '-t', type=int, default=150,
                       help='Detection threshold (lower = more sensitive)')
    parser.add_argument('--min-area', type=int, default=300,
                       help='Minimum contour area')
    parser.add_argument('--max-area', type=int, default=10000,
                       help='Maximum contour area')
    parser.add_argument('--display', '-d', action='store_true',
                       help='Display frames during processing')
    parser.add_argument('--debug', action='store_true',
                       help='Show debug information')
    parser.add_argument('--tune', action='store_true',
                       help='Tune parameters automatically')
    
    args = parser.parse_args()
    
    print("🔥 Thermal Camera Person Detection")
    print("=" * 40)
    
    # Initialize detector
    detector = ThermalPersonDetector(
        threshold=args.threshold,
        min_area=args.min_area,
        max_area=args.max_area
    )
    
    # Parameter tuning
    if args.tune:
        detector.tune_parameters(args.video)
    
    # Process video
    print(f"\n🎬 Processing video: {args.video}")
    detections = detector.detect_in_video(
        input_video_path=args.video,
        output_video_path=args.output,
        display=args.display,
        debug=args.debug
    )
    
    # Show sample detections
    if detections:
        print(f"\n📊 Sample detections (first 10 frames):")
        for frame_num, boxes in detections[:10]:
            if boxes:
                print(f"  Frame {frame_num}: {len(boxes)} detections")
            else:
                print(f"  Frame {frame_num}: No detections")
    else:
        print("❌ No frames were processed")


if __name__ == "__main__":
    main()
