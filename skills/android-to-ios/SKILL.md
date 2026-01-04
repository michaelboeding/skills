---
name: android-to-ios
description: Use Android/Kotlin code as the source of truth and implement the equivalent feature in iOS/Swift/SwiftUI. Understands the Android feature behavior, data structures, and logic, then creates idiomatic iOS code that achieves feature parity. Use when porting features from Android to iOS or ensuring platform consistency.
---

# Android to iOS: Feature Parity Implementation

Use Android code as the reference to implement the equivalent iOS feature. Not a literal translation - understand what the Android code does, then implement it idiomatically for iOS.

**Use this when:**
- Porting a feature from Android to iOS
- Android is the "source of truth" for a feature
- Ensuring feature parity between platforms
- iOS implementation should match Android behavior

## Key Principle

```
Android Code → Understand Feature → Implement for iOS
                  (what)                 (how)
```

**Preserved:** Feature behavior, data structure shapes, business logic, user flows
**Adapted:** Language idioms, UI framework, platform patterns

---

## Platform Mapping Reference

| Android/Kotlin | iOS/Swift |
|----------------|-----------|
| Jetpack Compose | SwiftUI |
| Kotlin Flow | Combine / async sequences |
| suspend functions | async/await |
| Room | Core Data / SwiftData |
| Retrofit / Ktor | URLSession / async networking |
| DataStore / SharedPreferences | UserDefaults |
| Kotlinx Serialization | Codable |
| MutableStateFlow / mutableStateOf | @State / @Published |
| ViewModel | ObservableObject / @Observable |
| Interfaces | Protocols |
| Extension functions | Extensions |
| Data classes | Structs |
| Sealed classes | Enums with associated values |
| ?.let / ?: / require | guard let / if let |
| Result / runCatching | throws / Result |

---

## Workflow

### Step 1: Get the Android Reference

Ask the user for the Android code to reference:

```
What Android code should I use as reference?

Options:
1. Paste the Kotlin code directly
2. Provide a file path (if Android repo is accessible)
3. Describe the feature and I'll ask for specific files
```

### Step 2: Analyze the Android Code

Thoroughly understand:

| Aspect | What to Extract |
|--------|-----------------|
| **Feature Behavior** | What does this feature do? User-facing functionality |
| **Data Structures** | Models, types, sealed classes - their shapes and relationships |
| **Business Logic** | Core logic, validations, transformations |
| **State Management** | What state exists, how it flows |
| **API Contracts** | Network calls, request/response shapes |
| **UI Flow** | Screens, navigation, user interactions |
| **Edge Cases** | Error handling, loading states, empty states |

Create a **Feature Summary**:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                  ANDROID FEATURE ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Feature: [Name]

### What It Does
[User-facing description]

### Data Structures
```kotlin
// Key models from Android
```

### Business Logic
[Core logic summary]

### State
[What state is managed, how it changes]

### API Calls
[Endpoints, request/response shapes]

### UI Flow
[Screens, navigation]

### Edge Cases Handled
- [Case 1]
- [Case 2]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Step 3: Check iOS Codebase Context

Before implementing, understand the target:

1. **Check for style guide**: Does `.claude/codebase-style.md` exist?
2. **Explore existing patterns**: How does this iOS codebase handle similar features?
3. **Identify conventions**: Naming, architecture (MVVM/TCA), patterns

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                   iOS CONTEXT CHECK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Style Guide: [Found / Not found]
Architecture: [MVVM / TCA / VIPER / etc.]
UI Framework: [SwiftUI / UIKit / Mixed]
Networking: [URLSession / Alamofire / etc.]
State: [Combine / Observation / etc.]
Navigation: [NavigationStack / Coordinator / etc.]

Similar features in codebase: [list if any]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Step 4: Create Implementation Plan

Map Android components to iOS equivalents:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                  IMPLEMENTATION PLAN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Files to Create

| # | File | Purpose | Android Equivalent |
|---|------|---------|-------------------|
| 1 | Models/User.swift | Data model | User.kt |
| 2 | Services/UserService.swift | Data access | UserRepository.kt |
| 3 | Views/UserView.swift | SwiftUI View | UserScreen.kt |
| 4 | ViewModels/UserViewModel.swift | State holder | UserViewModel.kt |

## Data Structure Mapping

| Android (Kotlin) | iOS (Swift) |
|------------------|-------------|
| data class User | struct User |
| sealed class Status | enum Status |
| interface UserRepository | protocol UserService |

## Implementation Order

1. Models (no dependencies)
2. Service protocols
3. Service implementations
4. ViewModels
5. SwiftUI Views

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Step 5: Implement for iOS

Create idiomatic Swift/SwiftUI code:

**Guidelines:**
- Use Swift idioms (structs, protocols, extensions)
- Use SwiftUI for all UI
- Use Combine or async/await for reactive streams
- Use structured concurrency for async work
- Match the iOS codebase's existing patterns
- Keep data structure shapes equivalent for API compatibility

### Step 6: Report Results

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                 ANDROID → iOS COMPLETE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Feature: [Name]

### Files Created

| File | Purpose |
|------|---------|
| [path] | [description] |
| ... | ... |

### Mapping Summary

| Android | iOS |
|---------|-----|
| User.kt | User.swift |
| UserRepository.kt | UserService.swift |
| UserScreen.kt | UserView.swift |
| UserViewModel.kt | UserViewModel.swift |

### Key Adaptations

| Aspect | Android Approach | iOS Approach |
|--------|------------------|--------------|
| UI | Jetpack Compose | SwiftUI |
| State | StateFlow | Combine / @Published |
| Async | Coroutines | async/await |
| [other] | [Android way] | [iOS way] |

### Feature Parity Checklist

- [x] Core functionality matches
- [x] Data structures equivalent
- [x] Error handling preserved
- [x] Loading states preserved
- [x] Edge cases handled

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Triggers

```
"android to ios"
"convert from android"
"port this kotlin to swift"
"implement this android feature for ios"
"ios version of this android code"
"kotlin to swift"
```

---

## Integration with style-guide

If `.claude/codebase-style.md` exists for the iOS project:
- Reference it before implementing
- Match existing naming conventions
- Follow established architecture patterns
- Use the same libraries already in use

---

## Common Conversions

### Models

```kotlin
// Android
@Serializable
data class User(
    val id: String,
    val name: String,
    val email: String?,
    val status: UserStatus
)

@Serializable
enum class UserStatus {
    @SerialName("active") ACTIVE,
    @SerialName("inactive") INACTIVE,
    @SerialName("pending") PENDING
}
```

```swift
// iOS
struct User: Codable {
    let id: String
    let name: String
    let email: String?
    let status: UserStatus
}

enum UserStatus: String, Codable {
    case active, inactive, pending
}
```

### Async/State

```kotlin
// Android
private val _users = MutableStateFlow<List<User>>(emptyList())
val users: StateFlow<List<User>> = _users.asStateFlow()

private val _isLoading = MutableStateFlow(false)
val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()

fun loadUsers() {
    viewModelScope.launch {
        _isLoading.value = true
        try {
            _users.value = userRepository.fetchUsers()
        } finally {
            _isLoading.value = false
        }
    }
}
```

```swift
// iOS
@MainActor
class UserViewModel: ObservableObject {
    @Published var users: [User] = []
    @Published var isLoading = false
    
    func loadUsers() async {
        isLoading = true
        defer { isLoading = false }
        
        do {
            users = try await userService.fetchUsers()
        } catch {
            // Handle error
        }
    }
}
```

### UI

```kotlin
// Android (Compose)
@Composable
fun UserScreen(viewModel: UserViewModel = hiltViewModel()) {
    val users by viewModel.users.collectAsStateWithLifecycle()
    val isLoading by viewModel.isLoading.collectAsStateWithLifecycle()
    
    Column {
        if (isLoading) {
            CircularProgressIndicator()
        } else {
            LazyColumn {
                items(users) { user ->
                    UserRow(user = user)
                }
            }
        }
    }
}
```

```swift
// iOS (SwiftUI)
struct UserView: View {
    @StateObject private var viewModel = UserViewModel()
    
    var body: some View {
        VStack {
            if viewModel.isLoading {
                ProgressView()
            } else {
                List(viewModel.users) { user in
                    UserRow(user: user)
                }
            }
        }
        .task {
            await viewModel.loadUsers()
        }
    }
}
```

---

## Tips

1. **Don't translate literally** - Understand the feature, then implement idiomatically
2. **Match data shapes** - Keep API compatibility where possible
3. **Check existing patterns** - Use what the iOS codebase already does
4. **Handle platform differences** - Some things work differently (lifecycle, permissions)
5. **Verify feature parity** - Same behavior, not same code
