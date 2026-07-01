import SwiftUI

struct MealImage: View {
    let imageUrl: String?
    let cuisine: String
    var height: CGFloat = 250

    var body: some View {
        if let urlString = imageUrl, let url = URL(string: urlString) {
            AsyncImage(url: url, transaction: Transaction(animation: nil)) { phase in
                switch phase {
                case .success(let image):
                    image
                        .resizable()
                        .aspectRatio(contentMode: .fill)
                case .failure:
                    placeholderContent
                default:
                    placeholderContent
                }
            }
            .frame(height: height)
            .clipped()
        } else {
            placeholderContent
                .frame(height: height)
        }
    }

    private var placeholderContent: some View {
        ZStack {
            LinearGradient(
                colors: [
                    Theme.cuisineColor(cuisine).opacity(0.4),
                    Theme.surface,
                ],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
        }
        .frame(height: height)
    }
}
