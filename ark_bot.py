import cv2
import numpy as np
import pyautogui
import time
#import keyboard
from PIL import ImageGrab
import threading

class ArkNavigationBot:
    def __init__(self, template_path, target_x, target_y, confidence_threshold=0.7):
        """
        Initialize the Ark first-person navigation bot
        
        Args:
            template_path (str): Path to the landmark/location template PNG image
            target_x (int): X coordinate where the landmark should appear on screen
            target_y (int): Y coordinate where the landmark should appear on screen
            confidence_threshold (float): Minimum confidence for template matching
        """
        self.template = cv2.imread(template_path, cv2.IMREAD_COLOR)
        if self.template is None:
            raise ValueError(f"Could not load template image from {template_path}")
        
        self.template_gray = cv2.cvtColor(self.template, cv2.COLOR_BGR2GRAY)
        self.template_h, self.template_w = self.template_gray.shape
        
        self.confidence_threshold = confidence_threshold
        self.target_position = (target_x, target_y)
        self.position_tolerance = 50  # Pixels tolerance for "aligned"
        self.running = False
        
        # Movement keys for Ark
        self.keys = {
            'forward': '=',
            'backward': "'", 
            'left': '[',
            'right': ']'
        }
        
        # Movement parameters
        self.movement_duration = 0.01  # Short bursts for fine control 0.05
        self.large_movement_threshold = 200  # For larger corrections
        self.large_movement_duration = 0.046 #0.15
        
        # Disable pyautogui failsafe
        pyautogui.FAILSAFE = False
        
    def capture_screen(self):
        """Capture the current screen"""
        screenshot = ImageGrab.grab()
        return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    
    def find_landmark(self, screen):
        """
        Find landmark position using template matching with rotation handling
        
        Args:
            screen: Screenshot of the game
            
        Returns:
            tuple: (center_x, center_y, confidence, rotation_angle) or None if not found
        """
        screen_gray = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
        
        # Test multiple scales and rotations for better detection
        #scales = [1.0, 0.9, 1.1, 0.8, 1.2]
        scales = [1.0, 0.9, 1.1, 0.8, 1.2]
        #rotations = [0, -5, 5, -10, 10, -15, 15, -20, 20, -25, 25, -30, 30, -35, 35, -40, 40, -45, 45]  # Test common rotation angles
        #rotations = [0, -5, 5, -10, 10, -15, 15, -20, 20]  # Test common rotation angles
        rotations = [0, -5, 5, 180, 90, -90]  # Test common rotation angles
        
        best_match = None
        best_confidence = 0
        best_rotation = 0
        
        for rotation in rotations:
            for scale in scales:
                print(f"Testing Scale: {scale}, Rotation: {rotation}")
                # Prepare template with scale and rotation
                if scale != 1.0:
                    new_w = int(self.template_w * scale)
                    new_h = int(self.template_h * scale)
                    scaled_template = cv2.resize(self.template_gray, (new_w, new_h))
                else:
                    scaled_template = self.template_gray
                    new_w, new_h = self.template_w, self.template_h
                
                # Apply rotation if needed
                if rotation != 0:
                    center = (new_w // 2, new_h // 2)
                    rotation_matrix = cv2.getRotationMatrix2D(center, rotation, 1.0)
                    rotated_template = cv2.warpAffine(scaled_template, rotation_matrix, (new_w, new_h))
                else:
                    rotated_template = scaled_template
                
                # Skip if template is larger than screen
                if rotated_template.shape[1] > screen_gray.shape[1] or rotated_template.shape[0] > screen_gray.shape[0]:
                    continue
                
                try:
                    result = cv2.matchTemplate(screen_gray, rotated_template, cv2.TM_CCOEFF_NORMED)
                    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                    
                    '''
                    if max_val > best_confidence:
                        best_confidence = max_val
                        # Calculate center of matched template
                        center_x = max_loc[0] + rotated_template.shape[1] // 2
                        center_y = max_loc[1] + rotated_template.shape[0] // 2
                        best_match = (center_x, center_y, max_val)
                        best_rotation = rotation
                        best_scale = scale
                    '''    
                    best_confidence = max_val
                    # Calculate center of matched template
                    center_x = max_loc[0] + rotated_template.shape[1] // 2
                    center_y = max_loc[1] + rotated_template.shape[0] // 2
                    best_match = (center_x, center_y, max_val)
                    best_rotation = rotation
                    best_scale = scale
                    
                    if best_confidence >= self.confidence_threshold:
                        return (*best_match, best_rotation, best_scale)
                    
                except cv2.error:
                    # Skip if template matching fails (e.g., template too large)
                    continue
        
        #if best_confidence >= self.confidence_threshold:
        #    return (*best_match, best_rotation, best_scale)
        
        return None
    
    def find_landmark_old(self, screen):
        """
        Find landmark position using template matching
        
        Args:
            screen: Screenshot of the game
            
        Returns:
            tuple: (center_x, center_y, confidence) or None if not found
        """
        screen_gray = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
        
        # Template matching with multiple scales for better detection
        scales = [1.0, 0.9, 1.1, 0.8, 1.2]
        best_match = None
        best_confidence = 0
        
        for scale in scales:
            if scale != 1.0:
                # Resize template
                new_w = int(self.template_w * scale)
                new_h = int(self.template_h * scale)
                scaled_template = cv2.resize(self.template_gray, (new_w, new_h))
            else:
                scaled_template = self.template_gray
                new_w, new_h = self.template_w, self.template_h
            
            # Skip if template is larger than screen
            if new_w > screen_gray.shape[1] or new_h > screen_gray.shape[0]:
                continue
            
            result = cv2.matchTemplate(screen_gray, scaled_template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            if max_val > best_confidence:
                best_confidence = max_val
                # Calculate center of matched template
                center_x = max_loc[0] + new_w // 2
                center_y = max_loc[1] + new_h // 2
                best_match = (center_x, center_y, max_val)
                best_scale = scale
        
        if best_confidence >= self.confidence_threshold:
            return (*best_match, 0, best_scale)
        
        return None
    
    def calculate_movement_needed(self, landmark_pos):
        """
        Calculate required movement to align landmark with target position
        
        Args:
            landmark_pos: Current landmark position (x, y)
            
        Returns:
            tuple: (horizontal_offset, vertical_offset)
        """
        dx = self.target_position[0] - landmark_pos[0]
        dy = self.target_position[1] - landmark_pos[1]
        
        return (dx, dy)
    
    def execute_movement(self, dx, dy):
        """
        Execute movement commands to align the view
        
        Args:
            dx: Horizontal offset (positive = landmark needs to move right, so we move left)
            dy: Vertical offset (positive = landmark needs to move down, so we move backward)
        """
        # Determine movement duration based on offset magnitude
        abs_dx = abs(dx)
        abs_dy = abs(dy)
        
        h_duration = self.large_movement_duration if abs_dx > self.large_movement_threshold else self.movement_duration
        v_duration = self.large_movement_duration if abs_dy > self.large_movement_threshold else self.movement_duration
        
        # Horizontal movement (strafe to adjust horizontal view)
        if abs_dx > self.position_tolerance:
            if dx > 0:
                # Landmark needs to move right, so we strafe left
                self.press_key(self.keys['left'], h_duration * abs_dx/100)
                print(f"Moving left (strafe) - offset: {dx}")
            else:
                # Landmark needs to move left, so we strafe right
                self.press_key(self.keys['right'], h_duration  * abs_dx/100)
                print(f"Moving right (strafe) - offset: {dx}")
        
        # Vertical movement (forward/backward to adjust distance/vertical view)
        if abs_dy > self.position_tolerance:
            if dy < 0:
                # Landmark needs to move up, move backward
                self.press_key(self.keys['backward'], v_duration * abs_dx/110)
                print(f"Moving backward - offset: {dy}")
            else:
                # Landmark needs to move down, move forward
                self.press_key(self.keys['forward'], v_duration * abs_dx/110)
                print(f"Moving forward - offset: {dy}")
    
    def press_key(self, key, duration):
        """Press and hold a key for specified duration"""
        print (f"Loop Interval: {duration}")
        start_time = time.time()
        pyautogui.keyDown('backslash')
        pyautogui.keyDown(key)
        
        while time.time() - start_time < duration:
            pass
        pyautogui.keyUp(key)
        print (f"Elapsed Time: {time.time() - start_time}")
            #time.sleep(duration)
            #pyautogui.keyUp(key)
        pyautogui.keyUp('backslash')
    
    def is_aligned(self, landmark_pos):
        """Check if landmark is sufficiently aligned with target position"""
        dx = abs(self.target_position[0] - landmark_pos[0])
        dy = abs(self.target_position[1] - landmark_pos[1])
        
        return dx <= self.position_tolerance and dy <= self.position_tolerance
    
    def draw_debug_overlay(self, screen, landmark_pos=None):
        """
        Draw debug information on screen (optional visualization)
        
        Args:
            screen: Current screen capture
            landmark_pos: Current landmark position if found
        """
        debug_screen = screen.copy()
        
        # Draw target position
        cv2.circle(debug_screen, self.target_position, 10, (0, 255, 0), 2)
        cv2.putText(debug_screen, "TARGET", 
                   (self.target_position[0] - 30, self.target_position[1] - 15),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        # Draw current landmark position if found
        if landmark_pos:
            cv2.circle(debug_screen, (int(landmark_pos[0]), int(landmark_pos[1])), 8, (0, 0, 255), 2)
            cv2.putText(debug_screen, "LANDMARK", 
                       (int(landmark_pos[0]) - 35, int(landmark_pos[1]) - 15),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
            
            # Draw line between target and current position
            cv2.line(debug_screen, self.target_position, 
                    (int(landmark_pos[0]), int(landmark_pos[1])), (255, 0, 0), 1)
        
        return debug_screen
    
    def run_bot(self, show_debug=False):
        """
        Main bot loop
        
        Args:
            show_debug (bool): Whether to show debug visualization window
        """
        print("Ark First-Person Navigation Bot started!")
        print("Controls:")
        print("- 'q': Quit bot")
        print("- 'p': Pause/Resume bot")
        print("Make sure Ark Survival Ascended is the active window.")
        print(f"Target position: {self.target_position}")
        
        self.running = True
        paused = False
        
        if show_debug:
            cv2.namedWindow('Debug View', cv2.WINDOW_NORMAL)
            cv2.resizeWindow('Debug View', 800, 600)
        
        while self.running:
            try:
                '''
                # Check for control commands
                if keyboard.is_pressed('q'):
                    print("Quit command received")
                    break
                
                if keyboard.is_pressed('p'):
                    paused = not paused
                    print(f"Bot {'paused' if paused else 'resumed'}")
                    time.sleep(0.5)  # Prevent multiple toggles
                
                if paused:
                    time.sleep(0.1)
                    continue
                '''
                # Capture screen
                screen = self.capture_screen()
                
                # Find landmark
                landmark_result = self.find_landmark(screen)
                
                if landmark_result:
                    landmark_x, landmark_y, confidence, rotation, scale = landmark_result
                    print(f"Landmark found at ({landmark_x:.1f}, {landmark_y:.1f}, Rotation: {rotation}, Scale: {scale}) "
                          f"with confidence {confidence:.3f}")
                    
                    # Check if already aligned
                    if self.is_aligned((landmark_x, landmark_y)):
                        print("✓ Landmark is aligned with target!")
                        if show_debug:
                            debug_screen = self.draw_debug_overlay(screen, (landmark_x, landmark_y))
                            cv2.imshow('Debug View', debug_screen)
                            cv2.waitKey(1)
                        time.sleep(0.5)
                        return True
                    
                    # Calculate and execute movement
                    dx, dy = self.calculate_movement_needed((landmark_x, landmark_y))
                    print(f"Offset from target: dx={dx:.1f}, dy={dy:.1f}")
                    
                    self.execute_movement(dx, dy)
                    
                    # Show debug view if enabled
                    if show_debug:
                        debug_screen = self.draw_debug_overlay(screen, (landmark_x, landmark_y))
                        cv2.imshow('Debug View', debug_screen)
                        cv2.waitKey(1)
                    
                else:
                    print("Landmark not found in current view - adjust your view manually")
                    if show_debug:
                        debug_screen = self.draw_debug_overlay(screen)
                        cv2.imshow('Debug View', debug_screen)
                        cv2.waitKey(1)
                    return False
                
                # Small delay to prevent excessive CPU usage
                time.sleep(0.1)
                
            except Exception as e:
                print(f"Error in bot loop: {e}")
                break
        
        self.running = False
        if show_debug:
            cv2.destroyAllWindows()
        print("Bot stopped.")
    
    def stop_bot(self):
        """Stop the bot"""
        self.running = False

def main():
    print("=== Ark Survival Ascended First-Person Navigation Bot ===")
    print()
    
    # Configuration
    template_path = input("Enter path to landmark template image (default: landmark.png): ").strip()
    if not template_path:
        template_path = '.\icons1440\teleporter_target_1150x475_260x400.png'     # 1150 + 130 = 1280  475 + 200 = 675
    
    print("\nSet target position where the landmark should appear on screen:")
    try:
        target_x = int(input("Target X coordinate (default: center ex. 1280): ") or pyautogui.size()[0] // 2)
        target_y = int(input("Target Y coordinate (default: center ex. 768): ") or pyautogui.size()[1] // 2)
    except ValueError:
        print("Using screen center as default target")
        target_x, target_y = pyautogui.size()[0] // 2, pyautogui.size()[1] // 2
    
    confidence = float(input("Confidence threshold (0.0-1.0, default: 0.7): ") or "0.7")
    
    show_debug = input("Show debug visualization? (y/n, default: n): ").lower().startswith('y')
    
    try:
        # Initialize bot
        bot = ArkNavigationBot(template_path, target_x, target_y, confidence)
        
        print(f"\nBot Configuration:")
        print(f'- Template: {template_path}')
        print(f"- Target position: ({target_x}, {target_y})")
        print(f"- Confidence threshold: {confidence}")
        print(f"- Debug view: {'Enabled' if show_debug else 'Disabled'}")
        
        print("\nInstructions:")
        print("1. Position yourself in Ark so the landmark is visible on screen")
        print("2. Alt+Tab to this window and press Enter to start")
        print("3. The bot will move your character to align the landmark with target position")
        print("4. Press 'q' to quit, 'p' to pause/resume")
        
        input("\nPress Enter to start the bot...")
        
        # Give time to switch to game window
        print("Starting in 5 seconds...")
        time.sleep(5)
        
        # Run bot
        bot.run_bot(show_debug)
        
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure you have the required packages installed:")
        print("pip install opencv-python pyautogui pillow keyboard numpy")

if __name__ == "__main__":
    main()