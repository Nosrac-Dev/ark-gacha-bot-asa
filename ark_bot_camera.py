import cv2
import numpy as np
import pyautogui
import time
import keyboard
from PIL import ImageGrab
import threading

class PIDController:
    def __init__(self, kp=1.0, ki=0.0, kd=0.0, setpoint=0.0):
        """
        PID Controller for smooth movement control
        
        Args:
            kp (float): Proportional gain
            ki (float): Integral gain  
            kd (float): Derivative gain
            setpoint (float): Target value (usually 0 for error correction)
        """
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.setpoint = setpoint
        
        self.previous_error = 0.0
        self.integral = 0.0
        self.last_time = time.time()
        
        # Limits for integral windup prevention
        self.integral_limit = 100.0
        
    def update(self, current_value):
        """
        Calculate PID output based on current value
        
        Args:
            current_value (float): Current measured value
            
        Returns:
            float: PID output
        """
        current_time = time.time()
        dt = current_time - self.last_time
        
        if dt <= 0.0:
            dt = 0.01  # Prevent division by zero
        
        # Calculate error
        error = self.setpoint - current_value
        
        # Proportional term
        proportional = self.kp * error
        
        # Integral term (with windup prevention)
        self.integral += error * dt
        self.integral = max(-self.integral_limit, min(self.integral_limit, self.integral))
        integral = self.ki * self.integral
        
        # Derivative term
        derivative = self.kd * (error - self.previous_error) / dt
        
        # Calculate output
        output = proportional + integral + derivative
        
        # Store values for next iteration
        self.previous_error = error
        self.last_time = current_time
        
        return output
    
    def reset(self):
        """Reset PID controller state"""
        self.previous_error = 0.0
        self.integral = 0.0
        self.last_time = time.time()

class ArkNavigationBot:
    def __init__(self, template_path, target_x, target_y, confidence_threshold=0.7):
        """
        Initialize the Ark first-person navigation bot with PID control
        
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
        self.position_tolerance = 8  # Reduced for more precision with PID
        self.running = False
        
        # Initialize PID controllers for X and Y axes
        # Tuned parameters for smooth movement (adjust as needed)
        self.pid_x = PIDController(kp=0.008, ki=0.001, kd=0.004, setpoint=0.0)
        self.pid_y = PIDController(kp=0.008, ki=0.001, kd=0.004, setpoint=0.0)
        
        # Movement keys for Ark
        self.keys = {
            'forward': '=',
            'backward': "'", 
            'strafe_left': '[',
            'strafe_right': ']',
            'look_left': 'left',      # Arrow key for camera rotation
            'look_right': 'right',    # Arrow key for camera rotation  
            'look_up': 'up',          # Arrow key for camera tilt
            'look_down': 'down'       # Arrow key for camera tilt
        }
        '''
        # Movement parameters for PID-controlled movement
        self.base_movement_duration = 0.02  # Very short base duration
        self.max_movement_duration = 0.15   # Maximum movement duration
        self.min_output_threshold = 0.1     # Minimum PID output to trigger movement
        self.max_output_clamp = 8.0         # Clamp PID output to prevent excessive movement
        
        # Camera control parameters
        self.camera_movement_duration = 0.01  # Very short for precise camera control
        self.max_camera_duration = 0.08      # Maximum camera movement duration
        self.camera_sensitivity = 0.006      # How much camera movement per PID output unit
        '''
        # Movement parameters for PID-controlled movement
        self.base_movement_duration = 0.02  # Very short base duration
        self.max_movement_duration = 0.15   # Maximum movement duration
        self.min_output_threshold = 0.1     # Minimum PID output to trigger movement
        self.max_output_clamp = 8.0         # Clamp PID output to prevent excessive movement
        
        # Camera control parameters
        self.camera_movement_duration = 0.01  # Very short for precise camera control
        self.max_camera_duration = 0.08      # Maximum camera movement duration
        self.camera_sensitivity = 0.006      # How much camera movement per PID output unit

               
        # Movement strategy: prioritize camera over character movement
        self.use_camera_first = False  # Try camera adjustments before character movement
        self.camera_threshold = 3 #30    # Use camera for adjustments smaller than this (pixels)
        
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
        scales = [1.0, 0.9, 1.1, 0.8, 1.2]
        rotations = [0, -5, 5, -10, 10, -15, 15, -20, 20, -25, 25, -30, 30, -35, 35, -40, 40, -45, 45]  # Test common rotation angles
        
        best_match = None
        best_confidence = 0
        best_rotation = 0
        
        for scale in scales:
            for rotation in rotations:
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
                    
                    if max_val > best_confidence:
                        best_confidence = max_val
                        # Calculate center of matched template
                        center_x = max_loc[0] + rotated_template.shape[1] // 2
                        center_y = max_loc[1] + rotated_template.shape[0] // 2
                        best_match = (center_x, center_y, max_val)
                        best_rotation = rotation
                        
                except cv2.error:
                    # Skip if template matching fails (e.g., template too large)
                    continue
        
        if best_confidence >= self.confidence_threshold:
            return (*best_match, best_rotation)
        
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
        Execute PID-controlled movement using both camera and character movement
        
        Args:
            dx: Horizontal offset (positive = landmark needs to move right)
            dy: Vertical offset (positive = landmark needs to move down)
        """
        # Get PID outputs (negative because we want to reduce the error to zero)
        pid_output_x = self.pid_x.update(-dx)  # Negative because we want to minimize offset
        pid_output_y = self.pid_y.update(-dy)
        
        # Clamp PID outputs to prevent excessive movement
        pid_output_x = max(-self.max_output_clamp, min(self.max_output_clamp, pid_output_x))
        pid_output_y = max(-self.max_output_clamp, min(self.max_output_clamp, pid_output_y))
        
        print(f"Offsets - dx: {dx:.1f}, dy: {dy:.1f}")
        print(f"PID outputs - X: {pid_output_x:.3f}, Y: {pid_output_y:.3f}")
        
        # Determine movement strategy based on offset magnitude
        abs_dx = abs(dx)
        abs_dy = abs(dy)
        
        # Horizontal movement - prioritize camera for small adjustments, character movement for large ones
        if abs(pid_output_x) > self.min_output_threshold:
            if abs_dx <= self.camera_threshold and self.use_camera_first:
                # Use camera rotation for fine horizontal adjustments
                camera_duration = min(abs(pid_output_x) * self.camera_sensitivity, self.max_camera_duration)
                if pid_output_x < 0:
                    self.press_key(self.keys['look_right'], camera_duration)
                    print(f"Camera right - duration: {camera_duration:.3f}s")
                else:
                    self.press_key(self.keys['look_left'], camera_duration)
                    print(f"Camera left - duration: {camera_duration:.3f}s")
            else:
                # Use character strafing for larger horizontal adjustments
                x_duration = min(abs(pid_output_x) * self.base_movement_duration, self.max_movement_duration)
                if pid_output_x < 0:
                    self.press_key(self.keys['strafe_right'], x_duration)
                    print(f"Strafe right - duration: {x_duration:.3f}s")
                else:
                    self.press_key(self.keys['strafe_left'], x_duration)
                    print(f"Strafe left - duration: {x_duration:.3f}s")
        
        # Vertical movement - prioritize camera for small adjustments, character movement for large ones
        if abs(pid_output_y) > self.min_output_threshold:
            if abs_dy <= self.camera_threshold and self.use_camera_first:
                # Use camera tilt for fine vertical adjustments
                camera_duration = min(abs(pid_output_y) * self.camera_sensitivity, self.max_camera_duration)
                if pid_output_y < 0:
                    self.press_key(self.keys['look_down'], camera_duration)
                    print(f"Camera down - duration: {camera_duration:.3f}s")
                else:
                    self.press_key(self.keys['look_up'], camera_duration)
                    print(f"Camera up - duration: {camera_duration:.3f}s")
            else:
                # Use character movement for larger vertical adjustments
                y_duration = min(abs(pid_output_y) * self.base_movement_duration, self.max_movement_duration)
                if pid_output_y < 0:
                    self.press_key(self.keys['backward'], y_duration)
                    print(f"Move backward - duration: {y_duration:.3f}s")
                else:
                    self.press_key(self.keys['forward'], y_duration)
                    print(f"Move forward - duration: {y_duration:.3f}s")
    
    def press_key(self, key, duration):
        """Press and hold a key for specified duration"""
        pyautogui.keyDown('backslash')
        pyautogui.keyDown(key)
        time.sleep(duration)
        pyautogui.keyUp(key)
        pyautogui.keyUp('backslash')
    
    def is_aligned(self, landmark_pos):
        """Check if landmark is sufficiently aligned with target position"""
        dx = abs(self.target_position[0] - landmark_pos[0])
        dy = abs(self.target_position[1] - landmark_pos[1])
        
        return dx <= self.position_tolerance and dy <= self.position_tolerance
    
    def draw_debug_overlay(self, screen, landmark_pos=None, rotation_angle=0):
        """
        Draw debug information on screen with rotation info
        
        Args:
            screen: Current screen capture
            landmark_pos: Current landmark position if found
            rotation_angle: Detected rotation angle of the landmark
        """
        debug_screen = screen.copy()
        
        # Draw target position
        cv2.circle(debug_screen, self.target_position, 12, (0, 255, 0), 2)
        cv2.putText(debug_screen, "TARGET", 
                   (self.target_position[0] - 30, self.target_position[1] - 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        # Draw current landmark position if found
        if landmark_pos:
            cv2.circle(debug_screen, (int(landmark_pos[0]), int(landmark_pos[1])), 10, (0, 0, 255), 2)
            
            # Show rotation angle
            text = f"LANDMARK (rot: {rotation_angle}°)"
            cv2.putText(debug_screen, text, 
                       (int(landmark_pos[0]) - 60, int(landmark_pos[1]) - 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
            
            # Draw line between target and current position
            cv2.line(debug_screen, self.target_position, 
                    (int(landmark_pos[0]), int(landmark_pos[1])), (255, 0, 0), 1)
            
            # Draw offset values
            dx = self.target_position[0] - landmark_pos[0]
            dy = self.target_position[1] - landmark_pos[1]
            offset_text = f"Offset: ({dx:.1f}, {dy:.1f})"
            cv2.putText(debug_screen, offset_text, (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        # Add control scheme info
        info_text = [
            "Controls: WASD=Move, Arrows=Look",
            "Camera threshold: < 30px",
            "Character movement: >= 30px"
        ]
        for i, text in enumerate(info_text):
            cv2.putText(debug_screen, text, (10, debug_screen.shape[0] - 60 + i*20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
        
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
                
                # Capture screen
                screen = self.capture_screen()
                
                # Find landmark
                landmark_result = self.find_landmark(screen)
                
                if landmark_result:
                    landmark_x, landmark_y, confidence, rotation = landmark_result
                    print(f"Landmark found at ({landmark_x:.1f}, {landmark_y:.1f}) "
                          f"with confidence {confidence:.3f}, rotation: {rotation}°")
                    
                    # Check if already aligned
                    if self.is_aligned((landmark_x, landmark_y)):
                        print("✓ Landmark is aligned with target!")
                        # Reset PID controllers when aligned to prevent integral windup
                        self.pid_x.reset()
                        self.pid_y.reset()
                        if show_debug:
                            debug_screen = self.draw_debug_overlay(screen, (landmark_x, landmark_y), rotation)
                            cv2.imshow('Debug View', debug_screen)
                            cv2.waitKey(1)
                        time.sleep(0.3)
                        continue
                    
                    # Calculate and execute movement
                    dx, dy = self.calculate_movement_needed((landmark_x, landmark_y))
                    print(f"Offset from target: dx={dx:.1f}, dy={dy:.1f}")
                    
                    self.execute_movement(dx, dy)
                    
                    # Show debug view if enabled
                    if show_debug:
                        debug_screen = self.draw_debug_overlay(screen, (landmark_x, landmark_y), rotation)
                        cv2.imshow('Debug View', debug_screen)
                        cv2.waitKey(1)
                    
                else:
                    print("Landmark not found in current view - adjust your view manually")
                    # Reset PID controllers when landmark is lost
                    self.pid_x.reset()
                    self.pid_y.reset()
                    if show_debug:
                        debug_screen = self.draw_debug_overlay(screen)
                        cv2.imshow('Debug View', debug_screen)
                        cv2.waitKey(1)
                
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
        template_path = ".\\icons1440\\teleporter_target_1150x475_260x400.png"
    
    print("\nSet target position where the landmark should appear on screen:")
    try:
        target_x = int(input("Target X coordinate (default: center ex. 1280): ") or pyautogui.size()[0] // 2)
        target_y = int(input("Target Y coordinate (default: center ex. 675): ") or pyautogui.size()[1] // 2)
    except ValueError:
        print("Using screen center as default target")
        target_x, target_y = pyautogui.size()[0] // 2, pyautogui.size()[1] // 2
    
    print("\nAdvanced PID Settings (press Enter for defaults):")
    try:
        kp = float(input("Proportional gain (default: 0.008): ") or "0.008")
        ki = float(input("Integral gain (default: 0.001): ") or "0.001") 
        kd = float(input("Derivative gain (default: 0.004): ") or "0.004")
    except ValueError:
        print("Using default PID values")
        kp, ki, kd = 0.008, 0.001, 0.004
    
    confidence = float(input("Confidence threshold (0.0-1.0, default: 0.7): ") or "0.7")
    
    show_debug = input("Show debug visualization? (y/n, default: n): ").lower().startswith('y')
    
    try:
        # Initialize bot
        bot = ArkNavigationBot(template_path, target_x, target_y, confidence)
        
        # Update PID parameters if provided
        bot.pid_x.kp = bot.pid_y.kp = kp
        bot.pid_x.ki = bot.pid_y.ki = ki  
        bot.pid_x.kd = bot.pid_y.kd = kd
        
        print(f"\nBot Configuration:")
        print(f"- Template: {template_path}")
        print(f"- Target position: ({target_x}, {target_y})")
        print(f"- Confidence threshold: {confidence}")
        print(f"- PID gains: Kp={kp}, Ki={ki}, Kd={kd}")
        print(f"- Debug view: {'Enabled' if show_debug else 'Disabled'}")
        
        print("Instructions:")
        print("1. Position yourself in Ark so the landmark is visible on screen")
        print("2. The bot will use WASD for movement and arrow keys for camera control")
        print("3. Camera control (arrows) for fine adjustments < 30 pixels")
        print("4. Character movement (WASD) for larger adjustments >= 30 pixels")
        print("5. Alt+Tab to this window and press Enter to start")
        print("6. Press 'q' to quit, 'p' to pause/resume")
        
        input("\nPress Enter to start the bot...")
        
        # Give time to switch to game window
        print("Starting in 3 seconds...")
        time.sleep(3)
        
        # Run bot
        bot.run_bot(show_debug)
        
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure you have the required packages installed:")
        print("pip install opencv-python pyautogui pillow keyboard numpy")

if __name__ == "__main__":
    main()