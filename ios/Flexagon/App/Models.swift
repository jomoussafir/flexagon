import Foundation

struct Problem: Codable, Identifiable, Hashable {
    struct Source: Codable, Hashable {
        let title: String
        let number: String
        let page: Int
        let url: String?
        var group: String {
            Self.groupTitle(title)
        }
        static func groupTitle(_ title: String) -> String {
            if title.range(of: "challenging problems in (algebra|geometry)", options: [.regularExpression, .caseInsensitive]) != nil { return "Challenging Problems in Geometry and Algebra" }
            if title.localizedCaseInsensitiveContains("International Mathematical Olympiad") || title.range(of: "\\bIMO\\b", options: [.regularExpression, .caseInsensitive]) != nil { return "IMO" }
            if title.localizedCaseInsensitiveContains("Animath") { return "Animath" }
            if title.localizedCaseInsensitiveContains("Yaglom") { return "Yaglom" }
            return title
        }
    }
    static func sourceRank(_ title: String) -> Int {
        let name = Source.groupTitle(title).lowercased()
        if name.contains("moscow") { return 0 }
        if name.contains("colossal") { return 1 }
        if name == "animath" { return 2 }
        if name.hasPrefix("challenging problems") { return 3 }
        if name == "yaglom" { return 4 }
        if name.contains("stanford") { return 5 }
        if name == "imo" { return 6 }
        return 7
    }
    static func sourceOrder(_ a: String, _ b: String) -> Bool {
        let left = sourceRank(a), right = sourceRank(b)
        return left == right ? a.localizedStandardCompare(b) == .orderedAscending : left < right
    }
    struct Translation: Codable, Hashable {
        let language: String
        let title: String
        let html: String
    }
    var versions: [Translation]? = nil
    var availableLanguages: [String] { versions?.map(\.language).sorted() ?? [language] }
    func preferredLanguage(_ preferred: String) -> String {
        availableLanguages.contains(preferred) ? preferred : (availableLanguages.first ?? language)
    }
    let id: String
    let title: String
    let language: String
    let topic: String
    let difficulty: Int
    let searchText: String
    let editorialNote: String
    let sources: [Source]
    let hasFigure: Bool

    private static let originalCategories: [String:String] = {
        guard let url = Bundle.main.url(forResource: "original-categories", withExtension: "json", subdirectory: "Content"),
              let data = try? Data(contentsOf: url) else { return [:] }
        return (try? JSONDecoder().decode([String:String].self, from: data)) ?? [:]
    }()
    var category: Category {
        Category(rawValue: topic) ?? Category(rawValue: Self.originalCategories[id] ?? "") ?? .logic
    }
    var datedSource: Source? { sources.first { $0.group == "IMO" || $0.group == "Animath" } }
    func displayTitle(language: String? = nil) -> String {
        let lang = language ?? self.language
        let original = versions?.first { $0.language == lang }?.title ?? title
        guard let source = datedSource,
              let range = source.title.range(of: "(?:19|20)[0-9]{2}", options: .regularExpression) else { return original }
        return "\(source.group) \(source.title[range]) \(lang == "fr" ? "Problème" : "Problem") \(source.number)"
    }
    var sourceLabel: String { sources.first.map { "\($0.title) · \($0.number)" } ?? "" }
}

enum Category: String, CaseIterable, Identifiable {
    case algebra, geometry, number_theory, combinatorics, logic
    var id: String { rawValue }
    var title: String {
        switch self {
        case .algebra: return "Algebra"
        case .geometry: return "Geometry"
        case .number_theory: return "Number Theory"
        case .combinatorics: return "Combinatorics"
        case .logic: return "Logic"
        }
    }
    var symbol: String {
        switch self {
        case .algebra: return "function"
        case .geometry: return "triangle"
        case .number_theory: return "number"
        case .combinatorics: return "square.grid.3x3"
        case .logic: return "puzzlepiece"
        }
    }
}

enum SolvingStatus: String, Codable, CaseIterable, Identifiable {
    case unseen, bookmarked, attempted, solved
    var id: String { rawValue }
    var title: String { rawValue.capitalized }
    var symbol: String { self == .solved ? "checkmark.circle.fill" : self == .attempted ? "pencil.circle" : self == .bookmarked ? "bookmark.fill" : "circle" }
}

struct ProgressRecord: Codable, Equatable {
    var status = SolvingStatus.unseen
    var note = ""
    var bookmarked: Bool { status == .bookmarked }

    init(status: SolvingStatus = .unseen, note: String = "") {
        self.status = status
        self.note = note
    }
    private enum CodingKeys: String, CodingKey { case bookmarked, status, note }
    init(from decoder: Decoder) throws {
        let values = try decoder.container(keyedBy: CodingKeys.self)
        status = try values.decodeIfPresent(SolvingStatus.self, forKey: .status) ?? .unseen
        note = try values.decodeIfPresent(String.self, forKey: .note) ?? ""
        // Preserve attempted/solved work; old bookmark-only records become Bookmarked.
        let oldBookmark = try values.decodeIfPresent(Bool.self, forKey: .bookmarked) ?? false
        if status == .unseen && oldBookmark { status = .bookmarked }
    }
    func encode(to encoder: Encoder) throws {
        var values = encoder.container(keyedBy: CodingKeys.self)
        try values.encode(status, forKey: .status)
        try values.encode(note, forKey: .note)
        try values.encode(bookmarked, forKey: .bookmarked)
    }
}

struct ProblemFilter {
    var query = ""
    var category: Category?
    var difficulty: Int?
    var language: String?
    var source: String?
    var progress: SolvingStatus?

    func matches(_ problem: Problem) -> Bool {
        let query = query.trimmingCharacters(in: .whitespacesAndNewlines)
        return (category == nil || problem.category == category)
        && (difficulty == nil || problem.difficulty == difficulty)
        && (language == nil || problem.availableLanguages.contains(language!))
        && (source == nil || problem.sources.contains { $0.group == source || $0.title == source })
        && (query.isEmpty || problem.displayTitle().localizedStandardContains(query) || problem.searchText.localizedStandardContains(query) || problem.id.localizedStandardContains(query))
    }
}

extension ProblemFilter {
    func matches(_ problem: Problem, record: ProgressRecord) -> Bool {
        matches(problem) && (progress == nil || record.status == progress)
    }
    func candidates(in problems: [Problem], progress records: [String: ProgressRecord]) -> [Problem] {
        problems.filter { matches($0, record: records[$0.id] ?? ProgressRecord()) }
    }
}

struct DailySelection {
    // Stable across launches (unlike Swift's randomized hashValue), and across time zones within a local day.
    static func choose(from problems: [Problem], date: Date, level: Int, calendar: Calendar = .current) -> Problem? {
        let pool = problems.filter { $0.difficulty == level }.sorted { $0.id < $1.id }
        guard !pool.isEmpty else { return nil }
        let c = calendar.dateComponents([.year, .month, .day], from: date)
        let key = "\(c.year ?? 0)-\(c.month ?? 0)-\(c.day ?? 0)"
        let hash = key.utf8.reduce(UInt64(14695981039346656037)) { ($0 ^ UInt64($1)) &* 1099511628211 }
        return pool[Int(hash % UInt64(pool.count))]
    }
}

struct PublishedCatalogue: Codable {
    let schemaVersion: Int
    let revision: String
    let problems: [Problem]

    func validated() throws -> [Problem] {
        guard schemaVersion == 1, problems.count <= 20000,
              Set(problems.map(\.id)).count == problems.count else { throw CocoaError(.fileReadCorruptFile) }
        for p in problems {
            guard p.id.range(of: "^[a-z0-9-]+$", options: .regularExpression) != nil,
                  (1...5).contains(p.difficulty), (Category(rawValue: p.topic) != nil || ["imo", "animath", "yaglom"].contains(p.topic)),
                  let versions = p.versions, !versions.isEmpty, versions.count <= 2,
                  Set(versions.map(\.language)).count == versions.count,
                  versions.allSatisfy({ ["en", "fr"].contains($0.language) && !$0.title.isEmpty && !$0.html.isEmpty && $0.html.utf8.count < 2_000_000 })
            else { throw CocoaError(.fileReadCorruptFile) }
        }
        return problems
    }
}

struct PublishedSourceCount: Identifiable {
    let name: String
    let count: Int
    var id: String { name }
    static func summary(_ problems: [Problem], including names: [String] = []) -> [PublishedSourceCount] {
        var counts = Dictionary(uniqueKeysWithValues: Set(names.map(Problem.Source.groupTitle)).map { ($0, 0) })
        for problem in Dictionary(problems.map { ($0.id, $0) }, uniquingKeysWith: { first, _ in first }).values {
            for name in Set(problem.sources.map(\.group)) { counts[name, default: 0] += 1 }
        }
        return counts.keys.sorted(by: Problem.sourceOrder).map { PublishedSourceCount(name: $0, count: counts[$0]!) }
    }
}
