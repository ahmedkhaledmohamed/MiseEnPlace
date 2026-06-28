import SwiftUI

struct MealImage: View {
    let imageName: String?
    let cuisine: String
    var height: CGFloat = 250

    var body: some View {
        if let name = imageName, let uiImage = UIImage(named: name) {
            Image(uiImage: uiImage)
                .resizable()
                .aspectRatio(contentMode: .fill)
                .frame(height: height)
                .clipped()
        } else {
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
}
