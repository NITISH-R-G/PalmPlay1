# Architecture Diagram

```mermaid
graph TD
    subgraph Repository
        check_env_py[check_env.py]
        gesture_spotify_player_py[gesture_spotify_player.py]
        click check_env_py href "https://github.com/NITISH-R-G/PalmPlay1/blob/main/check_env.py" "View source code"
        click gesture_spotify_player_py href "https://github.com/NITISH-R-G/PalmPlay1/blob/main/gesture_spotify_player.py" "View source code"
    end
    subgraph Frameworks
        fw_mediapipe[mediapipe]
        fw_opencv_python[opencv-python]
        fw_pygame[pygame]
    end
    check_env_py -.-> fw_mediapipe
    check_env_py -.-> fw_opencv_python
    check_env_py -.-> fw_pygame
    gesture_spotify_player_py -.-> fw_mediapipe
    gesture_spotify_player_py -.-> fw_opencv_python
    gesture_spotify_player_py -.-> fw_pygame
```