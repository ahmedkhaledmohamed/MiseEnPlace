import SwiftUI

struct MealImage: View {
    let imageName: String?
    let cuisine: String
    var height: CGFloat = 250

    private var uiImage: UIImage? {
        guard let name = imageName,
              let path = Bundle.main.path(forResource: name, ofType: nil) ??
                         Bundle.main.path(forResource: (name as NSString).deletingPathExtension, ofType: (name as NSString).pathExtension)
        else { return nil }
        return UIImage(contentsOfFile: path)
    }

    var body: some View {
        if let img = uiImage {
            Image(uiImage: img)
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
