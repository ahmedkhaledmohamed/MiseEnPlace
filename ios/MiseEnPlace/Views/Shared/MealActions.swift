import SwiftUI
import SwiftData

struct MealActions: View {
    let meal: Meal
    var iconSize: CGFloat = 24
    var tint: Color = Theme.text

    @Environment(\.modelContext) private var context
    @Query private var favorites: [FavoriteMeal]
    @State private var showAddToPlan = false
    @State private var showSignIn = false
    @State private var pendingAction: PendingAction?
    @AppStorage("hasPassedGate") private var hasPassedGate = false

    private var isFavorited: Bool {
        favorites.contains { $0.mealId == meal.id }
    }

    var body: some View {
        HStack(spacing: 18) {
            actionButton(
                icon: isFavorited ? "heart.fill" : "heart",
                color: isFavorited ? .red : tint
            ) { toggleFavorite() }

            actionButton(icon: "calendar.badge.plus", color: tint) {
                showAddToPlan = true
            }

            actionButton(icon: "paperplane", color: tint) {
                shareAction()
            }

            Spacer()

            actionButton(
                icon: isFavorited ? "bookmark.fill" : "bookmark",
                color: isFavorited ? Theme.accent : tint
            ) { toggleFavorite() }
        }
        .sheet(isPresented: $showAddToPlan) {
            AddToPlanSheet(meal: meal)
        }
        .sheet(isPresented: $showSignIn) {
            SignInSheet {
                if let action = pendingAction {
                    pendingAction = nil
                    DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) {
                        action.execute()
                    }
                }
            }
        }
    }

    @ViewBuilder
    private func actionButton(icon: String, color: Color, action: @escaping () -> Void) -> some View {
        Button {
            gated(action)
        } label: {
            Image(systemName: icon)
                .font(.system(size: iconSize))
                .foregroundStyle(color)
                .frame(width: 44, height: 44)
                .contentShape(Rectangle())
        }
        .buttonStyle(.plain)
    }

    private func gated(_ action: @escaping () -> Void) {
        if hasPassedGate {
            action()
        } else {
            pendingAction = PendingAction(execute: action)
            showSignIn = true
        }
    }

    private func toggleFavorite() {
        let impact = UIImpactFeedbackGenerator(style: .medium)
        impact.impactOccurred()
        if let existing = favorites.first(where: { $0.mealId == meal.id }) {
            context.delete(existing)
        } else {
            context.insert(FavoriteMeal(mealId: meal.id))
        }
    }

    private func shareAction() {
        var text = "\(meal.name) — \(meal.cuisine)\n\(meal.desc)\n\(meal.totalTime) min · $\(String(format: "%.2f", meal.costPerServing))/serving"
        if let url = meal.imageUrl { text += "\n\(url)" }

        let av = UIActivityViewController(activityItems: [text], applicationActivities: nil)
        if let windowScene = UIApplication.shared.connectedScenes.first as? UIWindowScene,
           let root = windowScene.windows.first?.rootViewController {
            root.present(av, animated: true)
        }
    }
}

private struct PendingAction {
    let execute: () -> Void
}
