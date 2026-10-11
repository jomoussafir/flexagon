import Foundation
import Combine

@MainActor
final class LibraryStore: ObservableObject {
    @Published private(set) var problems: [Problem] = []
    @Published private(set) var progress: [String: ProgressRecord] = [:]
    @Published var errorMessage: String?
    @Published private(set) var syncMessage: String?
    @Published private(set) var isRefreshing = false
    private let defaults: UserDefaults
    private let injectedCacheURL: URL?
    private var cacheURL: URL {
        if let injectedCacheURL { return injectedCacheURL }
        return FileManager.default.urls(for: .applicationSupportDirectory, in: .userDomainMask)[0]
            .appendingPathComponent("published-catalogue.json")
    }
    var feedURL: String {
        get { defaults.string(forKey: "catalogueFeedURL") ?? (Bundle.main.object(forInfoDictionaryKey: "CatalogueFeedURL") as? String ?? "") }
        set { defaults.set(newValue.trimmingCharacters(in: .whitespacesAndNewlines), forKey: "catalogueFeedURL") }
    }
    private let progressKey = "problemProgress.v1"

    init(bundle: Bundle = .main, defaults: UserDefaults = .standard, cacheURL: URL? = nil) {
        self.defaults = defaults
        self.injectedCacheURL = cacheURL
        do {
            guard let url = bundle.url(forResource: "published-catalogue", withExtension: "json", subdirectory: "Content") else {
                throw CocoaError(.fileNoSuchFile)
            }
            problems = try JSONDecoder().decode(PublishedCatalogue.self, from: Data(contentsOf: url)).validated()
            if let data = try? Data(contentsOf: self.cacheURL),
               let cached = try? JSONDecoder().decode(PublishedCatalogue.self, from: data),
               let validated = try? cached.validated() { problems = validated }
            if let data = defaults.data(forKey: progressKey) {
                progress = try JSONDecoder().decode([String: ProgressRecord].self, from: data)
            }
        } catch {
            errorMessage = "The library or saved progress could not be loaded. Your saved data has not been overwritten."
        }
    }

    func refresh(session: URLSession = .shared) async {
        guard !isRefreshing, !feedURL.isEmpty else { return }
        guard let url = URL(string: feedURL), url.scheme == "https", url.host != nil,
              url.user == nil, url.password == nil else {
            syncMessage = "Enter a valid HTTPS catalogue address."; return
        }
        isRefreshing = true
        defer { isRefreshing = false }
        do {
            var request = URLRequest(url: url, cachePolicy: .reloadIgnoringLocalCacheData, timeoutInterval: 30)
            request.setValue("application/json", forHTTPHeaderField: "Accept")
            let (data, response) = try await session.data(for: request)
            guard let http = response as? HTTPURLResponse, http.statusCode == 200,
                  http.url?.scheme == "https", data.count <= 50_000_000 else { throw URLError(.badServerResponse) }
            let catalogue = try JSONDecoder().decode(PublishedCatalogue.self, from: data)
            let next = try catalogue.validated()
            try FileManager.default.createDirectory(at: cacheURL.deletingLastPathComponent(), withIntermediateDirectories: true)
            try data.write(to: cacheURL, options: .atomic)
            problems = next
            syncMessage = "Up to date · \(next.count) problems"
        } catch {
            syncMessage = "Could not update. Your downloaded problems remain available."
        }
    }

    func record(for id: String) -> ProgressRecord { progress[id] ?? ProgressRecord() }
    func toggleBookmark(_ id: String) { setStatus(record(for: id).bookmarked ? .unseen : .bookmarked, for: id) }
    func setStatus(_ status: SolvingStatus, for id: String) { update(id) { $0.status = status } }
    func setNote(_ note: String, for id: String) { update(id) { $0.note = note } }

    private func update(_ id: String, mutation: (inout ProgressRecord) -> Void) {
        guard errorMessage == nil else { return }
        var record = record(for: id)
        mutation(&record)
        var next = progress
        next[id] = record
        do {
            let data = try JSONEncoder().encode(next)
            defaults.set(data, forKey: progressKey)
            progress = next
        } catch { errorMessage = "Your progress could not be saved. Please try again." }
    }
}
