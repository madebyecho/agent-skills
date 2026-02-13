# SwiftUI Before/After Examples

Real-world transformations showing what the swift-accessibility skill produces.

---

## Example 1: Settings Screen

### Before

```swift
struct SettingsView: View {
    @State private var darkMode = false
    @State private var notifications = true
    @State private var fontSize: Double = 16

    var body: some View {
        List {
            Text("Settings")
                .font(.system(size: 28, weight: .bold))

            Section {
                HStack {
                    Image(systemName: "moon.fill")
                    Toggle("Dark Mode", isOn: $darkMode)
                }

                HStack {
                    Image(systemName: "bell.fill")
                    Toggle("Notifications", isOn: $notifications)
                }
            }

            Section {
                Text("Font Size")
                    .font(.system(size: 18, weight: .semibold))
                Slider(value: $fontSize, in: 12...24)
            }

            Button(action: { logout() }) {
                Image(systemName: "arrow.right.square")
            }

            Image("settings-header-decoration")
                .resizable()
                .frame(height: 40)
        }
    }
}
```

### After

```swift
struct SettingsView: View {
    @State private var darkMode = false
    @State private var notifications = true
    @State private var fontSize: Double = 16

    var body: some View {
        List {
            Text("Settings")
                .font(.title.bold())
                .accessibilityAddTraits(.isHeader)

            Section {
                HStack {
                    Image(systemName: "moon.fill")
                    Toggle("Dark Mode", isOn: $darkMode)
                }
                .accessibilityIdentifier("darkModeToggle")

                HStack {
                    Image(systemName: "bell.fill")
                    Toggle("Notifications", isOn: $notifications)
                }
                .accessibilityIdentifier("notificationsToggle")
            }

            Section {
                Text("Font Size")
                    .font(.headline)
                    .accessibilityAddTraits(.isHeader)
                Slider(value: $fontSize, in: 12...24)
                    .accessibilityLabel("Font size")
                    .accessibilityValue("\(Int(fontSize)) points")
                    .accessibilityIdentifier("fontSizeSlider")
            }

            Button(action: { logout() }) {
                Image(systemName: "arrow.right.square")
            }
            .accessibilityLabel("Log out") // [VERIFY] confirm label matches intent
            .accessibilityHint("Signs you out of your account")
            .accessibilityIdentifier("logoutButton")

            Image("settings-header-decoration")
                .resizable()
                .frame(height: 40)
                .accessibilityHidden(true)
        }
    }
}
```

### Changes Summary

| Priority | Issue | Fix |
|----------|-------|-----|
| P0 | Icon-only logout button without label | Added `.accessibilityLabel("Log out")` |
| P1 | Toggles without identifiers | Added `.accessibilityIdentifier` |
| P1 | Logout button without hint | Added `.accessibilityHint(...)` |
| P2 | Hardcoded font `.system(size: 28)` | Changed to `.font(.title.bold())` |
| P2 | Hardcoded font `.system(size: 18)` | Changed to `.font(.headline)` |
| P2 | "Settings" text missing header trait | Added `.accessibilityAddTraits(.isHeader)` |
| P2 | "Font Size" text missing header trait | Added `.accessibilityAddTraits(.isHeader)` |
| P2 | Decorative image not hidden | Added `.accessibilityHidden(true)` |

---

## Example 2: Product Card

### Before

```swift
struct ProductCard: View {
    let product: Product

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Image(product.imageName)
                .resizable()
                .aspectRatio(contentMode: .fill)
                .frame(height: 200)
                .clipped()

            HStack {
                Image(systemName: "star.fill")
                    .foregroundColor(.yellow)
                    .font(.system(size: 12))
                Text("\(product.rating, specifier: "%.1f")")
                    .font(.system(size: 12))
            }

            Text(product.name)
                .font(.system(size: 16, weight: .semibold))

            Text("$\(product.price, specifier: "%.2f")")
                .font(.system(size: 14))
                .foregroundColor(.green)

            Button(action: { addToCart(product) }) {
                Image(systemName: "cart.badge.plus")
            }
        }
    }
}
```

### After

```swift
struct ProductCard: View {
    let product: Product

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Image(product.imageName)
                .resizable()
                .aspectRatio(contentMode: .fill)
                .frame(height: 200)
                .clipped()
                .accessibilityLabel("\(product.name) photo") // [VERIFY] confirm label matches intent

            HStack {
                Image(systemName: "star.fill")
                    .foregroundColor(.yellow)
                    .font(.caption2)
                Text("\(product.rating, specifier: "%.1f")")
                    .font(.caption2)
            }
            .accessibilityElement(children: .combine)
            .accessibilityLabel("\(product.rating, specifier: "%.1f") stars")

            Text(product.name)
                .font(.subheadline.weight(.semibold))

            Text("$\(product.price, specifier: "%.2f")")
                .font(.footnote)
                .foregroundColor(.green)

            Button(action: { addToCart(product) }) {
                Image(systemName: "cart.badge.plus")
            }
            .accessibilityLabel("Add to cart") // [VERIFY] confirm label matches intent
            .accessibilityHint("Adds \(product.name) to your shopping cart")
            .accessibilityIdentifier("addToCartButton_\(product.id)")
        }
        .accessibilityIdentifier("productCard_\(product.id)")
    }
}
```

---

## Example 3: Onboarding Page

### Before

```swift
struct OnboardingPage: View {
    var body: some View {
        VStack(spacing: 20) {
            Image(systemName: "sparkles")
                .font(.system(size: 60))
                .foregroundColor(.blue)

            Text("Welcome to MyApp")
                .font(.system(size: 32, weight: .bold))

            Text("Discover amazing features that help you stay organized and productive.")
                .font(.system(size: 16))
                .multilineTextAlignment(.center)

            Button(action: { continueOnboarding() }) {
                Text("Get Started")
                    .font(.system(size: 18, weight: .semibold))
                    .padding()
                    .frame(maxWidth: .infinity)
                    .background(Color.blue)
                    .foregroundColor(.white)
                    .cornerRadius(12)
            }

            Button(action: { skip() }) {
                Text("Skip")
                    .font(.system(size: 14))
                    .foregroundColor(.gray)
            }
        }
        .padding()
    }
}
```

### After

```swift
struct OnboardingPage: View {
    var body: some View {
        VStack(spacing: 20) {
            Image(systemName: "sparkles")
                .font(.system(size: 60))
                .foregroundColor(.blue)
                .accessibilityHidden(true)

            Text("Welcome to MyApp")
                .font(.largeTitle.bold())
                .accessibilityAddTraits(.isHeader)

            Text("Discover amazing features that help you stay organized and productive.")
                .font(.body)
                .multilineTextAlignment(.center)

            Button(action: { continueOnboarding() }) {
                Text("Get Started")
                    .font(.headline)
                    .padding()
                    .frame(maxWidth: .infinity)
                    .background(Color.blue)
                    .foregroundColor(.white)
                    .cornerRadius(12)
            }
            .accessibilityIdentifier("getStartedButton")

            Button(action: { skip() }) {
                Text("Skip")
                    .font(.footnote)
                    .foregroundColor(.gray)
            }
            .accessibilityHint("Skips the onboarding and goes to the main app")
            .accessibilityIdentifier("skipButton")
        }
        .padding()
    }
}
```
