---
name: add-to-xcode
description: >
  Automatically adds newly created files to Xcode projects. 
  When an agent creates .swift, .m, .mm, .c, .cpp, .h, or other source files 
  in a directory containing an .xcodeproj, this skill registers the file with 
  the Xcode project and adds it to the appropriate build target.
triggers:
  - create swift file
  - create objective-c file
  - add file to xcode
  - new ios file
  - new macos file
  - xcode project
---

# Add to Xcode

**Automatically register newly created files with Xcode projects.**

When you create source files in an Xcode project directory, they must be explicitly added to the `.xcodeproj` or they won't appear in Xcode's navigator or compile.

## When to Use

**After creating any of these file types in an Xcode project:**
- `.swift` - Swift source files
- `.m` - Objective-C implementation
- `.mm` - Objective-C++ implementation  
- `.c` - C source files
- `.cpp` - C++ source files
- `.h` - Header files

## Workflow

### Step 1: Create the file normally

```bash
# Example: Create a new Swift file
cat > Sources/Features/MyFeature.swift << 'EOF'
import Foundation

class MyFeature {
    // Implementation
}
EOF
```

### Step 2: Add to Xcode project

```bash
ruby ${CLAUDE_PLUGIN_ROOT}/skills/add-to-xcode/scripts/add_to_xcode.rb Sources/Features/MyFeature.swift
```

**Output:**
```
✓ Added Sources/Features/MyFeature.swift to MyApp.xcodeproj (target: MyApp)
```

## What the Script Does

1. **Finds the `.xcodeproj`** - Searches current directory and parents
2. **Creates group hierarchy** - Matches the file's directory structure
3. **Adds file reference** - Registers with the project
4. **Adds to build target** - Source files (`.swift`, `.m`, `.mm`, `.c`, `.cpp`) are added to the first target's compile sources

## Requirements

Ruby with the `xcodeproj` gem:

```bash
gem install xcodeproj
```

## Examples

### Adding a new Swift file

```bash
# Create the file
cat > MyApp/ViewModels/ProfileViewModel.swift << 'EOF'
import SwiftUI

@Observable
class ProfileViewModel {
    var name: String = ""
    var email: String = ""
}
EOF

# Add to Xcode
ruby ${CLAUDE_PLUGIN_ROOT}/skills/add-to-xcode/scripts/add_to_xcode.rb MyApp/ViewModels/ProfileViewModel.swift
```

### Adding a header file

```bash
# Create header
cat > MyApp/Bridge/MyApp-Bridging-Header.h << 'EOF'
#import <SomeLibrary/SomeLibrary.h>
EOF

# Add to Xcode (headers are added but not to compile sources)
ruby ${CLAUDE_PLUGIN_ROOT}/skills/add-to-xcode/scripts/add_to_xcode.rb MyApp/Bridge/MyApp-Bridging-Header.h
```

### Adding Objective-C files

```bash
# Create implementation
cat > MyApp/Legacy/LegacyManager.m << 'EOF'
#import "LegacyManager.h"

@implementation LegacyManager
// Implementation
@end
EOF

# Add to Xcode
ruby ${CLAUDE_PLUGIN_ROOT}/skills/add-to-xcode/scripts/add_to_xcode.rb MyApp/Legacy/LegacyManager.m
```

## Agent Integration

When working in an Xcode project, agents should:

1. **Check for `.xcodeproj`** before creating source files
2. **Create the file** using standard file creation
3. **Run add_to_xcode.rb** immediately after file creation

```bash
# Pattern for agents:
# 1. Create file
cat > NewFile.swift << 'EOF'
// content
EOF

# 2. Register with Xcode
ruby ${CLAUDE_PLUGIN_ROOT}/skills/add-to-xcode/scripts/add_to_xcode.rb NewFile.swift
```

## Troubleshooting

### "No .xcodeproj found"
- Make sure you're running from within the Xcode project directory or a subdirectory

### "gem not found: xcodeproj"
- Install with: `gem install xcodeproj`
- On macOS with system Ruby, you may need: `sudo gem install xcodeproj`

### File added but not compiling
- Check that the file extension is recognized (`.swift`, `.m`, `.mm`, `.c`, `.cpp`)
- Verify the target exists and has a source build phase
- Header files (`.h`) are not added to compile sources (this is correct)

## Related Skills

| Skill | Use Case |
|-------|----------|
| `ios-to-android` | Convert iOS code to Android |
| `android-to-ios` | Convert Android code to iOS |
