import SwiftUI
import WebKit
import PDFKit

struct ProblemDetailView: View {
    @EnvironmentObject private var store: LibraryStore
    let problem: Problem
    @AppStorage("preferredProblemLanguage") private var preferredLanguage = "fr"
    private var current: Problem { store.problems.first { $0.id == problem.id } ?? problem }
    private var language: String { current.preferredLanguage(preferredLanguage) }
    private var readerHTML: String? {
        guard let html = current.versions?.first(where: { $0.language == language })?.html else { return nil }
        guard current.datedSource != nil,
              let heading = html.range(of: "<h1>.*?</h1>", options: [.regularExpression, .caseInsensitive]) else { return html }
        let title = current.displayTitle(language: language).replacingOccurrences(of: "&", with: "&amp;").replacingOccurrences(of: "<", with: "&lt;").replacingOccurrences(of: ">", with: "&gt;")
        return html.replacingCharacters(in: heading, with: "<h1>\(title)</h1>")
    }
    @State private var readerError: String?
    @State private var readerAttempt = 0
    @State private var showPDF = false
    @State private var showNotes = false
    @State private var showSource = false
    @ScaledMetric(relativeTo: .body) private var textSize = 19.0
    private var record: ProgressRecord { store.record(for: problem.id) }
    var body: some View {
        if store.problems.contains(where: { $0.id == problem.id }) { detail }
        else { ContentUnavailableView("Problem withdrawn", systemImage: "doc.badge.ellipsis", description: Text("This problem is no longer in the published catalogue. Your notes and progress are saved.")) }
    }
    private var detail: some View {
        VStack(spacing: 0) {
            if current.availableLanguages.count > 1 {
                Picker("Problem language", selection: Binding(get: { language }, set: { preferredLanguage = $0 })) {
                    ForEach(current.availableLanguages, id: \.self) { Text($0.uppercased()).tag($0) }
                }.pickerStyle(.segmented).padding(.horizontal, 20).padding(.vertical, 10)
            }
            ZStack {
                MathReader(problemID: problem.id + (current.versions == nil ? "" : "-" + language), textSize: textSize,
                           publishedHTML: readerHTML, onError: { readerError = $0 })
                    .id(readerAttempt)
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
                if let readerError {
                    VStack(spacing: 16) {
                        ContentUnavailableView("Could not display the problem", systemImage: "doc.text", description: Text(readerError))
                        Button("Try again") { self.readerError = nil; readerAttempt += 1 }
                            .buttonStyle(.borderedProminent)
                    }.background(Palette.paper)
                }
            }.frame(maxWidth: .infinity, maxHeight: .infinity)
        }
            .background(Palette.paper)
            .navigationTitle(current.category.title).navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItemGroup(placement: .topBarTrailing) {
                    Menu {
                        if current.versions == nil { Button("View PDF", systemImage: "doc.richtext") { showPDF = true } }
                        Button("My notes", systemImage: "square.and.pencil") { showNotes = true }
                        Button("Source & details", systemImage: "info.circle") { showSource = true }
                    } label: { Image(systemName: "ellipsis.circle") }.accessibilityLabel("Problem actions")
                }
            }
            .safeAreaInset(edge: .bottom) {
                VStack(spacing: 8) {
                    HStack {
                        Text("Progress").font(.caption).foregroundStyle(.secondary)
                        Spacer()
                        Button { showNotes = true } label: { Label(record.note.isEmpty ? "Add a note" : "My notes", systemImage: "square.and.pencil") }.font(.caption)
                    }
                    Picker("Progress", selection: Binding(get: { record.status }, set: { store.setStatus($0, for: problem.id) })) {
                        ForEach(SolvingStatus.allCases) { Text($0.title).tag($0) }
                    }.pickerStyle(.segmented).accessibilityIdentifier("solving-status")
                }.padding(.horizontal, 20).padding(.vertical, 12).background(.regularMaterial)
            }
            .sheet(isPresented: $showPDF) { PDFSheet(problem: problem) }
            .sheet(isPresented: $showNotes) { NotesSheet(problem: problem) }
            .sheet(isPresented: $showSource) { SourceSheet(problem: problem) }
    }
}

struct MathReader: UIViewRepresentable {
    let problemID: String
    let textSize: Double
    var publishedHTML: String? = nil
    var onError: ((String?) -> Void)? = nil
    func makeCoordinator() -> Coordinator { Coordinator() }
    func makeUIView(context: Context) -> WKWebView {
        let configuration = WKWebViewConfiguration()
        configuration.websiteDataStore = .nonPersistent()
        let view = WKWebView(frame: .zero, configuration: configuration)
        view.isOpaque = false
        view.backgroundColor = .clear
        view.scrollView.backgroundColor = .clear
        view.navigationDelegate = context.coordinator
        view.accessibilityIdentifier = "math-reader"
        return view
    }
    func updateUIView(_ view: WKWebView, context: Context) {
        context.coordinator.onError = onError
        context.coordinator.fontSize = textSize
        guard context.coordinator.loadedID != problemID || context.coordinator.loadedHTML != publishedHTML else {
            context.coordinator.applyFont(to: view)
            return
        }
        context.coordinator.loadedID = problemID
        context.coordinator.loadedHTML = publishedHTML
        if let html = publishedHTML, let root = Bundle.main.resourceURL?.appendingPathComponent("Content/Reading", isDirectory: true) {
            // Load a real local document with an explicit read grant. A file base URL
            // on loadHTMLString does not grant WebKit access on a physical iPhone.
            // The native CSP prevents downloaded content from enabling scripts/network.
            let policy = "<meta http-equiv=\"Content-Security-Policy\" content=\"default-src 'none'; style-src 'self' 'unsafe-inline'; font-src 'self' data:; img-src data:; script-src 'none'; connect-src 'none'; frame-src 'none'\">"
            do {
                let directory = try context.coordinator.prepareDocument(policy + html, assets: root)
                context.coordinator.allowedRoot = directory.resolvingSymlinksInPath().path
                context.coordinator.recoveryAttempts = 0
                view.loadFileURL(directory.appendingPathComponent("problem.html"), allowingReadAccessTo: directory)
            } catch {
                DispatchQueue.main.async { context.coordinator.onError?("The downloaded statement could not be prepared. Please try again.") }
            }
            return
        }
        guard let root = Bundle.main.resourceURL?.appendingPathComponent("Content/Reading", isDirectory: true),
              FileManager.default.fileExists(atPath: root.appendingPathComponent(problemID + ".html").path) else {
            view.loadHTMLString("<h2>This problem could not be opened.</h2><p>Try View PDF from the menu.</p>", baseURL: nil)
            return
        }
        context.coordinator.allowedRoot = root.resolvingSymlinksInPath().path
        view.loadFileURL(root.appendingPathComponent(problemID + ".html"), allowingReadAccessTo: root)
    }
    final class Coordinator: NSObject, WKNavigationDelegate {
        var onError: ((String?) -> Void)?
        var recoveryAttempts = 0
        private var documentDirectory: URL?
        func prepareDocument(_ html: String, assets: URL) throws -> URL {
            let directory: URL
            if let existing = documentDirectory { directory = existing }
            else {
                directory = FileManager.default.temporaryDirectory.appendingPathComponent("ProblemReader-" + UUID().uuidString, isDirectory: true)
                try FileManager.default.createDirectory(at: directory, withIntermediateDirectories: true)
                documentDirectory = directory
                try FileManager.default.copyItem(at: assets.appendingPathComponent("katex"), to: directory.appendingPathComponent("katex"))
            }
            try html.write(to: directory.appendingPathComponent("problem.html"), atomically: true, encoding: .utf8)
            return directory
        }
        deinit {
            if let documentDirectory { try? FileManager.default.removeItem(at: documentDirectory) }
        }
        var loadedHTML: String?
        var loadedID: String?
        var allowedRoot = ""
        var fontSize = 19.0
        private var appliedSize: Double?
        func applyFont(to view: WKWebView) {
            guard appliedSize != fontSize else { return }
            appliedSize = fontSize
            view.evaluateJavaScript("document.body.style.fontSize = '\(fontSize)px';", completionHandler: nil)
        }
        func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
            appliedSize = nil
            applyFont(to: webView)
            onError?(nil)
        }
        func webView(_ webView: WKWebView, didFail navigation: WKNavigation!, withError error: Error) {
            report(error)
        }
        func webView(_ webView: WKWebView, didFailProvisionalNavigation navigation: WKNavigation!, withError error: Error) {
            report(error)
        }
        private func report(_ error: Error) {
            guard (error as NSError).code != NSURLErrorCancelled else { return }
            onError?("The statement could not be loaded. Please try again.")
        }
        func webViewWebContentProcessDidTerminate(_ webView: WKWebView) {
            if recoveryAttempts == 0 {
                recoveryAttempts += 1
                webView.reload()
            } else { onError?("The reader stopped unexpectedly. Please try again.") }
        }
        func webView(_ webView: WKWebView, decidePolicyFor action: WKNavigationAction, decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) {
            guard let url = action.request.url else { decisionHandler(.cancel); return }
            let path = url.standardizedFileURL.resolvingSymlinksInPath().path
            let isBundledFile = url.isFileURL && (path == allowedRoot || path.hasPrefix(allowedRoot + "/"))
            decisionHandler(isBundledFile || url.absoluteString == "about:blank" ? .allow : .cancel)
        }
    }
}

struct PDFSheet: View {
    @Environment(\.dismiss) private var dismiss
    let problem: Problem
    var body: some View {
        NavigationStack {
            if let url = Bundle.main.url(forResource: problem.id, withExtension: "pdf", subdirectory: "Content/PDFs") {
                PDFReader(url: url).navigationTitle("Problem PDF").navigationBarTitleDisplayMode(.inline)
                    .toolbar {
                        ToolbarItem(placement: .cancellationAction) { Button("Done") { dismiss() } }
                        ToolbarItem(placement: .primaryAction) { ShareLink(item: url) { Label("Share PDF", systemImage: "square.and.arrow.up") } }
                    }
            } else {
                ContentUnavailableView("PDF unavailable", systemImage: "doc")
                    .toolbar { Button("Done") { dismiss() } }
            }
        }
    }
}
struct PDFReader: UIViewRepresentable {
    let url: URL
    func makeUIView(context: Context) -> PDFView {
        let view = PDFView(); view.autoScales = true; view.displayMode = .singlePageContinuous
        view.document = PDFDocument(url: url)
        return view
    }
    func updateUIView(_ view: PDFView, context: Context) {}
}

struct NotesSheet: View {
    @EnvironmentObject private var store: LibraryStore
    @Environment(\.dismiss) private var dismiss
    let problem: Problem
    var body: some View {
        NavigationStack {
            VStack(alignment: .leading, spacing: 12) {
                Text(problem.displayTitle()).font(.system(.title3, design: .serif))
                Text("Ideas, observations, a possible first step…").font(.subheadline).foregroundStyle(.secondary)
                TextEditor(text: Binding(get: { store.record(for: problem.id).note }, set: { store.setNote($0, for: problem.id) }))
                    .scrollContentBackground(.hidden).accessibilityLabel("Problem notes")
            }.padding(20).background(Palette.paper).navigationTitle("My notes").navigationBarTitleDisplayMode(.inline)
                .toolbar { ToolbarItem(placement: .confirmationAction) { Button("Done") { dismiss() } } }
        }
    }
}

struct SourceSheet: View {
    @Environment(\.dismiss) private var dismiss
    let problem: Problem
    var body: some View {
        NavigationStack {
            List {
                Section("Original sources") {
                    ForEach(Array(problem.sources.enumerated()), id: \.offset) { _, source in
                        VStack(alignment: .leading, spacing: 8) {
                            Text(source.title).font(.headline)
                            Text("Problem \(source.number) · PDF page \(source.page)").font(.subheadline)
                            if let address = source.url, let url = URL(string: address), url.scheme == "https" {
                                Link("Visit source website", destination: url)
                            }
                        }.padding(.vertical, 6)
                    }
                }
                Section("Editorial note") { Text(problem.editorialNote) }
                Section("Review") {
                    Text(problem.versions == nil ? "Independent human review pending." : "Available language versions have been verified for publication.")
                    Text("Level \(problem.difficulty)/5 is provisional. Hints and solutions have not yet been imported.")
                }
                Section { Text(problem.id).font(.caption).foregroundStyle(.secondary) }
            }.navigationTitle("Source & details").navigationBarTitleDisplayMode(.inline)
                .toolbar { ToolbarItem(placement: .confirmationAction) { Button("Done") { dismiss() } } }
        }
    }
}
