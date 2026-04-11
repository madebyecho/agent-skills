# Expo Before/After Examples

Real-world transformations showing what the react-native-accessibility skill produces in Expo managed workflow projects.

---

## Example 1: Settings Screen

### Before

```tsx
import { View, Text, Switch, Pressable, Image } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';

export default function SettingsScreen() {
  const router = useRouter();
  const [darkMode, setDarkMode] = useState(false);
  const [notifications, setNotifications] = useState(true);

  return (
    <View style={styles.container}>
      <Text style={{ fontSize: 28, fontWeight: 'bold' }}>Settings</Text>

      <View style={styles.row}>
        <Ionicons name="moon" size={20} />
        <Text>Dark Mode</Text>
        <Switch value={darkMode} onValueChange={setDarkMode} />
      </View>

      <View style={styles.row}>
        <Ionicons name="notifications" size={20} />
        <Text>Push Notifications</Text>
        <Switch value={notifications} onValueChange={setNotifications} />
      </View>

      <View style={styles.separator} />

      <Pressable onPress={() => router.push('/profile')}>
        <Ionicons name="person" size={24} />
      </Pressable>

      <Pressable onPress={handleLogout}>
        <Ionicons name="log-out" size={24} />
      </Pressable>

      <Image
        source={require('../assets/settings-wave.png')}
        style={styles.decoration}
      />
    </View>
  );
}
```

### After

```tsx
import { View, Text, Switch, Pressable, Image } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';

export default function SettingsScreen() {
  const router = useRouter();
  const [darkMode, setDarkMode] = useState(false);
  const [notifications, setNotifications] = useState(true);

  return (
    <View style={styles.container}>
      <Text style={{ fontSize: 28, fontWeight: 'bold' }} accessibilityRole="header">
        Settings
      </Text>

      <View style={styles.row} accessible={true} accessibilityLabel="Dark Mode">
        <Ionicons name="moon" size={20} />
        <Text>Dark Mode</Text>
        <Switch
          value={darkMode}
          onValueChange={setDarkMode}
          accessibilityLabel="Dark Mode"
          accessibilityRole="switch"
          accessibilityState={{ checked: darkMode }}
        />
      </View>

      <View style={styles.row} accessible={true} accessibilityLabel="Push Notifications">
        <Ionicons name="notifications" size={20} />
        <Text>Push Notifications</Text>
        <Switch
          value={notifications}
          onValueChange={setNotifications}
          accessibilityLabel="Push Notifications"
          accessibilityRole="switch"
          accessibilityState={{ checked: notifications }}
        />
      </View>

      <View
        style={styles.separator}
        accessible={false}
        importantForAccessibility="no"
        accessibilityElementsHidden={true}
      />

      <Pressable
        onPress={() => router.push('/profile')}
        accessibilityLabel="Profile" // [VERIFY] confirm label matches intent
        accessibilityRole="button"
        accessibilityHint="Opens your profile page" // [VERIFY] confirm hint accuracy
      >
        <Ionicons name="person" size={24} />
      </Pressable>

      <Pressable
        onPress={handleLogout}
        accessibilityLabel="Log out" // [VERIFY] confirm label matches intent
        accessibilityRole="button"
        accessibilityHint="Signs you out of your account" // [VERIFY] confirm hint accuracy
      >
        <Ionicons name="log-out" size={24} />
      </Pressable>

      <Image
        source={require('../assets/settings-wave.png')}
        style={styles.decoration}
        accessible={false}
        importantForAccessibility="no"
        accessibilityElementsHidden={true}
      />
    </View>
  );
}
```

### Changes Summary

| Priority | Issue | Fix |
|----------|-------|-----|
| P0 | Icon-only Profile button without label | Added `accessibilityLabel` + `accessibilityRole` |
| P0 | Icon-only Log out button without label | Added `accessibilityLabel` + `accessibilityRole` |
| P1 | Profile button without hint | Added `accessibilityHint` |
| P1 | Log out button without hint | Added `accessibilityHint` |
| P1 | Switches without roles/state | Added `accessibilityRole="switch"` + `accessibilityState` |
| P2 | "Settings" heading without header role | Added `accessibilityRole="header"` |
| P2 | Icon+text rows not grouped | Added `accessible={true}` with composed label |
| P2 | Separator exposed to screen readers | Hidden with platform-specific props |
| P2 | Decorative image exposed | Hidden with platform-specific props |

---

## Example 2: Product Card

### Before

```tsx
import { View, Text, Pressable } from 'react-native';
import { Image } from 'expo-image';
import { Ionicons } from '@expo/vector-icons';

function ProductCard({ product }: { product: Product }) {
  return (
    <View style={styles.card}>
      <Image
        source={product.imageUrl}
        style={styles.productImage}
        contentFit="cover"
      />

      <View style={styles.ratingRow}>
        <Ionicons name="star" size={12} color="#FFD700" />
        <Text style={styles.ratingText}>{product.rating.toFixed(1)}</Text>
      </View>

      <Text style={styles.productName} allowFontScaling={false}>
        {product.name}
      </Text>

      <Text style={{ color: '#999', fontSize: 12 }}>
        {product.category}
      </Text>

      <Text style={styles.price}>${product.price.toFixed(2)}</Text>

      <Pressable onPress={() => addToCart(product)} style={styles.cartButton}>
        <Ionicons name="cart" size={20} color="white" />
      </Pressable>
    </View>
  );
}
```

### After

```tsx
import { View, Text, Pressable } from 'react-native';
import { Image } from 'expo-image';
import { Ionicons } from '@expo/vector-icons';

function ProductCard({ product }: { product: Product }) {
  return (
    <View style={styles.card}>
      <Image
        source={product.imageUrl}
        style={styles.productImage}
        contentFit="cover"
        accessibilityLabel={`${product.name} photo`} // [VERIFY] confirm label matches intent
      />

      <View
        style={styles.ratingRow}
        accessible={true}
        accessibilityLabel={`${product.rating.toFixed(1)} stars`}
      >
        <Ionicons name="star" size={12} color="#FFD700" />
        <Text style={styles.ratingText}>{product.rating.toFixed(1)}</Text>
      </View>

      <Text style={styles.productName}>
        {product.name}
      </Text>

      <Text style={{ color: '#767676', fontSize: 12 }}>
        {/* [VERIFY] contrast ratio of #767676 on background meets 4.5:1 */}
        {product.category}
      </Text>

      <Text style={styles.price}>${product.price.toFixed(2)}</Text>

      <Pressable
        onPress={() => addToCart(product)}
        style={styles.cartButton}
        accessibilityLabel={`Add ${product.name} to cart`} // [VERIFY] confirm label matches intent
        accessibilityRole="button"
        accessibilityHint="Adds this item to your shopping cart"
      >
        <Ionicons name="cart" size={20} color="white" />
      </Pressable>
    </View>
  );
}
```

### Changes Summary

| Priority | Issue | Fix |
|----------|-------|-----|
| P0 | Product image without label | Added `accessibilityLabel` |
| P0 | Icon-only cart button without label | Added `accessibilityLabel` + `accessibilityRole` |
| P1 | Cart button without hint | Added `accessibilityHint` |
| P2 | `allowFontScaling={false}` on product name | Removed restriction |
| P2 | Star icon + rating text not grouped | Added `accessible={true}` with composed label |
| P2 | `#999` color likely fails contrast | Changed to `#767676` with `[VERIFY]` |

---

## Example 3: Onboarding Screen (Expo Router)

### Before

```tsx
import { View, Text, Pressable } from 'react-native';
import Animated, { useSharedValue, withSpring, useAnimatedStyle } from 'react-native-reanimated';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';

export default function OnboardingScreen() {
  const router = useRouter();
  const scale = useSharedValue(0.8);

  useEffect(() => {
    scale.value = withSpring(1);
  }, []);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
  }));

  return (
    <View style={styles.container}>
      <Animated.View style={animatedStyle}>
        <Ionicons name="sparkles" size={64} color="#6C63FF" />
      </Animated.View>

      <Text style={{ fontSize: 32, fontWeight: 'bold' }}>Welcome</Text>
      <Text style={{ fontSize: 16, color: '#aaa' }}>
        Discover amazing features
      </Text>

      <Pressable onPress={() => router.push('/home')} style={styles.ctaButton}>
        <Text style={styles.ctaText}>Get Started</Text>
      </Pressable>

      <Pressable onPress={() => router.push('/home')}>
        <Text style={{ color: '#ccc', fontSize: 14 }}>Skip</Text>
      </Pressable>
    </View>
  );
}
```

### After

```tsx
import { View, Text, Pressable } from 'react-native';
import Animated, {
  useSharedValue,
  withSpring,
  useAnimatedStyle,
  useReducedMotion,
} from 'react-native-reanimated';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';

export default function OnboardingScreen() {
  const router = useRouter();
  const reduceMotion = useReducedMotion();
  const scale = useSharedValue(reduceMotion ? 1 : 0.8);

  useEffect(() => {
    if (!reduceMotion) {
      scale.value = withSpring(1);
    }
  }, [reduceMotion]);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
  }));

  return (
    <View style={styles.container}>
      <Animated.View style={animatedStyle}>
        <Ionicons
          name="sparkles"
          size={64}
          color="#6C63FF"
          accessible={false}
          importantForAccessibility="no"
          accessibilityElementsHidden={true}
        />
      </Animated.View>

      <Text
        style={{ fontSize: 32, fontWeight: 'bold' }}
        accessibilityRole="header"
      >
        Welcome
      </Text>
      <Text style={{ fontSize: 16, color: '#767676' }}>
        {/* [VERIFY] contrast ratio of #767676 on background meets 4.5:1 */}
        Discover amazing features
      </Text>

      <Pressable
        onPress={() => router.push('/home')}
        style={styles.ctaButton}
        accessibilityRole="button"
      >
        <Text style={styles.ctaText}>Get Started</Text>
      </Pressable>

      <Pressable
        onPress={() => router.push('/home')}
        accessibilityRole="button"
        accessibilityHint="Skips onboarding and goes to the main screen"
      >
        <Text style={{ color: '#767676', fontSize: 14 }}>
          {/* [VERIFY] contrast ratio meets 4.5:1 */}
          Skip
        </Text>
      </Pressable>
    </View>
  );
}
```

### Changes Summary

| Priority | Issue | Fix |
|----------|-------|-----|
| P1 | Buttons without roles | Added `accessibilityRole="button"` |
| P1 | Skip button without hint | Added `accessibilityHint` |
| P2 | "Welcome" heading without header role | Added `accessibilityRole="header"` |
| P2 | Decorative sparkles icon exposed | Hidden with platform-specific props |
| P2 | `#aaa` and `#ccc` text fails contrast | Changed to `#767676` with `[VERIFY]` |
| P2 | Animation ignores reduce motion | Added `useReducedMotion()` check |
