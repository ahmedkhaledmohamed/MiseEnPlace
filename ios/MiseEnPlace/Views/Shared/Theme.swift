import SwiftUI

enum Theme {
    static let bg = Color(hex: "0f1117")
    static let surface = Color(hex: "1a1d27")
    static let cardBg = Color(hex: "1e2130")
    static let border = Color(hex: "2a2d3a")
    static let text = Color(hex: "e4e4e7")
    static let textMuted = Color(hex: "71717a")
    static let accent = Color(hex: "f59e0b")
    static let green = Color(hex: "22c55e")
    static let red = Color(hex: "ef4444")

    static let cuisineColors: [String: Color] = [
        "Chinese": Color(hex: "ef4444"), "Japanese": Color(hex: "f87171"),
        "Korean": Color(hex: "dc2626"), "East Asian": Color(hex: "fb923c"),
        "Thai": Color(hex: "f97316"), "Vietnamese": Color(hex: "ea580c"),
        "Southeast Asian": Color(hex: "fb923c"), "Indian": Color(hex: "eab308"),
        "South Asian": Color(hex: "facc15"), "Middle Eastern": Color(hex: "22c55e"),
        "Turkish": Color(hex: "16a34a"), "Greek": Color(hex: "4ade80"),
        "Mediterranean": Color(hex: "34d399"), "French": Color(hex: "3b82f6"),
        "Italian": Color(hex: "60a5fa"), "Spanish": Color(hex: "2563eb"),
        "British": Color(hex: "93c5fd"), "Scandinavian": Color(hex: "7dd3fc"),
        "Eastern European": Color(hex: "818cf8"), "American": Color(hex: "a78bfa"),
        "Mexican": Color(hex: "c084fc"), "Latin American": Color(hex: "d946ef"),
        "Caribbean": Color(hex: "e879f9"), "African": Color(hex: "f472b6"),
        "Fusion": Color(hex: "94a3b8"),
    ]

    static let categoryColors: [String: Color] = [
        "protein": Color(hex: "ef4444"), "vegetable": Color(hex: "22c55e"),
        "fruit": Color(hex: "f97316"), "grain": Color(hex: "eab308"),
        "dairy": Color(hex: "93c5fd"), "spice": Color(hex: "f59e0b"),
        "oil-fat": Color(hex: "a3a3a3"), "sauce-condiment": Color(hex: "c084fc"),
        "herb": Color(hex: "34d399"), "legume": Color(hex: "a78bfa"),
        "nut-seed": Color(hex: "d97706"), "sweetener": Color(hex: "f472b6"),
        "liquid": Color(hex: "7dd3fc"), "other": Color(hex: "64748b"),
    ]

    static func cuisineColor(_ cuisine: String) -> Color {
        cuisineColors[cuisine] ?? Color(hex: "94a3b8")
    }

    static func categoryColor(_ category: String) -> Color {
        categoryColors[category] ?? Color(hex: "64748b")
    }
}

extension Color {
    init(hex: String) {
        let hex = hex.trimmingCharacters(in: CharacterSet.alphanumerics.inverted)
        var int: UInt64 = 0
        Scanner(string: hex).scanHexInt64(&int)
        let a, r, g, b: UInt64
        switch hex.count {
        case 6:
            (a, r, g, b) = (255, int >> 16, int >> 8 & 0xFF, int & 0xFF)
        case 8:
            (a, r, g, b) = (int >> 24, int >> 16 & 0xFF, int >> 8 & 0xFF, int & 0xFF)
        default:
            (a, r, g, b) = (255, 0, 0, 0)
        }
        self.init(
            .sRGB,
            red: Double(r) / 255,
            green: Double(g) / 255,
            blue: Double(b) / 255,
            opacity: Double(a) / 255
        )
    }
}
