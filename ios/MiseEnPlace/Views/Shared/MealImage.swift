import SwiftUI

struct MealImage: View {
    let imageUrl: String?
    let cuisine: String
    var height: CGFloat = 250

    var body: some View {
        if let urlString = imageUrl, let url = URL(string: urlString) {
            AsyncImage(url: url) { phase in
                switch phase {
                case .success(let image):
                    image
                        .resizable()
                        .aspectRatio(contentMode: .fill)
                        .frame(height: height)
                        .clipped()
                case .failure:
                    placeholder
                default:
                    placeholder
                        .overlay {
                            ProgressView()
                                .tint(Theme.textMuted)
                        }
                }
            }
            .frame(height: height)
        } else {
            placeholder
        }
    }

    private var placeholder: some View {
        ZStack {
            LinearGradient(
                colors: [
                    Theme.cuisineColor(cuisine).opacity(0.4),
                    Theme.surface,
                ],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
            Image(systemName: "fork.knife")
                .font(.system(size: 40))
                .foregroundStyle(Theme.textMuted.opacity(0.4))
        }
        .frame(height: height)
    }
}
