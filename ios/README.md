# iPhone app — local website test client

Open `ProblemOfTheDay.xcodeproj` and run the `ProblemOfTheDay` scheme in **Debug** on
an iPhone simulator. Start **Open Website.command** from the repository root first.

The Debug app opens **http://127.0.0.1:9400/** inside a persistent WKWebView. Sign in
using the same local website account. Published problems, progress, named languages,
figures, submissions, profiles and administrator review all come directly from the
website. Nothing is copied into a separate mobile problem database.

- The app keeps the existing icon and uses the website's mobile layout.
- Native Back, Home and Reload controls remain available below the website.
- Reference links open inside the same authenticated view, with a route back home.
- Website confirmation dialogs are supported, including unsaved changes.
- If the server is unavailable, a connection message and Try again button appear.
- Sign-in uses WordPress cookies and the site's existing permissions. Credentials
  are neither embedded in the app nor stored separately by native code.
- The website must stay running on this Mac. This test client needs connectivity.

## Physical iPhone and production

The loopback address works in the simulator, which runs on this Mac. A physical
iPhone cannot reach the Mac through `127.0.0.1`. For a device, configure a reachable
HTTPS website using the `CommunityWebsiteURL` Info.plist key. No network sharing,
public tunnel, OVH deployment, or device signing was configured here.

The embedded website is **Debug-only** for the requested local test. Release builds
still use the inherited native reader and need the production integration identified
in `docs/iphone-website-parity.md`. Do not distribute that foundation as the finished
community app. HTTP transport exceptions apply only to Debug and only to the two
loopback hosts. There is no global insecure-load exception.

- Minimum deployment target: iOS 17.
- App identifier: `com.leproblemedujour.community`.
- Display name: Le Problème Communauté (development name).
- The previous signing-team setting remains unchanged.

## Verification

The existing 18 reader tests plus 4 connection/configuration tests pass on iPhone 17
Pro / iOS 26. The connection smoke check loads the real local WordPress landing page
in WebKit and verifies that anonymous access to problems remains denied. It skips
when the local website is not running; the URL-policy tests always run.

```sh
DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer xcodebuild \
  -project ios/ProblemOfTheDay.xcodeproj -scheme ProblemOfTheDay \
  -destination 'platform=iOS Simulator,name=iPhone 17 Pro,OS=26.0' \
  -configuration Debug -derivedDataPath /private/tmp/lpdj-local-iphone-build \
  CODE_SIGNING_ALLOWED=NO test
```

`README-original.md` and `VERIFICATION-original.md` describe the historic reader.
The 40 pilot records remain inherited reader-test fixtures and resources; move them
into a test-only bundle before shipping the native release.
