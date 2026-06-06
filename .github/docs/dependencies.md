# Dependency Graph

```mermaid
graph LR
    check_env[check_env]
    check_env --> importlib[importlib]
    gesture_spotify_player[gesture_spotify_player]
    gesture_spotify_player --> collections[collections]
    gesture_spotify_player --> cv2[cv2]
    gesture_spotify_player --> time[time]
    gesture_spotify_player --> numpy[numpy]
    gesture_spotify_player --> math[math]
    gesture_spotify_player --> os[os]
    gesture_spotify_player --> argparse[argparse]
```