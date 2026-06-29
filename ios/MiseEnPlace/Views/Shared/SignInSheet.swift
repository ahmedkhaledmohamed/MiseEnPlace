import SwiftUI
import AuthenticationServices

struct SignInSheet: View {
    let onComplete: () -> Void
    @Environment(\.dismiss) private var dismiss
    @AppStorage("hasPassedGate") private var hasPassedGate = false

    var body: some View {
        VStack(spacing: 24) {
            Spacer()

            Image(systemName: "fork.knife.circle.fill")
                .font(.system(size: 64))
                .foregroundStyle(Theme.accent)

            Text("Create your profile")
                .font(.system(size: 28, weight: .bold, design: .serif))

            VStack(alignment: .leading, spacing: 14) {
                BenefitRow(icon: "heart.fill", color: .red,
                    text: "Save your favorite recipes across devices")
                BenefitRow(icon: "calendar", color: Theme.accent,
                    text: "Plan meals and generate grocery lists")
                BenefitRow(icon: "square.and.arrow.up", color: .blue,
                    text: "Share recipes with friends and family")
            }
            .padding(.horizontal, 8)

            Spacer()

            SignInWithAppleButton(.signIn) { request in
                request.requestedScopes = [.fullName, .email]
            } onCompletion: { result in
                switch result {
                case .success:
                    hasPassedGate = true
                    dismiss()
                    onComplete()
                case .failure:
                    break
                }
            }
            .signInWithAppleButtonStyle(.white)
            .frame(height: 50)
            .clipShape(RoundedRectangle(cornerRadius: 12))

            Button {
                hasPassedGate = true
                dismiss()
                onComplete()
            } label: {
                Text("Skip for now")
                    .font(.subheadline)
                    .foregroundStyle(Theme.textMuted)
            }
            .padding(.bottom, 8)
        }
        .padding(24)
        .background(Theme.bg)
        .presentationDetents([.medium])
    }
}

private struct BenefitRow: View {
    let icon: String
    let color: Color
    let text: String

    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: icon)
                .font(.body)
                .foregroundStyle(color)
                .frame(width: 24)
            Text(text)
                .font(.subheadline)
                .foregroundStyle(Theme.text)
        }
    }
}
