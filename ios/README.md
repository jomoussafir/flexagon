# iPhone app — community edition foundation

This is a copy of the original SwiftUI reader, using the identical existing app icon.
Open `ProblemOfTheDay.xcodeproj` and run the `ProblemOfTheDay` scheme on an iPhone simulator.

- Minimum deployment target: iOS 17.
- App identifier: `com.leproblemedujour.community`.
- Display name: Le Problème Communauté (development name).
- The bundled published catalogue is empty. No server address is configured.
- Existing filters, progress tracking, offline mathematics and reader tests are retained.
- Authentication and submission features have not been implemented yet.

The original signing team setting was retained. Device signing and the new app identifier
will be checked when preparing the first physical-device build. No new identifier has
been registered with Apple, and no build has been installed or submitted by this setup.

From the repository root on this Mac:

```sh
DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer xcodebuild \
  -project ios/ProblemOfTheDay.xcodeproj -scheme ProblemOfTheDay \
  -sdk iphonesimulator -configuration Debug \
  -derivedDataPath /private/tmp/le-probleme-du-jour-build \
  CODE_SIGNING_ALLOWED=NO build
```

`README-original.md` and `VERIFICATION-original.md` are historical documentation from
the original project, not verification of the new website or mobile authentication.
The 40 pilot records and their reading assets remain as inherited test fixtures; the
app loads `Content/published-catalogue.json` for its actual library.
