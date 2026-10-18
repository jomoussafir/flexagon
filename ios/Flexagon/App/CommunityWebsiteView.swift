#if DEBUG
import SwiftUI
import WebKit

/// The test client uses the real WordPress interface and its cookie session.
/// No credentials, published copies or privileged API bridges are bundled.
enum CommunityWebsiteConfiguration {
    static func websiteURL(configured: String?, isSimulator: Bool) -> URL? {
        let address = configured?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
        let candidate = address.isEmpty && isSimulator ? "http://127.0.0.1:9410/" : address
        guard let url = URL(string: candidate), let host = url.host?.lowercased(),
              url.user == nil, url.password == nil, url.query == nil, url.fragment == nil,
              url.scheme == "https" || (isSimulator && url.scheme == "http" && ["127.0.0.1", "localhost", "[::1]"].contains(host)) else { return nil }
        return url
    }

    static var current: URL? {
        #if targetEnvironment(simulator)
        let isSimulator = true
        #else
        let isSimulator = false
        #endif
        return websiteURL(configured: Bundle.main.object(forInfoDictionaryKey: "CommunityWebsiteURL") as? String,
                          isSimulator: isSimulator)
    }

    static func sameOrigin(_ candidate: URL, _ website: URL) -> Bool {
        func port(_ url: URL) -> Int { url.port ?? (url.scheme == "https" ? 443 : 80) }
        return candidate.user == nil && candidate.password == nil && candidate.scheme == website.scheme
            && candidate.host?.lowercased() == website.host?.lowercased() && port(candidate) == port(website)
    }
}

/// Keep the native controls in step with the selected website palette.
private enum CommunityWebsitePalette {
    case basquiat, vermeer
    static let current: Self = .vermeer

    var background: UIColor {
        switch self {
        case .basquiat: UIColor(red: 1, green: 246.0 / 255, blue: 228.0 / 255, alpha: 1)
        case .vermeer: UIColor(red: 246.0 / 255, green: 240.0 / 255, blue: 227.0 / 255, alpha: 1)
        }
    }
    var accent: Color {
        switch self {
        case .basquiat: Color(red: 23.0 / 255, green: 67.0 / 255, blue: 197.0 / 255)
        case .vermeer: Color(red: 40.0 / 255, green: 81.0 / 255, blue: 138.0 / 255)
        }
    }
}

@MainActor
final class CommunityWebsiteModel: NSObject, ObservableObject, WKNavigationDelegate, WKUIDelegate {
    struct Dialog: Identifiable {
        let id = UUID()
        let message: String
        let confirmation: Bool
        let respond: (Bool) -> Void
    }

    let website: URL
    let webView: WKWebView
    @Published var errorMessage: String?
    @Published var dialog: Dialog?
    @Published private(set) var loading = true
    @Published private(set) var canGoBack = false
    private var backObservation: NSKeyValueObservation?

    init(website: URL, dataStore: WKWebsiteDataStore = .default()) {
        self.website = website
        let configuration = WKWebViewConfiguration()
        configuration.websiteDataStore = dataStore
        webView = WKWebView(frame: .zero, configuration: configuration)
        super.init()
        webView.navigationDelegate = self
        webView.uiDelegate = self
        webView.allowsBackForwardNavigationGestures = true
        webView.accessibilityIdentifier = "community-website"
        webView.isOpaque = false
        webView.backgroundColor = CommunityWebsitePalette.current.background
        backObservation = webView.observe(\.canGoBack, options: [.new]) { [weak self] _, change in
            Task { @MainActor in self?.canGoBack = change.newValue ?? false }
        }
    }

    func start() { if webView.url == nil { retry() } }
    func retry() {
        errorMessage = nil
        loading = true
        webView.load(URLRequest(url: website, cachePolicy: .reloadIgnoringLocalCacheData, timeoutInterval: 20))
    }
    func home() {
        guard errorMessage == nil else { retry(); return }
        var components = URLComponents(url: website, resolvingAgainstBaseURL: false)!
        components.fragment = "/"
        // A fragment navigation keeps the website's unsaved-edit guard and session.
        webView.load(URLRequest(url: components.url!))
    }
    func back() { webView.goBack() }
    func reload() {
        if webView.url?.fragment?.hasPrefix("/editer/") == true {
            dialog = Dialog(message: "Reload this page? Any unsaved changes will be lost.", confirmation: true) { [weak self] confirmed in
                if confirmed { self?.performReload() }
            }
        } else { performReload() }
    }
    private func performReload() {
        if errorMessage != nil || webView.url == nil { retry() }
        else { webView.reload() }
    }

    func webView(_ webView: WKWebView, didStartProvisionalNavigation navigation: WKNavigation!) {
        loading = true
        errorMessage = nil
    }
    func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) { loading = false }
    func webView(_ webView: WKWebView, didFail navigation: WKNavigation!, withError error: Error) { failed(error) }
    func webView(_ webView: WKWebView, didFailProvisionalNavigation navigation: WKNavigation!, withError error: Error) { failed(error) }
    private func failed(_ error: Error) {
        if (error as NSError).code == NSURLErrorCancelled { return }
        loading = false
        errorMessage = website.scheme == "http"
            ? "Keep the local website running on your Mac, then try again."
            : "Check your internet connection, then try again. The app needs a connection to load problems."
    }
    func webViewWebContentProcessDidTerminate(_ webView: WKWebView) {
        loading = false
        errorMessage = "The website stopped responding. Reload to continue."
    }

    func webView(_ webView: WKWebView, decidePolicyFor navigationAction: WKNavigationAction,
                 decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) {
        guard let url = navigationAction.request.url else { decisionHandler(.cancel); return }
        if CommunityWebsiteConfiguration.sameOrigin(url, website) {
            decisionHandler(.allow)
        } else {
            decisionHandler(.cancel)
            if navigationAction.navigationType == .linkActivated && ["https", "http", "mailto"].contains(url.scheme ?? "") {
                UIApplication.shared.open(url)
            }
        }
    }
    func webView(_ webView: WKWebView, createWebViewWith configuration: WKWebViewConfiguration,
                 for navigationAction: WKNavigationAction, windowFeatures: WKWindowFeatures) -> WKWebView? {
        // Reference links use target=_blank. Keep them in the authenticated app,
        // with native Back and Home controls instead of handing the PDF to Safari.
        if navigationAction.targetFrame == nil, let url = navigationAction.request.url,
           CommunityWebsiteConfiguration.sameOrigin(url, website) {
            webView.load(navigationAction.request)
        }
        return nil
    }
    func webView(_ webView: WKWebView, runJavaScriptConfirmPanelWithMessage message: String,
                 initiatedByFrame frame: WKFrameInfo, completionHandler: @escaping (Bool) -> Void) {
        dialog = Dialog(message: message, confirmation: true, respond: completionHandler)
    }
    func webView(_ webView: WKWebView, runJavaScriptAlertPanelWithMessage message: String,
                 initiatedByFrame frame: WKFrameInfo, completionHandler: @escaping () -> Void) {
        dialog = Dialog(message: message, confirmation: false) { _ in completionHandler() }
    }
}

private struct CommunityWebView: UIViewRepresentable {
    let model: CommunityWebsiteModel
    func makeUIView(context: Context) -> WKWebView { model.start(); return model.webView }
    func updateUIView(_ uiView: WKWebView, context: Context) {}
}

struct CommunityWebsiteView: View {
    var body: some View {
        if let url = CommunityWebsiteConfiguration.current {
            ConnectedCommunityWebsite(website: url)
        } else {
            ContentUnavailableView("Website connection needed", systemImage: "network", description: Text("For local testing, run this app in the iPhone simulator on your Mac and start Open Website.command. A physical iPhone needs a reachable HTTPS website address configured in CommunityWebsiteURL."))
        }
    }
}

private struct ConnectedCommunityWebsite: View {
    @StateObject private var model: CommunityWebsiteModel
    init(website: URL) { _model = StateObject(wrappedValue: CommunityWebsiteModel(website: website)) }

    var body: some View {
        VStack(spacing: 0) {
            ZStack {
                CommunityWebView(model: model)
                if let message = model.errorMessage {
                    VStack(spacing: 18) {
                        ContentUnavailableView("Cannot connect to the website", systemImage: "wifi.exclamationmark", description: Text(message))
                        Button("Try again", action: model.retry).buttonStyle(.borderedProminent)
                    }.frame(maxWidth: .infinity, maxHeight: .infinity).background(Color(uiColor: .systemBackground))
                }
            }
            if model.loading { ProgressView().progressViewStyle(.linear).accessibilityLabel("Loading website") }
            Divider()
            HStack {
                Button(action: model.back) { Image(systemName: "chevron.left").frame(width: 44, height: 44) }
                    .disabled(!model.canGoBack).accessibilityLabel("Back")
                Spacer()
                Button(action: model.home) { Image(systemName: "house").frame(width: 44, height: 44) }
                    .accessibilityLabel("Home")
                Spacer()
                Button(action: model.reload) { Image(systemName: "arrow.clockwise").frame(width: 44, height: 44) }
                    .accessibilityLabel("Reload website")
            }.padding(.horizontal, 20).background(Color(uiColor: CommunityWebsitePalette.current.background))
        }
        .tint(CommunityWebsitePalette.current.accent)
        .preferredColorScheme(.light)
        .alert(item: $model.dialog) { dialog in
            if dialog.confirmation {
                return Alert(title: Text("Flexagon"), message: Text(dialog.message), primaryButton: .default(Text("Continue")) { dialog.respond(true) }, secondaryButton: .cancel { dialog.respond(false) })
            }
            return Alert(title: Text("Flexagon"), message: Text(dialog.message), dismissButton: .default(Text("OK")) { dialog.respond(true) })
        }
    }
}
#endif
