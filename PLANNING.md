
# TODO
* Platform-specific work to keep in sync:
    * Linux key binding.
    * Linux screenshot solution.
    * Linux environment setup at program start.

# Planning

## Cross-platform planning

### Strategy
- Develop Windows and Linux in parallel.
- Treat Windows and Linux as first-class targets for new behavior.
- Avoid platform-specific shortcuts in shared code unless they are hidden behind interfaces.
- For each feature, define the cross-platform contract first, then fill in platform-specific details.

### Setup
- Add a startup setup script that runs at program start so platform-dependent initialization can happen there.
- Keep startup behavior consistent across Windows and Linux.

### Shared behavior
- Keep shared features such as snapshot handling and recycle-bin location behind a common interface.
- Provide platform-specific implementations for that interface.
- Prefer shared UI and workflow logic where possible, with small platform adapters at the edges.

## Linux-specific work

### Scope
- Focus on Ubuntu for now.
- Keep Linux work aligned with the Windows implementation, not as a separate branch of the product.

### Ubuntu / GNOME

#### Screenshot capture
- X11 screenshots are sandboxed, and Wayland is also heavily restricted.
- Use CLI utilities in a subprocess to take screenshots.
- Two possible approaches:
    - Capture to disk and load from disk.
    - Use a pipe-based setup if needed, though that may be overkill.

#### Window positioning and borderless windows
- Investigate approaches here.

## Snapshot

### Window positioning
- Windows:
    - Native events, including `WM_NCHITTEST`, are likely overkill.
    - Revisit `CalcSize` handling later if partial native-window-manager overrides are needed.

### Crop
- Initial full-screen crop feels smooth.
- Secondary crop is still very rough.
- Current issues:
    - The crop box is not contained within the margin.
    - The margin is not hidden after crop.
    - Showing and hiding the margin causes visible artifacts and flicker.

### Context
- Not started; waiting on the context menu manager.

### Recycle integration
- Not started.

### Paint
- Review previous work in screencap/legacy.
- Investigate performance improvements such as quadtrees.
- Reduce code complexity.
- Remaining UI concerns:
    - Integrate with the key manager.
    - Provide a help menu and other visual cues.

### Quick crop
- Confirm the crop immediately when the user releases the selection box.
- Make this behavior toggleable.
- When disabled:
    - Allow selection repositioning. Done.
    - Show crop menu buttons.
    - UI is done.
    - Positioning still needs attention.
    - Button functionality still needs attention.

## Dock widgets
- Investigate ways to use the app when no keyboard is present.

## System tray button
- Use Qt built-in solutions as much as possible.
- Keep the implementation non-Windows-specific if possible.
- Reuse mostly the same options as the legacy version.

## Recycle bin
- Not started.
- Consider saving images to disk on a background thread to avoid blocking the UI, especially for larger images.

## Context menu manager
- TBD; still needs to be designed.

## Hotkeys

### Windows
- Done: local and global hotkey management is implemented.
- Global hotkeys use `user32.RegisterHotKey`.
- Local hotkeys are implemented with Qt.

### Linux
- Likely shares the local manager with Windows.
- Global hotkey options:
    - Key logger approach, similar to the "KeyMaster" project. This would require the user to manually add the app to the input group, which is not ideal.
    - Investigate Wayland-only solutions; X11 support is not planned.

### macOS
- TBD, once macOS hardware is available.

## Config
- See the implementation notes in `Config.py`.
- The current implementation is in good shape and is likely done.
- Supported config types: `int`, `float`, `str`, `bool`, and `list`.
- Lists may contain primitive values, but not nested structures.
- Future improvements:
    - Support a `dict` type.
    - Improve write performance by updating only the line for the parameter that changed at runtime.
    - Use a Python context manager (`with ... as ...:`) to support batch updates.

## Miscellaneous
- Update dependencies to the latest versions:
    - Nuitka: https://nuitka.net/posts/nuitka-release-40.html
    - Python 3.14

## Memory saving
- Strikethrough note removed: allowing bit depth selection does not help, because the image is converted to the monitor color space when displayed.
- Add downsampling for large monitors.
- Suggested approach:
    - Save the full image to disk.
    - Display a downscaled image on screen.
    - This should reduce memory usage.
