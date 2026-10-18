#if DEBUG
import XCTest
import WebKit
@testable import Flexagon

final class CommunityWebsiteConfigurationTests: XCTestCase {
    func testSimulatorDefaultsToMacWebsiteAndPhysicalPhoneDoesNotUseLoopback() {
        XCTAssertEqual(CommunityWebsiteConfiguration.websiteURL(configured: nil, isSimulator: true)?.absoluteString, "http://127.0.0.1:9410/")
        XCTAssertNil(CommunityWebsiteConfiguration.websiteURL(configured: nil, isSimulator: false))
        XCTAssertNil(CommunityWebsiteConfiguration.websiteURL(configured: "http://127.0.0.1:9410", isSimulator: false))
        XCTAssertEqual(CommunityWebsiteConfiguration.websiteURL(configured: "https://example.test/", isSimulator: false)?.host, "example.test")
    }
    func testOnlySimulatorLoopbackMayUseHTTPAndCredentialsCannotBeInAddress() {
        for address in ["http://example.test/", "http://192.168.1.10/", "https://user:password@example.test/", "file:///private/test", "javascript:alert(1)", "https://example.test/?token=secret", "https://example.test/#/login"] {
            XCTAssertNil(CommunityWebsiteConfiguration.websiteURL(configured: address, isSimulator: true), address)
        }
    }
    func testInAppNavigationRequiresExactOriginIncludingPort() throws {
        let website = try XCTUnwrap(URL(string: "http://127.0.0.1:9410/"))
        XCTAssertTrue(CommunityWebsiteConfiguration.sameOrigin(URL(string: "http://127.0.0.1:9410/#/reference/1")!, website))
        for address in ["http://127.0.0.1:9401/", "https://127.0.0.1:9410/", "http://127.0.0.1.example.test:9410/", "http://user@127.0.0.1:9410/"] {
            XCTAssertFalse(CommunityWebsiteConfiguration.sameOrigin(URL(string: address)!, website), address)
        }
        XCTAssertTrue(CommunityWebsiteConfiguration.sameOrigin(URL(string: "https://example.test:443/path")!, URL(string: "https://example.test/")!))
    }
}

@MainActor
final class CommunityWebsiteConnectionTests: XCTestCase {
    /// This smoke check uses only anonymous reads. No users or problems are changed.
    func testConfiguredWordPressLoadsInWebKitAndKeepsProblemsBehindSignIn() async throws {
        #if targetEnvironment(simulator)
        let base = try XCTUnwrap(CommunityWebsiteConfiguration.current)
        let session = URLSession(configuration: .ephemeral)
        // The query route also works when WordPress pretty permalinks are disabled.
        func endpoint(_ path: String) -> URL {
            var components = URLComponents(url: base, resolvingAgainstBaseURL: false)!
            components.queryItems = [URLQueryItem(name: "rest_route", value: "/lpdj/v1/" + path)]
            return components.url!
        }
        var request = URLRequest(url: endpoint("session"))
        request.timeoutInterval = 20
        let (data, _) = try await session.data(for: request)
        let payload = try XCTUnwrap(JSONSerialization.jsonObject(with: data) as? [String: Any])
        XCTAssertEqual(payload["local"] as? Bool, base.scheme == "http")
        XCTAssertTrue(payload["user"] is NSNull)
        let (_, response) = try await session.data(from: endpoint("problems"))
        XCTAssertEqual((response as? HTTPURLResponse)?.statusCode, 401)

        let model = CommunityWebsiteModel(website: base, dataStore: .nonPersistent())
        model.webView.frame = CGRect(x: 0, y: 0, width: 390, height: 844)
        model.start()
        var body = ""
        for _ in 0..<200 {
            body = (try? await model.webView.evaluateJavaScript("document.body.innerText")) as? String ?? ""
            if body.contains("Curated list of mathematical puzzles") { break }
            try await Task.sleep(for: .milliseconds(100))
        }
        XCTAssertNil(model.errorMessage)
        XCTAssertTrue(body.contains("Curated list of mathematical puzzles"), body)
        XCTAssertTrue(body.contains("Sign In"))
        XCTAssertTrue(body.contains("Create Account"))
        XCTAssertEqual(model.webView.url?.host, base.host)
        #else
        throw XCTSkip("Website connection smoke test runs in the simulator.")
        #endif
    }
}
#endif
