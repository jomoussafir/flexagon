import SwiftUI

@main
struct FlexagonApp: App {
    @Environment(\.scenePhase) private var scenePhase
    @StateObject private var store = LibraryStore()
    var body: some Scene {
        WindowGroup {
            #if DEBUG
            CommunityWebsiteView()
            #else
            RootView()
                .environmentObject(store)
                .tint(Palette.teal)
                .task { await store.refresh() }
                .onChange(of: scenePhase) { _, phase in
                    if phase == .active { Task { await store.refresh() } }
                }
            #endif
        }
    }
}

enum Palette {
    static let teal = Color(red: 0.13, green: 0.48, blue: 0.43)
    static let paper = Color(uiColor: UIColor { traits in
        traits.userInterfaceStyle == .dark ? UIColor(red: 0.08, green: 0.14, blue: 0.14, alpha: 1) : UIColor(red: 0.98, green: 0.97, blue: 0.95, alpha: 1)
    })
}
