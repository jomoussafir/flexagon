import SwiftUI

struct RootView: View {
    @State private var selectedTab = 0
    @State private var exploreSource: String?
    @EnvironmentObject private var store: LibraryStore
    var body: some View {
        TabView(selection: $selectedTab) {
            HomeView { source in exploreSource = source; selectedTab = 1 }.tabItem { Label("Home", systemImage: "house") }.tag(0)
            ExploreView(source: exploreSource).id(exploreSource).tabItem { Label("Explore", systemImage: "square.grid.2x2") }.tag(1)
            TodayView().tabItem { Label("Today", systemImage: "sun.max") }.tag(2)
            SavedView().tabItem { Label("My library", systemImage: "books.vertical") }.tag(3)
        }
        .overlay(alignment: .top) {
            if let message = store.errorMessage {
                Text(message).font(.callout).padding().frame(maxWidth: .infinity).background(.regularMaterial)
            }
        }
    }
}

struct HomeView: View {
    let onSourceSelect: (String) -> Void
    @EnvironmentObject private var store: LibraryStore
    private static let knownSources: [String] = {
        guard let url = Bundle.main.url(forResource: "source-groups", withExtension: "json", subdirectory: "Content"),
              let data = try? Data(contentsOf: url) else { return [] }
        return (try? JSONDecoder().decode([String].self, from: data)) ?? []
    }()
    var body: some View {
        NavigationStack {
            List {
                Section {
                    VStack(spacing: 16) {
                        Button {
                            Task { await store.refresh() }
                        } label: {
                            Image("BrandIcon").resizable().scaledToFit().frame(width: 112, height: 112)
                                .clipShape(RoundedRectangle(cornerRadius: 25))
                                .overlay {
                                    if store.isRefreshing {
                                        ProgressView().padding(10).background(.regularMaterial, in: Circle())
                                    }
                                }
                        }
                        .buttonStyle(.plain)
                        .disabled(store.isRefreshing)
                        .accessibilityLabel("Refresh problem list")
                        .accessibilityHint("Downloads the latest published problems from the server")
                        .accessibilityValue(store.isRefreshing ? "Updating" : "")
                        .accessibilityIdentifier("refresh-catalogue")
                        Text("Flexagon").font(.system(.title, design: .serif)).multilineTextAlignment(.center)
                        Text("\(store.problems.count) published problems").font(.title3.weight(.semibold))
                    }.frame(maxWidth: .infinity).padding(.vertical, 24)
                }.listRowBackground(Color.clear)
                Section("Published by source") {
                    ForEach(PublishedSourceCount.summary(store.problems, including: Self.knownSources)) { source in
                        Button { onSourceSelect(source.name) } label: {
                            HStack {
                                Text(source.name).foregroundStyle(.primary)
                                Spacer()
                                Text("\(source.count)").monospacedDigit().foregroundStyle(.secondary)
                            }
                        }
                    }
                }
                if let message = store.syncMessage { Section { Text(message).font(.footnote).foregroundStyle(.secondary) } }
            }.scrollContentBackground(.hidden).background(Palette.paper)
                .refreshable { await store.refresh() }
                .navigationTitle("Home").navigationBarTitleDisplayMode(.inline)
        }
    }
}

struct ExploreView: View {
    init(source: String? = nil) { _filter = State(initialValue: ProblemFilter(source: source)) }
    @EnvironmentObject private var store: LibraryStore
    @State private var filter = ProblemFilter()
    @State private var showFilters = false
    var filtered: [Problem] { store.problems.filter { filter.matches($0, record: store.record(for: $0.id)) }.sorted { ($0.difficulty, $0.id) < ($1.difficulty, $1.id) } }
    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 22) {
                    HStack {
                        Text("\(filtered.count) problems").font(.subheadline.weight(.semibold))
                        Spacer()
                        if filter.category != nil || filter.difficulty != nil || filter.language != nil || filter.source != nil || filter.progress != nil {
                            Button("Clear filters") { filter.category = nil; filter.difficulty = nil; filter.language = nil; filter.source = nil; filter.progress = nil }
                                .font(.subheadline)
                        }
                        Button { showFilters = true } label: { Label("Filter", systemImage: "slider.horizontal.3") }
                            .buttonStyle(.bordered).accessibilityIdentifier("filters")
                    }
                    if filtered.isEmpty {
                        if store.problems.isEmpty {
                            ContentUnavailableView("Ready for reviewed problems", systemImage: "checkmark.seal", description: Text("Approved problems appear here after publication. Pull down to check for updates."))
                        } else { ContentUnavailableView.search(text: filter.query) }
                        Button("Reset all filters") { filter = ProblemFilter() }.frame(maxWidth: .infinity)
                    }
                    LazyVStack(spacing: 12) {
                        ForEach(filtered) { problem in
                            NavigationLink { ProblemDetailView(problem: problem) } label: { ProblemCard(problem: problem) }
                                .buttonStyle(.plain)
                        }
                    }
                }.padding(.horizontal, 20).padding(.bottom, 24)
            }
            .refreshable { await store.refresh() }
            .background(Palette.paper)
            .navigationTitle("Flexagon").navigationBarTitleDisplayMode(.inline)
            .searchable(text: $filter.query, prompt: "Search problems or sources")
            .sheet(isPresented: $showFilters) { FilterSheet(filter: $filter) }
        }
    }
}

struct FilterSheet: View {
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject private var store: LibraryStore
    @Binding var filter: ProblemFilter
    var body: some View {
        NavigationStack {
            Form {
                Section("Category") {
                    Picker("Category", selection: $filter.category) {
                        Text("All categories").tag(nil as Category?)
                        ForEach(Category.allCases) { Text($0.title).tag(Optional($0)) }
                    }
                }
                Section("Level") {
                    Picker("Level", selection: $filter.difficulty) {
                        Text("All levels").tag(nil as Int?)
                        ForEach(1...5, id: \.self) { Text("Level \($0)").tag(Optional($0)) }
                    }
                    Text("1 · Introductory\n2 · Intermediate\n3 · Challenging\n4 · National olympiad\n5 · International olympiad")
                        .font(.footnote).foregroundStyle(.secondary)
                    Text("Ratings are provisional for secondary-school olympiad learners.").font(.footnote).foregroundStyle(.secondary)
                }
                Section {
                    Picker("Language", selection: $filter.language) {
                        Text("All languages").tag(nil as String?)
                        Text("French").tag(Optional("fr")); Text("English").tag(Optional("en"))
                    }
                    Picker("Source", selection: $filter.source) {
                        Text("All sources").tag(nil as String?)
                        ForEach(Array(Set(store.problems.flatMap { $0.sources.map(\.group) })).sorted(by: Problem.sourceOrder), id: \.self) { Text($0).tag(Optional($0)) }
                    }
                }
                Section("Progress") {
                    Picker("Progress", selection: $filter.progress) {
                        Text("All progress").tag(nil as SolvingStatus?)
                        ForEach(SolvingStatus.allCases) { Text($0.title).tag(Optional($0)) }
                    }
                }
                Button("Reset filters") { filter = ProblemFilter() }
            }.navigationTitle("Refine your library").navigationBarTitleDisplayMode(.inline)
                .toolbar { ToolbarItem(placement: .confirmationAction) { Button("Done") { dismiss() } } }
        }.presentationDetents([.medium, .large])
    }
}

struct ProblemCard: View {
    @EnvironmentObject private var store: LibraryStore
    let problem: Problem
    var body: some View {
        VStack(alignment: .leading, spacing: 13) {
            HStack {
                Label(problem.category.title, systemImage: problem.category.symbol).font(.caption.weight(.semibold)).foregroundStyle(Palette.teal)
                Spacer()
                Text(problem.availableLanguages.map { $0.uppercased() }.joined(separator: " / ")).font(.caption2.weight(.semibold)).foregroundStyle(.secondary)
                if store.record(for: problem.id).bookmarked { Image(systemName: "bookmark.fill").foregroundStyle(Palette.teal).accessibilityLabel("Bookmarked") }
            }
            Text(problem.displayTitle()).font(.system(.title3, design: .serif)).foregroundStyle(.primary).fixedSize(horizontal: false, vertical: true)
            HStack {
                DifficultyDots(level: problem.difficulty)
                Spacer()
                if store.record(for: problem.id).status != .unseen {
                    Label(store.record(for: problem.id).status.title, systemImage: store.record(for: problem.id).status.symbol).font(.caption).foregroundStyle(Palette.teal)
                }
                Image(systemName: "arrow.up.right").font(.caption).foregroundStyle(.secondary)
            }
            Text(problem.sourceLabel).font(.caption2).foregroundStyle(.secondary).lineLimit(2)
        }
        .padding(20).frame(maxWidth: .infinity, alignment: .leading)
        .background(Color(uiColor: .secondarySystemGroupedBackground), in: RoundedRectangle(cornerRadius: 20))
        .overlay(RoundedRectangle(cornerRadius: 20).stroke(Palette.teal.opacity(0.1)))
        .accessibilityElement(children: .combine)
        .accessibilityIdentifier("problem-\(problem.id)")
    }
}

struct DifficultyDots: View {
    let level: Int
    var body: some View {
        HStack(spacing: 4) {
            ForEach(1...5, id: \.self) { n in Circle().fill(n <= level ? Palette.teal : Palette.teal.opacity(0.16)).frame(width: 6, height: 6) }
            Text("Level \(level)").font(.caption).foregroundStyle(.secondary).padding(.leading, 4)
        }.accessibilityElement(children: .ignore).accessibilityLabel("Difficulty \(level) out of 5, provisional")
    }
}

struct TodayView: View {
    @EnvironmentObject private var store: LibraryStore
    @State private var filter = ProblemFilter()
    @State private var path: [Problem] = []
    private var candidates: [Problem] { filter.candidates(in: store.problems, progress: store.progress) }
    var body: some View {
        NavigationStack(path: $path) {
            ScrollView {
                VStack(alignment: .leading, spacing: 24) {
                    Button {
                        if let problem = candidates.randomElement() { path.append(problem) }
                    } label: {
                        Label("Pick one", systemImage: "shuffle").frame(maxWidth: .infinity).padding(.vertical, 8)
                    }.buttonStyle(.borderedProminent).disabled(candidates.isEmpty).accessibilityIdentifier("pick-one")
                    VStack(spacing: 16) {
                        Picker("Category", selection: $filter.category) {
                            Text("All categories").tag(nil as Category?)
                            ForEach(Category.allCases) { Text($0.title).tag(Optional($0)) }
                        }
                        Picker("Level", selection: $filter.difficulty) {
                            Text("All levels").tag(nil as Int?)
                            ForEach(1...5, id: \.self) { Text("Level \($0)").tag(Optional($0)) }
                        }
                        Picker("Source", selection: $filter.source) {
                            Text("All sources").tag(nil as String?)
                            ForEach(Array(Set(store.problems.flatMap { $0.sources.map(\.group) })).sorted(by: Problem.sourceOrder), id: \.self) { Text($0).tag(Optional($0)) }
                        }
                        HStack {
                            Text("Progress").foregroundStyle(.secondary)
                            Spacer()
                            Picker("Progress", selection: $filter.progress) {
                                Text("All").tag(nil as SolvingStatus?)
                                ForEach(SolvingStatus.allCases) { Text($0.title).tag(Optional($0)) }
                            }.accessibilityIdentifier("today-progress")
                        }
                    }.pickerStyle(.menu).frame(maxWidth: .infinity, alignment: .leading)
                    Text("\(candidates.count) matching problems").font(.subheadline).foregroundStyle(.secondary)

                    if candidates.isEmpty {
                        ContentUnavailableView("No problems match", systemImage: "book.closed", description: Text("Try another category, level, source or progress, or reset the filters."))
                        Button("Reset filters") { filter = ProblemFilter() }.frame(maxWidth: .infinity)
                    }
                }.padding(24)
            }.refreshable { await store.refresh() }
                .background(Palette.paper)
                .navigationTitle("Today").navigationBarTitleDisplayMode(.inline)
                .navigationDestination(for: Problem.self) { ProblemDetailView(problem: $0) }
        }
    }
}

struct SavedView: View {
    @EnvironmentObject private var store: LibraryStore
    @State private var selected = "Bookmarks"
    @State private var showAbout = false
    private let sections = ["Bookmarks", "Attempted", "Solved"]
    var rows: [Problem] {
        store.problems.filter {
            let r = store.record(for: $0.id)
            return selected == "Bookmarks" ? r.bookmarked : r.status.rawValue == selected.lowercased()
        }
    }
    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 20) {
                    Text("Your mathematical\nnotebook.").font(.system(.largeTitle, design: .serif))
                    Text("\(store.progress.values.filter { $0.status == .solved }.count) solved · \(store.progress.values.filter(\.bookmarked).count) bookmarked")
                        .font(.subheadline).foregroundStyle(.secondary)
                    Picker("Collection", selection: $selected) { ForEach(sections, id: \.self) { Text($0) } }.pickerStyle(.segmented)
                    if rows.isEmpty {
                        ContentUnavailableView("A fresh page", systemImage: selected == "Bookmarks" ? "bookmark" : "pencil", description: Text("Save a problem or mark your progress in the reader. It will appear here."))
                    }
                    ForEach(rows) { problem in
                        NavigationLink { ProblemDetailView(problem: problem) } label: { ProblemCard(problem: problem) }.buttonStyle(.plain)
                    }
                }.padding(20)
            }.background(Palette.paper).navigationTitle("My library").navigationBarTitleDisplayMode(.inline)
                .toolbar { Button { showAbout = true } label: { Image(systemName: "info.circle") }.accessibilityLabel("About this collection") }
                .sheet(isPresented: $showAbout) { AboutView() }
        }
    }
}

struct AboutView: View {
    @EnvironmentObject private var store: LibraryStore
    @State private var address = ""
    @Environment(\.dismiss) private var dismiss
    var body: some View {
        NavigationStack {
            List {
                Section("The collection") {
                    Text("\(store.problems.count) problems. Only reviewed translations from the publication feed appear in the library. Difficulty ratings are provisional.")
                    Text("Each language is reviewed separately before publication. Hints and solutions are not included yet.")
                }
                Section("Problem updates") {
                    TextField("HTTPS catalogue address", text: $address)
                        .textInputAutocapitalization(.never).autocorrectionDisabled().keyboardType(.URL)
                    Button(store.isRefreshing ? "Checking…" : "Save address & check for updates") {
                        store.feedURL = address
                        Task { await store.refresh() }
                    }.disabled(store.isRefreshing)
                    if let message = store.syncMessage { Text(message).font(.footnote) }
                    Text("New problems download when you open the app. Downloaded statements remain available offline.")
                }
                Section("On your device") {
                    Text("Downloaded problems and diagrams are available offline. Bookmarks, notes and progress stay on this device. No account or analytics. Deleting the app deletes its saved progress.")
                }
                Section("Private pilot") { Text("This collection is for private review. Public reuse permissions have not been reviewed.") }
                Section("Typesetting") {
                    Text("KaTeX 0.16.22 · MIT License")
                    Text((try? String(contentsOf: Bundle.main.resourceURL!.appendingPathComponent("Content/Reading/katex/LICENSE"), encoding: .utf8)) ?? "KaTeX copyright holders; MIT License.")
                        .font(.caption).textSelection(.enabled)
                }
            }.navigationTitle("About").navigationBarTitleDisplayMode(.inline)
                .onAppear { address = store.feedURL }
                .toolbar { ToolbarItem(placement: .confirmationAction) { Button("Done") { dismiss() } } }
        }
    }
}
