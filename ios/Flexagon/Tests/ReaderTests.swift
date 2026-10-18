import XCTest
import WebKit
import SwiftUI
@testable import Flexagon

@MainActor
final class ReaderTests: XCTestCase {
    func testDownloadedReaderUsesBundledMathAndBlocksScripts() async throws {
        let root = Bundle.main.resourceURL!.appendingPathComponent("Content/Reading")
        let original = try String(contentsOf: root.appendingPathComponent("animath-2024-01.html"), encoding: .utf8)
        let hostile = original.replacingOccurrences(of: "</body>", with: "<script>document.body.dataset.injected='yes'</script></body>")
        let host = UIHostingController(rootView: MathReader(problemID: "downloaded-fr", textSize: 23, publishedHTML: hostile))
        let scene = try XCTUnwrap(UIApplication.shared.connectedScenes.first as? UIWindowScene)
        let previous = scene.windows.first { $0.isKeyWindow }
        let window = UIWindow(windowScene: scene)
        window.frame = CGRect(x: 0, y: 0, width: 320, height: 700)
        window.rootViewController = host
        window.makeKeyAndVisible()
        host.view.frame = window.bounds
        host.view.layoutIfNeeded()
        defer { window.isHidden = true; previous?.makeKeyAndVisible() }
        func webView(in view: UIView) -> WKWebView? {
            if let web = view as? WKWebView { return web }
            return view.subviews.lazy.compactMap { webView(in: $0) }.first
        }
        var web: WKWebView?
        for _ in 0..<50 {
            web = webView(in: host.view)
            if let web, (try? await web.evaluateJavaScript("document.readyState === 'complete' && document.querySelectorAll('math').length > 0 && getComputedStyle(document.querySelector('.katex')).fontFamily.includes('KaTeX')")) as? Bool == true { break }
            try await Task.sleep(for: .milliseconds(100))
        }
        let reader = try XCTUnwrap(web)
        XCTAssertTrue(try XCTUnwrap(reader.url).isFileURL)
        XCTAssertEqual(reader.url?.lastPathComponent, "problem.html")
        XCTAssertGreaterThan(reader.bounds.height, 100)
        let statement = try await reader.evaluateJavaScript("document.body.innerText") as? String
        XCTAssertTrue(statement?.contains("Calculer") == true)
        let math = try await reader.evaluateJavaScript("document.querySelectorAll('math').length") as? Int
        XCTAssertGreaterThan(math ?? 0, 0)
        let styled = try await reader.evaluateJavaScript("getComputedStyle(document.querySelector('.katex')).fontFamily.includes('KaTeX')") as? Bool
        XCTAssertEqual(styled, true)
        let scriptRan = try await reader.evaluateJavaScript("document.body.dataset.injected === 'yes'") as? Bool
        XCTAssertEqual(scriptRan, false)
    }

    func testEveryReaderLoadsOfflineMathAndFitsPhoneWidth() async throws {
        let url = Bundle.main.resourceURL!.appendingPathComponent("Content")
        let data = try Data(contentsOf: url.appendingPathComponent("catalogue.json"))
        let problems = try JSONDecoder().decode([Problem].self, from: data)
        let web = WKWebView(frame: CGRect(x: 0, y: 0, width: 320, height: 700))
        let delegate = ReaderLoadDelegate()
        web.navigationDelegate = delegate
        for problem in problems {
            let source = try String(contentsOf: url.appendingPathComponent("Reading/\(problem.id).html"), encoding: .utf8)
            let expectsMath = source.contains("class=\"katex\"")
            let loaded = expectation(description: problem.id)
            delegate.loaded = loaded
            web.loadFileURL(url.appendingPathComponent("Reading/\(problem.id).html"), allowingReadAccessTo: url.appendingPathComponent("Reading"))
            await fulfillment(of: [loaded], timeout: 15)
            let mathCount = try await web.evaluateJavaScript("document.querySelectorAll('math').length") as? Int
            if expectsMath { XCTAssertGreaterThan(mathCount ?? 0, 0, problem.id) }
            let imagesOK = try await web.evaluateJavaScript("Array.from(document.images).every(i => i.complete && i.naturalWidth > 0)") as? Bool
            XCTAssertEqual(imagesOK, true, problem.id)
            let overflow = try await web.evaluateJavaScript("document.documentElement.scrollWidth > window.innerWidth + 1") as? Bool
            XCTAssertEqual(overflow, false, "Horizontal page overflow: \(problem.id)")
            if expectsMath {
                let katexStyled = try await web.evaluateJavaScript("getComputedStyle(document.querySelector('.katex')).fontFamily.includes('KaTeX')") as? Bool
                XCTAssertEqual(katexStyled, true, problem.id)
            }
        }
    }
}

@MainActor
private final class ReaderLoadDelegate: NSObject, WKNavigationDelegate {
    var loaded: XCTestExpectation?
    func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) { loaded?.fulfill(); loaded = nil }
    func webView(_ webView: WKWebView, didFail navigation: WKNavigation!, withError error: Error) { XCTFail(error.localizedDescription); loaded?.fulfill(); loaded = nil }
    func webView(_ webView: WKWebView, didFailProvisionalNavigation navigation: WKNavigation!, withError error: Error) { XCTFail(error.localizedDescription); loaded?.fulfill(); loaded = nil }
}
