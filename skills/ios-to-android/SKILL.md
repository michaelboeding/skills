---
name: ios-to-android
description: Use iOS/Swift code as the source of truth and implement the equivalent feature in Android/Kotlin/Compose. Understands the iOS feature behavior, data structures, and logic, then creates idiomatic Android code that achieves feature parity. Use when porting features from iOS to Android or ensuring platform consistency.
---

# iOS to Android: Feature Parity Implementation

Use iOS code as the reference to implement the equivalent Android feature. Not a literal translation - understand what the iOS code does, then implement it idiomatically for Android.

**Use this when:**
- Porting a feature from iOS to Android
- iOS is the "source of truth" for a feature
- Ensuring feature parity between platforms
- Android implementation should match iOS behavior

## Key Principle

```
iOS Code → Understand Feature → Implement for Android
              (what)                 (how)
```

**Preserved:** Feature behavior, data structure shapes, business logic, user flows
**Adapted:** Language idioms, UI framework, platform patterns

---

## Platform Mapping Reference

| iOS/Swift | Android/Kotlin |
|-----------|----------------|
| UIKit / SwiftUI | Jetpack Compose |
| Combine | Kotlin Flow / Coroutines |
| async/await | suspend functions |
| Core Data | Room |
| URLSession | Retrofit / Ktor |
| UserDefaults | DataStore / SharedPreferences |
| Codable | Kotlinx Serialization |
| @State / @Published | MutableStateFlow / mutableStateOf |
| ObservableObject | ViewModel |
| Protocols | Interfaces |
| Extensions | Extension functions |
| Structs | Data classes |
| Enums with associated values | Sealed classes |
| guard let / if let | ?.let / ?: / require |
| throws | Result / runCatching |

---

## Workflow

### Step 1: Get the iOS Reference

Ask the user for the iOS code to reference:

```
What iOS code should I use as reference?

Options:
1. Paste the Swift code directly
2. Provide a file path (if iOS repo is accessible)
3. Describe the feature and I'll ask for specific files
```

### Step 2: Analyze the iOS Code

Thoroughly understand:

| Aspect | What to Extract |
|--------|-----------------|
| **Feature Behavior** | What does this feature do? User-facing functionality |
| **Data Structures** | Models, types, enums - their shapes and relationships |
| **Business Logic** | Core logic, validations, transformations |
| **State Management** | What state exists, how it flows |
| **API Contracts** | Network calls, request/response shapes |
| **UI Flow** | Screens, navigation, user interactions |
| **Edge Cases** | Error handling, loading states, empty states |

Create a **Feature Summary**:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    iOS FEATURE ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Feature: [Name]

### What It Does
[User-facing description]

### Data Structures
```swift
// Key models from iOS
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

### Step 3: Check Android Codebase Context

Before implementing, understand the target:

1. **Check for style guide**: Does `.claude/codebase-style.md` exist?
2. **Explore existing patterns**: How does this Android codebase handle similar features?
3. **Identify conventions**: Naming, architecture (MVVM/MVI), DI patterns

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                 ANDROID CONTEXT CHECK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Style Guide: [Found / Not found]
Architecture: [MVVM / MVI / Clean / etc.]
DI Framework: [Hilt / Koin / Manual / etc.]
Networking: [Retrofit / Ktor / etc.]
State: [StateFlow / Compose State / etc.]
Navigation: [Compose Navigation / etc.]

Similar features in codebase: [list if any]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Step 4: Create Implementation Plan

Map iOS components to Android equivalents:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                  IMPLEMENTATION PLAN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Files to Create

| # | File | Purpose | iOS Equivalent |
|---|------|---------|----------------|
| 1 | data/model/User.kt | Data model | User.swift |
| 2 | data/repository/UserRepository.kt | Data access | UserService.swift |
| 3 | ui/screen/UserScreen.kt | Compose UI | UserViewController.swift |
| 4 | ui/viewmodel/UserViewModel.kt | State holder | UserViewModel.swift |

## Data Structure Mapping

| iOS (Swift) | Android (Kotlin) |
|-------------|------------------|
| struct User | data class User |
| enum Status | sealed class Status |
| protocol UserService | interface UserRepository |

## Implementation Order

1. Models (no dependencies)
2. Repository interfaces
3. Repository implementations
4. ViewModels
5. Compose UI

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Step 5: Implement for Android

Create idiomatic Kotlin/Compose code:

**Guidelines:**
- Use Kotlin idioms (data classes, sealed classes, extension functions)
- Use Jetpack Compose for all UI
- Use Kotlin Flow for reactive streams
- Use coroutines for async work
- Match the Android codebase's existing patterns
- Keep data structure shapes equivalent for API compatibility

### Step 6: Report Results

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                 iOS → ANDROID COMPLETE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Feature: [Name]

### Files Created

| File | Purpose |
|------|---------|
| [path] | [description] |
| ... | ... |

### Mapping Summary

| iOS | Android |
|-----|---------|
| User.swift | User.kt |
| UserService.swift | UserRepository.kt |
| UserViewController.swift | UserScreen.kt |
| UserViewModel.swift | UserViewModel.kt |

### Key Adaptations

| Aspect | iOS Approach | Android Approach |
|--------|--------------|------------------|
| UI | UIKit/SwiftUI | Jetpack Compose |
| State | Combine | StateFlow |
| Async | async/await | Coroutines |
| [other] | [iOS way] | [Android way] |

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
"ios to android"
"convert from ios"
"port this swift to kotlin"
"implement this ios feature for android"
"android version of this ios code"
"swift to kotlin"
```

---

## Integration with style-guide

If `.claude/codebase-style.md` exists for the Android project:
- Reference it before implementing
- Match existing naming conventions
- Follow established architecture patterns
- Use the same libraries already in use

---

## Common Conversions

### Models

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

### Async/State

```swift
// iOS
@Published var users: [User] = []
@Published var isLoading = false

func loadUsers() async throws {
    isLoading = true
    defer { isLoading = false }
    users = try await userService.fetchUsers()
}
```

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

### UI

```swift
// iOS (SwiftUI)
var body: some View {
    VStack {
        if isLoading {
            ProgressView()
        } else {
            List(users) { user in
                UserRow(user: user)
            }
        }
    }
}
```

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

---

## Tips

1. **Don't translate literally** - Understand the feature, then implement idiomatically
2. **Match data shapes** - Keep API compatibility where possible
3. **Check existing patterns** - Use what the Android codebase already does
4. **Handle platform differences** - Some things work differently (lifecycle, permissions)
5. **Verify feature parity** - Same behavior, not same code
