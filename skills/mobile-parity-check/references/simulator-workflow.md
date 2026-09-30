# Simulator workflow

Read before building or launching. Commands are patterns: derive project paths, schemes, variants, application IDs, artifacts, and devices from the repositories and installed tools. Check local help when flags differ; do not assume a particular device generation or automation MCP.

## Preflight and isolation

Inspect Xcode/SDK selection, installed runtimes, Android SDK paths, Java/Gradle compatibility, and existing UI tests. Follow lockfiles and documented dependency/submodule setup in the new worktrees. Use process-local `DEVELOPER_DIR` if needed rather than changing global Xcode selection. Report build blockers without silently upgrading dependencies.

Create a dedicated iOS simulator and Android AVD, or use clearly disposable audit devices. Record ownership before changing permissions, text scale, locale, app data, or snapshots. Never erase a shared simulator or wipe a personal AVD. A cold boot is not an app-data reset.

Discover an available UI driver: existing XCUITest and Espresso/Compose tests, installed cross-platform automation, simulator tools, or permitted computer-use tools. Read its required instructions before use. `simctl` and `adb` can launch/capture but do not themselves provide complete cross-platform UI inspection. If interaction or inspection is unavailable, block affected checks and continue available work; do not replace a UI audit with only code review.

## iOS

Discover projects/workspaces with file search and choose the documented workspace when dependencies require one:

```bash
xcodebuild -version
xcodebuild -list -workspace "$PARITY_IOS_WORKSPACE"
xcrun simctl list devices available --json
xcrun simctl list runtimes --json
xcrun simctl list devicetypes
```

Create a run-specific simulator with discovered device type/runtime identifiers using `xcrun simctl create`. Boot its returned UDID if shut down and wait with `xcrun simctl bootstatus "$PARITY_IOS_UDID" -b` under a bounded tool timeout. Use that explicit UDID throughout instead of `booted`.

Point the workspace to the iOS audit worktree and use run-specific DerivedData:

```bash
xcodebuild -workspace "$PARITY_IOS_WORKSPACE" \
  -scheme "$PARITY_IOS_SCHEME" -configuration "$PARITY_IOS_CONFIGURATION" \
  -destination "platform=iOS Simulator,id=$PARITY_IOS_UDID" \
  -derivedDataPath "$PARITY_RUN/build/ios" build
xcrun simctl install "$PARITY_IOS_UDID" "$PARITY_IOS_APP"
xcrun simctl launch "$PARITY_IOS_UDID" "$PARITY_IOS_BUNDLE_ID"
xcrun simctl io "$PARITY_IOS_UDID" screenshot "$PARITY_IOS_SCREENSHOT"
```

Use `-project` for a standalone project. Resolve the `.app` and bundle ID from the actual build product/settings, not a guessed filename or stale build. Supply the app's verified fixture arguments/environment; there is no universal fixture flag. A UI runner that relaunches the app must preserve it.

For existing UI tests, use the same scheme/configuration/destination with the `test` action and a new `-resultBundlePath` under the run directory. Record filters. Xcode may create separate test-device clones; record/capture the actual executing device or use the runner's supported single-device configuration. Do not pair screenshots of the idle manual app with results from another simulator.

## Android

Discover the SDK from project setup, `ANDROID_HOME`, or installed locations; tools may not be on PATH. Inspect AVDs and modules/variants:

```bash
"$PARITY_EMULATOR" -list-avds
"$PARITY_ADB" devices -l
./gradlew tasks --all
```

Create/select a dedicated AVD with an installed compatible image. Use a free even console port and track the long-running process/session:

```bash
"$PARITY_EMULATOR" -avd "$PARITY_ANDROID_AVD" -port "$PARITY_ANDROID_PORT" -no-snapshot
```

Run subsequent commands from another tool session. Verify that `emulator-<port>` belongs to the expected AVD. Wait with a deadline for that serial and `getprop sys.boot_completed` to return `1`; do not leave an unbounded polling loop. `-no-snapshot` does not reset persistent app data; use the fixture reset or the dedicated device.

Build using the wrapper in the Android audit worktree and its actual flavor/task. For the usual `app` module and `debug` variant:

```bash
./gradlew :app:assembleDebug
"$PARITY_ADB" -s "$PARITY_ANDROID_SERIAL" install -r "$PARITY_ANDROID_APK"
"$PARITY_ADB" -s "$PARITY_ANDROID_SERIAL" shell am start -W -n "$PARITY_ANDROID_COMPONENT"
"$PARITY_ADB" -s "$PARITY_ANDROID_SERIAL" exec-out screencap -p > "$PARITY_ANDROID_SCREENSHOT"
```

Resolve APK/application ID/component from the actual variant and build artifact; account for split APKs. Use fixture extras only when supported by the app and account for separate host/device shell quoting. `install -r` retains app data and does not prove seeding succeeded.

For instrumentation tests, use the runner's supported device selector/configuration to target this emulator. Gradle connected tests can otherwise reach other attached devices. Save test reports and process/device-scoped logcat evidence.

For local fixtures, configure and verify host routing separately for each platform. Scope any `adb reverse` mappings to the chosen serial, record them, and remove only this run's mappings. Keep the fixture service local.

## Evidence and recovery

Name captures by scenario/variant/checkpoint, for example `evidence/PROFILE-EDIT-001/default/after-save.ios.png` and `after-save.android.png`. Record fixture hash, device/build identity, and capture time. Keep raw screenshots and label derived side-by-side views, overlays, or crops. Inspect the originals as well as any image diff.

Use observable UI conditions to wait for readiness and finite deadlines for boot, build, requests, and scenarios. Preserve command exit codes when piping logs. On a failure, save the useful log and try a specific setup repair; after two attempts at the same cause, record the blocker and continue independent work. Keep hardware/mock limitations explicit.

Save changes and results before cleanup. Shut down only this run's processes/devices and remove only its temporary routing. Retain branches/worktrees and evidence for reproduction unless cleanup was requested. Provide resource-specific cleanup commands; global simulator shutdown, ADB server restart, and broad process kills are not routine cleanup.

## Official references

- [Apple: building/testing from the command line](https://developer.apple.com/library/archive/technotes/tn2339/_index.html) — schemes and destinations; installed `xcodebuild -help` and `xcrun simctl help` provide current flags.
- [Apple: running on simulated or physical devices](https://developer.apple.com/documentation/xcode/running-your-app-on-simulated-or-physical-devices) — simulator scope and limitations.
- [Android: emulator command line](https://developer.android.com/studio/run/emulator-commandline) — AVDs, ports, and snapshot options.
- [Android: Android Debug Bridge](https://developer.android.com/tools/adb) — targeting devices, installing apps, and captures.
