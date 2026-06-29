import SwiftUI

struct StatBadge: View {
    let icon: String
    let value: String

    var body: some View {
        HStack(spacing: 4) {
            Image(systemName: icon)
                .font(.caption2)
                .foregroundStyle(Theme.textMuted)
            Text(value)
                .font(.caption)
                .fontWeight(.medium)
        }
        .foregroundStyle(Theme.text)
    }
}

struct TagPill: View {
    let text: String
    var color: Color = Theme.green

    var body: some View {
        Text(text)
            .font(.caption2)
            .fontWeight(.medium)
            .padding(.horizontal, 8)
            .padding(.vertical, 3)
            .background(color.opacity(0.2))
            .foregroundStyle(color)
            .clipShape(Capsule())
    }
}

struct CuisinePill: View {
    let cuisine: String

    var body: some View {
        Text(cuisine)
            .font(.caption)
            .fontWeight(.bold)
            .tracking(0.3)
            .padding(.horizontal, 10)
            .padding(.vertical, 4)
            .background(Theme.cuisineColor(cuisine).opacity(0.85))
            .foregroundStyle(.white)
            .clipShape(Capsule())
            .shadow(color: .black.opacity(0.3), radius: 2, y: 1)
    }
}
