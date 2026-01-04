---
name: android-to-ios
description: Use Android/Kotlin code as the source of truth and implement the equivalent feature in iOS/Swift. Supports both SwiftUI and UIKit/Storyboard based on target codebase patterns. Understands the Android feature behavior, data structures, and logic, then creates idiomatic iOS code that achieves feature parity. Use when porting features from Android to iOS or ensuring platform consistency.
---

# Android to iOS: Feature Parity Implementation

Use Android code as the reference to implement the equivalent iOS feature. Not a literal translation - understand what the Android code does, then implement it idiomatically for iOS.

**Supports both UI approaches:**
- SwiftUI (modern declarative)
- UIKit + Storyboards (traditional)
- Mixed codebases

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

### Core Language

| Android/Kotlin | iOS/Swift |
|----------------|-----------|
| Interfaces | Protocols |
| Extension functions | Extensions |
| Data classes | Structs |
| Sealed classes | Enums with associated values |
| ?.let / ?: / require | guard let / if let |
| Result / runCatching | throws / Result |
| Kotlinx Serialization | Codable |

### Async & State

| Android/Kotlin | iOS/Swift |
|----------------|-----------|
| Kotlin Flow | Combine / async sequences |
| suspend functions | async/await |
| MutableStateFlow | @Published / CurrentValueSubject |
| ViewModel | ObservableObject / @Observable |

### Data & Networking

| Android/Kotlin | iOS/Swift |
|----------------|-----------|
| Room | Core Data / SwiftData |
| Retrofit / Ktor | URLSession / Alamofire |
| DataStore / SharedPreferences | UserDefaults |

### UI (depends on target codebase)

| Android/Kotlin | iOS/SwiftUI | iOS/UIKit |
|----------------|-------------|-----------|
| Jetpack Compose | SwiftUI Views | UIViewController + Storyboard |
| @Composable | View protocol | UIViewController subclass |
| LazyColumn | List / LazyVStack | UITableView / UICollectionView |
| Column/Row | VStack/HStack | UIStackView |
| Modifier | ViewModifier | Layout constraints |
| remember { } | @State | Instance properties |
| collectAsState | .onReceive / @Published | Combine subscribers / delegates |
| Navigation Compose | NavigationStack | Storyboard segues / coordinators |

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
Architecture: [MVVM / TCA / VIPER / MVC / etc.]

UI FRAMEWORK (critical - match this!):
├─ SwiftUI: [Yes / No] - Look for: View protocol, @State, VStack
├─ UIKit: [Yes / No] - Look for: UIViewController, .storyboard, .xib
├─ Storyboards: [Yes / No] - Look for: .storyboard files, segues
└─ Programmatic UIKit: [Yes / No] - Look for: UIViewController without storyboards

Networking: [URLSession / Alamofire / Moya / etc.]
State: [Combine / Observation / RxSwift / Delegates / etc.]
Navigation: [NavigationStack / Storyboard segues / Coordinators / etc.]

Similar features in codebase: [list if any]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**IMPORTANT:** Match the UI framework the codebase already uses:
- If they use Storyboards → use Storyboards
- If they use SwiftUI → use SwiftUI
- If mixed → ask the user which to use for this feature

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

Create idiomatic Swift code matching the target codebase's UI framework:

**If SwiftUI codebase:**
- Use SwiftUI Views
- Use @State, @Published, @ObservedObject
- Use NavigationStack or existing nav pattern

**If UIKit/Storyboard codebase:**
- Create UIViewController subclasses
- Create or update Storyboard scenes
- Use IBOutlet/IBAction or programmatic setup
- Use delegates, closures, or Combine for state

**If Programmatic UIKit:**
- Create UIViewController subclasses
- Build UI in code (no storyboards)
- Use Auto Layout programmatically

**Common guidelines:**
- Use Swift idioms (structs, protocols, extensions)
- Use Combine or async/await for async work
- Match the iOS codebase's existing patterns exactly
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

### UI - SwiftUI Version

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

### UI - UIKit/Storyboard Version

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
// iOS (UIKit)
class UserViewController: UIViewController {
    @IBOutlet weak var tableView: UITableView!
    @IBOutlet weak var activityIndicator: UIActivityIndicatorView!
    
    private let viewModel = UserViewModel()
    private var cancellables = Set<AnyCancellable>()
    
    override func viewDidLoad() {
        super.viewDidLoad()
        setupBindings()
        Task { await viewModel.loadUsers() }
    }
    
    private func setupBindings() {
        viewModel.$isLoading
            .receive(on: DispatchQueue.main)
            .sink { [weak self] isLoading in
                if isLoading {
                    self?.activityIndicator.startAnimating()
                    self?.tableView.isHidden = true
                } else {
                    self?.activityIndicator.stopAnimating()
                    self?.tableView.isHidden = false
                }
            }
            .store(in: &cancellables)
        
        viewModel.$users
            .receive(on: DispatchQueue.main)
            .sink { [weak self] _ in
                self?.tableView.reloadData()
            }
            .store(in: &cancellables)
    }
}

extension UserViewController: UITableViewDataSource {
    func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        return viewModel.users.count
    }
    
    func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell = tableView.dequeueReusableCell(withIdentifier: "UserCell", for: indexPath)
        let user = viewModel.users[indexPath.row]
        cell.textLabel?.text = user.name
        return cell
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
