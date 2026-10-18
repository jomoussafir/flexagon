import XCTest
@testable import Flexagon

@MainActor
final class CatalogueTests: XCTestCase {
    private func freshDefaults() -> UserDefaults {
        let name = "FlexagonTests.\(UUID().uuidString)"
        let defaults = UserDefaults(suiteName: name)!
        addTeardownBlock { defaults.removePersistentDomain(forName: name) }
        return defaults
    }
    private func pilotProblems() -> [Problem] {
        let url = Bundle.main.url(forResource: "catalogue", withExtension: "json", subdirectory: "Content")!
        return try! JSONDecoder().decode([Problem].self, from: Data(contentsOf: url))
    }
    func testAllBundledProblemsHaveOfflineAssets() throws {
        let store = LibraryStore(defaults: freshDefaults(), cacheURL: FileManager.default.temporaryDirectory.appendingPathComponent(UUID().uuidString + ".json"))
        XCTAssertNil(store.errorMessage)
        XCTAssertTrue(store.feedURL.isEmpty)
        XCTAssertTrue(store.problems.isEmpty)
        let problems = pilotProblems()
        XCTAssertEqual(problems.count, 40)
        XCTAssertEqual(Set(problems.map(\.id)).count, 40)
        for problem in problems {
            let root = Bundle.main.resourceURL!.appendingPathComponent("Content")
            XCTAssertTrue(FileManager.default.fileExists(atPath: root.appendingPathComponent("PDFs/\(problem.id).pdf").path))
            let html = try String(contentsOf: root.appendingPathComponent("Reading/\(problem.id).html"), encoding: .utf8)
            XCTAssertTrue(html.contains("katex"))
            XCTAssertFalse(html.contains("{{FONT_SIZE}}"))
            XCTAssertFalse(html.contains("<script"))
        }
    }
    func testCombinedFiltersAndDiacriticSearch() {
        let store = LibraryStore(defaults: freshDefaults(), cacheURL: FileManager.default.temporaryDirectory.appendingPathComponent(UUID().uuidString + ".json"))
        var f = ProblemFilter(category: .geometry, difficulty: 3, language: "en")
        XCTAssertTrue(pilotProblems().filter(f.matches).allSatisfy { $0.category == .geometry && $0.difficulty == 3 })
        f.difficulty = 1
        XCTAssertTrue(pilotProblems().filter(f.matches).isEmpty)
        f = ProblemFilter(query: "DIFFERENCE AU CARRE")
        XCTAssertEqual(pilotProblems().filter(f.matches).map(\.id), ["animath-2024-01"])
        f = ProblemFilter(source: "International Mathematical Olympiad 2024")
        XCTAssertEqual(pilotProblems().filter(f.matches).count, 2)
    }
    func testProgressChoicesSurviveRelaunch() {
        let defaults = freshDefaults()
        let store = LibraryStore(defaults: defaults)
        let id = "animath-2024-01"
        store.setNote("Try a factorisation", for: id)
        for status in SolvingStatus.allCases {
            store.setStatus(status, for: id)
            let restored = LibraryStore(defaults: defaults)
            XCTAssertEqual(restored.record(for: id), ProgressRecord(status: status, note: "Try a factorisation"))
            XCTAssertEqual(restored.record(for: id).bookmarked, status == .bookmarked)
        }
    }
    func testLegacyProgressMigrationKeepsNotesAndCompletedWork() throws {
        for (oldStatus, expected) in [("unseen",SolvingStatus.bookmarked),("attempted",.attempted),("solved",.solved)] {
            let json = "{\"bookmarked\":true,\"status\":\"\(oldStatus)\",\"note\":\"Keep me\"}"
            let record = try JSONDecoder().decode(ProgressRecord.self, from: Data(json.utf8))
            XCTAssertEqual(record.status, expected)
            XCTAssertEqual(record.note, "Keep me")
        }
    }
    func testCompetitionGroupsDatesAndCombinedProgressFilters() throws {
        let problems = pilotProblems()
        let imo = try XCTUnwrap(problems.first { $0.id == "imo-2024-01" })
        let animath = try XCTUnwrap(problems.first { $0.id == "animath-2024-01" })
        XCTAssertEqual(imo.category.rawValue, imo.topic)
        XCTAssertEqual(animath.category.rawValue, animath.topic)
        XCTAssertEqual(imo.displayTitle(language:"en"), "IMO 2024 Problem 1")
        XCTAssertEqual(animath.displayTitle(language:"fr"), "Animath 2024 Problème 1")
        let filter = ProblemFilter(category:imo.category, difficulty:imo.difficulty, source:imo.sources[0].title, progress:.bookmarked)
        XCTAssertTrue(filter.matches(imo, record:ProgressRecord(status:.bookmarked)))
        XCTAssertFalse(filter.matches(imo, record:ProgressRecord(status:.solved)))
        XCTAssertFalse(filter.matches(animath, record:ProgressRecord(status:.bookmarked)))
        XCTAssertTrue(ProblemFilter(progress:.unseen).matches(imo, record:ProgressRecord()))
    }
    func testPickOnePoolDefaultsToAllAndCombinesEveryProgressFilter() throws {
        let problems = pilotProblems()
        let first = try XCTUnwrap(problems.first { $0.sources.contains { $0.group == "IMO" } })
        var filter = ProblemFilter(category:first.category, difficulty:first.difficulty, source:first.sources[0].title)
        let all = filter.candidates(in:problems, progress:[:])
        XCTAssertFalse(all.isEmpty)
        XCTAssertTrue(all.allSatisfy { $0.sources.contains { $0.group == "IMO" } && $0.difficulty == first.difficulty && $0.sources.contains { $0.title == first.sources[0].title } })
        XCTAssertNil(filter.progress)
        for state in SolvingStatus.allCases {
            let records = Dictionary(uniqueKeysWithValues:all.map { ($0.id, ProgressRecord(status:state)) })
            filter.progress = nil
            XCTAssertEqual(filter.candidates(in:problems, progress:records), all)
            for selected in SolvingStatus.allCases {
                filter.progress = selected
                XCTAssertEqual(filter.candidates(in:problems, progress:records), selected == state ? all : [])
            }
        }
        filter.progress = .unseen
        XCTAssertEqual(filter.candidates(in:problems, progress:[:]), all)
        XCTAssertTrue(filter.candidates(in:[], progress:[:]).isEmpty)
    }
    func testSourceGroupsCombineYearsAndVolumesWithoutChangingOtherSources() {
        let cases: [(String, String, Flexagon.Category)] = [
            ("International Mathematical Olympiad 1959", "IMO", .logic),
            ("International Mathematical Olympiad 2026", "IMO", .logic),
            ("Coupe Animath - Automne 2021", "Animath", .logic),
            ("Coupe Animath - Automne 2024", "Animath", .logic),
            ("Yaglom Vol 1", "Yaglom", .logic),
            ("Yaglom Vol 2", "Yaglom", .logic),
            ("The Stanford Mathematics Problem Book", "The Stanford Mathematics Problem Book", .logic)
        ]
        for (title, group, category) in cases {
            let p = Problem(id:"group-test", title:"A problem", language:"en", topic:"logic", difficulty:3, searchText:"", editorialNote:"", sources:[Problem.Source(title:title,number:"1",page:1,url:nil)], hasFigure:false)
            XCTAssertEqual(p.sources[0].group, group)
            XCTAssertEqual(p.category, category)
            XCTAssertTrue(ProblemFilter(category:category,source:group).matches(p))
            XCTAssertFalse(ProblemFilter(source:"Unrelated source").matches(p))
        }
    }
    func testChallengingBooksShareOneSourceInRequestedOrder() {
        let names = ["IMO", "Yaglom", "Challenging Problems In Algebra", "The Moscow Puzzles", "Animath", "Challenging Problems In Geometry", "The Stanford Mathematics Problem Book", "The Colossal Book of Short Puzzles and Problems"]
        let summary = PublishedSourceCount.summary([], including: names)
        XCTAssertEqual(summary.map(\.name), ["The Moscow Puzzles", "The Colossal Book of Short Puzzles and Problems", "Animath", "Challenging Problems in Geometry and Algebra", "Yaglom", "The Stanford Mathematics Problem Book", "IMO"])
        for title in ["Challenging Problems In Algebra", "Challenging Problems In Geometry"] {
            let p = Problem(id: title.contains("Algebra") ? "algebra-test" : "geometry-test", title: "Example", language: "en", topic: "geometry", difficulty: 3, searchText: "", editorialNote: "", sources: [.init(title: title, number: "1", page: 1, url: nil)], hasFigure: false)
            XCTAssertTrue(ProblemFilter(source: "Challenging Problems in Geometry and Algebra").matches(p))
            XCTAssertEqual(p.category, .geometry)
        }
    }
    func testLegacyPublishedSourceCategoriesStillLoadOffline() throws {
        let p = Problem(versions: [Problem.Translation(language: "en", title: "Problem", html: "<p>Statement</p>")], id: "imo-1959-01", title: "Problem", language: "en", topic: "imo", difficulty: 3, searchText: "", editorialNote: "", sources: [], hasFigure: false)
        let rows = try PublishedCatalogue(schemaVersion: 1, revision: "legacy", problems: [p]).validated()
        XCTAssertEqual(rows.first?.category, .algebra)
    }
    func testPublishedCountsDeduplicateSourceReferencesAndKeepSubjectsSeparate() {
        let source = Problem.Source(title: "International Mathematical Olympiad 2024", number: "1", page: 1, url: nil)
        let p = Problem(id: "count-test", title: "Example", language: "en", topic: "geometry", difficulty: 3, searchText: "", editorialNote: "", sources: [source, source], hasFigure: false)
        XCTAssertEqual(p.category, .geometry)
        XCTAssertEqual(Category.allCases.count, 5)
        let summary = PublishedSourceCount.summary([p, p], including: ["Yaglom"])
        XCTAssertEqual(summary.first { $0.name == "IMO" }?.count, 1)
        XCTAssertEqual(summary.first { $0.name == "Yaglom" }?.count, 0)
    }
    func testDailySelectionIsStableAndRespectsLevel() {
        let store = LibraryStore(defaults: freshDefaults(), cacheURL: FileManager.default.temporaryDirectory.appendingPathComponent(UUID().uuidString + ".json"))
        var calendar = Calendar(identifier: .gregorian)
        calendar.timeZone = TimeZone(secondsFromGMT: 0)!
        let morning = calendar.date(from: DateComponents(year: 2026, month: 9, day: 18, hour: 8))!
        let evening = morning.addingTimeInterval(10 * 3600)
        for level in 1...5 {
            let first = DailySelection.choose(from: pilotProblems(), date: morning, level: level, calendar: calendar)
            XCTAssertEqual(first?.difficulty, level)
            XCTAssertEqual(first?.id, DailySelection.choose(from: pilotProblems().reversed(), date: evening, level: level, calendar: calendar)?.id)
        }
        XCTAssertNil(DailySelection.choose(from: [], date: morning, level: 2))
    }
    func testCorruptSavedProgressIsNotOverwritten() {
        let defaults = freshDefaults();let invalid = Data("invalid".utf8)
        defaults.set(invalid, forKey: "problemProgress.v1")
        let store = LibraryStore(defaults: defaults)
        XCTAssertNotNil(store.errorMessage)
        store.toggleBookmark("animath-2024-01")
        XCTAssertEqual(defaults.data(forKey: "problemProgress.v1"), invalid)
    }
}

final class PublicationTests: XCTestCase {
    func fixture(_ languages: [String]) throws -> PublishedCatalogue {
        let versions = languages.map { ["language": $0, "title": "A problem", "html": "<p>Statement</p>"] }
        let record: [String: Any] = ["id":"test-problem","title":"A problem","language":languages.first ?? "en","topic":"algebra","difficulty":2,"searchText":"problem","editorialNote":"reviewed","sources":[],"hasFigure":false,"versions":versions]
        let data = try JSONSerialization.data(withJSONObject: ["schemaVersion":1,"revision":"test","problems":[record]])
        return try JSONDecoder().decode(PublishedCatalogue.self, from: data)
    }
    func testOnlyPublishedLanguagesAreAvailable() throws {
        let french = try fixture(["fr"]).validated()[0]
        XCTAssertEqual(french.preferredLanguage("en"), "fr")
        XCTAssertFalse(ProblemFilter(language:"en").matches(french))
        XCTAssertTrue(ProblemFilter(language:"fr").matches(french))
        let both = try fixture(["en", "fr"]).validated()[0]
        XCTAssertEqual(both.preferredLanguage("fr"), "fr")
        XCTAssertEqual(both.preferredLanguage("en"), "en")
    }
    func testEmptyOrDuplicateLanguagesCannotEnterPublishedLibrary() throws {
        XCTAssertThrowsError(try fixture([]).validated())
        XCTAssertThrowsError(try fixture(["fr","fr"]).validated())
        XCTAssertThrowsError(try fixture(["de"]).validated())
    }
    func testAnEmptyPublicationCanWithdrawAllProblems() throws {
        XCTAssertTrue(try PublishedCatalogue(schemaVersion:1,revision:"withdrawn",problems:[]).validated().isEmpty)
    }
}

private final class FeedProtocol: URLProtocol {
    static var payload = Data()
    static var status = 200
    override class func canInit(with request: URLRequest) -> Bool { true }
    override class func canonicalRequest(for request: URLRequest) -> URLRequest { request }
    override func startLoading() {
        let response = HTTPURLResponse(url: request.url!, statusCode: Self.status, httpVersion: nil, headerFields: ["Content-Type":"application/json"])!
        client?.urlProtocol(self, didReceive: response, cacheStoragePolicy: .notAllowed)
        client?.urlProtocol(self, didLoad: Self.payload)
        client?.urlProtocolDidFinishLoading(self)
    }
    override func stopLoading() {}
}

@MainActor
final class CatalogueSyncTests: XCTestCase {
    func testAtomicRefreshOfflineRecoveryAndWithdrawalPreserveProgress() async throws {
        let name = "SyncTests.\(UUID().uuidString)"
        let defaults = UserDefaults(suiteName: name)!
        let cache = FileManager.default.temporaryDirectory.appendingPathComponent(UUID().uuidString + ".json")
        defer { defaults.removePersistentDomain(forName:name); try? FileManager.default.removeItem(at:cache) }
        let config = URLSessionConfiguration.ephemeral
        config.protocolClasses = [FeedProtocol.self]
        let session = URLSession(configuration:config)
        defer { session.invalidateAndCancel() }
        let store = LibraryStore(defaults:defaults, cacheURL:cache)
        store.feedURL = "https://example.test/catalogue.json"
        let fixture = try PublicationTests().fixture(["fr", "en"])
        FeedProtocol.payload = try JSONEncoder().encode(fixture); FeedProtocol.status = 200
        await store.refresh(session:session)
        XCTAssertEqual(store.problems.count,1)
        store.setNote("Keep this idea", for:"test-problem")
        let before = try Data(contentsOf:cache)
        FeedProtocol.payload = Data("broken JSON".utf8)
        await store.refresh(session:session)
        XCTAssertEqual(store.problems.count,1)
        XCTAssertEqual(try Data(contentsOf:cache),before)
        let offline = LibraryStore(defaults:defaults,cacheURL:cache)
        XCTAssertEqual(offline.problems.count,1)
        XCTAssertEqual(offline.record(for:"test-problem").note,"Keep this idea")
        FeedProtocol.payload = try JSONEncoder().encode(PublishedCatalogue(schemaVersion:1,revision:"withdraw",problems:[]))
        await store.refresh(session:session)
        XCTAssertTrue(store.problems.isEmpty)
        XCTAssertEqual(store.record(for:"test-problem").note,"Keep this idea")
    }
}
