# iPhone app — hosted website test client

Open `Flexagon.xcodeproj` and run the `Flexagon` scheme in **Debug** on
an iPhone simulator or a connected developer iPhone.

The Debug app opens **https://www.flexagon.fr/** inside a persistent WKWebView.
Sign in with the hosted WordPress account; local accounts were not copied. Published problems, progress, named languages,
figures, submissions, profiles and administrator review all come directly from the
website. Nothing is copied into a separate mobile problem database.

- The app keeps the existing icon and uses the website's mobile layout.
- Native Back, Home and Reload controls remain available below the website.
- Reference links open inside the same authenticated view, with a route back home.
- Website confirmation dialogs are supported, including unsaved changes.
- If the server is unavailable, a connection message and Try again button appear.
- Sign-in uses WordPress cookies and the site's existing permissions. Credentials
  are neither embedded in the app nor stored separately by native code.
- The local website does not need to be running. This test client needs internet access.

## Physical iPhone and production

`Flexagon/Debug-Info.plist` sets `CommunityWebsiteURL` to the hosted HTTPS
site. This works on both a simulator and a physical iPhone with internet access.
Choose the phone in Xcode, use your existing signing team and run the Debug scheme.
Device signing/installation must be completed from Xcode for the user's device.

For optional Mac-local development, change this Debug-only URL to
`http://127.0.0.1:9410/` and start **Open Website.command**. HTTP loopback is allowed
only in the simulator; a physical phone requires HTTPS. Removing the URL makes the
simulator fall back to localhost and displays a configuration message on a phone.

The embedded website is **Debug-only** for development testing. Release builds
still use the inherited native reader and need the production integration identified
in `docs/iphone-website-parity.md`. Do not distribute that foundation as the finished
community app. HTTP transport exceptions apply only to Debug and only to the two
loopback hosts. There is no global insecure-load exception.

- Minimum deployment target: iOS 17.
- App identifier: `com.flexagon.community`.
- Display name: Flexagon.
- The previous signing-team setting remains unchanged.

## Verification

All 22 tests passed on iPhone 17 Pro / iOS 26 against OVH on 13 October 2026. The
connection smoke check loads the configured WordPress landing page in WebKit and
verifies that anonymous access to problems remains denied. It uses WordPress’s
query REST route, which works with or without pretty permalinks.

```sh
DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer xcodebuild \
  -project ios/Flexagon.xcodeproj -scheme Flexagon \
  -destination 'platform=iOS Simulator,name=iPhone 17 Pro,OS=26.0' \
  -configuration Debug -derivedDataPath /private/tmp/lpdj-local-iphone-build \
  CODE_SIGNING_ALLOWED=NO test
```

`README-original.md` and `VERIFICATION-original.md` describe the historic reader.
The 40 pilot records remain inherited reader-test fixtures and resources; move them
into a test-only bundle before shipping the native release.
