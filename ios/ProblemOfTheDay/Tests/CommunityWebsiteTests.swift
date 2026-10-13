#if DEBUG
import XCTest
import WebKit
@testable import ProblemOfTheDay

final class CommunityWebsiteConfigurationTests: XCTestCase {
    func testSimulatorDefaultsToMacWebsiteAndPhysicalPhoneDoesNotUseLoopback() {
        XCTAssertEqual(CommunityWebsiteConfiguration.websiteURL(configured: nil, isSimulator: true)?.absoluteString, "http://127.0.0.1:9400/")
        XCTAssertNil(CommunityWebsiteConfiguration.websiteURL(configured: nil, isSimulator: false))
        XCTAssertNil(CommunityWebsiteConfiguration.websiteURL(configured: "http://127.0.0.1:9400", isSimulator: false))
        XCTAssertEqual(CommunityWebsiteConfiguration.websiteURL(configured: "https://example.test/", isSimulator: false)?.host, "example.test")
    }
    func testOnlySimulatorLoopbackMayUseHTTPAndCredentialsCannotBeInAddress() {
        for address in ["http://example.test/", "http://192.168.1.10/", "https://user:password@example.test/", "file:///private/test", "javascript:alert(1)", "https://example.test/?token=secret", "https://example.test/#/login"] {
            XCTAssertNil(CommunityWebsiteConfiguration.websiteURL(configured: address, isSimulator: true), address)
        }
    }
    func testInAppNavigationRequiresExactOriginIncludingPort() throws {
        let website = try XCTUnwrap(URL(string: "http://127.0.0.1:9400/"))
        XCTAssertTrue(CommunityWebsiteConfiguration.sameOrigin(URL(string: "http://127.0.0.1:9400/#/reference/1")!, website))
        for address in ["http://127.0.0.1:9401/", "https://127.0.0.1:9400/", "http://127.0.0.1.example.test:9400/", "http://user@127.0.0.1:9400/"] {
            XCTAssertFalse(CommunityWebsiteConfiguration.sameOrigin(URL(string: address)!, website), address)
        }
        XCTAssertTrue(CommunityWebsiteConfiguration.sameOrigin(URL(string: "https://example.test:443/path")!, URL(string: "https://example.test/")!))
    }
}

@MainActor
final class CommunityWebsiteConnectionTests: XCTestCase {
    /// This smoke check uses only anonymous reads. No users or problems are changed.
    func testLocalWordPressLoadsInWebKitAndKeepsProblemsBehindSignIn() async throws {
        #if targetEnvironment(simulator)
        let base = URL(string: "http://127.0.0.1:9400/")!
        let session = URLSession(configuration: .ephemeral)
        var request = URLRequest(url: base.appendingPathComponent("wp-json/lpdj/v1/session"))
        request.timeoutInterval = 3
        let data: Data
        do { (data, _) = try await session.data(for: request) }
        catch { throw XCTSkip("Start Open Website.command to run the local connection smoke check: \(error.localizedDescription)") }
        let payload = try XCTUnwrap(JSONSerialization.jsonObject(with: data) as? [String: Any])
        XCTAssertEqual(payload["local"] as? Bool, true)
        XCTAssertTrue(payload["user"] is NSNull)
        let (_, response) = try await session.data(from: base.appendingPathComponent("wp-json/lpdj/v1/problems"))
        XCTAssertEqual((response as? HTTPURLResponse)?.statusCode, 401)

        let model = CommunityWebsiteModel(website: base, dataStore: .nonPersistent())
        model.webView.frame = CGRect(x: 0, y: 0, width: 390, height: 844)
        model.start()
        var body = ""
        for _ in 0..<100 {
            body = (try? await model.webView.evaluateJavaScript("document.body.innerText")) as? String ?? ""
            if body.contains("Curated list of mathematical puzzles") { break }
            try await Task.sleep(for: .milliseconds(100))
        }
        XCTAssertNil(model.errorMessage)
        XCTAssertTrue(body.contains("Curated list of mathematical puzzles"), body)
        XCTAssertTrue(body.contains("Sign In"))
        XCTAssertTrue(body.contains("Create Account"))
        XCTAssertEqual(model.webView.url?.host, "127.0.0.1")
        #else
        throw XCTSkip("Mac-local website smoke test runs in the simulator.")
        #endif
    }
}
#endif
